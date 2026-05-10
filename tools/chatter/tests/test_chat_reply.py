"""Unit tests for tools/chatter/chat_reply.py — the shared CHAT_REPLY handler."""
import json
import unittest
from unittest.mock import MagicMock

from tools.chatter import chat_reply, conversations
from tools.chatter.azure_client import ApiResult


def _make_request(user_message: str, *, session_id: str = "s1",
                  leader_id: int = 7, leader_name: str = "Louis XIV",
                  civ: str = "France", human_name: str = "Harrison") -> dict:
    return {
        "request_id": "req-test",
        "session_id": session_id,
        "trigger": "CHAT_REPLY",
        "speaker": {"leader_name": leader_name, "civ_short_name": civ, "player_id": leader_id},
        "target": {"leader_name": human_name, "civ_short_name": "America",
                   "player_id": 0, "human_name": human_name},
        "context": {"user_message": user_message},
    }


def _fake_client(text: str):
    """Return a MagicMock that pretends to be an AzureClient.call_chat()."""
    client = MagicMock()
    client.call_chat = MagicMock(return_value=ApiResult(
        text=text, latency_ms=42, input_tokens=100, output_tokens=20,
    ))
    return client


class TestHandleChatReply(unittest.TestCase):
    def test_happy_path_appends_to_history(self):
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "How dare you, peasant.", "tone": "angry"}))
        req = _make_request("You are a fool, Louie!")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(line, "How dare you, peasant.")
        self.assertEqual(tone, "angry")
        self.assertEqual(resp["lines"][0]["text"], "How dare you, peasant.")
        self.assertEqual(resp["lines"][0]["tone"], "angry")
        self.assertEqual(resp["trigger"], "CHAT_REPLY")
        # History now has both turns.
        msgs = store.get_messages(("s1", 7))
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["content"], "How dare you, peasant.")

    def test_empty_user_message_short_circuits(self):
        store = conversations.ConversationStore()
        client = _fake_client("ignored")
        req = _make_request("")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "empty_user_message")
        client.call_chat.assert_not_called()

    def test_invalid_tone_falls_back_to_theatrical(self):
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Hello there.", "tone": "exuberant"}))
        req = _make_request("Hi.")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(tone, "theatrical")

    def test_history_passed_to_llm_grows_each_turn(self):
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Reply 1.", "tone": "haughty"}))
        req = _make_request("Turn 1.")
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        # Second turn: should see prior turns in the messages list.
        client2 = _fake_client(json.dumps({"line": "Reply 2.", "tone": "amused"}))
        req2 = _make_request("Turn 2.")
        chat_reply.handle_chat_reply(request=req2, store=store, client=client2)

        called_messages = client2.call_chat.call_args[0][0]
        # First message is the system prompt; remaining should be history.
        self.assertEqual(called_messages[0]["role"], "system")
        roles = [m["role"] for m in called_messages[1:]]
        # u-a-u: turn 1 user, turn 1 assistant, turn 2 user.
        self.assertEqual(roles, ["user", "assistant", "user"])
        self.assertEqual(called_messages[-1]["content"], "Turn 2.")

    def test_api_failure_returns_error_response(self):
        from tools.chatter.azure_client import ApiError
        store = conversations.ConversationStore()
        client = MagicMock()
        client.call_chat = MagicMock(side_effect=ApiError("boom"))
        req = _make_request("Hi.")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "api_failure")
        self.assertEqual(line, "")

    def test_malformed_json_falls_back_gracefully(self):
        store = conversations.ConversationStore()
        # Plain text reply (no JSON) -- parser should still produce a line.
        client = _fake_client("Just a plain string reply, no JSON here.")
        req = _make_request("Hi.")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertTrue(resp["ok"])
        self.assertIn("plain string reply", line)
        self.assertEqual(tone, "theatrical")


if __name__ == "__main__":
    unittest.main()
