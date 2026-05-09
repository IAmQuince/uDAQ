from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-META-023',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-GOV-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'controller concentration reduction and extracted handler assets',
}
pytestmark = pytest.mark.meta


HELPER_MODULES = [
    'src/universaldaq/app/workspace_profile_handler.py',
    'src/universaldaq/app/command_export_handler.py',
    'src/universaldaq/app/automation_review_handler.py',
]


def test_controller_concentration_reduced_and_handlers_exist():
    controller_path = PACKAGE_ROOT / 'src/universaldaq/app/controller.py'
    line_count = sum(1 for _ in controller_path.read_text(encoding='utf-8').splitlines())
    assert line_count < 950, line_count
    missing = [rel for rel in HELPER_MODULES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing
