from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _parse_rect(raw: str):
    parts = [int(item.strip()) for item in raw.split(',')]
    if len(parts) != 4:
        raise ValueError('rect must be x,y,width,height')
    return tuple(parts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--screen', default='0,0,1920,1040')
    parser.add_argument('--requested', default='1600,40,1500,920')
    parser.add_argument('--workspace', default='logic_designer')
    parser.add_argument('--pip', default='1500,800,420,260')
    args = parser.parse_args()

    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.ui.layout_state import (
        LAYOUT_SCHEMA_VERSION,
        Rect,
        clamp_pip_rect,
        clamp_window_rect,
        default_pip_rect,
        default_graph_presentation_for_workspace,
        default_window_rect,
        normalize_splitter_sizes,
        serialize_rect,
    )

    screen = Rect(*_parse_rect(args.screen))
    requested = Rect(*_parse_rect(args.requested))
    pip_requested = Rect(*_parse_rect(args.pip))
    default_rect = default_window_rect(available=screen)
    decision = clamp_window_rect(requested=requested, available=screen)
    pip_bounds = Rect(x=screen.x + 220, y=screen.y + 90, width=max(600, screen.width - 520), height=max(420, screen.height - 200))
    pip_decision = clamp_pip_rect(requested=pip_requested, bounds=pip_bounds)
    default_compact = default_pip_rect(bounds=pip_bounds, mode='compact_pip')
    default_primary = default_pip_rect(bounds=pip_bounds, mode='primary')
    payload = {
        'layout_schema_version': LAYOUT_SCHEMA_VERSION,
        'workspace': args.workspace,
        'graph_presentation': default_graph_presentation_for_workspace(args.workspace),
        'available_screen': serialize_rect(screen),
        'default_window_rect': serialize_rect(default_rect),
        'requested_window_rect': serialize_rect(requested),
        'resolved_window_rect': serialize_rect(decision.resolved),
        'window_rect_clamped': decision.clamped,
        'window_rect_reason': decision.reason,
        'suggested_outer_splitter_sizes': list(normalize_splitter_sizes(total=screen.width, requested=(300, 1180, 340), minimums=(220, 760, 260))),
        'suggested_center_splitter_sizes': list(normalize_splitter_sizes(total=screen.height, requested=(740, 220), minimums=(420, 160))),
        'pip_bounds': serialize_rect(pip_bounds),
        'requested_pip_rect': serialize_rect(pip_requested),
        'resolved_pip_rect': serialize_rect(pip_decision.resolved),
        'default_compact_pip_rect': serialize_rect(default_compact),
        'default_primary_pip_rect': serialize_rect(default_primary),
        'pip_clamped': pip_decision.clamped,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
