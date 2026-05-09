from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DesktopBenchPlan:
    package_root: str
    diagnostics_path: str
    runbook_path: str
    launch_command: str
    checklist: tuple[str, ...]


def build_desktop_bench_plan(*, package_root: Path, diagnostics_path: Path) -> DesktopBenchPlan:
    package_root = package_root.resolve()
    diagnostics_path = diagnostics_path.resolve()
    runbook_path = diagnostics_path.with_suffix('.md')
    launch_command = (
        f'python -m tools.ui.run_desktop_bench_harness '
        f'--package-root "{package_root}" '
        f'--diagnostics-path "{diagnostics_path}"'
    )
    checklist = (
        'Launch the shell and confirm it fits entirely within the usable screen.',
        'Resize the left explorer, center region, right control column, and bottom events region.',
        'Switch to Logic Designer and confirm the graph enters Compact PiP mode.',
        'Drag and resize the PiP graph; then switch back to Operate and confirm Primary graph mode returns.',
        'Use Restore Default Layout, Reset Panel Sizes, and Reset Layout Cache; confirm each behaves distinctly.',
        'Inspect the System workspace and confirm Mapping Drafts remain explicitly non-authoritative.',
        'Close the shell normally so the desktop bench diagnostics artifact is written automatically.',
    )
    return DesktopBenchPlan(
        package_root=str(package_root),
        diagnostics_path=str(diagnostics_path),
        runbook_path=str(runbook_path),
        launch_command=launch_command,
        checklist=checklist,
    )


def render_desktop_bench_runbook(plan: DesktopBenchPlan) -> str:
    lines = [
        '# UniversalDAQ Desktop Bench Runbook',
        '',
        f'- Package root: `{plan.package_root}`',
        f'- Diagnostics output: `{plan.diagnostics_path}`',
        f'- Launch command: `{plan.launch_command}`',
        '',
        '## Checklist',
    ]
    lines.extend(f'{idx}. {item}' for idx, item in enumerate(plan.checklist, start=1))
    lines.extend(
        [
            '',
            '## Notes',
            '- This harness is intended for a real desktop with the optional UI dependencies installed.',
            '- The diagnostics file is written on normal shell exit and can be pasted back for troubleshooting.',
            '- This bench run does not make the shell authoritative for backend-applied mappings; it verifies shell behavior and surfaces authority boundaries.',
        ]
    )
    return '\n'.join(lines) + '\n'


__all__ = ['DesktopBenchPlan', 'build_desktop_bench_plan', 'render_desktop_bench_runbook']
