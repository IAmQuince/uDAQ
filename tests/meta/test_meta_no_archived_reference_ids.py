from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT, parse_declaration

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-005', 'verifies_requirements': ['UDQ-REQ-GOV-004', 'UDQ-REQ-REL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'inactive-reference audit'}
pytestmark = pytest.mark.meta


def test_test_declarations_do_not_reference_archive_paths():
    bad = []
    for path in sorted((PACKAGE_ROOT / "tests").rglob("test_*.py")):
        decl = parse_declaration(path, "TEST_DECLARATION")
        for key, value in decl.items():
            if isinstance(value, str) and "archive" in value.lower():
                bad.append(f"{path.name}:{key}")
    assert not bad, bad
