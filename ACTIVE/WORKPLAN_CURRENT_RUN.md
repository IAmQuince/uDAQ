# Workplan — 20260515_04_session

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
Active sprint target: `20260515_04_session`

## Objective

Open Sprint 3 with a durable session/checkpoint/replay spine that attaches to the Sprint 2 authoritative runtime-state model without granting live mapping apply, hardware writes, historian production, or runtime logic deployment authority.

## In scope

- Session metadata model with schema version, actor/source context, and runtime snapshot hash.
- Checkpoint payloads that reference `RuntimeStateSnapshot` as the source of review truth.
- Deterministic JSON serialization and checkpoint hashing.
- Filesystem-backed save/load path for local no-hardware proof.
- Restore into non-authoritative review/session projection only.
- Replay evidence summary suitable for diagnostics/export.
- Focused tests for persistence, restore boundaries, corrupt payload rejection, and deterministic replay evidence.

## Out of scope

- Live mapping apply.
- Hardware output writes.
- Production historian storage.
- Runtime logic deployment.
- Remote command authority.
- Broad UI redesign or controller decomposition.

## Gates

1. Governance validators and package audit pass.
2. Session/checkpoint unit and contract tests pass.
3. Shell smoke and simulated LabJack U6 smoke continue to pass.
4. Evidence export proves checkpoint/replay behavior without hardware.
5. Requested/applied/observed semantics remain separated.

## Closeout expectation

Sprint 3 is complete when a no-hardware user can persist a runtime-state-backed session checkpoint, restore it into review/session state, replay it into deterministic evidence, and run the package quality gate without introducing live output authority.
