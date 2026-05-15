from __future__ import annotations

import json

import pytest

from universaldaq.common import RuntimeMetricsStore, as_event_time
from universaldaq.runtime import AppendOnlyJournalService, BoundedRecordQueue, JournalEntry

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-084',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded runtime queue drops oldest records and append-only journal persists ordered jsonl rows',
}
pytestmark = pytest.mark.contract


def test_runtime_quality_queue_drops_oldest_record_when_capacity_is_exceeded():
    queue = BoundedRecordQueue[str](max_items=2)

    queue.push(payload='first', enqueued_at=as_event_time(1))
    queue.push(payload='second', enqueued_at=as_event_time(2))
    queue.push(payload='third', enqueued_at=as_event_time(3))

    drained = queue.drain()
    assert [row.payload for row in drained] == ['second', 'third']
    assert queue.dropped_count == 1
    assert queue.high_watermark == 2


def test_append_only_runtime_journal_writes_jsonl_rows_in_order(tmp_path):
    metrics = RuntimeMetricsStore()
    journal_path = tmp_path / 'runtime' / 'journal.jsonl'
    journal = AppendOnlyJournalService(file_path=journal_path, metrics=metrics, queue_max_items=4)
    journal.enqueue(entry=JournalEntry(timestamp=as_event_time(10), record_type='sample', payload={'value': '1.0'}))
    journal.enqueue(entry=JournalEntry(timestamp=as_event_time(11), record_type='cycle', payload={'phase': 'live'}))

    result = journal.flush(now=as_event_time(12))

    assert result.written_count == 2
    lines = journal_path.read_text(encoding='utf-8').strip().splitlines()
    assert [json.loads(line)['record_type'] for line in lines] == ['sample', 'cycle']
    assert metrics.snapshot()['counters']['runtime.journal.write.count'] == 2
