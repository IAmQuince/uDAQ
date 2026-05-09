from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

if __package__ in {None, ''}:
    _REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))


def _prepare_import_path(package_root: Path) -> None:
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _is_floatish(value: object) -> bool:
    try:
        float(str(value))
    except (TypeError, ValueError):
        return False
    return True


def _build_variable_results(*, tag_rows: tuple[dict[str, object], ...], timestamp):
    from universaldaq.common import SignalQuality, VariableId
    from universaldaq.signals import VariableEvaluationResult, VariableSnapshot, VariableState

    values = {str(row['canonical_name']): float(row['value']) for row in tag_rows if row['value_type'] in {'analog', 'status'} and _is_floatish(row['value'])}
    u6 = values['labjack_u6_470201.analog_in_0']
    arduino = values['arduino_uno_ard_401.analog_in_0']
    cpu_temp = values['rpi_rpi_lab_401.host_cpu_temp_c']
    analog_sum = round(u6 + arduino, 6)
    delta = round(u6 - arduino, 6)
    cpu_gate = '1' if cpu_temp >= 45.0 else '0'
    return (
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-MIXED-ANALOG-SUM'),
                value=f'{analog_sum:.6f}',
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={
                    'labjack_u6_470201.analog_in_0': f'{u6:.6f}',
                    'arduino_uno_ard_401.analog_in_0': f'{arduino:.6f}',
                },
            ),
            resolved_dependencies={
                'labjack_u6_470201.analog_in_0': f'{u6:.6f}',
                'arduino_uno_ard_401.analog_in_0': f'{arduino:.6f}',
            },
        ),
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-MIXED-ANALOG-DELTA'),
                value=f'{delta:.6f}',
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={
                    'labjack_u6_470201.analog_in_0': f'{u6:.6f}',
                    'arduino_uno_ard_401.analog_in_0': f'{arduino:.6f}',
                },
            ),
            resolved_dependencies={
                'labjack_u6_470201.analog_in_0': f'{u6:.6f}',
                'arduino_uno_ard_401.analog_in_0': f'{arduino:.6f}',
            },
        ),
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-MIXED-RPI-CPU-GATE'),
                value=cpu_gate,
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={'rpi_rpi_lab_401.host_cpu_temp_c': f'{cpu_temp:.6f}'},
            ),
            resolved_dependencies={'rpi_rpi_lab_401.host_cpu_temp_c': f'{cpu_temp:.6f}'},
        ),
    )


def _find_adapter_id(adapter_ids: Iterable[str], needle: str) -> str:
    needle_lower = needle.lower()
    for adapter_id in adapter_ids:
        if needle_lower in adapter_id.lower():
            return adapter_id
    raise KeyError(f'expected adapter containing {needle!r} not found in {tuple(adapter_ids)!r}')


_DEGRADED_PLAN_TEMPLATE = {
    5: ('drop', ('labjack', 'arduino')),
    6: ('restore', ('labjack',)),
    7: ('restore', ('arduino',)),
    9: ('drop', ('rpi',)),
    10: ('restore', ('rpi',)),
}


def _build_runtime_quality(*, output_root: Path, session_id: str, checkpoint_interval_cycles: int):
    from universaldaq.runtime import RuntimeQualityService

    runtime_root = output_root / 'runtime'
    runtime = RuntimeQualityService(
        journal_file_path=runtime_root / 'session.jsonl',
        journal_max_segment_records=4,
        point_history_limit=256,
        event_history_limit=256,
        cycle_history_limit=256,
        variable_history_limit=256,
        presentation_interval_ticks=1,
        session_id=session_id,
        auto_checkpoint_interval_cycles=max(1, checkpoint_interval_cycles),
    )
    return runtime, runtime_root


