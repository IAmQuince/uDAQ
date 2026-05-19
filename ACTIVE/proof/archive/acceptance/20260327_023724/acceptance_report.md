# UniversalDAQ Acceptance Report

- generated_at_utc: 2026-03-27T02:37:28.613450+00:00
- verdict: PASS
- report_dir: /mnt/data/udq10_work/proof/acceptance/20260327_023724

## Checks

- [PASS] shell_smoke_entry — shell-smoke: profile=PROF-SMOKE page=review mode=live device_phase=live detected=4 command_allowed=False ack_states=(<AlarmLifecycleState.ASSERTED: 'asserted'>,) manifest=MAN-SMOKE-001
- [PASS] session_artifact_report — entries=149 segments=38
- [PASS] populated_history_counts — {"cold": {"checkpoint_count": 4, "persisted_record_count": 149, "segment_count": 38}, "hot": {"presentation_snapshot_available": true, "recent_sample_count": 36, "recent_signal_count": 2}, "warm": {"cycle_row_count": 18, "runtime_event_count": 59, "variable_row_count": 36}}
- [PASS] review_index_queryable — {"sample_points": {"SIM-HIST-001:PT-101": 18, "SIM-HIST-001:TT-101": 18}, "variable_ids": ["VAR-PT-AVG", "VAR-TT-MEAN"]}
- [PASS] deterministic_replay_hash — hash=af92b2ceb751c4c9f784eee53e7d612ecbc0b2f47585909b53f93b751a3a3355 tail=17
- [PASS] nonzero_tail_replay — tail=17 checkpoint=CHK-SESSION-POPULATED-REVIEW-45-132
- [PASS] multi_type_tail_replay — {"cycle": 2, "runtime_event": 7, "sample": 4, "variable_update": 4}
- [PASS] checkpoint_ladder_depth — {"count": 4, "spacing": {"average_sequence_gap": 33.0, "max_sequence_gap": 33, "min_sequence_gap": 33}}
- [PASS] longrun_history_depth — {"records": 149, "segments": 38}
- [PASS] repeatability_gate — {"consistent_depth_metrics": true, "consistent_replay_metrics": true, "run_count": 3}
- [PASS] fault_injection_fallback — recovered_checkpoint_id=CHK-SESSION-FAULT-INJECTION-111-99
- [PASS] fallback_nonzero_tail_replay — tail=34 min=16
- [PASS] fallback_multi_type_tail_replay — {"cycle": 4, "runtime_event": 14, "sample": 8, "variable_update": 8}
- [PASS] fallback_recovery_state_hash — state_hash_matches=True
- [PASS] recovery_review_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/fault_injection
- [PASS] review_summary_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/reviewability
- [PASS] repeatability_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/repeatability
- [PASS] longrun_characterization_thresholds — {"average_checkpoint_sequence_gap": 33.0, "average_records_per_segment": 3.92, "bounded_run_window_ticks": 48, "checkpoint_density_per_cycle": 0.222, "max_segment_record_count": 4, "meets_min_checkpoint_depth": true, "meets_min_record_depth": true, "meets_min_segment_depth": true, "min_segment_record_count": 1, "planned_cycle_count": 18, "queryable_sample_points": ["SIM-HIST-001:PT-101", "SIM-HIST-001:TT-101"], "queryable_variable_count": 2, "runtime_event_diversity": 4}
- [SKIP] real_hardware_bridge_status — {"driver_name": "not-installed", "mode": "driver_unavailable", "reason": "LabJack driver unavailable (not-installed)"}
- [PASS] real_hardware_bridge_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/real_hardware_bridge
- [PASS] real_hardware_bridge_review_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/real_hardware_bridge
- [SKIP] real_hardware_bridge_queryable — hardware bridge skipped
- [PASS] cross_device_acquisition_status — {"activated_adapter_count": 3, "tag_definition_count": 21}
- [PASS] cross_device_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/cross_device_acquisition
- [PASS] cross_device_queryable — {"sample_points": {"ARDUINO-UNO-ARD-401:analog_in_0": 4, "ARDUINO-UNO-ARD-401:analog_in_1": 4, "ARDUINO-UNO-ARD-401:digital_in_2": 4, "ARDUINO-UNO-ARD-401:digital_in_3": 4, "ARDUINO-UNO-ARD-401:firmware_alive": 4, "LABJACK-U6-470201:analog_in_0": 5, "LABJACK-U6-470201:analog_in_1": 5, "LABJACK-U6-470201:analog_in_2": 5, "LABJACK-U6-470201:analog_in_3": 5, "LABJACK-U6-470201:digital_in_0": 5, "LABJACK-U6-470201:digital_in_1": 5, "LABJACK-U6-470201:digital_in_2": 5, "LABJACK-U6-470201:digital_in_3": 5, "RPI-RPI-LAB-401:gpio_in_17": 5, "RPI-RPI-LAB-401:gpio_in_27": 5, "RPI-RPI-LAB-401:host_cpu_temp_c": 5, "RPI-RPI-LAB-401:host_uptime_s": 5}, "variable_ids": ["VAR-MIXED-ANALOG-DELTA", "VAR-MIXED-ANALOG-SUM", "VAR-MIXED-RPI-CPU-GATE"]}
- [PASS] cross_device_nontrivial_replay — {"tail_record_count": 41, "tail_record_counts_by_type": {"cycle": 2, "runtime_event": 5, "sample": 34}}
- [PASS] cross_device_fallback_recovery — {"replay_tail_count": 119, "replay_tail_counts_by_type": {"cycle": 6, "runtime_event": 15, "sample": 98}}
- [PASS] cross_device_repeatability — {"consistent_depth_metrics": true, "consistent_replay_metrics": true, "run_count": 3}
- [PASS] cross_device_degraded_conditions — {"degraded_transition_count": 5, "simultaneous_drop_event_count": 1}
- [PASS] cross_device_command_arbitration_status — {"command_attempt_count": 10, "writable_tag_count": 3}
- [PASS] cross_device_command_artifacts_present — /mnt/data/udq10_work/proof/acceptance/20260327_023724/cross_device_command_arbitration
- [PASS] cross_device_command_arbitration_conflicts — {"ownership_conflict_count": 2}
- [PASS] cross_device_command_degraded_behavior — {"degraded_transition_count": 6, "safe_state_event_count": 1, "simultaneous_drop_event_count": 1, "timeline_rows": [{"event_type": "target_degraded", "output_id": "arduino_uno_ard_401:digital_out_0", "owner": "", "summary": "adapter dropped out of the bounded command lane", "timestamp": "604"}, {"event_type": "target_restored", "output_id": "arduino_uno_ard_401:digital_out_0", "owner": "", "summary": "adapter returned to the bounded command lane", "timestamp": "605"}, {"event_type": "target_degraded", "output_id": "labjack_u6_470201:digital_out_0", "owner": "", "summary": "adapter dropped out of the bounded command lane", "timestamp": "606"}, {"event_type": "safe_state_required", "metadata::safe_state_value": "0", "output_id": "labjack_u6_470201:digital_out_0", "owner": "", "summary": "target degraded and safe state required", "timestamp": "606"}, {"event_type": "target_degraded", "output_id": "rpi_rpi_lab_401:gpio_out_0", "owner": "", "summary": "adapter dropped out of the bounded command lane", "timestamp": "606"}, {"event_type": "target_restored", "output_id": "labjack_u6_470201:digital_out_0", "owner": "", "summary": "adapter returned to the bounded command lane", "timestamp": "607"}, {"event_type": "target_restored", "output_id": "rpi_rpi_lab_401:gpio_out_0", "owner": "", "summary": "adapter returned to the bounded command lane", "timestamp": "607"}]}
- [PASS] cross_device_command_replay_tail — {"tail_record_count": 14, "tail_record_counts_by_type": {"adapter_command": 2, "command_trace": 2, "cycle": 1, "runtime_event": 6, "sample": 3}}

