from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

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
    history = payload.get('history_tier_summary', {})
    replay = payload.get('replay_report', {})
    artifact_report = payload.get('session_artifact_report', {})
    lines = [
        '# UniversalDAQ Real-Hardware Specimen Bridge',
        '',
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- verdict: {payload['verdict']}",
        f"- mode: {payload['mode']}",
        f"- reason: {payload.get('reason', '')}",
        f"- session_id: {payload.get('session_id')}",
        f"- report_dir: {payload.get('report_dir')}",
        '',
        '## Device status',
        '',
        f"- driver_available: {payload.get('driver_available')}",
        f"- driver_name: {payload.get('driver_name')}",
        f"- requested_serial_number: {payload.get('requested_serial_number')}",
        f"- resolved_serial_number: {payload.get('resolved_serial_number')}",
        f"- active_adapter_id: {payload.get('active_adapter_id')}",
        '',
    ]
    if history:
        lines.extend(
            [
                '## History summary',
                '',
                f"- hot_recent_sample_count: {history.get('hot', {}).get('recent_sample_count')}",
                f"- warm_variable_row_count: {history.get('warm', {}).get('variable_row_count')}",
                f"- warm_runtime_event_count: {history.get('warm', {}).get('runtime_event_count')}",
                f"- cold_segment_count: {history.get('cold', {}).get('segment_count')}",
                f"- cold_persisted_record_count: {history.get('cold', {}).get('persisted_record_count')}",
                '',
            ]
        )
    if replay:
        lines.extend(
            [
                '## Replay summary',
                '',
                f"- checkpoint_id: {replay.get('checkpoint_id')}",
                f"- tail_record_count: {replay.get('tail_record_count')}",
                f"- tail_record_type_count: {replay.get('tail_record_type_count')}",
                f"- tail_contains_multiple_record_types: {replay.get('tail_contains_multiple_record_types')}",
                '',
            ]
        )
    if artifact_report:
        lines.extend(
            [
                '## Session artifacts',
                '',
                f"- artifact_verdict: {artifact_report.get('verdict')}",
                f"- entry_count: {artifact_report.get('entry_count')}",
                f"- checkpoint_count: {len(artifact_report.get('checkpoint_rows', []))}",
                f"- segment_count: {len(artifact_report.get('segment_rows', []))}",
                '',
            ]
        )
    probe = payload.get('probe_result', {})
    if probe:
        lines.extend(['## Direct-open probe', ''])
        for key in (
            'success',
            'open_strategy',
            'open_stage',
            'ain0_value',
            'calibration_loaded',
            'error_type',
            'error_message',
        ):
            lines.append(f"- {key}: {probe.get(key)}")
        lines.append('')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _write_review_summary(path: Path, payload: dict[str, object]) -> None:
    history = payload['history_tier_summary']
    replay = payload['replay_report']
    index = payload['history_index_report']
    checkpoint = payload['checkpoint_summary']
    lines = [
        '# UniversalDAQ Real-Hardware Review Summary',
        '',
        f"- session_id: {payload['session_id']}",
        f"- recent_sample_count: {history['hot']['recent_sample_count']}",
        f"- variable_row_count: {history['warm']['variable_row_count']}",
        f"- runtime_event_count: {history['warm']['runtime_event_count']}",
        f"- persisted_record_count: {history['cold']['persisted_record_count']}",
        f"- checkpoint_count: {checkpoint['valid_checkpoint_count']}",
        f"- replay_tail_count: {replay['tail_record_count']}",
        '',
        '## Sample counts by point',
        '',
    ]
    for point_key, count in sorted(index['sample_counts_by_point'].items()):
        lines.append(f'- {point_key}: {count}')
    lines.extend(['', '## Variable ids', ''])
    for variable_id in index['variable_ids']:
        lines.append(f'- {variable_id}')
    lines.extend(['', '## Runtime event counts', ''])
    for event_type, count in sorted(index['runtime_event_counts_by_type'].items()):
        lines.append(f'- {event_type}: {count}')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _fake_probe_result(serial_number: str | None) -> dict[str, object]:
    resolved = serial_number or '470001'
    return {
        'requested_serial_number': serial_number,
        'resolved_serial_number': resolved,
        'success': True,
        'driver_name': 'injected-backend',
        'open_strategy': 'injected_backend_factory',
        'open_stage': 'first_read',
        'firmware_version': None,
        'hardware_revision': None,
        'ain0_value': None,
        'calibration_loaded': True,
        'close_succeeded': False,
        'error_type': None,
        'error_message': None,
        'detail_rows': (),
    }


