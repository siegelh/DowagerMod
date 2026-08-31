# Historical flag tools

This directory is the editable source of truth for the 59 playable
civilization flags. The active generation uses 56 issue-provided designs and
three retained historical-v1 designs. Read
[`../../docs/FLAG_PIPELINE.md`](../../docs/FLAG_PIPELINE.md) before changing a
master, manifest record, or generated DDS.

Common commands:

```powershell
python .\tools\flags\build_flags.py --check
python .\tools\flags\build_flags.py --civilization CIVILIZATION_FRANCE_BOURBON
python .\tools\flags\build_flags.py --changed
python .\tools\flags\build_flags.py --all
python .\tools\flags\build_review.py
```

The production format is 128x128 DXT3 with eight mip levels and zero encoded
alpha at every mip. That zero alpha is intentional for Civ4 fixed-color flags.
Ordinary image viewers may display a valid DDS as transparent.
