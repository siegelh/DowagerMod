# TTS Server: Robust Install & Voice Pipeline

- Status: `draft`
- Owner / agent: @hasiegel + Copilot
- Last updated: `2026-06-16`

## Problem Statement

- Task: Make the local TTS server install process self-guiding on a fresh machine, and make adding new leader voices a one-command experience.
- Current observed behavior: `Start-TtsServer.ps1` only checks if venv exists. No validation of CUDA, GPU availability, model download status, reference audio presence, or leader wiring. Adding a new voice requires 4+ manual edits across files.
- Why this is a real repo/code problem: Any collaborator (or the user on a new machine after `git pull`) hits a confusing failure wall. The voice pipeline is powerful but undocumented as a workflow.

## How Zero-Shot Voice Cloning Works (Key Design Fact)

XTTSv2 is a **zero-shot** model. There is NO training, fine-tuning, or per-machine
GPU work needed per voice. The model listens to a short reference WAV at synthesis
time and produces speech in that style on the fly.

**What lives in git (persists across machines):**
- `tools/tts-server/voice_registry.json` — maps voice IDs → reference WAVs + metadata
- `tools/tts-server/voices/<id>_ref.wav` — 6-12 second reference clips (committed)
- `tools/chatter/leader_voices.json` — leader → voice spec wiring

**What each machine needs (one-time setup via `Setup-TtsServer.ps1`):**
- Python 3.10+ venv with torch + CUDA
- XTTSv2 model weights (~1.7 GB, cached in `~/.local/share/tts/`)
- A GPU with ≥2.5 GB VRAM (or CPU mode, slower)

**Result:** After `git pull` + `Setup-TtsServer.ps1` on any machine, ALL registered
voices work immediately. No re-training. No voice-specific setup. The ref WAVs
travel with the repo.

### Adding Tokugawa (example walkthrough):
```
.\tools\Add-TtsVoice.ps1
> Voice ID: tokugawa
> Display name: Tokugawa Ieyasu
> Reference audio source: [B] Use existing WAV file
> Path: C:\Users\you\Downloads\tokugawa_sample.wav
> What is said in this audio? (verbatim transcript):
> The patience of the wise outlasts the fury of the reckless. Those who
> strike first often find themselves striking last.
  ✓ Resampled to 24kHz mono → voices/tokugawa_ref.wav
  ✓ Added to voice_registry.json (with transcript)
  ✓ Found leader "tokugawa" in leader_voices.json — set tts_provider
  ✓ Added local_tts_voice_id mapping in config.py / daemon

  🎧 Audition mode — type anything to hear it, or press Enter to finish:
  > The patience of the wise outlasts the fury of the reckless.
  🔊 Playing... (2.9s)
  > You dare insult me? I will burn your cities to ash.
  🔊 Playing... (3.1s)
  > [Enter]

All done! Commit + push. Every machine with `git pull` now has Tokugawa.
```

The transcript is stored in `voice_registry.json` alongside the WAV path:
```json
{
  "tokugawa": {
    "display_name": "Tokugawa Ieyasu",
    "reference_wav": "voices/tokugawa_ref.wav",
    "reference_transcript": "The patience of the wise outlasts...",
    "description": "..."
  }
}
```
This future-proofs us for models like Qwen3-TTS that require verbatim transcript
for in-context learning (ICL) mode to achieve highest quality cloning.

## Why This Matters

- User or gameplay impact: Faster iteration on new leaders, less friction deploying to desktop.
- Maintenance / workflow / agent impact: Self-documenting scripts reduce support burden; agents can run the wizard programmatically.

## Scope

- In scope: Smart startup prereq checks with guided remediation
- In scope: `Add-TtsVoice.ps1` interactive wizard (ref audio → registry → leader wiring → audition)
- In scope: Model pre-download step in Setup
- In scope: `Test-TtsVoice.ps1` end-to-end voice validation
- In scope: Updated README and docs

## Non-Goals

- Not changing: The TTS server Python code / FastAPI endpoints
- Not changing: The dispatcher/circuit-breaker architecture (already done)
- Not changing: ElevenLabs or Azure integration
- Not changing: Qwen3-TTS support — XTTSv2 is the only supported model for now.
  Qwen3 is stubbed in server.py but never tested, needs 6-8GB VRAM (won't fit
  A2000), and has a `transformers<4.44` pin conflict. Future desktop-only experiment.

## Trusted Sources Of Truth

