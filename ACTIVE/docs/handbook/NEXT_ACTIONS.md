# Next actions

**CANONICAL CURRENT ENTRY DOCUMENT**

**Controlled document**  
ID: UDQ-HANDBOOK-NEXT-001  
Status: ACTIVE  
Revision: r25  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-IMP-PLAN-001, UDQ-GAP-RPT-001, UDQ-GOV-REG-003, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Best next sprint

`20260515_03_state`

## Why

Sprint 1 now proves sandbox-only mapping apply, diff, rollback, and diagnostics. The next safe implementation move is the authoritative runtime state model so devices, points, mappings, signals, variables, logic, commands, and UI projections share one controlled truth boundary before live mutation is considered.

This next step should preserve the recent reconciliation work: keep package-root/document alignment coherent while adding the runtime-state truth spine instead of opening a competing authority path.

## Required Sprint 2 boundaries

- Define authoritative runtime state without granting live output authority.
- Preserve the Sprint 1 sandbox apply boundary.
- Keep physical hardware writes out of scope.
- Maintain requested/applied/observed separation.
- Keep UI/session state separate from machine truth.
- Update roadmap/register/SOP surfaces only if the sprint boundary changes.

## Handoff governance rule

Future work should modify `ACTIVE/` by default. `HISTORICAL/` should be updated only when a document/package is superseded, imported as a reference, or reconciled for lineage.

## Sequence note

- Authoritative readback is implemented.
- Draft edits remain intentionally non-authoritative.
- Preflight/review/prepared-request generation is implemented.
- Controller-authorized dry-run commit is implemented and non-mutating.
- Sprint Zero roadmap and sprint register are implemented.
- Sprint 1 sandbox mapping apply, rollback, diff, Testing menu, and diagnostic bundle are implemented.
- Phase 3 remains the later durable session/checkpoint/replay spine; Sprint 2 should prepare that path without collapsing requested, applied, and observed runtime semantics.
- Live hardware apply, runtime logic deployment, and hardware-in-loop verification remain deferred until prerequisite sprints are separately reviewed and tested.
