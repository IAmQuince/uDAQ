from __future__ import annotations

import argparse
import fnmatch
import zipfile
from pathlib import Path

EXCLUDE_PATTERNS = [
    '.pytest_cache/*',
    '.pytest_cache/**',
    '__pycache__/*',
    '__pycache__/**',
    '*.pyc',
    '*.pyo',
    '.mypy_cache/*',
    '.mypy_cache/**',
    '.ruff_cache/*',
    '.ruff_cache/**',
    '*.zip',
]
DEFAULT_WINDOWS_ROOT_PREFIX = r'C:\Users\user\Documents\Code\uDAQ\QUAR'
DEFAULT_MAX_WINDOWS_FULL_PATH = 230


def is_excluded(relpath: str) -> bool:
    if relpath.startswith('proof/acceptance/') and '/runtime/' in relpath:
        return True
    return any(fnmatch.fnmatch(relpath, pattern) for pattern in EXCLUDE_PATTERNS)


def included_files(root: Path) -> list[Path]:
    rows: list[Path] = []
    for path in sorted(root.rglob('*')):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root))
        if is_excluded(rel):
            continue
        rows.append(path)
    return rows


def validate_windows_path_budget(
    *,
    root: Path,
    delivery_root: str,
    windows_root_prefix: str = DEFAULT_WINDOWS_ROOT_PREFIX,
    max_full_path: int = DEFAULT_MAX_WINDOWS_FULL_PATH,
) -> tuple[bool, list[str]]:
    findings: list[str] = []
    for path in included_files(root):
        rel = str(path.relative_to(root)).replace('/', '\\')
        full = f"{windows_root_prefix}\\{delivery_root}\\{rel}"
        if len(full) > max_full_path:
            findings.append(f'{len(full)}::{full}')
    findings.sort(reverse=True)
    return not findings, findings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='universaldaq_precode_package.zip')
    parser.add_argument('--delivery-root', default='udq_pkg')
    parser.add_argument('--windows-root-prefix', default=DEFAULT_WINDOWS_ROOT_PREFIX)
    parser.add_argument('--max-windows-full-path', type=int, default=DEFAULT_MAX_WINDOWS_FULL_PATH)
    parser.add_argument('--skip-path-budget-check', action='store_true')
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    output = Path(args.output).resolve()
    if not args.skip_path_budget_check:
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
            return 2
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for path in included_files(root):
            rel = str(path.relative_to(root))
            zf.write(path, arcname=f'{args.delivery_root}/{rel}')
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
