from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Summarize a sprint JSONL timing ledger by phase and command label.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--ledger-jsonl', default='audit_reports/active/SPRINT_TIME_LEDGER__20260330_10.jsonl')
    parser.add_argument('--output-md', default='audit_reports/active/SPRINT_TIME_SUMMARY__20260330_10.md')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    ledger = root / args.ledger_jsonl
    rows = []
    if ledger.exists():
        for line in ledger.read_text(encoding='utf-8').splitlines():
            if line.strip():
                rows.append(json.loads(line))
    phase_seconds: dict[str, float] = defaultdict(float)
    failures = []
    for row in rows:
        phase = str(row.get('phase', 'UNCLASSIFIED'))
        duration = float(row.get('duration_seconds', 0.0))
        phase_seconds[phase] += duration
        if int(row.get('exit_code', 0)) != 0:
            failures.append(row)
    total = sum(phase_seconds.values())
    lines = [
        '# Sprint Time Summary — 20260330_10',
        '',
        f'- instrumented_command_count: `{len(rows)}`',
        f'- total_instrumented_seconds: `{round(total, 3)}`',
        '',
        '## Phase totals',
    ]
    for phase, seconds in sorted(phase_seconds.items(), key=lambda item: item[0]):
        pct = 0.0 if total == 0 else seconds * 100.0 / total
        lines.append(f'- `{phase}`: `{round(seconds, 3)}s` ({pct:0.1f}%)')
    lines.extend(['', '## Command rows'])
    for row in rows:
        lines.append(f"- `{row.get('phase')}` / `{row.get('label')}`: `{row.get('duration_seconds')}s`, exit `{row.get('exit_code')}`")
    lines.extend(['', '## Non-zero command exits'])
    if failures:
        for row in failures:
            lines.append(f"- `{row.get('label')}` exited `{row.get('exit_code')}`")
    else:
        lines.append('- None recorded.')
    out = root / args.output_md
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
