from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_repeatability_gate import run_repeatability_gate

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-031',
    'verifies_requirements': ['UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'repeatability gate reruns the bounded long-run specimen session and proves stable depth and replay metrics across fresh acceptance runs',
}
pytestmark = pytest.mark.integration


def test_repeatability_gate_emits_consistent_runs(tmp_path):
    report = run_repeatability_gate(package_root=PACKAGE_ROOT, output_root=tmp_path / 'repeatability', run_count=3)
    assert report['verdict'] == 'PASS'
    assert report['run_count'] == 3
    assert report['consistent_depth_metrics'] is True
    assert report['consistent_replay_metrics'] is True
    assert report['minimum_valid_checkpoint_count'] >= 4
    report_json = json.loads((tmp_path / 'repeatability' / 'repeatability_report.json').read_text(encoding='utf-8'))
    assert report_json['verdict'] == 'PASS'
    assert len(report_json['runs']) == 3
    assert (tmp_path / 'repeatability' / 'repeatability_report.md').exists()
