from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._time import timestamp_slug


def inventory(root: Path) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob('*')):
        if path.is_dir():
            continue
        rows.append({'path': str(path.relative_to(root)), 'size_bytes': path.stat().st_size})
    return {'generated_at': timestamp_slug(), 'rows': rows}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_REPO_INVENTORY__2026-03-21_235959.json')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    payload = inventory(root)
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
