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

## Best next sprint

`20260515_05_acquire`

## Why

Sprint 3 closed the durable session/checkpoint/replay spine: checkpoints embed authoritative runtime snapshots, restore stays review-only, replay evidence is deterministic, and corrupt payloads fail closed at the store boundary.

The next safe move is live acquisition runtime (`UDQ-SPRINT-04`), building canonical live samples with health/quality states while preserving requested/applied/observed separation and keeping sandbox mapping apply isolated.

## Required Sprint 4 boundaries

- Introduce live acquisition projections without granting unreviewed output authority.
- Preserve Sprint 1 sandbox apply and Sprint 3 session/replay review boundaries.
- Keep physical hardware writes and production historian out of scope unless explicitly opened in a later sprint.
- Maintain requested/applied/observed separation in runtime state and diagnostics.
- Update roadmap/register/SOP surfaces only when the sprint boundary changes.

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
- Sprint 3 session/checkpoint store, review restore, replay evidence (CLI + Testing menu), and corrupt-checkpoint hardening are implemented.
- Phase 4 / `20260515_05_acquire` is the live acquisition runtime sprint and must not collapse requested, applied, and observed runtime semantics.
- Live hardware apply, runtime logic deployment, and hardware-in-loop verification remain deferred until prerequisite sprints are separately reviewed and tested.
