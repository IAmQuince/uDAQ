from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._time import iso_timestamp_utc, timestamp_slug


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_SAVEPOINT_BASELINE__2026-03-21_235959.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    payload = {
        'baseline_id': f'UDQ-SAVEPOINT-{timestamp_slug()}',
        'created_at': iso_timestamp_utc(),
        'package_root': str(root),
    }
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
