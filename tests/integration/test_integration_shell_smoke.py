from __future__ import annotations

import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-004', 'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-AUD-001'], 'checks_invariants': ['UDQ-INV-EVID-006'], 'worked_example_reference': None, 'expected_proof_output': 'shell smoke diagnostic'}
pytestmark = pytest.mark.integration


def test_shell_smoke_command_passes():
    result = subprocess.run(
        [sys.executable, '-m', 'tools.dev.run_shell_smoke', '--package-root', str(PACKAGE_ROOT)],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'shell-smoke:' in result.stdout
