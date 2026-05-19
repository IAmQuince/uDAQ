from __future__ import annotations

import argparse
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json
from tools._time import timestamp_slug


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='audit_reports/active/UDQ_GOVERNANCE_STATUS__2026-03-21_235959.md')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    gov = load_json(active_registry_path(root, 'governance_model_json'))
    out = root / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        '\n'.join([
            '# Governance Snapshot',
            '',
            f'- generated_at: {timestamp_slug()}',
            f"- package_id: {gov['package_id']}",
            f"- package_disposition: {gov['package_disposition']}",
        ])
        + '\n',
        encoding='utf-8',
    )
    print(out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
