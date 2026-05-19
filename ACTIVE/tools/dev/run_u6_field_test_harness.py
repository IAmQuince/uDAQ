from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from time import sleep


PROMPT_PREFIX = 'udq-u6-field-validation'


def _record_operator_event(events: list[dict[str, object]], *, event_type: str, phase_name: str, timestamp: int, detail: str, source: str = 'harness') -> None:
    events.append(
        {
            'event_type': event_type,
            'phase_name': phase_name,
            'timestamp': timestamp,
            'detail': detail,
            'source': source,
        }
    )


def _prompt(message: str) -> None:
    print(f'{PROMPT_PREFIX}: {message}')
    input('Press Enter to continue... ')


def _date_prefix() -> str:
    return datetime.now().strftime('%Y%m%d')


def _default_run_stem(*, real_hardware: bool, startup_only: bool) -> str:
    prefix = _date_prefix()
    if real_hardware and startup_only:
        return f'{prefix}_01_real-u6-startup-open-smoke'
    if real_hardware:
        return f'{prefix}_02_real-u6-guided-unplug-replug-validation'
    if startup_only:
        return f'{prefix}_00_simulated-u6-startup-open-smoke'
    return f'{prefix}_00_simulated-u6-guided-validation'


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a guided UniversalDAQ LabJack U6 field-validation harness with automatic diagnostics packaging.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-dir', default='proof/field_tests')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--real-hardware', action='store_true')
    parser.add_argument('--baseline-cycles', type=int, default=6)
    parser.add_argument('--loss-cycles', type=int, default=6)
    parser.add_argument('--recovery-cycles', type=int, default=6)
    parser.add_argument('--stabilization-cycles', type=int, default=6)
    parser.add_argument('--cycle-delay-seconds', type=float, default=0.0)
    parser.add_argument('--real-cycle-delay-seconds', type=float, default=0.75)
    parser.add_argument('--reconnect-settle-seconds', type=float, default=2.0)
    parser.add_argument('--skip-recovery', action='store_true')
    parser.add_argument('--startup-smoke-only', action='store_true')
    parser.add_argument('--run-stem', default='')
    parser.add_argument('--noninteractive', action='store_true')
    parser.add_argument('--skip-preflight-direct-open-probe', action='store_true')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from tools.dev._u6_field_test_support import (
        build_phase_expectations,
        build_phase_records,
        build_preflight_report,
        capture_phase,
        load_package_identity,
        write_field_test_bundle,
    )
    from tools.dev._u6_live_support import (
        bootstrap_controller,
        build_services,
        install_labjack_support_pack,
        prepare_u6_live_value_slice,
        summarize_discovered_devices,
    )
    from universaldaq_labjack.models import LabJackProbeRow
    from universaldaq_labjack.real_u6 import build_primed_backend_factory, prime_real_u6_backend
    from tools.diagnostics.validate_runtime_evidence_consistency import evaluate_runtime_evidence_consistency

    output_root = (package_root / args.output_dir) if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    stale_artifact_count = len([path for path in output_root.iterdir() if path.is_dir()])

    requested_serial = None if args.serial_number == 'AUTO' else args.serial_number
    preflight_direct_open_probe = None
    real_probe_rows: tuple[LabJackProbeRow, ...] = ()
    auto_probe_real_hardware = args.real_hardware
    primed_backend_factory = None
    if args.real_hardware and not args.skip_preflight_direct_open_probe:
        primed_backend, probe_result = prime_real_u6_backend(requested_serial_number=requested_serial, perform_ain0_read=True)
        preflight_direct_open_probe = probe_result.as_dict()
        probe_row = probe_result.probe_row()
        if probe_row is not None:
            real_probe_rows = (
                LabJackProbeRow(
                    model=probe_row.get('model', 'U6'),
                    serial_number=probe_row['serial_number'],
                    transport=probe_row.get('transport', 'usb'),
                    firmware_version=probe_row.get('firmware_version'),
                    hardware_revision=probe_row.get('hardware_revision'),
                    connection_label=probe_row.get('connection_label'),
                    metadata={key: value for key, value in probe_row.items() if key not in {'model', 'serial_number', 'transport', 'firmware_version', 'hardware_revision', 'connection_label'}},
                ),
            )
            auto_probe_real_hardware = False
            requested_serial = probe_row['serial_number']
            if args.serial_number == 'AUTO':
                args.serial_number = probe_row['serial_number']
            if primed_backend is not None:
                primed_backend_factory = build_primed_backend_factory(primed_backend)

    journal_path = package_root / 'proof' / 'U6_FIELD_TEST_JOURNAL.jsonl'
    services = build_services(journal_path=journal_path)
    install_labjack_support_pack(
        services,
        real_hardware=args.real_hardware,
        serial_number=requested_serial,
        simulated_serial_number='470211',
        probe_rows=real_probe_rows,
        auto_probe_real_hardware=auto_probe_real_hardware,
        real_backend_factory=primed_backend_factory,
    )
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-FIELDTEST', actor_id='u6-field-test')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)

    discovered_devices = list(summarize_discovered_devices(controller))
    package_identity = load_package_identity(package_root)
    session_metadata = {
        'package_id': package_identity.get('package_id'),
        'requested_mode': 'real' if args.real_hardware else 'simulated',
        'entered_mode': 'unknown',
        'serial_number': args.serial_number,
        'active_adapter_id': prepared.active_adapter_id,
        'journal_path': str(journal_path),
        'discovered_devices': discovered_devices,
        'validation_flow': 'pending',
        'run_stem': '',
        'baseline_gate_passed': False,
        'direct_open_probe': preflight_direct_open_probe,
        'discovery_strategy': 'prevalidated_probe_rows' if real_probe_rows else ('auto_probe_real_hardware' if args.real_hardware else 'simulated_probe_rows'),
    }

    capture_clock = 100
    operator_events: list[dict[str, object]] = []
    cycle_delay_seconds = args.real_cycle_delay_seconds if args.real_hardware else args.cycle_delay_seconds
    _record_operator_event(operator_events, event_type='harness_start', phase_name='preflight', timestamp=capture_clock, detail='guided field validation started')

    captures = [
        capture_phase(
            controller=controller,
            phase_name='baseline',
            timestamp_start=capture_clock,
            poll_cycles=args.baseline_cycles,
            cycle_delay_seconds=cycle_delay_seconds,
        )
    ]
    session_metadata['entered_mode'] = captures[0].adapter_status.get('hardware_mode', 'unknown') if captures else 'unknown'
    baseline_gate_passed = bool(captures and captures[0].semantic_state_family == 'live_ready_healthy')
    session_metadata['baseline_gate_passed'] = baseline_gate_passed
    startup_only = bool(args.startup_smoke_only or not baseline_gate_passed)
    session_metadata['validation_flow'] = 'startup_open_smoke' if startup_only else 'guided_unplug_replug_validation'
    session_metadata['run_stem'] = args.run_stem.strip() or _default_run_stem(real_hardware=args.real_hardware, startup_only=startup_only)
    bundle_dir = output_root / session_metadata['run_stem']
    preflight_report = build_preflight_report(
        package_root=package_root,
        bundle_dir=bundle_dir,
        session_metadata=session_metadata,
        controller=controller,
        journal_path=journal_path,
        stale_artifact_count=stale_artifact_count,
        direct_open_probe=preflight_direct_open_probe,
    )
    capture_clock += max(args.baseline_cycles, 1) + 20

    if startup_only and not baseline_gate_passed:
        _record_operator_event(
            operator_events,
            event_type='harness_startup_gate_failed',
            phase_name='baseline',
            timestamp=capture_clock,
            detail='baseline never reached live-ready-healthy; guided unplug/replug phases skipped',
        )
    elif startup_only:
        _record_operator_event(
            operator_events,
            event_type='harness_startup_smoke_complete',
            phase_name='baseline',
            timestamp=capture_clock,
            detail='startup-open smoke completed after healthy baseline was confirmed',
        )

    interactive = args.real_hardware and not args.noninteractive
    if not startup_only:
        if interactive:
            _record_operator_event(operator_events, event_type='harness_prompt_disconnect', phase_name='device_loss_window', timestamp=capture_clock, detail='operator prompted to unplug the U6')
            _prompt('Baseline capture complete. Unplug the U6 now.')
            _record_operator_event(operator_events, event_type='operator_confirm_disconnect', phase_name='device_loss_window', timestamp=capture_clock, detail='operator confirmed disconnect window start', source='operator')
        else:
            _record_operator_event(operator_events, event_type='harness_auto_disconnect_phase', phase_name='device_loss_window', timestamp=capture_clock, detail='disconnect window started without an interactive prompt')
        captures.append(
            capture_phase(
                controller=controller,
                phase_name='device_loss_window',
                timestamp_start=capture_clock,
                poll_cycles=args.loss_cycles,
                cycle_delay_seconds=cycle_delay_seconds,
            )
        )
        capture_clock += max(args.loss_cycles, 1) + 20

        if not args.skip_recovery:
            if interactive:
                _record_operator_event(operator_events, event_type='harness_prompt_reconnect', phase_name='recovery_window', timestamp=capture_clock, detail='operator prompted to reconnect the U6')
                _prompt('Reconnect the U6 now, then give Windows a moment to re-enumerate the device before the recovery window starts.')
                _record_operator_event(operator_events, event_type='operator_confirm_reconnect', phase_name='recovery_window', timestamp=capture_clock, detail='operator confirmed recovery window start', source='operator')
            else:
                _record_operator_event(operator_events, event_type='harness_auto_recovery_phase', phase_name='recovery_window', timestamp=capture_clock, detail='recovery window started without an interactive prompt')
            if args.reconnect_settle_seconds > 0:
                _record_operator_event(operator_events, event_type='harness_reconnect_settle_wait', phase_name='recovery_window', timestamp=capture_clock, detail=f'waiting {args.reconnect_settle_seconds:.2f}s for USB/device re-enumeration before recovery polling')
                sleep(args.reconnect_settle_seconds)
            captures.append(
                capture_phase(
                    controller=controller,
                    phase_name='recovery_window',
                    timestamp_start=capture_clock,
                    poll_cycles=args.recovery_cycles,
                    cycle_delay_seconds=cycle_delay_seconds,
                )
            )
            capture_clock += max(args.recovery_cycles, 1) + 20

            _record_operator_event(operator_events, event_type='harness_stabilization_window', phase_name='post_recovery_stabilization', timestamp=capture_clock, detail='post-recovery stabilization window started')
            captures.append(
                capture_phase(
                    controller=controller,
                    phase_name='post_recovery_stabilization',
                    timestamp_start=capture_clock,
                    poll_cycles=args.stabilization_cycles,
                    cycle_delay_seconds=cycle_delay_seconds,
                )
            )
            capture_clock += max(args.stabilization_cycles, 1) + 20

    _record_operator_event(operator_events, event_type='harness_packaging', phase_name='finalization', timestamp=capture_clock, detail='diagnostic packaging started')
    final_review_bundle = controller.lifecycle_review_bundle()
    expectations = build_phase_expectations(
        requested_mode=session_metadata['requested_mode'],
        skip_recovery=args.skip_recovery,
        startup_only=startup_only,
    )
    phase_records = build_phase_records(captures=captures, expectations=expectations)
    semantic_consistency = evaluate_runtime_evidence_consistency(
        session_metadata=session_metadata,
        phase_records=phase_records,
        operator_events=operator_events,
        final_review_bundle=final_review_bundle,
    )
    bundle_paths = write_field_test_bundle(
        bundle_dir=bundle_dir,
        preflight_report=preflight_report,
        session_metadata=session_metadata,
        captures=captures,
        phase_records=phase_records,
        operator_events=operator_events,
        semantic_consistency=semantic_consistency,
        final_review_bundle=final_review_bundle,
    )
    print('udq-u6-field-validation: bundle written')
    print(f'  bundle_dir: {bundle_dir}')
    print(f"  verdict: {semantic_consistency.get('verdict')}")
    for label, path in bundle_paths.items():
        print(f'  {label}: {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
