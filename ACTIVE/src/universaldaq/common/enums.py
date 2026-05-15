from __future__ import annotations

from enum import StrEnum


class SignalQuality(StrEnum):
    GOOD = "good"
    STALE = "stale"
    INVALID = "invalid"
    DISCONNECTED = "disconnected"
    SIMULATED = "simulated"


class GraphMode(StrEnum):
    LIVE = "live"
    REVIEW = "review"
    HISTORY = "history"
    LIVE_TRACE = "live-trace"


class RestoreOrigin(StrEnum):
    SESSION = "session"
    PROFILE = "profile"
    AUTOSAVE = "autosave"


class EvidenceKind(StrEnum):
    TRACE = "trace"
    EVENT = "event"
    EXPORT = "export"
    SCREENSHOT = "screenshot"
    ASSERTION = "assertion"


class ExportArtifactClass(StrEnum):
    SIMPLE_EXPORT = "simple_export"
    REVIEW_ARTIFACT = "review_artifact"
    EVIDENCE_BUNDLE = "evidence_bundle"
    DIAGNOSTIC_SNAPSHOT = "diagnostic_snapshot"


class CommandDecision(StrEnum):
    REQUESTED = "requested"
    BLOCKED = "blocked"
    APPLIED = "applied"
    OBSERVED = "observed"
    MISMATCHED = "mismatched"
    REJECTED = "rejected"


class AlarmLifecycleState(StrEnum):
    NORMAL = "normal"
    ASSERTED = "asserted"
    ACKNOWLEDGED = "acknowledged"
    RETURNED_TO_NORMAL = "returned_to_normal"


class AuthorizationState(StrEnum):
    ALLOWED = "allowed"
    DENIED = "denied"
    VIEW_ONLY = "view_only"
