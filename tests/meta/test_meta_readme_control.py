from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-011', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'README control validation'}
pytestmark = pytest.mark.meta


REQUIRED_FILES = [
    'docs/active/UDQ-GOV-POL-002__README_Control_and_Classification_Policy__r0__WIP.md',
    'registries/active/universalDAQ_readme_registry_r0.json',
    'registries/active/universalDAQ_readme_registry_r0.csv',
    'tools/governance/validate_readme_control.py',
    'README.md',
    'docs/handbook/START_HERE.md',
    'docs/release/EXEC_SUMMARY.md',
    'docs/release/SAVEPOINT_SUMMARY.md',
    'docs/handbook/IMPLEMENTATION_ENTRY.md',
    'docs/handbook/TESTS_AND_TOOLS.md',
    'docs/handbook/AUDIT_AND_GOVERNANCE.md',
    'docs/handbook/NEXT_ACTIONS.md',
    'docs/review/HUMAN_PASS_CHECKLIST.md',
    'docs/release/RELEASE_NOTES.md',
]


def test_readme_control_assets_exist():
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing


def test_readme_control_validator_passes():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.governance.validate_readme_control', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
