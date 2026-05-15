from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.conftest import PACKAGE_ROOT
from tools.acceptance.run_evidence_acceptance import run_acceptance

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-030',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'the one-command acceptance runner proves populated historian content, non-zero tail replay, and checkpoint ladder spacing while emitting reviewable acceptance artifacts with minimal operator overhead',
}
pytestmark = pytest.mark.integration


def test_evidence_acceptance_runner_reports_populated_reviewability(tmp_path):
    report = run_acceptance(package_root=PACKAGE_ROOT, output_root=tmp_path / 'acceptance')
    assert report['verdict'] == 'PASS'
    review = report['populated_review_report']
    assert review['history_tier_summary']['hot']['recent_sample_count'] > 0
    assert review['history_tier_summary']['warm']['variable_row_count'] > 0
    assert review['history_tier_summary']['warm']['cycle_row_count'] > 0
    assert review['replay_report']['tail_record_count'] > 0
    assert review['replay_report']['tail_contains_multiple_record_types'] is True
    assert review['checkpoint_summary']['valid_checkpoint_count'] >= 4
    report_dir = Path(report['report_dir'])
    acceptance_json = json.loads((report_dir / 'acceptance_report.json').read_text(encoding='utf-8'))
    assert acceptance_json['verdict'] == 'PASS'
    assert (report_dir / 'reviewability' / 'review_summary.json').exists()
    assert (report_dir / 'reviewability' / 'review_summary.md').exists()
    assert (report_dir / 'reviewability' / 'replay_detail.json').exists()
    assert (report_dir / 'reviewability' / 'checkpoint_ladder.json').exists()
    assert (report_dir / 'reviewability' / 'session_timeline.json').exists()
    assert (report_dir / 'fault_injection' / 'fallback_recovery_detail.json').exists()
    check_names = {check['name'] for check in acceptance_json['checks']}
    assert {'nonzero_tail_replay', 'multi_type_tail_replay', 'checkpoint_ladder_depth', 'longrun_history_depth', 'repeatability_gate', 'fallback_nonzero_tail_replay', 'fallback_multi_type_tail_replay', 'fallback_recovery_state_hash', 'longrun_characterization_thresholds'} <= check_names
    assert (report_dir / 'reviewability' / 'longrun_characterization.json').exists()
    assert (report_dir / 'repeatability' / 'repeatability_report.json').exists()
