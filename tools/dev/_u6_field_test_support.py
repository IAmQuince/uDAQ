from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, Sequence

from universaldaq.runtime.semantics import build_runtime_semantic_state, reviewer_label_for_family

from tools.dev._u6_live_support import run_poll_cycles


@dataclass(frozen=True, slots=True)
class U6FieldTestCapture:
    phase_name: str
    timestamp_start: int
    timestamp_end: int
    poll_cycles: int
    observed_at_utc: str
    ui_phase: str
    lifecycle_summary_phase: str
    active_adapter_id: str | None
    adapter_status: dict[str, object]
    runtime_status: dict[str, object]
    incremental_runtime_summary: dict[str, object]
    event_alarm_summary: dict[str, object]
    recent_event_count: int
    recent_runtime_event_count: int
    active_alarm_count: int
    semantic_state_family: str
    semantic_reviewer_label: str

    def as_dict(self) -> dict[str, object]:
        return {
            'phase_name': self.phase_name,
            'timestamp_start': self.timestamp_start,
            'timestamp_end': self.timestamp_end,
            'poll_cycles': self.poll_cycles,
            'observed_at_utc': self.observed_at_utc,
            'ui_phase': self.ui_phase,
            'lifecycle_summary_phase': self.lifecycle_summary_phase,
            'active_adapter_id': self.active_adapter_id,
            'adapter_status': self.adapter_status,
            'runtime_status': self.runtime_status,
            'incremental_runtime_summary': self.incremental_runtime_summary,
            'event_alarm_summary': self.event_alarm_summary,
            'recent_event_count': self.recent_event_count,
            'recent_runtime_event_count': self.recent_runtime_event_count,
            'active_alarm_count': self.active_alarm_count,
            'semantic_state_family': self.semantic_state_family,
            'semantic_reviewer_label': self.semantic_reviewer_label,
        }


@dataclass(frozen=True, slots=True)
class U6FieldTestPhaseExpectation:
    phase_name: str
    phase_label: str
    expected_state_family: str
    acceptable_state_families: tuple[str, ...]
    strict_expectation: bool
    rationale: str

    def as_dict(self) -> dict[str, object]:
        return {
            'phase_name': self.phase_name,
            'phase_label': self.phase_label,
            'expected_state_family': self.expected_state_family,
            'expected_state_label': reviewer_label_for_family(self.expected_state_family),
            'acceptable_state_families': list(self.acceptable_state_families),
            'strict_expectation': self.strict_expectation,
            'rationale': self.rationale,
        }


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def snapshot_active_adapter(controller) -> dict[str, object]:
    adapter_id = controller.session.ui_session.active_adapter_id
    if adapter_id is None:
        return {'adapter_id': None, 'status': 'no_active_adapter'}
    adapter = controller.services.adapters.adapters.get(adapter_id)
    if adapter is None:
        return {'adapter_id': adapter_id, 'status': 'adapter_missing'}
    status_snapshot = getattr(adapter, 'status_snapshot', None)
    if callable(status_snapshot):
        snapshot = status_snapshot()
        if hasattr(snapshot, 'as_dict'):
            return snapshot.as_dict()
        return dict(snapshot)
    capability = adapter.capability()
    health = adapter.health()
    return {
        'adapter_id': adapter_id,
        'status': 'generic_adapter_snapshot',
        'hardware_mode': capability.metadata.get('hardware_mode', 'unknown'),
        'is_simulated': capability.is_simulated,
        'health_state': health.state.value,
        'health_summary': health.summary,
        'consecutive_failures': health.consecutive_failures,
    }


