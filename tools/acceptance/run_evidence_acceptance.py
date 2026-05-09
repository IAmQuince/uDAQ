from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__ in {None, ''}:
    _REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))


_FALLBACK_MIN_TAIL = 16
_FALLBACK_MIN_RECORD_TYPES = 3
_MIN_VALID_CHECKPOINTS = 4
_MIN_PERSISTED_RECORDS = 100
_MIN_SEGMENTS = 20


def _prepare_import_path(package_root: Path) -> None:
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _status_ok(status: str) -> bool:
    return status in {'PASS', 'SKIP'}


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    review = payload['populated_review_report']
    history = review['history_tier_summary']
    replay = review['replay_report']
    checkpoint_summary = review['checkpoint_summary']
    depth = review['session_depth_summary']
    characterization = review['characterization_summary']
    repeatability = payload['repeatability_report']
    fallback = payload['fault_injection_report']
    hardware = payload['real_hardware_bridge_report']
    lines = [
        '# UniversalDAQ Acceptance Report',
        '',
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- verdict: {payload['verdict']}",
        f"- report_dir: {payload['report_dir']}",
        '',
        '## Checks',
        '',
    ]
    for check in payload['checks']:
        lines.append(f"- [{check['status']}] {check['name']} — {check['message']}")
    lines.extend([
        '',
        '## Shell smoke output',
        '',
        '```text',
        payload['shell_smoke_output'],
        '```',
        '',
        '## Long-run populated review summary',
        '',
        f"- session_id: {review['session_id']}",
        f"- hot_recent_sample_count: {history['hot']['recent_sample_count']}",
        f"- warm_variable_row_count: {history['warm']['variable_row_count']}",
        f"- warm_cycle_row_count: {history['warm']['cycle_row_count']}",
        f"- warm_runtime_event_count: {history['warm']['runtime_event_count']}",
        f"- cold_segment_count: {history['cold']['segment_count']}",
        f"- cold_persisted_record_count: {history['cold']['persisted_record_count']}",
        f"- checkpoint_count: {checkpoint_summary['valid_checkpoint_count']}",
        f"- checkpoint_sequence_ids: {depth['checkpoint_sequence_ids']}",
        '',
        '## Replay summary',
        '',
        f"- checkpoint_id: {replay.get('checkpoint_id')}",
        f"- tail_record_count: {replay['tail_record_count']}",
        f"- tail_record_type_count: {replay['tail_record_type_count']}",
        f"- tail_contains_multiple_record_types: {replay['tail_contains_multiple_record_types']}",
        f"- replay_state_hash: {replay['replay_state_hash']}",
        '',
        '## Long-run characterization',
        '',
        f"- average_records_per_segment: {characterization['average_records_per_segment']}",
        f"- checkpoint_density_per_cycle: {characterization['checkpoint_density_per_cycle']}",
        f"- bounded_run_window_ticks: {characterization['bounded_run_window_ticks']}",
        f"- runtime_event_diversity: {characterization['runtime_event_diversity']}",
        '',
        '## Session artifact summary',
        '',
        f"- session_root: {payload['session_artifact_report']['session_root']}",
        f"- entry_count: {payload['session_artifact_report']['entry_count']}",
        f"- checkpoint_count: {len(payload['session_artifact_report']['checkpoint_rows'])}",
        f"- segment_count: {len(payload['session_artifact_report']['segment_rows'])}",
        '',
        '## Repeatability gate',
        '',
        f"- verdict: {repeatability['verdict']}",
        f"- run_count: {repeatability['run_count']}",
        f"- consistent_depth_metrics: {repeatability['consistent_depth_metrics']}",
        f"- consistent_replay_metrics: {repeatability['consistent_replay_metrics']}",
        f"- minimum_valid_checkpoint_count: {repeatability['minimum_valid_checkpoint_count']}",
        '',
        '## Fallback recovery summary',
        '',
        f"- corrupted_checkpoint_id: {fallback['corrupted_checkpoint_id']}",
        f"- recovered_checkpoint_id: {fallback['recovered_checkpoint_id']}",
        f"- fallback_candidate_count: {fallback['fallback_candidate_count']}",
        f"- replay_tail_count: {fallback['replay_tail_count']}",
        f"- replay_tail_record_type_count: {fallback['replay_tail_record_type_count']}",
        f"- replay_tail_contains_multiple_record_types: {fallback['replay_tail_contains_multiple_record_types']}",
        f"- state_hash_matches: {fallback['state_hash_matches']}",
        '',
        '## Real-hardware specimen bridge',
        '',
        f"- verdict: {hardware['verdict']}",
        f"- mode: {hardware['mode']}",
        f"- reason: {hardware.get('reason', '')}",
        f"- driver_name: {hardware.get('driver_name')}",
        f"- resolved_serial_number: {hardware.get('resolved_serial_number')}",
    ])
    if hardware['verdict'] == 'PASS':
        lines.extend(
            [
                f"- bridge_recent_sample_count: {hardware['history_tier_summary']['hot']['recent_sample_count']}",
                f"- bridge_persisted_record_count: {hardware['history_tier_summary']['cold']['persisted_record_count']}",
                f"- bridge_checkpoint_count: {hardware['checkpoint_summary']['valid_checkpoint_count']}",
                f"- bridge_tail_record_count: {hardware['replay_report']['tail_record_count']}",
            ]
        )
    cross_device = payload['cross_device_acquisition_report']
    command_arbitration = payload['cross_device_command_arbitration_report']
    lines.extend([
        '',
        '## Cross-device read-side closure',
        '',
        f"- verdict: {cross_device['verdict']}",
        f"- activated_adapter_count: {cross_device['activated_adapter_count']}",
        f"- tag_definition_count: {cross_device['tag_definition_count']}",
        f"- latest_sample_count: {cross_device['latest_sample_count']}",
    ])
    for adapter_id, count in cross_device.get('tag_counts_by_adapter', {}).items():
        lines.append(f'- {adapter_id}: {count}')
    lines.extend([
        '',
        '## Cross-device command and arbitration',
        '',
        f"- verdict: {command_arbitration['verdict']}",
        f"- writable_tag_count: {command_arbitration['writable_tag_count']}",
        f"- command_attempt_count: {command_arbitration['command_summary']['command_attempt_count']}",
        f"- accepted_count: {command_arbitration['command_summary']['accepted_count']}",
        f"- rejected_count: {command_arbitration['command_summary']['rejected_count']}",
        f"- ownership_conflict_count: {command_arbitration['command_summary']['ownership_conflict_count']}",
        f"- degraded_transition_count: {command_arbitration['degraded_report']['degraded_transition_count']}",
        f"- replay_tail_count: {command_arbitration['replay_report']['tail_record_count']}",
    ])
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')



