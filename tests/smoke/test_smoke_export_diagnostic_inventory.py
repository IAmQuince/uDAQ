from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-006', 'verifies_requirements': ['UDQ-REQ-HIS-001', 'UDQ-REQ-EXP-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'export inventory diagnostic'}
pytestmark = pytest.mark.smoke


def test_export_inventory_diagnostic_runs_and_reports_artifacts():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_export_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['manifest_id'] == 'MAN-INV-001'
    assert 'review.md' in payload['artifact_paths']
    assert payload['bundle_record_count'] >= 1
