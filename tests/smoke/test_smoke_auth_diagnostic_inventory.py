from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-003', 'verifies_requirements': ['UDQ-REQ-SEC-001', 'UDQ-REQ-SEC-002'], 'checks_invariants': ['UDQ-INV-EVID-004'], 'worked_example_reference': None, 'expected_proof_output': 'authorization diagnostic inventory'}
pytestmark = pytest.mark.smoke


def test_authorization_diagnostic_inventory_emits_expected_fields():
    root = Path(__file__).resolve().parents[2]
    proc = subprocess.run(
        [sys.executable, str(root / 'tools' / 'diagnostics' / 'dump_authorization_inventory.py')],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    assert payload['role_class'] == 'observer'
    assert payload['last_authorization_action'] == 'export_review_artifact'
    assert payload['authorization_history_count'] >= 3
