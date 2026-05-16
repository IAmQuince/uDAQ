from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

COMPARE_FIELDS: tuple[str, ...] = (
    'session_model_version',
    'session_id',
    'checkpoint_id',
    'checkpoint_timestamp',
    'runtime_snapshot_id',
    'runtime_state_model_version',
    'checkpoint_count',
    'event_count',
    'warning_count',
    'degraded_count',
    'stale_count',
    'unavailable_count',
    'session_api_available',
    'replay_is_live',
    'hardware_mutation_enabled',
    'live_mapping_apply_enabled',
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Compare two session checkpoint diagnostic artifacts.',
    )
    parser.add_argument('--left', required=True, help='Path to baseline artifact.')
    parser.add_argument('--right', required=True, help='Path to comparison artifact.')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print output.')
    return parser.parse_args(argv)


def _load(path: str) -> dict[str, Any]:
    payload = json.loads(Path(path).resolve().read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise TypeError(f'checkpoint artifact must be JSON object: {path}')
    return payload


def _compare(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    changed: list[dict[str, Any]] = []
    for field in COMPARE_FIELDS:
        if left.get(field) != right.get(field):
            changed.append(
                {
                    'field': field,
                    'left': left.get(field),
                    'right': right.get(field),
                }
            )
    return {
        'changed_field_count': len(changed),
        'fields_changed': changed,
        'same_session_id': left.get('session_id') == right.get('session_id'),
        'same_runtime_snapshot_id': left.get('runtime_snapshot_id') == right.get('runtime_snapshot_id'),
        'left_checkpoint_id': left.get('checkpoint_id'),
        'right_checkpoint_id': right.get('checkpoint_id'),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    left = _load(args.left)
    right = _load(args.right)
    report = _compare(left, right)
    report['left_path'] = str(Path(args.left).resolve())
    report['right_path'] = str(Path(args.right).resolve())
    indent = 2 if args.pretty else None
    separators = None if args.pretty else (',', ':')
    print(json.dumps(report, indent=indent, sort_keys=True, separators=separators))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
