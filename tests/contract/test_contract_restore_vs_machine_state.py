from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, ProfileId, RestoreOrigin, as_event_time
from universaldaq.profiles import ProfileSnapshot, RestorePlan, RestorePlanner, WorkspaceState

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-002', 'verifies_requirements': ['UDQ-REQ-ARCH-002', 'UDQ-REQ-PROF-001', 'UDQ-REQ-PROF-002'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-TRANS-002', 'UDQ-INV-EVID-003'], 'worked_example_reference': 'UDQ-EXM-003', 'expected_proof_output': 'restore-origin trace'}
pytestmark = pytest.mark.contract


def test_contract_restore_vs_machine_state():
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-001'),
        workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.HISTORY),
    )
    result = RestorePlanner.apply(
        RestorePlan(snapshot=snapshot, origin=RestoreOrigin.AUTOSAVE, machine_write_intent=False),
        timestamp=as_event_time(3),
    )
    assert result.machine_write_intent is False
    assert result.restored_workspace.page == 'graphing'
    assert result.restored_workspace.review_mode == GraphMode.HISTORY
    assert result.evidence_records[0].attributes['origin'] == 'autosave'
