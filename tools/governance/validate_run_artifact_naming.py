from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r'^\d{8}_\d{2}_[a-z0-9][a-z0-9-]*$')
FILE_RE = re.compile(r'^\d{8}_\d{2}_[a-z0-9][a-z0-9-]*(?:__[a-z0-9][a-z0-9-]*)*\.[a-z0-9]+$')


def _valid(name: str) -> bool:
    return bool(FILE_RE.fullmatch(name) if '.' in name else NAME_RE.fullmatch(name))


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate artifact names against yyyymmdd_00_description-of-run.')
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--directory', default='')
    args = parser.parse_args()

    names: list[str] = []
    if args.directory:
        directory = Path(args.directory)
        if not directory.exists():
            print(f'missing directory: {directory}', file=sys.stderr)
            return 1
        names.extend(path.name for path in directory.iterdir())
    names.extend(Path(item).name for item in args.paths)
    if not names:
        print('no artifact names provided', file=sys.stderr)
        return 1

    invalid = [name for name in names if not _valid(name)]
    if invalid:
        print('invalid artifact names:')
        for name in invalid:
            print(f' - {name}')
        return 1
    print(f'validated {len(names)} artifact name(s)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
