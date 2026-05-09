from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_evidence_acceptance import run_acceptance

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-029',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'one-command evidence acceptance produces a readable report bundle and bounded fault-injection proof without requiring a long manual pass',
}
pytestmark = pytest.mark.integration


def test_evidence_acceptance_runner_emits_pass_report(tmp_path):
    report = run_acceptance(package_root=PACKAGE_ROOT, output_root=tmp_path / 'acceptance')

    assert report['verdict'] == 'PASS'
    assert 'shell-smoke:' in report['shell_smoke_output']
    assert report['real_hardware_bridge_report']['verdict'] in {'PASS', 'SKIP'}
    report_dir = Path(report['report_dir'])
    json_report = json.loads((report_dir / 'acceptance_report.json').read_text(encoding='utf-8'))
    assert json_report['verdict'] == 'PASS'
    assert (report_dir / 'acceptance_report.md').exists()
