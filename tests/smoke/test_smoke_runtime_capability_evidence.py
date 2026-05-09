from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-006',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-IMPL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime capability evidence diagnostic emits generic and enhanced capability-state summaries',
}
pytestmark = pytest.mark.smoke


def test_runtime_capability_evidence_diagnostic_runs() -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'tools.diagnostics.dump_runtime_capability_evidence'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['generic']['devices']
    assert payload['generic']['devices'][0]['capability_mode'] == 'generic_baseline'
    assert payload['policy_note'].startswith('optional support packs enrich')
