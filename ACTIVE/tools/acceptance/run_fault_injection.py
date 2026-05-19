from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


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



def _generated_profile(*, start_tick: int, cycle_count: int) -> list[tuple[int, dict[str, tuple[str, str, str]]]]:
    profile: list[tuple[int, dict[str, tuple[str, str, str]]]] = []
    pressure = 1.0
    temperature = 20.0
    for offset in range(cycle_count):
        tick = start_tick + offset
        pressure += 0.27 + (0.03 if offset % 4 == 0 else 0.0)
        temperature += 0.24 + (0.02 if offset % 5 == 0 else 0.0)
        profile.append(
            (
                tick,
                {
                    'PT-101': (f'{pressure:.1f}', f'{pressure:.1f}', 'psi'),
                    'TT-101': (f'{temperature:.1f}', f'{temperature:.1f}', 'C'),
                },
            )
        )
    return profile



def _populate_fault_runtime(runtime, *, start_tick: int, cycle_count: int, checkpoint_offsets: set[int]) -> None:
    from universaldaq.adapters import SimulatedReadAdapter
    from universaldaq.common import SignalQuality, VariableId, as_event_time
    from universaldaq.signals import VariableEvaluationResult, VariableSnapshot, VariableState
    from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary

    profile = _generated_profile(start_tick=start_tick, cycle_count=cycle_count)
    previous_variable_snapshots: dict[VariableId, VariableSnapshot] = {}
    for offset, (tick, values) in enumerate(profile, start=1):
        adapter = SimulatedReadAdapter.from_values(adapter_id='SIM-HIST-FAULT', values=values, timestamp=tick)
        poll_result = adapter.poll(timestamp=tick)
        ts = as_event_time(tick)
        runtime.capture_acquisition(adapter_id='SIM-HIST-FAULT', timestamp=ts, poll_result=poll_result)
        runtime.record_state_event(timestamp=ts, event_type='operator_note', attributes={'message': f'fault-cycle-{tick}'})
        runtime.record_state_event(
            timestamp=ts,
            event_type='mode_transition',
            attributes={'mode': 'recovery-test', 'cycle': tick, 'window': 'fault-injection-v3'},
        )
        runtime.record_state_event(
            timestamp=ts,
            event_type='quality_transition',
            attributes={'quality': 'good', 'cycle': tick, 'window': 'fault-injection-v3'},
        )
        if offset in checkpoint_offsets:
            runtime.record_state_event(
                timestamp=ts,
                event_type='checkpoint_boundary',
                attributes={'boundary': 'fault-window', 'cycle': tick, 'offset': offset},
            )
        pressure = values['PT-101'][1]
        temperature = values['TT-101'][1]
        variable_results = (
            VariableEvaluationResult(
                snapshot=VariableSnapshot(
                    variable_id=VariableId('VAR-PT-AVG'),
                    value=pressure,
                    quality=SignalQuality.GOOD,
                    state=VariableState.HEALTHY,
                    timestamp=ts,
                    dependency_values={'PT-101': pressure},
                ),
                resolved_dependencies={'PT-101': pressure},
            ),
            VariableEvaluationResult(
                snapshot=VariableSnapshot(
                    variable_id=VariableId('VAR-TT-MEAN'),
                    value=temperature,
                    quality=SignalQuality.GOOD,
                    state=VariableState.HEALTHY,
                    timestamp=ts,
                    dependency_values={'TT-101': temperature},
                ),
                resolved_dependencies={'TT-101': temperature},
            ),
        )
        runtime.record_variable_results(timestamp=ts, results=variable_results, previous_snapshots=previous_variable_snapshots)
        previous_variable_snapshots = {result.snapshot.variable_id: result.snapshot for result in variable_results}
        runtime.record_processed_cycle(
            timestamp=ts,
            lifecycle_summary=DeviceLifecycleSummary(
                phase='live',
                detected_device_count=1,
                active_device_key='SIM-FAULT-DEVICE-001',
                active_adapter_id='SIM-HIST-FAULT',
                projected_point_count=2,
                published_signal_count=2,
                last_poll_snapshot_count=len(poll_result.snapshots),
                disconnected_signal_count=0,
                last_transition='poll_active_adapter',
                needs_review=False,
            ),
            variable_summary=VariableHealthSummary(total_variable_count=2, healthy_count=2),
            changed_signal_ids=('PT-101', 'TT-101'),
            poll_result=poll_result,
        )
    tail_tick = start_tick + cycle_count
    runtime.record_state_event(
        timestamp=as_event_time(tail_tick),
        event_type='operator_note',
        attributes={'message': 'post-corruption-tail-window-v3'},
    )
    runtime.flush_journal(now=as_event_time(tail_tick))



