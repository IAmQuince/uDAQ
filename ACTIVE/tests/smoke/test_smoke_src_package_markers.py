from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-004', 'verifies_requirements': ['UDQ-REQ-IMPL-001', 'UDQ-REQ-ARCH-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'module-marker smoke output'}
pytestmark = pytest.mark.smoke


def test_first_slice_module_markers_exist():
    files = [
        "src/universaldaq/app/__init__.py",
        "src/universaldaq/common/__init__.py",
        "src/universaldaq/signals/__init__.py",
        "src/universaldaq/outputs/__init__.py",
        "src/universaldaq/events/__init__.py",
        "src/universaldaq/historian/__init__.py",
        "src/universaldaq/profiles/__init__.py",
        "src/universaldaq/ui/__init__.py",
    ]
    missing = [f for f in files if not (PACKAGE_ROOT / f).exists()]
    assert not missing, missing
