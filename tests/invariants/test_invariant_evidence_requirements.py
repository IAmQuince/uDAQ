from __future__ import annotations

import pytest

from universaldaq.common import GraphMode, as_event_time
from universaldaq.historian import EvidenceBundle
from universaldaq.ui import GraphModeSession

TEST_DECLARATION = {'test_id': 'UDQ-TST-INV-005', 'verifies_requirements': ['UDQ-REQ-HIS-001', 'UDQ-REQ-HIS-002', 'UDQ-REQ-GOV-001'], 'checks_invariants': ['UDQ-INV-EVID-001', 'UDQ-INV-EVID-002', 'UDQ-INV-EVID-006'], 'worked_example_reference': 'UDQ-EXM-004', 'expected_proof_output': 'evidence invariant report'}
pytestmark = pytest.mark.invariants


def test_invariant_evidence_requirements():
    session = GraphModeSession.start(GraphMode.LIVE, as_event_time(0)).transition(GraphMode.REVIEW, as_event_time(1))
    bundle = EvidenceBundle(bundle_id='BUNDLE-EVID-001', records=session.evidence_records, overlays=('screenshot',), review_mode=GraphMode.REVIEW)
    assert bundle.records
    assert bundle.overlays == ('screenshot',)
    assert all(record.summary for record in bundle.records)
