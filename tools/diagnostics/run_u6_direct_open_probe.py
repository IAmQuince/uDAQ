from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def _date_prefix() -> str:
    return datetime.now(timezone.utc).strftime('%Y%m%d')


def _default_run_stem() -> str:
    return f'{_date_prefix()}_04_real-u6-direct-open-probe'


def _write_text(path: Path, lines: list[str]) -> None:
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a minimal direct-open probe against a real LabJack U6 using the Python driver stack.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-dir', default='proof/field_tests')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--run-stem', default='')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq_labjack.real_u6 import run_real_u6_direct_open_probe

    output_root = (package_root / args.output_dir) if not Path(args.output_dir).is_absolute() else Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)
    run_stem = args.run_stem.strip() or _default_run_stem()
    bundle_dir = output_root / run_stem
    bundle_dir.mkdir(parents=True, exist_ok=True)

    requested_serial = None if args.serial_number == 'AUTO' else args.serial_number
    probe = run_real_u6_direct_open_probe(requested_serial_number=requested_serial, perform_ain0_read=True)
    payload = {
        'generated_at_utc': datetime.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'run_stem': run_stem,
        'requested_serial_number': args.serial_number,
        'probe': probe.as_dict(),
    }

    report_json = bundle_dir / f'{run_stem}__report.json'
    report_txt = bundle_dir / f'{run_stem}__report.txt'
    start_here = bundle_dir / f'{run_stem}__start-here.txt'
    manifest_json = bundle_dir / f'{run_stem}__artifact-manifest.json'
    manifest_txt = bundle_dir / f'{run_stem}__artifact-manifest.txt'

    report_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    report_lines = [
        'UDQ Real U6 Direct-Open Probe',
        '=============================',
        f'generated_at_utc: {payload["generated_at_utc"]}',
        f'run_stem: {run_stem}',
        f'requested_serial_number: {args.serial_number}',
        f'success: {probe.success}',
        f'resolved_serial_number: {probe.resolved_serial_number}',
        f'open_strategy: {probe.open_strategy}',
        f'open_stage: {probe.open_stage}',
        f'ain0_value: {probe.ain0_value}',
        f'error_type: {probe.error_type}',
        f'error_message: {probe.error_message}',
        '',
        'Detail rows',
        '-----------',
    ]
    if probe.detail_rows:
        for row in probe.detail_rows:
            report_lines.append(json.dumps(dict(row), sort_keys=True))
    else:
        report_lines.append('- none')
    _write_text(report_txt, report_lines)

    start_here_lines = [
        'UDQ Real U6 Direct-Open Probe — Start Here',
        '==========================================',
        f'success: {probe.success}',
        f'resolved_serial_number: {probe.resolved_serial_number}',
        f'open_strategy: {probe.open_strategy}',
        f'open_stage: {probe.open_stage}',
        f'ain0_value: {probe.ain0_value}',
        f'error_message: {probe.error_message}',
        '',
        f'Open next: {report_txt.name}',
        f'JSON report: {report_json.name}',
    ]
    _write_text(start_here, start_here_lines)

    artifacts = []
    for label, path in [
        ('start_here', start_here),
        ('report_json', report_json),
        ('report_text', report_txt),
    ]:
        data = path.read_bytes()
        artifacts.append({'label': label, 'relative_path': path.relative_to(bundle_dir).as_posix(), 'bytes': len(data)})
    manifest = {'bundle_dir': str(bundle_dir), 'artifact_count': len(artifacts), 'artifacts': artifacts}
    manifest_json.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    _write_text(manifest_txt, [
        'UDQ Real U6 Direct-Open Probe — Artifact Manifest',
        '===============================================',
        f'bundle_dir: {bundle_dir}',
        f'artifact_count: {len(artifacts)}',
        '',
        *[f"- {row['label']}: {row['relative_path']} ({row['bytes']} bytes)" for row in artifacts],
    ])
    print(f'udq-u6-direct-open-probe: bundle written: {bundle_dir}')
    print(f'  success: {probe.success}')
    print(f'  resolved_serial_number: {probe.resolved_serial_number}')
    print(f'  open_strategy: {probe.open_strategy}')
    print(f'  open_stage: {probe.open_stage}')
    return 0 if probe.success else 1


if __name__ == '__main__':
    raise SystemExit(main())
