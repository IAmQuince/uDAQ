from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-010',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle inventory diagnostic snapshot',
}
pytestmark = pytest.mark.smoke


def test_lifecycle_inventory_diagnostic_runs_and_emits_device_and_variable_sections():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_lifecycle_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert 'device_records' in payload
    assert 'signal_bindings' in payload
    assert 'variable_definitions' in payload
