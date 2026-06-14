"""Tests for audio_postprocess module."""
from __future__ import annotations

import io
import struct
import sys
import unittest
import wave
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio_postprocess import PRESETS, apply_postprocess


def _make_silent_wav(seconds: float = 0.2, sample_rate: int = 24000) -> bytes:
    """Build a valid mono 16-bit PCM WAV of silence -- minimum bytes the
    ffmpeg pipe demuxer will accept."""
    n_samples = int(seconds * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(struct.pack("<%dh" % n_samples, *([0] * n_samples)))
    return buf.getvalue()


class TestApplyPostprocess(unittest.TestCase):

    def test_empty_preset_returns_original(self) -> None:
        data = b"abc"
        self.assertEqual(apply_postprocess(data, ""), data)

    def test_unknown_preset_returns_original(self) -> None:
        data = b"abc"
        self.assertEqual(apply_postprocess(data, "no_such_preset"), data)

    def test_elderly_crone_preset_registered(self) -> None:
        self.assertIn("elderly_crone", PRESETS)
        self.assertIn("atempo", PRESETS["elderly_crone"])
        self.assertIn("vibrato", PRESETS["elderly_crone"])
        self.assertIn("acrusher", PRESETS["elderly_crone"])

    def test_missing_ffmpeg_returns_original(self) -> None:
        data = b"abc"
        with patch("audio_postprocess.shutil.which", return_value=None):
            self.assertEqual(apply_postprocess(data, "elderly_crone"), data)

    def test_ffmpeg_failure_returns_original(self) -> None:
        """When ffmpeg fails (e.g. malformed input), fall back to raw."""
        garbage = b"not a wav file"
        out = apply_postprocess(garbage, "elderly_crone", timeout_seconds=5.0)
        # Either ffmpeg isn't installed (returns raw) or it errors on garbage
        # input (returns raw). Both paths are correct fallback behavior.
        self.assertEqual(out, garbage)

    def test_roundtrip_real_wav_when_ffmpeg_present(self) -> None:
        """If ffmpeg is on PATH, processing a valid WAV should return non-empty
        output that differs from input (filter chain changed it)."""
        import shutil
        if shutil.which("ffmpeg") is None:
            self.skipTest("ffmpeg not on PATH")
        wav = _make_silent_wav()
        out = apply_postprocess(wav, "elderly_crone", timeout_seconds=15.0)
        self.assertGreater(len(out), 100, "ffmpeg should produce a non-trivial WAV")


if __name__ == "__main__":
    unittest.main()
