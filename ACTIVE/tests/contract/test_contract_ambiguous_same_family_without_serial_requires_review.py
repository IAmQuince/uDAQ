from __future__ import annotations

import pytest

from universaldaq.adapters import DeviceIdentity, MatchConfidence, ReconciliationOutcomeKind
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-023',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'ambiguous identical-device review proof',
}
pytestmark = pytest.mark.contract


def test_same_family_device_without_serial_requires_review_when_existing_records_exist():
    services = build_default_service_registry()
    services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='arduino::uno::known-1',
            display_name='Arduino Uno',
            vendor='Arduino',
            model='Uno',
            serial_number='A1',
            transport='usb',
        ),
        provider_id='serial_bridge',
        transport_path='usb:4',
        timestamp=as_event_time(20),
    )

    outcome = services.device_registry.register_or_attach(
        identity=DeviceIdentity(
            stable_key='arduino::uno::candidate',
            display_name='Arduino Candidate',
            vendor='Arduino',
            model='Uno',
            transport='usb',
            provisional=True,
        ),
        provider_id='serial_probe',
        transport_path='usb:9',
        timestamp=as_event_time(21),
    )

    assert outcome.kind == ReconciliationOutcomeKind.CANDIDATE_REMAP_REQUIRES_REVIEW
    assert outcome.confidence == MatchConfidence.POSSIBLE_MATCH
    assert outcome.remap_candidates
