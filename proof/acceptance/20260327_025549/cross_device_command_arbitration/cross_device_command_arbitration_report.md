# UniversalDAQ Cross-Device Command and Arbitration

- generated_at_utc: 2026-03-27T02:55:53.848328+00:00
- verdict: PASS
- session_id: SESSION-CROSS-DEVICE-COMMANDS
- report_dir: /mnt/data/udq11_run/proof/acceptance/20260327_025549/cross_device_command_arbitration
- writable_tag_count: 3
- activated_adapter_count: 3

## Command summary

- command_attempt_count: 13
- accepted_count: 8
- rejected_count: 5
- adapter_failed_count: 0
- ownership_conflict_count: 2
- same_owner_renewal_count: 2
- stale_lease_expiration_count: 3
- target_unavailable_count: 3

## Degraded conditions

- degraded_transition_count: 7
- simultaneous_drop_event_count: 1
- safe_state_event_count: 1
- lease_revoked_on_degrade_count: 2

## Evidence depth

- persisted_record_count: 109
- segment_count: 28
- checkpoint_count: 5
- replay_tail_count: 10
- replay_tail_record_type_count: 4

## Checks

- [PASS] writable_tag_inventory — writable_tag_count=3
- [PASS] healthy_command_acknowledged — {"accepted_count": 8}
- [PASS] ownership_conflict_rejected — {"ownership_conflict_count": 2}
- [PASS] same_owner_lease_renewal — {"same_owner_renewal_count": 2}
- [PASS] stale_lease_expiry — {"stale_lease_expiration_count": 3}
- [PASS] degraded_output_behavior — {"degraded_transition_count": 7, "lease_revoked_on_degrade_count": 2, "simultaneous_drop_event_count": 1}
- [PASS] target_unavailable_rejected — {"target_unavailable_count": 3}
- [PASS] command_evidence_depth — {"checkpoints": 5, "records": 109}
- [PASS] command_replay_tail — {"tail_record_count": 10, "tail_record_counts_by_type": {"command_trace": 1, "cycle": 1, "runtime_event": 5, "sample": 3}}
- [PASS] session_artifact_integrity — entries=109 checkpoints=5