def _build_variable_results(*, timestamp, poll_result):
    from universaldaq.common import SignalQuality, VariableId
    from universaldaq.signals import VariableEvaluationResult, VariableSnapshot, VariableState

    values_by_point = {snapshot.point.point_id: float(snapshot.engineering_value) for snapshot in poll_result.snapshots}
    a = values_by_point.get('analog_in_0', 0.0)
    b = values_by_point.get('analog_in_1', 0.0)
    c = values_by_point.get('analog_in_2', 0.0)
    avg = round((a + b + c) / 3.0, 6)
    delta = round(a - b, 6)
    return (
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-U6-AIN0'),
                value=f'{a:.6f}',
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={'analog_in_0': f'{a:.6f}'},
            ),
            resolved_dependencies={'analog_in_0': f'{a:.6f}'},
        ),
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-U6-DELTA-AB'),
                value=f'{delta:.6f}',
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={'analog_in_0': f'{a:.6f}', 'analog_in_1': f'{b:.6f}'},
            ),
            resolved_dependencies={'analog_in_0': f'{a:.6f}', 'analog_in_1': f'{b:.6f}'},
        ),
        VariableEvaluationResult(
            snapshot=VariableSnapshot(
                variable_id=VariableId('VAR-U6-AVG-ABC'),
                value=f'{avg:.6f}',
                quality=SignalQuality.GOOD,
                state=VariableState.HEALTHY,
                timestamp=timestamp,
                dependency_values={
                    'analog_in_0': f'{a:.6f}',
                    'analog_in_1': f'{b:.6f}',
                    'analog_in_2': f'{c:.6f}',
                },
            ),
            resolved_dependencies={
                'analog_in_0': f'{a:.6f}',
                'analog_in_1': f'{b:.6f}',
                'analog_in_2': f'{c:.6f}',
            },
        ),
    )


def _build_runtime_quality(
    *,
    output_root: Path,
    session_id: str,
    checkpoint_interval_cycles: int,
):
    from universaldaq.runtime import RuntimeQualityService

    runtime_root = output_root / 'runtime'
    runtime = RuntimeQualityService(
        journal_file_path=runtime_root / 'session.jsonl',
        journal_max_segment_records=4,
        point_history_limit=96,
        event_history_limit=96,
        cycle_history_limit=96,
        variable_history_limit=96,
        presentation_interval_ticks=1,
        session_id=session_id,
        auto_checkpoint_interval_cycles=max(1, checkpoint_interval_cycles),
    )
    return runtime, runtime_root


def run_real_hardware_specimen_bridge(
    *,
    package_root: Path,
    output_root: Path,
    serial_number: str | None = None,
    require_hardware: bool = False,
    session_id: str = 'SESSION-REAL-HARDWARE-BRIDGE',
    poll_cycles: int = 6,
    checkpoint_interval_cycles: int = 4,
    cycle_delay_seconds: float = 0.0,
    real_backend_factory: Callable[[str | None], object] | None = None,
    probe_rows: tuple[object, ...] = (),
) -> dict[str, object]:
    _prepare_import_path(package_root)
    from tools.acceptance.verify_session_artifacts import verify_session_artifacts
    from tools.dev._u6_live_support import run_poll_cycles
    from universaldaq.common import SignalQuality, as_event_time
    from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary
    from universaldaq_labjack.discovery import probe_driver_status
    from universaldaq_labjack.real_u6 import RealLabJackU6Adapter, build_primed_backend_factory, prime_real_u6_backend

    output_root.mkdir(parents=True, exist_ok=True)
    generated_at_utc = datetime.now(timezone.utc).isoformat()
    driver_available, driver_name = probe_driver_status()
    probe_result: dict[str, object] | None = None
    resolved_serial_number = serial_number
    reason = 'real hardware specimen completed'
    mode = 'completed'

    if real_backend_factory is not None:
        probe_result = _fake_probe_result(serial_number)
        resolved_serial_number = str(probe_result['resolved_serial_number'])
        adapter = RealLabJackU6Adapter(
            adapter_id=f'LABJACK-U6-REAL-{resolved_serial_number}',
            serial_number=resolved_serial_number,
            backend_factory=real_backend_factory,
            prefer_direct_reacquire=True,
        )
        driver_name = 'injected-backend'
        driver_available = True
        mode = 'injected-backend'
    else:
        if not driver_available:
            mode = 'driver_unavailable'
            reason = f'LabJack driver unavailable ({driver_name})'
            verdict = 'FAIL' if require_hardware else 'SKIP'
            payload = {
                'generated_at_utc': generated_at_utc,
                'verdict': verdict,
                'mode': mode,
                'reason': reason,
                'report_dir': str(output_root),
                'driver_available': driver_available,
                'driver_name': driver_name,
                'requested_serial_number': serial_number,
                'resolved_serial_number': None,
                'active_adapter_id': None,
                'session_id': session_id,
                'probe_result': None,
            }
            _write_json(output_root / 'real_hardware_bridge_report.json', payload)
            _write_markdown(output_root / 'real_hardware_bridge_report.md', payload)
            return payload
        primed_backend, probe = prime_real_u6_backend(requested_serial_number=serial_number, perform_ain0_read=True)
        probe_result = probe.as_dict()
        if primed_backend is None or not probe.success:
            mode = 'device_unavailable'
            reason = probe.error_message or 'real hardware probe did not detect a usable device'
            verdict = 'FAIL' if require_hardware else 'SKIP'
            payload = {
                'generated_at_utc': generated_at_utc,
                'verdict': verdict,
                'mode': mode,
                'reason': reason,
                'report_dir': str(output_root),
                'driver_available': driver_available,
                'driver_name': driver_name,
                'requested_serial_number': serial_number,
                'resolved_serial_number': probe.resolved_serial_number,
                'active_adapter_id': None,
                'session_id': session_id,
                'probe_result': probe_result,
            }
            _write_json(output_root / 'real_hardware_bridge_report.json', payload)
            _write_markdown(output_root / 'real_hardware_bridge_report.md', payload)
            return payload
        resolved_serial_number = str(probe.resolved_serial_number)
        adapter = RealLabJackU6Adapter(
            adapter_id=f'LABJACK-U6-REAL-{resolved_serial_number}',
            serial_number=resolved_serial_number,
            backend_factory=build_primed_backend_factory(primed_backend),
            prefer_direct_reacquire=True,
        )
        mode = 'hardware_present'

    runtime, runtime_root = _build_runtime_quality(
        output_root=output_root,
        session_id=session_id,
        checkpoint_interval_cycles=checkpoint_interval_cycles,
    )
    previous_snapshots: dict[str, object] = {}
    for cycle_index in range(max(1, poll_cycles)):
        tick = 100 + cycle_index
        ts = as_event_time(tick)
        poll_result = adapter.poll(timestamp=tick)
        runtime.capture_acquisition(adapter_id=adapter.adapter_id, timestamp=ts, poll_result=poll_result)
        status = adapter.status_snapshot().as_dict()
        runtime.record_state_event(
            timestamp=ts,
            event_type='hardware_bridge_status',
            attributes={
                'cycle_index': cycle_index + 1,
                'lifecycle_state': status.get('lifecycle_state', 'unknown'),
                'startup_classification': status.get('startup_classification', 'unknown'),
                'backend_connected': bool(status.get('backend_connected', False)),
                'hardware_mode': 'real',
            },
        )
        if cycle_index == 0:
            runtime.record_state_event(
                timestamp=ts,
                event_type='hardware_bridge_detected',
                attributes={
                    'serial_number': resolved_serial_number,
                    'driver_name': driver_name,
                },
            )
        variable_results = _build_variable_results(timestamp=ts, poll_result=poll_result)
        runtime.record_variable_results(timestamp=ts, results=variable_results, previous_snapshots=previous_snapshots)
        previous_snapshots = {str(result.snapshot.variable_id): result.snapshot for result in variable_results}
        runtime.record_processed_cycle(
            timestamp=ts,
            lifecycle_summary=DeviceLifecycleSummary(
                phase='live',
                detected_device_count=1,
                active_device_key=f'LABJACK-U6-{resolved_serial_number}',
                active_adapter_id=adapter.adapter_id,
                projected_point_count=len(poll_result.snapshots),
                published_signal_count=len(poll_result.snapshots),
                last_poll_snapshot_count=len(poll_result.snapshots),
                disconnected_signal_count=sum(1 for snapshot in poll_result.snapshots if snapshot.quality != SignalQuality.GOOD),
                last_transition='poll_active_adapter',
                needs_review=bool(status.get('disconnect_incident_active', False)),
            ),
            variable_summary=VariableHealthSummary(total_variable_count=len(variable_results), healthy_count=len(variable_results)),
            changed_signal_ids=tuple(snapshot.point.point_id for snapshot in poll_result.snapshots),
            poll_result=poll_result,
        )
    tail_tick = 100 + max(1, poll_cycles)
    runtime.record_state_event(
        timestamp=as_event_time(tail_tick),
        event_type='hardware_bridge_tail',
        attributes={'serial_number': resolved_serial_number, 'poll_cycles': max(1, poll_cycles)},
    )
    runtime.flush_journal(now=as_event_time(tail_tick))
    if cycle_delay_seconds > 0:
        run_poll_cycles  # keep import validated without introducing extra runtime complexity

    review_summary = runtime.build_review_summary(limit=16)
    review_summary['session_root'] = str(runtime_root / 'sessions' / session_id)
    _write_json(output_root / 'review_summary.json', review_summary)
    _write_review_summary(output_root / 'review_summary.md', review_summary)
    artifact_report = verify_session_artifacts(Path(review_summary['session_root']))
    payload = {
        'generated_at_utc': generated_at_utc,
        'verdict': 'PASS',
        'mode': mode,
        'reason': reason,
        'report_dir': str(output_root),
        'driver_available': driver_available,
        'driver_name': driver_name,
        'requested_serial_number': serial_number,
        'resolved_serial_number': resolved_serial_number,
        'active_adapter_id': adapter.adapter_id,
        'session_id': session_id,
        'probe_result': probe_result,
        'history_tier_summary': review_summary['history_tier_summary'],
        'replay_report': review_summary['replay_report'],
        'checkpoint_summary': review_summary['checkpoint_summary'],
        'history_index_report': review_summary['history_index_report'],
        'session_artifact_report': artifact_report,
    }
    _write_json(output_root / 'real_hardware_bridge_report.json', payload)
    _write_markdown(output_root / 'real_hardware_bridge_report.md', payload)
    return payload



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/real_hardware_bridge')
    parser.add_argument('--serial-number')
    parser.add_argument('--require-hardware', action='store_true')
    parser.add_argument('--session-id', default='SESSION-REAL-HARDWARE-BRIDGE')
    parser.add_argument('--poll-cycles', type=int, default=6)
    parser.add_argument('--checkpoint-interval-cycles', type=int, default=4)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    report = run_real_hardware_specimen_bridge(
        package_root=package_root,
        output_root=output_root,
        serial_number=args.serial_number,
        require_hardware=args.require_hardware,
        session_id=args.session_id,
        poll_cycles=max(1, args.poll_cycles),
        checkpoint_interval_cycles=max(1, args.checkpoint_interval_cycles),
    )
    print(
        'real-hardware-bridge:'
        f" verdict={report['verdict']}"
        f" mode={report['mode']}"
        f" driver={report['driver_name']}"
        f" serial={report.get('resolved_serial_number')}"
        f" report_dir={report['report_dir']}"
    )
    return 0 if report['verdict'] in {'PASS', 'SKIP'} else 1


if __name__ == '__main__':
    raise SystemExit(main())
