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
    'expected_proof_output': 'first-signal inventory diagnostic snapshot',
}
pytestmark = pytest.mark.smoke


def test_first_signal_inventory_diagnostic_runs_and_emits_trace_preview():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_first_signal_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['device_phase'] == 'live'
    assert payload['published_signal_count'] == 1
    assert payload['first_signal_summary'] is not None
    assert payload['first_signal_summary']['trace_point_count'] >= 3
    assert payload['replay_tape'] is not None
    assert len(payload['replay_tape']['trace_points']) >= 3