def _write_fallback_recovery_artifacts(output_root: Path, report: dict[str, object]) -> None:
    _write_json(output_root / 'fallback_recovery_detail.json', report)
    lines = [
        '# UniversalDAQ Fallback Recovery Detail',
        '',
        f"- verdict: {report['verdict']}",
        f"- corrupted_checkpoint_id: {report['corrupted_checkpoint_id']}",
        f"- recovered_checkpoint_id: {report['recovered_checkpoint_id']}",
        f"- recovered_last_committed_sequence_id: {report['recovered_last_committed_sequence_id']}",
        f"- fallback_candidate_count: {report['fallback_candidate_count']}",
        f"- replay_tail_count: {report['replay_tail_count']}",
        f"- replay_tail_record_type_count: {report['replay_tail_record_type_count']}",
        f"- replay_tail_contains_multiple_record_types: {report['replay_tail_contains_multiple_record_types']}",
        f"- state_hash_matches: {report['state_hash_matches']}",
        '',
        '## Tail counts by type',
        '',
    ]
    for record_type, count in report['replay_tail_counts_by_type'].items():
        lines.append(f'- {record_type}: {count}')
    _write_markdown(output_root / 'fallback_recovery_detail.md', lines)

    timeline = {
        'corrupted_checkpoint_id': report['corrupted_checkpoint_id'],
        'recovered_checkpoint_id': report['recovered_checkpoint_id'],
        'checkpoint_sequence_ids': report['checkpoint_sequence_ids'],
        'segment_ranges': report['segment_ranges'],
        'replay_tail_first_sequence_id': report['replay_tail_first_sequence_id'],
        'replay_tail_last_sequence_id': report['replay_tail_last_sequence_id'],
        'fallback_candidate_count': report['fallback_candidate_count'],
    }
    _write_json(output_root / 'session_timeline.json', timeline)
    lines = [
        '# UniversalDAQ Fault Injection Session Timeline',
        '',
        f"- corrupted_checkpoint_id: {timeline['corrupted_checkpoint_id']}",
        f"- recovered_checkpoint_id: {timeline['recovered_checkpoint_id']}",
        f"- checkpoint_sequence_ids: {timeline['checkpoint_sequence_ids']}",
        f"- replay_tail_first_sequence_id: {timeline['replay_tail_first_sequence_id']}",
        f"- replay_tail_last_sequence_id: {timeline['replay_tail_last_sequence_id']}",
        f"- fallback_candidate_count: {timeline['fallback_candidate_count']}",
        '',
        '## Segment ranges',
        '',
    ]
    for row in timeline['segment_ranges']:
        lines.append(
            f"- {row['segment_id']}: {row['first_sequence_id']} -> {row['last_sequence_id']} ({row['record_count']} records)"
        )
    _write_markdown(output_root / 'session_timeline.md', lines)



def simulate_corrupted_latest_checkpoint(*, package_root: Path, output_root: Path | None = None) -> dict[str, object]:
    _prepare_import_path(package_root)

    from universaldaq.runtime import RuntimeQualityService

    target_root = (output_root or package_root / 'proof' / 'acceptance' / 'fault_injection').resolve()
    target_root.mkdir(parents=True, exist_ok=True)
    runtime_root = target_root / 'runtime'
    runtime = RuntimeQualityService(
        journal_file_path=runtime_root / 'session.jsonl',
        journal_max_segment_records=4,
        point_history_limit=160,
        event_history_limit=192,
        cycle_history_limit=192,
        variable_history_limit=192,
        presentation_interval_ticks=1,
        session_id='SESSION-FAULT-INJECTION',
        auto_checkpoint_interval_cycles=4,
    )
    _populate_fault_runtime(runtime, start_tick=100, cycle_count=16, checkpoint_offsets={4, 8, 12, 16})

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
    recovery_bundle = runtime.build_recovery_bundle(limit=1024)
    replay_report = recovery_bundle['replay_report']
    valid_checkpoint_rows = [row for row in runtime.checkpoint_rows() if bool(row.get('hash_valid'))]
    recovered_rank = None
    if recovered_checkpoint is not None:
        recovered_ids = [str(row['checkpoint_id']) for row in valid_checkpoint_rows]
        if recovered_checkpoint.checkpoint_id in recovered_ids:
            recovered_rank = recovered_ids.index(recovered_checkpoint.checkpoint_id) + 1
    report = {
        'verdict': 'PASS' if recovered_checkpoint is not None else 'FAIL',
        'latest_checkpoint_corrupted': True,
        'corrupted_checkpoint_id': corrupted_checkpoint_id,
        'recovered_checkpoint_id': None if recovered_checkpoint is None else recovered_checkpoint.checkpoint_id,
        'recovered_last_committed_sequence_id': None if recovered_checkpoint is None else recovered_checkpoint.last_committed_sequence_id,
        'fallback_candidate_count': len(valid_checkpoint_rows),
        'recovered_checkpoint_rank': recovered_rank,
        'replay_tail_count': len(recovery_bundle.get('journal_tail', ())),
        'replay_tail_counts_by_type': dict(replay_report.get('tail_record_counts_by_type', {})),
        'replay_tail_record_type_count': int(replay_report.get('tail_record_type_count', 0) or 0),
        'replay_tail_contains_multiple_record_types': bool(replay_report.get('tail_contains_multiple_record_types', False)),
        'replay_tail_first_sequence_id': replay_report.get('tail_first_sequence_id'),
        'replay_tail_last_sequence_id': replay_report.get('tail_last_sequence_id'),
        'state_hash_matches': bool(recovery_bundle.get('state_hash_matches', False)),
        'reconstructed_state_hash': recovery_bundle.get('reconstructed_state_hash'),
        'session_root': str(runtime_root / 'sessions' / 'SESSION-FAULT-INJECTION'),
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
    _write_fallback_recovery_artifacts(target_root, report)
    return report



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root')
    parser.add_argument('--json-output')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = None if args.output_root is None else Path(args.output_root).resolve()
    report = simulate_corrupted_latest_checkpoint(package_root=package_root, output_root=output_root)
    if args.json_output:
        output_path = Path(args.json_output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(
        f"fault-injection: verdict={report['verdict']} recovered_checkpoint_id={report['recovered_checkpoint_id']} tail={report['replay_tail_count']} types={report['replay_tail_record_type_count']} candidates={report['fallback_candidate_count']}"
    )
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
