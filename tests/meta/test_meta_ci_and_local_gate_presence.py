from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-006', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'ci-and-gate presence report'}
pytestmark = pytest.mark.meta


REQUIRED_FILES = [
    '.github/workflows/ci.yml',
    '.pre-commit-config.yaml',
    'CONTRIBUTING.md',
    'CODEOWNERS',
    'tools/dev/run_local_gate.py',
    'tools/dev/run_type_gate.py',
    'tools/audit/run_master_audit.py',
]


def test_ci_and_gate_files_exist():
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing
