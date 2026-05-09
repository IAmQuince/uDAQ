from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-META-017',
    'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-QUAL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'tool registry path centralization audit',
}
pytestmark = pytest.mark.meta


REGEX = re.compile(r'registries/active/universalDAQ_[^\"\']+')
ALLOWED = {
    'tools/_registry_paths.py',
}


def test_tools_use_central_registry_path_config():
    findings: list[str] = []
    for path in sorted((PACKAGE_ROOT / 'tools').rglob('*.py')):
        rel = str(path.relative_to(PACKAGE_ROOT))
        if rel in ALLOWED:
            continue
        matches = REGEX.findall(path.read_text(encoding='utf-8'))
        if matches:
            findings.append(f'{rel}: {matches}')
    assert not findings, findings
