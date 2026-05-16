from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from tools.diagnostics import dump_session_checkpoint as checkpoint_tool


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Validate a session checkpoint diagnostic JSON artifact.',
    )
    parser.add_argument('--input', required=True, help='Path to session checkpoint JSON artifact.')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print validation output.')
    parser.add_argument(
        '--require-api',
        action='store_true',
        help='Require session_api_available=true for successful validation.',
    )
    return parser.parse_args(argv)


def _validate_payload(payload: dict[str, Any], require_api: bool) -> tuple[dict[str, Any], int]:
    missing_required = [field for field in checkpoint_tool.REQUIRED_FIELDS if field not in payload]
    invariant_violations: list[str] = []
    if payload.get('replay_is_live') is not False:
        invariant_violations.append('replay_is_live must be false')
    if payload.get('hardware_mutation_enabled') is not False:
        invariant_violations.append('hardware_mutation_enabled must be false')
    if payload.get('live_mapping_apply_enabled') is not False:
        invariant_violations.append('live_mapping_apply_enabled must be false')
    if require_api and payload.get('session_api_available') is not True:
        invariant_violations.append('session_api_available must be true when --require-api is set')

    valid = not missing_required and not invariant_violations
    report = {
        'valid': valid,
        'required_fields_present': not missing_required,
        'missing_required_fields': missing_required,
        'invariant_violations': invariant_violations,
        'warning_count': int(payload.get('warning_count', 0) or 0),
        'session_api_available': bool(payload.get('session_api_available', False)),
    }
    return report, (0 if valid else 2)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_path = Path(args.input).resolve()
    payload = json.loads(input_path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise TypeError('session checkpoint artifact must be a JSON object')
    report, exit_code = _validate_payload(payload, require_api=bool(args.require_api))
    report['input_path'] = str(input_path)
    indent = 2 if args.pretty else None
    separators = None if args.pretty else (',', ':')
    print(json.dumps(report, indent=indent, sort_keys=True, separators=separators))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
