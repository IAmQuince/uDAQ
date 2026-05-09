from __future__ import annotations

import argparse
from pathlib import Path

from tools._registry_paths import active_registry_path
from tools._shared import load_json, parse_assignment


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    valid = {row['requirement_id'] for row in load_json(active_registry_path(root, 'requirement_json'))['requirements']}
    failures: list[str] = []
    for path in sorted((root / 'tests').rglob('test_*.py')):
        decl = parse_assignment(path, 'TEST_DECLARATION')
        missing = sorted(set(decl['verifies_requirements']) - valid)
        if missing:
            failures.append(f'{path.relative_to(root)} -> {missing}')
    if failures:
        print('\n'.join(failures))
        return 1
    print('OK')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
