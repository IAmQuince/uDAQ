from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-008',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-004'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'workspace design diagnostic reports task-first primary surfaces and graph defaults',
}
pytestmark = pytest.mark.smoke


def test_workspace_design_inventory_runs() -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_workspace_design_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    ids = {row['workspace_id'] for row in payload['workspace_task_maps']}
    assert {'operate', 'logic_designer', 'system', 'session_review'}.issubset(ids)
