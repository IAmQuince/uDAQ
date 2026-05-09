from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    package_root = Path(__file__).resolve().parents[2]
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.common import GraphMode, as_event_time
    from universaldaq.ui import (
        FirstSignalCardViewModel,
        GraphPanelViewModel,
        ShellViewModel,
        TrustedSessionSummary,
        dump_operator_shell_foundation_dict,
    )

    shell = ShellViewModel(
        page='operate',
        graph_panel=GraphPanelViewModel(
            mode=GraphMode.LIVE,
            page='operate',
            visible_trace_count=4,
            status_label='interactive',
        ),
        authority_label='interactive',
        first_signal_summary=FirstSignalCardViewModel(
            signal_id='SIG-DEMO-001',
            display_name='garage_temp_filtered',
            point_key='TEMP-001',
            point_class='analog',
            latest_value='21.2',
            quality_label='simulated',
            latest_timestamp=as_event_time(1),
            engineering_units='C',
            freshness_label='simulated',
            provenance_label='Demo Device / garage_temp_filtered',
        ),
        trusted_session_summary=TrustedSessionSummary(
            lifecycle_state='connected',
            graph_status_label='live',
            live_numeric_visible=True,
            graph_visible=True,
            trace_point_count=12,
            session_event_count=3,
            ready_for_operator=True,
            signal_freshness_label='simulated',
            control_mode_label='view_only',
            active_alarm_count=1,
            unacknowledged_alarm_count=1,
            highest_active_severity='warning',
            recent_action_count=2,
            flight_record_ready=True,
        ),
        preferred_device_key='DEMO-FIRST-SIGNAL-001',
        preferred_channel_key='garage_temp_filtered',
        restored_historical_context_label='demo runtime context only',
    )
    print(json.dumps(dump_operator_shell_foundation_dict(shell=shell, demo_active=True, active_scenario_id='logic_control_demo'), indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