def _write_tag_inventory(output_root: Path, payload: dict[str, object]) -> None:
    inventory = {
        'tag_rows': payload['tag_rows'],
        'tag_counts_by_adapter': payload['tag_counts_by_adapter'],
        'tag_counts_by_value_type': payload['tag_counts_by_value_type'],
    }
    _write_json(output_root / 'tag_inventory.json', inventory)
    lines = ['# UniversalDAQ Cross-Device Tag Inventory', '', '## Tags', '']
    for row in payload['tag_rows']:
        lines.append(
            f"- {row['tag_key']} canonical={row['canonical_name']} adapter={row['adapter_id']} point={row['source_point_id']} value={row['value']} quality={row['quality']}"
        )
    lines.extend(['', '## Counts by adapter', ''])
    for adapter_id, count in payload['tag_counts_by_adapter'].items():
        lines.append(f'- {adapter_id}: {count}')
    lines.extend(['', '## Counts by value type', ''])
    for value_type, count in payload['tag_counts_by_value_type'].items():
        lines.append(f'- {value_type}: {count}')
    _write_markdown(output_root / 'tag_inventory.md', lines)


def _write_degraded_timeline(output_root: Path, timeline: dict[str, object]) -> None:
    _write_json(output_root / 'degraded_adapter_timeline.json', timeline)
    lines = [
        '# UniversalDAQ Cross-Device Degraded Adapter Timeline',
        '',
        f"- simultaneous_drop_event_count: {timeline['simultaneous_drop_event_count']}",
        f"- degraded_transition_count: {timeline['degraded_transition_count']}",
        f"- adapters_seen_degraded: {timeline['adapters_seen_degraded']}",
        '',
        '## Cycle transitions',
        '',
    ]
    for event in timeline['events']:
        lines.append(
            f"- cycle={event['cycle_index']} tick={event['tick']} action={event['action']} adapters={event['adapter_ids']} active_after={event['active_adapter_ids_after']}"
        )
    _write_markdown(output_root / 'degraded_adapter_timeline.md', lines)


def _write_repeatability(output_root: Path, payload: dict[str, object]) -> None:
    _write_json(output_root / 'repeatability_report.json', payload)
    lines = [
        '# UniversalDAQ Cross-Device Repeatability Report',
        '',
        f"- verdict: {payload['verdict']}",
        f"- run_count: {payload['run_count']}",
        f"- consistent_depth_metrics: {payload['consistent_depth_metrics']}",
        f"- consistent_replay_metrics: {payload['consistent_replay_metrics']}",
        f"- consistent_fallback_metrics: {payload['consistent_fallback_metrics']}",
        '',
        '## Runs',
        '',
    ]
    for run in payload['runs']:
        lines.append(
            f"- {run['session_id']}: records={run['persisted_record_count']} checkpoints={run['valid_checkpoint_count']} tail={run['replay_tail_record_count']} fallback_tail={run['fallback_tail_record_count']} degraded_events={run['degraded_transition_count']}"
        )
    _write_markdown(output_root / 'repeatability_report.md', lines)


def _write_summary_markdown(path: Path, payload: dict[str, object]) -> None:
    history = payload['history_tier_summary']
    replay = payload['replay_report']
    checkpoint = payload['checkpoint_summary']
    fallback = payload['fallback_recovery_report']
    repeatability = payload['repeatability_report']
    degraded = payload['degraded_conditions_report']
    lines = [
        '# UniversalDAQ Cross-Device Recovery and Repeatability Closure',
        '',
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- verdict: {payload['verdict']}",
        f"- session_id: {payload['session_id']}",
        f"- report_dir: {payload['report_dir']}",
        f"- activated_adapter_count: {payload['activated_adapter_count']}",
        f"- tag_definition_count: {payload['tag_definition_count']}",
        f"- latest_sample_count: {payload['latest_sample_count']}",
        '',
        '## History depth',
        '',
        f"- persisted_record_count: {history['cold']['persisted_record_count']}",
        f"- segment_count: {history['cold']['segment_count']}",
        f"- valid_checkpoint_count: {checkpoint['valid_checkpoint_count']}",
        f"- checkpoint_sequence_ids: {[int(row.get('last_committed_sequence_id', 0) or 0) for row in checkpoint.get('checkpoint_ladder', [])]}",
        '',
        '## Nominal replay',
        '',
        f"- tail_record_count: {replay['tail_record_count']}",
        f"- tail_record_type_count: {replay['tail_record_type_count']}",
        f"- tail_contains_multiple_record_types: {replay['tail_contains_multiple_record_types']}",
        '',
        '## Fallback recovery',
        '',
        f"- corrupted_checkpoint_id: {fallback['corrupted_checkpoint_id']}",
        f"- recovered_checkpoint_id: {fallback['recovered_checkpoint_id']}",
        f"- replay_tail_count: {fallback['replay_tail_count']}",
        f"- replay_tail_record_type_count: {fallback['replay_tail_record_type_count']}",
        f"- state_hash_matches: {fallback['state_hash_matches']}",
        '',
        '## Degraded conditions',
        '',
        f"- degraded_transition_count: {degraded['degraded_transition_count']}",
        f"- simultaneous_drop_event_count: {degraded['simultaneous_drop_event_count']}",
        f"- adapters_seen_degraded: {degraded['adapters_seen_degraded']}",
        '',
        '## Repeatability',
        '',
        f"- verdict: {repeatability['verdict']}",
        f"- run_count: {repeatability['run_count']}",
        f"- consistent_depth_metrics: {repeatability['consistent_depth_metrics']}",
        f"- consistent_replay_metrics: {repeatability['consistent_replay_metrics']}",
        f"- consistent_fallback_metrics: {repeatability['consistent_fallback_metrics']}",
        '',
        '## Checks',
        '',
    ]
    for check in payload['checks']:
        lines.append(f"- [{check['status']}] {check['name']} — {check['message']}")
    _write_markdown(path, lines)


