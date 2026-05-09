"""End-to-end Discord bot smoke test for DowagerMod Chatter voiceover.

Connects to your configured Discord voice channel, plays one TTS line
(via Azure Speech), then disconnects. Reads everything from .env.

Usage:

    python tools/chatter/test_discord_bot.py

You should be in the configured voice channel BEFORE running this. The
bot will join, you'll hear the test phrase, then it will leave.

Exit 0 on success, non-zero with diagnostic on failure.
"""
from __future__ import annotations

import asyncio
import os
import sys
import time
from pathlib import Path

# Make tools/chatter importable when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
RESET = "\033[0m"


def _need(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        print(f"{RED}FAIL: {name} not set in env or .env{RESET}")
        sys.exit(2)
    return v


async def _run_test() -> int:
    # 1. Synthesize a test phrase via Speech
    test_text = (
        "Greetings, civilizations of the world. The Court Herald has arrived. "
        "Tremble before my synthesized eloquence."
    )
    speech_endpoint = _need("DOWAGER_CHATTER_SPEECH_ENDPOINT")
    speech_key = _need("DOWAGER_CHATTER_SPEECH_KEY")
    speech_voice = os.environ.get("DOWAGER_CHATTER_SPEECH_VOICE", "en-US-AriaNeural").strip()
    bot_token = _need("DOWAGER_CHATTER_DISCORD_BOT_TOKEN")
    guild_id_str = _need("DOWAGER_CHATTER_DISCORD_GUILD_ID")
    channel_id_str = _need("DOWAGER_CHATTER_DISCORD_VOICE_CHANNEL_ID")

    try:
        guild_id = int(guild_id_str)
        channel_id = int(channel_id_str)
    except ValueError:
        print(f"{RED}FAIL: guild ID or channel ID is not numeric{RESET}")
        return 2

    print(f"  Speech endpoint: {speech_endpoint}")
    print(f"  Voice:           {speech_voice}")
    print(f"  Guild ID:        {guild_id}")
    print(f"  Channel ID:      {channel_id}")
    print()

    print(f"{YELLOW}Step 1: Synthesizing test phrase...{RESET}")
    from tools.chatter.azure_speech_client import AzureSpeechClient
    sc = AzureSpeechClient(
        endpoint=speech_endpoint, key=speech_key,
        default_voice=speech_voice, request_timeout_seconds=15.0,
        daily_char_cap=10000,
    )
    try:
        result = sc.synthesize(test_text)
    except Exception as exc:  # noqa: BLE001
        print(f"{RED}FAIL: TTS synthesize raised: {exc}{RESET}")
        return 3

    wav_path = Path("test_discord_audio.wav").resolve()
    wav_path.write_bytes(result.audio_bytes)
    print(f"  {GREEN}OK{RESET} synthesized {result.char_count} chars, {len(result.audio_bytes)} bytes -> {wav_path.name}")

    # 2. Connect Discord bot, join voice channel, play, disconnect
    print()
    print(f"{YELLOW}Step 2: Connecting Discord bot...{RESET}")
    import discord

    intents = discord.Intents.default()
    intents.guilds = True
    intents.voice_states = True
    client = discord.Client(intents=intents)

    done_event = asyncio.Event()
    overall_ok = {"ok": False, "msg": ""}

    @client.event
    async def on_ready():
        try:
            print(f"  {GREEN}OK{RESET} bot ready as {client.user}")
            guild = discord.utils.get(client.guilds, id=guild_id)
            if guild is None:
                overall_ok["msg"] = (
                    f"guild_id {guild_id} not found in client guilds. "
                    f"Bot is in: {[(g.id, g.name) for g in client.guilds]}"
                )
                await client.close()
                return
            channel = discord.utils.get(guild.voice_channels, id=channel_id)
            if channel is None:
                overall_ok["msg"] = (
                    f"voice_channel_id {channel_id} not found in guild {guild.name}. "
                    f"Voice channels: {[(c.id, c.name) for c in guild.voice_channels]}"
                )
                await client.close()
                return
            print(f"  {GREEN}OK{RESET} resolved guild='{guild.name}' channel='{channel.name}'")

            print(f"  {YELLOW}Connecting to voice channel...{RESET}")
            voice_client = await channel.connect(reconnect=False)
            print(f"  {GREEN}OK{RESET} voice connected")

            print(f"  {YELLOW}Playing test phrase (you should hear it now)...{RESET}")
            playback_done = asyncio.Event()
            loop = asyncio.get_event_loop()

            def _after(err):
                if err:
                    overall_ok["msg"] = f"playback error: {err}"
                loop.call_soon_threadsafe(playback_done.set)

            source = discord.FFmpegPCMAudio(str(wav_path))
            voice_client.play(source, after=_after)

            try:
                await asyncio.wait_for(playback_done.wait(), timeout=30.0)
                print(f"  {GREEN}OK{RESET} playback finished")
                overall_ok["ok"] = True
            except asyncio.TimeoutError:
                overall_ok["msg"] = "playback timed out after 30s"

            print(f"  {YELLOW}Disconnecting...{RESET}")
            await voice_client.disconnect()
            await client.close()
        except Exception as exc:  # noqa: BLE001
            overall_ok["msg"] = f"on_ready exception: {type(exc).__name__}: {exc}"
            try:
                await client.close()
            except Exception:
                pass

    try:
        await client.start(bot_token)
    except discord.errors.LoginFailure as exc:
        print(f"{RED}FAIL: Discord login failed: {exc}{RESET}")
        print(f"{YELLOW}  -> Bot token is wrong or has been reset. Reset token in Discord dev portal and update .env.{RESET}")
        return 4
    except Exception as exc:  # noqa: BLE001
        if "ok" not in overall_ok or not overall_ok["ok"]:
            if not overall_ok["msg"]:
                overall_ok["msg"] = f"client.start raised: {exc}"

    print()
    print("===== Summary =====")
    if overall_ok["ok"]:
        print(f"{GREEN}PASS: Discord bot connected, played test phrase, disconnected.{RESET}")
        print()
        print(f"{YELLOW}Did you hear the test phrase in your Discord voice channel?{RESET}")
        print(f"{YELLOW}If yes -> voiceover is fully wired. Run Stop-Chatter + Start-Chatter and play Civ4.{RESET}")
        print(f"{YELLOW}If no -> check that you joined the voice channel BEFORE running this test.{RESET}")
        return 0
    else:
        print(f"{RED}FAIL: {overall_ok['msg']}{RESET}")
        return 5


def main() -> int:
    try:
        from tools.chatter.dotenv import load_dotenv
        loaded = load_dotenv()
        if loaded:
            print(f"  (loaded env from {loaded})")
    except Exception as exc:  # noqa: BLE001
        print(f"  (warning: dotenv loader failed: {exc})")
    print()

    # Quick check that voiceover is enabled
    enabled = os.environ.get("DOWAGER_CHATTER_VOICEOVER_ENABLED", "").lower() in ("1", "true", "yes", "on")
    if not enabled:
        print(f"{YELLOW}Note: DOWAGER_CHATTER_VOICEOVER_ENABLED is not 'true' in .env.{RESET}")
        print(f"{YELLOW}      The smoke test will still run but the sidecar daemon will skip voiceover.{RESET}")
        print()

    try:
        return asyncio.run(_run_test())
    except KeyboardInterrupt:
        print(f"{YELLOW}Interrupted.{RESET}")
        return 130


if __name__ == "__main__":
    sys.exit(main())
