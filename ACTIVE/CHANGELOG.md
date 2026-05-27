# Changelog — 20260515_02_mapping

## 2026-05-15 — Sprint 1 mapping sandbox mutation proof

### Added

- Sandbox-only mapping state store with deterministic state hashing.
- Prepared mapping request apply into sandbox only.
- Rollback token and sandbox state restoration.
- Mapping diff report generation.
- `Testing` menu in the visible shell specification and Qt shell wiring.
- `RUN_UDAQ.bat` and `RUN_DIAGNOSTICS.bat` user entry points.
- Sprint 1 manual test checklist and diagnostic bundle export.
- Sprint-specific unit, contract, UI, and diagnostic harness tests.

### Preserved

- Existing dry-run/preflight/review mapping boundary behavior.
- No live mapping apply.
- No hardware output writes.
- No support-pack/vendor logic added to core.


## R2 hotfix

- Restored visible-shell launchability by deferring workspace tab-change wiring until after the System workspace creates `system_summary`.
- Restored real draft/demo Logic workspace node callbacks instead of hiding or stubbing the remove-node action.
- Added a visible-shell wiring audit to the diagnostic suite and Testing menu.
- Package artifact/root is `20260515_02_mapping-r2`; package ID advanced to `UDQ-PKG-20260515-02-MAPPING-R02`.


## 2026-05-27 — Sprint 3 session activation

### Changed

- Updated active workplan and next-action surfaces for `20260515_04_session`.
- Added Sprint 3 acceptance expectations for session persistence, checkpoint restore, and replay evidence.
- Added deterministic session checkpoint hashing, filesystem checkpoint store, review restore result, and no-hardware checkpoint smoke command.
- Marked Sprint 3 active in the sprint sequence register.

### Preserved

- No live mapping apply.
- No hardware output writes.
- No historian production storage.
- No runtime logic deployment.

- Added deterministic checkpoint replay evidence export with a summary-only hash payload that excludes full runtime snapshot history.

- Added Testing-menu access for deterministic session replay evidence export.
