from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-007', 'verifies_requirements': ['UDQ-REQ-IMPL-001', 'UDQ-REQ-GOV-003'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'reserved-package guardrail report'}
pytestmark = pytest.mark.meta

RESERVED_DIRS = [
    'src/universaldaq/backend',
    'src/universaldaq/diagnostics',
    'src/universaldaq/remote',
]


def test_reserved_packages_only_hold_guardrail_files():
    allowed = {'README.md', '__init__.py', '.gitkeep'}
    failures = []
    for rel in RESERVED_DIRS:
        path = PACKAGE_ROOT / rel
        assert (path / 'README.md').exists(), rel
        extra = sorted(p.name for p in path.iterdir() if p.is_file() and p.name not in allowed)
        if extra:
            failures.append(f'{rel}: {extra}')
    assert not failures, failures
