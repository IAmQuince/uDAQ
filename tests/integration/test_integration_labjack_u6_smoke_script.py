from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-013',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-007'],
    'checks_invariants': ['UDQ-INV-TIME-001', 'UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'labjack U6 smoke path in simulated mode',
}
pytestmark = pytest.mark.integration


def test_labjack_u6_smoke_script_runs_in_simulated_mode():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.dev.run_labjack_u6_smoke', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'labjack-u6-smoke:' in result.stdout
    assert 'hardware_mode=simulated' in result.stdout
    assert 'variable_total=4' in result.stdout
