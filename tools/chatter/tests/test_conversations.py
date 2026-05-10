"""Unit tests for tools/chatter/conversations.py."""
import time
import unittest

from tools.chatter import conversations


class TestConversationStore(unittest.TestCase):
    def test_round_trip_single_conversation(self):
        store = conversations.ConversationStore(history_seconds=600, max_turns=24)
        key = ("session-1", 7)
        store.append_user(key, "Hello, Louis.", leader_name="Louis XIV")
        store.append_assistant(key, "Greetings, mortal.")
        store.append_user(key, "How is Versailles?")
        msgs = store.get_messages(key)
        self.assertEqual(len(msgs), 3)
        self.assertEqual(msgs[0]["role"], "user")
        self.assertEqual(msgs[0]["content"], "Hello, Louis.")
        self.assertEqual(msgs[1]["role"], "assistant")
        self.assertEqual(msgs[1]["content"], "Greetings, mortal.")
        self.assertEqual(msgs[2]["role"], "user")

    def test_separate_conversations_isolated(self):
        store = conversations.ConversationStore()
        a = ("s", 7)
        b = ("s", 9)
        store.append_user(a, "to-louis")
        store.append_user(b, "to-gilg")
        self.assertEqual(len(store.get_messages(a)), 1)
        self.assertEqual(len(store.get_messages(b)), 1)
        self.assertEqual(store.get_messages(a)[0]["content"], "to-louis")
        self.assertEqual(store.get_messages(b)[0]["content"], "to-gilg")

    def test_max_turns_truncates_oldest(self):
        store = conversations.ConversationStore(max_turns=4)
        key = ("s", 1)
        for i in range(10):
            role = "user" if i % 2 == 0 else "assistant"
            if role == "user":
                store.append_user(key, "u" + str(i))
            else:
                store.append_assistant(key, "a" + str(i))
        msgs = store.get_messages(key)
        self.assertLessEqual(len(msgs), 4)
        # The most recent messages should be retained.
        self.assertEqual(msgs[-1]["content"], "a9")

    def test_idle_gc_drops_old_conversations(self):
        store = conversations.ConversationStore(history_seconds=0.05)
        key = ("s", 1)
        store.append_user(key, "old")
        time.sleep(0.1)
        # Force GC by triggering another operation; either way, after the
        # idle window, get_messages should return empty for the stale key.
        store._gc_idle()
        self.assertEqual(store.get_messages(key), [])

    def test_clear_session_drops_only_that_session(self):
        store = conversations.ConversationStore()
        store.append_user(("s1", 7), "keep-or-drop")
        store.append_user(("s2", 7), "different-session")
        store.clear_session("s1")
        self.assertEqual(store.get_messages(("s1", 7)), [])
        self.assertEqual(len(store.get_messages(("s2", 7))), 1)


if __name__ == "__main__":
    unittest.main()