def capture_phase(
    *,
    controller,
    phase_name: str,
    timestamp_start: int,
    poll_cycles: int,
    cycle_delay_seconds: float = 0.0,
) -> U6FieldTestCapture:
    run_poll_cycles(controller, timestamp_start=timestamp_start, cycles=poll_cycles, cycle_delay_seconds=cycle_delay_seconds)
    timestamp_end = timestamp_start + max(0, poll_cycles) - 1 if poll_cycles else timestamp_start
    bundle = controller.lifecycle_review_bundle()
    adapter_status = snapshot_active_adapter(controller)
    semantic_state = build_runtime_semantic_state(
        ui_phase=controller.session.ui_session.device_lifecycle_phase.value,
        lifecycle_summary_phase=bundle['lifecycle_summary']['phase'],
        adapter_status=adapter_status,
    )
    return U6FieldTestCapture(
        phase_name=phase_name,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        poll_cycles=poll_cycles,
        observed_at_utc=utc_now_iso(),
        ui_phase=controller.session.ui_session.device_lifecycle_phase.value,
        lifecycle_summary_phase=bundle['lifecycle_summary']['phase'],
        active_adapter_id=controller.session.ui_session.active_adapter_id,
        adapter_status=adapter_status,
        runtime_status=bundle['runtime_status'],
        incremental_runtime_summary=bundle['incremental_runtime_summary'],
        event_alarm_summary=bundle['event_alarm_summary'],
        recent_event_count=len(bundle['recent_event_rows']),
        recent_runtime_event_count=len(bundle.get('recent_runtime_event_rows', [])),
        active_alarm_count=len(bundle['active_alarm_rows']),
        semantic_state_family=semantic_state.canonical_state_family,
        semantic_reviewer_label=semantic_state.reviewer_label,
    )


def load_package_identity(package_root: Path) -> dict[str, str]:
    manifest_path = package_root / 'docs' / 'release' / 'RELEASE_MANIFEST.yaml'
    identity = {
        'package_id': 'unknown',
        'package_slug': 'unknown',
        'package_date': 'unknown',
        'run_id': 'unknown',
        'disposition': 'unknown',
    }
    if not manifest_path.exists():
        return identity
    for raw_line in manifest_path.read_text(encoding='utf-8').splitlines():
        if ':' not in raw_line or raw_line.startswith('  '):
            continue
        key, value = raw_line.split(':', 1)
        key = key.strip()
        if key in identity:
            identity[key] = value.strip()
    return identity


def build_preflight_report(
    *,
    package_root: Path,
    bundle_dir: Path,
    session_metadata: Mapping[str, object],
    controller,
    journal_path: Path,
    stale_artifact_count: int,
    direct_open_probe: Mapping[str, object] | None = None,
) -> dict[str, object]:
    profile_id = 'unknown'
    profile_snapshot = getattr(controller.session, 'profile_snapshot', None)
    if profile_snapshot is not None:
        profile_id = str(profile_snapshot.profile_id)
    return {
        'generated_at_utc': utc_now_iso(),
        'package_identity': load_package_identity(package_root),
        'python_version': sys.version.split()[0],
        'python_implementation': platform.python_implementation(),
        'platform': platform.platform(),
        'platform_system': platform.system(),
        'platform_release': platform.release(),
        'requested_mode': session_metadata.get('requested_mode'),
        'real_hardware_requested': session_metadata.get('requested_mode') == 'real',
        'validation_flow': session_metadata.get('validation_flow'),
        'run_stem': session_metadata.get('run_stem'),
        'entered_mode': session_metadata.get('entered_mode'),
        'serial_number': session_metadata.get('serial_number'),
        'active_adapter_id': session_metadata.get('active_adapter_id'),
        'profile_id': profile_id,
        'journal_path': str(journal_path),
        'output_directory': str(bundle_dir),
        'discovered_devices': list(session_metadata.get('discovered_devices', [])),
        'stale_artifact_count_in_output_root': stale_artifact_count,
        'discovery_strategy': session_metadata.get('discovery_strategy'),
        'direct_open_probe': None if direct_open_probe is None else dict(direct_open_probe),
    }


