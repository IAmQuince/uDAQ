from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._registry_paths import ACTIVE_REGISTRIES
from tools._time import timestamp_slug


SCHEMA_PATHS = (
    ACTIVE_REGISTRIES.requirement_json,
    ACTIVE_REGISTRIES.execution_contract_json,
    ACTIVE_REGISTRIES.decision_log_json,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_SCHEMA_INVENTORY__2026-03-21_235959.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    rows = []
    for rel in SCHEMA_PATHS:
        path = root / rel
        rows.append({'path': rel, 'exists': path.exists(), 'size_bytes': 0 if not path.exists() else path.stat().st_size})
    payload = {'generated_at': timestamp_slug(), 'rows': rows}
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
