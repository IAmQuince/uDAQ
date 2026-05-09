from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-META-023',
    'verifies_requirements': ['UDQ-REQ-GOV-001', 'UDQ-REQ-IMPL-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'run artifact naming validation',
}

pytestmark = pytest.mark.meta


def test_run_artifact_naming_validator_accepts_expected_pattern(tmp_path: Path):
    good_dir = tmp_path / '20260325_01_real-u6-startup-open-smoke'
    good_dir.mkdir()
    good_file = tmp_path / '20260325_00_sprint-3c-startup-open-diagnostic-correction__execution-plan.md'
    good_file.write_text('ok\n', encoding='utf-8')
    tool = Path(__file__).resolve().parents[2] / 'tools' / 'governance' / 'validate_run_artifact_naming.py'
    result = subprocess.run([sys.executable, str(tool), str(good_dir), str(good_file)], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_run_artifact_naming_validator_rejects_invalid_pattern(tmp_path: Path):
    bad = tmp_path / 'UDQ_SPRINT_03C_EXECUTION_PLAN.md'
    bad.write_text('bad\n', encoding='utf-8')
    tool = Path(__file__).resolve().parents[2] / 'tools' / 'governance' / 'validate_run_artifact_naming.py'
    result = subprocess.run([sys.executable, str(tool), str(bad)], capture_output=True, text=True)
    assert result.returncode == 1
    assert 'invalid artifact names' in result.stdout
