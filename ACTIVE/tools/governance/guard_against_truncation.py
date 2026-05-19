from __future__ import annotations

import argparse
import json
from pathlib import Path

TRACKED_SUFFIXES = {'.py', '.md', '.txt', '.yaml', '.yml', '.json', '.csv', '.bat'}


def _line_count(data: bytes) -> int:
    if not data:
        return 0
    return data.count(b'\n') + (0 if data.endswith(b'\n') else 1)


def analyze(*, package_root: Path, snapshot_path: Path, shrink_threshold: float = 0.25) -> dict[str, object]:
    snapshot = json.loads(snapshot_path.read_text(encoding='utf-8'))
    findings: list[dict[str, object]] = []
    checked = 0
    for entry in snapshot.get('entries', []):
        rel = str(entry['path'])
        current = package_root / rel
        if current.suffix.lower() not in TRACKED_SUFFIXES:
            continue
        checked += 1
        if not current.exists():
            findings.append({'path': rel, 'severity': 'error', 'code': 'missing_file', 'message': 'tracked file is missing from working tree'})
            continue
        data = current.read_bytes()
        current_bytes = len(data)
        current_lines = _line_count(data)
        baseline_bytes = int(entry['bytes'])
        baseline_lines = int(entry['lines'])
        if current_bytes == 0:
            findings.append({'path': rel, 'severity': 'error', 'code': 'zero_byte', 'message': 'tracked file is now zero bytes'})
            continue
        if bool(entry.get('ends_with_newline', False)) and not data.endswith(b'\n'):
            findings.append({'path': rel, 'severity': 'warning', 'code': 'missing_terminal_newline', 'message': 'tracked file lost its terminal newline relative to baseline'})
        if baseline_bytes > 0:
            shrink_ratio = (baseline_bytes - current_bytes) / baseline_bytes
            if shrink_ratio > shrink_threshold and current_lines < baseline_lines:
                findings.append({
                    'path': rel,
                    'severity': 'warning',
                    'code': 'suspicious_shrink',
                    'message': 'tracked file shrank materially relative to baseline snapshot',
                    'baseline_bytes': baseline_bytes,
                    'current_bytes': current_bytes,
                    'baseline_lines': baseline_lines,
                    'current_lines': current_lines,
                    'shrink_ratio': round(shrink_ratio, 4),
                })
    return {
        'checked_count': checked,
        'finding_count': len(findings),
        'findings': findings,
        'shrink_threshold': shrink_threshold,
        'snapshot_path': str(snapshot_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Compare the working tree against a baseline file snapshot and flag suspicious shrinkage or missing tracked files.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--snapshot', required=True)
    parser.add_argument('--report', default=None)
    parser.add_argument('--shrink-threshold', type=float, default=0.25)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    snapshot_path = Path(args.snapshot)
    if not snapshot_path.is_absolute():
        snapshot_path = (package_root / snapshot_path).resolve()
    payload = analyze(package_root=package_root, snapshot_path=snapshot_path, shrink_threshold=args.shrink_threshold)
    report_text = json.dumps(payload, indent=2, sort_keys=True) + '\n'
    if args.report:
        report_path = Path(args.report)
        if not report_path.is_absolute():
            report_path = package_root / report_path
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report_text, encoding='utf-8')
    print(report_text, end='')
    return 0 if payload['finding_count'] == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
