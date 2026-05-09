from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-015', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-GOV-003', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'documentation debt register validation'}
pytestmark = pytest.mark.meta

REQUIRED_FILES = [
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
    'tools/governance/validate_document_debt.py',
]


def test_documentation_debt_assets_exist():
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing


def test_documentation_debt_validator_passes():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.governance.validate_document_debt', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
