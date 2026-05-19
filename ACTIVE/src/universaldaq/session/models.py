from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field, replace
from enum import StrEnum

from universaldaq.common import EventTime, as_event_time

SESSION_MODEL_VERSION = 'udq.session.v1'
SESSION_CHECKPOINT_SCHEMA_VERSION = 'udq.session.checkpoint.v1'
SESSION_REPLAY_SCHEMA_VERSION = 'udq.session.replay.v1'
DEFAULT_SOURCE_PACKAGE_ID = 'UDQ-PKG-20260515-03-STATE-R01'


class SessionMode(StrEnum):
    DEMO = 'demo'
    REVIEW = 'review'
    DIAGNOSTIC = 'diagnostic'


class ReplayMode(StrEnum):
    REVIEW = 'review'
    DIAGNOSTIC = 'diagnostic'
    REGRESSION = 'regression'
    TRAINING = 'training'


def _json_value(value: object) -> object:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in sorted(value.items(), key=lambda row: str(row[0]))}
    if isinstance(value, tuple | list):
        return [_json_value(item) for item in value]
    return value


def _event_time(value: object, *, default: int = 0) -> EventTime:
    if value is None:
        return as_event_time(default)
    if isinstance(value, int | str):
        return as_event_time(int(value))
    raise TypeError('event time must be an integer-compatible value')


def _payload_mapping(value: object, *, field_name: str) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    raise TypeError(f'{field_name} must be a mapping')


def _payload_sequence(value: object, *, field_name: str) -> Sequence[object]:
    if value is None:
        return ()
    if isinstance(value, list | tuple):
        return value
    raise TypeError(f'{field_name} must be a sequence')


