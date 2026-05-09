from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-014',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-ARCH-002'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'no direct optional support-pack imports in universal core',
}
pytestmark = pytest.mark.invariants


def test_universal_core_contains_no_direct_optional_support_pack_imports():
    failures = []
    forbidden = ('universaldaq_labjack', 'universaldaq_arduino', 'universaldaq_rpi')
    for path in sorted((PACKAGE_ROOT / 'src' / 'universaldaq').rglob('*.py')):
        text = path.read_text(encoding='utf-8')
        if any(f'import {module}' in text or f'from {module}' in text for module in forbidden):
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