def _build_fallback_report(*, runtime, output_root: Path) -> dict[str, object]:
    checkpoint_rows_before = runtime.checkpoint_rows()
    corrupted_checkpoint_id = None if not checkpoint_rows_before else str(checkpoint_rows_before[-1]['checkpoint_id'])
    latest_path = runtime.checkpoints._latest_path
    assert latest_path is not None
    latest_payload = json.loads(latest_path.read_text(encoding='utf-8'))
    latest_payload['state_hash'] = 'corrupted'
    latest_path.write_text(json.dumps(latest_payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    if corrupted_checkpoint_id is not None and runtime.checkpoints._checkpoint_dir is not None:
        checkpoint_path = runtime.checkpoints._checkpoint_dir / f'{corrupted_checkpoint_id}.json'
        checkpoint_payload = json.loads(checkpoint_path.read_text(encoding='utf-8'))
        checkpoint_payload['state_hash'] = 'corrupted'
        checkpoint_path.write_text(json.dumps(checkpoint_payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')

    recovered_checkpoint = runtime.latest_checkpoint()
    recovery_bundle = runtime.build_recovery_bundle(limit=2048)
    replay_report = recovery_bundle['replay_report']
    valid_checkpoint_rows = [row for row in runtime.checkpoint_rows() if bool(row.get('hash_valid'))]
    report = {
        'verdict': 'PASS' if recovered_checkpoint is not None else 'FAIL',
        'latest_checkpoint_corrupted': True,
        'corrupted_checkpoint_id': corrupted_checkpoint_id,
        'recovered_checkpoint_id': None if recovered_checkpoint is None else recovered_checkpoint.checkpoint_id,
        'recovered_last_committed_sequence_id': None if recovered_checkpoint is None else recovered_checkpoint.last_committed_sequence_id,
        'fallback_candidate_count': len(valid_checkpoint_rows),
        'replay_tail_count': len(recovery_bundle.get('journal_tail', ())),
        'replay_tail_counts_by_type': dict(replay_report.get('tail_record_counts_by_type', {})),
        'replay_tail_record_type_count': int(replay_report.get('tail_record_type_count', 0) or 0),
        'replay_tail_contains_multiple_record_types': bool(replay_report.get('tail_contains_multiple_record_types', False)),
        'replay_tail_first_sequence_id': replay_report.get('tail_first_sequence_id'),
        'replay_tail_last_sequence_id': replay_report.get('tail_last_sequence_id'),
        'state_hash_matches': bool(recovery_bundle.get('state_hash_matches', False)),
        'reconstructed_state_hash': recovery_bundle.get('reconstructed_state_hash'),
        'checkpoint_sequence_ids': [
            int(row.get('last_committed_sequence_id', 0) or 0)
            for row in valid_checkpoint_rows
        ],
        'segment_ranges': [
            {
                'segment_id': row.get('segment_id'),
                'first_sequence_id': row.get('first_sequence_id'),
                'last_sequence_id': row.get('last_sequence_id'),
                'record_count': row.get('record_count'),
            }
            for row in runtime.journal.segment_index_rows()
        ],
    }

    from tools.acceptance.run_fault_injection import _write_fallback_recovery_artifacts

    _write_fallback_recovery_artifacts(output_root, report)
    return report


def _run_single_session(
    *,
    package_root: Path,
    output_root: Path,
    session_id: str,
    cycle_count: int,
    checkpoint_interval_cycles: int,
    start_tick: int,
) -> dict[str, object]:
    _prepare_import_path(package_root)

    from tools.acceptance.verify_session_artifacts import verify_session_artifacts
    from universaldaq.app import build_default_service_registry
    from universaldaq.adapters import AdapterPollResult
    from universaldaq.common import SignalQuality, as_event_time
    from universaldaq.tags import CanonicalTagRegistryService, MultiAdapterAcquisitionBroker
    from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary
    from universaldaq_arduino.models import ArduinoProbeRow
    from universaldaq_arduino.plugin import build_support_pack_registration as build_arduino_pack
    from universaldaq_labjack.models import LabJackProbeRow
    from universaldaq_labjack.plugin import build_support_pack_registration as build_labjack_pack
    from universaldaq_rpi.models import RaspberryPiProbeRow
    from universaldaq_rpi.plugin import build_support_pack_registration as build_rpi_pack

    output_root.mkdir(parents=True, exist_ok=True)
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.install_support_pack(
        build_labjack_pack(probe_rows=(LabJackProbeRow(model='U6', serial_number='470201', transport='usb'),))
    )
    services.adapters.install_support_pack(
        build_arduino_pack(probe_rows=(ArduinoProbeRow(board='Uno', serial_number='ARD-401', port='COM41'),))
    )
    services.adapters.install_support_pack(
        build_rpi_pack(probe_rows=(RaspberryPiProbeRow(model='5', host_id='rpi-lab-401', enable_gpio=True),))
    )

    discovered = services.adapters.discover_devices(timestamp=as_event_time(start_tick - 5))
    activated_adapter_ids: list[str] = []
    target_provider_ids = {'labjack_u6_support', 'arduino_serial_support', 'raspberry_pi_support'}
    for device in discovered:
        if device.provider_id not in target_provider_ids:
            continue
        activated, adapter_id, _ = services.adapters.activate_discovered_device(device_key=device.device_key)
        if adapter_id is None:
            continue
        services.device_registry.register_or_attach(
            identity=activated.identity,
            provider_id=activated.provider_id,
            transport_path=activated.identity.transport,
            timestamp=as_event_time(start_tick - 4),
        )
        activated_adapter_ids.append(adapter_id)

    family_map = {
        'labjack': _find_adapter_id(activated_adapter_ids, 'labjack'),
        'arduino': _find_adapter_id(activated_adapter_ids, 'arduino'),
        'rpi': _find_adapter_id(activated_adapter_ids, 'rpi'),
    }
    current_active = set(activated_adapter_ids)
    tag_registry = CanonicalTagRegistryService(metrics=services.runtime_metrics)
    broker = MultiAdapterAcquisitionBroker(adapter_manager=services.adapters, tag_registry=tag_registry, metrics=services.runtime_metrics)
    runtime, runtime_root = _build_runtime_quality(output_root=output_root, session_id=session_id, checkpoint_interval_cycles=checkpoint_interval_cycles)
    previous_variable_snapshots: dict[str, object] = {}
    degraded_events: list[dict[str, object]] = []

    for offset in range(max(1, cycle_count)):
        cycle_index = offset + 1
        tick = start_tick + offset
        ts = as_event_time(tick)
        transition = _DEGRADED_PLAN_TEMPLATE.get(cycle_index)
        if transition is not None:
            action, families = transition
            affected_ids = [family_map[family] for family in families]
            for adapter_id in affected_ids:
                if action == 'drop':
                    current_active.discard(adapter_id)
                elif action == 'restore':
                    current_active.add(adapter_id)
            degraded_events.append(
                {
                    'cycle_index': cycle_index,
                    'tick': tick,
                    'action': action,
                    'adapter_ids': affected_ids,
                    'active_adapter_ids_after': sorted(current_active),
                }
            )
            runtime.record_state_event(
                timestamp=ts,
                event_type='adapter_state_transition',
                attributes={
                    'action': action,
                    'adapter_ids': ','.join(sorted(affected_ids)),
                    'transition_count': len(affected_ids),
                    'active_adapter_count_after': len(current_active),
                },
            )
            if action == 'drop' and len(affected_ids) > 1:
                runtime.record_state_event(
                    timestamp=ts,
                    event_type='simultaneous_adapter_dropout',
                    attributes={
                        'adapter_ids': ','.join(sorted(affected_ids)),
                        'drop_count': len(affected_ids),
                    },
                )
        active_ids = tuple(sorted(current_active))
        batch = broker.poll(adapter_ids=active_ids, timestamp=ts)
        snapshots = []
        for adapter_id in active_ids:
            poll_result = services.adapters.last_poll_results.get(adapter_id)
            if poll_result is None:
                continue
            runtime.capture_acquisition(adapter_id=adapter_id, timestamp=ts, poll_result=poll_result)
            snapshots.extend(poll_result.snapshots)

        tag_rows = tag_registry.latest_sample_rows()
        variable_results = _build_variable_results(tag_rows=tag_rows, timestamp=ts)
        runtime.record_variable_results(timestamp=ts, results=variable_results, previous_snapshots=previous_variable_snapshots)
        previous_variable_snapshots = {str(result.snapshot.variable_id): result.snapshot for result in variable_results}
        runtime.record_state_event(
            timestamp=ts,
            event_type='cross_device_health_summary',
            attributes={
                'healthy_adapter_count': len(active_ids),
                'degraded_adapter_count': len(activated_adapter_ids) - len(active_ids),
                'runtime_mode': 'mixed_source_read_only',
            },
        )
        runtime.record_state_event(
            timestamp=ts,
            event_type='cross_device_poll_cycle',
            attributes={
                'adapter_count': len(active_ids),
                'sample_count': len(batch.samples),
                'tag_count': len(tag_registry.definitions),
            },
        )
        combined_poll_result = AdapterPollResult(
            adapter_id='BROKER-MIXED-001',
            polled_at=ts,
            snapshots=tuple(snapshots),
            diagnostics=batch.diagnostics,
        )
        runtime.record_processed_cycle(
            timestamp=ts,
            lifecycle_summary=DeviceLifecycleSummary(
                phase='live',
                detected_device_count=len(discovered),
                active_device_key='MIXED-SOURCE-SESSION',
                active_adapter_id='BROKER-MIXED-001',
                projected_point_count=len(tag_registry.definitions),
                published_signal_count=len(snapshots),
                last_poll_snapshot_count=len(snapshots),
                disconnected_signal_count=max(0, len(activated_adapter_ids) - len(active_ids)),
                last_transition='poll_multi_adapter_broker',
                needs_review=len(active_ids) != len(activated_adapter_ids),
            ),
            variable_summary=VariableHealthSummary(total_variable_count=len(variable_results), healthy_count=len(variable_results)),
            changed_signal_ids=tuple(sample.tag_key for sample in batch.samples),
            poll_result=combined_poll_result,
        )

    tail_tick = start_tick + max(1, cycle_count)
    runtime.record_state_event(
        timestamp=as_event_time(tail_tick),
        event_type='cross_device_tail_verification',
        attributes={
            'activated_adapter_count': len(activated_adapter_ids),
            'degraded_transition_count': len(degraded_events),
        },
    )
    runtime.flush_journal(now=as_event_time(tail_tick))
    review_summary = runtime.build_review_summary(limit=48)
    review_summary['session_root'] = str(runtime_root / 'sessions' / session_id)
    session_root = Path(review_summary['session_root'])
    tag_rows = list(tag_registry.latest_sample_rows())
    tag_counts_by_value_type: dict[str, int] = {}
    for definition in tag_registry.definitions.values():
        tag_counts_by_value_type[definition.value_type.value] = tag_counts_by_value_type.get(definition.value_type.value, 0) + 1

    degraded_report = {
        'events': degraded_events,
        'degraded_transition_count': len(degraded_events),
        'simultaneous_drop_event_count': sum(1 for event in degraded_events if event['action'] == 'drop' and len(event['adapter_ids']) > 1),
        'adapters_seen_degraded': sorted({adapter_id for event in degraded_events for adapter_id in event['adapter_ids']}),
        'max_degraded_adapter_count': max((len(activated_adapter_ids) - len(event['active_adapter_ids_after']) for event in degraded_events), default=0),
    }
    _write_json(output_root / 'review_summary.json', review_summary)
    _write_degraded_timeline(output_root, degraded_report)
    _write_tag_inventory(
        output_root,
        {
            'tag_rows': tag_rows,
            'tag_counts_by_adapter': tag_registry.counts_by_adapter(),
            'tag_counts_by_value_type': dict(sorted(tag_counts_by_value_type.items())),
        },
    )
    fallback_report = _build_fallback_report(runtime=runtime, output_root=output_root)
    session_artifact_report = verify_session_artifacts(session_root)

    return {
        'session_id': session_id,
        'report_dir': str(output_root),
        'activated_adapter_count': len(activated_adapter_ids),
        'activated_adapter_ids': sorted(activated_adapter_ids),
        'tag_definition_count': len(tag_registry.definitions),
        'latest_sample_count': len(tag_registry.latest_samples),
        'tag_rows': tag_rows,
        'tag_counts_by_adapter': tag_registry.counts_by_adapter(),
        'tag_counts_by_value_type': dict(sorted(tag_counts_by_value_type.items())),
        'history_tier_summary': review_summary['history_tier_summary'],
        'history_index_report': review_summary['history_index_report'],
        'checkpoint_summary': review_summary['checkpoint_summary'],
        'replay_report': review_summary['replay_report'],
        'session_artifact_report': session_artifact_report,
        'degraded_conditions_report': degraded_report,
        'fallback_recovery_report': fallback_report,
        'review_summary': review_summary,
    }


def _run_repeatability(*, package_root: Path, output_root: Path, run_count: int, cycle_count: int, checkpoint_interval_cycles: int) -> dict[str, object]:
    runs = []
    for index in range(run_count):
        session = _run_single_session(
            package_root=package_root,
            output_root=output_root / f'run_{index + 1:02d}',
            session_id=f'SESSION-CROSS-DEVICE-CLOSURE-{index + 1:02d}',
            cycle_count=cycle_count,
            checkpoint_interval_cycles=checkpoint_interval_cycles,
            start_tick=500 + index * 100,
        )
        runs.append(
            {
                'session_id': session['session_id'],
                'persisted_record_count': int(session['history_tier_summary']['cold']['persisted_record_count']),
                'valid_checkpoint_count': int(session['checkpoint_summary']['valid_checkpoint_count']),
                'segment_count': int(session['history_tier_summary']['cold']['segment_count']),
                'replay_tail_record_count': int(session['replay_report']['tail_record_count']),
                'replay_tail_record_type_count': int(session['replay_report']['tail_record_type_count']),
                'fallback_tail_record_count': int(session['fallback_recovery_report']['replay_tail_count']),
                'fallback_tail_record_type_count': int(session['fallback_recovery_report']['replay_tail_record_type_count']),
                'degraded_transition_count': int(session['degraded_conditions_report']['degraded_transition_count']),
                'simultaneous_drop_event_count': int(session['degraded_conditions_report']['simultaneous_drop_event_count']),
                'activated_adapter_count': int(session['activated_adapter_count']),
                'tag_definition_count': int(session['tag_definition_count']),
            }
        )
    depth_vectors = {
        (run['persisted_record_count'], run['valid_checkpoint_count'], run['segment_count'])
        for run in runs
    }
    replay_vectors = {
        (run['replay_tail_record_count'], run['replay_tail_record_type_count'])
        for run in runs
    }
    fallback_vectors = {
        (run['fallback_tail_record_count'], run['fallback_tail_record_type_count'])
        for run in runs
    }
    payload = {
        'verdict': 'PASS' if len(depth_vectors) == 1 and len(replay_vectors) == 1 and len(fallback_vectors) == 1 else 'FAIL',
        'run_count': len(runs),
        'consistent_depth_metrics': len(depth_vectors) == 1,
        'consistent_replay_metrics': len(replay_vectors) == 1,
        'consistent_fallback_metrics': len(fallback_vectors) == 1,
        'runs': runs,
    }
    _write_repeatability(output_root, payload)
    return payload


def run_cross_device_recovery_closure(
    *,
    package_root: Path,
    output_root: Path,
    session_id: str = 'SESSION-CROSS-DEVICE-CLOSURE',
    cycle_count: int = 14,
    checkpoint_interval_cycles: int = 4,
    repeatability_runs: int = 3,
) -> dict[str, object]:
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    output_root.mkdir(parents=True, exist_ok=True)
    session = _run_single_session(
        package_root=package_root,
        output_root=output_root / 'session',
        session_id=session_id,
        cycle_count=cycle_count,
        checkpoint_interval_cycles=checkpoint_interval_cycles,
        start_tick=300,
    )
    repeatability_report = _run_repeatability(
        package_root=package_root,
        output_root=output_root / 'repeatability',
        run_count=max(1, repeatability_runs),
        cycle_count=cycle_count,
        checkpoint_interval_cycles=checkpoint_interval_cycles,
    )

    replay = session['replay_report']
    fallback = session['fallback_recovery_report']
    degraded = session['degraded_conditions_report']
    checkpoint = session['checkpoint_summary']
    checks = [
        {
            'name': 'activated_adapter_count',
            'status': 'PASS' if session['activated_adapter_count'] >= 3 else 'FAIL',
            'message': json.dumps(session['activated_adapter_ids'], sort_keys=True),
        },
        {
            'name': 'nonzero_tag_population_per_adapter',
            'status': 'PASS' if all(count > 0 for count in session['tag_counts_by_adapter'].values()) and len(session['tag_counts_by_adapter']) >= 3 else 'FAIL',
            'message': json.dumps(session['tag_counts_by_adapter'], sort_keys=True),
        },
        {
            'name': 'mixed_source_variable_population',
            'status': 'PASS' if len(session['history_index_report']['variable_ids']) >= 3 else 'FAIL',
            'message': json.dumps(session['history_index_report']['variable_ids'], sort_keys=True),
        },
        {
            'name': 'mixed_source_review_queryable',
            'status': 'PASS' if len(session['history_index_report']['sample_counts_by_point']) >= 6 else 'FAIL',
            'message': json.dumps(session['history_index_report']['sample_counts_by_point'], sort_keys=True),
        },
        {
            'name': 'checkpoint_ladder_depth',
            'status': 'PASS' if checkpoint['valid_checkpoint_count'] >= 3 else 'FAIL',
            'message': json.dumps({'count': checkpoint['valid_checkpoint_count'], 'spacing': checkpoint['checkpoint_spacing']}, sort_keys=True),
        },
        {
            'name': 'nontrivial_mixed_source_replay',
            'status': 'PASS' if replay['tail_record_count'] >= 8 else 'FAIL',
            'message': f"tail={replay['tail_record_count']} first={replay.get('tail_first_sequence_id')} last={replay.get('tail_last_sequence_id')}",
        },
        {
            'name': 'multi_type_mixed_source_replay',
            'status': 'PASS' if replay['tail_contains_multiple_record_types'] and replay['tail_record_type_count'] >= 3 else 'FAIL',
            'message': json.dumps(replay['tail_record_counts_by_type'], sort_keys=True),
        },
        {
            'name': 'mixed_source_fallback_recovery',
            'status': fallback['verdict'],
            'message': f"recovered_checkpoint_id={fallback['recovered_checkpoint_id']}",
        },
        {
            'name': 'fallback_nonzero_tail_replay',
            'status': 'PASS' if fallback['replay_tail_count'] >= 8 else 'FAIL',
            'message': f"tail={fallback['replay_tail_count']}",
        },
        {
            'name': 'fallback_multi_type_tail_replay',
            'status': 'PASS' if fallback['replay_tail_contains_multiple_record_types'] and fallback['replay_tail_record_type_count'] >= 3 else 'FAIL',
            'message': json.dumps(fallback['replay_tail_counts_by_type'], sort_keys=True),
        },
        {
            'name': 'fallback_state_hash_valid',
            'status': 'PASS' if fallback['state_hash_matches'] else 'FAIL',
            'message': f"state_hash_matches={fallback['state_hash_matches']}",
        },
        {
            'name': 'degraded_conditions_documented',
            'status': 'PASS' if degraded['degraded_transition_count'] >= 4 and degraded['simultaneous_drop_event_count'] >= 1 else 'FAIL',
            'message': json.dumps({'degraded_transition_count': degraded['degraded_transition_count'], 'simultaneous_drop_event_count': degraded['simultaneous_drop_event_count']}, sort_keys=True),
        },
        {
            'name': 'degraded_conditions_cover_all_adapters',
            'status': 'PASS' if len(degraded['adapters_seen_degraded']) >= 3 else 'FAIL',
            'message': json.dumps(degraded['adapters_seen_degraded'], sort_keys=True),
        },
        {
            'name': 'artifact_integrity',
            'status': session['session_artifact_report']['verdict'],
            'message': f"entries={session['session_artifact_report']['entry_count']} checkpoints={len(session['session_artifact_report']['checkpoint_rows'])}",
        },
        {
            'name': 'repeatability_gate',
            'status': repeatability_report['verdict'],
            'message': json.dumps({'run_count': repeatability_report['run_count'], 'consistent_depth_metrics': repeatability_report['consistent_depth_metrics'], 'consistent_replay_metrics': repeatability_report['consistent_replay_metrics'], 'consistent_fallback_metrics': repeatability_report['consistent_fallback_metrics']}, sort_keys=True),
        },
    ]
    verdict = 'PASS' if all(check['status'] == 'PASS' for check in checks) else 'FAIL'
    for name in (
        'review_summary.json',
        'degraded_adapter_timeline.json',
        'degraded_adapter_timeline.md',
        'fallback_recovery_detail.json',
        'fallback_recovery_detail.md',
        'session_timeline.json',
        'session_timeline.md',
        'tag_inventory.json',
        'tag_inventory.md',
    ):
        source = output_root / 'session' / name
        if source.exists():
            shutil.copyfile(source, output_root / name)
    for name in ('repeatability_report.json', 'repeatability_report.md'):
        source = output_root / 'repeatability' / name
        if source.exists():
            shutil.copyfile(source, output_root / name)

    payload = {
        'generated_at_utc': generated_at_utc,
        'verdict': verdict,
        'session_id': session_id,
        'report_dir': str(output_root),
        'activated_adapter_count': session['activated_adapter_count'],
        'activated_adapter_ids': session['activated_adapter_ids'],
        'tag_definition_count': session['tag_definition_count'],
        'latest_sample_count': session['latest_sample_count'],
        'tag_rows': session['tag_rows'],
        'tag_counts_by_adapter': session['tag_counts_by_adapter'],
        'tag_counts_by_value_type': session['tag_counts_by_value_type'],
        'history_tier_summary': session['history_tier_summary'],
        'history_index_report': session['history_index_report'],
        'checkpoint_summary': session['checkpoint_summary'],
        'replay_report': session['replay_report'],
        'session_artifact_report': session['session_artifact_report'],
        'degraded_conditions_report': session['degraded_conditions_report'],
        'fallback_recovery_report': session['fallback_recovery_report'],
        'repeatability_report': repeatability_report,
        'checks': checks,
    }
    _write_json(output_root / 'cross_device_recovery_closure_report.json', payload)
    _write_summary_markdown(output_root / 'cross_device_recovery_closure_report.md', payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/cross_device_recovery_closure')
    parser.add_argument('--session-id', default='SESSION-CROSS-DEVICE-CLOSURE')
    parser.add_argument('--cycle-count', type=int, default=14)
    parser.add_argument('--checkpoint-interval-cycles', type=int, default=4)
    parser.add_argument('--repeatability-runs', type=int, default=3)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    report = run_cross_device_recovery_closure(
        package_root=package_root,
        output_root=output_root,
        session_id=args.session_id,
        cycle_count=max(1, args.cycle_count),
        checkpoint_interval_cycles=max(1, args.checkpoint_interval_cycles),
        repeatability_runs=max(1, args.repeatability_runs),
    )
    print(
        'cross-device-recovery-closure:'
        f" verdict={report['verdict']}"
        f" adapters={report['activated_adapter_count']}"
        f" tags={report['tag_definition_count']}"
        f" replay_tail={report['replay_report']['tail_record_count']}"
        f" fallback_tail={report['fallback_recovery_report']['replay_tail_count']}"
        f" report_dir={report['report_dir']}"
    )
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
