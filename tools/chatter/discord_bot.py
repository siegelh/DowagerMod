"""Discord bot worker for the DowagerMod Chatter sidecar voiceover.

Runs the bot in a dedicated background thread (the bot needs its own
asyncio loop). The chatter daemon enqueues WAV file paths via
``enqueue_audio(path)``; the bot plays them in the configured voice
channel, one at a time, in arrival order.

Imports of ``discord`` are deferred so that an environment without
``discord.py`` installed can still load this module — the bot just
fails to start and logs a warning, leaving text chatter unaffected.
"""
from __future__ import annotations

import asyncio
import logging
import queue
import threading
import time
from pathlib import Path
from typing import Optional


class _DiscordBotUnavailable(Exception):
    """discord.py not installed or otherwise unimportable."""


def _import_discord():
    try:
        import discord  # type: ignore
    except ImportError as exc:  # noqa: F841
        raise _DiscordBotUnavailable(
            "discord.py not installed. Run: pip install -U \"discord.py[voice]\""
        )
    return discord


class DiscordBotWorker:
    """Background-thread Discord bot. Plays WAV files in a voice channel.

    Public API (thread-safe):
      - start()                : start the worker thread
      - is_ready()             : True once bot has connected to the voice channel
      - enqueue_audio(path)    : queue a WAV file for playback
      - stop()                 : disconnect + stop the thread
    """

    def __init__(
        self,
        *,
        bot_token: str,
        guild_id: int,
        voice_channel_id: int,
        logger: Optional[logging.Logger] = None,
    ):
        self.bot_token = bot_token
        self.guild_id = int(guild_id)
        self.voice_channel_id = int(voice_channel_id)
        self.logger = logger or logging.getLogger("dowager.chatter.discord")

        self._audio_q: "queue.Queue[Optional[Path]]" = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._client = None
        self._voice_client = None
        self._ready_event = threading.Event()
        self._stop_event = threading.Event()
        self._message_handler = None  # set via set_message_handler

    # ---------- public, thread-safe API ----------

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._thread = threading.Thread(target=self._run, name="DowagerChatterDiscordBot", daemon=True)
        self._thread.start()

    def is_ready(self) -> bool:
        return self._ready_event.is_set()

    def is_playing(self) -> bool:
        """True iff the bot has an active voice client currently playing audio."""
        vc = self._voice_client
        try:
            return bool(vc and vc.is_connected() and vc.is_playing())
        except Exception:
            return False

    def queue_size(self) -> int:
        """Number of audio items waiting in the playback queue (excludes the one currently playing)."""
        try:
            return self._audio_q.qsize()
        except Exception:
            return 0

    def enqueue_audio(self, path: Path) -> None:
        if self._stop_event.is_set():
            return
        self._audio_q.put(path)

    def set_message_handler(self, handler) -> None:
        """Register a callback fired whenever a user @mentions the bot or DMs it.

        Signature: ``handler(text: str, author_name: str, author_id: int, is_dm: bool) -> None``

        Called on the bot's asyncio thread. The handler must be fast and
        non-blocking — schedule any synth/IO on a background thread itself.
        Exceptions are caught and logged.
        """
        self._message_handler = handler

    def stop(self) -> None:
        self._stop_event.set()
        # Sentinel to break the playback loop
        self._audio_q.put(None)
        if self._loop is not None and self._client is not None:
            try:
                asyncio.run_coroutine_threadsafe(self._client.close(), self._loop).result(timeout=5)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("discord stop: close failed: %s", exc)
        if self._thread is not None:
            self._thread.join(timeout=10)

    # ---------- internal, runs in worker thread ----------

    def _run(self) -> None:
        try:
            discord = _import_discord()
        except _DiscordBotUnavailable as exc:
            self.logger.warning("discord bot disabled: %s", exc)
            return

        intents = discord.Intents.default()
        intents.guilds = True
        intents.voice_states = True
        intents.messages = True
        # NOTE: message_content is a privileged intent and is NOT required
        # for our use case — Discord delivers full content for messages that
        # mention the bot or are DMs to it, even without the intent.
        client = discord.Client(intents=intents)
        self._client = client

        @client.event
        async def on_ready():
            self.logger.info("discord bot ready as %s", client.user)
            await self._connect_voice_and_drain(discord)

        @client.event
        async def on_message(msg):
            try:
                # Ignore the bot's own messages and other bots
                if msg.author.id == client.user.id or getattr(msg.author, "bot", False):
                    return
                is_dm = msg.guild is None
                mentioned = False
                try:
                    mentioned = client.user in (msg.mentions or [])
                except Exception:
                    mentioned = False
                if not (is_dm or mentioned):
                    return
                text = msg.content or ""
                # Strip the bot mention so we only speak the actual prompt
                if mentioned:
                    for mid in (client.user.id,):
                        text = text.replace("<@%d>" % mid, "").replace("<@!%d>" % mid, "")
                text = text.strip()
                if not text:
                    return
                handler = self._message_handler
                if handler is None:
                    return
                try:
                    handler(text, str(msg.author), int(msg.author.id), bool(is_dm))
                except Exception as exc:  # noqa: BLE001
                    self.logger.warning("discord bot: message handler raised: %s", exc)
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("discord bot: on_message failed: %s", exc)

        # Run client until stop_event is set
        loop = asyncio.new_event_loop()
        self._loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(client.start(self.bot_token))
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("discord bot exited with error: %s", exc)
        finally:
            try:
                loop.close()
            except Exception:
                pass
            self._ready_event.clear()

    async def _connect_voice_and_drain(self, discord) -> None:
        try:
            guild = discord.utils.get(self._client.guilds, id=self.guild_id)
            if guild is None:
                self.logger.warning("discord bot: guild_id %s not found in client guilds", self.guild_id)
                return
            channel = discord.utils.get(guild.voice_channels, id=self.voice_channel_id)
            if channel is None:
                self.logger.warning(
                    "discord bot: voice_channel_id %s not found in guild %s", self.voice_channel_id, guild.name
                )
                return
            self._voice_client = await channel.connect(reconnect=True)
            self.logger.info("discord bot connected to voice channel: %s / %s", guild.name, channel.name)
            self._ready_event.set()
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("discord bot voice connect failed: %s", exc)
            return

        # Playback loop: blocking queue read on a thread, posted into the loop
        while not self._stop_event.is_set():
            path = await asyncio.get_event_loop().run_in_executor(None, self._audio_q.get)
            if path is None:
                break
            await self._play_one(discord, path)

    async def _play_one(self, discord, path: Path) -> None:
        if not self._voice_client or not self._voice_client.is_connected():
            self.logger.info("discord bot: voice client not connected; dropping %s", path.name)
            return
        try:
            source = discord.FFmpegPCMAudio(str(path))
        except Exception as exc:  # noqa: BLE001
            self.logger.warning("discord bot: FFmpegPCMAudio failed for %s: %s", path, exc)
            return

        done_event = asyncio.Event()

        def _after(err):
            if err:
                self.logger.warning("discord bot: playback error: %s", err)
            try:
                self._loop.call_soon_threadsafe(done_event.set)
            except Exception:
                pass

        try:
            self._voice_client.play(source, after=_after)
        except discord.errors.ClientException as exc:
            self.logger.info("discord bot: skipping (already playing): %s", exc)
            return

        # Wait for playback to finish, with a generous safety timeout
        try:
            await asyncio.wait_for(done_event.wait(), timeout=60.0)
        except asyncio.TimeoutError:
            self.logger.warning("discord bot: playback timeout, stopping current source")
            try:
                self._voice_client.stop()
            except Exception:
                pass
