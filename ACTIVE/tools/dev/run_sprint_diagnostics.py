from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _add_src_to_path(package_root: Path) -> None:
    active_root = package_root if (package_root / 'src').is_dir() else package_root / 'ACTIVE'
    src_root = active_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def main() -> int:
    parser = argparse.ArgumentParser(description='Run UniversalDAQ Sprint 1 sandbox mapping diagnostics.')
    parser.add_argument('--package-root', default='.', help='Package root or ACTIVE directory. Defaults to current directory.')
    parser.add_argument('--acceptance-only', action='store_true', help='Run the acceptance suite without exporting a bundle.')
    args = parser.parse_args()
    raw_root = Path(args.package_root).resolve()
    _add_src_to_path(raw_root)

    from universaldaq.testing import export_diagnostic_bundle, package_root_from, run_sprint_acceptance_suite

    root = package_root_from(raw_root)
    result = run_sprint_acceptance_suite(package_root=root) if args.acceptance_only else export_diagnostic_bundle(package_root=root)
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    return 0 if result.passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
