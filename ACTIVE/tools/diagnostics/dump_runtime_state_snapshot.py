from __future__ import annotations

import argparse
import importlib
import importlib.util
import inspect
import json
import os
import platform
import subprocess
import sys
from collections.abc import Mapping
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ARTIFACT_VERSION = 'udq.runtime_state_snapshot.diagnostic.v1'
DEFAULT_PROVIDER_CANDIDATES: tuple[str, ...] = (
    'universaldaq.runtime.state_snapshot:get_authoritative_runtime_state_snapshot',
    'universaldaq.runtime.state_snapshot:build_authoritative_runtime_state_snapshot',
    'universaldaq.runtime.state_snapshot:get_runtime_state_snapshot',
)
OPTIONAL_DEPENDENCY_MODULES: tuple[str, ...] = (
    'PySide6',
    'pyqtgraph',
    'universaldaq_labjack',
    'universaldaq_rpi',
    'universaldaq_arduino',
    'pymodbus',
)
DEFAULT_WARNINGS: tuple[str, ...] = (
    'Authoritative runtime snapshot API is pending leader branch integration.',
    'Diagnostic artifact is placeholder-only and does not claim live runtime authority.',
)
KNOWN_LIMITATIONS: tuple[str, ...] = (
    'Live mapping apply is not implemented in this diagnostic helper.',
    'Hardware writes and physical output authority remain disabled.',
    'Sandbox mapping state is non-authoritative and must not be interpreted as live state.',
)
REQUIRED_FIELDS: tuple[str, ...] = (
    'artifact_id',
    'artifact_version',
    'generated_at_utc',
    'package_root',
    'git_branch',
    'git_commit',
    'python_version',
    'runtime_state_api_available',
    'runtime_state_model_version',
    'snapshot_id',
    'snapshot_timestamp',
    'device_count',
    'point_count',
    'signal_count',
    'variable_count',
    'mapping_count',
    'sandbox_mapping_count',
    'proposal_mapping_count',
    'applied_mapping_count',
    'stale_count',
    'degraded_count',
    'unavailable_count',
    'command_posture',
    'safety_posture',
    'hardware_mutation_enabled',
    'live_mapping_apply_enabled',
    'sandbox_is_authoritative',
    'optional_dependency_status',
    'warnings',
    'known_limitations',
    'validation_summary',
)


def _now_utc() -> datetime:
    return datetime.now(UTC)


def _iso_utc(now: datetime) -> str:
    return now.isoformat(timespec='seconds').replace('+00:00', 'Z')


def _timestamp_slug(now: datetime) -> str:
    return now.strftime('%Y%m%dT%H%M%SZ')


def _resolve_output_path(package_root: Path, output: str) -> Path:
    output_path = Path(output)
    if output_path.is_absolute():
        return output_path
    return package_root / output_path


def _read_optional_dependency_status() -> dict[str, str]:
    status: dict[str, str] = {}
    for module_name in OPTIONAL_DEPENDENCY_MODULES:
        status[module_name] = 'available' if importlib.util.find_spec(module_name) is not None else 'missing'
    return status


