from __future__ import annotations

import json

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import (
    BenchPersistenceState,
    ProfileSnapshot,
    WorkspaceState,
    deserialize_bench_persistence_state,
    serialize_bench_persistence_state,
)
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-055',
    'verifies_requirements': ['UDQ-REQ-PROF-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-002', 'UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'bench persistence state round-trips and restores only historical continuity context',
}
pytestmark = pytest.mark.contract


def _controller() -> ShellController:
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-PERSIST-ROUNDTRIP'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == 'DEMO-001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    controller.poll_adapters(timestamp=as_event_time(6))
    controller.poll_adapters(timestamp=as_event_time(7))
    controller.add_operator_note(note_text='roundtrip note', timestamp=as_event_time(8))
    controller.set_pending_note_draft(note_text='remember to reconnect carefully')
    return controller


def test_contract_bench_persistence_roundtrip_and_restore_is_historical():
    controller = _controller()
    state = controller.save_bench_state(timestamp=as_event_time(9))
    payload = serialize_bench_persistence_state(state)
    restored_state = deserialize_bench_persistence_state(json.loads(json.dumps(payload)))
    assert isinstance(restored_state, BenchPersistenceState)
    assert restored_state.restored_historical_only is True
    assert restored_state.preferred_channel_key == 'DEMO-FIRST-SIGNAL-001:demo_wave_0'
    assert restored_state.historical_summary is not None
    assert restored_state.historical_summary.operator_notes[0].text == 'roundtrip note'

    restored_boot = ShellBootstrapper.bootstrap_from_bench_state(
        bench_state=restored_state,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(10)),
        timestamp=as_event_time(11),
        services=controller.services,
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
    )
    restored_controller = ShellController.from_bootstrapped_shell(restored_boot)
    vm = restored_controller.view_model()
    assert vm.preferred_channel_key == 'DEMO-FIRST-SIGNAL-001:demo_wave_0'
    assert vm.restored_historical_context_label is not None
    assert vm.session_note_count == 1
    assert restored_controller.session.last_persisted_session_summary is not None
