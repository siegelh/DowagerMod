# Local TTS Server — Zero-Shot Voice Cloning

A standalone FastAPI service that performs zero-shot voice cloning using XTTSv2
or Chatterbox Turbo. Pass text + a voice ID and get back WAV audio in a cloned
voice — no training or fine-tuning required.

## How It Works

Both backends are **zero-shot** models. You provide a 6-12 second reference WAV of
the voice you want to clone. At synthesis time, the model listens to that reference
and generates speech in that style on the fly. There is no per-voice training step.

### Model Backends

| Backend | Package | VRAM | Quality | Latency | Notes |
|---------|---------|------|---------|---------|-------|
| **xtts** (default) | Coqui TTS | ~2.5-4 GB | Good | ~2-4s | Lighter, runs on laptops |
| **chatterbox** | chatterbox-tts | ~6-8 GB | Excellent | ~1-3s | Best clone fidelity, needs more VRAM |

Choose your backend by setting `TTS_MODEL` in `.env`:
```ini
TTS_MODEL=xtts         # default — lighter, for laptops or lower VRAM
TTS_MODEL=chatterbox   # higher quality, needs RTX 4080 or similar (≥8GB VRAM)
```

**What lives in git (works on every machine after `git pull`):**
- `voice_registry.json` — maps voice IDs → reference WAVs + transcripts
- `voices/*.wav` — reference audio clips (6-12s each, ~500KB)

**What each machine needs (one-time `Setup-TtsServer.ps1`):**
- Python 3.10+ venv with torch + CUDA
- Model weights (downloaded automatically on first run)
- GPU with sufficient VRAM (see table above) or CPU mode (much slower)

## Fresh Machine Setup

```powershell
# 1. Clone/pull the repo
git pull

# 2. One-time setup (creates venv, installs deps, downloads model)
#    Default (XTTSv2 — lighter, works on laptops):
.\tools\Setup-TtsServer.ps1

#    Or for higher quality (Chatterbox Turbo — needs ≥8GB VRAM):
.\tools\Setup-TtsServer.ps1 -Model chatterbox
#    Then set TTS_MODEL=chatterbox in your .env

# 3. Start the server (reads TTS_MODEL from .env)
.\tools\Start-TtsServer.ps1

# 4. Verify (in another terminal)
.\tools\Test-TtsVoice.ps1
```

That's it. All registered voices work immediately.

### Switching Models

To switch between backends on the same machine:
```powershell
# Switch to Chatterbox (rebuilds venv automatically):
.\tools\Setup-TtsServer.ps1 -Model chatterbox
# Update .env: TTS_MODEL=chatterbox

# Switch back to XTTSv2:
.\tools\Setup-TtsServer.ps1 -Model xtts
# Update .env: TTS_MODEL=xtts
```

The setup script detects when you're switching and rebuilds the venv with the
correct dependencies (~3-5 minutes).

## Architecture

```
[Chatter Daemon] --POST /synthesize--> [Local TTS Server :8080] --returns WAV-->
                                              |
                                     voice_registry.json
                                              |
                                     voices/dowager_ref.wav  (6-12s reference clip)
```

## Adding a New Leader Voice

Use the interactive wizard:

```powershell
.\tools\Add-TtsVoice.ps1
```

The wizard:
1. Asks for voice ID and display name
2. Takes reference audio (existing WAV or generates via ElevenLabs)
3. Asks for the **verbatim transcript** of what's said in the reference
4. Copies/resamples the WAV to `voices/`
5. Updates `voice_registry.json`
6. Wires `leader_voices.json` (if matching leaders found)
7. Opens an interactive audition — type anything to hear it

Or non-interactive:
```powershell
.\tools\Add-TtsVoice.ps1 -VoiceId "tokugawa" -DisplayName "Tokugawa Ieyasu" `
    -RefWav "C:\path\to\ref.wav" `
    -Transcript "The patience of the wise outlasts the fury of the reckless."
```

Then commit + push. Every machine with `git pull` now has the voice.

## Testing Voices