- Primary code/config/scripts:
  - `tools/tts-server/server.py` — FastAPI server
  - `tools/tts-server/voice_registry.json` — voice ID → ref WAV mapping
  - `tools/tts-server/requirements.txt` — Python deps
  - `tools/Setup-TtsServer.ps1` — venv creation
  - `tools/Start-TtsServer.ps1` — server launcher
  - `tools/Generate-TtsReference.ps1` — ElevenLabs ref audio generator
  - `tools/chatter/leader_voices.json` — leader → voice spec (106 entries)
  - `tools/chatter/config.py` — `local_tts_voice_id_*` fields
- Runtime entrypoints/import paths to verify:
  - `tools/tts-server/.venv/Scripts/python.exe`
  - CUDA toolkit availability via `torch.cuda.is_available()`
- Validation scripts/tests/hooks:
  - `tools/test_gate.ps1`
  - `python -m pytest tools/chatter/tests/`

## Existing Docs / Plans Trust Review

- Reviewed docs/plans:
  - `tools/tts-server/README.md` — `trusted for this task` (accurate Quick Start)
  - `docs/plans/active/2026-05-03-leader-chatter.md` — `useful context only` (broader chatter scope)
- Conflicts with code/config/scripts: None

## Affected Files / Directories

- Primary implementation paths:
  - `tools/Start-TtsServer.ps1` (enhance with prereq checks)
  - `tools/Setup-TtsServer.ps1` (add model pre-download step)
  - `tools/Add-TtsVoice.ps1` (NEW — voice wizard)
  - `tools/Test-TtsVoice.ps1` (NEW — voice validation)
  - `tools/tts-server/README.md` (update docs)
- Adjacent paths to inspect:
  - `tools/chatter/leader_voices.json`
  - `tools/chatter/config.py`
  - `tools/tts-server/voice_registry.json`