def build_phase_expectations(*, requested_mode: str, skip_recovery: bool, startup_only: bool = False) -> dict[str, U6FieldTestPhaseExpectation]:
    expectations = {
        'baseline': U6FieldTestPhaseExpectation(
            phase_name='baseline',
            phase_label='Baseline nominal sampling',
            expected_state_family='live_ready_healthy',
            acceptable_state_families=('live_ready_healthy',),
            strict_expectation=True,
            rationale='The bounded slice should reach a healthy live posture before the disturbance is introduced.',
        ),
    }
    if startup_only:
        return expectations
    expectations['device_loss_window'] = U6FieldTestPhaseExpectation(
        phase_name='device_loss_window',
        phase_label='Disconnect observation window',
        expected_state_family='disconnected',
        acceptable_state_families=('degraded', 'disconnected', 'recovering', 'faulted'),
        strict_expectation=requested_mode == 'real',
        rationale='In real hardware mode the requested unplug should produce a degraded/disconnected style observation. In simulated mode this remains an observation-only phase.',
    )
    if not skip_recovery:
        expectations['recovery_window'] = U6FieldTestPhaseExpectation(
            phase_name='recovery_window',
            phase_label='Recovery observation window',
            expected_state_family='recovering',
            acceptable_state_families=('recovering', 'live_ready_healthy', 'degraded'),
            strict_expectation=requested_mode == 'real',
            rationale='After reconnection the bounded slice should either be actively recovering or already back to a live-ready posture.',
        )
        expectations['post_recovery_stabilization'] = U6FieldTestPhaseExpectation(
            phase_name='post_recovery_stabilization',
            phase_label='Post-recovery stabilization window',
            expected_state_family='live_ready_healthy',
            acceptable_state_families=('live_ready_healthy',),
            strict_expectation=True,
            rationale='The final confirmation window should settle back to a healthy live posture before the diagnostic package is written.',
        )
    return expectations