```powershell
# Quick smoke test (synthesize + play)
.\tools\Test-TtsVoice.ps1 -VoiceId dowager

# Test all registered voices
.\tools\Test-TtsVoice.ps1

# Interactive audition — type anything, hear it
.\tools\Test-TtsVoice.ps1 -VoiceId dowager -Interactive
```

## Reference Audio Best Practices

- **Duration**: 6-12 seconds (sweet spot for both XTTSv2 and Chatterbox quality)
- **Quality**: Clean, single speaker, no background noise or music
- **Content**: Varied intonation that represents the character's personality
- **Format**: Any WAV (auto-resampled to 24 kHz mono 16-bit)
- **Transcript**: Always record what was said — used by some models for better cloning
- **Generate**: Use `.\tools\Generate-TtsReference.ps1` to create from ElevenLabs

## Voice Registry Format

`voice_registry.json`:
```json
{
  "voices": {
    "dowager": {
      "display_name": "Dowager Countess",
      "reference_wav": "voices/dowager_ref.wav",
      "reference_transcript": "I have always found that...",
      "description": "Elderly aristocratic British lady."
    },
    "tokugawa": {
      "display_name": "Tokugawa Ieyasu",
      "reference_wav": "voices/tokugawa_ref.wav",
      "reference_transcript": "The patience of the wise...",
      "description": "Feudal Japanese shogun."
    }
  },
  "default_voice": "dowager"
}
```

## Chatter Integration

The chatter daemon uses this as a TTS provider with the priority chain:
`local → elevenlabs → azure`

If the local server is not running (connection refused), the dispatcher's circuit
breaker trips immediately and falls through to the next provider — no timeout delay.

Set in `.env`:
```ini
DOWAGER_CHATTER_LOCAL_TTS_URL=http://localhost:8080
DOWAGER_CHATTER_LOCAL_TTS_VOICE_ID_DOWAGER=dowager

# Local TTS model backend (xtts or chatterbox)
TTS_MODEL=xtts
```

## API Reference

### `GET /health`
Returns server status, loaded model, and available voices.

### `POST /synthesize`
```json
{"text": "Hello world", "voice_id": "dowager"}
```
Returns: `audio/wav` (24 kHz mono 16-bit PCM)

Response headers:
- `X-Latency-Ms`: synthesis time in milliseconds
- `X-Voice-Id`: voice used
- `X-Model`: model backend

## Network Deployment

The server binds to `0.0.0.0` by default — accessible from other machines on LAN.
Point the chatter daemon's `LOCAL_TTS_URL` at `http://<desktop-ip>:8080` to run
the model on a beefy desktop while the game runs on a different machine.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `Start-TtsServer.ps1` fails preflight | Follow the `[FAIL]` messages — each has a fix command |
| CUDA not available | Install CUDA Toolkit 12.x, then re-run `Setup-TtsServer.ps1` |
| Model download stalls | Check network; re-run `Setup-TtsServer.ps1` (idempotent) |
| "Out of memory" on GPU | Switch to `TTS_MODEL=xtts` (lighter) or use `-Device cpu` |
| Voice sounds wrong | Try a different reference WAV (6-12s, clean, expressive) |
| Port already in use | Use `-Port 8081` or stop the other process |
| Switching models | Run `Setup-TtsServer.ps1 -Model <name>` — venv auto-rebuilds |

## Performance

### XTTSv2 (default)
| GPU | Speed | Notes |
|-----|-------|-------|
| RTX A2000 (4GB) | ~3s/sentence | Laptop, tight on VRAM |
| RTX 3080 Ti (12GB) | ~1-2s/sentence | Desktop, comfortable |
| RTX 4080 (16GB) | ~1s/sentence | Desktop, fast |
| CPU (no GPU) | ~15-30s/sentence | Emergency fallback only |

### Chatterbox Turbo
| GPU | Speed | Notes |
|-----|-------|-------|
| RTX 3060 (6GB) | ~3-4s/sentence | Minimum viable |
| RTX 3080 Ti (12GB) | ~1-2s/sentence | Comfortable |
| RTX 4080 (16GB) | ~1s/sentence | Recommended |
| CPU (no GPU) | ~20-40s/sentence | Not recommended |

