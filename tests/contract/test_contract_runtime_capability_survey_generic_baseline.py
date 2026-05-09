from __future__ import annotations

import pytest

from universaldaq.adapters import survey_runtime_capabilities
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-060',
    'verifies_requirements': ['UDQ-REQ-ARCH-001', 'UDQ-REQ-DEV-001'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-STATE-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'runtime capability survey reports generic baseline discovery without requiring optional support packs',
}
pytestmark = pytest.mark.contract


def test_runtime_capability_survey_reports_generic_baseline_without_optional_support_packs() -> None:
    services = build_default_service_registry(load_support_packs=False)

    survey = survey_runtime_capabilities(adapters=services.adapters, timestamp=as_event_time(22))

    assert survey.devices
    assert all(device.capability_mode == 'generic_baseline' for device in survey.devices)
    assert all(device.activation_available for device in survey.devices)
    assert survey.support_packs == ()
    assert 'generic discovery available' in survey.summary
