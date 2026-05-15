from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_cross_device_recovery_closure import run_cross_device_recovery_closure

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-038',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001', 'UDQ-REQ-SIG-001', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-004', 'UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'cross-device read-side closure proves deeper nominal replay, fallback recovery, degraded adapter handling, and repeatability without destabilizing the evidence spine',
}
pytestmark = pytest.mark.integration


def test_cross_device_recovery_closure_emits_pass_report(tmp_path: Path):
    report = run_cross_device_recovery_closure(package_root=PACKAGE_ROOT, output_root=tmp_path / 'cross_device_closure')

    assert report['verdict'] == 'PASS'
    assert report['activated_adapter_count'] >= 3
    assert report['checkpoint_summary']['valid_checkpoint_count'] >= 3
    assert report['replay_report']['tail_record_count'] >= 8
    assert report['replay_report']['tail_contains_multiple_record_types'] is True
    assert report['fallback_recovery_report']['verdict'] == 'PASS'
    assert report['fallback_recovery_report']['replay_tail_count'] >= 8
    assert report['degraded_conditions_report']['degraded_transition_count'] >= 4
    assert report['repeatability_report']['verdict'] == 'PASS'

    report_dir = Path(report['report_dir'])
    json_report = json.loads((report_dir / 'cross_device_recovery_closure_report.json').read_text(encoding='utf-8'))
    assert json_report['verdict'] == 'PASS'
    assert (report_dir / 'cross_device_recovery_closure_report.md').exists()
    assert (report_dir / 'degraded_adapter_timeline.json').exists()
    assert (report_dir / 'fallback_recovery_detail.json').exists()
    assert (report_dir / 'repeatability' / 'repeatability_report.json').exists()
