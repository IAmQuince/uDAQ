# Known limitations — post Sprint 3 session package

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Still deferred

- Live mapping apply is not implemented.
- Live acquisition runtime (`20260515_05_acquire`) is not implemented.
- Output authority and physical writes remain unavailable.
- Modbus support remains a planned support-pack sprint.
- Historian production storage and review remain planned work.
- Logic Designer runtime deployment remains planned work.

## Current implemented boundary

Runtime-state snapshots are authoritative read/review projections. Mapping apply can mutate a sandbox store only. Session checkpoints persist runtime snapshots for review-only restore and deterministic replay evidence export without hardware. Rollback restores the sandbox hash, diff reports are generated, and automated testing evidence can be exported without hardware.

## Testing caveat

The visible GUI requires optional UI dependencies (`PySide6` and `pyqtgraph`). Sprint 3 session/replay evidence is fully exercisable from `RUN_DIAGNOSTICS.bat`, the `Testing` menu when the GUI is available, `python3 -m tools.dev.run_session_checkpoint_smoke`, and `udq-session-replay-evidence` without installing PySide6.

## Accepted integration debt

The meta controller decomposition check remains the only accepted non-blocking failure for this closeout. `src/universaldaq/app/controller.py` is still above the current threshold in `tests/meta/test_meta_controller_decomposition.py`; broad controller extraction is deferred to a bounded future decomposition pass.

## Testing caveat

If the visible GUI cannot launch due missing optional dependencies, use `RUN_DIAGNOSTICS.bat`; it exercises the Sprint 1 acceptance harness without requiring the GUI.
