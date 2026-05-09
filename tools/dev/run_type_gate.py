from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    if importlib.util.find_spec('mypy') is None:
        if args.strict:
            print('mypy is not installed', file=sys.stderr)
            return 2
        print('skipping mypy because it is not installed')
        return 0
    result = subprocess.run([sys.executable, '-m', 'mypy', 'src', 'tests', 'tools'], cwd=root)
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
