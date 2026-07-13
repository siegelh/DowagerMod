# Multiplayer synchronization manifest

`tools\multiplayer_manifest.ps1` verifies files that can change deterministic BtS gameplay:

- every `.xml` below `Beyond the Sword\Assets\XML`;
- every `.py` and `.pyc` below `Beyond the Sword\Assets\Python`;
- `Beyond the Sword\Assets\CvGameCoreDLL.dll`.

Paths use `/` separators and comparisons are case-insensitive. Each file has a SHA-256 and byte count; aggregate SHA-256 values are stable across machines and cover scope, normalized path, size, and file hash. Generated JSON contains no machine path or timestamp.

Client-only art, audio, movies, fonts, executables, saves, and configuration are intentionally excluded. They usually do not affect multiplayer simulation and make friend comparisons unnecessarily large. Art should only be added as a separately marked optional scope if a future diagnostic needs it. Python bytecode is included because BtS can load it; stale generated `.pyc` files therefore appear as extra or different.

## Commands

Run from the repository root in Windows PowerShell or PowerShell 7.

Create a JSON file to exchange:

```powershell
.\tools\multiplayer_manifest.ps1 `
  -Root ".\CoreFiles\Sid Meier's Civilization IV Beyond the Sword" `
  -OutputPath ".\my-multiplayer-manifest.json"
```

Compare the repository payload with a live game installation:

```powershell
.\tools\multiplayer_manifest.ps1 `
  -ReferenceRoot ".\CoreFiles\Sid Meier's Civilization IV Beyond the Sword" `
  -CandidateRoot "C:\Games\Sid Meier's Civilization IV Beyond the Sword"
```

Compare JSON files exchanged by two players:

```powershell
.\tools\multiplayer_manifest.ps1 `
  -ReferenceManifest ".\host.json" `
  -CandidateManifest ".\friend.json"
```

A match exits `0`. Missing, extra, or different files are listed and exit `1`; invalid input or manifest corruption exits `2`. Use `-ReferenceOutputPath` and `-CandidateOutputPath` during a root comparison to save both manifests.

Run the self-test:

```powershell
.\tools\test_multiplayer_manifest.ps1
```

The test compares identical manifests, alters one XML file in a temporary repository-local copy, requires a reported mismatch and exit `1`, then removes the copy.
