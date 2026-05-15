from __future__ import annotations

import pytest

from universaldaq.ui.live_runtime import LiveRuntimeEngine

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-067',
    'verifies_requirements': ['UDQ-REQ-UI-002', 'UDQ-REQ-ARCH-001'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'live runtime device records surface generic versus enhanced capability evidence without requiring support packs for baseline discovery',
}
pytestmark = pytest.mark.contract


def test_live_runtime_available_devices_surface_capability_evidence() -> None:
    runtime = LiveRuntimeEngine(load_support_packs=False)
    devices = runtime.available_devices()
    assert devices
    first = devices[0]
    assert first.capability_mode
    assert first.identity_state in {'known_identity', 'generic_identity', 'unknown'}
    assert first.read_state in {'readable', 'not_readable', 'unknown'}
    assert first.write_state in {'writable', 'not_writable', 'unknown'}
