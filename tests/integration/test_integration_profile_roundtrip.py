from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, ProfileId, TraceId
from universaldaq.profiles import FileProfileStore, ProfileSnapshot, WorkspaceState

TEST_DECLARATION = {'test_id': 'UDQ-TST-INT-001', 'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-PROF-002', 'UDQ-REQ-ARCH-002'], 'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-TRANS-002', 'UDQ-INV-EVID-003'], 'worked_example_reference': None, 'expected_proof_output': 'profile round-trip diagnostic'}
pytestmark = pytest.mark.integration


def test_profile_roundtrip(tmp_path):
    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-ROUNDTRIP'),
        workspace_state=WorkspaceState(
            page='graphing',
            review_mode=GraphMode.HISTORY,
            visible_traces=(TraceId('TRACE-A'), TraceId('TRACE-B')),
        ),
    )
    store = FileProfileStore(root=tmp_path)
    saved_path = store.save(snapshot)
    loaded = store.load(ProfileId('PROF-ROUNDTRIP'))
    assert saved_path.exists()
    assert loaded == snapshot
