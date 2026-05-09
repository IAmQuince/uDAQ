from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    package_root = Path(__file__).resolve().parents[2]
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.qt_shell import build_visible_shell_spec_for_demo, detect_gui_dependencies
    from universaldaq.ui.live_runtime import LiveRuntimeEngine
    from universaldaq.ui.workspace_design import default_workspace_task_maps

    spec = build_visible_shell_spec_for_demo()
    live_runtime = LiveRuntimeEngine()
    payload = {
        'shell_title': spec.shell_title,
        'persistent_info_bar_required': spec.persistent_info_bar_required,
        'right_default_control_dock': spec.right_default_control_dock,
        'launch_entry_point': spec.launch_entry_point,
        'graph_engine_label': spec.graph_engine_label,
        'menus': [
            {
                'menu_id': menu.menu_id,
                'label': menu.label,
                'actions': [action.action_id for action in menu.actions],
            }
            for menu in spec.menus
        ],
        'workspaces': [workspace.workspace_id for workspace in spec.workspaces],
        'dependencies': detect_gui_dependencies(),
        'user_demo_scenarios': [scenario.scenario_id for scenario in spec.foundation.user_demo_mode.scenarios],
        'mode_actions': {
            menu.menu_id: [
                {'action_id': action.action_id, 'enabled': action.enabled, 'checked': action.checked}
                for action in menu.actions
            ]
            for menu in spec.menus
            if menu.menu_id == 'mode'
        },
        'live_runtime_inventory': live_runtime.inventory(),
        'workspace_task_maps': [item.workspace_id for item in default_workspace_task_maps()],
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
