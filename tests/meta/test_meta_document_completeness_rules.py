from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-021', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-GOV-003', 'UDQ-REQ-QUAL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'document completeness validation'}
pytestmark = pytest.mark.meta

REQUIRED_FILES = [
    'docs/active/UDQ-GOV-SOP-002__Controlled_Document_Completeness_and_Recovery_Process__r0__WIP.md',
    'tools/governance/validate_document_completeness.py',
]


def test_document_completeness_assets_exist():
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing


def test_document_completeness_validator_passes():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.governance.validate_document_completeness', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
