from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
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


def _write_markdown(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _write_writable_inventory(output_root: Path, rows: tuple[dict[str, str], ...]) -> None:
    payload = {'rows': list(rows)}
    _write_json(output_root / 'writable_tag_inventory.json', payload)
    lines = ['# UniversalDAQ Cross-Device Writable Tag Inventory', '', '## Writable tags', '']
    for row in rows:
        lines.append(
            f"- {row['output_id']} adapter={row['adapter_id']} point={row['point_id']} policy={row['safe_state_policy']} safe_state={row['safe_state_value']}"
        )
    _write_markdown(output_root / 'writable_tag_inventory.md', lines)


def _write_timeline(output_root: Path, rows: tuple[dict[str, str], ...]) -> None:
    payload = {'rows': list(rows)}
    _write_json(output_root / 'command_timeline.json', payload)
    lines = ['# UniversalDAQ Cross-Device Command Timeline', '', '## Events', '']
    for row in rows:
        lines.append(
            f"- t={row['timestamp']} output={row['output_id']} event={row['event_type']} owner={row['owner']} summary={row['summary']}"
        )
    _write_markdown(output_root / 'command_timeline.md', lines)


def _write_ownership_ledger(output_root: Path, rows: tuple[dict[str, str], ...]) -> None:
    payload = {'rows': list(rows)}
    _write_json(output_root / 'ownership_ledger.json', payload)
    lines = ['# UniversalDAQ Cross-Device Ownership Ledger', '', '## Ownership lifecycle', '']
    if not rows:
        lines.append('- none')
    else:
        for row in rows:
            summary = row.get('summary', '')
            prior = row.get('prior_lease_expires_at', '')
            lease_expires_at = row.get('lease_expires_at', row.get('expires_at', ''))
            extra = '' if not prior else f" prior_lease_expires_at={prior}"
            lines.append(
                f"- t={row['timestamp']} output={row['output_id']} event={row['event_type']} owner={row['owner']} lease_expires_at={lease_expires_at}{extra} summary={summary}"
            )
    _write_markdown(output_root / 'ownership_ledger.md', lines)


def _write_report_markdown(path: Path, payload: dict[str, object]) -> None:
    summary = payload['command_summary']
    replay = payload['replay_report']
    checkpoint = payload['checkpoint_summary']
    degraded = payload['degraded_report']
    lines = [
        '# UniversalDAQ Cross-Device Command and Arbitration',
        '',
        f"- generated_at_utc: {payload['generated_at_utc']}",
        f"- verdict: {payload['verdict']}",
        f"- session_id: {payload['session_id']}",
        f"- report_dir: {payload['report_dir']}",
        f"- writable_tag_count: {payload['writable_tag_count']}",
        f"- activated_adapter_count: {payload['activated_adapter_count']}",
        '',
        '## Command summary',
        '',
        f"- command_attempt_count: {summary['command_attempt_count']}",
        f"- accepted_count: {summary['accepted_count']}",
        f"- rejected_count: {summary['rejected_count']}",
        f"- adapter_failed_count: {summary['adapter_failed_count']}",
        f"- ownership_conflict_count: {summary['ownership_conflict_count']}",
        f"- same_owner_renewal_count: {summary['same_owner_renewal_count']}",
        f"- stale_lease_expiration_count: {summary['stale_lease_expiration_count']}",
        f"- target_unavailable_count: {summary['target_unavailable_count']}",
        '',
        '## Degraded conditions',
        '',
        f"- degraded_transition_count: {degraded['degraded_transition_count']}",
        f"- simultaneous_drop_event_count: {degraded['simultaneous_drop_event_count']}",
        f"- safe_state_event_count: {degraded['safe_state_event_count']}",
        f"- lease_revoked_on_degrade_count: {degraded['lease_revoked_on_degrade_count']}",
        '',
        '## Evidence depth',
        '',
        f"- persisted_record_count: {payload['history_tier_summary']['cold']['persisted_record_count']}",
        f"- segment_count: {payload['history_tier_summary']['cold']['segment_count']}",
        f"- checkpoint_count: {checkpoint['valid_checkpoint_count']}",
        f"- replay_tail_count: {replay['tail_record_count']}",
        f"- replay_tail_record_type_count: {replay['tail_record_type_count']}",
        '',
        '## Checks',
        '',
    ]
    for check in payload['checks']:
        lines.append(f"- [{check['status']}] {check['name']} — {check['message']}")
    _write_markdown(path, lines)


def _make_writable_adapter(*, adapter_id: str, point_ids: tuple[str, ...]):
    from universaldaq.adapters.simulated import SimulatedWritableAdapter

    return SimulatedWritableAdapter(
        adapter_id=adapter_id,
        writable_points={point_id: '0' for point_id in point_ids},
        observed_points={point_id: '0' for point_id in point_ids},
    )


def run_cross_device_command_arbitration(
    *,
    package_root: Path,
    output_root: Path,
    session_id: str = 'SESSION-CROSS-DEVICE-COMMANDS',
    cycle_count: int = 11,
    checkpoint_interval_cycles: int = 2,
) -> dict[str, object]:
    _prepare_import_path(package_root)

    from tools.acceptance.run_real_hardware_specimen_bridge import _build_runtime_quality
    from tools.acceptance.verify_session_artifacts import verify_session_artifacts
    from universaldaq.adapters import AdapterPollResult
    from universaldaq.app import build_default_service_registry
    from universaldaq.common import ActorId, OutputId, RequestId, as_event_time
    from universaldaq.outputs import (
        CommandArbitrationBroker,
        OutputCommandService,
        SafeStatePolicy,
        WritableTagBinding,
    )
    from universaldaq.tags import CanonicalTagRegistryService, MultiAdapterAcquisitionBroker
    from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary

    output_root.mkdir(parents=True, exist_ok=True)
    generated_at_utc = datetime.now(timezone.utc).isoformat()

    services = build_default_service_registry(load_support_packs=False)
    adapters = {
        'labjack_u6_470201': _make_writable_adapter(adapter_id='labjack_u6_470201', point_ids=('digital_out_0',)),
        'arduino_uno_ard_401': _make_writable_adapter(adapter_id='arduino_uno_ard_401', point_ids=('digital_out_0',)),
        'rpi_rpi_lab_401': _make_writable_adapter(adapter_id='rpi_rpi_lab_401', point_ids=('gpio_out_0',)),
    }
    for adapter in adapters.values():
        services.adapters.register(adapter)

    tag_registry = CanonicalTagRegistryService(metrics=services.runtime_metrics)
    acquisition_broker = MultiAdapterAcquisitionBroker(adapter_manager=services.adapters, tag_registry=tag_registry, metrics=services.runtime_metrics)
    output_service = OutputCommandService()
    command_broker = CommandArbitrationBroker(adapter_manager=services.adapters, output_service=output_service)

    writable_rows: list[dict[str, str]] = []
    for adapter_id, adapter in adapters.items():
        for definition in tag_registry.register_capability(adapter.capability()):
            if not definition.writable:
                continue
            policy = {
                'labjack_u6_470201': SafeStatePolicy.RETURN_TO_SAFE,
                'arduino_uno_ard_401': SafeStatePolicy.REJECT_COMMANDS,
                'rpi_rpi_lab_401': SafeStatePolicy.HOLD_LAST,
            }[adapter_id]
            binding = WritableTagBinding(
                output_id=OutputId(definition.tag_key),
                tag_key=definition.tag_key,
                adapter_id=definition.adapter_id,
                point_id=definition.source_point_id,
                display_name=definition.display_name,
                safe_state_policy=policy,
                safe_state_value='0',
            )
            command_broker.register_binding(binding)
            writable_rows.append(binding.export_row())

    runtime, runtime_root = _build_runtime_quality(
        output_root=output_root,
        session_id=session_id,
        checkpoint_interval_cycles=checkpoint_interval_cycles,
    )

    scenario = {
        1: {'commands': [('manual', 'labjack_u6_470201:digital_out_0', '1')]},
        2: {'commands': [('manual', 'labjack_u6_470201:digital_out_0', '0')]},
        3: {'commands': [('runtime', 'labjack_u6_470201:digital_out_0', '1'), ('runtime', 'rpi_rpi_lab_401:gpio_out_0', '1')]},
        4: {'drop': ('arduino_uno_ard_401',), 'commands': [('manual', 'arduino_uno_ard_401:digital_out_0', '1')]},
        5: {'restore': ('arduino_uno_ard_401',), 'commands': [('manual', 'arduino_uno_ard_401:digital_out_0', '1')]},
        6: {'drop': ('labjack_u6_470201', 'rpi_rpi_lab_401'), 'commands': [('runtime', 'rpi_rpi_lab_401:gpio_out_0', '0')]},
        7: {'restore': ('labjack_u6_470201', 'rpi_rpi_lab_401'), 'commands': [('runtime', 'labjack_u6_470201:digital_out_0', '0')]},
        8: {'commands': [('manual', 'labjack_u6_470201:digital_out_0', '1')]},
        9: {'commands': [('supervisor', 'arduino_uno_ard_401:digital_out_0', '0'), ('runtime', 'rpi_rpi_lab_401:gpio_out_0', '0')]},
        10: {'commands': [('supervisor', 'arduino_uno_ard_401:digital_out_0', '1')]},
        11: {'drop': ('arduino_uno_ard_401',), 'commands': [('manual', 'arduino_uno_ard_401:digital_out_0', '0')]},
    }

    degraded_rows: list[dict[str, str]] = []
    command_rows: list[dict[str, str]] = []
    adapter_ids = tuple(adapters.keys())

    def _binding_ids_for_adapter(adapter_id: str) -> tuple[str, ...]:
        return tuple(row['output_id'] for row in writable_rows if row['adapter_id'] == adapter_id)

    for cycle_index in range(1, max(1, cycle_count) + 1):
        ts = as_event_time(600 + cycle_index)
        step = scenario.get(cycle_index, {})
        for adapter_id in step.get('drop', ()):  # type: ignore[arg-type]
            services.adapters.disconnected_adapter_ids.add(adapter_id)
            for output_id in _binding_ids_for_adapter(adapter_id):
                events = command_broker.set_output_availability(
                    output_id=OutputId(output_id),
                    available=False,
                    timestamp=ts,
                    summary='adapter dropped out of the bounded command lane',
                )
                for event in events:
                    degraded_rows.append(event.export_row())
                    runtime.record_state_event(timestamp=event.timestamp, event_type=event.event_type, attributes=event.export_row())
        if len(tuple(step.get('drop', ()))) > 1:
            runtime.record_state_event(
                timestamp=ts,
                event_type='simultaneous_adapter_drop',
                attributes={'adapter_ids': tuple(step.get('drop', ())), 'count': len(tuple(step.get('drop', ())))},
            )
        for adapter_id in step.get('restore', ()):  # type: ignore[arg-type]
            services.adapters.disconnected_adapter_ids.discard(adapter_id)
            for output_id in _binding_ids_for_adapter(adapter_id):
                events = command_broker.set_output_availability(
                    output_id=OutputId(output_id),
                    available=True,
                    timestamp=ts,
                    summary='adapter returned to the bounded command lane',
                )
                for event in events:
                    degraded_rows.append(event.export_row())
                    runtime.record_state_event(timestamp=event.timestamp, event_type=event.event_type, attributes=event.export_row())
        for owner, output_id, requested_value in step.get('commands', ()):  # type: ignore[arg-type]
            result = command_broker.issue_command(
                request_id=RequestId(f'REQ-CMD-{cycle_index}-{owner}-{output_id.replace(":", "-")}'),
                output_id=OutputId(output_id),
                requested_value=requested_value,
                actor=ActorId(owner),
                requested_at=ts,
                lease_duration_ticks=2,
            )
            command_rows.append(result.export_row())
            for event in result.broker_events:
                runtime.record_state_event(timestamp=event.timestamp, event_type=event.event_type, attributes=event.export_row())
            for row in result.trace.export_rows():
                runtime.record_operational_entry(timestamp=ts, record_type=row['record_type'], payload=row)
        batch = acquisition_broker.poll(adapter_ids=adapter_ids, timestamp=ts)
        snapshots = []
        for adapter_id in adapter_ids:
            poll_result = services.adapters.last_poll_results.get(adapter_id)
            if poll_result is None:
                continue
            runtime.capture_acquisition(adapter_id=adapter_id, timestamp=ts, poll_result=poll_result)
            snapshots.extend(poll_result.snapshots)
        runtime.record_state_event(
            timestamp=ts,
            event_type='command_cycle_summary',
            attributes={
                'cycle_index': cycle_index,
                'adapter_count': len(batch.adapter_ids),
                'snapshot_count': len(batch.samples),
                'command_count': len(tuple(step.get('commands', ()))),
            },
        )
        combined_poll_result = AdapterPollResult(
            adapter_id='BROKER-COMMAND-001',
            polled_at=ts,
            snapshots=tuple(snapshots),
            diagnostics=batch.diagnostics,
        )
        runtime.record_processed_cycle(
            timestamp=ts,
            lifecycle_summary=DeviceLifecycleSummary(
                phase='live',
                detected_device_count=len(adapter_ids),
                active_device_key='CROSS-DEVICE-COMMANDS',
                active_adapter_id='BROKER-COMMAND-001',
                projected_point_count=len(tag_registry.definitions),
                published_signal_count=len(tag_registry.latest_samples),
                last_poll_snapshot_count=len(snapshots),
                disconnected_signal_count=0,
                last_transition='command_arbitration_cycle',
                needs_review=False,
            ),
            variable_summary=VariableHealthSummary(total_variable_count=0, healthy_count=0),
            changed_signal_ids=tuple(sample.tag_key for sample in batch.samples),
            poll_result=combined_poll_result,
        )

    tail_ts = as_event_time(700)
    runtime.record_state_event(
        timestamp=tail_ts,
        event_type='command_tail_verification',
        attributes={'command_attempt_count': len(command_rows), 'event_count': len(command_broker.events)},
    )
    runtime.flush_journal(now=tail_ts)
    review_summary = runtime.build_review_summary(limit=32)
    review_summary['session_root'] = str(runtime_root / 'sessions' / session_id)
    artifact_report = verify_session_artifacts(Path(review_summary['session_root']))

    command_counter = Counter(row['disposition'] for row in command_rows)
    degraded_report = {
        'degraded_transition_count': sum(1 for row in degraded_rows if row['event_type'] in {'target_degraded', 'target_restored'}),
        'simultaneous_drop_event_count': sum(1 for row in runtime.event_history if row.get('event_type') == 'simultaneous_adapter_drop'),
        'safe_state_event_count': sum(1 for row in degraded_rows if row['event_type'] == 'safe_state_required'),
        'lease_revoked_on_degrade_count': sum(1 for row in degraded_rows if row['event_type'] == 'lease_revoked_on_degrade'),
        'timeline_rows': list(degraded_rows),
    }
    command_summary = {
        'command_attempt_count': len(command_rows),
        'accepted_count': command_counter.get('accepted', 0),
        'rejected_count': command_counter.get('ownership_conflict', 0) + command_counter.get('target_unavailable', 0) + command_counter.get('invalid_target', 0),
        'adapter_failed_count': command_counter.get('adapter_failed', 0),
        'ownership_conflict_count': command_counter.get('ownership_conflict', 0),
        'same_owner_renewal_count': sum(1 for event in command_broker.events if event.event_type == 'ownership_renewed'),
        'stale_lease_expiration_count': sum(1 for event in command_broker.events if event.event_type == 'lease_expired'),
        'target_unavailable_count': command_counter.get('target_unavailable', 0),
        'command_rows': list(command_rows),
    }

    checks = [
        {
            'name': 'writable_tag_inventory',
            'status': 'PASS' if len(writable_rows) >= 3 else 'FAIL',
            'message': f'writable_tag_count={len(writable_rows)}',
        },
        {
            'name': 'healthy_command_acknowledged',
            'status': 'PASS' if command_summary['accepted_count'] >= 4 else 'FAIL',
            'message': json.dumps({'accepted_count': command_summary['accepted_count']}, sort_keys=True),
        },
        {
            'name': 'ownership_conflict_rejected',
            'status': 'PASS' if command_summary['ownership_conflict_count'] >= 1 else 'FAIL',
            'message': json.dumps({'ownership_conflict_count': command_summary['ownership_conflict_count']}, sort_keys=True),
        },
        {
            'name': 'same_owner_lease_renewal',
            'status': 'PASS' if command_summary['same_owner_renewal_count'] >= 1 else 'FAIL',
            'message': json.dumps({'same_owner_renewal_count': command_summary['same_owner_renewal_count']}, sort_keys=True),
        },
        {
            'name': 'stale_lease_expiry',
            'status': 'PASS' if command_summary['stale_lease_expiration_count'] >= 1 else 'FAIL',
            'message': json.dumps({'stale_lease_expiration_count': command_summary['stale_lease_expiration_count']}, sort_keys=True),
        },
        {
            'name': 'degraded_output_behavior',
            'status': 'PASS' if degraded_report['degraded_transition_count'] >= 5 and degraded_report['simultaneous_drop_event_count'] >= 1 and degraded_report['lease_revoked_on_degrade_count'] >= 1 else 'FAIL',
            'message': json.dumps({'degraded_transition_count': degraded_report['degraded_transition_count'], 'simultaneous_drop_event_count': degraded_report['simultaneous_drop_event_count'], 'lease_revoked_on_degrade_count': degraded_report['lease_revoked_on_degrade_count']}, sort_keys=True),
        },
        {
            'name': 'target_unavailable_rejected',
            'status': 'PASS' if command_summary['target_unavailable_count'] >= 2 else 'FAIL',
            'message': json.dumps({'target_unavailable_count': command_summary['target_unavailable_count']}, sort_keys=True),
        },
        {
            'name': 'command_evidence_depth',
            'status': 'PASS' if review_summary['history_tier_summary']['cold']['persisted_record_count'] >= 40 and review_summary['checkpoint_summary']['valid_checkpoint_count'] >= 3 else 'FAIL',
            'message': json.dumps({'records': review_summary['history_tier_summary']['cold']['persisted_record_count'], 'checkpoints': review_summary['checkpoint_summary']['valid_checkpoint_count']}, sort_keys=True),
        },
        {
            'name': 'command_replay_tail',
            'status': 'PASS' if review_summary['replay_report']['tail_record_count'] >= 4 and review_summary['replay_report']['tail_contains_multiple_record_types'] else 'FAIL',
            'message': json.dumps({'tail_record_count': review_summary['replay_report']['tail_record_count'], 'tail_record_counts_by_type': review_summary['replay_report']['tail_record_counts_by_type']}, sort_keys=True),
        },
        {
            'name': 'session_artifact_integrity',
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
        'activated_adapter_count': len(adapter_ids),
        'writable_tag_count': len(writable_rows),
        'writable_tag_rows': writable_rows,
        'command_summary': command_summary,
        'degraded_report': degraded_report,
        'history_tier_summary': review_summary['history_tier_summary'],
        'history_index_report': review_summary['history_index_report'],
        'checkpoint_summary': review_summary['checkpoint_summary'],
        'replay_report': review_summary['replay_report'],
        'session_artifact_report': artifact_report,
        'checks': checks,
    }
    _write_json(output_root / 'cross_device_command_arbitration_report.json', payload)
    _write_report_markdown(output_root / 'cross_device_command_arbitration_report.md', payload)
    _write_writable_inventory(output_root, tuple(writable_rows))
    timeline_rows = tuple(event.export_row() for event in command_broker.events)
    _write_timeline(output_root, timeline_rows)
    ownership_rows = tuple(
        row for row in timeline_rows if row['event_type'] in {'ownership_granted', 'ownership_renewed', 'lease_expired', 'lease_revoked_on_degrade', 'lease_cleared_on_restore'}
    )
    _write_ownership_ledger(output_root, ownership_rows)
    _write_json(output_root / 'review_summary.json', review_summary)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/cross_device_command_arbitration')
    parser.add_argument('--session-id', default='SESSION-CROSS-DEVICE-COMMANDS')
    parser.add_argument('--cycle-count', type=int, default=9)
    parser.add_argument('--checkpoint-interval-cycles', type=int, default=2)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    output_root = Path(args.output_root)
    if not output_root.is_absolute():
        output_root = package_root / output_root
    report = run_cross_device_command_arbitration(
        package_root=package_root,
        output_root=output_root,
        session_id=args.session_id,
        cycle_count=args.cycle_count,
        checkpoint_interval_cycles=args.checkpoint_interval_cycles,
    )
    print(
        'cross-device-command-arbitration:'
        f" verdict={report['verdict']}"
        f" writable_tags={report['writable_tag_count']}"
        f" commands={report['command_summary']['command_attempt_count']}"
        f" accepted={report['command_summary']['accepted_count']}"
        f" degraded_events={report['degraded_report']['degraded_transition_count']}"
        f" checkpoints={report['checkpoint_summary']['valid_checkpoint_count']}"
    )
    return 0 if report['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
