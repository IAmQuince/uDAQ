# UniversalDAQ

**Controlled document**  
ID: UDQ-README-ROOT-001  
Status: ACTIVE  
Revision: r36  
Owner: Core Architecture  
Authority: PRIMARY  
Source docs: UDQ-GOV-LOG-001, UDQ-ARCH-NAR-001, UDQ-ARCH-NAR-002, UDQ-REQ-MAT-001, UDQ-GOV-REG-003, UDQ-ROADMAP-SPEC-001

## Package identity

- Package ID: `UDQ-PKG-20260515-03-STATE-R01`
- Package slug: `20260515_03_state`
- Package date: `2026-05-15`
- Run ID: `R01`
- Package status: `closed Sprint 2 authoritative runtime-state integration package`
- Supersedes: `UDQ-PKG-20260515-02-MAPPING-R02`
- Canonical review entry: `docs/release/REVIEW_START_HERE__UDQ-PKG-20260515-02-MAPPING-R02__ACTIVE.md`

## What this package is

This Sprint 2 integration package adds the authoritative runtime-state spine on top of the Sprint 1 sandbox-only mapping mutation proof while preserving the live hardware and output-authority boundaries on top of the save-point reconciliation baseline.

## What changed in this package

- Added sandbox mapping state, apply, diff, and rollback implementation.
- Added Sprint 1 diagnostic harness and batch launcher.
- Added a visible-shell `Testing` menu with smoke, sandbox demo, rollback, diff, and diagnostic actions.
- Added manual checklist and changed-area tests.
- Added `RuntimeStateSnapshot`, compatibility runtime-state API aliases, contract/invariant tests, and the runtime-state diagnostic snapshot CLI for `20260515_03_state`.
- Kept the root folder short as `20260515_02_mapping` to preserve the Windows path budget.

## Current implementation boundary

This package implements an authoritative runtime-state model and sandbox mutation only. It does not implement live mapping apply authority, physical output authority, Modbus support, historian production, or runtime logic deployment; those capabilities are still intentionally deferred.

## Start here

1. `README_START_HERE.md`
2. `PACKAGE_MANIFEST.md`
3. `docs/release/REVIEW_START_HERE__UDQ-PKG-20260515-02-MAPPING-R02__ACTIVE.md`
4. `docs/release/EXEC_SUMMARY.md`
5. `docs/active/UDQ-ROADMAP-SPEC-001__Completed_Product_Roadmap_and_Sprint_Sequence__r0__ACTIVE.md`
6. `docs/active/UDQ-SPRINT-SOP-001__Sprint_Planning_Execution_and_Closeout_Process__r0__ACTIVE.md`
7. `docs/handbook/START_HERE.md`
8. `docs/handbook/NEXT_ACTIONS.md`
9. `ACCEPTANCE_TEST_PLAN.md`
10. `KNOWN_LIMITATIONS.md`

## Historical material

Historical snapshots, superseded release docs, old audit material, and reconciliation evidence are in `../HISTORICAL/`.
