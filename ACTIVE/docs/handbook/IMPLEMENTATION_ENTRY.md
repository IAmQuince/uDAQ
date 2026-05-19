# Implementation entry

**CANONICAL CURRENT ENTRY DOCUMENT**

**Controlled document**  
ID: UDQ-HANDBOOK-IMPLEMENTATION-ENTRY-001  
Status: ACTIVE  
Revision: r22
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-IMP-PLAN-001, UDQ-IMP-GUIDE-001, UDQ-GOV-SOP-001, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Current implementation baseline

The active implementation baseline is the closed Sprint 2 runtime-state integration package built on the Sprint 1 mapping package and the prior save point / save-point reconciliation baseline rather than the earlier dry-run-only boundary.

## Phase guidance

- Phase 0 for contributors is package-root reconciliation: work from `ACTIVE/`, keep `HISTORICAL/` read-only except for lineage, and confirm the current entry/control surfaces before editing.
- Phase 4 for the roadmap remains a future live acquisition/runtime slice; this package does not claim that capability and keeps the current proof bounded below that level.

## Current source/test roots

- `src/`
- `tests/`
- `tools/`

These paths are relative to `ACTIVE/`.

## Current boundary

- Controller-authorized dry-run mapping apply commit is present and non-mutating.
- Sandbox mapping mutation is now implemented for Sprint 1, but only inside the sandbox store.
- Authoritative runtime-state snapshots are implemented for Sprint 2 through `RuntimeStateSnapshot` and compatibility API aliases.
- Draft shell edits remain non-authoritative.
- Live mapping apply remains deferred.
- Hardware-specific support remains outside core architecture.

## Implementation notes

For future implementation work, start from `ACTIVE/`, not from `HISTORICAL/`. Use `HISTORICAL/` only for lineage, regression comparison, and prior decision context.
