from __future__ import annotations

from universaldaq.common import AuthorizationState

from .models import GovernedAction, PermissionFamily, RoleClass

DEFAULT_ROLE_PERMISSIONS: dict[RoleClass, tuple[PermissionFamily, ...]] = {
    RoleClass.OBSERVER: (
        PermissionFamily.VIEW_RUNTIME,
        PermissionFamily.VIEW_DIAGNOSTICS,
        PermissionFamily.EXPORT_ARTIFACTS,
    ),
    RoleClass.OPERATOR: (
        PermissionFamily.VIEW_RUNTIME,
        PermissionFamily.ACKNOWLEDGE_ALARMS,
        PermissionFamily.ISSUE_MANUAL_COMMANDS,
        PermissionFamily.EXPORT_ARTIFACTS,
    ),
    RoleClass.SUPERVISOR: (
        PermissionFamily.VIEW_RUNTIME,
        PermissionFamily.ACKNOWLEDGE_ALARMS,
        PermissionFamily.ISSUE_MANUAL_COMMANDS,
        PermissionFamily.EXPORT_ARTIFACTS,
        PermissionFamily.VIEW_DIAGNOSTICS,
        PermissionFamily.SUPERVISE_SEQUENCES,
    ),
    RoleClass.SERVICE: (
        PermissionFamily.VIEW_RUNTIME,
        PermissionFamily.VIEW_DIAGNOSTICS,
        PermissionFamily.SERVICE_ACTIONS,
        PermissionFamily.EXPORT_ARTIFACTS,
    ),
    RoleClass.ENGINEER: (
        PermissionFamily.VIEW_RUNTIME,
        PermissionFamily.VIEW_DIAGNOSTICS,
        PermissionFamily.ACKNOWLEDGE_ALARMS,
        PermissionFamily.ISSUE_MANUAL_COMMANDS,
        PermissionFamily.EXPORT_ARTIFACTS,
        PermissionFamily.EDIT_CONFIGURATION,
        PermissionFamily.APPLY_CONFIGURATION,
    ),
    RoleClass.ADMIN: tuple(PermissionFamily),
}

DEFAULT_ROLE_ACTIONS: dict[RoleClass, tuple[GovernedAction, ...]] = {
    RoleClass.OBSERVER: (
        GovernedAction.EXPORT_REVIEW_ARTIFACT,
    ),
    RoleClass.OPERATOR: (
        GovernedAction.ACK_ALARM,
        GovernedAction.ISSUE_OUTPUT_COMMAND,
        GovernedAction.EXPORT_REVIEW_ARTIFACT,
        GovernedAction.EXPORT_EVIDENCE_BUNDLE,
    ),
    RoleClass.SUPERVISOR: (
        GovernedAction.ACK_ALARM,
        GovernedAction.ISSUE_OUTPUT_COMMAND,
        GovernedAction.EXPORT_REVIEW_ARTIFACT,
        GovernedAction.EXPORT_EVIDENCE_BUNDLE,
        GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT,
    ),
    RoleClass.SERVICE: (
        GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT,
    ),
    RoleClass.ENGINEER: (
        GovernedAction.ACK_ALARM,
        GovernedAction.ISSUE_OUTPUT_COMMAND,
        GovernedAction.EXPORT_REVIEW_ARTIFACT,
        GovernedAction.EXPORT_EVIDENCE_BUNDLE,
        GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT,
    ),
    RoleClass.ADMIN: tuple(GovernedAction),
}

DEFAULT_ACTION_PERMISSIONS: dict[GovernedAction, PermissionFamily] = {
    GovernedAction.ACK_ALARM: PermissionFamily.ACKNOWLEDGE_ALARMS,
    GovernedAction.ISSUE_OUTPUT_COMMAND: PermissionFamily.ISSUE_MANUAL_COMMANDS,
    GovernedAction.EXPORT_REVIEW_ARTIFACT: PermissionFamily.EXPORT_ARTIFACTS,
    GovernedAction.EXPORT_EVIDENCE_BUNDLE: PermissionFamily.EXPORT_ARTIFACTS,
    GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT: PermissionFamily.VIEW_DIAGNOSTICS,
}


def derive_role_class_from_authority_state(state: AuthorizationState) -> RoleClass:
    if state == AuthorizationState.ALLOWED:
        return RoleClass.OPERATOR
    return RoleClass.OBSERVER
