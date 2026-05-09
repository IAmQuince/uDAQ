from __future__ import annotations

import pytest

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-053',
    'verifies_requirements': ['UDQ-REQ-DEV-001', 'UDQ-REQ-UI-006', 'UDQ-REQ-DIAG-001'],
    'checks_invariants': ['UDQ-INV-STATE-001'],
    'worked_example_reference': None,
    'expected_proof_output': 'first-signal summary now carries freshness state plus channel provenance and metadata at the shell seam',
}
pytestmark = pytest.mark.contract


def test_first_signal_summary_carries_freshness_and_provenance_metadata():
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-FIRST-SIGNAL-PROVENANCE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
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

    summary = controller.view_model().first_signal_summary
    assert summary is not None
    assert summary.freshness_label == 'simulated'
    assert summary.source_adapter_id == 'DEMO-FIRST-SIGNAL-001'
    assert summary.device_identity_key == device.identity.stable_key
    assert summary.source_transport == 'in_memory'
    assert summary.hardware_channel == 'demo_wave_0'
    assert summary.provenance_label is not None and 'First Signal Demo Device' in summary.provenance_label
    metadata = dict(summary.channel_metadata)
    assert metadata['source_adapter_id'] == 'DEMO-FIRST-SIGNAL-001'
    assert metadata['source_point_id'] == 'demo_wave_0'
    assert metadata['binding_origin'] == 'auto_bound'
