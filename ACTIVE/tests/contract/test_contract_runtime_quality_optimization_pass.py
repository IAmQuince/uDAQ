from __future__ import annotations

import json

import pytest

from universaldaq.common import as_event_time
from universaldaq.runtime import RuntimeQualityService

TEST_DECLARATION = {
    "test_id": "UDQ-TST-CON-096",
    "verifies_requirements": ["UDQ-REQ-DIAG-001", "UDQ-REQ-ARCH-001"],
    "checks_invariants": ["UDQ-INV-TIME-001"],
    "worked_example_reference": None,
    "expected_proof_output": "runtime optimization pass keeps sample counts bounded, supports metrics-free operation, and flushes deferred operational entries on snapshot",
}
pytestmark = pytest.mark.contract


def test_runtime_quality_tracks_recent_sample_count_without_full_scan(tmp_path):
    runtime = RuntimeQualityService(
        point_history_limit=2,
        journal_file_path=tmp_path / 'runtime' / 'session.jsonl',
    )
    from universaldaq.adapters import SimulatedReadAdapter

    adapter = SimulatedReadAdapter.from_values(
        adapter_id='SIM-001',
        values={'PT-101': ('1.0', '1.0', 'psi')},
        timestamp=1,
    )

    for tick in (10, 11, 12):
        poll_result = adapter.poll(timestamp=tick)
        runtime.capture_acquisition(adapter_id='SIM-001', timestamp=as_event_time(tick), poll_result=poll_result)
        batch = runtime.acquisition_queue.pop_oldest()
        assert batch is not None
        runtime._append_samples(batch.payload.poll_result.snapshots)

    status = runtime.snapshot(now=as_event_time(12))
    assert status.recent_signal_count == 1
    assert status.recent_sample_count == 2


def test_runtime_quality_flushes_deferred_operational_entries_on_snapshot(tmp_path):
    runtime = RuntimeQualityService(
        journal_file_path=tmp_path / 'runtime' / 'session.jsonl',
        journal_event_flush_threshold=8,
    )
    runtime.record_operational_entry(
        timestamp=as_event_time(10),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'queued first'},
    )
    runtime.record_operational_entry(
        timestamp=as_event_time(11),
        record_type='runtime_event',
        payload={'event_type': 'operator_note', 'message': 'queued second'},
    )

    assert runtime.journal.queue_depth == 2
    status = runtime.snapshot(now=as_event_time(12))
    assert status.journal_queue_depth == 0
    rows = [json.loads(line) for line in (tmp_path / 'runtime' / 'session.jsonl').read_text(encoding='utf-8').splitlines()]
    assert [row['payload']['message'] for row in rows] == ['queued first', 'queued second']


def test_runtime_quality_supports_metrics_free_operation(tmp_path):
    runtime = RuntimeQualityService(journal_file_path=tmp_path / 'runtime' / 'session.jsonl')
    runtime.record_operational_entry(timestamp=as_event_time(5), record_type='runtime_event', payload={'event_type': 'noop'})
    status = runtime.snapshot(now=as_event_time(6))
    assert status.recent_runtime_event_count == 1
