from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-013', 'verifies_requirements': ['UDQ-REQ-AUD-001', 'UDQ-REQ-REL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'root audit wrapper cleanup audit'}
pytestmark = pytest.mark.meta


FORBIDDEN = [
    'udq_master_audit_v7.py',
    'udq_master_audit_v8.py',
    'udq_master_audit_v9.py',
    'sitecustomize.py',
    'UDQ_MASTER_AUDIT__2026-03-21_235959.md',
]


def test_forbidden_root_cleanup_artifacts_are_absent():
    missing_cleanup = [name for name in FORBIDDEN if (PACKAGE_ROOT / name).exists()]
    assert not missing_cleanup, missing_cleanup
