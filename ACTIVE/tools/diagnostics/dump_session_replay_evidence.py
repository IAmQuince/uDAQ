from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export deterministic session replay evidence.")
    parser.add_argument("--package-root", default=".")
    parser.add_argument("--output", required=True)
    parser.add_argument("--session-id", default="SES-EVIDENCE-001")
    parser.add_argument("--checkpoint-id", default="CHK-EVIDENCE-001")
    parser.add_argument("--replay-id", default="REPLAY-EVIDENCE-001")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_root = Path(args.package_root).resolve()
    src_root = package_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from universaldaq.runtime import build_authoritative_runtime_snapshot
    from universaldaq.session import DurableSessionService

    service = DurableSessionService()
    session = service.create_session(session_id=args.session_id, created_at=200)
    checkpoint = service.create_checkpoint(
        session=session,
        checkpoint_id=args.checkpoint_id,
        timestamp=201,
        runtime_snapshot=build_authoritative_runtime_snapshot(timestamp=201, sequence_number=2),
    )
    session = service.append_checkpoint(session=session, checkpoint=checkpoint)
    evidence = service.build_replay_evidence(
        session=session,
        checkpoint=checkpoint,
        replay_id=args.replay_id,
        created_at=202,
    )
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        f"session-replay-evidence: session={evidence['session_id']} "
        f"checkpoint={evidence['checkpoint_id']} hash={evidence['replay_evidence_hash']} "
        f"authority={evidence['authority_scope']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
