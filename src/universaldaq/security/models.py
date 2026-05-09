from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum

from universaldaq.common import ActorId, AuthorizationState


class RoleClass(StrEnum):
    OBSERVER = 'observer'
    OPERATOR = 'operator'
    SUPERVISOR = 'supervisor'
    SERVICE = 'service'
    ENGINEER = 'engineer'
    ADMIN = 'admin'


class PermissionFamily(StrEnum):
    VIEW_RUNTIME = 'view_runtime'
    VIEW_DIAGNOSTICS = 'view_diagnostics'
    ACKNOWLEDGE_ALARMS = 'acknowledge_alarms'
    ISSUE_MANUAL_COMMANDS = 'issue_manual_commands'
    EXPORT_ARTIFACTS = 'export_artifacts'
    EDIT_CONFIGURATION = 'edit_configuration'
    APPLY_CONFIGURATION = 'apply_configuration'
    SUPERVISE_SEQUENCES = 'supervise_sequences'
    SERVICE_ACTIONS = 'service_actions'


class GovernedAction(StrEnum):
    ACK_ALARM = 'ack_alarm'
    ISSUE_OUTPUT_COMMAND = 'issue_output_command'
    EXPORT_REVIEW_ARTIFACT = 'export_review_artifact'
    EXPORT_EVIDENCE_BUNDLE = 'export_evidence_bundle'
    EXPORT_DIAGNOSTIC_SNAPSHOT = 'export_diagnostic_snapshot'


class AuthorizationReasonCode(StrEnum):
    ALLOWED = 'allowed'
    INSUFFICIENT_ROLE = 'insufficient_role'
    ACTION_NOT_PERMITTED = 'action_not_permitted'
    NO_POLICY = 'no_policy'


@dataclass(frozen=True, slots=True, kw_only=True)
class ActorContext:
    actor_id: ActorId
    role_class: RoleClass
    display_name: str | None = None
    origin: str = 'local-shell'
    is_local: bool = True
    session_id: str | None = None
    tags: tuple[str, ...] = field(default_factory=tuple)

    def with_session(self, session_id: str) -> 'ActorContext':
        return replace(self, session_id=session_id)

    def with_actor(self, actor_id: ActorId, display_name: str | None = None) -> 'ActorContext':
        return replace(self, actor_id=actor_id, display_name=self.display_name if display_name is None else display_name)

    @property
    def role_label(self) -> str:
        return self.role_class.value.replace('_', ' ')


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizationDecision:
    allowed: bool
    permission_family: PermissionFamily
    action: GovernedAction
    reason_code: AuthorizationReasonCode
    reason_text: str
    actor_id: ActorId
    session_id: str | None = None
    origin: str = 'local-shell'
    target_kind: str | None = None
    target_id: str | None = None

    @property
    def authorization_state(self) -> AuthorizationState:
        return AuthorizationState.ALLOWED if self.allowed else AuthorizationState.DENIED

    @property
    def summary(self) -> str:
        outcome = 'allowed' if self.allowed else 'denied'
        target = '' if self.target_kind is None else f' on {self.target_kind}:{self.target_id or ""}'
        return f'{self.action.value} {outcome}{target}'.strip()


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilitySnapshot:
    role_class: RoleClass
    permissions: tuple[PermissionFamily, ...] = field(default_factory=tuple)
    allowed_actions: tuple[GovernedAction, ...] = field(default_factory=tuple)

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(permission.value for permission in self.permissions)
