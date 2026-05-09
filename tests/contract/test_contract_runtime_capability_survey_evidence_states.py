from __future__ import annotations

import pytest

from universaldaq.adapters import survey_runtime_capabilities
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-064',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-UI-001'],
    'checks_invariants': ['UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime capability survey emits explicit generic-versus-enhanced evidence states and limited-access reasons',
}
pytestmark = pytest.mark.contract


def test_runtime_capability_survey_emits_explicit_evidence_states() -> None:
    services = build_default_service_registry(load_support_packs=False)
    survey = survey_runtime_capabilities(adapters=services.adapters, timestamp=as_event_time(33))
    assert survey.devices
    for device in survey.devices:
        assert device.capability_mode == 'generic_baseline'
        assert device.identity_state in {'known_identity', 'generic_identity'}
        assert device.read_state in {'readable', 'not_readable', 'unknown'}
        assert device.write_state in {'writable', 'not_writable', 'unknown'}
        assert device.limited_access_reason is not None
        assert 'support pack' in device.limited_access_reason or 'activation path' in device.limited_access_reason
