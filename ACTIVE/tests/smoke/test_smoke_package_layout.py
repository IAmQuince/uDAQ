from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-SMK-001', 'verifies_requirements': ['UDQ-REQ-AUD-001', 'UDQ-REQ-REL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'package layout audit'}
pytestmark = pytest.mark.smoke

REQUIRED_DIRS = [
    "tests/meta", "tests/smoke", "tests/contract", "tests/scenario", "tests/invariants",
    "tests/fixtures", "tests/data", "tools/governance", "tools/traceability", "tools/audit",
    "tools/diagnostics", "tools/package_build", "tools/proof", "tools/dev",
]


def test_required_scaffold_directories_exist():
    missing = [d for d in REQUIRED_DIRS if not (PACKAGE_ROOT / d).exists()]
    assert not missing, missing
