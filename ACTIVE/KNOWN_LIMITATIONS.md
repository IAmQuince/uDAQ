# Known limitations — Sprint 2 runtime-state package

Package ID: `UDQ-PKG-20260515-03-STATE-R01`

## Still deferred

- Live mapping apply is not implemented.
- Sandbox mappings are projected into authoritative runtime snapshots only as non-authoritative requested/review state.
- Output authority and physical writes remain unavailable.
- Modbus support remains a planned support-pack sprint.
- Historian production storage and review remain planned work.
- Logic Designer runtime deployment remains planned work.
- The visible shell requires optional UI dependencies (`PySide6` and `pyqtgraph`).

## Current implemented boundary

Runtime-state snapshots are authoritative read/review projections. Mapping apply can mutate a sandbox store only. Rollback restores the sandbox hash, diff reports are generated, and automated testing evidence can be exported without hardware.

## Accepted integration debt

The meta controller decomposition check remains the only accepted non-blocking failure for this closeout. `src/universaldaq/app/controller.py` is still above the current threshold in `tests/meta/test_meta_controller_decomposition.py`; broad controller extraction is deferred to a bounded future decomposition pass.

## Testing caveat

If the visible GUI cannot launch due missing optional dependencies, use `RUN_DIAGNOSTICS.bat`; it exercises the Sprint 1 acceptance harness without requiring the GUI.
