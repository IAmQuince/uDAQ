from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

PACKAGE_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = PACKAGE_ROOT / 'src'
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


def _status(name: str, status: str, message: str, *, severity: str | None = None) -> dict[str, object]:
    return {
        'name': name,
        'status': status,
        'severity': severity or status,
        'message': message,
    }


def _runtime_event_types(final_review_bundle: Mapping[str, object]) -> list[str]:
    rows = list(final_review_bundle.get('recent_runtime_event_rows', []))
    return [str(row.get('event_type', row.get('record_type', 'runtime_event'))).lower() for row in rows]


def _contains_any(items: Sequence[str], probes: Sequence[str]) -> bool:
    lowered = tuple(item.lower() for item in items)
    return any(any(probe in item for probe in probes) for item in lowered)


def evaluate_runtime_evidence_consistency(
    *,
    session_metadata: Mapping[str, object],
    phase_records: Sequence[Mapping[str, object]],
    operator_events: Sequence[Mapping[str, object]],
    final_review_bundle: Mapping[str, object],
) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    reviewer_rollup = dict(final_review_bundle.get('reviewer_runtime_rollup', {}))
    canonical_bundle = dict(final_review_bundle.get('canonical_runtime_evidence_bundle_v1', {}))
    canonical_runtime_state = dict(canonical_bundle.get('runtime_state', {}))
    canonical_rollup = dict(canonical_bundle.get('reviewer_rollup', {}))
    runtime_event_types = _runtime_event_types(final_review_bundle)
    requested_mode = str(session_metadata.get('requested_mode', 'unknown'))
    validation_flow = str(session_metadata.get('validation_flow', 'guided_unplug_replug_validation'))
    startup_only = validation_flow == 'startup_open_smoke'
    active_adapter_status = dict(final_review_bundle.get('active_adapter_status') or {})
    startup_open_successes = int(active_adapter_status.get('startup_open_success_count', 0) or 0)
    startup_open_attempts = int(active_adapter_status.get('startup_open_attempts', 0) or 0)
    startup_open_confirmed = bool(active_adapter_status.get('has_successful_startup_open', False)) or startup_open_successes > 0

    rollup_family = reviewer_rollup.get('state_family')
    canonical_family = canonical_runtime_state.get('canonical_state_family')
    if rollup_family == canonical_family:
        checks.append(_status('rollup_matches_canonical_state', 'PASS', f'rollup state family `{rollup_family}` matches canonical runtime state family.'))
    else:
        checks.append(_status('rollup_matches_canonical_state', 'FAIL', f'rollup state family `{rollup_family}` does not match canonical runtime state family `{canonical_family}`.'))

    if reviewer_rollup.get('summary') == canonical_rollup.get('summary'):
        checks.append(_status('reviewer_summary_matches_canonical_bundle', 'PASS', 'reviewer summary matches the canonical bundle renderer.'))
    else:
        checks.append(_status('reviewer_summary_matches_canonical_bundle', 'FAIL', 'reviewer summary diverges from the canonical bundle renderer.'))

    if phase_records:
        final_phase = phase_records[-1]
        final_phase_family = final_phase.get('observed_state_family')
        if final_phase_family == rollup_family:
            checks.append(_status('final_phase_matches_rollup', 'PASS', 'final phase posture matches the reviewer rollup state family.'))
        else:
            checks.append(_status('final_phase_matches_rollup', 'ADVISORY', f'final phase family `{final_phase_family}` differs from reviewer rollup family `{rollup_family}`.'))
    else:
        checks.append(_status('final_phase_matches_rollup', 'FAIL', 'no phase records were available for comparison.'))

    phase_failures = [record for record in phase_records if record.get('status') == 'FAIL']
    if phase_failures:
        names = ', '.join(str(record.get('phase_name')) for record in phase_failures)
        checks.append(_status('phase_expectations_hold', 'FAIL', f'one or more strict phase expectations failed: {names}.'))
    else:
        checks.append(_status('phase_expectations_hold', 'PASS', 'all strict phase expectations passed.'))

    operator_distinct = all(str(event.get('event_type', '')).startswith(('operator_', 'harness_')) for event in operator_events)
    if operator_distinct:
        checks.append(_status('operator_markers_are_distinct', 'PASS', 'operator and harness markers remain distinct from runtime event rows.'))
    else:
        checks.append(_status('operator_markers_are_distinct', 'FAIL', 'one or more operator markers used an event type that can be confused with runtime rows.'))

    disconnect_count = int(reviewer_rollup.get('disconnect_count', 0) or 0)
    if disconnect_count > 0:
        if _contains_any(runtime_event_types, ('disconnect', 'degraded', 'adapter_rebind', 'recovery')) or any(
            record.get('phase_name') == 'device_loss_window' and record.get('observed_state_family') in {'degraded', 'disconnected', 'recovering', 'faulted'}
            for record in phase_records
        ):
            checks.append(_status('disconnect_has_runtime_evidence', 'PASS', 'disconnect count is supported by runtime-event or phase evidence.'))
        else:
            checks.append(_status('disconnect_has_runtime_evidence', 'FAIL', 'disconnect count is nonzero but no disconnect-class evidence was found in runtime rows or phase records.'))
    else:
        checks.append(_status('disconnect_has_runtime_evidence', 'PASS', 'no disconnect evidence was required for this run.'))

    recovery_count = int(reviewer_rollup.get('recovery_count', 0) or 0)
    if recovery_count > 0:
        if _contains_any(runtime_event_types, ('recovery', 'adapter_rebind', 'ready')) or any(
            record.get('phase_name') in {'recovery_window', 'post_recovery_stabilization'} and record.get('observed_state_family') == 'live_ready_healthy'
            for record in phase_records
        ):
            checks.append(_status('recovery_has_runtime_evidence', 'PASS', 'recovery count is supported by runtime-event or stabilization evidence.'))
        else:
            checks.append(_status('recovery_has_runtime_evidence', 'ADVISORY', 'recovery count is nonzero but the recent event window did not retain explicit recovery-class rows.'))
    else:
        checks.append(_status('recovery_has_runtime_evidence', 'PASS', 'no recovery evidence was required for this run.'))

    required_phase_names = {'baseline'} if startup_only else {'baseline', 'device_loss_window'}
    if not startup_only and any(record.get('phase_name') == 'recovery_window' for record in phase_records):
        required_phase_names.add('recovery_window')
    if not startup_only and any(record.get('phase_name') == 'post_recovery_stabilization' for record in phase_records):
        required_phase_names.add('post_recovery_stabilization')
    observed_phase_names = {str(record.get('phase_name')) for record in phase_records}
    missing = sorted(required_phase_names - observed_phase_names)
    if missing:
        checks.append(_status('phase_records_complete', 'FAIL', f'missing required phase records: {", ".join(missing)}.'))
    else:
        checks.append(_status('phase_records_complete', 'PASS', 'required phase records are present.'))

    if requested_mode == 'real':
        baseline_phase = next((record for record in phase_records if record.get('phase_name') == 'baseline'), None)
        if startup_only:
            if baseline_phase is None:
                checks.append(_status('real_mode_startup_baseline_present', 'FAIL', 'startup-open smoke did not retain a baseline phase record.'))
            elif baseline_phase.get('observed_state_family') == 'live_ready_healthy':
                checks.append(_status('real_mode_startup_baseline_present', 'PASS', 'startup-open smoke reached a healthy live baseline posture.'))
            else:
                checks.append(_status('real_mode_startup_baseline_present', 'FAIL', 'startup-open smoke never reached the healthy live baseline posture.'))
            if _contains_any(runtime_event_types, ('startup_open', 'device_startup_open', 'backend_init_failed', 'backend_reopen_failed')):
                checks.append(_status('startup_open_has_runtime_evidence', 'PASS', 'startup-open run retained startup/open-class runtime evidence.'))
            elif startup_open_confirmed:
                checks.append(
                    _status(
                        'startup_open_has_runtime_evidence',
                        'PASS',
                        'startup-open evidence is confirmed by adapter startup-open success counters even though explicit startup/open rows did not remain in the recent runtime-event window.',
                    )
                )
            elif startup_open_attempts > 0:
                checks.append(
                    _status(
                        'startup_open_has_runtime_evidence',
                        'ADVISORY',
                        'startup-open was attempted, but neither explicit startup/open runtime rows nor a successful startup-open counter were retained for the final review surface.',
                    )
                )
            else:
                checks.append(_status('startup_open_has_runtime_evidence', 'ADVISORY', 'startup-open run did not retain explicit startup/open-class runtime rows in the recent event window.'))
        else:
            disconnect_phase = next((record for record in phase_records if record.get('phase_name') == 'device_loss_window'), None)
            if disconnect_phase is None:
                checks.append(_status('real_mode_disconnect_observed', 'FAIL', 'real hardware mode requested a disconnect window but no disconnect phase record exists.'))
            elif disconnect_phase.get('observed_state_family') in {'degraded', 'disconnected', 'recovering', 'faulted'} or disconnect_count > 0:
                checks.append(_status('real_mode_disconnect_observed', 'PASS', 'real hardware disconnect window produced an observable disturbance.'))
            else:
                checks.append(_status('real_mode_disconnect_observed', 'FAIL', 'real hardware disconnect window never left the nominal live family.'))

            stabilization_phase = next((record for record in phase_records if record.get('phase_name') == 'post_recovery_stabilization'), None)
            if stabilization_phase is None:
                checks.append(_status('real_mode_stabilization_observed', 'ADVISORY', 'real hardware run did not include a stabilization phase.'))
            elif stabilization_phase.get('observed_state_family') == 'live_ready_healthy':
                checks.append(_status('real_mode_stabilization_observed', 'PASS', 'real hardware run returned to a healthy live posture during stabilization.'))
            else:
                checks.append(_status('real_mode_stabilization_observed', 'FAIL', 'real hardware stabilization did not return to the healthy live family.'))
    else:
        checks.append(_status('simulated_mode_note', 'PASS', 'simulated mode permits observation-only disconnect/recovery phases without requiring a physical disturbance.'))

    fail_count = sum(1 for check in checks if check['status'] == 'FAIL')
    advisory_count = sum(1 for check in checks if check['status'] == 'ADVISORY')
    verdict = 'FAIL' if fail_count else ('PASS WITH ADVISORIES' if advisory_count else 'PASS')
    return {
        'verdict': verdict,
        'summary': (
            'Runtime evidence consistency checks failed.'
            if verdict == 'FAIL'
            else ('Runtime evidence consistency passed with advisories.' if verdict == 'PASS WITH ADVISORIES' else 'Runtime evidence consistency checks passed.')
        ),
        'check_count': len(checks),
        'fail_count': fail_count,
        'advisory_count': advisory_count,
        'checks': checks,
    }


def _load_payload(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate the semantic consistency of a U6 field-validation diagnostics bundle.')
    parser.add_argument('--diagnostics-json', required=True)
    parser.add_argument('--report-json', default='')
    args = parser.parse_args()

    diagnostics_path = Path(args.diagnostics_json)
    if not diagnostics_path.is_absolute():
        diagnostics_path = (Path.cwd() / diagnostics_path).resolve()
    payload = _load_payload(diagnostics_path)
    verdict = evaluate_runtime_evidence_consistency(
        session_metadata=dict(payload.get('session_metadata', {})),
        phase_records=list(payload.get('phase_records', [])),
        operator_events=list(payload.get('operator_events', [])),
        final_review_bundle=dict(payload.get('final_review_bundle', {})),
    )
    if args.report_json:
        report_path = Path(args.report_json)
        if not report_path.is_absolute():
            report_path = (Path.cwd() / report_path).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(verdict, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(json.dumps(verdict, indent=2, sort_keys=True))
    return 0 if verdict['verdict'] != 'FAIL' else 1


if __name__ == '__main__':
    raise SystemExit(main())
