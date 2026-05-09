# Real-Hardware Specimen Bridge Sprint — Release Notes

## Scope
This sprint opened the next bounded section of the package by bridging the stabilized runtime evidence/recovery lane into one narrow read-only real-hardware specimen entry.

## What landed
- added `tools/acceptance/run_real_hardware_specimen_bridge.py`
- kept the main operator surface flat by extending the existing one-command acceptance runner instead of creating a second test framework
- added explicit PASS/SKIP reporting for the real-hardware bridge so hardware absence does not silently masquerade as simulation success
- emitted reviewable bridge artifacts in the same proof-bundle style when a real-mode backend is available
- preserved the current simulated bounded baseline as the regression floor

## Claim discipline
This sprint does **not** claim broad hardware generalization.
It adds one bounded real-U6 specimen bridge result to the package acceptance surface and keeps the core runtime/evidence spine vendor-agnostic.
