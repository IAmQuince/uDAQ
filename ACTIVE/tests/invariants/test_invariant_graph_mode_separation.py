from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, as_event_time
from universaldaq.ui import GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-004', 'verifies_requirements': ['UDQ-REQ-UI-003', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-006'], 'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004', 'UDQ-INV-EVID-004'], 'worked_example_reference': 'UDQ-EXM-005', 'expected_proof_output': 'graph-mode invariant report'}
pytestmark = pytest.mark.invariants


def test_invariant_graph_mode_separation():
    session = GraphModeSession.start(GraphMode.LIVE, as_event_time(0)).transition(GraphMode.REVIEW, as_event_time(2)).transition(GraphMode.LIVE_TRACE, as_event_time(3))
    assert GraphMode.LIVE in session.transition_modes
    assert GraphMode.REVIEW in session.transition_modes
    assert GraphMode.LIVE_TRACE in session.transition_modes
    assert len(set(session.transition_modes)) == 3
