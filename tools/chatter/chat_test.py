"""DowagerMod chatter CLI test harness.

Lets you exercise the player <-> AI conversation loop end-to-end without
launching Civ4. Same handler the daemon uses (chat_reply.handle_chat_reply),
same prompts, same conversation store, same TTS pipeline, same audio.

Modes
-----

One-shot::

    python -m tools.chatter.chat_test --leader "Louis XIV" --message "You are a fool!"

Prints::

    [Louis XIV / angry / pitch=+8% rate=+62%]
      How dare you address me so, you ignorant peasant!
    [voice playing...]

REPL (multi-turn, conversation history persists in memory)::

    python -m tools.chatter.chat_test --leader "Louis XIV" --repl
    You: You are a fool, Louie!
    [Louis XIV / angry / pitch=+8% rate=+62%]
      How dare you address me so, you ignorant peasant!
    You: My apologies, your majesty.
    [Louis XIV / haughty / pitch=-3% rate=+48%]
      Apology noted, but not yet accepted.
    You: :switch Gilgamesh
    (switched to Gilgamesh)
    You: Stand with me?
    ...
    You: :quit

REPL meta-commands (prefix ``:``)
    :quit / :q / :exit  -- leave the REPL
    :reset              -- clear all conversation history (any leader)
    :clear              -- alias for :reset
    :switch NAME        -- change active leader (resolves fuzzy)
    :leader             -- show current leader
    :history            -- print recent turns for the current leader
    :voice / :novoice   -- toggle audio playback for the rest of the session
    :help               -- show this list

Other flags
    --no-voice          synthesize nothing; text only (fast iteration)
    --reset             discard any persisted history before starting (no-op
                        right now -- history is in-memory only -- but kept
                        for forward-compat in case we add persistence)
    --list-leaders      print the static BTS roster and exit
    --max-tokens N      override chat_reply_max_tokens (default from config)
    --human-name NAME   the name the AI sees as the human player (default: 'You')

This is in-process: it does NOT use the spool, does NOT require the daemon
to be running. The daemon's spool consumer eventually calls the same
handle_chat_reply() function this CLI calls directly.
"""
from __future__ import annotations

import argparse
import getpass
import logging
import os
import sys
import tempfile
import time
import uuid
from pathlib import Path
from typing import Optional, Tuple

# Make sure repo root is on sys.path when the file is run as a script
# (vs. via -m). When run as -m, this is harmless.
_repo_root = Path(__file__).resolve().parents[2]
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from tools.chatter.azure_client import AzureClient
from tools.chatter.chat_reply import handle_chat_reply
from tools.chatter.chat_resolve import resolve_addressed_leader
from tools.chatter.config import Config, load_config
from tools.chatter.conversations import ConversationStore
from tools.chatter.leader_roster import LEADERS, civ_for_leader
from tools.chatter.tone import add_percent, prosody_for
from tools.chatter.voice_picker import VoicePicker, VoiceSpec

def _default_human_name() -> str:
    """Default human name = Windows account name. Falls back to 'Player'.

    'You' is a bad default because the LLM treats target.human_name as a
    real name and addresses the user as "You" in the line ("Your greeting
    shows proper grace, You").
    """
    try:
        name = (getpass.getuser() or "").strip()
    except Exception:  # noqa: BLE001
        name = ""
    return name or "Player"


DEFAULT_HUMAN_NAME = _default_human_name()


# ----------------------------------------------------------------------------
# Leader fuzzy-resolution helper for CLI args.

def _resolve_leader_arg(name_arg: str) -> Optional[str]:
    """Resolve a --leader CLI argument via the same fuzzy resolver the game uses.

    Returns the canonical leader_name on success, or None if no match.
    Accepts exact ('Louis XIV'), nickname ('Louie'), or prefix ('Gilg').
    """
    if not name_arg:
        return None
    arg = name_arg.strip()
    # Direct exact (case-insensitive) match wins immediately.
    for leader_name, _civ in LEADERS:
        if leader_name.lower() == arg.lower():
            return leader_name
    # Otherwise run through the fuzzy resolver wrapped in a sentence so token
    # logic engages (the resolver requires >=3-char tokens).
    name, _why = resolve_addressed_leader(arg + ", I greet you.")
    return name


# ----------------------------------------------------------------------------
# Audio playback (Windows winsound; lazy import).

