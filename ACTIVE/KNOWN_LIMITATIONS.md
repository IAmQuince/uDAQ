# Known limitations — Sprint 3 session activation

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
Active sprint target: `20260515_04_session`

## Still deferred

- Live mapping apply is not implemented.
- Sandbox mappings are projected into authoritative runtime snapshots only as non-authoritative requested/review state.
- Output authority and physical writes remain unavailable.
- Modbus support remains a planned support-pack sprint.
- Historian production storage and review remain planned work.
- Logic Designer runtime deployment remains planned work.
- Remote command authority remains out of scope.
- The visible shell requires optional UI dependencies (`PySide6` and `pyqtgraph`).

## Current implemented boundary

Runtime-state snapshots are authoritative read/review projections. Mapping apply can mutate a sandbox store only. Rollback restores the sandbox hash, diff reports are generated, and automated testing evidence can be exported without hardware.

## Sprint 3 boundary

Session persistence, checkpoint restore, and replay evidence must remain review/session capabilities. They must not mutate live hardware state, call adapters, grant output authority, or replace requested/applied/observed runtime semantics.

## Accepted integration debt

The meta controller decomposition check remains accepted non-blocking debt for this closeout line. `src/universaldaq/app/controller.py` is still above the current threshold in `tests/meta/test_meta_controller_decomposition.py`; broad controller extraction is deferred to a bounded future decomposition pass.

## Testing caveat

If the visible GUI cannot launch due missing optional dependencies, use no-hardware diagnostic and smoke commands from `ACCEPTANCE_TEST_PLAN.md`.
