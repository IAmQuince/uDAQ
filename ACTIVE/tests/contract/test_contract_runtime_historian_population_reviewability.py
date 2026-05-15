from __future__ import annotations

from pathlib import Path

import pytest

from tools.acceptance.build_populated_review_session import build_populated_review_session
from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-103',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'the specimen historian lane is populated with non-zero sample, variable, and cycle content and emits bounded review, replay, and checkpoint ladder summaries without manual folder archaeology',
}
pytestmark = pytest.mark.contract


def test_populated_review_session_emits_nonzero_history_counts(tmp_path):
    report = build_populated_review_session(package_root=PACKAGE_ROOT, output_root=tmp_path / 'reviewability', cycle_count=18)
    history = report['history_tier_summary']
    assert history['hot']['recent_sample_count'] >= 16
    assert history['warm']['variable_row_count'] >= 16
    assert history['warm']['cycle_row_count'] >= 8
    assert history['cold']['segment_count'] >= 4
    index = report['history_index_report']
    assert index['sample_counts_by_point']['SIM-HIST-001:PT-101'] == 18
    assert index['sample_counts_by_point']['SIM-HIST-001:TT-101'] == 18
    assert index['variable_ids'] == ['VAR-PT-AVG', 'VAR-TT-MEAN']
    replay = report['replay_report']
    assert replay['tail_record_count'] > 0
    assert replay['tail_contains_multiple_record_types'] is True
    assert replay['tail_record_type_count'] >= 3
    checkpoint_summary = report['checkpoint_summary']
    assert checkpoint_summary['valid_checkpoint_count'] >= 2
    assert checkpoint_summary['checkpoint_spacing']['max_sequence_gap'] not in (None, 0)
    assert len(report['recent_sample_rows']) >= 12
    assert Path(tmp_path / 'reviewability' / 'review_summary.json').exists()
    assert Path(tmp_path / 'reviewability' / 'review_summary.md').exists()
    assert Path(tmp_path / 'reviewability' / 'replay_detail.json').exists()
    assert Path(tmp_path / 'reviewability' / 'checkpoint_ladder.json').exists()
    assert Path(tmp_path / 'reviewability' / 'session_timeline.json').exists()
