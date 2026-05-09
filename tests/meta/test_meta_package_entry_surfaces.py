from __future__ import annotations

import subprocess
import sys

import pytest
import yaml

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-022', 'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-GOV-003'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'package entry validation'}
pytestmark = pytest.mark.meta

REQUIRED_FILES = [
    'docs/release/PACKAGE_ENTRY_REGISTRY.yaml',
    'tools/governance/validate_package_entry_surfaces.py',
]


def test_package_entry_assets_exist() -> None:
    missing = [rel for rel in REQUIRED_FILES if not (PACKAGE_ROOT / rel).exists()]
    assert not missing, missing
    registry = yaml.safe_load((PACKAGE_ROOT / 'docs' / 'release' / 'PACKAGE_ENTRY_REGISTRY.yaml').read_text(encoding='utf-8'))
    canonical_review_entry = next(entry['path'] for entry in registry['entries'] if entry.get('canonical') and entry.get('role') == 'review_entry')
    assert (PACKAGE_ROOT / canonical_review_entry).exists()



def test_package_entry_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'tools.governance.validate_package_entry_surfaces', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
