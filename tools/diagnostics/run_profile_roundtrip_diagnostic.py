from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def main() -> int:
    src_root = Path(__file__).resolve().parents[2] / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.common import GraphMode, ProfileId, TraceId
    from universaldaq.profiles import FileProfileStore, ProfileSnapshot, WorkspaceState

    snapshot = ProfileSnapshot(
        profile_id=ProfileId('PROF-ROUNDTRIP'),
        workspace_state=WorkspaceState(
            page='graphing',
            review_mode=GraphMode.HISTORY,
            visible_traces=(TraceId('TRACE-A'), TraceId('TRACE-B')),
        ),
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        store = FileProfileStore(root=Path(tmpdir))
        path = store.save(snapshot)
        loaded = store.load(ProfileId('PROF-ROUNDTRIP'))
        payload = {
            'saved_path': str(path.name),
            'page': loaded.workspace_state.page,
            'review_mode': loaded.workspace_state.review_mode.value,
            'visible_traces': [str(item) for item in loaded.workspace_state.visible_traces],
        }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
