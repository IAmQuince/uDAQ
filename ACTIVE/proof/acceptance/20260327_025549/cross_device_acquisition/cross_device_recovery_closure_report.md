# UniversalDAQ Cross-Device Recovery and Repeatability Closure

- generated_at_utc: 2026-03-27T02:55:52.874021+00:00
- verdict: PASS
- session_id: SESSION-CROSS-DEVICE-CLOSURE
- report_dir: /mnt/data/udq11_run/proof/acceptance/20260327_025549/cross_device_acquisition
- activated_adapter_count: 3
- tag_definition_count: 21
- latest_sample_count: 17

## History depth

- persisted_record_count: 268
- segment_count: 67
- valid_checkpoint_count: 3
- checkpoint_sequence_ids: [83, 149, 227]

## Nominal replay

- tail_record_count: 41
- tail_record_type_count: 3
- tail_contains_multiple_record_types: True

## Fallback recovery

- corrupted_checkpoint_id: CHK-SESSION-CROSS-DEVICE-CLOSURE-311-227
- recovered_checkpoint_id: CHK-SESSION-CROSS-DEVICE-CLOSURE-307-149
- replay_tail_count: 119
- replay_tail_record_type_count: 3
- state_hash_matches: True

## Degraded conditions

- degraded_transition_count: 5
- simultaneous_drop_event_count: 1
- adapters_seen_degraded: ['ARDUINO-UNO-ARD-401', 'LABJACK-U6-470201', 'RPI-RPI-LAB-401']

## Repeatability

- verdict: PASS
- run_count: 3
- consistent_depth_metrics: True
- consistent_replay_metrics: True
- consistent_fallback_metrics: True

## Checks

- [PASS] activated_adapter_count — ["ARDUINO-UNO-ARD-401", "LABJACK-U6-470201", "RPI-RPI-LAB-401"]
- [PASS] nonzero_tag_population_per_adapter — {"ARDUINO-UNO-ARD-401": 5, "LABJACK-U6-470201": 8, "RPI-RPI-LAB-401": 4}
- [PASS] mixed_source_variable_population — ["VAR-MIXED-ANALOG-DELTA", "VAR-MIXED-ANALOG-SUM", "VAR-MIXED-RPI-CPU-GATE"]
- [PASS] mixed_source_review_queryable — {"ARDUINO-UNO-ARD-401:analog_in_0": 4, "ARDUINO-UNO-ARD-401:analog_in_1": 4, "ARDUINO-UNO-ARD-401:digital_in_2": 4, "ARDUINO-UNO-ARD-401:digital_in_3": 4, "ARDUINO-UNO-ARD-401:firmware_alive": 4, "LABJACK-U6-470201:analog_in_0": 5, "LABJACK-U6-470201:analog_in_1": 5, "LABJACK-U6-470201:analog_in_2": 5, "LABJACK-U6-470201:analog_in_3": 5, "LABJACK-U6-470201:digital_in_0": 5, "LABJACK-U6-470201:digital_in_1": 5, "LABJACK-U6-470201:digital_in_2": 5, "LABJACK-U6-470201:digital_in_3": 5, "RPI-RPI-LAB-401:gpio_in_17": 5, "RPI-RPI-LAB-401:gpio_in_27": 5, "RPI-RPI-LAB-401:host_cpu_temp_c": 5, "RPI-RPI-LAB-401:host_uptime_s": 5}
- [PASS] checkpoint_ladder_depth — {"count": 3, "spacing": {"average_sequence_gap": 72.0, "max_sequence_gap": 78, "min_sequence_gap": 66}}
- [PASS] nontrivial_mixed_source_replay — tail=41 first=228 last=268
- [PASS] multi_type_mixed_source_replay — {"cycle": 2, "runtime_event": 5, "sample": 34}
- [PASS] mixed_source_fallback_recovery — recovered_checkpoint_id=CHK-SESSION-CROSS-DEVICE-CLOSURE-307-149
- [PASS] fallback_nonzero_tail_replay — tail=119
- [PASS] fallback_multi_type_tail_replay — {"cycle": 6, "runtime_event": 15, "sample": 98}
- [PASS] fallback_state_hash_valid — state_hash_matches=True
- [PASS] degraded_conditions_documented — {"degraded_transition_count": 5, "simultaneous_drop_event_count": 1}
- [PASS] degraded_conditions_cover_all_adapters — ["ARDUINO-UNO-ARD-401", "LABJACK-U6-470201", "RPI-RPI-LAB-401"]
- [PASS] artifact_integrity — entries=268 checkpoints=3
- [PASS] repeatability_gate — {"consistent_depth_metrics": true, "consistent_fallback_metrics": true, "consistent_replay_metrics": true, "run_count": 3}
