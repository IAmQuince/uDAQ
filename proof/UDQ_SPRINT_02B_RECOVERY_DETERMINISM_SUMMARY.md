# Sprint 2B — U6 Recovery Determinism Summary

## Objective
Pin down and fix the same-run U6 recovery path so unplug/replug behavior becomes either repeatably real or stage-specifically explained.

## What changed
- enabled bounded recovery polling for a disconnected active adapter by allowing the lifecycle poll path to explicitly poll the active adapter while it remains in the disconnected set
- tightened the real-U6 adapter recovery pipeline so backend reopen is tracked separately from post-disconnect successful polling
- added reconnect-stage status fields and counters:
  - `reconnect_backend_open_success_count`
  - `reconnect_backend_open_failure_count`
  - `post_disconnect_successful_poll_count`
  - `recovery_stage`
  - `last_reconnect_attempt_at`
  - `last_backend_reopen_at`
  - `last_reconnect_failure_at`
  - `last_recovery_failure_stage`
  - `last_recovery_failure_reason`
- emitted reconnect-stage runtime events:
  - `device_reconnect_attempt_started`
  - `backend_reopen_failed`
  - `backend_reopen_succeeded`
  - `post_disconnect_poll_resumed`
  - `adapter_rebind_succeeded`
  - existing `device_recovered`
- upgraded the field-test bundle so it now includes a dedicated recovery-analysis section and stage-specific smoke payload fields

## Why this mattered
The prior two hardware reruns showed the same pattern: device loss was handled correctly, but same-run recovery was not repeatably demonstrated because the active adapter stayed in the disconnected set and stopped being polled. This pass removes that blind spot and makes the reconnect pipeline observable.

## Boundaries preserved
- no widening to other devices
- no UI redesign
- no historian or export expansion
- no broad architecture rewrite
- no support-pack leakage into the universal core

## Key implementation note
Recovery is no longer treated as equivalent to backend reopen. The bounded U6 adapter now only marks recovery complete after a real post-disconnect successful poll.