def _mapping_tuple(rows: object) -> tuple[dict[str, object], ...]:
    if rows is None:
        return ()
    rows = _payload_sequence(rows, field_name='mapping rows')
    return tuple({str(key): _json_value(value) for key, value in dict(row).items()} for row in rows if isinstance(row, Mapping))


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionSafetyPosture:
    hardware_mutation_enabled: bool = False
    live_mapping_apply_enabled: bool = False
    replay_is_live: bool = False
    production_historian_enabled: bool = False
    runtime_logic_deployed: bool = False
    summary: str = 'review-only session posture; no live authority'

    @property
    def safe(self) -> bool:
        return not (
            self.hardware_mutation_enabled
            or self.live_mapping_apply_enabled
            or self.replay_is_live
            or self.production_historian_enabled
            or self.runtime_logic_deployed
        )

    def to_dict(self) -> dict[str, object]:
        return {
            'hardware_mutation_enabled': self.hardware_mutation_enabled,
            'live_mapping_apply_enabled': self.live_mapping_apply_enabled,
            'replay_is_live': self.replay_is_live,
            'production_historian_enabled': self.production_historian_enabled,
            'runtime_logic_deployed': self.runtime_logic_deployed,
            'safe': self.safe,
            'summary': self.summary,
        }

    @staticmethod
    def from_dict(payload: Mapping[str, object] | None) -> SessionSafetyPosture:
        if payload is None:
            return SessionSafetyPosture()
        return SessionSafetyPosture(
            hardware_mutation_enabled=bool(payload.get('hardware_mutation_enabled', False)),
            live_mapping_apply_enabled=bool(payload.get('live_mapping_apply_enabled', False)),
            replay_is_live=bool(payload.get('replay_is_live', False)),
            production_historian_enabled=bool(payload.get('production_historian_enabled', False)),
            runtime_logic_deployed=bool(payload.get('runtime_logic_deployed', False)),
            summary=str(payload.get('summary', 'review-only session posture; no live authority')),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionValidationResult:
    ok: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            'ok': self.ok,
            'errors': list(self.errors),
            'warnings': list(self.warnings),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionCheckpoint:
    checkpoint_id: str
    session_id: str
    checkpoint_timestamp: EventTime
    runtime_snapshot: Mapping[str, object]
    schema_version: str = SESSION_CHECKPOINT_SCHEMA_VERSION
    source_package_id: str = DEFAULT_SOURCE_PACKAGE_ID
    source_package_tag: str | None = DEFAULT_SOURCE_PACKAGE_ID
    runtime_snapshot_model_version: str | None = None
    event_log: tuple[dict[str, object], ...] = ()
    warnings: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = (
        'Replay is review-only and non-live.',
        'Checkpoint replay does not grant command authority.',
    )
    safety: SessionSafetyPosture = field(default_factory=SessionSafetyPosture)

    def __post_init__(self) -> None:
        if self.runtime_snapshot_model_version is None:
            identity = self.runtime_snapshot.get('identity')
            model_version = None
            if isinstance(identity, Mapping):
                model_version = identity.get('model_version')
            object.__setattr__(self, 'runtime_snapshot_model_version', None if model_version is None else str(model_version))

    def to_dict(self) -> dict[str, object]:
        return {
            'schema_version': self.schema_version,
            'checkpoint_id': self.checkpoint_id,
            'session_id': self.session_id,
            'checkpoint_timestamp': int(self.checkpoint_timestamp),
            'source_package_id': self.source_package_id,
            'source_package_tag': self.source_package_tag,
            'runtime_snapshot_model_version': self.runtime_snapshot_model_version,
            'runtime_snapshot': _json_value(dict(self.runtime_snapshot)),
            'event_log': [_json_value(row) for row in self.event_log],
            'warnings': list(self.warnings),
            'known_limitations': list(self.known_limitations),
            'safety': self.safety.to_dict(),
        }

    @staticmethod
    def from_dict(payload: Mapping[str, object]) -> SessionCheckpoint:
        runtime_snapshot = _payload_mapping(payload.get('runtime_snapshot', {}), field_name='runtime_snapshot')
        warnings = _payload_sequence(payload.get('warnings', ()), field_name='warnings')
        known_limitations = _payload_sequence(payload.get('known_limitations', ()), field_name='known_limitations')
        safety_payload = payload.get('safety')
        return SessionCheckpoint(
            schema_version=str(payload.get('schema_version', SESSION_CHECKPOINT_SCHEMA_VERSION)),
            checkpoint_id=str(payload['checkpoint_id']),
            session_id=str(payload['session_id']),
            checkpoint_timestamp=_event_time(payload.get('checkpoint_timestamp')),
            source_package_id=str(payload.get('source_package_id', DEFAULT_SOURCE_PACKAGE_ID)),
            source_package_tag=None if payload.get('source_package_tag') in {None, ''} else str(payload.get('source_package_tag')),
            runtime_snapshot_model_version=None
            if payload.get('runtime_snapshot_model_version') in {None, ''}
            else str(payload.get('runtime_snapshot_model_version')),
            runtime_snapshot={str(key): value for key, value in runtime_snapshot.items()},
            event_log=_mapping_tuple(payload.get('event_log', ())),
            warnings=tuple(str(item) for item in warnings),
            known_limitations=tuple(str(item) for item in known_limitations),
            safety=SessionSafetyPosture.from_dict(
                safety_payload if isinstance(safety_payload, Mapping) else None
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class DurableSession:
    session_id: str
    created_at: EventTime
    updated_at: EventTime
    model_version: str = SESSION_MODEL_VERSION
    source_package_id: str = DEFAULT_SOURCE_PACKAGE_ID
    source_package_tag: str | None = DEFAULT_SOURCE_PACKAGE_ID
    mode: SessionMode = SessionMode.REVIEW
    operator_context: Mapping[str, object] = field(default_factory=dict)
    checkpoints: tuple[SessionCheckpoint, ...] = ()
    events: tuple[dict[str, object], ...] = ()
    warnings: tuple[str, ...] = ()
    known_limitations: tuple[str, ...] = (
        'Session replay is non-live.',
        'Production historian behavior is not implemented.',
    )
    safety: SessionSafetyPosture = field(default_factory=SessionSafetyPosture)

    def with_checkpoint(self, checkpoint: SessionCheckpoint) -> DurableSession:
        return replace(
            self,
            updated_at=checkpoint.checkpoint_timestamp,
            checkpoints=self.checkpoints + (checkpoint,),
        )

    @property
    def checkpoint_ids(self) -> tuple[str, ...]:
        return tuple(checkpoint.checkpoint_id for checkpoint in self.checkpoints)

    def to_dict(self) -> dict[str, object]:
        return {
            'model_version': self.model_version,
            'session_id': self.session_id,
            'created_at': int(self.created_at),
            'updated_at': int(self.updated_at),
            'source_package_id': self.source_package_id,
            'source_package_tag': self.source_package_tag,
            'mode': self.mode.value,
            'operator_context': _json_value(dict(self.operator_context)),
            'checkpoint_ids': list(self.checkpoint_ids),
            'checkpoint_count': len(self.checkpoints),
            'checkpoints': [checkpoint.to_dict() for checkpoint in self.checkpoints],
            'events': [_json_value(row) for row in self.events],
            'warnings': list(self.warnings),
            'known_limitations': list(self.known_limitations),
            'safety': self.safety.to_dict(),
        }

    @staticmethod
    def from_dict(payload: Mapping[str, object]) -> DurableSession:
        operator_context = _payload_mapping(payload.get('operator_context', {}), field_name='operator_context')
        checkpoint_rows = _payload_sequence(payload.get('checkpoints', ()), field_name='checkpoints')
        warnings = _payload_sequence(payload.get('warnings', ()), field_name='warnings')
        known_limitations = _payload_sequence(payload.get('known_limitations', ()), field_name='known_limitations')
        safety_payload = payload.get('safety')
        return DurableSession(
            model_version=str(payload.get('model_version', SESSION_MODEL_VERSION)),
            session_id=str(payload['session_id']),
            created_at=_event_time(payload.get('created_at')),
            updated_at=_event_time(payload.get('updated_at')),
            source_package_id=str(payload.get('source_package_id', DEFAULT_SOURCE_PACKAGE_ID)),
            source_package_tag=None if payload.get('source_package_tag') in {None, ''} else str(payload.get('source_package_tag')),
            mode=SessionMode(str(payload.get('mode', SessionMode.REVIEW.value))),
            operator_context={str(key): value for key, value in operator_context.items()},
            checkpoints=tuple(
                SessionCheckpoint.from_dict(dict(item))
                for item in checkpoint_rows
                if isinstance(item, Mapping)
            ),
            events=_mapping_tuple(payload.get('events', ())),
            warnings=tuple(str(item) for item in warnings),
            known_limitations=tuple(str(item) for item in known_limitations),
            safety=SessionSafetyPosture.from_dict(
                safety_payload if isinstance(safety_payload, Mapping) else None
            ),
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class ReplayView:
    replay_id: str
    session_id: str
    checkpoint_id: str
    created_at: EventTime
    runtime_snapshot: Mapping[str, object]
    replay_mode: ReplayMode = ReplayMode.REVIEW
    schema_version: str = SESSION_REPLAY_SCHEMA_VERSION
    validation: SessionValidationResult = field(default_factory=lambda: SessionValidationResult(ok=True))
    safety: SessionSafetyPosture = field(default_factory=SessionSafetyPosture)
    summary: str = 'review-only replay view'

    @property
    def replay_is_live(self) -> bool:
        return self.safety.replay_is_live

    def to_dict(self) -> dict[str, object]:
        return {
            'schema_version': self.schema_version,
            'replay_id': self.replay_id,
            'session_id': self.session_id,
            'checkpoint_id': self.checkpoint_id,
            'created_at': int(self.created_at),
            'replay_mode': self.replay_mode.value,
            'replay_is_live': self.replay_is_live,
            'summary': self.summary,
            'runtime_snapshot': _json_value(dict(self.runtime_snapshot)),
            'validation': self.validation.to_dict(),
            'safety': self.safety.to_dict(),
        }
