from __future__ import annotations

import yaml
import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-META-015',
    'verifies_requirements': ['UDQ-REQ-REL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'current package review entry and legacy pass-2 guide are present',
}
pytestmark = pytest.mark.meta


def test_current_review_entry_matches_package_registry() -> None:
    registry = yaml.safe_load((PACKAGE_ROOT / 'docs' / 'release' / 'PACKAGE_ENTRY_REGISTRY.yaml').read_text(encoding='utf-8'))
    review_entry = PACKAGE_ROOT / registry['entries'][4]['path']
    assert review_entry.exists()
    assert (PACKAGE_ROOT / 'docs' / 'release' / 'EXEC_SUMMARY.md').exists()


def test_legacy_pass2_hardening_guide_is_retained_for_traceability() -> None:
    release_history = PACKAGE_ROOT / 'docs' / 'release' / 'history'
    assert (release_history / 'PASS2_REVIEW_HARDENING_SUMMARY__2026-03-23.md').exists()
    assert (release_history / 'REVIEW_START_HERE__PASS2__2026-03-23.md').exists()
    assert (PACKAGE_ROOT / 'tools' / 'diagnostics' / 'dump_lifecycle_transition_history.py').exists()
