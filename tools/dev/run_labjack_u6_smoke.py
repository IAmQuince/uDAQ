from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--real-hardware', action='store_true')
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from tools.dev._u6_field_test_support import snapshot_active_adapter
    from tools.dev._u6_live_support import (
        bootstrap_controller,
        build_services,
        install_labjack_support_pack,
        prepare_u6_live_value_slice,
    )

    services = build_services()
    install_labjack_support_pack(
        services,
        real_hardware=args.real_hardware,
        serial_number=None if args.serial_number == 'AUTO' else args.serial_number,
        simulated_serial_number='470001',
    )
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-SMOKE', actor_id='u6-smoke')
    try:
        prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
    except Exception as exc:
        print(f'labjack-u6-smoke: error={exc}')
        return 2
    review_bundle = prepared.controller.lifecycle_review_bundle()
    adapter_status = snapshot_active_adapter(prepared.controller)
    print(
        'labjack-u6-smoke:'
        f' hardware_mode={"real" if args.real_hardware else "simulated"}'
        f' active_adapter={prepared.active_adapter_id}'
        f' phase={prepared.controller.session.ui_session.device_lifecycle_phase.value}'
        f' projected_points={review_bundle["lifecycle_summary"]["projected_point_count"]}'
        f' published_signals={review_bundle["lifecycle_summary"]["published_signal_count"]}'
        f' highlighted_bindings={len(review_bundle["binding_review_summary"]["highlighted_items"])}'
        f' variable_total={review_bundle["variable_health_summary"]["total_variable_count"]}'
        f' recent_variable_rows={len(review_bundle["runtime_variable_rows"])}'
        f' lifecycle_state={adapter_status.get("lifecycle_state", adapter_status.get("status", "unknown"))}'
        f' startup_classification={adapter_status.get("startup_classification", "n/a")}'
    )
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
