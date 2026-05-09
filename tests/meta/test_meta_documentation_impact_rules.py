from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-010', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-IMPL-001', 'UDQ-REQ-QUAL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'documentation impact control validation'}
pytestmark = pytest.mark.meta

REQUIRED_FILES = [
    '.github/PULL_REQUEST_TEMPLATE/typed_domain_model_sprint.md',
    '.github/ISSUE_TEMPLATE/implementation_change.yml',
    '.github/ISSUE_TEMPLATE/docs_change.yml',
    'docs/active/UDQ-GOV-SOP-001__Controlled_Document_Update_and_Impact_Process__r4__WIP.md',
    'docs/active/UDQ-GOV-TPL-001__Sprint_Documentation_Impact_Checklist__r2__WIP.md',
    'docs/active/UDQ-GOV-REG-003__Documentation_Update_Debt_Register__r3__WIP.md',
    'docs/active/UDQ-IMP-PLAN-001__Implementation_Transition_and_Handoff_Plan__r7__WIP.md',
    'docs/active/UDQ-GOV-WI-001__Step_by_Step_Document_Reconciliation_and_Logging_Work_Instruction__r0__WIP.md',
    'docs/active/UDQ-GOV-TPL-002__Documentation_Review_and_Outcome_Ledger_Template__r0__WIP.md',
    'tools/governance/validate_document_impact.py',
    'tools/traceability/dump_requirement_to_code_and_test_links.py',
]


def test_documentation_impact_assets_exist():
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing


def test_documentation_impact_validator_passes():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.governance.validate_document_impact', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
