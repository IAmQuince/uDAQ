from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    src_root = package_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.runtime import build_authoritative_runtime_snapshot
    from universaldaq.session import (
        DurableSessionService,
        FileSystemSessionCheckpointStore,
        restore_review_session,
    )

    service = DurableSessionService()
    session = service.create_session(session_id="SES-SMOKE-001", created_at=100)
    snapshot = build_authoritative_runtime_snapshot(timestamp=101, sequence_number=1)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id="CHK-SMOKE-001",
        timestamp=102,
        runtime_snapshot=snapshot,
    )
    output_root = (
        Path(args.output).resolve()
        if args.output
        else package_root / "audit_reports" / "testing" / "session-smoke"
    )
    store = FileSystemSessionCheckpointStore(output_root)
    store.save_checkpoint(checkpoint)
    loaded = store.load_checkpoint(
        session_id=session.session_id, checkpoint_id=checkpoint.checkpoint_id
    )
    restored = restore_review_session(loaded)
    replay = service.build_replay_view(
        session=service.append_checkpoint(session=session, checkpoint=loaded),
        checkpoint=loaded,
        replay_id="REPLAY-SMOKE-001",
        created_at=103,
    )
    replay_evidence = service.build_replay_evidence(
        session=service.append_checkpoint(session=session, checkpoint=loaded),
        checkpoint=loaded,
        replay_id="REPLAY-SMOKE-001",
        created_at=103,
    )
    payload = {
        "session_id": session.session_id,
        "checkpoint_id": loaded.checkpoint_id,
        "authority_scope": restored.authority_scope,
        "checkpoint_hash": loaded.checkpoint_hash,
        "runtime_snapshot_hash": loaded.runtime_snapshot_hash,
        "replay_evidence_hash": replay_evidence["replay_evidence_hash"],
        "replay_evidence": replay_evidence,
        "replay_is_live": replay.replay_is_live,
        "hardware_mutation_enabled": replay.safety.hardware_mutation_enabled,
        "live_mapping_apply_enabled": replay.safety.live_mapping_apply_enabled,
        "stored_checkpoint_count": len(store.list_checkpoints(session_id=session.session_id)),
    }
    summary_path = output_root / "session_checkpoint_smoke.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"session-checkpoint-smoke: session={payload['session_id']} "
        f"checkpoint={payload['checkpoint_id']} authority={payload['authority_scope']} "
        f"replay_is_live={payload['replay_is_live']} stored={payload['stored_checkpoint_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
