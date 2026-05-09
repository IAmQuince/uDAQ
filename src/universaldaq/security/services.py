from __future__ import annotations

from dataclasses import dataclass

from universaldaq.common import ExportArtifactClass

from .builtin_policies import DEFAULT_ACTION_PERMISSIONS, DEFAULT_ROLE_ACTIONS, DEFAULT_ROLE_PERMISSIONS
from .models import (
    ActorContext,
    AuthorizationDecision,
    AuthorizationReasonCode,
    CapabilitySnapshot,
    GovernedAction,
    PermissionFamily,
)
from .policy import AuthorizationPolicy

TARGET_KIND_OUTPUT = 'output'
TARGET_KIND_ALARM = 'alarm'
TARGET_KIND_EXPORT_ARTIFACT = 'export_artifact'
EXPORT_ARTIFACT_ACTIONS: dict[ExportArtifactClass, GovernedAction] = {
    ExportArtifactClass.REVIEW_ARTIFACT: GovernedAction.EXPORT_REVIEW_ARTIFACT,
    ExportArtifactClass.EVIDENCE_BUNDLE: GovernedAction.EXPORT_EVIDENCE_BUNDLE,
    ExportArtifactClass.DIAGNOSTIC_SNAPSHOT: GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT,
    ExportArtifactClass.SIMPLE_EXPORT: GovernedAction.EXPORT_REVIEW_ARTIFACT,
}


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizationService:
    policy: AuthorizationPolicy

    @classmethod
    def from_default_policy(cls) -> 'AuthorizationService':
        return cls(
            policy=AuthorizationPolicy(
                role_permissions=DEFAULT_ROLE_PERMISSIONS,
                role_actions=DEFAULT_ROLE_ACTIONS,
                action_permissions=DEFAULT_ACTION_PERMISSIONS,
            )
        )

    def permissions_for_actor(self, actor_context: ActorContext) -> tuple[str, ...]:
        return tuple(permission.value for permission in self.policy.permissions_for_role(actor_context.role_class))

    def capability_snapshot(self, actor_context: ActorContext) -> CapabilitySnapshot:
        return CapabilitySnapshot(
            role_class=actor_context.role_class,
            permissions=self.policy.permissions_for_role(actor_context.role_class),
            allowed_actions=self.policy.actions_for_role(actor_context.role_class),
        )

    def evaluate(
        self,
        *,
        action: GovernedAction,
        actor_context: ActorContext,
        target_kind: str | None = None,
        target_id: str | None = None,
    ) -> AuthorizationDecision:
        return self.policy.evaluate(
            action=action,
            actor_context=actor_context,
            target_kind=target_kind,
            target_id=target_id,
        )

    def can_issue_output_command(self, *, actor_context: ActorContext, output_id: str) -> AuthorizationDecision:
        return self.evaluate(
            action=GovernedAction.ISSUE_OUTPUT_COMMAND,
            actor_context=actor_context,
            target_kind=TARGET_KIND_OUTPUT,
            target_id=output_id,
        )

    def can_acknowledge_alarm(self, *, actor_context: ActorContext, alarm_id: str) -> AuthorizationDecision:
        return self.evaluate(
            action=GovernedAction.ACK_ALARM,
            actor_context=actor_context,
            target_kind=TARGET_KIND_ALARM,
            target_id=alarm_id,
        )

    def can_export_artifact(self, *, actor_context: ActorContext, artifact_class: ExportArtifactClass | str) -> AuthorizationDecision:
        resolved_artifact = artifact_class if isinstance(artifact_class, ExportArtifactClass) else None
        action = None if resolved_artifact is None else EXPORT_ARTIFACT_ACTIONS.get(resolved_artifact)
        target_id = artifact_class.value if isinstance(artifact_class, ExportArtifactClass) else str(artifact_class)
        if action is None:
            return AuthorizationDecision(
                allowed=False,
                permission_family=PermissionFamily.EXPORT_ARTIFACTS,
                action=GovernedAction.EXPORT_REVIEW_ARTIFACT,
                reason_code=AuthorizationReasonCode.NO_POLICY,
                reason_text=f'unsupported export artifact class: {target_id}',
                actor_id=actor_context.actor_id,
                session_id=actor_context.session_id,
                origin=actor_context.origin,
                target_kind=TARGET_KIND_EXPORT_ARTIFACT,
                target_id=target_id,
            )
        return self.evaluate(
            action=action,
            actor_context=actor_context,
            target_kind=TARGET_KIND_EXPORT_ARTIFACT,
            target_id=target_id,
        )
