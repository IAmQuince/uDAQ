from __future__ import annotations

import json
import subprocess
import sys

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-ADAPT-001', 'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-DEV-001'], 'checks_invariants': ['UDQ-INV-TIME-001', 'UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'adapter inventory diagnostic dump'}


def test_adapter_inventory_diagnostic_runs_and_reports_capabilities():
    proc = subprocess.run(
        [sys.executable, str(PACKAGE_ROOT / 'tools' / 'diagnostics' / 'dump_adapter_inventory.py')],
        cwd=PACKAGE_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)

    assert payload['adapter_ids']
    assert any(item['writable_points'] for item in payload['capabilities'])
