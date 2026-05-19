from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

src_root = Path(__file__).resolve().parents[2] / 'src'
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AlarmId, AuthorizationState, GraphMode, ProfileId, VariableId, as_event_time
from universaldaq.events import AlarmDefinition
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

PACKAGE_ID = 'UDQ-PKG-20260328-LIVE-RUNTIME-INTEGRATION-AND-SAFE-CONTROL-POSTURE-FOUNDATIONS-R01'
PACKAGE_SLUG = 'live-runtime-integration-and-safe-control-posture-foundations'


def build_controller(*, disconnect_after_polls: int | None = None, stale_after_polls: int | None = None) -> ShellController:
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(
        DeterministicWaveformAdapter(
            adapter_id='DEMO-FIRST-SIGNAL-001',
            disconnect_after_polls=disconnect_after_polls,
            stale_after_polls=stale_after_polls,
        )
    )
    services.events.register_alarm_definition(
        AlarmDefinition(
            alarm_id=AlarmId('ALM-FLIGHT-001'),
            summary='Flight record warning',
            severity='warning',
            source_kind='manual',
            source_id='flight_record',
            variable_id=VariableId('manual_alarm_stub'),
            condition_kind='variable_boolean_true',
        )
    )
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-SESSION-FLIGHT-RECORD'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('flight-record-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    return ShellController.from_bootstrapped_shell(boot)


def build_inventory(*, sample_count: int, assert_alarm: bool, disconnect_after_polls: int | None = None, stale_after_polls: int | None = None) -> dict[str, object]:
    controller = build_controller(disconnect_after_polls=disconnect_after_polls, stale_after_polls=stale_after_polls)
    timings: dict[str, float] = {}

    start = time.perf_counter()
    devices = controller.discover_devices(timestamp=as_event_time(3))
    timings['discover_ms'] = round((time.perf_counter() - start) * 1000.0, 3)
    device = next(item for item in devices if item.identity.serial_number == 'DEMO-001')

    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    for offset in range(sample_count):
        controller.poll_adapters(timestamp=as_event_time(6 + offset))

    if assert_alarm:
        controller.assert_alarm(alarm_id=AlarmId('ALM-FLIGHT-001'), timestamp=as_event_time(20))

    payload = controller.session_flight_record()
    payload['package_id'] = PACKAGE_ID
    payload['package_slug'] = PACKAGE_SLUG
    payload['timings_ms'] = timings
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description='Emit a deterministic session flight record diagnostic.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='')
    parser.add_argument('--sample-count', type=int, default=8)
    parser.add_argument('--disconnect-after-polls', type=int, default=None)
    parser.add_argument('--stale-after-polls', type=int, default=None)
    parser.add_argument('--assert-alarm', action='store_true')
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    payload = build_inventory(
        sample_count=max(1, args.sample_count),
        assert_alarm=args.assert_alarm,
        disconnect_after_polls=args.disconnect_after_polls,
        stale_after_polls=args.stale_after_polls,
    )
    rendered = json.dumps(payload, indent=2)
    if args.output:
        output_path = package_root / args.output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + '\n', encoding='utf-8')
    else:
        print(rendered)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
