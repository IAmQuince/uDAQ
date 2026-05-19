from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_TRACEABILITY_GAPS__2026-03-21_235959.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    coverage = load_json(active_registry_path(root, 'implementation_coverage_json'))
    rows = [row for row in coverage['rows'] if row.get('implementation_entry_status') != 'READY_FOR_IMPLEMENTATION']
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'rows': rows}, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
