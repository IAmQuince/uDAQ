from __future__ import annotations

import pytest

from universaldaq.common import as_event_time
from universaldaq.runtime import RuntimeQualityService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-102',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime evidence exposes bounded hot-warm-cold history summaries and deterministic replay hashes over the checkpoint tail',
}
pytestmark = pytest.mark.contract


def test_runtime_replay_report_and_history_tiers_are_deterministic(tmp_path):
    runtime = RuntimeQualityService(
        journal_file_path=tmp_path / 'runtime' / 'session.jsonl',
        journal_max_segment_records=2,
        session_id='SESSION-HISTORY',
    )
    runtime.record_operational_entry(
        timestamp=as_event_time(10),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'before checkpoint'},
        flush=True,
    )
    runtime.write_checkpoint(timestamp=as_event_time(11), payload={'phase': 'baseline'})
    for tick in range(12, 17):
        runtime.record_operational_entry(
            timestamp=as_event_time(tick),
            record_type='runtime_event',
            payload={'event_type': 'operator_note', 'message': f'tail-{tick}'},
            flush=True,
        )

    history_summary = runtime.history_tier_summary()
    replay_a = runtime.build_replay_report(limit=256)
    replay_b = runtime.build_replay_report(limit=256)

    assert history_summary['cold']['segment_count'] >= 2
    assert history_summary['cold']['checkpoint_count'] >= 1
    assert replay_a['tail_record_count'] == 5
    assert replay_a['replay_state_hash'] == replay_b['replay_state_hash']
    assert replay_a['deterministic_input_hash'] == replay_b['deterministic_input_hash']
    assert replay_a['projected_state']['tail_runtime_event_counts_by_type']['operator_note'] == 5
    assert len(runtime.session_artifact_inventory()['segment_rows']) >= 2
