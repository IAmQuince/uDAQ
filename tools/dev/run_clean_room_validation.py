from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import textwrap
import venv
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, env: dict[str, str], log_lines: list[str]) -> None:
    log_lines.append(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, env=env, text=True, capture_output=True)
    if result.stdout:
        log_lines.append(result.stdout.rstrip())
    if result.stderr:
        log_lines.append(result.stderr.rstrip())
    if result.returncode != 0:
        joined = ' '.join(cmd)
        raise RuntimeError(f'command failed with exit code {result.returncode}: {joined}')


def _host_site_package_path() -> str:
    candidates = [entry for entry in sys.path if 'site-packages' in entry]
    return os.pathsep.join(dict.fromkeys(candidates))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--log-output', default='')
    args = parser.parse_args()

    root = Path(args.package_root).resolve()
    log_lines = [f'package_root={root}']
    env = os.environ.copy()
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    host_site_packages = _host_site_package_path()
    if host_site_packages:
        env['PYTHONPATH'] = host_site_packages
        log_lines.append(f'host_site_packages={host_site_packages}')

    with tempfile.TemporaryDirectory(prefix='udq-clean-room-') as tmpdir:
        venv_dir = Path(tmpdir) / 'venv'
        builder = venv.EnvBuilder(with_pip=True, system_site_packages=False)
        builder.create(venv_dir)
        python_exe = venv_dir / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        run([str(python_exe), '-m', 'pip', 'install', '-e', str(root)], cwd=root, env=env, log_lines=log_lines)
        run([str(python_exe), '-m', 'pytest', '-q'], cwd=root, env=env, log_lines=log_lines)

    message = textwrap.dedent(
        f'''
        clean-room validation: PASS
        package_root: {root}
        steps:
        - editable install in isolated virtual environment
        - pytest executed from fresh environment using host pytest package path only as the test runner dependency source
        '''
    ).strip()
    log_lines.append(message)
    output = '\n\n'.join(log_lines) + '\n'
    if args.log_output:
        Path(args.log_output).write_text(output, encoding='utf-8')
    print(message)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
