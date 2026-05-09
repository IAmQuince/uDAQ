from __future__ import annotations

from pathlib import Path

import pytest

from universaldaq.ui.bench_plan import build_desktop_bench_plan, render_desktop_bench_runbook


TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-061',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-AUD-001', 'UDQ-REQ-QUAL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'desktop bench plan exposes runbook and diagnostics artifact targets',
}
pytestmark = pytest.mark.contract


def test_desktop_bench_plan_includes_runbook_and_diagnostics_targets(tmp_path: Path) -> None:
    package_root = tmp_path / 'pkg'
    package_root.mkdir()
    diagnostics_path = package_root / 'proof' / 'bundles' / 'desktop_bench.json'

    plan = build_desktop_bench_plan(package_root=package_root, diagnostics_path=diagnostics_path)
    text = render_desktop_bench_runbook(plan)

    assert plan.diagnostics_path.endswith('desktop_bench.json')
    assert plan.runbook_path.endswith('desktop_bench.md')
    assert 'tools.ui.run_desktop_bench_harness' in plan.launch_command
    assert 'diagnostics will be written on shell exit' not in text.lower()
    assert 'Close the shell normally so the desktop bench diagnostics artifact is written automatically.' in text
    assert str(diagnostics_path) in text
