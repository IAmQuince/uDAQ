# Acceptance note — 20260515_04_session

**Controlled release companion document**  
ID: UDQ-REL-SESSION-ACCEPT-20260515-04  
Status: REVIEW  
Revision: r0  
Owner: Core Architecture / GPT-5.5 Integration  
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
- Diagnostics can find a real session checkpoint provider in strict mode.

## Contract and governance coverage

- GPT-5.4 helper tests run against `universaldaq.session` instead of API-pending skips once the leader branch is merged.
- Contract helpers may use compatibility wrappers, but assertions must target the real session/checkpoint/replay model.
- The accepted controller decomposition failure remains non-blocking for this sprint and should not trigger a broad integration refactor.

## Diagnostic expectations

- `dump_session_checkpoint --strict` should report `session_api_available: true`.
- Session diagnostics must keep `hardware_mutation_enabled`, `live_mapping_apply_enabled`, and `replay_is_live` false.
- Comparison diagnostics should compare review/checkpoint payloads only and must not claim current observed hardware state.

## Non-goals

- No live mapping apply.
- No hardware writes.
- No physical output authority.
- No production historian.
- No runtime logic deployment.
- No broad UI redesign.
- No full Device Explorer / Signal Explorer implementation.

## Expected validation

- `python3 -m pytest tests/unit/test_session_models.py -q`
- `python3 -m pytest tests/unit/test_session_serialization.py -q`
- `python3 -m pytest tests/contract/test_session_checkpoint_contract.py -q`
- `python3 -m pytest tests/invariants/test_session_replay_boundaries.py -q`
- session diagnostic tool tests
- runtime-state regression tests from `20260515_03_state`
- runtime and session diagnostic strict mode
- shell and simulated LabJack smoke checks

## Merge-order recommendation

1. Merge GPT-5.5 session implementation branch first.
2. Merge GPT-5.4 contract/tests/governance branch second, removing API-pending skips.
3. Merge Codex diagnostic tooling third so strict diagnostics can bind to the real session API.