def _play_wav_blocking(path: str, *, logger: logging.Logger) -> None:
    """Play a WAV file synchronously via winsound. Best-effort; never raises.

    We use BLOCKING playback (no SND_ASYNC) so the REPL waits for the line
    to finish before showing the next prompt. Keeps the conversation pacing
    natural -- you don't get the next prompt while the leader is still
    speaking.
    """
    try:
        import winsound  # type: ignore
        winsound.PlaySound(path, winsound.SND_FILENAME)
    except Exception as exc:  # noqa: BLE001
        logger.warning("audio playback failed: %s", exc)


def _save_wav(audio_bytes: bytes) -> str:
    """Write audio bytes to a temp .wav and return the path."""
    fd, path = tempfile.mkstemp(prefix="chatter_test_", suffix=".wav")
    os.close(fd)
    with open(path, "wb") as f:
        f.write(audio_bytes)
    return path


# ----------------------------------------------------------------------------
# CLI session state.

class CliSession:
    """One CLI run's state. Conversation store + active leader + voice cache."""

    def __init__(self, cfg: Config, human_name: str, *, voice_enabled: bool,
                 max_tokens: int, logger: logging.Logger):
        self.cfg = cfg
        self.human_name = human_name or DEFAULT_HUMAN_NAME
        self.voice_enabled = bool(voice_enabled)
        self.max_tokens = int(max_tokens)
        self.logger = logger
        self.session_id = "cli-" + uuid.uuid4().hex[:12]
        self.store = ConversationStore(
            history_seconds=float(cfg.chat_history_seconds),
            max_turns=int(cfg.chat_max_history_turns),
        )
        self.client = AzureClient(
            endpoint=cfg.endpoint,
            api_key=cfg.api_key,
            deployment=cfg.deployment,
            api_version=cfg.api_version,
            request_timeout_seconds=float(cfg.request_timeout_seconds),
        )
        # Voice picker (used only if voice is enabled)
        self.voice_picker: Optional[VoicePicker] = None
        self.speech_client = None
        if self.voice_enabled:
            self._init_voice()
        # Stable per-leader player_id assignment (CLI uses synthetic IDs
        # since there's no real game). Same leader name -> same id within
        # this run, so ConversationStore keys are stable.
        self._leader_ids: dict = {}
        # Active leader for REPL no-name follow-ups.
        self.active_leader: Optional[str] = None

    # -- voice setup ---------------------------------------------------------

    def _init_voice(self) -> None:
        cfg = self.cfg
        # If voice config isn't set up at all, silently disable audio. The
        # CLI still prints text + tone, so it's useful even without voice.
        if not (cfg.voiceover.azure_speech_endpoint and cfg.voiceover.azure_speech_key):
            self.logger.warning(
                "voice disabled: azure_speech_endpoint/key not set in config "
                "(set CHATTER_AZURE_SPEECH_ENDPOINT and CHATTER_AZURE_SPEECH_KEY "
                "or use --no-voice). Continuing in text-only mode."
            )
            self.voice_enabled = False
            return
        try:
            from tools.chatter.azure_speech_client import AzureSpeechClient
            self.voice_picker = VoicePicker(default_voice=cfg.voiceover.azure_speech_voice,
                                            logger=self.logger)
            self.speech_client = AzureSpeechClient(
                endpoint=cfg.voiceover.azure_speech_endpoint,
                key=cfg.voiceover.azure_speech_key,
                default_voice=cfg.voiceover.azure_speech_voice,
                daily_char_cap=int(cfg.voiceover.daily_char_cap),
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("voice init failed (%s); continuing in text-only mode", exc)
            self.voice_enabled = False
            self.voice_picker = None
            self.speech_client = None

    # -- request shaping -----------------------------------------------------

    def _player_id_for(self, leader_name: str) -> int:
        """Synthesize a stable per-leader player_id for the CLI."""
        if leader_name not in self._leader_ids:
            self._leader_ids[leader_name] = len(self._leader_ids) + 1
        return self._leader_ids[leader_name]

    def build_request(self, *, leader_name: str, user_message: str) -> dict:
        civ = civ_for_leader(leader_name) or "Unknown"
        return {
            "schema": 1,
            "request_id": "req-" + uuid.uuid4().hex[:12],
            "session_id": self.session_id,
            "trigger": "CHAT_REPLY",
            "speaker": {
                "leader_name": leader_name,
                "civ_short_name": civ,
                "player_id": self._player_id_for(leader_name),
            },
            "target": {
                "leader_name": "Human Player",
                "human_name": self.human_name,
                "player_id": 0,
            },
            "context": {"user_message": user_message},
        }

    # -- one round-trip ------------------------------------------------------

    def speak_to(self, leader_name: str, user_message: str) -> Tuple[bool, str, str]:
        """Send one user message; print and (optionally) play the AI's reply.

        Returns (ok, line, tone).
        """
        request = self.build_request(leader_name=leader_name, user_message=user_message)
        resp, line, tone = handle_chat_reply(
            request=request, store=self.store, client=self.client,
            max_tokens=self.max_tokens, logger=self.logger,
        )
        if not resp.get("ok"):
            err = resp.get("error", "unknown")
            print("[%s / ERROR / %s]" % (leader_name, err), flush=True)
            return False, "", ""

        pitch_off, rate_off = prosody_for(tone)
        # Show the *effective* prosody (base + tone offset) so we can debug
        # tone modulation just by reading the printed line.
        leader_voice_spec = self._voice_spec_for(leader_name)
        base_rate = leader_voice_spec.rate if leader_voice_spec else self.cfg.voiceover.speech_rate
        base_pitch = leader_voice_spec.pitch if leader_voice_spec else ""
        eff_rate = add_percent(base_rate, rate_off)
        eff_pitch = add_percent(base_pitch, pitch_off)

        print("[%s / %s / pitch=%s rate=%s]" % (
            leader_name, tone, eff_pitch or "0", eff_rate or "0",
        ), flush=True)
        print("  " + line, flush=True)

        if self.voice_enabled and self.speech_client is not None:
            self._play_line(leader_name, line, eff_rate, eff_pitch, leader_voice_spec)

        # Update active partner (REPL no-name follow-ups).
        self.active_leader = leader_name
        return True, line, tone

    def _voice_spec_for(self, leader_name: str) -> Optional[VoiceSpec]:
        if not self.voice_picker:
            return None
        try:
            return self.voice_picker.pick_spec(leader_name)
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("voice picker failed for %s: %s", leader_name, exc)
            return None

    def _play_line(self, leader_name: str, line: str, rate: str, pitch: str,
                   spec: Optional[VoiceSpec]) -> None:
        chosen_voice = spec.voice if spec else self.cfg.voiceover.azure_speech_voice
        locale = (spec.derived_locale() if spec else "") or "en-US"
        try:
            result = self.speech_client.synthesize(
                line, voice=chosen_voice, rate=rate, pitch=pitch, locale=locale,
            )
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("synthesize failed: %s", exc)
            return
        # AzureSpeechClient returns SpeechResult with .audio_bytes.
        audio = getattr(result, "audio_bytes", None)
        if not audio:
            return
        path = _save_wav(audio)
        try:
            _play_wav_blocking(path, logger=self.logger)
        finally:
            try:
                os.remove(path)
            except OSError:
                pass


# ----------------------------------------------------------------------------
# REPL.

REPL_HELP = (
    "Meta commands:\n"
    "  :quit / :q / :exit       leave the REPL\n"
    "  :reset / :clear          clear ALL conversation history\n"
    "  :switch NAME             switch active leader (fuzzy match)\n"
    "  :leader                  show current leader\n"
    "  :history                 print recent turns for the current leader\n"
    "  :voice / :novoice        toggle audio playback\n"
    "  :help / :?               show this list\n"
    "\n"
    "Anything not starting with ':' is sent to the active leader. To talk to\n"
    "a different leader inside one REPL session, use ':switch NAME'.\n"
)


def _run_repl(session: CliSession, initial_leader: str) -> int:
    session.active_leader = initial_leader
    print("Talking to %s. Type ':help' for commands, ':quit' to exit." % initial_leader,
          flush=True)
    while True:
        try:
            user = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n(exit)", flush=True)
            return 0
        if not user:
            continue

        # Meta commands
        if user.startswith(":"):
            cmd_full = user[1:].strip()
            if not cmd_full:
                continue
            parts = cmd_full.split(None, 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            if cmd in ("quit", "q", "exit"):
                return 0
            if cmd in ("reset", "clear"):
                session.store.clear_all()
                print("(history cleared)", flush=True)
                continue
            if cmd in ("help", "?"):
                print(REPL_HELP, flush=True)
                continue
            if cmd == "leader":
                print("(current leader: %s)" % (session.active_leader or "<none>"),
                      flush=True)
                continue
            if cmd == "switch":
                resolved = _resolve_leader_arg(arg)
                if not resolved:
                    print("(no leader matches '%s')" % arg, flush=True)
                    continue
                session.active_leader = resolved
                print("(switched to %s)" % resolved, flush=True)
                continue
            if cmd == "voice":
                # Re-init voice if it wasn't enabled before.
                if not session.voice_enabled:
                    session.voice_enabled = True
                    session._init_voice()
                if session.voice_enabled:
                    print("(voice ON)", flush=True)
                else:
                    print("(voice could not be enabled; check config)", flush=True)
                continue
            if cmd == "novoice":
                session.voice_enabled = False
                print("(voice OFF)", flush=True)
                continue
            if cmd == "history":
                lid = session._player_id_for(session.active_leader)
                msgs = session.store.get_messages((session.session_id, lid))
                if not msgs:
                    print("(no history with %s)" % session.active_leader, flush=True)
                else:
                    print("(history with %s -- %d turns)" % (session.active_leader, len(msgs)),
                          flush=True)
                    for m in msgs:
                        role = m.get("role", "?")
                        content = m.get("content", "")
                        print("  [%s] %s" % (role, content), flush=True)
                continue
            print("(unknown command ':%s'; try ':help')" % cmd, flush=True)
            continue

        # Plain message: try resolving an addressed leader within the line.
        # If found AND different from the current active leader, switch.
        # If not found, fall through to the active leader.
        candidate, why = resolve_addressed_leader(
            user,
            active_partner_name=session.active_leader,
            active_partner_idle_seconds=0,  # CLI: always within window
        )
        if candidate and candidate != session.active_leader and why == "name_match":
            session.active_leader = candidate
            print("(switched to %s)" % candidate, flush=True)
        target_leader = session.active_leader
        if not target_leader:
            print("(no active leader; use ':switch NAME')", flush=True)
            continue
        try:
            session.speak_to(target_leader, user)
        except Exception as exc:  # noqa: BLE001
            print("[ERROR] %s" % exc, flush=True)


# ----------------------------------------------------------------------------
# Entry point.

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chat_test",
        description="DowagerMod chatter CLI test harness (player <-> AI conversation).",
    )
    p.add_argument("--leader", help="Leader to talk to (fuzzy: 'Louie', 'Gilg', 'Louis XIV').")
    p.add_argument("--message", help="One-shot mode: send this message and exit.")
    p.add_argument("--repl", action="store_true",
                   help="Interactive multi-turn REPL. Required if --message is omitted.")
    p.add_argument("--no-voice", action="store_true",
                   help="Skip TTS / audio playback (text-only).")
    p.add_argument("--reset", action="store_true",
                   help="Clear any persisted history before starting (no-op for now).")
    p.add_argument("--list-leaders", action="store_true",
                   help="Print the BTS leader roster and exit.")
    p.add_argument("--max-tokens", type=int, default=None,
                   help="Override chat_reply_max_tokens (default from config).")
    p.add_argument("--human-name", default=DEFAULT_HUMAN_NAME,
                   help="Name the AI sees as the human player (default: 'You').")
    p.add_argument("--debug", action="store_true",
                   help="Verbose logging to stderr.")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    if args.list_leaders:
        for name, civ in LEADERS:
            print("%-22s  %s" % (name, civ))
        return 0

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )
    logger = logging.getLogger("chat_test")

    cfg = load_config()
    if not cfg.endpoint or not cfg.api_key:
        print("ERROR: no chatter API endpoint/key configured. "
              "Set CHATTER_ENDPOINT and CHATTER_API_KEY (or run config.json setup).",
              file=sys.stderr)
        return 2

    if not args.leader:
        print("ERROR: --leader is required (or use --list-leaders).", file=sys.stderr)
        return 2
    leader = _resolve_leader_arg(args.leader)
    if not leader:
        print("ERROR: no leader matches '%s'. Try --list-leaders." % args.leader,
              file=sys.stderr)
        return 2

    voice_enabled = not args.no_voice
    max_tokens = args.max_tokens if args.max_tokens is not None else cfg.chat_reply_max_tokens

    session = CliSession(
        cfg=cfg, human_name=args.human_name,
        voice_enabled=voice_enabled, max_tokens=max_tokens, logger=logger,
    )

    if args.message and args.repl:
        print("ERROR: choose --message OR --repl, not both.", file=sys.stderr)
        return 2

    if args.message is not None:
        ok, _line, _tone = session.speak_to(leader, args.message)
        return 0 if ok else 1

    if args.repl:
        return _run_repl(session, leader)

    print("ERROR: provide --message TEXT (one-shot) or --repl (interactive).",
          file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
