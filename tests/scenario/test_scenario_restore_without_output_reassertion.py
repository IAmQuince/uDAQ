from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT
from universaldaq.common import GraphMode, ProfileId, RestoreOrigin, as_event_time
from universaldaq.profiles import ProfileSnapshot, RestorePlan, RestorePlanner, WorkspaceState

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-003', 'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-PROF-002', 'UDQ-REQ-ARCH-002'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-TRANS-002', 'UDQ-INV-EVID-003'], 'worked_example_reference': 'UDQ-EXM-003', 'expected_proof_output': 'restore proof bundle'}
pytestmark = pytest.mark.scenario


def test_scenario_restore_without_output_reassertion():
    sample = json.loads((DATA_ROOT / 'sample_restore_workspace_state.json').read_text(encoding='utf-8'))
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-RESTORE'),
        workspace_state=WorkspaceState(page=sample['workspace']['page'], review_mode=GraphMode.HISTORY),
    )
    result = RestorePlanner.apply(
        RestorePlan(snapshot=snapshot, origin=RestoreOrigin(sample['restore_origin']), machine_write_intent=sample['machine_write_intent']),
        timestamp=as_event_time(7),
    )
    assert result.machine_write_intent is False
    assert result.restored_workspace.page == 'graphing'
    assert result.evidence_records[0].summary == 'restore-origin workspace rebuild'
