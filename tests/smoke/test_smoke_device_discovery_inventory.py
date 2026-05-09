from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-004',
    'verifies_requirements': ['UDQ-REQ-AUD-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'device discovery inventory smoke output',
}
pytestmark = pytest.mark.smoke


def test_device_discovery_inventory_diagnostic_runs_and_emits_json():
    proc = subprocess.run(
        [sys.executable, str(PACKAGE_ROOT / 'tools' / 'diagnostics' / 'dump_device_discovery_inventory.py')],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(proc.stdout)
    assert 'discovered_devices' in payload
    assert 'provider_ids' in payload
