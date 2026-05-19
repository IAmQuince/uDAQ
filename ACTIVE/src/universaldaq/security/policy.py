from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .models import ActorContext, AuthorizationDecision, AuthorizationReasonCode, GovernedAction, PermissionFamily, RoleClass


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthorizationPolicy:
    role_permissions: Mapping[RoleClass, tuple[PermissionFamily, ...]] = field(default_factory=dict)
    role_actions: Mapping[RoleClass, tuple[GovernedAction, ...]] = field(default_factory=dict)
    action_permissions: Mapping[GovernedAction, PermissionFamily] = field(default_factory=dict)

    def permissions_for_role(self, role_class: RoleClass) -> tuple[PermissionFamily, ...]:
        return tuple(self.role_permissions.get(role_class, ()))

    def actions_for_role(self, role_class: RoleClass) -> tuple[GovernedAction, ...]:
        return tuple(self.role_actions.get(role_class, ()))

    def permission_for_action(self, action: GovernedAction) -> PermissionFamily | None:
        return self.action_permissions.get(action)

    def evaluate(
        self,
        *,
        action: GovernedAction,
        actor_context: ActorContext,
        target_kind: str | None = None,
        target_id: str | None = None,
    ) -> AuthorizationDecision:
        permission_family = self.permission_for_action(action)
        if permission_family is None:
            return AuthorizationDecision(
                allowed=False,
                permission_family=PermissionFamily.VIEW_RUNTIME,
                action=action,
                reason_code=AuthorizationReasonCode.NO_POLICY,
                reason_text=f'no policy mapping exists for {action.value}',
                actor_id=actor_context.actor_id,
                session_id=actor_context.session_id,
                origin=actor_context.origin,
                target_kind=target_kind,
                target_id=target_id,
            )
        permissions = self.permissions_for_role(actor_context.role_class)
        if permission_family not in permissions:
            return AuthorizationDecision(
                allowed=False,
                permission_family=permission_family,
                action=action,
                reason_code=AuthorizationReasonCode.INSUFFICIENT_ROLE,
                reason_text=f'role {actor_context.role_class.value} lacks {permission_family.value}',
                actor_id=actor_context.actor_id,
                session_id=actor_context.session_id,
                origin=actor_context.origin,
                target_kind=target_kind,
                target_id=target_id,
            )
        allowed_actions = self.actions_for_role(actor_context.role_class)
        if allowed_actions and action not in allowed_actions:
            return AuthorizationDecision(
                allowed=False,
                permission_family=permission_family,
                action=action,
                reason_code=AuthorizationReasonCode.ACTION_NOT_PERMITTED,
                reason_text=f'role {actor_context.role_class.value} is not permitted to execute {action.value}',
                actor_id=actor_context.actor_id,
                session_id=actor_context.session_id,
                origin=actor_context.origin,
                target_kind=target_kind,
                target_id=target_id,
            )
        return AuthorizationDecision(
            allowed=True,
            permission_family=permission_family,
            action=action,
            reason_code=AuthorizationReasonCode.ALLOWED,
            reason_text=f'role {actor_context.role_class.value} permits {action.value}',
            actor_id=actor_context.actor_id,
            session_id=actor_context.session_id,
            origin=actor_context.origin,
            target_kind=target_kind,
            target_id=target_id,
        )
