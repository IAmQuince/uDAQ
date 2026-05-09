from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-META-009', 'verifies_requirements': ['UDQ-REQ-REL-001', 'UDQ-REQ-IMPL-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'package-build exclusion audit'}
pytestmark = pytest.mark.meta


def test_package_builder_declares_cache_exclusions():
    text = (PACKAGE_ROOT / 'tools/package_build/build_precode_package.py').read_text(encoding='utf-8')
    for token in ['.pytest_cache', '__pycache__', '.mypy_cache', '.ruff_cache', '*.pyc']:
        assert token in text



def test_windows_path_budget_validator_exists_and_passes_for_short_delivery_root():
    import subprocess, sys
    result = subprocess.run(
        [sys.executable, '-m', 'tools.package_build.validate_windows_path_budget', '--package-root', str(PACKAGE_ROOT), '--delivery-root', 'udq_s02b_r01'],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'windows-path-budget: PASS' in result.stdout