## Shell smoke output

```text
shell-smoke: profile=PROF-SMOKE page=review mode=live device_phase=live detected=4 command_allowed=False ack_states=(<AlarmLifecycleState.ASSERTED: 'asserted'>,) manifest=MAN-SMOKE-001
```

## Long-run populated review summary

- session_id: SESSION-POPULATED-REVIEW
- hot_recent_sample_count: 36
- warm_variable_row_count: 36
- warm_cycle_row_count: 18
- warm_runtime_event_count: 59
- cold_segment_count: 38
- cold_persisted_record_count: 149
- checkpoint_count: 4
- checkpoint_sequence_ids: [33, 66, 99, 132]

## Replay summary

- checkpoint_id: CHK-SESSION-POPULATED-REVIEW-45-132
- tail_record_count: 17
- tail_record_type_count: 4
- tail_contains_multiple_record_types: True
- replay_state_hash: af92b2ceb751c4c9f784eee53e7d612ecbc0b2f47585909b53f93b751a3a3355

## Long-run characterization

- average_records_per_segment: 3.92
- checkpoint_density_per_cycle: 0.222
- bounded_run_window_ticks: 48
- runtime_event_diversity: 4

## Session artifact summary

- session_root: /mnt/data/udq10_work/proof/acceptance/20260327_023724/reviewability/runtime/sessions/SESSION-POPULATED-REVIEW
- entry_count: 149
- checkpoint_count: 4
- segment_count: 38

## Repeatability gate

- verdict: PASS
- run_count: 3
- consistent_depth_metrics: True
- consistent_replay_metrics: True
- minimum_valid_checkpoint_count: 4

## Fallback recovery summary

- corrupted_checkpoint_id: CHK-SESSION-FAULT-INJECTION-115-132
- recovered_checkpoint_id: CHK-SESSION-FAULT-INJECTION-111-99
- fallback_candidate_count: 3
- replay_tail_count: 34
- replay_tail_record_type_count: 4
- replay_tail_contains_multiple_record_types: True
- state_hash_matches: True

## Real-hardware specimen bridge

- verdict: SKIP
- mode: driver_unavailable
- reason: LabJack driver unavailable (not-installed)
- driver_name: not-installed
- resolved_serial_number: None

## Cross-device read-side closure

- verdict: PASS
- activated_adapter_count: 3
- tag_definition_count: 21
- latest_sample_count: 17
- ARDUINO-UNO-ARD-401: 5
- LABJACK-U6-470201: 8
- RPI-RPI-LAB-401: 4

## Cross-device command and arbitration

- verdict: PASS
- writable_tag_count: 3
- command_attempt_count: 10
- accepted_count: 6
- rejected_count: 4
- ownership_conflict_count: 2
- degraded_transition_count: 6
- replay_tail_count: 14
