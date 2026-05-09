from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-005', 'verifies_requirements': ['UDQ-REQ-IMPL-001', 'UDQ-REQ-HIS-001', 'UDQ-REQ-EXP-001', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'shell state inventory diagnostic output'}
pytestmark = pytest.mark.smoke


def test_shell_state_inventory_diagnostic_runs_and_emits_rich_state():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_shell_state_inventory'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['graph_mode'] == 'live'
    assert payload['authority'] == 'review-only'
    assert payload['bundle_ids'] == ['BUNDLE-DIAG-001']
    assert payload['shell_evidence_count'] >= 5
    assert payload['last_export_manifest_id'] == 'MAN-DIAG-001'
    assert 'profiles.json' in payload['serialized_artifact_paths']
    assert payload['export_history_ids'] == ['EXPORT-DIAG-001']
