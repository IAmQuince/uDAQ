from __future__ import annotations

import json

import pytest

from tests.conftest import DATA_ROOT
from universaldaq.common import GraphMode, as_event_time
from universaldaq.historian import EvidenceBundle
from universaldaq.ui import GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-SCN-005', 'verifies_requirements': ['UDQ-REQ-UI-003', 'UDQ-REQ-UI-004', 'UDQ-REQ-UI-006', 'UDQ-REQ-HIS-002'], 'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-TRANS-004', 'UDQ-INV-EVID-004'], 'worked_example_reference': 'UDQ-EXM-005', 'expected_proof_output': 'graph mode proof bundle'}
pytestmark = pytest.mark.scenario


MODE_MAP = {
    'live': GraphMode.LIVE,
    'review': GraphMode.REVIEW,
    'history': GraphMode.HISTORY,
    'live-trace': GraphMode.LIVE_TRACE,
}


def test_scenario_graph_live_review_live_trace():
    sample = json.loads((DATA_ROOT / 'sample_graph_mode_trace.json').read_text(encoding='utf-8'))['trace']
    session = GraphModeSession.start(MODE_MAP[sample[0]['mode']], as_event_time(sample[0]['t']))
    for event in sample[1:]:
        session = session.transition(MODE_MAP[event['mode']], as_event_time(event['t']))
    bundle = EvidenceBundle(bundle_id='BUNDLE-GRAPH-001', records=session.evidence_records, overlays=('mode-change-trace',), review_mode=session.mode)
    assert session.transition_modes == (GraphMode.LIVE, GraphMode.REVIEW, GraphMode.LIVE_TRACE, GraphMode.LIVE)
    assert bundle.overlays == ('mode-change-trace',)
    assert bundle.review_mode == GraphMode.LIVE
