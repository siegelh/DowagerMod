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
        # History rendering prefixes user turns with [<typer>] when the
        # request carried a typer name (target.human_name in SP).
        self.assertEqual(called_messages[-1]["content"], "[Harrison] Turn 2.")
        self.assertEqual(called_messages[1]["content"], "[Harrison] Turn 1.")

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

    # --- MP / from_human ---

    def test_from_human_in_context_overrides_target_human_name(self):
        """ctx['from_human'] (game-side chrome) takes precedence over target."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Indeed.", "tone": "amused"}))
        req = _make_request("Howdy.", human_name="Harrison")
        # MP: a friend typed it, chrome said 'Foo'.
        req["context"]["from_human"] = "Foo"

        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        msgs = store.get_messages(("s1", 7))
        self.assertEqual(msgs[0]["content"], "[Foo] Howdy.")
        # System prompt should name Foo, not Harrison.
        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertIn("Foo", sys_msg)
        # No "other humans" yet on first turn.
        self.assertNotIn("Other humans", sys_msg)
        self.assertNotIn("Another human", sys_msg)

    def test_multi_human_thread_records_other_humans(self):
        """Two different humans in the same thread => system prompt mentions the other."""
        store = conversations.ConversationStore()

        client1 = _fake_client(json.dumps({"line": "Greetings.", "tone": "amused"}))
        req1 = _make_request("First.", human_name="Harrison")
        req1["context"]["from_human"] = "Harrison"
        chat_reply.handle_chat_reply(request=req1, store=store, client=client1)

        client2 = _fake_client(json.dumps({"line": "Both of you.", "tone": "haughty"}))
        req2 = _make_request("Second.", human_name="Harrison")
        req2["context"]["from_human"] = "Foo"
        chat_reply.handle_chat_reply(request=req2, store=store, client=client2)

        called = client2.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        # Latest typer is Foo; Harrison is the "other".
        self.assertIn("Foo", sys_msg)
        self.assertIn("Harrison", sys_msg)
        self.assertIn("Another human", sys_msg)
        # History reflects prefixes for both turns.
        msgs = store.get_messages(("s1", 7))
        self.assertEqual(msgs[0]["content"], "[Harrison] First.")
        self.assertEqual(msgs[2]["content"], "[Foo] Second.")

    def test_three_humans_uses_plural_clause(self):
        store = conversations.ConversationStore()
        for typer in ("Harrison", "Foo", "Bar"):
            client = _fake_client(json.dumps({"line": "Sure.", "tone": "amused"}))
            req = _make_request("Hi.", human_name="Harrison")
            req["context"]["from_human"] = typer
            chat_reply.handle_chat_reply(request=req, store=store, client=client)

        # On the last call, the "other humans" list contains the first two.
        # (We can fish the system prompt off the last call.)
        # Re-issue once more with a known typer so we can capture cleanly.
        client_final = _fake_client(json.dumps({"line": "Done.", "tone": "amused"}))
        req_final = _make_request("End.", human_name="Harrison")
        req_final["context"]["from_human"] = "Bar"
        chat_reply.handle_chat_reply(request=req_final, store=store, client=client_final)

        called = client_final.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertIn("Other humans", sys_msg)
        self.assertIn("Harrison", sys_msg)
        self.assertIn("Foo", sys_msg)

    def test_sp_no_from_human_falls_back_to_target_human_name(self):
        """SP path: ctx has no from_human; we use target.human_name."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "OK.", "tone": "amused"}))
        req = _make_request("Hi.", human_name="Harrison")
        # No ctx['from_human'].
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        msgs = store.get_messages(("s1", 7))
        self.assertEqual(msgs[0]["content"], "[Harrison] Hi.")
        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertIn("Harrison", sys_msg)

    # --- MP / pivot context ---

    def test_pivot_includes_prior_thread_summary_in_system_prompt(self):
        """Pivot from leader 9 to leader 7: summary of leader 9's thread shows up."""
        store = conversations.ConversationStore()

        # Seed prior thread with leader 9 (Montezuma).
        c1 = _fake_client(json.dumps({"line": "your stench rivals my pyramids.",
                                      "tone": "haughty"}))
        req_prior = _make_request("Montezuma you stink.", leader_id=9,
                                  leader_name="Montezuma")
        req_prior["context"]["from_human"] = "Harrison"
        chat_reply.handle_chat_reply(request=req_prior, store=store, client=c1)

        # Now pivot to leader 7 (Louis); context flags the prior thread.
        c2 = _fake_client(json.dumps({"line": "Indeed, mon ami.", "tone": "amused"}))
        req_pivot = _make_request("Louis what do you think?", leader_id=7,
                                  leader_name="Louis XIV")
        req_pivot["context"]["from_human"] = "Harrison"
        req_pivot["context"]["prior_thread_with_leader_id"] = "9"
        chat_reply.handle_chat_reply(request=req_pivot, store=store, client=c2)

        called = c2.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        # Background block names the prior leader and includes recap content.
        self.assertIn("BACKGROUND", sys_msg)
        self.assertIn("Montezuma", sys_msg)
        self.assertIn("you stink", sys_msg)
        self.assertIn("pyramids", sys_msg)

    def test_pivot_with_no_prior_thread_skips_background_block(self):
        """If prior thread doesn't exist in store, no BACKGROUND block."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Hello.", "tone": "amused"}))
        req = _make_request("First contact.", leader_id=7)
        req["context"]["from_human"] = "Harrison"
        # Claim a pivot from leader 9, but leader 9 has no prior thread.
        req["context"]["prior_thread_with_leader_id"] = "9"
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertNotIn("BACKGROUND", sys_msg)

    def test_pivot_to_same_leader_skips_background_block(self):
        """prior_thread_with_leader_id == speaker is a no-op (defensive)."""
        store = conversations.ConversationStore()
        # Seed thread with leader 7.
        c0 = _fake_client(json.dumps({"line": "Hello there.", "tone": "amused"}))
        chat_reply.handle_chat_reply(request=_make_request("hi"), store=store, client=c0)

        client = _fake_client(json.dumps({"line": "More.", "tone": "amused"}))
        req = _make_request("Continue.", leader_id=7)
        req["context"]["from_human"] = "Harrison"
        # Bogus pivot pointer pointing to ourselves.
        req["context"]["prior_thread_with_leader_id"] = "7"
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertNotIn("BACKGROUND", sys_msg)

    def test_pivot_summary_is_truncated(self):
        """If prior thread is long, summary stays under PIVOT_SUMMARY_MAX_CHARS."""
        from tools.chatter import prompts
        store = conversations.ConversationStore()
        # Build a verbose prior thread with leader 9.
        long_line = "x" * 200
        for i in range(8):
            ck = _fake_client(json.dumps({"line": long_line, "tone": "amused"}))
            r = _make_request(long_line, leader_id=9, leader_name="Montezuma")
            r["context"]["from_human"] = "Harrison"
            chat_reply.handle_chat_reply(request=r, store=store, client=ck)

        cf = _fake_client(json.dumps({"line": "Sure.", "tone": "amused"}))
        rf = _make_request("Switch to Louis.", leader_id=7,
                           leader_name="Louis XIV")
        rf["context"]["from_human"] = "Harrison"
        rf["context"]["prior_thread_with_leader_id"] = "9"
        chat_reply.handle_chat_reply(request=rf, store=store, client=cf)

        called = cf.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        # The recap segment lives between "Brief recap" and "They have now turned"
        idx_start = sys_msg.find("Brief recap of that thread:")
        idx_end = sys_msg.find("They have now turned")
        self.assertGreater(idx_start, 0)
        self.assertGreater(idx_end, idx_start)
        recap = sys_msg[idx_start:idx_end]
        # Truncation cap: ~PIVOT_SUMMARY_MAX_CHARS plus the leading line and ellipsis.
        self.assertLess(len(recap), prompts.PIVOT_SUMMARY_MAX_CHARS + 80)


class TestChainReply(unittest.TestCase):
    """mp-chain-replies: chain-flavored CHAT_REPLY when prior speaker is an AI."""

    def test_chain_reply_uses_chain_system_prompt(self):
        """When ctx['chain_reply']='1', system msg uses the chain variant."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Spare me, Victoria.", "tone": "haughty"}))
        req = _make_request("Montezuma is a buffoon.",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")
        # Vic just said "Montezuma is a buffoon" -- now Monte should chain-reply.
        req["context"]["chain_reply"] = "1"
        req["context"]["chain_depth"] = "1"
        req["context"]["prior_leader_speaker_name"] = "Victoria"

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        self.assertTrue(resp["ok"])
        # System prompt: chain variant referenced "Victoria has just said".
        sys_msg = client.call_chat.call_args[0][0][0]["content"]
        self.assertIn("Victoria", sys_msg)
        self.assertIn("Another leader", sys_msg)
        # Pivot block must NOT appear in chain replies.
        self.assertNotIn("BACKGROUND:", sys_msg)
        # Chain prompt does NOT use the human-typer phrasing.
        self.assertNotIn("most\nrecent message was sent by the human", sys_msg)

    def test_chain_reply_appends_leader_speaker_turn(self):
        """Chain user_message goes in via append_leader_speaker, not append_user."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "Hold your tongue.", "tone": "angry"}))
        req = _make_request("You are a buffoon.",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")
        req["context"]["chain_reply"] = "1"
        req["context"]["chain_depth"] = "1"
        req["context"]["prior_leader_speaker_name"] = "Victoria"

        chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        # Conversation should have two turns: leader-speaker user + assistant.
        conv = store.get(("s1", 4))
        self.assertIsNotNone(conv)
        self.assertEqual(len(conv.turns), 2)
        first = conv.turns[0]
        self.assertEqual(first.role, "user")
        self.assertEqual(first.speaker_type, "leader")
        self.assertEqual(first.speaker_name, "Victoria")
        # humans_heard should NOT include Victoria (she's a leader, not human).
        self.assertEqual(store.humans_heard(("s1", 4)), [])

    def test_address_to_parsed_and_surfaced_in_response(self):
        """Optional address_to in LLM JSON is surfaced on lines[0]."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({
            "line": "Victoria, you are next.",
            "tone": "menacing",
            "address_to": "Victoria",
        }))
        req = _make_request("Tell Victoria to back off.",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(len(resp["lines"]), 1)
        self.assertEqual(resp["lines"][0]["address_to"], "Victoria")

    def test_address_to_missing_defaults_empty(self):
        """No address_to in LLM output -> empty string on the response line."""
        store = conversations.ConversationStore()
        client = _fake_client(json.dumps({"line": "How charming.", "tone": "amused"}))
        req = _make_request("hello",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(resp["lines"][0]["address_to"], "")

    def test_address_to_non_string_dropped(self):
        """Non-string address_to (e.g. null, number) is dropped to empty."""
        from tools.chatter.azure_client import parse_chat_reply
        # null
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": None}))
        self.assertEqual(out["address_to"], "")
        # number
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": 42}))
        self.assertEqual(out["address_to"], "")
        # whitespace-only string -> stripped to empty
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": "   "}))
        self.assertEqual(out["address_to"], "")
        # legit string
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": "Vic"}))
        self.assertEqual(out["address_to"], "Vic")


if __name__ == "__main__":
    unittest.main()
