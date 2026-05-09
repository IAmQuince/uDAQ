from __future__ import annotations

import subprocess
import sys

import pytest

from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, SignalId, VariableId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.signals import VariableDefinition, VariableSourceKind
from universaldaq.ui import AuthoritySurface, GraphModeSession
from universaldaq_labjack.models import LabJackProbeRow
from universaldaq_labjack.plugin import build_support_pack_registration
from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-027',
    'verifies_requirements': ['UDQ-REQ-DIAG-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-STATE-003', 'UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'lifecycle review bundle exposes one canonical runtime evidence route and field-test summaries surface the derived reviewer rollup',
}
pytestmark = pytest.mark.integration


def _bootstrap_controller(tmp_path):
    services = build_default_service_registry()
    services.runtime_quality.journal.file_path = tmp_path / 'runtime' / 'session.jsonl'
    services.adapters.install_support_pack(
        build_support_pack_registration(
            probe_rows=(LabJackProbeRow(model='U6', serial_number='470099', transport='usb'),)
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(profile_id=ProfileId('PROF-RUNTIME-EVIDENCE'), workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE)),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == '470099')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    point_key = next(
        point_key
        for point_key, definition in services.bindings.point_definitions.items()
        if definition.device_identity_key == device.identity.stable_key and definition.point_ref.point_id == 'analog_in_0'
    )
    controller.bind_logical_signal_to_point(logical_signal_id=SignalId('stack_voltage'), point_key=point_key, timestamp=as_event_time(5))
    controller.register_variable_definition(
        definition=VariableDefinition(
            variable_id=VariableId('stack_voltage_copy'),
            display_name='Stack Voltage Copy',
            source_kind=VariableSourceKind.SIGNAL,
            signal_dependencies=(SignalId('stack_voltage'),),
        ),
        timestamp=as_event_time(6),
    )
    controller.begin_quick_start(timestamp=as_event_time(7))
    return controller


def test_lifecycle_review_bundle_contains_canonical_runtime_evidence_bundle(tmp_path):
    controller = _bootstrap_controller(tmp_path)
    controller.mark_active_device_disconnected(timestamp=as_event_time(8))
    controller.reconnect_active_device(timestamp=as_event_time(9))

    bundle = controller.lifecycle_review_bundle()
    assert 'active_adapter_status' in bundle
    assert 'runtime_truth_surface_inventory' in bundle
    assert 'runtime_vocabulary' in bundle
    assert 'runtime_event_taxonomy' in bundle
    assert 'runtime_metric_layers' in bundle
    assert 'reviewer_runtime_rollup' in bundle
    canonical = bundle['canonical_runtime_evidence_bundle_v1']
    assert canonical['bundle_version'] == 'v1'
    assert canonical['runtime_state']['canonical_state_family'] in {
        'live_ready_healthy',
        'disconnected',
        'recovering',
        'degraded',
    }
    assert 'diagnostic_snapshots' in canonical
    assert 'metric_layers' in canonical
    assert canonical['reviewer_rollup']['summary'] == bundle['reviewer_runtime_rollup']['summary']


def test_u6_field_test_summary_surfaces_reviewer_rollup(tmp_path):
    output_dir = tmp_path / 'field_tests'
    result = subprocess.run(
        [
            sys.executable,
            '-m',
            'tools.dev.run_u6_field_test_harness',
            '--package-root',
            str(PACKAGE_ROOT),
            '--output-dir',
            str(output_dir),
            '--noninteractive',
            '--baseline-cycles',
            '1',
            '--loss-cycles',
            '1',
            '--recovery-cycles',
            '1',
        ],
        cwd=PACKAGE_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    bundle_dir = next(path for path in output_dir.iterdir() if path.is_dir())
    summary_text = next(bundle_dir.glob('*__summary.txt')).read_text(encoding='utf-8')
    assert 'Reviewer Runtime Rollup' in summary_text
    assert 'Canonical Runtime Evidence Bundle' in summary_text
