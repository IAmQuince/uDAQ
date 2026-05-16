# Acceptance note — 20260515_04_session

**Controlled release companion document**  
ID: UDQ-REL-SESSION-ACCEPT-20260515-04  
Status: REVIEW  
Revision: r0  
Owner: Core Architecture / GPT-5.5 Leader  
Authority: DERIVED  
Source docs: UDQ-HANDBOOK-NEXT-001, UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-REG-001  
Package ID: `UDQ-PKG-20260515-04-SESSION-R01`

## Sprint objective

Create a durable, review-safe session/checkpoint/replay spine over the authoritative runtime-state model.

## Acceptance criteria

- Sessions can be created without hardware.
- Checkpoints embed or accept `RuntimeStateSnapshot.to_dict()` output.
- Session and checkpoint JSON serialization is deterministic for tests and diagnostics.
- Replay views are explicitly non-live.
- Safety flags remain false for hardware mutation, live mapping apply, live replay, and production historian behavior.
- Requested/applied/observed runtime-state channels survive checkpoint capture.
- Stale/degraded/unavailable snapshot state remains reviewable after checkpoint capture.
- Unsafe or corrupted checkpoint payloads are rejected or surfaced through validation errors/warnings.
- The session package does not import optional hardware support packs.

## Non-goals

- No live mapping apply.
- No hardware writes.
- No physical output authority.
- No production historian.
- No runtime logic deployment.
- No broad UI redesign.

## Expected validation

- `python3 -m pytest tests/unit/test_session_models.py -q`
- `python3 -m pytest tests/unit/test_session_serialization.py -q`
- `python3 -m pytest tests/contract/test_session_checkpoint_contract.py -q`
- `python3 -m pytest tests/invariants/test_session_replay_boundaries.py -q`
- runtime-state regression tests from `20260515_03_state`
- runtime diagnostic strict mode
- shell and simulated LabJack smoke checks
