from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-012', 'verifies_requirements': ['UDQ-REQ-REL-001', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'root layer allowlist audit'}
pytestmark = pytest.mark.meta


ALLOWED_ROOT_NAMES = {
    '.github', '.gitignore', '.pre-commit-config.yaml', 'CODEOWNERS', 'CONTRIBUTING.md', 'README.md',
    'audit_reports', 'docs', 'proof', 'pyproject.toml', 'registries', 'runtime', 'src', 'tests', 'tools',
}


def test_root_layer_contains_only_allowed_front_door_entries():
    names = {path.name for path in PACKAGE_ROOT.iterdir()}
    assert names.issubset(ALLOWED_ROOT_NAMES), sorted(names - ALLOWED_ROOT_NAMES)
