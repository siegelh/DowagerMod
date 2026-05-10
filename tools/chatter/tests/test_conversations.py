"""Unit tests for tools/chatter/conversations.py — shared-room store."""
import time
import unittest

from tools.chatter import conversations


class TestRoomStore(unittest.TestCase):
    def test_round_trip_single_room(self):
        store = conversations.RoomStore(history_seconds=600, max_turns=24)
        sid = "session-1"
        store.append_human(sid, "Hello, Louis.",
                           speaker_name="Harrison", speaker_player_id=0)
        store.append_leader(sid, "Greetings, mortal.",
                            speaker_name="Louis XIV", speaker_player_id=7)
        store.append_human(sid, "How is Versailles?",
                           speaker_name="Harrison", speaker_player_id=0)
        msgs = store.get_messages_for(sid, leader_player_id=7)
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["content"], "[Harrison] Hello, Louis.")
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["content"], "Greetings, mortal.")
        self.assertEqual(msgs[2]["role"], "user")
        self.assertEqual(msgs[2]["content"], "[Harrison] How is Versailles?")

    def test_separate_sessions_isolated(self):
        store = conversations.RoomStore()
        store.append_human("s1", "to-louis", speaker_name="A", speaker_player_id=0)
        store.append_human("s2", "to-gilg",  speaker_name="B", speaker_player_id=0)
        a = store.get_messages_for("s1", leader_player_id=7)
        b = store.get_messages_for("s2", leader_player_id=9)
        self.assertEqual(len(a), 1)
        self.assertEqual(len(b), 1)
        self.assertEqual(a[0]["content"], "[A] to-louis")
        self.assertEqual(b[0]["content"], "[B] to-gilg")

    def test_max_turns_truncates_oldest(self):
        store = conversations.RoomStore(max_turns=4)
        sid = "s"
        for i in range(10):
            if i % 2 == 0:
                store.append_human(sid, "u" + str(i),
                                   speaker_name="H", speaker_player_id=0)
            else:
                store.append_leader(sid, "a" + str(i),
                                    speaker_name="L", speaker_player_id=1)
        msgs = store.get_messages_for(sid, leader_player_id=1)
        self.assertLessEqual(len(msgs), 4)
        # The most-recent message should be retained.
        self.assertEqual(msgs[-1]["content"], "a9")

    def test_idle_gc_drops_old_rooms(self):
        store = conversations.RoomStore(history_seconds=0.05)
        sid = "s"
        store.append_human(sid, "old", speaker_name="A", speaker_player_id=0)
        time.sleep(0.1)
        # Force GC; after the idle window the room is gone.
        store._gc_idle()
        self.assertEqual(store.get_messages_for(sid, leader_player_id=7), [])

    def test_clear_session_drops_only_that_session(self):
        store = conversations.RoomStore()
        store.append_human("s1", "keep-or-drop",
                           speaker_name="A", speaker_player_id=0)
        store.append_human("s2", "different-session",
                           speaker_name="B", speaker_player_id=0)
        store.clear_session("s1")
        self.assertEqual(store.get_messages_for("s1", leader_player_id=7), [])
        self.assertEqual(len(store.get_messages_for("s2", leader_player_id=7)), 1)

    # --- speaker prefixes ---

    def test_human_speaker_prefixed_with_brackets(self):
        store = conversations.RoomStore()
        store.append_human("s", "hi", speaker_name="Alice", speaker_player_id=0)
        msgs = store.get_messages_for("s", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[Alice] hi")

    def test_multi_human_renders_each_typer_name(self):
        store = conversations.RoomStore()
        store.append_human("s", "first",  speaker_name="Alice", speaker_player_id=0)
        store.append_human("s", "second", speaker_name="Bob",   speaker_player_id=1)
        msgs = store.get_messages_for("s", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[Alice] first")
        self.assertEqual(msgs[1]["content"], "[Bob] second")

    def test_no_speaker_name_renders_generic_human(self):
        """SP-style callsite with no speaker_name gets `[human]` prefix."""
        store = conversations.RoomStore()
        store.append_human("s", "no-name")
        msgs = store.get_messages_for("s", leader_player_id=7)
        self.assertEqual(msgs[0]["content"], "[human] no-name")

    def test_humans_heard_returns_distinct_typers_in_order(self):
        store = conversations.RoomStore()
        for typer in ("Alice", "Bob", "Alice", "Carol"):
            store.append_human("s", "t", speaker_name=typer, speaker_player_id=0)
        self.assertEqual(store.humans_heard("s"), ["Alice", "Bob", "Carol"])

    # --- shared room across leaders ---

    def test_other_leaders_rendered_with_said_prefix(self):
        """Lines from other AI leaders prefix `[<name> said] ...` from POV
        of a different leader."""
        store = conversations.RoomStore()
        store.append_human("s", "you stink",
                           speaker_name="Alice", speaker_player_id=0)
        # Montezuma (pid=4) replies.
        store.append_leader("s", "no, YOU stink",
                            speaker_name="Montezuma", speaker_player_id=4)
        # Now render from Victoria's POV (pid=2): Montezuma's line is "user".
        msgs = store.get_messages_for("s", leader_player_id=2)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["content"], "[Alice] you stink")
        self.assertEqual(msgs[1]["role"], "user")
        self.assertEqual(msgs[1]["content"], "[Montezuma said] no, YOU stink")

    def test_speakers_own_line_renders_as_assistant(self):
        """A leader's own past lines render as 'assistant' from their POV."""
        store = conversations.RoomStore()
        store.append_human("s", "ok",
                           speaker_name="A", speaker_player_id=0)
        store.append_leader("s", "fine",
                            speaker_name="Louis XIV", speaker_player_id=7)
        msgs = store.get_messages_for("s", leader_player_id=7)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["content"], "fine")

    def test_leaders_heard_returns_distinct_speaker_pids(self):
        store = conversations.RoomStore()
        store.append_leader("s", "x", speaker_name="L1", speaker_player_id=1)
        store.append_leader("s", "y", speaker_name="L2", speaker_player_id=2)
        store.append_leader("s", "z", speaker_name="L1", speaker_player_id=1)
        self.assertEqual(store.leaders_heard("s"), [1, 2])

    # --- back-compat alias ---

    def test_conversation_store_alias_points_at_room_store(self):
        """Old name still imports and behaves identically."""
        self.assertIs(conversations.ConversationStore, conversations.RoomStore)


if __name__ == "__main__":
    unittest.main()

