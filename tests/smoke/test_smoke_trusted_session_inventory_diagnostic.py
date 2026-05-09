from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-013',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'trusted-session inventory diagnostic snapshot with reconnect evidence',
}
pytestmark = pytest.mark.smoke


def test_trusted_session_inventory_diagnostic_runs_and_emits_reconnect_ready_state():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_trusted_session_inventory', '--reconnect'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['device_phase'] == 'live'
    assert payload['published_signal_count'] == 1
    trusted = payload['trusted_session_summary']
    assert trusted['graph_status_label'] == 'live'
    assert trusted['graph_visible'] is True
    assert trusted['live_numeric_visible'] is True
    assert trusted['ready_for_operator'] is True
    assert trusted['reconnect_count'] >= 1
    assert trusted['sparkline']
    assert len(trusted['recent_events']) >= 3
