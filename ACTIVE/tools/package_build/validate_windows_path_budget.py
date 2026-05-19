from __future__ import annotations

import argparse
from pathlib import Path

from .build_precode_package import (
    DEFAULT_MAX_WINDOWS_FULL_PATH,
    DEFAULT_WINDOWS_ROOT_PREFIX,
    validate_windows_path_budget,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--delivery-root', default='udq_pkg')
    parser.add_argument('--windows-root-prefix', default=DEFAULT_WINDOWS_ROOT_PREFIX)
    parser.add_argument('--max-windows-full-path', type=int, default=DEFAULT_MAX_WINDOWS_FULL_PATH)
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    okay, findings = validate_windows_path_budget(
        root=root,
        delivery_root=args.delivery_root,
        windows_root_prefix=args.windows_root_prefix,
        max_full_path=args.max_windows_full_path,
    )
    if not okay:
        print('windows-path-budget: FAIL')
        for item in findings[:20]:
            print(item)
        return 1
    print('windows-path-budget: PASS')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
