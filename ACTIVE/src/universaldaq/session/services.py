from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from universaldaq.common import EventTime, as_event_time
from universaldaq.runtime import RuntimeStateSnapshot, build_authoritative_runtime_snapshot

from .models import (
    DEFAULT_SOURCE_PACKAGE_ID,
    SESSION_AUTHORITY_SCOPE,
    DurableSession,
    ReplayMode,
    ReplayView,
    SessionCheckpoint,
    SessionMode,
    SessionSafetyPosture,
    SessionValidationResult,
)


def canonical_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def state_hash(payload: Mapping[str, object]) -> str:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def write_json(path: Path, payload: Mapping[str, object]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _snapshot_dict(
    snapshot: RuntimeStateSnapshot | Mapping[str, object] | None,
) -> dict[str, object]:
    if snapshot is None:
        return build_authoritative_runtime_snapshot().to_dict()
    if isinstance(snapshot, RuntimeStateSnapshot):
        return snapshot.to_dict()
    return {str(key): value for key, value in snapshot.items()}


def _truth_keys_present(runtime_snapshot: Mapping[str, object]) -> bool:
    return all(
        key in runtime_snapshot for key in ("requested_state", "applied_state", "observed_state")
    )


def validate_checkpoint_payload(payload: Mapping[str, object]) -> SessionValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    safety = payload.get("safety")
    if not isinstance(safety, Mapping):
        errors.append("checkpoint safety posture is missing")
    else:
        for key in ("hardware_mutation_enabled", "live_mapping_apply_enabled", "replay_is_live"):
            if safety.get(key) is True:
                errors.append(f"{key} must be false")
    runtime_snapshot = payload.get("runtime_snapshot")
    if not isinstance(runtime_snapshot, Mapping):
        errors.append("runtime_snapshot is missing or invalid")
    elif not _truth_keys_present(runtime_snapshot):
        errors.append("runtime_snapshot must preserve requested/applied/observed state")
    authority_scope = payload.get("authority_scope", SESSION_AUTHORITY_SCOPE)
    if authority_scope != SESSION_AUTHORITY_SCOPE:
        errors.append(f"authority_scope must be {SESSION_AUTHORITY_SCOPE}")
    if payload.get("schema_version") != "udq.session.checkpoint.v1":
        warnings.append("checkpoint schema version differs from current version")
    return SessionValidationResult(ok=not errors, errors=tuple(errors), warnings=tuple(warnings))


class DurableSessionService:
    def create_session(
        self,
        *,
        session_id: str,
        created_at: EventTime | int = 0,
        mode: SessionMode = SessionMode.REVIEW,
        source_package_id: str = DEFAULT_SOURCE_PACKAGE_ID,
        source_package_tag: str | None = DEFAULT_SOURCE_PACKAGE_ID,
        operator_context: Mapping[str, object] | None = None,
    ) -> DurableSession:
        created = as_event_time(int(created_at))
        return DurableSession(
            session_id=session_id,
            created_at=created,
            updated_at=created,
            source_package_id=source_package_id,
            source_package_tag=source_package_tag,
            mode=mode,
            operator_context={} if operator_context is None else dict(operator_context),
        )

    def create_checkpoint(
        self,
        *,
        session: DurableSession,
        checkpoint_id: str,
        timestamp: EventTime | int,
        runtime_snapshot: RuntimeStateSnapshot | Mapping[str, object] | None = None,
        event_log: tuple[dict[str, object], ...] = (),
        warnings: tuple[str, ...] = (),
    ) -> SessionCheckpoint:
        return SessionCheckpoint(
            checkpoint_id=checkpoint_id,
            session_id=session.session_id,
            checkpoint_timestamp=as_event_time(int(timestamp)),
            runtime_snapshot=_snapshot_dict(runtime_snapshot),
            source_package_id=session.source_package_id,
            source_package_tag=session.source_package_tag,
            event_log=event_log,
            warnings=warnings,
        )

    def append_checkpoint(
        self, *, session: DurableSession, checkpoint: SessionCheckpoint
    ) -> DurableSession:
        return session.with_checkpoint(checkpoint)

    def validate_checkpoint(self, checkpoint: SessionCheckpoint) -> SessionValidationResult:
        return validate_checkpoint_payload(checkpoint.to_dict())

    def validate_session(self, session: DurableSession) -> SessionValidationResult:
        errors: list[str] = []
        warnings: list[str] = []
        if not session.safety.safe:
            errors.append("session safety posture must remain non-live")
        if not session.checkpoints:
            warnings.append("session has no checkpoints")
        for checkpoint in session.checkpoints:
            result = self.validate_checkpoint(checkpoint)
            errors.extend(f"{checkpoint.checkpoint_id}: {item}" for item in result.errors)
            warnings.extend(f"{checkpoint.checkpoint_id}: {item}" for item in result.warnings)
        return SessionValidationResult(
            ok=not errors, errors=tuple(errors), warnings=tuple(warnings)
        )

    def save_session(self, *, session: DurableSession, path: Path) -> Path:
        return write_json(path, session.to_dict())

    def load_session(self, *, path: Path) -> DurableSession:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return DurableSession.from_dict(payload)

    def save_checkpoint(self, *, checkpoint: SessionCheckpoint, path: Path) -> Path:
        return write_json(path, checkpoint.to_dict())

    def load_checkpoint(self, *, path: Path) -> SessionCheckpoint:
        payload = json.loads(path.read_text(encoding="utf-8"))
        return SessionCheckpoint.from_dict(payload)

    def build_replay_view(
        self,
        *,
        session: DurableSession,
        checkpoint: SessionCheckpoint,
        replay_id: str,
        created_at: EventTime | int,
        replay_mode: ReplayMode = ReplayMode.REVIEW,
    ) -> ReplayView:
        validation = self.validate_checkpoint(checkpoint)
        safety = SessionSafetyPosture(
            hardware_mutation_enabled=False,
            live_mapping_apply_enabled=False,
            replay_is_live=False,
            production_historian_enabled=False,
            runtime_logic_deployed=False,
            summary="checkpoint replay is review-only and non-live",
        )
        return ReplayView(
            replay_id=replay_id,
            session_id=session.session_id,
            checkpoint_id=checkpoint.checkpoint_id,
            created_at=as_event_time(int(created_at)),
            runtime_snapshot=checkpoint.runtime_snapshot,
            replay_mode=replay_mode,
            validation=validation,
            safety=safety,
            checkpoint_hash=checkpoint.checkpoint_hash,
            summary="Checkpoint replay is for review, diagnostics, UI reconstruction, and regression only.",
        )

    def build_replay_from_latest(
        self,
        *,
        session: DurableSession,
        replay_id: str,
        created_at: EventTime | int,
    ) -> ReplayView:
        if not session.checkpoints:
            raise ValueError("session has no checkpoints to replay")
        return self.build_replay_view(
            session=session,
            checkpoint=session.checkpoints[-1],
            replay_id=replay_id,
            created_at=created_at,
        )


def create_session(
    *,
    session_id: str = "SES-DIAGNOSTIC-001",
    created_at: EventTime | int = 0,
    mode: SessionMode = SessionMode.DIAGNOSTIC,
    source_package_id: str = DEFAULT_SOURCE_PACKAGE_ID,
    source_package_tag: str | None = DEFAULT_SOURCE_PACKAGE_ID,
    operator_context: Mapping[str, object] | None = None,
) -> DurableSession:
    return DurableSessionService().create_session(
        session_id=session_id,
        created_at=created_at,
        mode=mode,
        source_package_id=source_package_id,
        source_package_tag=source_package_tag,
        operator_context=operator_context,
    )


def build_session_checkpoint(
    *,
    session: DurableSession | None = None,
    checkpoint_id: str = "CHK-DIAGNOSTIC-001",
    timestamp: EventTime | int = 0,
    runtime_snapshot: RuntimeStateSnapshot | Mapping[str, object] | None = None,
    package_root: Path | str | None = None,
) -> SessionCheckpoint:
    _ = package_root
    service = DurableSessionService()
    resolved_session = session or service.create_session(
        session_id="SES-DIAGNOSTIC-001", created_at=timestamp
    )
    return service.create_checkpoint(
        session=resolved_session,
        checkpoint_id=checkpoint_id,
        timestamp=timestamp,
        runtime_snapshot=runtime_snapshot,
    )


def create_checkpoint_from_runtime_state(
    *,
    session: DurableSession | None = None,
    checkpoint_id: str = "CHK-DIAGNOSTIC-001",
    timestamp: EventTime | int = 0,
    runtime_snapshot: RuntimeStateSnapshot | Mapping[str, object] | None = None,
    package_root: Path | str | None = None,
) -> SessionCheckpoint:
    return build_session_checkpoint(
        session=session,
        checkpoint_id=checkpoint_id,
        timestamp=timestamp,
        runtime_snapshot=runtime_snapshot,
        package_root=package_root,
    )


def get_current_session_checkpoint(*, package_root: Path | str | None = None) -> SessionCheckpoint:
    return build_session_checkpoint(package_root=package_root)


def build_replay_from_checkpoint(
    *,
    session: DurableSession | None = None,
    checkpoint: SessionCheckpoint,
    replay_id: str = "REPLAY-DIAGNOSTIC-001",
    created_at: EventTime | int = 0,
) -> ReplayView:
    service = DurableSessionService()
    resolved_session = session or service.create_session(
        session_id=checkpoint.session_id, created_at=checkpoint.checkpoint_timestamp
    )
    return service.build_replay_view(
        session=resolved_session,
        checkpoint=checkpoint,
        replay_id=replay_id,
        created_at=created_at,
    )


def save_session(*, session: DurableSession, path: Path) -> Path:
    return DurableSessionService().save_session(session=session, path=path)


def load_session(*, path: Path) -> DurableSession:
    return DurableSessionService().load_session(path=path)


def validate_session_checkpoint(
    checkpoint: SessionCheckpoint | Mapping[str, object],
) -> SessionValidationResult:
    if isinstance(checkpoint, SessionCheckpoint):
        return DurableSessionService().validate_checkpoint(checkpoint)
    return validate_checkpoint_payload(checkpoint)
