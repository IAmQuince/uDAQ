from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-011',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime performance inventory diagnostic snapshot',
}
pytestmark = pytest.mark.smoke


def test_runtime_performance_inventory_runs_and_emits_metrics():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_runtime_performance_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert 'runtime_performance' in payload
    assert 'counters' in payload['runtime_performance']
    assert payload['object_counts']['variable_count'] >= 1
    assert payload['authorization_allowed'] is True
