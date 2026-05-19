from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

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


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        '# UniversalDAQ Cross-Device Tag and Acquisition Spine',
        '',
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- verdict: {payload['verdict']}",
        f"- session_id: {payload['session_id']}",
        f"- report_dir: {payload['report_dir']}",
        f"- activated_adapter_count: {payload['activated_adapter_count']}",
        f"- tag_definition_count: {payload['tag_definition_count']}",
        f"- latest_sample_count: {payload['latest_sample_count']}",
        '',
        '## Adapter sample counts',
        '',
    ]
    for adapter_id, count in payload['tag_counts_by_adapter'].items():
        lines.append(f'- {adapter_id}: {count}')
    lines.extend(['', '## Mixed-source variable ids', ''])
    for variable_id in payload['history_index_report']['variable_ids']:
        lines.append(f'- {variable_id}')
    lines.extend(['', '## Sample counts by point', ''])
    for point_key, count in payload['history_index_report']['sample_counts_by_point'].items():
        lines.append(f'- {point_key}: {count}')
    lines.extend(['', '## Checks', ''])
    for check in payload['checks']:
        lines.append(f"- [{check['status']}] {check['name']} — {check['message']}")
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


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
    (output_root / 'tag_inventory.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


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


def run_cross_device_acquisition_spine(
    *,
    package_root: Path,
    output_root: Path,
    session_id: str = 'SESSION-CROSS-DEVICE-SPINE',
    cycle_count: int = 6,
    checkpoint_interval_cycles: int = 3,
) -> dict[str, object]:
    _prepare_import_path(package_root)

    from tools.acceptance.run_real_hardware_specimen_bridge import _build_runtime_quality
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
    generated_at_utc = datetime.now(timezone.utc).isoformat()

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

    discovered = services.adapters.discover_devices(timestamp=as_event_time(10))
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
            timestamp=as_event_time(11),
        )
        activated_adapter_ids.append(adapter_id)

    tag_registry = CanonicalTagRegistryService(metrics=services.runtime_metrics)
    broker = MultiAdapterAcquisitionBroker(adapter_manager=services.adapters, tag_registry=tag_registry, metrics=services.runtime_metrics)
    runtime, runtime_root = _build_runtime_quality(
        output_root=output_root,
        session_id=session_id,
        checkpoint_interval_cycles=checkpoint_interval_cycles,
    )
    previous_variable_snapshots: dict[str, object] = {}

    for offset in range(max(1, cycle_count)):
        tick = 200 + offset
        ts = as_event_time(tick)
        batch = broker.poll(adapter_ids=tuple(activated_adapter_ids), timestamp=ts)
        snapshots = []
        for adapter_id in activated_adapter_ids:
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
            event_type='cross_device_poll_cycle',
            attributes={
                'adapter_count': len(batch.adapter_ids),
                'sample_count': len(batch.samples),
                'tag_count': len(tag_registry.latest_samples),
            },
        )
        runtime.record_state_event(
            timestamp=ts,
            event_type='cross_device_health_summary',
            attributes={
                'healthy_adapter_count': len(batch.adapter_ids),
                'runtime_mode': 'mixed_source_read_only',
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
                published_signal_count=len(tag_registry.latest_samples),
                last_poll_snapshot_count=len(snapshots),
                disconnected_signal_count=sum(1 for row in tag_rows if row['quality'] != SignalQuality.SIMULATED.value),
                last_transition='poll_multi_adapter_broker',
                needs_review=False,
            ),
            variable_summary=VariableHealthSummary(total_variable_count=len(variable_results), healthy_count=len(variable_results)),
            changed_signal_ids=tuple(sample.tag_key for sample in batch.samples),
            poll_result=combined_poll_result,
        )
    tail_tick = 200 + max(1, cycle_count)
    runtime.record_state_event(
        timestamp=as_event_time(tail_tick),
        event_type='cross_device_tail_verification',
        attributes={'activated_adapter_count': len(activated_adapter_ids)},
    )
    runtime.flush_journal(now=as_event_time(tail_tick))
    review_summary = runtime.build_review_summary(limit=24)
    review_summary['session_root'] = str(runtime_root / 'sessions' / session_id)
    artifact_report = verify_session_artifacts(Path(review_summary['session_root']))
    tag_rows = list(tag_registry.latest_sample_rows())
    tag_counts_by_value_type: dict[str, int] = {}
    for definition in tag_registry.definitions.values():
        tag_counts_by_value_type[definition.value_type.value] = tag_counts_by_value_type.get(definition.value_type.value, 0) + 1

    checks = [
        {
            'name': 'activated_adapter_count',
            'status': 'PASS' if len(activated_adapter_ids) >= 3 else 'FAIL',
            'message': f'count={len(activated_adapter_ids)} adapter_ids={activated_adapter_ids}',
        },
        {
            'name': 'nonzero_tag_population_per_adapter',
            'status': 'PASS' if all(count > 0 for count in tag_registry.counts_by_adapter().values()) and len(tag_registry.counts_by_adapter()) >= 3 else 'FAIL',
            'message': json.dumps(tag_registry.counts_by_adapter(), sort_keys=True),
        },
        {
            'name': 'cross_device_variable_population',
            'status': 'PASS' if len(review_summary['history_index_report']['variable_ids']) >= 3 else 'FAIL',
            'message': json.dumps(review_summary['history_index_report']['variable_ids'], sort_keys=True),
        },
        {
            'name': 'mixed_source_review_queryable',
            'status': 'PASS' if len(review_summary['history_index_report']['sample_counts_by_point']) >= 6 else 'FAIL',
            'message': json.dumps(review_summary['history_index_report']['sample_counts_by_point'], sort_keys=True),
        },
        {
            'name': 'artifact_integrity',
            'status': artifact_report['verdict'],
            'message': f"entries={artifact_report['entry_count']} checkpoints={len(artifact_report['checkpoint_rows'])}",
        },
    ]
    verdict = 'PASS' if all(check['status'] == 'PASS' for check in checks) else 'FAIL'
    payload = {
        'generated_at_utc': generated_at_utc,
        'verdict': verdict,
        'session_id': session_id,
        'report_dir': str(output_root),
        'activated_adapter_count': len(activated_adapter_ids),
        'activated_adapter_ids': activated_adapter_ids,
        'tag_definition_count': len(tag_registry.definitions),
        'latest_sample_count': len(tag_registry.latest_samples),
        'tag_rows': tag_rows,
        'tag_counts_by_adapter': tag_registry.counts_by_adapter(),
        'tag_counts_by_value_type': dict(sorted(tag_counts_by_value_type.items())),
        'history_tier_summary': review_summary['history_tier_summary'],
        'history_index_report': review_summary['history_index_report'],
        'checkpoint_summary': review_summary['checkpoint_summary'],
        'replay_report': review_summary['replay_report'],
        'session_artifact_report': artifact_report,
        'checks': checks,
    }
    _write_json(output_root / 'cross_device_acquisition_report.json', payload)
    _write_markdown(output_root / 'cross_device_acquisition_report.md', payload)
    _write_tag_inventory(output_root, payload)
    _write_json(output_root / 'review_summary.json', review_summary)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/cross_device_acquisition')
    parser.add_argument('--session-id', default='SESSION-CROSS-DEVICE-SPINE')
    parser.add_argument('--cycle-count', type=int, default=6)
    parser.add_argument('--checkpoint-interval-cycles', type=int, default=3)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    report = run_cross_device_acquisition_spine(
        package_root=package_root,
        output_root=output_root,
        session_id=args.session_id,
        cycle_count=max(1, args.cycle_count),
        checkpoint_interval_cycles=max(1, args.checkpoint_interval_cycles),
    )
    print(
        'cross-device-acquisition:'
        f" verdict={report['verdict']}"
        f" adapters={report['activated_adapter_count']}"
        f" tags={report['tag_definition_count']}"
        f" report_dir={report['report_dir']}"
    )
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
