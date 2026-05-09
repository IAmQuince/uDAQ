---
document_id: UDQ-SEC-SPEC-001
title: Roles, Permissions, and Command Authorization Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-HIS-SPEC-001"
  - "UDQ-OUT-SPEC-001"
  - "UDQ-REM-SPEC-001"
  - "UDQ-UI-MOD-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
supersedes:
  - "UDQ-SEC-SPEC-001__Roles_Permissions_and_Command_Authorization_Specification__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Subsystem reconciliation pass: clarified backend authorization doctrine and attribution requirements across command paths."
  - "r0 | 2026-03-21 | Prior active revision carried forward before subsystem reconciliation pass."
---
# Roles, Permissions, and Command Authorization Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r1 | 2026-03-21 | WIP | Subsystem reconciliation pass: clarified backend authorization doctrine and attribution requirements across command paths. |
| r0 | 2026-03-21 | WIP | Initial issue defining the authorization model for viewing, acknowledging, configuring, and commanding within UniversalDAQ. |

# 1. Purpose [SEC:UDQ-SEC-SPEC-001::1]

This specification defines how UniversalDAQ shall govern roles, permissions, and command authorization without undermining backend truth or evidence integrity.

# 2. Scope [SEC:UDQ-SEC-SPEC-001::2]

This specification applies to:

- runtime viewing privileges
- acknowledgment, shelving, and service actions
- configuration editing and apply behavior
- command issuance and command approval boundaries where used
- local versus remote client actions
- evidence obligations tied to authorized actions

# 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-SEC-SPEC-001::2A]

Authorization is a backend-enforced policy layer. UI visibility, enabled-state, or client locality does not constitute authorization by itself. All command, acknowledgment, configuration-apply, and remote control actions shall remain attributable to actor, session, origin, and target action.

# 3. Authorization model [SEC:UDQ-SEC-SPEC-001::3]

UniversalDAQ shall treat authorization as a backend-enforced policy layer, not merely a frontend visibility preference. UI controls may be hidden or disabled for usability, but enforcement shall occur in backend-authoritative command pathways.

# 4. Canonical role classes [SEC:UDQ-SEC-SPEC-001::4]

The platform should support role classes sufficient to separate, at minimum:

- observer/reviewer
- operator/supervisor
- commissioning/service user
- configuration engineer/author
- administrative/governance user

Implementations may choose different names, but the functional separation shall remain clear.

# 5. Permission families [SEC:UDQ-SEC-SPEC-001::5]

Permissions shall be governable by family, at minimum for:

- view runtime state
- view diagnostics/service detail
- acknowledge/shelve alarms
- issue manual commands
- start/stop/hold/reset sequences
- edit rules, sequences, and configuration objects
- apply governed configuration to live runtime
- export governed artifacts
- create release/package artifacts where applicable

# 6. Command authorization doctrine [SEC:UDQ-SEC-SPEC-001::6]

## 6.1 Request path [SEC:UDQ-SEC-SPEC-001::6.1]

All command requests shall pass through backend authorization and arbitration. Authorization is a prerequisite to command consideration, not a post hoc display decision.

## 6.2 Authorization versus permissives/interlocks [SEC:UDQ-SEC-SPEC-001::6.2]

Authorization does not override permissives, interlocks, or safe-state policy by itself. A fully authorized actor may still have a command blocked by runtime conditions.

## 6.3 Visibility of denial [SEC:UDQ-SEC-SPEC-001::6.3]

The UI should make it visible whether a command failed because of lack of authorization, arbitration conflict, interlock/permissive block, or transport/device failure.

# 7. Local versus remote implications [SEC:UDQ-SEC-SPEC-001::7]

Remote origin shall not imply weaker or stronger authorization semantics by default. Policy may differentiate local and remote command scopes, but such distinctions shall be explicit and evidence-bearing.

# 8. Session and identity expectations [SEC:UDQ-SEC-SPEC-001::8]

Actors issuing governed actions shall be attributable. The platform shall preserve enough session/client identity to support evidence trails for:

- acknowledgments and shelving
- manual commands
- configuration apply actions
- sequence control actions
- export/bundle creation when governed

# 9. UI obligations [SEC:UDQ-SEC-SPEC-001::9]

The UI shall support, at minimum:

- clear indication of current session/client capability level
- disabled or hidden controls where appropriate for usability
- visible reason when a requested action is denied or blocked
- review surfaces that distinguish lack of permission from runtime unavailability
- confirmation flows for higher-consequence actions where policy demands them

# 10. Historian and evidence obligations [SEC:UDQ-SEC-SPEC-001::10]

Governed actions shall preserve actor identity, client origin, action type, target, and outcome. Authorization-denied attempts may also be evidence-bearing where policy requires review or security posture awareness.

# 11. Configuration and governance implications [SEC:UDQ-SEC-SPEC-001::11]

Role/permission models should be governable as configuration rather than scattered ad hoc checks. Changes to command-authority policy itself should be subject to stronger review/change control than ordinary runtime use.

# 12. Validation and test obligations [SEC:UDQ-SEC-SPEC-001::12]

Authorization behavior shall be testable for:

- role separation correctness
- local/remote parity or intentional difference where declared
- denial reason visibility
- evidence generation for allowed and denied actions as required
- interaction with arbitration, interlocks, and safe-state logic

# 13. Anti-patterns [SEC:UDQ-SEC-SPEC-001::13]

The platform shall avoid:

- treating hidden buttons as sufficient authorization
- allowing backend command paths to bypass permission checks
- conflating authorization failure with device/transport failure
- losing actor identity for material actions
- granting broad configuration/apply rights merely because a user can view runtime state

# 9A. Bounded control-posture presentation [SEC:UDQ-SEC-SPEC-001::9A]

The current operator-flow slice shall expose a simplified but canonical control-posture surface derived from backend permissions:
- `view_only`: observe and export without manual command authority
- `armed_control`: permitted to issue manual control actions in the current bounded slice
- `engineering`: configuration/apply-capable posture for future higher-consequence workflows

This posture is a shell-facing interpretation of backend authorization state and permission families; it does not replace backend enforcement. The purpose of the posture label is to prevent the first bench slice from looking interactive in ways the backend would later deny.
