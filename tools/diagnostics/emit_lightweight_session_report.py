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


def build_controller() -> tuple[ShellController, str]:
    services = build_default_service_registry(load_support_packs=False)
    services.adapters.register(DeterministicWaveformAdapter(adapter_id='DEMO-FIRST-SIGNAL-001'))
    boot = ShellBootstrapper.bootstrap_from_profile(
        profile_snapshot=ProfileSnapshot(
            profile_id=ProfileId('PROF-SESSION-REPORT'),
            workspace_state=WorkspaceState(page='graphing', review_mode=GraphMode.LIVE),
        ),
        authority_surface=AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True),
        graph_session=GraphModeSession.start(GraphMode.LIVE, as_event_time(1)),
        timestamp=as_event_time(2),
        actor_context=ActorContext(actor_id=ActorId('report-operator'), role_class=RoleClass.OPERATOR, origin='local-shell'),
        services=services,
    )
    controller = ShellController.from_bootstrapped_shell(boot)
    device = next(item for item in controller.discover_devices(timestamp=as_event_time(3)) if item.identity.serial_number == 'DEMO-001')
    controller.select_detected_device(device_key=device.device_key, timestamp=as_event_time(4))
    controller.begin_quick_start(timestamp=as_event_time(5))
    controller.poll_adapters(timestamp=as_event_time(6))
    controller.poll_adapters(timestamp=as_event_time(7))
    controller.add_operator_note(note_text='Session report check', timestamp=as_event_time(8), category='operator_note')
    state = controller.save_bench_state(timestamp=as_event_time(9))
    return controller, state.historical_summary.summary_id


def main() -> int:
    parser = argparse.ArgumentParser(description='Emit a deterministic lightweight session report.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--markdown-output', default='')
    parser.add_argument('--json-output', default='')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    controller, summary_id = build_controller()
    report = controller.generate_lightweight_session_report(summary_id=summary_id, timestamp=as_event_time(10))
    if args.markdown_output:
        output_path = package_root / args.markdown_output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report.markdown, encoding='utf-8')
    else:
        print(report.markdown)
    if args.json_output:
        output_path = package_root / args.json_output
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report.payload, indent=2) + '\n', encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
