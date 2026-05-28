# Release notes — 20260515_02_mapping

**CANONICAL CURRENT RELEASE NOTES**

**Controlled release document**  
ID: UDQ-REL-NOTES-20260515-002  
Status: ACTIVE  
Revision: r1  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-SOP-001, UDQ-LIFECYCLE-SPEC-001, UDQ-EXP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## R2 hotfix

This package supersedes the initial `20260515_02_mapping.zip` because the visible shell launch path exposed two UI wiring regressions: `system_summary` could be refreshed before the System workspace existed, and the active `OperatorShellWindow` class did not include the Logic workspace node-edit callbacks wired by the buttons.

The fix restores the intended draft/demo Logic node model, connects workspace tab-change refreshes only after the System workspace is constructed, adds a visible-shell wiring audit, and exposes that audit from the `Testing` menu. This is not a stub patch: the remove-node action changes the draft model/view, empty state is explicit, and the System Summary remains a real populated widget.

## Added

- `src/universaldaq/mapping/sandbox.py` with sandbox state, apply, diff, rollback, and demo request helpers.
- `src/universaldaq/testing/sprint_mapping.py` with user-runnable Sprint 1 diagnostics.
- Visible shell `Testing` menu actions, including the R2 visible-shell wiring audit.
- Root launchers `RUN_UDAQ.bat` and `RUN_DIAGNOSTICS.bat`.
- Manual checklist at `docs/testing/20260515_02_manual-test-checklist.md`.
- Sprint-specific tests for sandbox state, diff, boundary, rollback, menu presence, and diagnostic bundle export.

## Changed

- Package identity advanced to `UDQ-PKG-20260515-02-MAPPING-R02`.
- Sprint sequence register marks Sprint 1 as complete and points next work toward the runtime state sprint.

## 2026-05-27 — Sprint 3 session spine closeout

### Added

- Filesystem session checkpoint store with hash verification and corrupt-payload rejection.
- Review-only session restore and deterministic replay evidence export.
- `udq-session-replay-evidence` console script and Testing-menu replay evidence export.
- Session-focused tests under `tests/session/`.

### Changed

- Sprint sequence register marks Sprint 3 (`20260515_04_session`) complete; next sprint is `20260515_05_acquire`.
- `NEXT_ACTIONS.md` and workplan surfaces hand off to live acquisition runtime.

### Preserved

- No live mapping apply, hardware writes, historian production, or runtime logic deployment in this closeout.

## Safety boundary

The sandbox controller accepts only prepared/dry-run mapping requests and never executes live. No adapter calls, hardware writes, or live authoritative mapping updates are performed by this package.
