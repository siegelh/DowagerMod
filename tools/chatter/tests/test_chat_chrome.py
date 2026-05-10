"""Unit tests for tools/chatter/chat_chrome.py.

This is the sidecar parallel of CvLeaderChatter._parse_chat_chrome.
Keep cases in sync with both implementations.
"""
import unittest

from tools.chatter.chat_chrome import parse_chat_chrome, strip_chat_chrome


class TestParseChatChrome(unittest.TestCase):
    def test_full_color_wrapped_to_all(self):
        s = "<color=165,140,229,255>[hasiegel to all]:  uhhh hello?</color>"
        typer, body = parse_chat_chrome(s)
        self.assertEqual(typer, "hasiegel")
        self.assertEqual(body, "uhhh hello?")

    def test_no_color_to_all(self):
        typer, body = parse_chat_chrome("[Foo to all]: hi there")
        self.assertEqual(typer, "Foo")
        self.assertEqual(body, "hi there")

    def test_pm_to_player(self):
        typer, body = parse_chat_chrome("[Charlie to Player3]: psst")
        self.assertEqual(typer, "Charlie")
        self.assertEqual(body, "psst")

    def test_team_chat(self):
        typer, body = parse_chat_chrome("[Bob to TeamRed]: rush!")
        self.assertEqual(typer, "Bob")
        self.assertEqual(body, "rush!")

    def test_no_chrome_returns_empty_typer(self):
        typer, body = parse_chat_chrome("just text")
        self.assertEqual(typer, "")
        self.assertEqual(body, "just text")

    def test_empty_string(self):
        typer, body = parse_chat_chrome("")
        self.assertEqual(typer, "")
        self.assertEqual(body, "")

    def test_malformed_bracket_no_close(self):
        typer, body = parse_chat_chrome("[hasiegel to all hi")
        self.assertEqual(typer, "")
        # Falls through to "no bracket chrome" path; preserves body.
        self.assertEqual(body, "[hasiegel to all hi")

    def test_bracket_no_to_separator(self):
        typer, body = parse_chat_chrome("[weird]: message")
        self.assertEqual(typer, "")
        self.assertEqual(body, "message")

    def test_color_tag_only_no_chrome(self):
        s = "<color=255,0,0,255>plain text</color>"
        typer, body = parse_chat_chrome(s)
        self.assertEqual(typer, "")
        self.assertEqual(body, "plain text")

    def test_uppercase_color_closer(self):
        s = "<color=1,2,3,4>[hasiegel to all]: hey</COLOR>"
        typer, body = parse_chat_chrome(s)
        self.assertEqual(typer, "hasiegel")
        self.assertEqual(body, "hey")

    def test_typer_with_space_in_name(self):
        typer, body = parse_chat_chrome("[John Smith to all]: yo")
        self.assertEqual(typer, "John Smith")
        self.assertEqual(body, "yo")

    def test_typer_with_underscore(self):
        typer, body = parse_chat_chrome("[player_one to all]: hi")
        self.assertEqual(typer, "player_one")
        self.assertEqual(body, "hi")

    def test_extra_whitespace_after_colon(self):
        typer, body = parse_chat_chrome("[Foo to all]:    spaced  ")
        self.assertEqual(typer, "Foo")
        self.assertEqual(body, "spaced")

    def test_leading_whitespace_before_bracket(self):
        typer, body = parse_chat_chrome("   [Foo to all]: hi")
        self.assertEqual(typer, "Foo")
        self.assertEqual(body, "hi")

    def test_unicode_typer_name(self):
        typer, body = parse_chat_chrome("[Zoë to all]: bonjour")
        self.assertEqual(typer, "Zoë")
        self.assertEqual(body, "bonjour")

    def test_message_body_contains_brackets(self):
        # Body brackets must NOT confuse the parser; only leading bracket
        # forms chrome.
        typer, body = parse_chat_chrome("[Foo to all]: I said [run!]")
        self.assertEqual(typer, "Foo")
        self.assertEqual(body, "I said [run!]")

    def test_message_body_contains_to(self):
        # ' to ' inside the body must NOT match the chrome separator.
        typer, body = parse_chat_chrome("[Foo to all]: go to the city")
        self.assertEqual(typer, "Foo")
        self.assertEqual(body, "go to the city")


class TestStripChatChromeBackCompat(unittest.TestCase):
    """strip_chat_chrome is a back-compat wrapper that returns body only."""

    def test_returns_body(self):
        s = "<color=1,2,3,4>[hasiegel to all]: hi</color>"
        self.assertEqual(strip_chat_chrome(s), "hi")

    def test_no_chrome_pass_through(self):
        self.assertEqual(strip_chat_chrome("just text"), "just text")

    def test_empty(self):
        self.assertEqual(strip_chat_chrome(""), "")


if __name__ == "__main__":
    unittest.main()
