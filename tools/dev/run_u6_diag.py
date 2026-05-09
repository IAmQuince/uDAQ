from __future__ import annotations

import argparse
import platform
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a bounded UniversalDAQ LabJack U6 diagnostic.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--out', default='proof/U6_DIAG.txt')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--real-hardware', action='store_true')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    out_path = (package_root / args.out).resolve() if not Path(args.out).is_absolute() else Path(args.out)
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from tools.dev._u6_field_test_support import snapshot_active_adapter
    from tools.dev._u6_live_support import (
        bootstrap_controller,
        build_services,
        format_key_values,
        install_labjack_support_pack,
        prepare_u6_live_value_slice,
        summarize_discovered_devices,
    )
    from universaldaq.common import as_event_time

    lines: list[str] = []
    exit_code = 0
    try:
        services = build_services(journal_path=package_root / 'proof' / 'U6_DIAG_JOURNAL.jsonl')
        install_labjack_support_pack(
            services,
            real_hardware=args.real_hardware,
            serial_number=None if args.serial_number == 'AUTO' else args.serial_number,
            simulated_serial_number='470099',
        )
        controller = bootstrap_controller(services=services, profile_id='PROF-U6-DIAG', actor_id='u6-diag')
        discovered = controller.discover_devices(timestamp=as_event_time(3))
        lines.extend(
            [
                'UDQ U6 Diagnostic',
                '=================',
                format_key_values(
                    (
                        ('package_root', package_root),
                        ('python', sys.version.replace('\n', ' ')),
                        ('platform', platform.platform()),
                        ('real_hardware', args.real_hardware),
                        ('requested_serial', args.serial_number),
                        ('core_boot_ok', True),
                        ('discovered_device_count', len(discovered)),
                    )
                ),
                '',
                'Discovered Devices',
                '------------------',
            ]
        )
        device_rows = summarize_discovered_devices(controller)
        if device_rows:
            for row in device_rows:
                lines.append(', '.join(f'{key}={value}' for key, value in row.items()))
        else:
            lines.append('none')
        lines.append('')

        prepared = prepare_u6_live_value_slice(controller, timestamp_start=10)
        bundle = prepared.controller.lifecycle_review_bundle()
        adapter_status = snapshot_active_adapter(prepared.controller)
        lines.extend(
            [
                'Live Slice Review',
                '-----------------',
                format_key_values(
                    (
                        ('active_adapter_id', prepared.active_adapter_id),
                        ('signal_count', len(prepared.signal_ids)),
                        ('variable_count', len(prepared.variable_ids)),
                        ('phase', prepared.controller.session.ui_session.device_lifecycle_phase.value),
                        ('projected_point_count', bundle['lifecycle_summary']['projected_point_count']),
                        ('published_signal_count', bundle['lifecycle_summary']['published_signal_count']),
                        ('recent_runtime_variables', len(bundle['runtime_variable_rows'])),
                        ('journal_path', bundle['runtime_status']['journal_path']),
                    )
                ),
                '',
                'Variable Snapshots',
                '------------------',
            ]
        )
        lines.extend(['', 'Adapter Status Snapshot', '----------------------'])
        for key, value in sorted(adapter_status.items()):
            lines.append(f'{key}: {value}')
        for row in bundle['variable_snapshot_rows']:
            lines.append(
                ', '.join(
                    [
                        f"variable_id={row['variable_id']}",
                        f"value={row['value']}",
                        f"quality={row['quality']}",
                        f"state={row['state']}",
                        f"timestamp={row['timestamp']}",
                        f"deps={row['dependency_values']}",
                    ]
                )
            )
        lines.extend(['', 'Runtime Status', '--------------'])
        for key, value in sorted(bundle['runtime_status'].items()):
            lines.append(f'{key}: {value}')
        lines.extend(['', 'Command Summary', '---------------'])
        for key, value in sorted(bundle['command_summary'].items()):
            lines.append(f'{key}: {value}')
        lines.extend(['', 'Recent Command Rows', '-------------------'])
        if bundle['recent_command_rows']:
            for row in bundle['recent_command_rows']:
                lines.append(', '.join(f'{key}={value}' for key, value in row.items()))
        else:
            lines.append('none')
        lines.extend(['', 'Incremental Runtime Summary', '---------------------------'])
        for key, value in sorted(bundle['incremental_runtime_summary'].items()):
            lines.append(f'{key}: {value}')
    except Exception as exc:
        exit_code = 2
        lines.extend(['ERROR', '-----', str(exc), '', traceback.format_exc()])

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'udq-u6-diag: wrote {out_path}')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
