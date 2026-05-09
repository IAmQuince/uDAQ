from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, ProfileId, RestoreOrigin, as_event_time
from universaldaq.profiles import ProfileSnapshot, RestorePlan, RestorePlanner, WorkspaceState

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-002', 'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-PROF-002'], 'checks_invariants': ['UDQ-INV-TRANS-002', 'UDQ-INV-EVID-003'], 'worked_example_reference': 'UDQ-EXM-003', 'expected_proof_output': 'restore-path invariant report'}
pytestmark = pytest.mark.invariants


def test_invariant_restore_path():
    snapshot = ProfileSnapshot(profile_id=ProfileId('PROF-INV-001'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY))
    result = RestorePlanner.apply(RestorePlan(snapshot=snapshot, origin=RestoreOrigin.SESSION, machine_write_intent=False), timestamp=as_event_time(2))
    assert result.machine_write_intent is False
    assert result.evidence_records[0].attributes['machine_write_intent'] == 'false'
