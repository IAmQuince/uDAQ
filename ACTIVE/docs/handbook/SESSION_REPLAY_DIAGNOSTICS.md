# Session replay diagnostics

## Purpose

Session/checkpoint diagnostics provide no-hardware, non-live artifact output for sprint `20260515_04_session`.

These tools are developer/review helpers only. They do not grant runtime authority.

## Commands

Run from `ACTIVE/`:

- Emit session checkpoint artifact JSON:
  - `python3 -m tools.diagnostics.dump_session_checkpoint --package-root . --pretty`
- Strict mode (requires session provider availability):
  - `python3 -m tools.diagnostics.dump_session_checkpoint --package-root . --strict --pretty`
- Demo/non-live mode:
  - `python3 -m tools.diagnostics.dump_session_checkpoint --package-root . --demo --pretty`
- Write output file:
  - `python3 -m tools.diagnostics.dump_session_checkpoint --package-root . --pretty --output audit_reports/testing/session_checkpoint.json`
- Validate artifact:
  - `python3 -m tools.diagnostics.validate_session_checkpoint --input audit_reports/testing/session_checkpoint.json --pretty`
- Compare two artifacts:
  - `python3 -m tools.diagnostics.compare_session_checkpoints --left left.json --right right.json --pretty`

## Provider discovery order

`dump_session_checkpoint` checks providers in this order:

1. `universaldaq.session:create_checkpoint_from_runtime_state`
2. `universaldaq.session:build_session_checkpoint`
3. `universaldaq.session:get_current_session_checkpoint`
4. `universaldaq.session.checkpoint:create_checkpoint_from_runtime_state`
5. `universaldaq.session.checkpoint:build_session_checkpoint`
6. `universaldaq.session.services:build_session_checkpoint`

Supported provider return types:
- mapping payload,
- object with `to_dict()`,
- object with `as_dict()`,
- object with `model_dump()`.

## Safety/non-authority behavior

Required invariants:
- `replay_is_live: false`
- `hardware_mutation_enabled: false`
- `live_mapping_apply_enabled: false`

If the session API is absent:
- default mode emits a placeholder diagnostic artifact,
- strict mode exits non-zero.

## Expected JSON fields

- `artifact_id`
- `artifact_version`
- `generated_at_utc`
- `package_root`
- `git_branch`
- `git_commit`
- `python_version`
- `session_api_available`
- `session_model_version`
- `session_id`
- `checkpoint_id`
- `checkpoint_timestamp`
- `runtime_snapshot_id`
- `runtime_state_model_version`
- `replay_is_live`
- `hardware_mutation_enabled`
- `live_mapping_apply_enabled`
- `checkpoint_count`
- `event_count`
- `warning_count`
- `degraded_count`
- `stale_count`
- `unavailable_count`
- `validation_summary`
- `warnings`
- `known_limitations`

## ChatGPT review workflow

1. Run the command with `--pretty`.
2. Copy JSON from stdout (or from output path).
3. Paste into ChatGPT for diagnostics/review discussion.

## Scope boundary notes

- Checkpoint diagnostics are not production historian behavior.
- Replay diagnostics are non-live by design and must not be treated as current observed hardware state.
- Session artifacts are review evidence and developer tooling, not output authority surfaces.

## Wiring to GPT-5.5 session API

When the leader session API is available, expose one of the provider callables listed in the discovery order above.

No competing session truth model should be introduced in this helper. The tool should consume leader-owned session/checkpoint payloads and normalize them into the diagnostic wrapper fields.
