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
from universaldaq.app import FirstSignalReplayTape, ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
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
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-FIRST-SIGNAL'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('first-signal-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    return ShellController.from_bootstrapped_shell(boot)


def build_inventory(*, sample_count: int, disconnect_after_polls: int | None = None, stale_after_polls: int | None = None) -> dict[str, object]:
    controller = build_controller(disconnect_after_polls=disconnect_after_polls, stale_after_polls=stale_after_polls)

    timings: dict[str, float] = {}
    start = time.perf_counter()
    devices = controller.discover_devices(timestamp=as_event_time(3))
    timings['discover_ms'] = round((time.perf_counter() - start) * 1000.0, 3)
    device = next(item for item in devices if item.identity.serial_number == 'DEMO-001')

    start = time.perf_counter()
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    timings['select_ms'] = round((time.perf_counter() - start) * 1000.0, 3)

    start = time.perf_counter()
    controller.begin_quick_start(timestamp=as_event_time(5))
    timings['quick_start_ms'] = round((time.perf_counter() - start) * 1000.0, 3)

    for offset in range(sample_count):
        controller.poll_adapters(timestamp=as_event_time(6 + offset))

    view = controller.view_model()
    replay = FirstSignalReplayTape.from_summary(controller.session.ui_session.first_signal_summary)
    return {
        'package_id': PACKAGE_ID,
        'package_slug': PACKAGE_SLUG,
        'selected_device': {
            'device_key': device.device_key,
            'display_name': device.display_name,
            'serial_number': device.identity.serial_number,
            'support_tier': device.support_tier.value,
        },
        'timings_ms': timings,
        'device_phase': view.device_phase,
        'published_signal_count': None if view.lifecycle_summary is None else view.lifecycle_summary.published_signal_count,
        'first_signal_summary': None if view.first_signal_summary is None else {
            'signal_id': view.first_signal_summary.signal_id,
            'display_name': view.first_signal_summary.display_name,
            'point_key': view.first_signal_summary.point_key,
            'point_class': view.first_signal_summary.point_class,
            'latest_value': view.first_signal_summary.latest_value,
            'latest_numeric_value': view.first_signal_summary.latest_numeric_value,
            'quality_label': view.first_signal_summary.quality_label,
            'freshness_label': view.first_signal_summary.freshness_label,
            'engineering_units': view.first_signal_summary.engineering_units,
            'trace_point_count': view.first_signal_summary.trace_point_count,
            'auto_bound': view.first_signal_summary.auto_bound,
            'source_adapter_id': view.first_signal_summary.source_adapter_id,
            'device_identity_key': view.first_signal_summary.device_identity_key,
            'source_transport': view.first_signal_summary.source_transport,
            'hardware_channel': view.first_signal_summary.hardware_channel,
            'provenance_label': view.first_signal_summary.provenance_label,
            'channel_metadata': dict(view.first_signal_summary.channel_metadata),
        },
        'replay_tape': None if replay is None else replay.as_dict(),
        'shell_evidence_count': len(controller.session.shell_evidence_records),
        'runtime_transition_count': len(controller._recent_lifecycle_transition_trace(limit=128)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Emit a deterministic first-signal usability diagnostic inventory.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='')
    parser.add_argument('--sample-count', type=int, default=8)
    parser.add_argument('--disconnect-after-polls', type=int, default=None)
    parser.add_argument('--stale-after-polls', type=int, default=None)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    payload = build_inventory(
        sample_count=max(1, args.sample_count),
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
