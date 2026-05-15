from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--scenario-id', default='logic_control_demo')
    parser.add_argument('--diagnostics-path', default='proof/bundles/20260330_05_desktop_bench_diagnostics.json')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    diagnostics_path = Path(args.diagnostics_path)
    if not diagnostics_path.is_absolute():
        diagnostics_path = (package_root / diagnostics_path).resolve()
    diagnostics_path.parent.mkdir(parents=True, exist_ok=True)

    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.bench_plan import build_desktop_bench_plan, render_desktop_bench_runbook
    from universaldaq.ui.qt_shell import launch_visible_operator_shell

    plan = build_desktop_bench_plan(package_root=package_root, diagnostics_path=diagnostics_path)
    Path(plan.runbook_path).write_text(render_desktop_bench_runbook(plan), encoding='utf-8')

    os.environ['UNIVERSALDAQ_BENCH_MODE'] = '1'
    os.environ['UNIVERSALDAQ_SHELL_DIAGNOSTICS_PATH'] = str(diagnostics_path)
    os.environ['UNIVERSALDAQ_BENCH_RUNBOOK_PATH'] = str(plan.runbook_path)

    print(f'runbook written: {plan.runbook_path}')
    print(f'diagnostics will be written on shell exit: {diagnostics_path}')
    return launch_visible_operator_shell(
        initial_scenario_id=args.scenario_id,
        diagnostics_path=str(diagnostics_path),
        bench_mode=True,
    )


if __name__ == '__main__':
    raise SystemExit(main())
