from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-014', 'verifies_requirements': ['UDQ-REQ-REL-001', 'UDQ-REQ-QUAL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'package hygiene audit'}
pytestmark = pytest.mark.meta


def test_package_builder_excludes_cache_and_bytecode_artifacts():
    text = (PACKAGE_ROOT / 'tools/package_build/build_precode_package.py').read_text(encoding='utf-8')
    for token in ['.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache', '*.pyc']:
        assert token in text


def test_forbidden_cache_artifacts_are_not_checked_in_at_root():
    forbidden_root_entries = [
        name for name in ['__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache']
        if (PACKAGE_ROOT / name).exists()
    ]
    assert not forbidden_root_entries


def test_pytest_default_addopts_disable_cacheprovider_to_keep_root_clean():
    text = (PACKAGE_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "-p no:cacheprovider" in text


def test_package_builder_supports_short_delivery_root_and_path_budget_gate():
    text = (PACKAGE_ROOT / 'tools/package_build/build_precode_package.py').read_text(encoding='utf-8')
    assert '--delivery-root' in text
    assert 'validate_windows_path_budget' in text
    assert 'DEFAULT_MAX_WINDOWS_FULL_PATH' in text
