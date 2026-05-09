from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, as_event_time
from universaldaq.ui import GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-004', 'verifies_requirements': ['UDQ-REQ-UI-003', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-006', 'UDQ-REQ-HIS-002'], 'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004', 'UDQ-INV-EVID-004'], 'worked_example_reference': 'UDQ-EXM-005', 'expected_proof_output': 'graph mode trace'}
pytestmark = pytest.mark.contract


def test_contract_graph_mode_semantics():
    session = GraphModeSession.start(GraphMode.LIVE, as_event_time(0))
    session = session.transition(GraphMode.REVIEW, as_event_time(4))
    session = session.transition(GraphMode.LIVE_TRACE, as_event_time(6))
    session = session.transition(GraphMode.LIVE, as_event_time(9))
    assert session.transition_modes == (GraphMode.LIVE, GraphMode.REVIEW, GraphMode.LIVE_TRACE, GraphMode.LIVE)
    assert len(session.evidence_records) == 4
