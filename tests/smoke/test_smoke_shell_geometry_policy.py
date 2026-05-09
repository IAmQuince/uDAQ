from __future__ import annotations

import json
import subprocess
import sys

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-SMK-007',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'shell geometry policy diagnostic emits clamped window and PiP decisions',
}
pytestmark = pytest.mark.smoke


def test_shell_geometry_policy_diagnostic_runs() -> None:
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.diagnostics.dump_shell_geometry_policy',
            '--screen',
            '0,0,1920,1040',
            '--requested',
            '1600,40,1500,920',
            '--workspace',
            'logic_designer',
            '--pip',
            '1500,850,420,260',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    payload = json.loads(result.stdout)
    assert payload['graph_presentation'] == 'compact_pip'
    assert payload['window_rect_clamped'] is True
    assert payload['pip_clamped'] is True
