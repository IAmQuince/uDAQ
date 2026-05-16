# Acceptance note — 20260515_04_session

**Controlled release companion document**  
ID: UDQ-REL-SESSION-ACCEPT-20260515-04  
Status: REVIEW  
Revision: r0  
Owner: GPT-5.4 Helper  
Authority: DERIVED  
Source docs: UDQ-HANDBOOK-NEXT-001, UDQ-ROADMAP-SPEC-001, UDQ-SPRINT-REG-001  
Package ID: `UDQ-PKG-20260515-03-STATE-R01`

## Objective

Make the durable session/checkpoint/replay sprint verifiable against the authoritative runtime-state spine without allowing replay, checkpoint capture, or session persistence to imply live hardware state, live mapping apply, or production historian behavior.

## Non-goals

- No live hardware writes.
- No physical output authority.
- No live mapping apply.
- No production historian behavior.
- No runtime logic deployment.
- No broad controller rewrite outside a bounded mechanical extraction.

## Session / checkpoint criteria

- A session can be created without hardware.
- A checkpoint can be created from `RuntimeStateSnapshot` or `RuntimeStateSnapshot.to_dict()` output.
- Checkpoint validation rejects unsafe flags such as `hardware_mutation_enabled=true`.
- Session and checkpoint JSON are deterministic enough for diagnostics and review fixtures.
- Degraded, stale, unavailable, and requested/applied/observed runtime-state channels survive save/load round trip.

## Replay non-live criteria

- Replay views remain explicitly non-live.
- `hardware_mutation_enabled` remains false.
- `live_mapping_apply_enabled` remains false.
- `replay_is_live` remains false.
- Replay does not imply current observed hardware truth or live command authority.

## Runtime-state preservation criteria

- Requested, applied, and observed channels remain distinct inside checkpoints and replay views.
- Sandbox/review state remains non-authoritative.
- Checkpoint capture does not mutate authoritative live runtime state.
- Replay does not collapse runtime-state truth channels into one status field.

## Diagnostic criteria

- Runtime snapshot strict diagnostic continues to pass from `20260515_03_state`.
- Future session diagnostics from Codex should serialize checkpoints/replay views without enabling live behavior.
- If Codex adds checkpoint or replay dump commands, they must remain side-effect-free and clearly label replay as non-live.

## Controller decomposition debt status

- Current baseline meta failure: `tests/meta/test_meta_controller_decomposition.py::test_controller_concentration_reduced_and_handlers_exist`.
- The bounded extraction target is the session/persistence/review block in `src/universaldaq/app/controller.py`.
- If extraction cannot be completed without behavior risk, this debt remains accepted and non-blocking for the helper branch.

## Session API expectations for GPT-5.5

- Preferred public surface: `universaldaq.session`.
- Expected types/surfaces when present: `DurableSession`, `SessionCheckpoint`, `ReplayView` or `ReplaySession`, `SessionValidationResult`, and `DurableSessionService`.
- Expected service capabilities: session creation, checkpoint creation from runtime state, validation, save/load round trip, and replay construction from a checkpoint.

## Diagnostic expectations for Codex

- Add checkpoint dump and replay diagnostic commands only after the session API is real.
- Diagnostics must consume public session/runtime APIs, not private helpers.
- Diagnostics must preserve `hardware_mutation_enabled: false`, `live_mapping_apply_enabled: false`, `replay_is_live: false`, and no production historian claim.

## Validation commands

- `python3 -m pytest tests/contract/test_session_checkpoint_contract.py -q`
- `python3 -m pytest tests/invariants/test_session_replay_boundaries.py -q`
- `python3 -m pytest tests/unit/test_session_serialization.py -q`
- `python3 -m pytest tests/contract/test_authoritative_runtime_state_contract.py -q`
- `python3 -m pytest tests/invariants/test_runtime_state_boundaries.py -q`
- `python3 -m pytest tests/meta -q`
- `python3 -m pytest tests/unit tests/contract tests/invariants -q`
- `python3 -m ruff check <touched python files>`
- If/when the diagnostic commands exist: checkpoint dump and replay dump should be run in strict mode and verified non-live.

## Merge order

1. GPT-5.5 session implementation branch merges first.
2. This GPT-5.4 helper branch merges second, with API-pending skips removed where the real session package is present.
3. Codex diagnostic tooling merges after the real session API is available and the helper tests define the accepted non-live boundaries.
