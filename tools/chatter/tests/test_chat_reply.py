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
    def test_happy_path_appends_to_room(self):
        store = conversations.RoomStore()
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
        # Room now has both turns (human + leader).
        msgs = store.get_messages_for("s1", leader_player_id=7)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["content"], "How dare you, peasant.")

    def test_empty_user_message_short_circuits(self):
        store = conversations.RoomStore()
        client = _fake_client("ignored")
        req = _make_request("")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertFalse(resp["ok"])
        self.assertEqual(resp["error"], "empty_user_message")
        client.call_chat.assert_not_called()

    def test_invalid_tone_falls_back_to_theatrical(self):
        store = conversations.RoomStore()
        client = _fake_client(json.dumps({"line": "Hello there.", "tone": "exuberant"}))
        req = _make_request("Hi.")

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client,
        )
        self.assertTrue(resp["ok"])
        self.assertEqual(tone, "theatrical")

    def test_history_passed_to_llm_grows_each_turn(self):
        store = conversations.RoomStore()
        client = _fake_client(json.dumps({"line": "Reply 1.", "tone": "haughty"}))
        req = _make_request("Turn 1.")
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        client2 = _fake_client(json.dumps({"line": "Reply 2.", "tone": "amused"}))
        req2 = _make_request("Turn 2.")
        chat_reply.handle_chat_reply(request=req2, store=store, client=client2)

        called_messages = client2.call_chat.call_args[0][0]
        self.assertEqual(called_messages[0]["role"], "system")
        roles = [m["role"] for m in called_messages[1:]]
        # u-a-u: turn 1 user, turn 1 assistant, turn 2 user.
        self.assertEqual(roles, ["user", "assistant", "user"])
        # History prefixes user turns with the typer's bracketed name.
        self.assertEqual(called_messages[-1]["content"], "[Harrison] Turn 2.")
        self.assertEqual(called_messages[1]["content"], "[Harrison] Turn 1.")

    def test_api_failure_returns_error_response(self):
        from tools.chatter.azure_client import ApiError
        store = conversations.RoomStore()
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
        store = conversations.RoomStore()
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
        store = conversations.RoomStore()
        client = _fake_client(json.dumps({"line": "Indeed.", "tone": "amused"}))
        req = _make_request("Howdy.", human_name="Harrison")
        # MP: a friend typed it, chrome said 'Foo'.
        req["context"]["from_human"] = "Foo"

        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        msgs = store.get_messages_for("s1", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[Foo] Howdy.")
        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertIn("Foo", sys_msg)
        self.assertNotIn("Other humans", sys_msg)
        self.assertNotIn("Another human", sys_msg)

    def test_multi_human_thread_records_other_humans(self):
        """Two different humans in the same room => system prompt mentions the other."""
        store = conversations.RoomStore()

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
        # Both turns visible in shared room.
        msgs = store.get_messages_for("s1", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[Harrison] First.")
        self.assertEqual(msgs[2]["content"], "[Foo] Second.")

    def test_three_humans_uses_plural_clause(self):
        store = conversations.RoomStore()
        for typer in ("Harrison", "Foo", "Bar"):
            client = _fake_client(json.dumps({"line": "Sure.", "tone": "amused"}))
            req = _make_request("Hi.", human_name="Harrison")
            req["context"]["from_human"] = typer
            chat_reply.handle_chat_reply(request=req, store=store, client=client)

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
        store = conversations.RoomStore()
        client = _fake_client(json.dumps({"line": "OK.", "tone": "amused"}))
        req = _make_request("Hi.", human_name="Harrison")
        # No ctx['from_human'].
        chat_reply.handle_chat_reply(request=req, store=store, client=client)

        msgs = store.get_messages_for("s1", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[Harrison] Hi.")
        called = client.call_chat.call_args[0][0]
        sys_msg = called[0]["content"]
        self.assertIn("Harrison", sys_msg)

    # --- Shared-room: humans see all leaders, leaders see all humans + each other ---

    def test_shared_room_other_leader_visible_in_new_leader_history(self):
        """Pivot is implicit: when Louis is asked to reply, Montezuma's prior
        turn is right there in the room transcript prefixed `[Montezuma said] ...`.
        """
        store = conversations.RoomStore()

        # Harrison talks to Montezuma (pid=9).
        c1 = _fake_client(json.dumps({"line": "your stench rivals my pyramids.",
                                      "tone": "haughty"}))
        req_a = _make_request("Montezuma you stink.", leader_id=9,
                              leader_name="Montezuma")
        req_a["context"]["from_human"] = "Harrison"
        chat_reply.handle_chat_reply(request=req_a, store=store, client=c1)

        # Now Harrison turns to Louis (pid=7). Louis should see Montezuma's
        # line in his history, attributed by name.
        c2 = _fake_client(json.dumps({"line": "Indeed, mon ami.", "tone": "amused"}))
        req_b = _make_request("Louis what do you think?", leader_id=7,
                              leader_name="Louis XIV")
        req_b["context"]["from_human"] = "Harrison"
        chat_reply.handle_chat_reply(request=req_b, store=store, client=c2)

        called = c2.call_chat.call_args[0][0]
        # Verify history was visible to Louis with Montezuma's name on it.
        history = [m for m in called[1:]]
        joined = "\n".join(m["content"] for m in history)
        self.assertIn("[Harrison] Montezuma you stink.", joined)
        self.assertIn("[Montezuma said] your stench rivals my pyramids.", joined)

    def test_shared_room_no_background_block_in_system_prompt(self):
        """Shared room replaces the old pivot BACKGROUND block entirely."""
        store = conversations.RoomStore()
        # Seed prior thread for leader 9.
        c1 = _fake_client(json.dumps({"line": "x.", "tone": "amused"}))
        r1 = _make_request("hi.", leader_id=9, leader_name="Montezuma")
        r1["context"]["from_human"] = "Harrison"
        chat_reply.handle_chat_reply(request=r1, store=store, client=c1)

        # Now pivot via the OLD ctx flag -- it should NOT trigger any
        # BACKGROUND block in the new world (shared room handles it).
        c2 = _fake_client(json.dumps({"line": "y.", "tone": "amused"}))
        r2 = _make_request("turn.", leader_id=7, leader_name="Louis XIV")
        r2["context"]["from_human"] = "Harrison"
        r2["context"]["prior_thread_with_leader_id"] = "9"
        chat_reply.handle_chat_reply(request=r2, store=store, client=c2)

        sys_msg = c2.call_chat.call_args[0][0][0]["content"]
        self.assertNotIn("BACKGROUND", sys_msg)


class TestChainReply(unittest.TestCase):
    """Chain reply: one AI leader replies to another via shared room."""

    def test_chain_reply_uses_chain_system_prompt(self):
        """When ctx['chain_reply']='1', system msg uses the chain variant."""
        store = conversations.RoomStore()
        # Seed the room: Victoria spoke first.
        store.append_leader("s1", "Montezuma is a buffoon.",
                            speaker_name="Victoria", speaker_player_id=2)

        client = _fake_client(json.dumps({"line": "Spare me, Victoria.", "tone": "haughty"}))
        req = _make_request("Montezuma is a buffoon.",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")
        req["context"]["chain_reply"] = "1"
        req["context"]["chain_depth"] = "1"
        req["context"]["prior_leader_speaker_name"] = "Victoria"

        resp, line, tone = chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        self.assertTrue(resp["ok"])
        sys_msg = client.call_chat.call_args[0][0][0]["content"]
        self.assertIn("Victoria", sys_msg)
        self.assertIn("Another leader", sys_msg)
        # No BACKGROUND block in chain replies.
        self.assertNotIn("BACKGROUND:", sys_msg)
        # Chain prompt does NOT use the human-typer phrasing.
        self.assertNotIn("most\nrecent message was sent by the human", sys_msg)

    def test_chain_reply_does_not_re_append_prior_leader_line(self):
        """Chain reply does NOT re-append user_message to the room; the
        prior leader's line was already added when that leader spoke."""
        store = conversations.RoomStore()
        # Victoria's line is already in the room.
        store.append_leader("s1", "You are a buffoon.",
                            speaker_name="Victoria", speaker_player_id=2)

        client = _fake_client(json.dumps({"line": "Hold your tongue.", "tone": "angry"}))
        req = _make_request("You are a buffoon.",
                            leader_id=4, leader_name="Montezuma", civ="Aztec")
        req["context"]["chain_reply"] = "1"
        req["context"]["chain_depth"] = "1"
        req["context"]["prior_leader_speaker_name"] = "Victoria"

        chat_reply.handle_chat_reply(
            request=req, store=store, client=client, max_tokens=120,
        )
        room = store.get("s1")
        # Two turns: Victoria's prior + Montezuma's response. NOT three.
        self.assertEqual(len(room.turns), 2)
        self.assertEqual(room.turns[0].speaker_name, "Victoria")
        self.assertEqual(room.turns[1].speaker_name, "Montezuma")
        # humans_heard is empty (no humans typed).
        self.assertEqual(store.humans_heard("s1"), [])

    def test_address_to_parsed_and_surfaced_in_response(self):
        """Optional address_to in LLM JSON is surfaced on lines[0]."""
        store = conversations.RoomStore()
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
        store = conversations.RoomStore()
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
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": None}))
        self.assertEqual(out["address_to"], "")
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": 42}))
        self.assertEqual(out["address_to"], "")
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": "   "}))
        self.assertEqual(out["address_to"], "")
        out = parse_chat_reply(json.dumps({"line": "x", "tone": "amused", "address_to": "Vic"}))
        self.assertEqual(out["address_to"], "Vic")


if __name__ == "__main__":
    unittest.main()

