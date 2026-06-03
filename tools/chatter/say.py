"""Make DowagerBot say an arbitrary line in the Discord voice channel.

Standalone one-shot. Bypasses the LLM and the game; talks directly to the
existing Azure Speech + Discord bot infra so you can puppet any leader.

IMPORTANT: Discord only allows one live session per bot token. If the
chatter sidecar (``tools\\Start-Chatter.ps1``) is running, stop it first
(``tools\\Stop-Chatter.ps1``) or your one-shot will kick the sidecar (or
vice-versa).

Usage:
    python -m tools.chatter.say "Taylor is totally shit tier" --leader Victoria
    python -m tools.chatter.say "Hmph." --voice en-US-AndrewNeural
    python -m tools.chatter.say "..." --leader Lincoln --rate -10% --pitch -5%

When ``--leader`` is given the voice and prosody come from
``leader_voices.json``. Explicit ``--voice``/``--rate``/``--pitch`` override
the leader defaults.
"""
from __future__ import annotations

import argparse
import logging
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tools.chatter import config as cfg_mod
from tools.chatter.azure_speech_client import AzureSpeechClient
from tools.chatter.discord_bot import DiscordBotWorker
from tools.chatter.voice_picker import VoicePicker


def main() -> int:
    p = argparse.ArgumentParser(description="Make DowagerBot say a line.")
    p.add_argument("text", help="Text to speak")
    p.add_argument("--leader", default="", help="Leader name (e.g. Victoria) -- resolves voice from leader_voices.json")
    p.add_argument("--voice", default="", help="Override voice (e.g. en-GB-MiaNeural)")
    p.add_argument("--rate", default=None, help='SSML prosody rate (e.g. "-10%"). Empty string = none.')
    p.add_argument("--pitch", default=None, help='SSML prosody pitch (e.g. "-5%"). Empty string = none.')
    p.add_argument("--ready-timeout", type=float, default=30.0, help="Seconds to wait for bot voice-channel connect")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("say")

    cfg = cfg_mod.load_config()
    vo = cfg.voiceover
    if not vo.is_ready():
        log.error("voiceover not configured -- need azure_speech_endpoint/key and discord_bot_token/guild/channel")
        return 2

    # Resolve voice + prosody from --leader if provided, then apply explicit overrides
    voice = vo.azure_speech_voice
    rate = ""
    pitch = ""
    if args.leader:
        picker = VoicePicker(default_voice=vo.azure_speech_voice, logger=log)
        spec = picker.pick_spec(args.leader)
        voice = spec.voice
        rate = spec.rate
        pitch = spec.pitch
        log.info("leader=%s -> voice=%s rate=%r pitch=%r", args.leader, voice, rate, pitch)
    if args.voice:
        voice = args.voice
    if args.rate is not None:
        rate = args.rate
    if args.pitch is not None:
        pitch = args.pitch

    log.info("synthesizing %d chars voice=%s rate=%r pitch=%r", len(args.text), voice, rate, pitch)
    speech = AzureSpeechClient(
        endpoint=vo.azure_speech_endpoint,
        key=vo.azure_speech_key,
        default_voice=voice,
        daily_char_cap=vo.daily_char_cap,
    )
    result = speech.synthesize(args.text, voice=voice, rate=rate, pitch=pitch)
    log.info("speech ok: %d bytes, %d ms", len(result.audio_bytes), result.latency_ms)

    wav_path = Path(tempfile.gettempdir()) / ("dowager_say_%d.wav" % int(time.time()))
    wav_path.write_bytes(result.audio_bytes)
    log.info("wav: %s", wav_path)

    bot = DiscordBotWorker(
        bot_token=vo.discord_bot_token,
        guild_id=int(vo.discord_guild_id),
        voice_channel_id=int(vo.discord_voice_channel_id),
        logger=log,
    )
    bot.start()

    deadline = time.time() + args.ready_timeout
    while time.time() < deadline and not bot.is_ready():
        time.sleep(0.25)
    if not bot.is_ready():
        log.error("discord bot didn't become ready within %.0fs", args.ready_timeout)
        bot.stop()
        return 3
    log.info("bot ready; enqueueing audio")
    bot.enqueue_audio(wav_path)

    # Wait for the audio queue to be picked up (qsize goes from 1 -> 0)
    deadline = time.time() + 10.0
    while time.time() < deadline and bot.queue_size() > 0:
        time.sleep(0.1)
    if bot.queue_size() > 0:
        log.warning("queue never drained; bot may not be processing audio")

    # Wait for ffmpeg+discord to actually start playing
    deadline = time.time() + 15.0
    while time.time() < deadline and not bot.is_playing():
        time.sleep(0.1)
    if not bot.is_playing():
        log.warning("playback never started; expected ffmpeg+voice handshake within 15s")
    else:
        log.info("playback started; waiting for it to finish")

    # Wait for playback to end (is_playing goes False), with a hard cap
    deadline = time.time() + 60.0
    while time.time() < deadline and bot.is_playing():
        time.sleep(0.25)

    # Small grace period so the last audio frame reaches Discord clients
    time.sleep(1.5)

    log.info("stopping bot")
    bot.stop()
    try:
        wav_path.unlink()
    except Exception:
        pass
    log.info("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
