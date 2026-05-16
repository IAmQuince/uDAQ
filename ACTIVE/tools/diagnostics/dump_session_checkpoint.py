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

ARTIFACT_VERSION = 'udq.session_checkpoint.diagnostic.v1'
DEFAULT_PROVIDER_CANDIDATES: tuple[str, ...] = (
    'universaldaq.session:create_checkpoint_from_runtime_state',
    'universaldaq.session:build_session_checkpoint',
    'universaldaq.session:get_current_session_checkpoint',
    'universaldaq.session.checkpoint:create_checkpoint_from_runtime_state',
    'universaldaq.session.checkpoint:build_session_checkpoint',
    'universaldaq.session.services:build_session_checkpoint',
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
    'Authoritative session checkpoint API is pending leader branch integration.',
    'Session checkpoint artifact is diagnostic-only and non-live.',
)
KNOWN_LIMITATIONS: tuple[str, ...] = (
    'Replay diagnostics remain non-live and must not be treated as current hardware truth.',
    'Hardware writes and physical output authority remain disabled.',
    'Production historian behavior is not implemented in this diagnostic helper.',
)
REQUIRED_FIELDS: tuple[str, ...] = (
    'artifact_id',
    'artifact_version',
    'generated_at_utc',
    'package_root',
    'git_branch',
    'git_commit',
    'python_version',
    'session_api_available',
    'session_model_version',
    'session_id',
    'checkpoint_id',
    'checkpoint_timestamp',
    'runtime_snapshot_id',
    'runtime_state_model_version',
    'replay_is_live',
    'hardware_mutation_enabled',
    'live_mapping_apply_enabled',
    'checkpoint_count',
    'event_count',
    'warning_count',
    'degraded_count',
    'stale_count',
    'unavailable_count',
    'validation_summary',
    'warnings',
    'known_limitations',
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


def _coerce_mapping(payload: object) -> Mapping[str, object]:
    if isinstance(payload, Mapping):
        return {str(key): value for key, value in payload.items()}
    for method_name in ('to_dict', 'as_dict', 'model_dump'):
        method = getattr(payload, method_name, None)
        if method is None or not callable(method):
            continue
        candidate = method()
        if isinstance(candidate, Mapping):
            return {str(key): value for key, value in candidate.items()}
    raise TypeError('session checkpoint provider must return mapping or object with to_dict/as_dict/model_dump')


def _call_provider(provider: Any, package_root: Path) -> Mapping[str, object]:
    signature = inspect.signature(provider)
    kwargs: dict[str, object] = {}
    if 'package_root' in signature.parameters:
        kwargs['package_root'] = package_root
    payload = provider(**kwargs)
    return _coerce_mapping(payload)


def _discover_session_checkpoint(
    package_root: Path,
    provider_override: str | None,
) -> tuple[bool, Mapping[str, object] | None, str | None, str | None]:
    candidate_refs: list[str] = []
    if provider_override:
        candidate_refs.append(provider_override)
    env_provider = os.environ.get('UDQ_SESSION_CHECKPOINT_PROVIDER')
    if env_provider:
        candidate_refs.append(env_provider)
    candidate_refs.extend(DEFAULT_PROVIDER_CANDIDATES)
    last_error: str | None = None
    for provider_ref in candidate_refs:
        try:
            provider = _load_provider(provider_ref)
            payload = _call_provider(provider, package_root)
            return True, payload, provider_ref, None
        except Exception as exc:  # pragma: no cover - fallback path
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


def _normalize_session_payload(payload: Mapping[str, object]) -> dict[str, object]:
    normalized = {str(key): value for key, value in payload.items()}

    checkpoint = payload.get('checkpoint')
    if isinstance(checkpoint, Mapping):
        normalized.setdefault('checkpoint_id', checkpoint.get('checkpoint_id'))
        normalized.setdefault('checkpoint_timestamp', checkpoint.get('timestamp'))
        normalized.setdefault('session_id', checkpoint.get('session_id'))
        normalized.setdefault('runtime_snapshot_id', checkpoint.get('runtime_snapshot_id'))

    runtime_snapshot = payload.get('runtime_snapshot')
    if isinstance(runtime_snapshot, Mapping):
        normalized.setdefault('runtime_snapshot_id', runtime_snapshot.get('snapshot_id'))
        normalized.setdefault('runtime_state_model_version', runtime_snapshot.get('model_version'))

    identity = payload.get('identity')
    if isinstance(identity, Mapping):
        normalized.setdefault('session_model_version', identity.get('model_version'))
        normalized.setdefault('session_id', identity.get('session_id'))
        normalized.setdefault('checkpoint_id', identity.get('checkpoint_id'))

    warnings = payload.get('warnings')
    if isinstance(warnings, list | tuple):
        normalized.setdefault('warning_count', len(warnings))
    normalized.setdefault('checkpoint_count', 1 if normalized.get('checkpoint_id') else 0)
    normalized.setdefault('event_count', _read_int(normalized, 'event_count', default=0))
    normalized.setdefault('warning_count', _read_int(normalized, 'warning_count', default=0))
    normalized.setdefault('degraded_count', _read_int(normalized, 'degraded_count', default=0))
    normalized.setdefault('stale_count', _read_int(normalized, 'stale_count', default=0))
    normalized.setdefault('unavailable_count', _read_int(normalized, 'unavailable_count', default=0))
    normalized.setdefault('replay_is_live', False)
    normalized.setdefault('hardware_mutation_enabled', False)
    normalized.setdefault('live_mapping_apply_enabled', False)
    return normalized


def _build_demo_payload(now: datetime) -> dict[str, object]:
    return {
        'session_model_version': 'udq.session.checkpoint.demo.v1',
        'session_id': 'demo-session',
        'checkpoint_id': f'demo-checkpoint-{_timestamp_slug(now)}',
        'checkpoint_timestamp': _iso_utc(now),
        'runtime_snapshot_id': 'demo-runtime-snapshot',
        'runtime_state_model_version': 'udq.runtime.state.v1',
        'checkpoint_count': 1,
        'event_count': 3,
        'warning_count': 1,
        'degraded_count': 0,
        'stale_count': 0,
        'unavailable_count': 0,
        'replay_is_live': False,
        'hardware_mutation_enabled': False,
        'live_mapping_apply_enabled': False,
    }


def build_session_checkpoint_artifact(
    *,
    package_root: Path,
    strict: bool,
    include_git: bool,
    demo: bool,
    provider_override: str | None,
) -> tuple[dict[str, object], int]:
    now = _now_utc()
    generated_at_utc = _iso_utc(now)
    artifact_id = f'udq-session-checkpoint-{_timestamp_slug(now)}'
    git_branch, git_commit = _read_git_metadata(package_root, include_git=include_git)

    provider_ref: str | None = None
    provider_error: str | None = None
    session_available = False
    if demo:
        payload = _build_demo_payload(now)
        warnings = ['Demo mode enabled; emitted simulated non-live checkpoint artifact.']
    else:
        session_available, provider_payload, provider_ref, provider_error = _discover_session_checkpoint(
            package_root,
            provider_override,
        )
        warnings = [] if session_available else list(DEFAULT_WARNINGS)
        if provider_error and not session_available:
            warnings.append(f'Session checkpoint provider probe failed: {provider_error}')
        payload = _normalize_session_payload({} if provider_payload is None else provider_payload)

    artifact: dict[str, object] = {
        'artifact_id': artifact_id,
        'artifact_version': ARTIFACT_VERSION,
        'generated_at_utc': generated_at_utc,
        'package_root': str(package_root),
        'git_branch': git_branch,
        'git_commit': git_commit,
        'python_version': platform.python_version(),
        'session_api_available': session_available and not demo,
        'session_model_version': _read_str(payload, 'session_model_version', 'model_version'),
        'session_id': _read_str(payload, 'session_id'),
        'checkpoint_id': _read_str(payload, 'checkpoint_id', 'id'),
        'checkpoint_timestamp': _read_str(payload, 'checkpoint_timestamp', 'timestamp', 'created_at'),
        'runtime_snapshot_id': _read_str(payload, 'runtime_snapshot_id', 'snapshot_id'),
        'runtime_state_model_version': _read_str(payload, 'runtime_state_model_version'),
        'replay_is_live': False,
        'hardware_mutation_enabled': False,
        'live_mapping_apply_enabled': False,
        'checkpoint_count': _read_int(payload, 'checkpoint_count', default=0),
        'event_count': _read_int(payload, 'event_count', default=0),
        'warning_count': _read_int(payload, 'warning_count', default=len(warnings)),
        'degraded_count': _read_int(payload, 'degraded_count', default=0),
        'stale_count': _read_int(payload, 'stale_count', default=0),
        'unavailable_count': _read_int(payload, 'unavailable_count', default=0),
        'optional_dependency_status': _read_optional_dependency_status(),
        'validation_summary': {},
        'warnings': warnings,
        'known_limitations': list(KNOWN_LIMITATIONS),
    }
    if provider_ref is not None:
        artifact['session_checkpoint_provider'] = provider_ref

    strict_fail_reasons: list[str] = []
    if strict and not artifact['session_api_available']:
        strict_fail_reasons.append('strict mode requires session checkpoint API availability')
    if _read_bool(payload, 'replay_is_live', default=False):
        strict_fail_reasons.append('provider reported replay as live')
    if _read_bool(payload, 'hardware_mutation_enabled', default=False):
        strict_fail_reasons.append('provider reported hardware mutation enabled')
    if _read_bool(payload, 'live_mapping_apply_enabled', default=False):
        strict_fail_reasons.append('provider reported live mapping apply enabled')

    missing_required_fields = [field for field in REQUIRED_FIELDS if field not in artifact]
    validation_passed = not strict_fail_reasons and not missing_required_fields
    artifact['validation_summary'] = {
        'required_fields_present': len(missing_required_fields) == 0,
        'missing_required_fields': missing_required_fields,
        'strict_mode': strict,
        'strict_fail_reasons': strict_fail_reasons,
        'validation_passed': validation_passed,
    }

    exit_code = 2 if strict and strict_fail_reasons else 0
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
        description='Emit diagnostic session checkpoint artifact JSON without requiring hardware.',
    )
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--output', help='Optional path to write JSON artifact output.')
    parser.add_argument('--pretty', action='store_true', help='Pretty-print JSON output.')
    parser.add_argument('--strict', action='store_true', help='Fail if session checkpoint API is unavailable.')
    parser.add_argument('--demo', action='store_true', help='Emit a simulated non-live checkpoint artifact.')
    parser.add_argument('--include-git', action='store_true', help='Include git branch/commit metadata when available.')
    parser.add_argument(
        '--provider',
        help='Optional session checkpoint provider as module:function.',
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_root = Path(args.package_root).resolve()
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    artifact, exit_code = build_session_checkpoint_artifact(
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
