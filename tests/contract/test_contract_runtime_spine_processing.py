from __future__ import annotations

import pytest

from universaldaq.adapters import SimulatedReadAdapter
from universaldaq.common import RuntimeMetricsStore, as_event_time
from universaldaq.runtime import RuntimeQualityService
from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-085',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime spine drains acquisition work, bounds presentation staging, and records cycle/journal activity across repeated live polls',
}
pytestmark = pytest.mark.contract


def _live_summary() -> DeviceLifecycleSummary:
    return DeviceLifecycleSummary(
        phase='live',
        detected_device_count=1,
        active_device_key='DEV-001',
        active_adapter_id='SIM-001',
        projected_point_count=1,
        published_signal_count=1,
        last_poll_snapshot_count=1,
        disconnected_signal_count=0,
        last_transition='poll_active_adapter',
        needs_review=False,
    )


def _variable_summary() -> VariableHealthSummary:
    return VariableHealthSummary(total_variable_count=2, healthy_count=2)


def test_runtime_spine_drains_acquisition_and_coalesces_presentation(tmp_path):
    metrics = RuntimeMetricsStore()
    runtime = RuntimeQualityService(
        metrics=metrics,
        presentation_interval_ticks=2,
        journal_file_path=tmp_path / 'runtime' / 'session.jsonl',
    )
    adapter = SimulatedReadAdapter.from_values(
        adapter_id='SIM-001',
        values={'PT-101': ('1.0', '1.0', 'psi')},
        timestamp=1,
    )

    for tick in (10, 11, 12):
        poll_result = adapter.poll(timestamp=tick)
        runtime.capture_acquisition(adapter_id='SIM-001', timestamp=as_event_time(tick), poll_result=poll_result)
        runtime.record_processed_cycle(
            timestamp=as_event_time(tick),
            lifecycle_summary=_live_summary(),
            variable_summary=_variable_summary(),
            changed_signal_ids=('stack_voltage',),
            poll_result=poll_result,
        )

    status = runtime.snapshot(now=as_event_time(12))
    assert status.acquisition_queue_depth == 0
    assert status.presentation_queue_depth == 0
    assert status.presentation_publish_count == 2
    assert status.presentation_coalesced_count == 1
    assert status.recent_signal_count == 1
    assert status.recent_sample_count == 3
    assert status.recent_cycle_count == 3
    assert status.journal_write_count >= 6
    assert status.journal_flush_count == 3
    assert metrics.snapshot()['counters']['runtime.processing.cycle.count'] == 3
