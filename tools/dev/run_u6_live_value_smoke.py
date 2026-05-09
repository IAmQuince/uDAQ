from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a bounded UniversalDAQ LabJack U6 live-value smoke test.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--summary', default='proof/U6_LIVE_SUMMARY.txt')
    parser.add_argument('--journal', default='proof/U6_LIVE_JOURNAL.jsonl')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--real-hardware', action='store_true')
    parser.add_argument('--cycles', type=int, default=12)
    parser.add_argument('--reconnect-test', action='store_true')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    summary_path = (package_root / args.summary).resolve() if not Path(args.summary).is_absolute() else Path(args.summary)
    journal_path = (package_root / args.journal).resolve() if not Path(args.journal).is_absolute() else Path(args.journal)
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from tools.dev._u6_field_test_support import snapshot_active_adapter
    from tools.dev._u6_live_support import (
        bootstrap_controller,
        build_services,
        install_labjack_support_pack,
        prepare_u6_live_value_slice,
        run_poll_cycles,
    )
    from universaldaq.common import as_event_time

    lines: list[str] = []
    exit_code = 0
    try:
        services = build_services(journal_path=journal_path)
        install_labjack_support_pack(
            services,
            real_hardware=args.real_hardware,
            serial_number=None if args.serial_number == 'AUTO' else args.serial_number,
            simulated_serial_number='470155',
        )
        controller = bootstrap_controller(services=services, profile_id='PROF-U6-LIVE', actor_id='u6-live')
        prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
        run_poll_cycles(prepared.controller, timestamp_start=25, cycles=args.cycles)
        if args.reconnect_test:
            prepared.controller.mark_active_device_disconnected(timestamp=as_event_time(1000))
            prepared.controller.reconnect_active_device(timestamp=as_event_time(1001))
            run_poll_cycles(prepared.controller, timestamp_start=1002, cycles=4)
        bundle = prepared.controller.lifecycle_review_bundle()
        adapter_status = snapshot_active_adapter(prepared.controller)
        summary_payload = {
            'active_adapter_id': prepared.active_adapter_id,
            'phase': prepared.controller.session.ui_session.device_lifecycle_phase.value,
            'signal_count': len(prepared.signal_ids),
            'variable_count': len(prepared.variable_ids),
            'runtime_status': bundle['runtime_status'],
            'adapter_status': adapter_status,
            'event_alarm_summary': bundle['event_alarm_summary'],
            'active_alarm_rows': bundle['active_alarm_rows'],
            'recent_event_rows': bundle['recent_event_rows'],
            'incremental_runtime_summary': bundle['incremental_runtime_summary'],
            'variable_snapshot_rows': bundle['variable_snapshot_rows'],
            'runtime_variable_rows': bundle['runtime_variable_rows'],
            'reconnect_test': args.reconnect_test,
        }
        lines.extend(['UDQ U6 Live Value Smoke', '=======================', json.dumps(summary_payload, indent=2, sort_keys=True)])
    except Exception as exc:
        exit_code = 2
        lines.extend(['ERROR', '-----', str(exc), '', traceback.format_exc()])

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'udq-u6-live-value-smoke: wrote {summary_path}')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
