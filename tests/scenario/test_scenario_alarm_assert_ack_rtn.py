from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT
from universaldaq.common import ActorId, AlarmId, AlarmLifecycleState, as_event_time
from universaldaq.events import AlarmLifecycle
from universaldaq.historian import EvidenceBundle

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-004', 'verifies_requirements': ['UDQ-REQ-EVT-001', 'UDQ-REQ-EVT-002', 'UDQ-REQ-HIS-001'], 'checks_invariants': ['UDQ-INV-TRANS-003', 'UDQ-INV-EVID-002'], 'worked_example_reference': 'UDQ-EXM-004', 'expected_proof_output': 'alarm lifecycle proof bundle'}
pytestmark = pytest.mark.scenario


def test_scenario_alarm_assert_ack_rtn():
    sample = json.loads((DATA_ROOT / 'sample_alarm_lifecycle_trace.json').read_text(encoding='utf-8'))['trace']
    lifecycle = AlarmLifecycle(alarm_id=AlarmId('ALM-001'))
    lifecycle = lifecycle.assert_alarm(as_event_time(sample[0]['t']))
    lifecycle = lifecycle.acknowledge(ActorId(sample[1]['actor']), as_event_time(sample[1]['t']))
    lifecycle = lifecycle.return_to_normal(as_event_time(sample[2]['t']))
    bundle = EvidenceBundle(bundle_id='BUNDLE-ALARM-001', records=lifecycle.evidence_records)
    assert lifecycle.ordered_states == (
        AlarmLifecycleState.ASSERTED,
        AlarmLifecycleState.ACKNOWLEDGED,
        AlarmLifecycleState.RETURNED_TO_NORMAL,
    )
    assert bundle.summaries() == ('alarm asserted', 'alarm acknowledged', 'alarm returned to normal')
