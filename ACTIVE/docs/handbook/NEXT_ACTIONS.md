# Next actions

**CANONICAL CURRENT ENTRY DOCUMENT**

**Controlled document**  
ID: UDQ-HANDBOOK-NEXT-001  
Status: ACTIVE  
Revision: r27
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-IMP-PLAN-001, UDQ-GAP-RPT-001, UDQ-GOV-REG-003, UDQ-ROADMAP-SPEC-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Active sprint

`20260515_04_session`

## Why

Sprint 2 provides the authoritative runtime-state model so devices, points, mappings, signals, variables, logic, commands, and UI projections share one controlled truth boundary before live mutation is considered.

The active implementation move is the durable session/checkpoint/replay spine. It should preserve the recent reconciliation work and attach to the runtime-state truth spine without opening a competing authority path.

## Required Sprint 3 boundaries

- Persist and restore sessions/checkpoints/replay evidence without granting live output authority.
- Preserve the Sprint 1 sandbox apply boundary.
- Keep physical hardware writes out of scope.
- Maintain requested/applied/observed separation.
- Keep UI/session state separate from machine truth.
- Treat replay evidence as checkpoint review proof, not historian production storage.

## Handoff governance rule

Future work should modify `ACTIVE/` by default. `HISTORICAL/` should be updated only when a document/package is superseded, imported as a reference, or reconciled for lineage.

## Sequence note

- Authoritative readback is implemented.
- Draft edits remain intentionally non-authoritative.
- Preflight/review/prepared-request generation is implemented.
- Controller-authorized dry-run commit is implemented and non-mutating.
- Sprint Zero roadmap and sprint register are implemented.
- Sprint 1 sandbox mapping apply, rollback, diff, Testing menu, and diagnostic bundle are implemented.
- Sprint 2 authoritative runtime state, compatibility API aliases, contract/invariant coverage, and runtime-state diagnostic strict mode are implemented.
- Phase 3 / `20260515_04_session` is now active and should not collapse requested, applied, and observed runtime semantics.
- Live hardware apply, runtime logic deployment, historian production, and hardware-in-loop verification remain deferred until prerequisite sprints are separately reviewed and tested.

## Next after Sprint 3

If Sprint 3 closes with deterministic checkpoint/replay evidence and no authority-boundary drift, the roadmap points to `20260515_05_acquire` / live acquisition runtime as the next implementation candidate.
