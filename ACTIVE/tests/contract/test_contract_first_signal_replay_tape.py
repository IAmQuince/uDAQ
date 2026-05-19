from __future__ import annotations

import pytest

from universaldaq.app import FirstSignalReplayTape
from universaldaq.common import EventTime
from universaldaq.ui import FirstSignalSummary, FirstSignalTracePoint

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-052',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-TIME-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'first-signal replay tape roundtrip remains deterministic and bounded',
}
pytestmark = pytest.mark.contract


def test_first_signal_replay_tape_roundtrips_summary_payload_without_loss():
    summary = FirstSignalSummary(
        signal_id='first_signal__demo',
        display_name='Wave 0',
        point_key='DEMO-FIRST-SIGNAL-001:demo_wave_0',
        point_class='analog',
        latest_value='2.500',
        quality_label='simulated',
        latest_timestamp=EventTime(12),
        engineering_units='V',
        auto_bound=True,
        source_device_key='generic_adapter_inventory:DEMO-FIRST-SIGNAL-001',
        trace_points=(
            FirstSignalTracePoint(timestamp=EventTime(10), value='1.500'),
            FirstSignalTracePoint(timestamp=EventTime(11), value='2.000'),
            FirstSignalTracePoint(timestamp=EventTime(12), value='2.500'),
        ),
    )
    tape = FirstSignalReplayTape.from_summary(summary)
    assert tape is not None
    replay = FirstSignalReplayTape.from_dict(tape.as_dict())
    assert replay.signal_id == tape.signal_id
    assert replay.display_name == tape.display_name
    assert replay.quality_label == tape.quality_label
    assert replay.trace_points == tape.trace_points
