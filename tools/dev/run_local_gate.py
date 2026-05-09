from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--strict-dev-tools', action='store_true')
    args = parser.parse_args()

    root = Path(args.package_root).resolve()
    run([sys.executable, '-m', 'tools.audit.run_master_audit', '--package-root', str(root), '--profile', 'package-normalization'], cwd=root)
    run([sys.executable, '-m', 'tools.governance.validate_document_impact', '--package-root', str(root)], cwd=root)
    run([sys.executable, '-m', 'tools.governance.validate_package_entry_surfaces', '--package-root', str(root)], cwd=root)
    run([sys.executable, '-m', 'tools.governance.validate_readme_control', '--package-root', str(root)], cwd=root)
    run([sys.executable, '-m', 'tools.governance.validate_document_debt', '--package-root', str(root)], cwd=root)
    run([sys.executable, '-m', 'tools.package_build.validate_windows_path_budget', '--package-root', str(root), '--delivery-root', 'udq_s02b_r01'], cwd=root)
    run([sys.executable, '-m', 'tools.dev.run_shell_smoke', '--package-root', str(root)], cwd=root)

    dev_commands = [
        ('ruff', [sys.executable, '-m', 'ruff', 'check', '.']),
        ('ruff', [sys.executable, '-m', 'ruff', 'format', '--check', '.']),
        ('mypy', [sys.executable, '-m', 'mypy', 'src', 'tests', 'tools']),
    ]
    for module_name, cmd in dev_commands:
        if module_available(module_name):
            run(cmd, cwd=root)
        elif args.strict_dev_tools:
            print(f'missing required dev tool: {module_name}', file=sys.stderr)
            return 2
        else:
            print(f'skipping optional dev tool because it is not installed: {module_name}')

    run(['pytest', '-q', '-p', 'no:cacheprovider'], cwd=root)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
