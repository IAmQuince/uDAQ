from __future__ import annotations

import json

import pytest

from universaldaq.common import as_event_time
from universaldaq.runtime import AppendOnlyJournalService, JournalEntry, RuntimeQualityService

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-101',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'session journal emits ordered sequence ids, rotates governed segments, and checkpoint recovery can replay the tail after the last committed sequence',
}
pytestmark = pytest.mark.contract


def test_session_journal_rotates_segments_and_persists_manifest(tmp_path):
    journal = AppendOnlyJournalService(
        file_path=tmp_path / 'runtime' / 'legacy.jsonl',
        queue_max_items=8,
        max_segment_records=2,
    )
    journal.activate_session(session_id='SESSION-ROTATE', session_root_path=tmp_path / 'runtime' / 'sessions' / 'SESSION-ROTATE')

    for tick in range(1, 6):
        journal.enqueue(entry=JournalEntry(timestamp=as_event_time(tick), record_type='runtime_event', payload={'tick': tick}))

    result = journal.flush(now=as_event_time(6))

    assert result.written_count == 5
    assert result.segment_count == 3
    manifest = json.loads((tmp_path / 'runtime' / 'sessions' / 'SESSION-ROTATE' / 'journal' / 'manifest.json').read_text(encoding='utf-8'))
    assert manifest['last_sequence_id'] == 5
    assert [segment['record_count'] for segment in manifest['segments']] == [2, 2, 1]
    rows = journal.read_persisted_entries()
    assert [row['sequence_id'] for row in rows] == [1, 2, 3, 4, 5]
    assert [row['payload']['tick'] for row in rows] == [1, 2, 3, 4, 5]


def test_runtime_quality_checkpoint_recovery_replays_journal_tail(tmp_path):
    runtime = RuntimeQualityService(
        journal_file_path=tmp_path / 'runtime' / 'session.jsonl',
        journal_max_segment_records=2,
        session_id='SESSION-RECOVER',
    )
    runtime.record_operational_entry(
        timestamp=as_event_time(10),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'before checkpoint'},
    )
    runtime.flush_journal(now=as_event_time(10))
    checkpoint = runtime.write_checkpoint(
        timestamp=as_event_time(11),
        payload={'phase': 'baseline', 'operator_note': 'checkpointed'},
    )
    assert checkpoint is not None

    runtime.record_operational_entry(
        timestamp=as_event_time(12),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'after checkpoint'},
    )
    runtime.flush_journal(now=as_event_time(12))

    recovery = runtime.build_recovery_bundle()
    assert recovery['checkpoint_available'] is True
    assert recovery['state_hash_matches'] is True
    assert recovery['checkpoint']['last_committed_sequence_id'] == checkpoint.checkpoint.last_committed_sequence_id
    assert [row['payload']['message'] for row in recovery['journal_tail']] == ['after checkpoint']
