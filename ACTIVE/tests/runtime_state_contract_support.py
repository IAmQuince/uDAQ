from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from typing import Any

import pytest

import universaldaq.runtime as runtime_module

_PENDING_API_REASON = (
    'pending authoritative runtime-state API on universaldaq.runtime; '
    'expected RuntimeStateSnapshot and/or build_runtime_state_snapshot'
)


def load_authoritative_runtime_state_api() -> tuple[type[Any] | None, Any | None]:
    snapshot_type = getattr(runtime_module, 'RuntimeStateSnapshot', None)
    builder = getattr(runtime_module, 'build_runtime_state_snapshot', None)
    if snapshot_type is None and builder is None:
        pytest.skip(_PENDING_API_REASON)
    return snapshot_type, builder


def materialize_runtime_state_snapshot(payload: Mapping[str, Any]) -> Any:
    snapshot_type, builder = load_authoritative_runtime_state_api()
    attempts: list[str] = []
    if builder is not None:
        for label, factory in (
            ('build_runtime_state_snapshot(payload=payload)', lambda: builder(payload=payload)),
            ('build_runtime_state_snapshot(snapshot=payload)', lambda: builder(snapshot=payload)),
            ('build_runtime_state_snapshot(data=payload)', lambda: builder(data=payload)),
            ('build_runtime_state_snapshot(**payload)', lambda: builder(**payload)),
            ('build_runtime_state_snapshot(payload)', lambda: builder(payload)),
        ):
            try:
                return factory()
            except TypeError as exc:
                attempts.append(f'{label}: {exc}')
    if snapshot_type is not None:
        if hasattr(snapshot_type, 'from_dict'):
            try:
                return snapshot_type.from_dict(payload)
            except TypeError as exc:
                attempts.append(f'RuntimeStateSnapshot.from_dict(payload): {exc}')
        for label, factory in (
            ('RuntimeStateSnapshot(**payload)', lambda: snapshot_type(**payload)),
            ('RuntimeStateSnapshot(payload)', lambda: snapshot_type(payload)),
        ):
            try:
                return factory()
            except TypeError as exc:
                attempts.append(f'{label}: {exc}')
    raise AssertionError(
        'authoritative runtime-state API exists but the contract payload could not be materialized:\n'
        + '\n'.join(attempts)
    )


def runtime_state_to_dict(snapshot: Any) -> dict[str, Any]:
    if isinstance(snapshot, Mapping):
        return {str(key): value for key, value in snapshot.items()}
    for method_name in ('as_dict', 'to_dict', 'model_dump', 'dict'):
        method = getattr(snapshot, method_name, None)
        if callable(method):
            payload = method()
            if isinstance(payload, Mapping):
                return {str(key): value for key, value in payload.items()}
    if is_dataclass(snapshot):
        payload = asdict(snapshot)
        if isinstance(payload, Mapping):
            return {str(key): value for key, value in payload.items()}
    raise AssertionError(
        'authoritative runtime-state snapshot is not serializable through as_dict(), '
        'to_dict(), model_dump(), dict(), or dataclasses.asdict()'
    )


def canonical_runtime_state_json(snapshot: Any) -> str:
    return json.dumps(runtime_state_to_dict(snapshot), sort_keys=True, separators=(',', ':'))


def build_empty_runtime_state_payload() -> dict[str, Any]:
    return {
        'model_version': 'udq.runtime_state.v1',
        'snapshot_id': 'RTSNAP-EMPTY-001',
        'captured_at': 1000,
        'runtime_mode': 'simulated',
        'devices': [],
        'points': [],
        'mappings': {
            'drafts': [],
            'applied': [],
        },
        'signals': [],
        'variables': [],
        'command_posture': {
            'authority': 'review_only',
            'hardware_write_authorized': False,
        },
        'safety_posture': {
            'state': 'write_inhibited',
            'hardware_write_authorized': False,
        },
        'logic_posture': {
            'deployment_state': 'draft_only',
        },
        'review_projection': {
            'summary': 'empty runtime state',
        },
    }


def build_degraded_runtime_state_payload() -> dict[str, Any]:
    payload = build_empty_runtime_state_payload()
    payload.update(
        {
            'snapshot_id': 'RTSNAP-DEGRADED-001',
            'captured_at': 2000,
            'devices': [
                {
                    'device_id': 'DEV-SIM-001',
                    'mode': 'simulated',
                    'availability_state': 'simulated',
                    'requested_state': 'discover',
                    'applied_state': 'simulated_attached',
                    'observed_state': 'simulated_attached',
                },
                {
                    'device_id': 'DEV-REAL-001',
                    'mode': 'physical',
                    'availability_state': 'unavailable',
                    'requested_state': 'discover',
                    'applied_state': 'not_attached',
                    'observed_state': 'device_missing',
                },
                {
                    'device_id': 'DEV-REAL-002',
                    'mode': 'physical',
                    'availability_state': 'recovering',
                    'requested_state': 'connected',
                    'applied_state': 'recovering',
                    'observed_state': 'stale',
                },
            ],
            'signals': [
                {
                    'signal_id': 'SIG-001',
                    'requested_state': {'value': 10},
                    'applied_state': {'value': 9},
                    'observed_state': {'value': 8},
                    'freshness_state': 'stale',
                },
                {
                    'signal_id': 'SIG-002',
                    'requested_state': {'value': None},
                    'applied_state': {'value': None},
                    'observed_state': {'value': None},
                    'freshness_state': 'unknown',
                },
            ],
            'mappings': {
                'drafts': [
                    {
                        'mapping_id': 'MAP-DRAFT-001',
                        'posture': 'sandbox-only',
                        'authoritative_applied': False,
                    },
                ],
                'applied': [
                    {
                        'mapping_id': 'MAP-APPLIED-001',
                        'posture': 'authoritative_applied',
                        'authoritative_applied': True,
                    },
                ],
            },
            'command_posture': {
                'authority': 'review_only',
                'hardware_write_authorized': False,
                'requested_state': 'armed',
                'applied_state': 'blocked',
                'observed_state': 'not_executed',
            },
            'safety_posture': {
                'state': 'degraded',
                'hardware_write_authorized': False,
                'interlock_open': True,
            },
            'logic_posture': {
                'deployment_state': 'draft_only',
                'runtime_enabled': False,
            },
            'review_projection': {
                'summary': 'degraded runtime state',
            },
        }
    )
    return payload
