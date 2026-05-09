from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT, parse_declaration

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-002', 'verifies_requirements': ['UDQ-REQ-AUD-001', 'UDQ-REQ-GOV-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'traceability gap report'}
pytestmark = pytest.mark.meta


def test_all_referenced_invariants_exist(invariant_registry):
    valid = {row["invariant_id"] for row in invariant_registry["rows"]}
    failures = []
    for path in sorted((PACKAGE_ROOT / "tests").rglob("test_*.py")):
        decl = parse_declaration(path, "TEST_DECLARATION")
        missing = sorted(set(decl.get("checks_invariants", [])) - valid)
        if missing:
            failures.append(f"{path.relative_to(PACKAGE_ROOT)} -> {missing}")
    assert not failures, "\n".join(failures)
