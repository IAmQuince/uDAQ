# Known limitations — Sprint 1 mapping package

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Still deferred

- Live mapping apply is not implemented.
- Sandbox mappings are not promoted into authoritative runtime state.
- Output authority and physical writes remain unavailable.
- Modbus support remains a planned support-pack sprint.
- Historian production storage and review remain planned work.
- Logic Designer runtime deployment remains planned work.
- The visible shell requires optional UI dependencies (`PySide6` and `pyqtgraph`).

## Current implemented boundary

Mapping apply can mutate a sandbox store only. Rollback restores the sandbox hash, diff reports are generated, and automated testing evidence can be exported without hardware.

## Testing caveat

If the visible GUI cannot launch due missing optional dependencies, use `RUN_DIAGNOSTICS.bat`; it exercises the Sprint 1 acceptance harness without requiring the GUI.