def _git_value(package_root: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ['git', *args],
            cwd=package_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip() or None


def _read_git_metadata(package_root: Path, include_git: bool) -> tuple[str | None, str | None]:
    if not include_git:
        return None, None
    branch = _git_value(package_root, ['rev-parse', '--abbrev-ref', 'HEAD'])
    commit = _git_value(package_root, ['rev-parse', 'HEAD'])
    return branch, commit


def _load_provider(provider_ref: str) -> Any:
    module_name, sep, function_name = provider_ref.partition(':')
    if not sep:
        raise ValueError(f'provider reference must use module:function format: {provider_ref}')
    module = importlib.import_module(module_name)
    provider = getattr(module, function_name)
    if not callable(provider):
        raise TypeError(f'provider is not callable: {provider_ref}')
    return provider


def _call_provider(provider: Any, package_root: Path) -> Mapping[str, object]:
    signature = inspect.signature(provider)
    if len(signature.parameters) == 0:
        payload = provider()
    else:
        payload = provider(package_root=package_root)
    if hasattr(payload, 'to_dict') and callable(payload.to_dict):
        payload = payload.to_dict()
    if not isinstance(payload, Mapping):
        raise TypeError('runtime snapshot provider must return a mapping payload')
    return payload


def _discover_runtime_snapshot(
    package_root: Path,
    provider_override: str | None,
) -> tuple[bool, Mapping[str, object] | None, str | None, str | None]:
    candidate_refs: list[str] = []
    if provider_override:
        candidate_refs.append(provider_override)
    env_provider = os.environ.get('UDQ_RUNTIME_STATE_SNAPSHOT_PROVIDER')
    if env_provider:
        candidate_refs.append(env_provider)
    candidate_refs.extend(DEFAULT_PROVIDER_CANDIDATES)
    last_error: str | None = None
    for provider_ref in candidate_refs:
        try:
            provider = _load_provider(provider_ref)
            payload = _call_provider(provider, package_root)
            return True, payload, provider_ref, None
        except Exception as exc:  # pragma: no cover - bounded fallback behavior
            last_error = f'{provider_ref}: {type(exc).__name__}: {exc}'
    return False, None, None, last_error


def _read_int(payload: Mapping[str, object], *keys: str, default: int = 0) -> int:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    counts = payload.get('counts')
    if isinstance(counts, Mapping):
        for key in keys:
            value = counts.get(key)
            if isinstance(value, bool):
                continue
            if isinstance(value, int):
                return value
            if isinstance(value, str) and value.isdigit():
                return int(value)
    return default


def _read_str(payload: Mapping[str, object], *keys: str) -> str | None:
    for key in keys:
        value = payload.get(key)
        if value is None:
            continue
        return str(value)
    return None


def _read_bool(payload: Mapping[str, object], *keys: str, default: bool = False) -> bool:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {'true', 'yes', '1'}:
                return True
            if normalized in {'false', 'no', '0'}:
                return False
    return default


def _truth_count(payload: Mapping[str, object], key: str) -> int:
    truth = payload.get(key)
    if not isinstance(truth, Mapping):
        return 0
    value = truth.get('value')
    if not isinstance(value, Mapping):
        return 0
    count = value.get('count')
    if isinstance(count, int) and not isinstance(count, bool):
        return count
    return 0


def _normalize_runtime_snapshot_payload(payload: Mapping[str, object]) -> dict[str, object]:
    normalized = {str(key): value for key, value in payload.items()}
    identity = payload.get('identity')
    if isinstance(identity, Mapping):
        normalized.setdefault('model_version', identity.get('model_version'))
        normalized.setdefault('snapshot_id', identity.get('snapshot_id'))
        normalized.setdefault('snapshot_timestamp', identity.get('timestamp'))

    devices = payload.get('devices')
    points = payload.get('points')
    signals = payload.get('signals')
    variables = payload.get('variables')
    mappings = payload.get('mappings')
    if isinstance(devices, list | tuple):
        normalized.setdefault('device_count', len(devices))
    if isinstance(points, list | tuple):
        normalized.setdefault('point_count', len(points))
    if isinstance(signals, list | tuple):
        normalized.setdefault('signal_count', len(signals))
    if isinstance(variables, list | tuple):
        normalized.setdefault('variable_count', len(variables))
    if isinstance(mappings, list | tuple):
        normalized.setdefault('mapping_count', len(mappings))
        normalized.setdefault(
            'sandbox_mapping_count',
            sum(1 for item in mappings if isinstance(item, Mapping) and item.get('authority_zone') == 'sandbox'),
        )
        normalized.setdefault(
            'proposal_mapping_count',
            sum(
                1
                for item in mappings
                if isinstance(item, Mapping)
                and item.get('lifecycle') in {'draft', 'proposal', 'preflight', 'review', 'prepared-request', 'diagnostic'}
            ),
        )
        normalized.setdefault(
            'applied_mapping_count',
            sum(1 for item in mappings if isinstance(item, Mapping) and item.get('authoritative_applied') is True),
        )
        normalized.setdefault(
            'sandbox_is_authoritative',
            any(
                isinstance(item, Mapping)
                and item.get('authority_zone') == 'sandbox'
                and item.get('authoritative_applied') is True
                for item in mappings
            ),
        )

    normalized.setdefault('stale_count', _truth_count(payload, 'stale_state'))
    normalized.setdefault('degraded_count', _truth_count(payload, 'degraded_state'))
    normalized.setdefault('unavailable_count', _truth_count(payload, 'unavailable_state'))

    command_posture = payload.get('command_posture')
    if isinstance(command_posture, Mapping):
        normalized['command_posture'] = command_posture.get('summary') or command_posture.get('posture_id')
        normalized['hardware_mutation_enabled'] = bool(command_posture.get('authority_enabled'))
    safety_posture = payload.get('safety_posture')
    if isinstance(safety_posture, Mapping):
        normalized['safety_posture'] = safety_posture.get('summary') or safety_posture.get('posture_id')
    normalized.setdefault('live_mapping_apply_enabled', False)
    normalized.setdefault('sandbox_is_authoritative', False)
    return normalized


def build_runtime_state_snapshot_artifact(
    *,
    package_root: Path,
    strict: bool,
    include_git: bool,
    demo: bool,
    provider_override: str | None,
) -> tuple[dict[str, object], int]:
    now = _now_utc()
    generated_at_utc = _iso_utc(now)
    artifact_id = f'udq-runtime-state-snapshot-{_timestamp_slug(now)}'
    git_branch, git_commit = _read_git_metadata(package_root, include_git=include_git)
    runtime_available, snapshot_payload, provider_ref, provider_error = _discover_runtime_snapshot(
        package_root,
        provider_override,
    )
    warnings = list(DEFAULT_WARNINGS)
    if runtime_available:
        warnings = []
    if provider_error and not runtime_available:
        warnings.append(f'Runtime snapshot provider probe failed: {provider_error}')
    if demo:
        warnings.append('Demo mode enabled; values remain non-authoritative diagnostic placeholders.')

    payload = {} if snapshot_payload is None else _normalize_runtime_snapshot_payload(snapshot_payload)
    artifact: dict[str, object] = {
        'artifact_id': artifact_id,
        'artifact_version': ARTIFACT_VERSION,
        'generated_at_utc': generated_at_utc,
        'package_root': str(package_root),
        'git_branch': git_branch,
        'git_commit': git_commit,
        'python_version': platform.python_version(),
        'runtime_state_api_available': runtime_available,
        'runtime_state_model_version': _read_str(payload, 'runtime_state_model_version', 'model_version'),
        'snapshot_id': _read_str(payload, 'snapshot_id', 'id'),
        'snapshot_timestamp': _read_str(payload, 'snapshot_timestamp', 'timestamp', 'captured_at'),
        'device_count': _read_int(payload, 'device_count', 'devices'),
        'point_count': _read_int(payload, 'point_count', 'points'),
        'signal_count': _read_int(payload, 'signal_count', 'signals'),
        'variable_count': _read_int(payload, 'variable_count', 'variables'),
        'mapping_count': _read_int(payload, 'mapping_count', 'mappings'),
        'sandbox_mapping_count': _read_int(payload, 'sandbox_mapping_count', default=0),
        'proposal_mapping_count': _read_int(payload, 'proposal_mapping_count', default=0),
        'applied_mapping_count': _read_int(payload, 'applied_mapping_count', default=0),
        'stale_count': _read_int(payload, 'stale_count', default=0),
        'degraded_count': _read_int(payload, 'degraded_count', default=0),
        'unavailable_count': _read_int(payload, 'unavailable_count', default=0),
        'command_posture': _read_str(payload, 'command_posture') or 'non-authoritative',
        'safety_posture': _read_str(payload, 'safety_posture') or 'safe-readonly',
        'hardware_mutation_enabled': _read_bool(payload, 'hardware_mutation_enabled', default=False),
        'live_mapping_apply_enabled': _read_bool(payload, 'live_mapping_apply_enabled', default=False),
        'sandbox_is_authoritative': _read_bool(payload, 'sandbox_is_authoritative', default=False),
        'optional_dependency_status': _read_optional_dependency_status(),
        'warnings': warnings,
        'known_limitations': list(KNOWN_LIMITATIONS),
        'validation_summary': {},
    }
    if provider_ref is not None:
        artifact['runtime_snapshot_provider'] = provider_ref

    strict_fail_reasons: list[str] = []
    if strict and not runtime_available:
        strict_fail_reasons.append('strict mode requires authoritative runtime snapshot API availability')
    if artifact['hardware_mutation_enabled'] is True:
        strict_fail_reasons.append('hardware_mutation_enabled must be false for this diagnostic helper')
    if artifact['live_mapping_apply_enabled'] is True:
        strict_fail_reasons.append('live_mapping_apply_enabled must be false for this diagnostic helper')
    if artifact['sandbox_is_authoritative'] is True:
        strict_fail_reasons.append('sandbox_is_authoritative must be false for this diagnostic helper')

    missing_required_fields = [field for field in REQUIRED_FIELDS if field not in artifact]
    validation_passed = not strict_fail_reasons and not missing_required_fields
    artifact['validation_summary'] = {
        'required_fields_present': len(missing_required_fields) == 0,
        'missing_required_fields': missing_required_fields,
        'strict_mode': strict,
        'strict_fail_reasons': strict_fail_reasons,
        'validation_passed': validation_passed,
    }

    exit_code = 0
    if strict and strict_fail_reasons:
        exit_code = 2
    return artifact, exit_code


def write_artifact(path: Path, artifact: Mapping[str, object], pretty: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    separators = None if pretty else (',', ':')
    path.write_text(
        json.dumps(artifact, indent=indent, sort_keys=True, separators=separators) + '\n',
        encoding='utf-8',
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Emit runtime-state snapshot diagnostic JSON without requiring hardware.',
    )
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', help='Optional path to write JSON artifact output.')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output.')
    parser.add_argument('--strict', action='store_true', help='Fail if authoritative runtime snapshot API is unavailable.')
    parser.add_argument('--demo', action='store_true', help='Emit explicit placeholder warnings for demo diagnostics.')
    parser.add_argument('--include-git', action='store_true', help='Include git branch/commit metadata when available.')
    parser.add_argument(
        '--provider',
        help='Optional runtime snapshot provider as module:function for integration wiring.',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    artifact, exit_code = build_runtime_state_snapshot_artifact(
        package_root=package_root,
        strict=bool(args.strict),
        include_git=bool(args.include_git),
        demo=bool(args.demo),
        provider_override=args.provider,
    )

    if args.output:
        output_path = _resolve_output_path(package_root, args.output)
        write_artifact(output_path, artifact, pretty=bool(args.pretty))

    indent = 2 if args.pretty else None
    separators = None if args.pretty else (',', ':')
    print(json.dumps(artifact, indent=indent, sort_keys=True, separators=separators))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
