from __future__ import annotations

import argparse
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    rows = load_json(active_registry_path(root, 'implementation_coverage_json'))['rows']
    failures = [
        row['requirement_id']
        for row in rows
        if row['implementation_entry_status'] == 'READY_FOR_IMPLEMENTATION'
        and row['test_stub_status'] not in {'SCAFFOLDED', 'IMPLEMENTED'}
    ]
    if failures:
        print('\n'.join(failures))
        return 1
    print('first-slice readiness: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
