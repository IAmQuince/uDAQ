from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

src_root = Path(__file__).resolve().parents[2] / 'src'
if str(src_root) not in sys.path:
    sys.path.insert(0, str(src_root))

from universaldaq.adapters import DeterministicWaveformAdapter
from universaldaq.app import ShellBootstrapper, ShellController, build_default_service_registry
from universaldaq.common import ActorId, AuthorizationState, GraphMode, ProfileId, as_event_time
from universaldaq.profiles import ProfileSnapshot, WorkspaceState
from universaldaq.security import ActorContext, RoleClass
from universaldaq.ui import AuthoritySurface, GraphModeSession

PACKAGE_ID = 'UDQ-PKG-20260328-LIVE-RUNTIME-INTEGRATION-AND-SAFE-CONTROL-POSTURE-FOUNDATIONS-R01'
PACKAGE_SLUG = 'live-runtime-integration-and-safe-control-posture-foundations'


def build_controller() -> ShellController:
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-BENCH-PERSIST'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('bench-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    return ShellController.from_bootstrapped_shell(boot)


def build_inventory() -> dict[str, object]:
    controller = build_controller()
    devices = controller.discover_devices(timestamp=as_event_time(3))
    device = next(item for item in devices if item.identity.serial_number == 'DEMO-001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    controller.poll_adapters(timestamp=as_event_time(6))
    controller.poll_adapters(timestamp=as_event_time(7))
    controller.add_operator_note(note_text='Started bench persistence check', timestamp=as_event_time(8), category='bench_note')
    controller.set_pending_note_draft(note_text='Check tubing before reconnect')
    state = controller.save_bench_state(timestamp=as_event_time(9))

    restored_boot = ShellBootstrapper.bootstrap_from_bench_state(
        bench_state=state,
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(10)),
        timestamp=as_event_time(11),
        services=controller.services,
        actor_context=ActorContext(actor_id=ActorId('bench-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
    )
    restored = ShellController.from_bootstrapped_shell(restored_boot)
    return {
        'package_id': PACKAGE_ID,
        'package_slug': PACKAGE_SLUG,
        'saved_state': state.export_summary(),
        'restored_view_model': {
            'preferred_adapter_id': restored.view_model().preferred_adapter_id,
            'preferred_device_key': restored.view_model().preferred_device_key,
            'preferred_channel_key': restored.view_model().preferred_channel_key,
            'restored_historical_context_label': restored.view_model().restored_historical_context_label,
            'session_note_count': restored.view_model().session_note_count,
            'pending_note_draft': restored.view_model().pending_note_draft,
        },
        'recent_summary_ids': [item.summary_id for item in restored.recent_persisted_summaries(limit=5)],
        'flight_record': restored.session_flight_record(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Emit a deterministic bench-persistence diagnostic inventory.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', default='')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    payload = build_inventory()
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
