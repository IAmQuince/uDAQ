from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--scenario-id', default='logic_control_demo')
    parser.add_argument('--diagnostics-path', default='')
    parser.add_argument('--bench-mode', action='store_true')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.qt_shell import launch_visible_operator_shell

    return launch_visible_operator_shell(
        initial_scenario_id=args.scenario_id,
        diagnostics_path=args.diagnostics_path or None,
        bench_mode=args.bench_mode,
    )


if __name__ == '__main__':
    raise SystemExit(main())
