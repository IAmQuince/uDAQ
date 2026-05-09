from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-017',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-PROF-001'],
    'checks_invariants': ['UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'bench persistence diagnostic inventory renders saved and restored continuity state',
}
pytestmark = pytest.mark.smoke


def test_smoke_bench_persistence_inventory_diagnostic_runs():
    result = subprocess.run(
        [sys.executable, 'tools/diagnostics/dump_bench_persistence_inventory.py', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['saved_state']['restored_historical_only'] is True
    assert payload['restored_view_model']['restored_historical_context_label']
    assert payload['recent_summary_ids']
