from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

if __package__ in {None, ""}:
    _REPO_ROOT = Path(__file__).resolve().parents[2]
    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    lines = [
        "# UniversalDAQ Repeatability Gate",
        "",
        f"- verdict: {payload['verdict']}",
        f"- run_count: {payload['run_count']}",
        f"- consistent_depth_metrics: {payload['consistent_depth_metrics']}",
        f"- consistent_replay_metrics: {payload['consistent_replay_metrics']}",
        f"- minimum_valid_checkpoint_count: {payload['minimum_valid_checkpoint_count']}",
        "",
        "## Runs",
        "",
    ]
    for run in payload['runs']:
        lines.append(
            f"- {run['session_id']}: records={run['persisted_record_count']} checkpoints={run['valid_checkpoint_count']} segments={run['segment_count']} tail={run['replay_tail_record_count']} types={run['replay_tail_record_type_count']}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")



def run_repeatability_gate(*, package_root: Path, output_root: Path, run_count: int = 3) -> dict[str, object]:
    from tools.acceptance.build_populated_review_session import build_populated_review_session

    runs: list[dict[str, object]] = []
    for index in range(1, max(1, run_count) + 1):
        session_id = f"SESSION-REPEAT-{index:03d}"
        review = build_populated_review_session(
            package_root=package_root,
            output_root=output_root / f"run_{index:02d}",
            session_id=session_id,
            cycle_count=18,
            checkpoint_interval_cycles=4,
            start_tick=30 + ((index - 1) * 100),
        )
        run_summary = {
            'session_id': session_id,
            'persisted_record_count': review['history_tier_summary']['cold']['persisted_record_count'],
            'segment_count': review['history_tier_summary']['cold']['segment_count'],
            'valid_checkpoint_count': review['checkpoint_summary']['valid_checkpoint_count'],
            'checkpoint_sequence_ids': list(review['session_depth_summary']['checkpoint_sequence_ids']),
            'replay_tail_record_count': review['replay_report']['tail_record_count'],
            'replay_tail_record_type_count': review['replay_report']['tail_record_type_count'],
            'sample_counts_by_point': dict(review['history_index_report']['sample_counts_by_point']),
            'variable_ids': list(review['history_index_report']['variable_ids']),
        }
        runs.append(run_summary)

    depth_tuples = {
        (
            int(run['persisted_record_count']),
            int(run['segment_count']),
            int(run['valid_checkpoint_count']),
            tuple(int(value) for value in run['checkpoint_sequence_ids']),
        )
        for run in runs
    }
    replay_tuples = {
        (
            int(run['replay_tail_record_count']),
            int(run['replay_tail_record_type_count']),
            tuple(sorted(run['sample_counts_by_point'].items())),
            tuple(run['variable_ids']),
        )
        for run in runs
    }
    payload = {
        'verdict': 'PASS' if len(depth_tuples) == 1 and len(replay_tuples) == 1 and min(int(run['valid_checkpoint_count']) for run in runs) >= 4 else 'FAIL',
        'run_count': len(runs),
        'consistent_depth_metrics': len(depth_tuples) == 1,
        'consistent_replay_metrics': len(replay_tuples) == 1,
        'minimum_valid_checkpoint_count': min(int(run['valid_checkpoint_count']) for run in runs),
        'runs': runs,
    }
    _write_json(output_root / 'repeatability_report.json', payload)
    _write_markdown(output_root / 'repeatability_report.md', payload)
    return payload



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output-root', default='proof/repeatability')
    parser.add_argument('--run-count', type=int, default=3)
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    payload = run_repeatability_gate(package_root=package_root, output_root=output_root, run_count=max(1, args.run_count))
    print(
        f"repeatability-gate: verdict={payload['verdict']} runs={payload['run_count']} consistent_depth={payload['consistent_depth_metrics']} consistent_replay={payload['consistent_replay_metrics']}"
    )
    return 0 if payload['verdict'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
