from __future__ import annotations

import importlib
import json
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

import pytest


_PENDING_SESSION_API_REASON = (
    'pending durable session/checkpoint/replay API merge from GPT-5.5; '
    'expected universaldaq.session with DurableSessionService and review-only replay support'
)


def _load_session_module() -> Any:
    try:
        return importlib.import_module('universaldaq.session')
    except ModuleNotFoundError:
        pytest.skip(_PENDING_SESSION_API_REASON)


def accepted_session_api_names() -> tuple[str, ...]:
    module = _load_session_module()
    names = []
    if hasattr(module, 'DurableSession'):
        names.append('DurableSession')
    if hasattr(module, 'SessionCheckpoint'):
        names.append('SessionCheckpoint')
    if hasattr(module, 'ReplayView'):
        names.append('ReplayView')
    if hasattr(module, 'ReplaySession'):
        names.append('ReplaySession')
    if hasattr(module, 'SessionValidationResult'):
        names.append('SessionValidationResult')
    if hasattr(module, 'DurableSessionService'):
        names.append('DurableSessionService')
    for name in (
        'create_session',
        'create_checkpoint_from_runtime_state',
        'save_session',
        'load_session',
        'build_replay_from_checkpoint',
    ):
        if hasattr(module, name):
            names.append(name)
    return tuple(names)


def make_session_service() -> Any:
    module = _load_session_module()
    service_type = getattr(module, 'DurableSessionService', None)
    if service_type is not None:
        return service_type()
    pytest.skip(
        'pending DurableSessionService-compatible session API; '
        'top-level helpers are not available on this branch'
    )


def canonical_json(payload: Mapping[str, object]) -> str:
    module = _load_session_module()
    helper = getattr(module, 'canonical_json', None)
    if callable(helper):
        return str(helper(payload))
    return json.dumps(payload, sort_keys=True, separators=(',', ':'))


def state_hash(payload: Mapping[str, object]) -> str:
    module = _load_session_module()
    helper = getattr(module, 'state_hash', None)
    if callable(helper):
        return str(helper(payload))
    return canonical_json(payload)


def to_dict(value: Any) -> dict[str, object]:
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}
    for method_name in ('to_dict', 'as_dict', 'model_dump', 'dict'):
        method = getattr(value, method_name, None)
        if callable(method):
            payload = method()
            if isinstance(payload, Mapping):
                return {str(key): item for key, item in payload.items()}
    raise AssertionError(f'value of type {type(value)!r} is not serializable to dict')


def create_session(
    *,
    session_id: str,
    created_at: int,
    mode: Any | None = None,
) -> Any:
    service = make_session_service()
    kwargs: dict[str, object] = {'session_id': session_id, 'created_at': created_at}
    if mode is not None:
        kwargs['mode'] = mode
    return service.create_session(**kwargs)


def create_checkpoint(
    *,
    session: Any,
    checkpoint_id: str,
    timestamp: int,
    runtime_snapshot: Any,
) -> Any:
    service = make_session_service()
    module = _load_session_module()
    helper = getattr(module, 'create_checkpoint_from_runtime_state', None)
    if callable(helper):
        return helper(
            session=session,
            checkpoint_id=checkpoint_id,
            timestamp=timestamp,
            runtime_snapshot=runtime_snapshot,
        )
    return service.create_checkpoint(
        session=session,
        checkpoint_id=checkpoint_id,
        timestamp=timestamp,
        runtime_snapshot=runtime_snapshot,
    )


def append_checkpoint(*, session: Any, checkpoint: Any) -> Any:
    service = make_session_service()
    append = getattr(service, 'append_checkpoint', None)
    if callable(append):
        return append(session=session, checkpoint=checkpoint)
    with_checkpoint = getattr(session, 'with_checkpoint', None)
    if callable(with_checkpoint):
        return with_checkpoint(checkpoint)
    raise AssertionError('session API cannot append a checkpoint')


def validate_checkpoint(checkpoint: Any) -> Any:
    service = make_session_service()
    validator = getattr(service, 'validate_checkpoint', None)
    if not callable(validator):
        pytest.skip('pending session checkpoint validation API on DurableSessionService')
    return validator(checkpoint)


def validate_session(session: Any) -> Any:
    service = make_session_service()
    validator = getattr(service, 'validate_session', None)
    if not callable(validator):
        pytest.skip('pending session validation API on DurableSessionService')
    return validator(session)


def save_session(*, session: Any, path: Path) -> Path:
    service = make_session_service()
    saver = getattr(service, 'save_session', None)
    if callable(saver):
        return Path(saver(session=session, path=path))
    module = _load_session_module()
    helper = getattr(module, 'save_session', None)
    if callable(helper):
        return Path(helper(session=session, path=path))
    pytest.skip('pending session save API')


def load_session(*, path: Path) -> Any:
    service = make_session_service()
    loader = getattr(service, 'load_session', None)
    if callable(loader):
        return loader(path=path)
    module = _load_session_module()
    helper = getattr(module, 'load_session', None)
    if callable(helper):
        return helper(path=path)
    pytest.skip('pending session load API')


def save_checkpoint(*, checkpoint: Any, path: Path) -> Path:
    service = make_session_service()
    saver = getattr(service, 'save_checkpoint', None)
    if callable(saver):
        return Path(saver(checkpoint=checkpoint, path=path))
    pytest.skip('pending checkpoint save API')


def load_checkpoint(*, path: Path) -> Any:
    service = make_session_service()
    loader = getattr(service, 'load_checkpoint', None)
    if callable(loader):
        return loader(path=path)
    pytest.skip('pending checkpoint load API')


def build_replay_from_checkpoint(
    *,
    session: Any,
    checkpoint: Any,
    replay_id: str,
    created_at: int,
) -> Any:
    service = make_session_service()
    module = _load_session_module()
    helper = getattr(module, 'build_replay_from_checkpoint', None)
    if callable(helper):
        return helper(
            session=session,
            checkpoint=checkpoint,
            replay_id=replay_id,
            created_at=created_at,
        )
    builder = getattr(service, 'build_replay_view', None)
    if callable(builder):
        return builder(
            session=session,
            checkpoint=checkpoint,
            replay_id=replay_id,
            created_at=created_at,
        )
    builder = getattr(service, 'build_replay_from_latest', None)
    if callable(builder):
        session = append_checkpoint(session=session, checkpoint=checkpoint)
        return builder(
            session=session,
            replay_id=replay_id,
            created_at=created_at,
        )
    pytest.skip('pending replay builder API')