- Paths to avoid unless evidence requires them:
  - `tools/tts-server/server.py` (working, don't touch)
  - `tools/chatter/tts_dispatcher.py` (just committed, stable)

## Proposed Implementation Steps

### 0. Commit Reference WAVs to Git

Currently `voices/.gitignore` has `*.wav` — all ref audio is excluded. Fix:
- Change `.gitignore` to only ignore test outputs (`test_*.wav`)
- Commit `dowager_ref.wav` (and future voices) directly
- ~500KB per voice × ~20 leaders max = ~10MB total — fine for git, no LFS needed

This is the foundation: after `git pull`, all voices are present on every machine.

### 1. Smart `Start-TtsServer.ps1` — Prereq Validation

Enhance the startup script with a preflight checklist that checks each requirement and provides clear remediation:

```
[CHECK] Python 3.10+ .............. OK (3.11.9)
[CHECK] Venv exists ............... OK
[CHECK] torch + CUDA .............. OK (torch 2.6.0+cu124, CUDA available)
[CHECK] XTTSv2 model cached ...... OK (~/.local/share/tts/...)
[CHECK] voice_registry.json ...... OK (1 voice registered)
[CHECK] Reference audio present ... OK (voices/dowager_ref.wav)
[CHECK] Port 8080 available ...... OK

Starting server...
```

If any check fails, print the fix command and exit:
```
[FAIL] Venv not found.
  Fix: .\tools\Setup-TtsServer.ps1
```

### 2. Model Pre-Download in `Setup-TtsServer.ps1`

Add an optional `-DownloadModel` switch (default ON) that pulls the XTTSv2 model weights during setup rather than on first synthesis:

```powershell
# At end of Setup-TtsServer.ps1:
Write-Host "Downloading XTTSv2 model (~1.7 GB)..."
& $python -c "from TTS.api import TTS; TTS('tts_models/multilingual/multi-dataset/xtts_v2')"
```

This eliminates the surprise wait on first server start.

### 3. `Add-TtsVoice.ps1` — Interactive Voice Wizard

A guided script that handles the full pipeline:

```powershell
.\tools\Add-TtsVoice.ps1

# Interactive flow:
# 1. What's the voice ID? (e.g., "stalin", "gandhi")
# 2. What's the display name? (e.g., "Joseph Stalin")
# 3. Reference audio source:
#    [A] Record from ElevenLabs (uses Generate-TtsReference.ps1)
#    [B] Use existing WAV file (provide path)
#    [C] Record from microphone (future)
# 4. If using Qwen3-TTS: enter verbatim transcript of reference audio
# 5. Copies ref WAV to voices/<id>_ref.wav (resamples to 24kHz mono if needed)
# 6. Adds entry to voice_registry.json
# 7. Asks: Wire to leader_voices.json? (shows matching leaders by fuzzy name)
# 8. Adds local_tts_voice_id_<name> to config.py pattern (if new leader)
# 9. Runs audition: synthesizes a test line and plays it
# 10. Prints summary of all changes made
```

Also supports non-interactive mode for scripting:
```powershell
.\tools\Add-TtsVoice.ps1 -VoiceId "stalin" -DisplayName "Joseph Stalin" -RefWav "C:\path\to\ref.wav" -NoAudition
```

### 4. `Test-TtsVoice.ps1` — End-to-End Validation

Quick smoke test for a registered voice:

```powershell
.\tools\Test-TtsVoice.ps1 -VoiceId dowager

# Output:
# [1/3] Checking server health ... OK (model=xtts, 1 voices)
# [2/3] Synthesizing test line ... OK (2.8s, 47KB WAV)
# [3/3] Playing audio ............ (plays via default player)
#
# Voice "dowager" is working. Output: tools/tts-server/test_dowager.wav
```

Options:
- `-VoiceId` — which voice to test (default: all registered)
- `-Text` — custom test line (default: characteristic phrase per voice)
- `-NoPlay` — skip playback, just validate synthesis succeeds
- `-ServerUrl` — override (default: http://localhost:8080)
- `-Interactive` — enters a REPL loop: type any text, hear it immediately, repeat until blank line

Interactive mode example:
```
.\tools\Test-TtsVoice.ps1 -VoiceId dowager -Interactive

# [health OK, model=xtts]
# 🎧 Interactive audition for "dowager" — type text to hear, blank line to quit:
# > One does wonder what they teach in schools these days.
# 🔊 Playing... (2.4s)
# > How perfectly dreadful.
# 🔊 Playing... (1.8s)
# >
# Done.
```

### 5. Documentation Updates

- Update `tools/tts-server/README.md` with:
  - "Fresh Machine Setup" section (git pull → Setup → Start → verify)
  - "Adding a New Leader Voice" section referencing the wizard
  - Troubleshooting section (common CUDA issues, model download failures)
- Add entry to `docs/index.md`

## Validation Plan

- Required automated checks:
  - `python -m pytest tools/chatter/tests/` — all existing tests pass
  - `.\tools\test_gate.ps1`
- Required manual smoke test:
  - Run `Setup-TtsServer.ps1` on existing venv (idempotent check)
  - Run `Start-TtsServer.ps1` and verify all preflight checks pass
  - Run `Test-TtsVoice.ps1 -VoiceId dowager` end-to-end
  - Run `Add-TtsVoice.ps1` with a dummy voice to exercise the wizard flow
- Validation blocked or not yet runnable:
  - LAN deployment test (needs desktop machine)

## Documentation Updates Required

- Docs to update: `tools/tts-server/README.md`
- Docs/plans to mark stale: none
- `docs/index.md`: add link to TTS server README
- Runbook updates: mention `Start-TtsServer.ps1` prereq checks in `CHATTER_RUNBOOK.md`

## Risks / Rollback

- Main risks: Model download step in Setup could fail on network issues (already handles gracefully with error message)
- Likely failure modes: CUDA version mismatch (Setup detects, prints fix)
- Safe rollback: All changes are additive scripts; old workflow still works
- Paths that should not be touched during rollback: `server.py`, `tts_dispatcher.py`

## Open Questions

- Should `Add-TtsVoice.ps1` edit `config.py` programmatically (adding new `local_tts_voice_id_<leader>` fields), or just print instructions? Recommendation: edit programmatically — the whole point is one-command.
- Should there be a `Remove-TtsVoice.ps1` for cleanup? (Low priority, can defer.)
- Voice reference WAVs: commit them directly to git, or use Git LFS? They're small (6-12s ≈ 200-500KB each), so direct commit is fine for <20 voices. Revisit if the roster grows large.

## Completion Checklist

- [ ] Smart `Start-TtsServer.ps1` with preflight checks
- [ ] Model pre-download in `Setup-TtsServer.ps1`
- [ ] `Add-TtsVoice.ps1` voice wizard (interactive + scripted modes)
- [ ] `Test-TtsVoice.ps1` end-to-end validation
- [ ] README and docs updated
- [ ] All tests passing
- [ ] Manual smoke test on existing venv
