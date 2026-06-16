# Local TTS Server — Zero-Shot Voice Cloning

A standalone FastAPI service that performs zero-shot voice cloning using open-source
models (XTTSv2, Qwen3-TTS). Pass text + a voice ID and get back WAV audio in a
cloned voice.

## Architecture

```
[Chatter Daemon] --POST /synthesize--> [Local TTS Server :8080] --returns WAV-->
                                              |
                                     voice_registry.json
                                              |
                                     voices/dowager_ref.wav  (6-12s reference clip)
```

## Quick Start

```powershell
# 1. Set up the venv (one-time)
.\tools\Setup-TtsServer.ps1          # GPU (CUDA 12.x)
.\tools\Setup-TtsServer.ps1 -CpuOnly # CPU fallback (slower)

# 2. Generate reference audio (uses ElevenLabs — needs .env)
.\tools\Generate-TtsReference.ps1

# 3. Start the server
.\tools\Start-TtsServer.ps1 -Model xtts -Port 8080

# 4. Test
curl http://localhost:8080/health
curl -X POST http://localhost:8080/synthesize -H "Content-Type: application/json" -d '{"text":"Hello","voice_id":"dowager"}' -o test.wav
```

## Models

| Model | VRAM | Speed (GPU) | Quality | Notes |
|-------|------|-------------|---------|-------|
| XTTSv2 | ~2.5 GB | ~1-2s/sentence | Good | Proven, Coqui ecosystem |
| Qwen3-TTS | ~6-8 GB | ~2-4s/sentence | Potentially better | Newer, HuggingFace |

## Voice Registry

`voice_registry.json` maps voice IDs to reference WAV files:

```json
{
  "voices": {
    "dowager": {
      "display_name": "Dowager Countess",
      "reference_wav": "voices/dowager_ref.wav"
    },
    "stalin": {
      "display_name": "Joseph Stalin",
      "reference_wav": "voices/stalin_ref.wav"
    }
  }
}
```

## Adding a New Voice

1. Place a 6-12 second reference WAV in `voices/<name>_ref.wav`
2. Add an entry to `voice_registry.json`
3. In `leader_voices.json`, set `"tts_provider": "local"` for that leader
4. Set `LOCAL_TTS_URL=http://<server-ip>:8080` in `.env`

## Reference Audio Best Practices

- **Duration**: 6-12 seconds (sweet spot for zero-shot quality)
- **Quality**: Clean, single speaker, no background noise
- **Content**: Varied intonation that represents the character
- **Format**: 24 kHz mono 16-bit PCM WAV
- **Generate**: Use `Generate-TtsReference.ps1` to create from ElevenLabs

## Chatter Integration

The chatter daemon uses this as a TTS provider (`"local"`) with the priority chain:
`local → elevenlabs → azure`

If the local server is not running (connection refused), the dispatcher's circuit
breaker trips immediately and falls through to the next provider — no timeout delay.

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
- `X-Model`: model backend (xtts/qwen3)

## Network Deployment

The server binds to `0.0.0.0` by default — accessible from other machines on LAN.
Point the chatter daemon's `LOCAL_TTS_URL` at `http://<desktop-ip>:8080` to run
the model on a beefy desktop while the game runs on a different machine.
