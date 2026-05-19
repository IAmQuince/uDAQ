from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-007', 'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-DIAG-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'session-review diagnostic inventory'}
pytestmark = pytest.mark.smoke


def test_session_review_inventory_diagnostic_runs_and_reports_recent_session_state():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_session_review_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['review_count'] >= 1
    assert payload['selected_detail']['historical_label'].startswith('historical review only')
    assert payload['report_payload']['signal']['trace_preview']
    assert payload['report_payload']['notes']