def build_phase_records(
    *,
    captures: Sequence[U6FieldTestCapture],
    expectations: Mapping[str, U6FieldTestPhaseExpectation],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for capture in captures:
        expectation = expectations.get(capture.phase_name)
        acceptable = tuple(expectation.acceptable_state_families) if expectation is not None else tuple()
        observed = capture.semantic_state_family
        if expectation is None:
            status = 'PASS'
            note = 'no explicit expectation registered'
        elif observed in acceptable:
            status = 'PASS'
            note = 'observed state family falls within the accepted phase set'
        elif expectation.strict_expectation:
            status = 'FAIL'
            note = 'observed state family did not satisfy the strict phase expectation'
        else:
            status = 'ADVISORY'
            note = 'observation differed from the nominal expectation, but this phase is non-strict in the current mode'
        rows.append(
            {
                'phase_name': capture.phase_name,
                'phase_label': expectation.phase_label if expectation else capture.phase_name,
                'phase_start_timestamp': capture.timestamp_start,
                'phase_end_timestamp': capture.timestamp_end,
                'poll_cycles': capture.poll_cycles,
                'observed_at_utc': capture.observed_at_utc,
                'expected_state_family': None if expectation is None else expectation.expected_state_family,
                'expected_state_label': None if expectation is None else reviewer_label_for_family(expectation.expected_state_family),
                'acceptable_state_families': list(acceptable),
                'strict_expectation': False if expectation is None else expectation.strict_expectation,
                'observed_state_family': observed,
                'observed_reviewer_label': capture.semantic_reviewer_label,
                'ui_phase': capture.ui_phase,
                'lifecycle_summary_phase': capture.lifecycle_summary_phase,
                'adapter_lifecycle_state': capture.adapter_status.get('lifecycle_state', capture.adapter_status.get('status')),
                'recent_event_count': capture.recent_event_count,
                'recent_runtime_event_count': capture.recent_runtime_event_count,
                'active_alarm_count': capture.active_alarm_count,
                'status': status,
                'note': note,
                'rationale': '' if expectation is None else expectation.rationale,
            }
        )
    return rows


def _incident_summary(*, captures: Sequence[U6FieldTestCapture]) -> dict[str, object]:
    final_status = {} if not captures else captures[-1].adapter_status
    disconnect_count = int(final_status.get('disconnect_count', 0) or 0)
    recovery_count = int(final_status.get('recovery_count', 0) or 0)
    return {
        'disconnect_count': disconnect_count,
        'recovery_count': recovery_count,
        'session_had_disconnect': bool(final_status.get('session_had_disconnect', False)),
        'session_recovered_after_disconnect': bool(final_status.get('session_recovered_after_disconnect', False)),
        'last_disconnect_at': final_status.get('last_disconnect_at'),
        'last_disconnect_reason': final_status.get('last_disconnect_reason'),
        'last_recovery_at': final_status.get('last_recovery_at'),
        'last_recovery_reason': final_status.get('last_recovery_reason'),
    }


def _recovery_analysis(
    *,
    captures: Sequence[U6FieldTestCapture],
    final_review_bundle: Mapping[str, object],
) -> dict[str, object]:
    final_status = {} if not captures else captures[-1].adapter_status
    runtime_events = list(final_review_bundle.get('recent_runtime_event_rows', []))
    runtime_event_types = [str(event.get('event_type', event.get('record_type', 'runtime_event'))) for event in runtime_events]
    stabilization_capture = next((capture for capture in reversed(captures) if capture.phase_name == 'post_recovery_stabilization'), None)
    return {
        'rediscovery_required': False,
        'rediscovery_observed': 'not_required',
        'reconnect_attempt_started': bool(int(final_status.get('reconnect_attempts', 0) or 0) > 0),
        'backend_reopen_observed': bool(int(final_status.get('reconnect_backend_open_success_count', 0) or 0) > 0),
        'backend_reopen_failure_count': int(final_status.get('reconnect_backend_open_failure_count', 0) or 0),
        'active_adapter_rebound_observed': 'adapter_rebind_succeeded' in runtime_event_types,
        'post_disconnect_successful_poll_observed': bool(int(final_status.get('post_disconnect_successful_poll_count', 0) or 0) > 0),
        'recovered': bool(final_status.get('session_recovered_after_disconnect', False)),
        'recovery_stage': final_status.get('recovery_stage', 'unknown'),
        'last_recovery_failure_stage': final_status.get('last_recovery_failure_stage'),
        'last_recovery_failure_reason': final_status.get('last_recovery_failure_reason'),
        'runtime_event_types': runtime_event_types,
        'stabilization_observed': stabilization_capture is not None,
        'stabilization_state_family': None if stabilization_capture is None else stabilization_capture.semantic_state_family,
        'stabilization_reviewer_label': None if stabilization_capture is None else stabilization_capture.semantic_reviewer_label,
    }


def _write_json(path: Path, payload: Mapping[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def _write_text(path: Path, lines: Sequence[str]) -> None:
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def _artifact_manifest(bundle_dir: Path, paths: Mapping[str, Path]) -> dict[str, object]:
    artifacts: list[dict[str, object]] = []
    for label, path in sorted(paths.items()):
        data = path.read_bytes()
        artifacts.append(
            {
                'label': label,
                'relative_path': path.relative_to(bundle_dir).as_posix(),
                'bytes': len(data),
                'sha256': hashlib.sha256(data).hexdigest(),
            }
        )
    return {
        'bundle_dir': str(bundle_dir),
        'artifact_count': len(artifacts),
        'artifacts': artifacts,
    }


def write_field_test_bundle(
    *,
    bundle_dir: Path,
    preflight_report: Mapping[str, object],
    session_metadata: Mapping[str, object],
    captures: Sequence[U6FieldTestCapture],
    phase_records: Sequence[Mapping[str, object]],
    operator_events: Sequence[Mapping[str, object]],
    semantic_consistency: Mapping[str, object],
    final_review_bundle: Mapping[str, object],
) -> dict[str, Path]:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    stem = bundle_dir.name
    summary_path = bundle_dir / f'{stem}__summary.txt'
    events_path = bundle_dir / f'{stem}__events.csv'
    diagnostics_path = bundle_dir / f'{stem}__diagnostics.json'
    smoke_path = bundle_dir / f'{stem}__smoke.txt'
    preflight_json_path = bundle_dir / f'{stem}__preflight-report.json'
    preflight_text_path = bundle_dir / f'{stem}__preflight-report.txt'
    verdict_json_path = bundle_dir / f'{stem}__semantic-consistency-verdict.json'
    verdict_text_path = bundle_dir / f'{stem}__semantic-consistency-verdict.txt'
    start_here_path = bundle_dir / f'{stem}__start-here.txt'
    review_summary_path = bundle_dir / f'{stem}__review-summary.md'
    manifest_json_path = bundle_dir / f'{stem}__artifact-manifest.json'
    manifest_text_path = bundle_dir / f'{stem}__artifact-manifest.txt'

    incident_summary = _incident_summary(captures=captures)
    recovery_analysis = _recovery_analysis(captures=captures, final_review_bundle=final_review_bundle)
    diagnostics_payload = {
        'preflight_report': dict(preflight_report),
        'session_metadata': dict(session_metadata),
        'incident_summary': incident_summary,
        'recovery_analysis': recovery_analysis,
        'phase_records': list(phase_records),
        'captures': [capture.as_dict() for capture in captures],
        'operator_events': list(operator_events),
        'semantic_consistency': dict(semantic_consistency),
        'final_review_bundle': dict(final_review_bundle),
    }
    _write_json(preflight_json_path, dict(preflight_report))
    _write_json(verdict_json_path, dict(semantic_consistency))
    _write_json(diagnostics_path, diagnostics_payload)

    preflight_lines = [
        'UDQ U6 Guided Field Validation — Preflight',
        '=========================================',
        f"generated_at_utc: {preflight_report.get('generated_at_utc')}",
        f"package_id: {preflight_report.get('package_identity', {}).get('package_id')}",
        f"requested_mode: {preflight_report.get('requested_mode')}",
        f"validation_flow: {preflight_report.get('validation_flow')}",
        f"run_stem: {preflight_report.get('run_stem')}",
        f"entered_mode: {preflight_report.get('entered_mode')}",
        f"serial_number: {preflight_report.get('serial_number')}",
        f"active_adapter_id: {preflight_report.get('active_adapter_id')}",
        f"profile_id: {preflight_report.get('profile_id')}",
        f"python_version: {preflight_report.get('python_version')}",
        f"platform: {preflight_report.get('platform')}",
        f"output_directory: {preflight_report.get('output_directory')}",
        f"journal_path: {preflight_report.get('journal_path')}",
        f"stale_artifact_count_in_output_root: {preflight_report.get('stale_artifact_count_in_output_root')}",
        f"discovery_strategy: {preflight_report.get('discovery_strategy')}",
        '',
        'Direct-open probe',
        '-----------------',
    ]
    direct_open_probe = preflight_report.get('direct_open_probe')
    if direct_open_probe:
        preflight_lines.extend([
            f"- success: {direct_open_probe.get('success')}",
            f"- resolved_serial_number: {direct_open_probe.get('resolved_serial_number')}",
            f"- open_strategy: {direct_open_probe.get('open_strategy')}",
            f"- open_stage: {direct_open_probe.get('open_stage')}",
            f"- ain0_value: {direct_open_probe.get('ain0_value')}",
            f"- error_type: {direct_open_probe.get('error_type')}",
            f"- error_message: {direct_open_probe.get('error_message')}",
        ])
    else:
        preflight_lines.append('- not run')
    preflight_lines.extend([
        '',
        'Discovered devices',
        '------------------',
    ])
    discovered_devices = list(preflight_report.get('discovered_devices', []))
    if discovered_devices:
        for row in discovered_devices:
            preflight_lines.append(
                f"- {row.get('device_key')}: {row.get('display_name')} (provider={row.get('provider_id')}, serial={row.get('serial_number')})"
            )
    else:
        preflight_lines.append('- none discovered')
    _write_text(preflight_text_path, preflight_lines)

    with events_path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=['event_type', 'source', 'phase_name', 'timestamp', 'detail'])
        writer.writeheader()
        for event in operator_events:
            writer.writerow(
                {
                    'event_type': event.get('event_type', 'operator_action'),
                    'source': event.get('source', 'operator'),
                    'phase_name': event.get('phase_name', ''),
                    'timestamp': event.get('timestamp', ''),
                    'detail': event.get('detail', ''),
                }
            )
        for event in final_review_bundle.get('recent_runtime_event_rows', []):
            writer.writerow(
                {
                    'event_type': event.get('event_type', event.get('record_type', 'runtime_event')),
                    'source': 'runtime',
                    'phase_name': '',
                    'timestamp': event.get('timestamp', ''),
                    'detail': json.dumps(event, sort_keys=True),
                }
            )
        for record in phase_records:
            writer.writerow(
                {
                    'event_type': 'phase_capture',
                    'source': 'harness',
                    'phase_name': record.get('phase_name', ''),
                    'timestamp': record.get('phase_end_timestamp', ''),
                    'detail': json.dumps(record, sort_keys=True),
                }
            )

    reviewer_rollup = final_review_bundle.get('reviewer_runtime_rollup', {})
    canonical_bundle = final_review_bundle.get('canonical_runtime_evidence_bundle_v1', {})
    summary_lines = [
        'UDQ U6 Guided Field Validation Summary',
        '=====================================',
        f'bundle_dir: {bundle_dir}',
        f'validation_flow: {session_metadata.get("validation_flow")}',
        f'run_stem: {session_metadata.get("run_stem")}',
        f'mode_requested: {session_metadata.get("requested_mode")}',
        f'mode_entered: {session_metadata.get("entered_mode")}',
        f'serial_number: {session_metadata.get("serial_number")}',
        f'capture_count: {len(captures)}',
        f"discovery_strategy: {session_metadata.get('discovery_strategy')}",
        f"semantic_verdict: {semantic_consistency.get('verdict')}",
        f"semantic_verdict_reason: {semantic_consistency.get('summary')}",
        '',
        'Session Inventory',
        '-----------------',
        f"discovered_support_pack_device_count: {len(session_metadata.get('discovered_devices', []))}",
    ]
    for row in session_metadata.get('discovered_devices', []):
        summary_lines.append(
            f"- {row.get('device_key')}: {row.get('display_name')} (provider={row.get('provider_id')}, serial={row.get('serial_number')})"
        )
    direct_open_probe = session_metadata.get('direct_open_probe') or preflight_report.get('direct_open_probe')
    summary_lines.extend(
        [
            '',
            'Direct-open probe',
            '-----------------',
            f"success: {None if direct_open_probe is None else direct_open_probe.get('success')}",
            f"resolved_serial_number: {None if direct_open_probe is None else direct_open_probe.get('resolved_serial_number')}",
            f"open_strategy: {None if direct_open_probe is None else direct_open_probe.get('open_strategy')}",
            f"open_stage: {None if direct_open_probe is None else direct_open_probe.get('open_stage')}",
            f"ain0_value: {None if direct_open_probe is None else direct_open_probe.get('ain0_value')}",
            f"error_message: {None if direct_open_probe is None else direct_open_probe.get('error_message')}",
        ]
    )
    summary_lines.extend(
        [
            '',
            'Incident Summary',
            '----------------',
            f"disconnect_count: {incident_summary['disconnect_count']}",
            f"recovery_count: {incident_summary['recovery_count']}",
            f"session_had_disconnect: {incident_summary['session_had_disconnect']}",
            f"session_recovered_after_disconnect: {incident_summary['session_recovered_after_disconnect']}",
            f"last_disconnect_at: {incident_summary['last_disconnect_at']}",
            f"last_disconnect_reason: {incident_summary['last_disconnect_reason']}",
            f"last_recovery_at: {incident_summary['last_recovery_at']}",
            f"last_recovery_reason: {incident_summary['last_recovery_reason']}",
            '',
            'Recovery Analysis',
            '-----------------',
            f"reconnect_attempt_started: {recovery_analysis['reconnect_attempt_started']}",
            f"backend_reopen_observed: {recovery_analysis['backend_reopen_observed']}",
            f"active_adapter_rebound_observed: {recovery_analysis['active_adapter_rebound_observed']}",
            f"post_disconnect_successful_poll_observed: {recovery_analysis['post_disconnect_successful_poll_observed']}",
            f"recovered: {recovery_analysis['recovered']}",
            f"recovery_stage: {recovery_analysis['recovery_stage']}",
            f"stabilization_state_family: {recovery_analysis['stabilization_state_family']}",
            f"last_recovery_failure_stage: {recovery_analysis['last_recovery_failure_stage']}",
            f"last_recovery_failure_reason: {recovery_analysis['last_recovery_failure_reason']}",
            '',
            'Phase Timeline',
            '--------------',
        ]
    )
    for record in phase_records:
        summary_lines.append(
            f"- {record.get('phase_name')}: status={record.get('status')} observed={record.get('observed_reviewer_label')} "
            f"(family={record.get('observed_state_family')}) expected={record.get('expected_state_label')}"
        )
    summary_lines.extend(
        [
            '',
            'Reviewer Runtime Rollup',
            '-----------------------',
            f"state_family: {reviewer_rollup.get('state_family')}",
            f"reviewer_label: {reviewer_rollup.get('reviewer_label')}",
            f"summary: {reviewer_rollup.get('summary')}",
            '',
            'Canonical Runtime Evidence Bundle',
            '---------------------------------',
            f"bundle_version: {canonical_bundle.get('bundle_version')}",
            f"recent_runtime_event_count: {len(canonical_bundle.get('recent_runtime_events', []))}",
            f"recent_alarm_event_count: {len(canonical_bundle.get('recent_alarm_events', []))}",
            f"recent_operator_action_count: {len(canonical_bundle.get('recent_operator_actions', []))}",
            '',
            'Semantic Consistency Checks',
            '---------------------------',
        ]
    )
    for check in semantic_consistency.get('checks', []):
        summary_lines.append(f"- {check.get('status')}: {check.get('name')} — {check.get('message')}")
    summary_lines.extend(
        [
            '',
            'Output Files',
            '------------',
            str(start_here_path.name),
            str(summary_path.name),
            str(review_summary_path.name),
            str(preflight_json_path.name),
            str(preflight_text_path.name),
            str(events_path.name),
            str(diagnostics_path.name),
            str(verdict_json_path.name),
            str(verdict_text_path.name),
            str(manifest_json_path.name),
            str(manifest_text_path.name),
            str(smoke_path.name),
        ]
    )
    _write_text(summary_path, summary_lines)

    review_summary_lines = [
        '# U6 Guided Field Validation Summary',
        '',
        f"- **Generated at:** {preflight_report.get('generated_at_utc')}",
        f"- **Validation flow:** {session_metadata.get('validation_flow')}",
        f"- **Run stem:** {session_metadata.get('run_stem')}",
        f"- **Mode requested:** {session_metadata.get('requested_mode')}",
        f"- **Mode entered:** {session_metadata.get('entered_mode')}",
        f"- **Semantic verdict:** {semantic_consistency.get('verdict')}",
        '',
        '## Headline',
        '',
        f"{semantic_consistency.get('summary')}",
        '',
        '## Final runtime posture',
        '',
        f"- Reviewer label: `{reviewer_rollup.get('reviewer_label')}`",
        f"- State family: `{reviewer_rollup.get('state_family')}`",
        f"- Disconnect count: `{reviewer_rollup.get('disconnect_count')}`",
        f"- Recovery count: `{reviewer_rollup.get('recovery_count')}`",
        '',
        '## Phase results',
        '',
    ]
    for record in phase_records:
        review_summary_lines.append(
            f"- **{record.get('phase_label')}** — {record.get('status')} — observed `{record.get('observed_state_family')}` ({record.get('observed_reviewer_label')})"
        )
    review_summary_lines.extend(['', '## Next files to inspect', '', f"- `{verdict_text_path.name}`", f"- `{diagnostics_path.name}`", f"- `{events_path.name}`"])
    _write_text(review_summary_path, review_summary_lines)

    verdict_lines = [
        'UDQ U6 Guided Field Validation — Semantic Consistency Verdict',
        '===========================================================',
        f"verdict: {semantic_consistency.get('verdict')}",
        f"summary: {semantic_consistency.get('summary')}",
        f"check_count: {semantic_consistency.get('check_count')}",
        f"fail_count: {semantic_consistency.get('fail_count')}",
        f"advisory_count: {semantic_consistency.get('advisory_count')}",
        '',
        'Checks',
        '------',
    ]
    for check in semantic_consistency.get('checks', []):
        verdict_lines.append(f"- {check.get('status')}: {check.get('name')} — {check.get('message')}")
    _write_text(verdict_text_path, verdict_lines)

    smoke_payload = {
        'active_adapter_id': session_metadata.get('active_adapter_id'),
        'entered_mode': session_metadata.get('entered_mode'),
        'capture_count': len(captures),
        'disconnect_count': incident_summary['disconnect_count'],
        'recovery_count': incident_summary['recovery_count'],
        'backend_reopen_observed': recovery_analysis['backend_reopen_observed'],
        'active_adapter_rebound_observed': recovery_analysis['active_adapter_rebound_observed'],
        'post_disconnect_successful_poll_observed': recovery_analysis['post_disconnect_successful_poll_observed'],
        'final_recovery_failure_stage': recovery_analysis['last_recovery_failure_stage'],
        'final_ui_phase': captures[-1].ui_phase if captures else session_metadata.get('entered_mode', 'unknown'),
        'final_lifecycle_summary_phase': captures[-1].lifecycle_summary_phase if captures else 'unknown',
        'final_adapter_state': captures[-1].adapter_status.get('lifecycle_state', captures[-1].adapter_status.get('status')) if captures else 'unknown',
        'final_state_family': captures[-1].semantic_state_family if captures else 'unknown',
        'semantic_verdict': semantic_consistency.get('verdict'),
    }
    smoke_path.write_text(
        'UDQ U6 Guided Field Validation Smoke\n===================================\n' + json.dumps(smoke_payload, indent=2, sort_keys=True) + '\n',
        encoding='utf-8',
    )

    start_here_lines = [
        'START HERE — UDQ U6 Guided Field Validation',
        '===========================================',
        f"Semantic verdict: {semantic_consistency.get('verdict')}",
        f"Headline: {semantic_consistency.get('summary')}",
        '',
        'Open these in order:',
        f"1. {review_summary_path.name}",
        f"2. {verdict_text_path.name}",
        f"3. {summary_path.name}",
        f"4. {preflight_text_path.name}",
        f"5. {events_path.name}",
        f"6. {diagnostics_path.name}",
        '',
        'Most useful quick facts:',
        f"- Mode requested: {session_metadata.get('requested_mode')}",
        f"- Mode entered: {session_metadata.get('entered_mode')}",
        f"- Disconnect count: {incident_summary.get('disconnect_count')}",
        f"- Recovery count: {incident_summary.get('recovery_count')}",
        f"- Stabilization state family: {recovery_analysis.get('stabilization_state_family')}",
    ]
    _write_text(start_here_path, start_here_lines)

    provisional_paths = {
        'start_here': start_here_path,
        'summary': summary_path,
        'review_summary': review_summary_path,
        'preflight_json': preflight_json_path,
        'preflight_text': preflight_text_path,
        'events': events_path,
        'diagnostics': diagnostics_path,
        'semantic_verdict_json': verdict_json_path,
        'semantic_verdict_text': verdict_text_path,
        'smoke': smoke_path,
    }
    manifest_payload = _artifact_manifest(bundle_dir, provisional_paths)
    _write_json(manifest_json_path, manifest_payload)
    manifest_lines = [
        'UDQ U6 Guided Field Validation — Artifact Manifest',
        '=================================================',
        f"bundle_dir: {manifest_payload.get('bundle_dir')}",
        f"artifact_count: {manifest_payload.get('artifact_count')}",
        '',
        'Artifacts',
        '---------',
    ]
    for artifact in manifest_payload.get('artifacts', []):
        manifest_lines.append(
            f"- {artifact.get('label')}: {artifact.get('relative_path')} ({artifact.get('bytes')} bytes, sha256={artifact.get('sha256')})"
        )
    _write_text(manifest_text_path, manifest_lines)

    return {
        **provisional_paths,
        'artifact_manifest_json': manifest_json_path,
        'artifact_manifest_text': manifest_text_path,
    }
