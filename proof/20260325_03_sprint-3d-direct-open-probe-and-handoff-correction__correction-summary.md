# Correction summary

## What changed
- Added a standalone direct-open probe (`tools/diagnostics/run_u6_direct_open_probe.py`) and Windows launcher.
- Changed the real-U6 backend factory to prefer the LabJackPython documented explicit-serial constructor path before falling back to alternate strategies.
- Added open stage/strategy diagnostics to the real-U6 startup-open path.
- Taught the guided startup smoke to run a preflight direct-open probe in real mode and, when successful, reuse that probe row instead of rediscovering by re-opening the device during controller discovery.

## Why it matters to the main app
This keeps the work focused on the generic app seam: discover → select → startup open/init → first healthy baseline. The direct-open probe is a reusable support-pack bring-up pattern rather than a LabJack-only side quest.