def run_acceptance(
    *,
    package_root: Path,
    output_root: Path,
    include_real_hardware_bridge: bool = True,
    real_hardware_required: bool = False,
    include_cross_device_acquisition: bool = True,
    include_cross_device_command_arbitration: bool = True,
) -> dict[str, object]:
    _prepare_import_path(package_root)

    from tools.acceptance.build_populated_review_session import build_populated_review_session
    from tools.acceptance.run_fault_injection import simulate_corrupted_latest_checkpoint
    from tools.acceptance.run_real_hardware_specimen_bridge import run_real_hardware_specimen_bridge
    from tools.acceptance.run_cross_device_recovery_closure import run_cross_device_recovery_closure
    from tools.acceptance.run_cross_device_command_arbitration import run_cross_device_command_arbitration
    from tools.acceptance.run_repeatability_gate import run_repeatability_gate
    from tools.acceptance.verify_session_artifacts import verify_session_artifacts

    report_stamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    report_dir = output_root / report_stamp
    report_dir.mkdir(parents=True, exist_ok=True)

    shell_smoke = subprocess.run(
        [sys.executable, '-m', 'tools.dev.run_shell_smoke', '--package-root', str(package_root)],
        cwd=package_root,
        capture_output=True,
        text=True,
    )
    shell_smoke_output = (shell_smoke.stdout + shell_smoke.stderr).strip()

    populated_review_report = build_populated_review_session(
        package_root=package_root,
        output_root=report_dir / 'reviewability',
        session_id='SESSION-POPULATED-REVIEW',
        cycle_count=18,
        checkpoint_interval_cycles=4,
        start_tick=30,
    )
    session_root = Path(populated_review_report['session_root'])
    session_artifact_report = verify_session_artifacts(session_root)
    repeatability_report = run_repeatability_gate(package_root=package_root, output_root=report_dir / 'repeatability', run_count=3)
    fault_injection_report = simulate_corrupted_latest_checkpoint(package_root=package_root, output_root=report_dir / 'fault_injection')
    if include_real_hardware_bridge:
        real_hardware_bridge_report = run_real_hardware_specimen_bridge(
            package_root=package_root,
            output_root=report_dir / 'real_hardware_bridge',
            require_hardware=real_hardware_required,
        )
    else:
        real_hardware_bridge_report = {
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'verdict': 'SKIP',
            'mode': 'disabled',
            'reason': 'real hardware bridge disabled for this acceptance run',
            'report_dir': str(report_dir / 'real_hardware_bridge'),
            'driver_available': None,
            'driver_name': None,
            'requested_serial_number': None,
            'resolved_serial_number': None,
            'active_adapter_id': None,
            'session_id': 'SESSION-REAL-HARDWARE-BRIDGE',
            'probe_result': None,
        }
    if include_cross_device_acquisition:
        cross_device_acquisition_report = run_cross_device_recovery_closure(
            package_root=package_root,
            output_root=report_dir / 'cross_device_acquisition',
        )
    else:
        cross_device_acquisition_report = {
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'verdict': 'SKIP',
            'session_id': 'SESSION-CROSS-DEVICE-SPINE',
            'report_dir': str(report_dir / 'cross_device_acquisition'),
            'activated_adapter_count': 0,
            'tag_definition_count': 0,
            'latest_sample_count': 0,
            'tag_counts_by_adapter': {},
            'tag_counts_by_value_type': {},
            'history_index_report': {'sample_counts_by_point': {}, 'variable_ids': []},
            'checks': (),
        }

    if include_cross_device_command_arbitration:
        cross_device_command_arbitration_report = run_cross_device_command_arbitration(
            package_root=package_root,
            output_root=report_dir / 'cross_device_command_arbitration',
        )
    else:
        cross_device_command_arbitration_report = {
            'generated_at_utc': datetime.now(timezone.utc).isoformat(),
            'verdict': 'SKIP',
            'session_id': 'SESSION-CROSS-DEVICE-COMMANDS',
            'report_dir': str(report_dir / 'cross_device_command_arbitration'),
            'activated_adapter_count': 0,
            'writable_tag_count': 0,
            'command_summary': {'command_attempt_count': 0, 'accepted_count': 0, 'rejected_count': 0, 'ownership_conflict_count': 0},
            'degraded_report': {'degraded_transition_count': 0, 'simultaneous_drop_event_count': 0},
            'history_index_report': {'sample_counts_by_point': {}, 'variable_ids': []},
            'checks': (),
            'replay_report': {'tail_record_count': 0, 'tail_contains_multiple_record_types': False},
        }

    replay_report = populated_review_report['replay_report']
    history_summary = populated_review_report['history_tier_summary']
    review_index = populated_review_report['history_index_report']
    checkpoint_summary = populated_review_report['checkpoint_summary']
    characterization = populated_review_report['characterization_summary']

    checks = [
        {
            'name': 'shell_smoke_entry',
            'status': 'PASS' if shell_smoke.returncode == 0 and 'shell-smoke:' in shell_smoke_output else 'FAIL',
            'message': shell_smoke_output or 'shell smoke produced no output',
        },
        {
            'name': 'session_artifact_report',
            'status': session_artifact_report['verdict'],
            'message': f"entries={session_artifact_report['entry_count']} segments={len(session_artifact_report['segment_rows'])}",
        },
        {
            'name': 'populated_history_counts',
            'status': 'PASS' if history_summary['hot']['recent_sample_count'] > 0 and history_summary['warm']['variable_row_count'] > 0 and history_summary['warm']['cycle_row_count'] > 0 else 'FAIL',
            'message': json.dumps(history_summary, sort_keys=True),
        },
        {
            'name': 'review_index_queryable',
            'status': 'PASS' if bool(review_index['sample_counts_by_point']) and bool(review_index['variable_ids']) else 'FAIL',
            'message': json.dumps({'sample_points': review_index['sample_counts_by_point'], 'variable_ids': review_index['variable_ids']}, sort_keys=True),
        },
        {
            'name': 'deterministic_replay_hash',
            'status': 'PASS' if replay_report['deterministic_replay'] and replay_report['tail_record_count'] >= 0 else 'FAIL',
            'message': f"hash={replay_report['replay_state_hash']} tail={replay_report['tail_record_count']}",
        },
        {
            'name': 'nonzero_tail_replay',
            'status': 'PASS' if replay_report['tail_record_count'] > 0 else 'FAIL',
            'message': f"tail={replay_report['tail_record_count']} checkpoint={replay_report.get('checkpoint_id')}",
        },
        {
            'name': 'multi_type_tail_replay',
            'status': 'PASS' if replay_report['tail_contains_multiple_record_types'] else 'FAIL',
            'message': json.dumps(replay_report['tail_record_counts_by_type'], sort_keys=True),
        },
        {
            'name': 'checkpoint_ladder_depth',
            'status': 'PASS' if checkpoint_summary['valid_checkpoint_count'] >= _MIN_VALID_CHECKPOINTS else 'FAIL',
            'message': json.dumps({'count': checkpoint_summary['valid_checkpoint_count'], 'spacing': checkpoint_summary['checkpoint_spacing']}, sort_keys=True),
        },
        {
            'name': 'longrun_history_depth',
            'status': 'PASS' if history_summary['cold']['persisted_record_count'] >= _MIN_PERSISTED_RECORDS and history_summary['cold']['segment_count'] >= _MIN_SEGMENTS else 'FAIL',
            'message': json.dumps({'records': history_summary['cold']['persisted_record_count'], 'segments': history_summary['cold']['segment_count']}, sort_keys=True),
        },
        {
            'name': 'repeatability_gate',
            'status': repeatability_report['verdict'],
            'message': json.dumps({'run_count': repeatability_report['run_count'], 'consistent_depth_metrics': repeatability_report['consistent_depth_metrics'], 'consistent_replay_metrics': repeatability_report['consistent_replay_metrics']}, sort_keys=True),
        },
        {
            'name': 'fault_injection_fallback',
            'status': fault_injection_report['verdict'],
            'message': f"recovered_checkpoint_id={fault_injection_report['recovered_checkpoint_id']}",
        },
        {
            'name': 'fallback_nonzero_tail_replay',
            'status': 'PASS' if fault_injection_report['replay_tail_count'] >= _FALLBACK_MIN_TAIL else 'FAIL',
            'message': f"tail={fault_injection_report['replay_tail_count']} min={_FALLBACK_MIN_TAIL}",
        },
        {
            'name': 'fallback_multi_type_tail_replay',
            'status': 'PASS' if fault_injection_report['replay_tail_record_type_count'] >= _FALLBACK_MIN_RECORD_TYPES and fault_injection_report['replay_tail_contains_multiple_record_types'] else 'FAIL',
            'message': json.dumps(fault_injection_report['replay_tail_counts_by_type'], sort_keys=True),
        },
        {
            'name': 'fallback_recovery_state_hash',
            'status': 'PASS' if fault_injection_report['state_hash_matches'] else 'FAIL',
            'message': f"state_hash_matches={fault_injection_report['state_hash_matches']}",
        },
        {
            'name': 'recovery_review_artifacts_present',
            'status': 'PASS' if all((report_dir / 'fault_injection' / name).exists() for name in ('fallback_recovery_detail.json', 'fallback_recovery_detail.md', 'session_timeline.json', 'session_timeline.md')) else 'FAIL',
            'message': str(report_dir / 'fault_injection'),
        },
        {
            'name': 'review_summary_artifacts_present',
            'status': 'PASS' if all((report_dir / 'reviewability' / name).exists() for name in ('review_summary.json', 'review_summary.md', 'replay_detail.json', 'replay_detail.md', 'checkpoint_ladder.json', 'checkpoint_ladder.md', 'session_timeline.json', 'session_timeline.md', 'longrun_characterization.json', 'longrun_characterization.md')) else 'FAIL',
            'message': str(report_dir / 'reviewability'),
        },
        {
            'name': 'repeatability_artifacts_present',
            'status': 'PASS' if all((report_dir / 'repeatability' / name).exists() for name in ('repeatability_report.json', 'repeatability_report.md')) else 'FAIL',
            'message': str(report_dir / 'repeatability'),
        },
        {
            'name': 'longrun_characterization_thresholds',
            'status': 'PASS' if characterization['meets_min_checkpoint_depth'] and characterization['meets_min_segment_depth'] and characterization['meets_min_record_depth'] else 'FAIL',
            'message': json.dumps(characterization, sort_keys=True),
        },
        {
            'name': 'real_hardware_bridge_status',
            'status': real_hardware_bridge_report['verdict'],
            'message': json.dumps({'mode': real_hardware_bridge_report['mode'], 'reason': real_hardware_bridge_report.get('reason'), 'driver_name': real_hardware_bridge_report.get('driver_name')}, sort_keys=True),
        },
        {
            'name': 'real_hardware_bridge_artifacts_present',
            'status': 'PASS' if all((report_dir / 'real_hardware_bridge' / name).exists() for name in ('real_hardware_bridge_report.json', 'real_hardware_bridge_report.md')) else 'FAIL',
            'message': str(report_dir / 'real_hardware_bridge'),
        },
        {
            'name': 'real_hardware_bridge_review_artifacts_present',
            'status': 'PASS' if real_hardware_bridge_report['verdict'] != 'PASS' or all((report_dir / 'real_hardware_bridge' / name).exists() for name in ('review_summary.json', 'review_summary.md')) else 'FAIL',
            'message': str(report_dir / 'real_hardware_bridge'),
        },
        {
            'name': 'real_hardware_bridge_queryable',
            'status': 'SKIP' if real_hardware_bridge_report['verdict'] != 'PASS' else ('PASS' if bool(real_hardware_bridge_report['history_index_report']['sample_counts_by_point']) else 'FAIL'),
            'message': 'hardware bridge skipped' if real_hardware_bridge_report['verdict'] != 'PASS' else json.dumps(real_hardware_bridge_report['history_index_report']['sample_counts_by_point'], sort_keys=True),
        },
        {
            'name': 'cross_device_acquisition_status',
            'status': cross_device_acquisition_report['verdict'],
            'message': json.dumps({'activated_adapter_count': cross_device_acquisition_report['activated_adapter_count'], 'tag_definition_count': cross_device_acquisition_report['tag_definition_count']}, sort_keys=True),
        },
        {
            'name': 'cross_device_artifacts_present',
            'status': 'PASS' if all((report_dir / 'cross_device_acquisition' / name).exists() for name in ('cross_device_recovery_closure_report.json', 'cross_device_recovery_closure_report.md', 'tag_inventory.json', 'tag_inventory.md', 'review_summary.json', 'degraded_adapter_timeline.json', 'degraded_adapter_timeline.md', 'fallback_recovery_detail.json', 'fallback_recovery_detail.md')) else 'FAIL',
            'message': str(report_dir / 'cross_device_acquisition'),
        },
        {
            'name': 'cross_device_queryable',
            'status': 'PASS' if len(cross_device_acquisition_report['history_index_report']['sample_counts_by_point']) >= 6 and len(cross_device_acquisition_report['history_index_report']['variable_ids']) >= 3 else 'FAIL',
            'message': json.dumps({'sample_points': cross_device_acquisition_report['history_index_report']['sample_counts_by_point'], 'variable_ids': cross_device_acquisition_report['history_index_report']['variable_ids']}, sort_keys=True),
        },
        {
            'name': 'cross_device_nontrivial_replay',
            'status': 'PASS' if cross_device_acquisition_report['replay_report']['tail_record_count'] >= 8 else 'FAIL',
            'message': json.dumps({'tail_record_count': cross_device_acquisition_report['replay_report']['tail_record_count'], 'tail_record_counts_by_type': cross_device_acquisition_report['replay_report']['tail_record_counts_by_type']}, sort_keys=True),
        },
        {
            'name': 'cross_device_fallback_recovery',
            'status': cross_device_acquisition_report['fallback_recovery_report']['verdict'],
            'message': json.dumps({'replay_tail_count': cross_device_acquisition_report['fallback_recovery_report']['replay_tail_count'], 'replay_tail_counts_by_type': cross_device_acquisition_report['fallback_recovery_report']['replay_tail_counts_by_type']}, sort_keys=True),
        },
        {
            'name': 'cross_device_repeatability',
            'status': cross_device_acquisition_report['repeatability_report']['verdict'],
            'message': json.dumps({'run_count': cross_device_acquisition_report['repeatability_report']['run_count'], 'consistent_depth_metrics': cross_device_acquisition_report['repeatability_report']['consistent_depth_metrics'], 'consistent_replay_metrics': cross_device_acquisition_report['repeatability_report']['consistent_replay_metrics']}, sort_keys=True),
        },
        {
            'name': 'cross_device_degraded_conditions',
            'status': 'PASS' if cross_device_acquisition_report['degraded_conditions_report']['degraded_transition_count'] >= 4 else 'FAIL',
            'message': json.dumps({'degraded_transition_count': cross_device_acquisition_report['degraded_conditions_report']['degraded_transition_count'], 'simultaneous_drop_event_count': cross_device_acquisition_report['degraded_conditions_report']['simultaneous_drop_event_count']}, sort_keys=True),
        },
        {
            'name': 'cross_device_command_arbitration_status',
            'status': cross_device_command_arbitration_report['verdict'],
            'message': json.dumps({'writable_tag_count': cross_device_command_arbitration_report['writable_tag_count'], 'command_attempt_count': cross_device_command_arbitration_report['command_summary']['command_attempt_count']}, sort_keys=True),
        },
        {
            'name': 'cross_device_command_artifacts_present',
            'status': 'PASS' if all((report_dir / 'cross_device_command_arbitration' / name).exists() for name in ('cross_device_command_arbitration_report.json', 'cross_device_command_arbitration_report.md', 'writable_tag_inventory.json', 'writable_tag_inventory.md', 'command_timeline.json', 'command_timeline.md', 'ownership_ledger.json', 'ownership_ledger.md', 'review_summary.json')) else 'FAIL',
            'message': str(report_dir / 'cross_device_command_arbitration'),
        },
        {
            'name': 'cross_device_command_arbitration_conflicts',
            'status': 'PASS' if cross_device_command_arbitration_report['command_summary']['ownership_conflict_count'] >= 1 else 'FAIL',
            'message': json.dumps({'ownership_conflict_count': cross_device_command_arbitration_report['command_summary']['ownership_conflict_count']}, sort_keys=True),
        },
        {
            'name': 'cross_device_command_degraded_behavior',
            'status': 'PASS' if cross_device_command_arbitration_report['degraded_report']['degraded_transition_count'] >= 4 and cross_device_command_arbitration_report['degraded_report']['simultaneous_drop_event_count'] >= 1 else 'FAIL',
            'message': json.dumps(cross_device_command_arbitration_report['degraded_report'], sort_keys=True),
        },
        {
            'name': 'cross_device_command_replay_tail',
            'status': 'PASS' if cross_device_command_arbitration_report['replay_report']['tail_record_count'] >= 4 and cross_device_command_arbitration_report['replay_report']['tail_contains_multiple_record_types'] else 'FAIL',
            'message': json.dumps({'tail_record_count': cross_device_command_arbitration_report['replay_report']['tail_record_count'], 'tail_record_counts_by_type': cross_device_command_arbitration_report['replay_report'].get('tail_record_counts_by_type', {})}, sort_keys=True),
        },
    ]
    verdict = 'PASS' if all(_status_ok(str(check['status'])) for check in checks) else 'FAIL'
    payload = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(),
        'verdict': verdict,
        'report_dir': str(report_dir),
        'shell_smoke_output': shell_smoke_output,
        'checks': checks,
        'populated_review_report': populated_review_report,
        'session_artifact_report': session_artifact_report,
        'repeatability_report': repeatability_report,
        'fault_injection_report': fault_injection_report,
        'real_hardware_bridge_report': real_hardware_bridge_report,
        'cross_device_acquisition_report': cross_device_acquisition_report,
        'cross_device_command_arbitration_report': cross_device_command_arbitration_report,
    }
    _write_json(report_dir / 'acceptance_report.json', payload)
    _write_markdown(report_dir / 'acceptance_report.md', payload)
    return payload



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/acceptance')
    parser.add_argument('--skip-real-hardware-bridge', action='store_true')
    parser.add_argument('--real-hardware-required', action='store_true')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    report = run_acceptance(
        package_root=package_root,
        output_root=output_root,
        include_real_hardware_bridge=not args.skip_real_hardware_bridge,
        real_hardware_required=args.real_hardware_required,
    )
    print(f"evidence-acceptance: verdict={report['verdict']} report_dir={report['report_dir']}")
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
