from __future__ import annotations

import pytest

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-059',
    'verifies_requirements': ['UDQ-REQ-ARCH-002', 'UDQ-REQ-OUT-001', 'UDQ-REQ-UI-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'live runtime inventory remains visible, one supported live specimen path can connect, and view-only posture blocks writes until armed-control is explicit',
}
pytestmark = pytest.mark.contract

from universaldaq.ui.live_runtime import LiveRuntimeEngine


def test_live_runtime_inventory_exposes_one_supported_visible_path() -> None:
    engine = LiveRuntimeEngine(load_support_packs=False)

    devices = engine.available_devices()

    assert devices
    assert any(device.live_capable for device in devices)
    assert all(device.device_key for device in devices)
    inventory = engine.inventory()
    assert inventory['runtime_mode'] == 'LIVE'
    assert inventory['support_pack_state'] == []


def test_live_runtime_write_is_blocked_in_view_only_and_allowed_in_armed_control() -> None:
    engine = LiveRuntimeEngine(load_support_packs=False)
    device = engine.available_devices()[0]

    assert engine.connect(device_key=device.device_key) is True
    engine.step()

    blocked = engine.request_write(point_id='analog_out_0', request_value='2.500', posture='view_only')
    allowed = engine.request_write(point_id='analog_out_0', request_value='2.500', posture='armed_control')

    assert blocked.allowed is False
    assert 'posture' in blocked.reason
    assert allowed.allowed is True
    assert allowed.result is not None
    assert allowed.result.outcome.value in {'observed', 'accepted_for_transmission', 'observation_pending'}
