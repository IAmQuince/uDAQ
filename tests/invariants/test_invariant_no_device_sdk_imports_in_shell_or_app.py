from __future__ import annotations

import re

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INV-017',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-ARCH-002'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'shell and application layers do not import device SDK modules directly',
}
pytestmark = pytest.mark.invariants


_FORBIDDEN = (
    r'\bfrom\s+u6\b',
    r'\bimport\s+u6\b',
    r'LabJackPython',
    r'RPi\.GPIO',
    r'gpiozero',
    r'from\s+universaldaq_labjack',
    r'import\s+universaldaq_labjack',
    r'from\s+universaldaq_arduino',
    r'import\s+universaldaq_arduino',
    r'from\s+universaldaq_rpi',
    r'import\s+universaldaq_rpi',
)


def test_shell_and_app_layers_contain_no_direct_device_sdk_imports() -> None:
    failures: list[str] = []
    for relative in ('src/universaldaq/ui', 'src/universaldaq/app'):
        root = PACKAGE_ROOT / relative
        for path in sorted(root.rglob('*.py')):
            text = path.read_text(encoding='utf-8')
            if any(re.search(pattern, text) for pattern in _FORBIDDEN):
                failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
