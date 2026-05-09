from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    package_root = Path(__file__).resolve().parents[2]
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.workspace_design import default_workspace_task_maps

    payload = {
        'workspace_task_maps': [
            {
                'workspace_id': item.workspace_id,
                'primary_goal': item.primary_goal,
                'primary_surface': item.primary_surface,
                'graph_mode_default': item.graph_mode_default,
                'secondary_surfaces': list(item.secondary_surfaces),
                'persistent_status': list(item.persistent_status),
                'hidden_or_contextual': list(item.hidden_or_contextual),
            }
            for item in default_workspace_task_maps()
        ]
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
