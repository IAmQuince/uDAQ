from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _append_jsonl(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(payload, sort_keys=True) + '\n')


def _append_markdown(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text('# Sprint Time Ledger\n\n', encoding='utf-8')
    lines = [
        f"## {payload['label']}",
        '',
        f"- phase: `{payload['phase']}`",
        f"- start_utc: `{payload['start_utc']}`",
        f"- end_utc: `{payload['end_utc']}`",
        f"- duration_seconds: `{payload['duration_seconds']}`",
        f"- exit_code: `{payload['exit_code']}`",
        f"- command: `{' '.join(payload['command'])}`",
    ]
    if payload.get('notes'):
        lines.append(f"- notes: {payload['notes']}")
    lines.append('')
    path.write_text(path.read_text(encoding='utf-8') + '\n'.join(lines) + '\n', encoding='utf-8')


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a command and append timing data to sprint ledgers.')
    parser.add_argument('--label', required=True)
    parser.add_argument('--phase', default='UNCLASSIFIED')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--ledger-jsonl', default='audit_reports/active/SPRINT_TIME_LEDGER__20260330_10.jsonl')
    parser.add_argument('--ledger-md', default='audit_reports/active/SPRINT_TIME_LEDGER__20260330_10.md')
    parser.add_argument('--notes', default='')
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = list(args.command)
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        print('timed-command: missing command', file=sys.stderr)
        return 2
    root = Path(args.package_root).resolve()
    start = _utc_now()
    t0 = time.perf_counter()
    completed = subprocess.run(command, cwd=str(root), text=True)
    duration = round(time.perf_counter() - t0, 3)
    end = _utc_now()
    payload: dict[str, object] = {
        'label': args.label,
        'phase': args.phase,
        'package_root': str(root),
        'start_utc': start,
        'end_utc': end,
        'duration_seconds': duration,
        'exit_code': int(completed.returncode),
        'command': command,
        'notes': args.notes,
    }
    _append_jsonl(root / args.ledger_jsonl, payload)
    _append_markdown(root / args.ledger_md, payload)
    print(f"timed-command: {args.label}: exit={completed.returncode} duration={duration}s")
    return int(completed.returncode)


if __name__ == '__main__':
    raise SystemExit(main())
