from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-012',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle transition history diagnostic snapshot',
}
pytestmark = pytest.mark.smoke


def test_lifecycle_transition_history_diagnostic_runs_and_emits_trace():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_lifecycle_transition_history'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert len(payload['transition_trace']) >= 4
    assert payload['phase'] == 'live'
    assert 'lifecycle.transition.current_phase' in payload['incremental_runtime_summary']
