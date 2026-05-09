from __future__ import annotations

import pathlib

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-013',
    'verifies_requirements': ['UDQ-REQ-ARCH-002', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'no direct LabJack imports in universal core',
}
pytestmark = pytest.mark.invariants


def test_universal_core_contains_no_direct_labjack_imports():
    failures = []
    for path in sorted((PACKAGE_ROOT / 'src' / 'universaldaq').rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if 'import universaldaq_labjack' in text or 'from universaldaq_labjack' in text:
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
