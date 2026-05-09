from __future__ import annotations

import pytest

from universaldaq.security import AuthorizationService, GovernedAction, PermissionFamily, RoleClass

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-013', 'verifies_requirements': ['UDQ-REQ-SEC-001'], 'checks_invariants': ['UDQ-INV-STATE-002'], 'worked_example_reference': None, 'expected_proof_output': 'role permission mapping'}
pytestmark = pytest.mark.contract


def test_role_permission_mapping_matches_bounded_policy_for_all_roles():
    service = AuthorizationService.from_default_policy()
    expected_permissions = {
        RoleClass.OBSERVER: {PermissionFamily.VIEW_RUNTIME, PermissionFamily.VIEW_DIAGNOSTICS, PermissionFamily.EXPORT_ARTIFACTS},
        RoleClass.OPERATOR: {PermissionFamily.VIEW_RUNTIME, PermissionFamily.ACKNOWLEDGE_ALARMS, PermissionFamily.ISSUE_MANUAL_COMMANDS, PermissionFamily.EXPORT_ARTIFACTS},
        RoleClass.SUPERVISOR: {PermissionFamily.VIEW_RUNTIME, PermissionFamily.ACKNOWLEDGE_ALARMS, PermissionFamily.ISSUE_MANUAL_COMMANDS, PermissionFamily.EXPORT_ARTIFACTS, PermissionFamily.VIEW_DIAGNOSTICS, PermissionFamily.SUPERVISE_SEQUENCES},
        RoleClass.SERVICE: {PermissionFamily.VIEW_RUNTIME, PermissionFamily.VIEW_DIAGNOSTICS, PermissionFamily.SERVICE_ACTIONS, PermissionFamily.EXPORT_ARTIFACTS},
        RoleClass.ENGINEER: {PermissionFamily.VIEW_RUNTIME, PermissionFamily.VIEW_DIAGNOSTICS, PermissionFamily.ACKNOWLEDGE_ALARMS, PermissionFamily.ISSUE_MANUAL_COMMANDS, PermissionFamily.EXPORT_ARTIFACTS, PermissionFamily.EDIT_CONFIGURATION, PermissionFamily.APPLY_CONFIGURATION},
        RoleClass.ADMIN: set(PermissionFamily),
    }
    expected_actions = {
        RoleClass.OBSERVER: {GovernedAction.EXPORT_REVIEW_ARTIFACT},
        RoleClass.OPERATOR: {GovernedAction.ACK_ALARM, GovernedAction.ISSUE_OUTPUT_COMMAND, GovernedAction.EXPORT_REVIEW_ARTIFACT, GovernedAction.EXPORT_EVIDENCE_BUNDLE},
        RoleClass.SUPERVISOR: {GovernedAction.ACK_ALARM, GovernedAction.ISSUE_OUTPUT_COMMAND, GovernedAction.EXPORT_REVIEW_ARTIFACT, GovernedAction.EXPORT_EVIDENCE_BUNDLE, GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT},
        RoleClass.SERVICE: {GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT},
        RoleClass.ENGINEER: {GovernedAction.ACK_ALARM, GovernedAction.ISSUE_OUTPUT_COMMAND, GovernedAction.EXPORT_REVIEW_ARTIFACT, GovernedAction.EXPORT_EVIDENCE_BUNDLE, GovernedAction.EXPORT_DIAGNOSTIC_SNAPSHOT},
        RoleClass.ADMIN: set(GovernedAction),
    }

    for role in RoleClass:
        assert set(service.policy.permissions_for_role(role)) == expected_permissions[role]
        assert set(service.policy.actions_for_role(role)) == expected_actions[role]
