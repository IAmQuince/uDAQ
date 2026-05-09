---
document_id: UDQ-GOV-REG-001
title: Contradiction and Reconciliation Register
revision: r2
status: WIP
document_class: governance_register
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-002"
  - "UDQ-GOV-GLO-001"
supersedes:
  - "UDQ-GOV-REG-001__Contradiction_and_Reconciliation_Register__r1__WIP.md"
revision_history:
  - "r2 | 2026-03-24 | Restored the full register body after accidental truncation during cleanup and preserved the current bounded proof rulings around support-pack isolation, command admission, action claims, and identity/correlation semantics."
---
# Contradiction and Reconciliation Register [SEC:UDQ-GOV-REG-001::0]

## 1. Purpose [SEC:UDQ-GOV-REG-001::1]

This register records detected contradictions or material semantic ambiguities, their ruling, and their closure status.

## 2. Closure rule [SEC:UDQ-GOV-REG-001::2]

A register item is considered closed only when the owning semantic source and affected downstream documents have been updated or when the item is explicitly elevated as an open decision that blocks downstream use.

## 3. Current register entries [SEC:UDQ-GOV-REG-001::3]

| issue_id | class | term_cluster | source_docs | finding_summary | canonical_ruling | resolution_vehicle | status |
|---|---|---|---|---|---|---|---|
| UDQ-CON-001 | CONTRADICTION | active vs archive revision truth | UDQ-GOV-LOG-001 r15; package root structure | The package previously kept active and superseded revisions in one docs directory, making active-corpus truth depend on a highest-revision inference rather than explicit placement. | Exactly one active revision of each controlled document ID shall live in docs/active. Older revisions shall live in docs/archive. | UDQ-GOV-STD-003 r0; UDQ-IMP-MAP-001 r1; udq_master_audit_v6.py | RESOLVED |
| UDQ-CON-002 | AMBIGUITY | profile / restore / workspace state / machine state | UDQ-PROF-SPEC-001 r0; UDQ-UI-MOD-001 r1; UDQ-ARCH-NAR-001 r3; UDQ-GOV-GLO-001 r1 | The corpus separated continuity from live truth in spirit, but the subsystem layer still needed stronger operational anti-conflation language. | Restore reconstructs local/session/configuration context and shall never by itself imply live machine-state restoration. | UDQ-PROF-SPEC-001 r1; UDQ-UI-MOD-001 r2; UDQ-GOV-RPT-002 r0 | RESOLVED |
| UDQ-CON-003 | AMBIGUITY | requested / applied / observed state | UDQ-OUT-SPEC-001 r1; UDQ-UI-SPEC-004 r0; UDQ-REM-SPEC-001 r1; UDQ-GOV-GLO-001 r1 | The corpus used the terms consistently enough for planning, but the subsystem layer still needed stronger anti-conflation language where overlays and remote presentation occur. | Requested, applied, and observed state remain distinct. UI and remote surfaces may visualize them, but shall not redefine or collapse them. | UDQ-OUT-SPEC-001 r2; UDQ-UI-SPEC-004 r1; UDQ-REM-SPEC-001 r2; universalDAQ_term_usage_matrix_r2 | RESOLVED |
| UDQ-CON-004 | AMBIGUITY | live / historical / review mode / live trace | UDQ-HIS-SPEC-001 r1; UDQ-UI-SPEC-004 r0; UDQ-UI-MOD-001 r1 | The four terms were centrally defined, but historian and graph-spec language still needed a tighter operational split. | Historical review is evidence exploration, review mode is the broader UI posture, and live trace remains a live explainability surface. | UDQ-HIS-SPEC-001 r2; UDQ-UI-SPEC-004 r1; UDQ-EXM-SPEC-001 r1 | RESOLVED |
| UDQ-CON-005 | AMBIGUITY | rules and sequences versus direct writes | UDQ-LOG-SPEC-001 r1; UDQ-SEQ-SPEC-001 r1; UDQ-OUT-SPEC-001 r1 | Rules and sequences were intended to remain governed, but the subsystem layer still needed an explicit statement that they do not bypass arbitration/authorization. | Rules and sequences emit governed requests or state transitions and do not become hidden direct-write paths. | UDQ-LOG-SPEC-001 r2; UDQ-SEQ-SPEC-001 r2; UDQ-OUT-SPEC-001 r2 | RESOLVED |
| UDQ-CON-006 | AMBIGUITY | remote capability parity versus backend policy | UDQ-REM-SPEC-001 r1; UDQ-SEC-SPEC-001 r0; UDQ-UI-SPEC-005 r0 | Remote observation and control boundaries were discussed, but the subsystem layer still needed more explicit non-parity and attribution language. | Remote clients are policy-bounded capability classes; parity with local capability shall never be assumed. | UDQ-REM-SPEC-001 r2; UDQ-SEC-SPEC-001 r1; UDQ-GOV-RPT-002 r0 | RESOLVED |
| UDQ-CON-007 | AMBIGUITY | authorization versus ui visibility | UDQ-SEC-SPEC-001 r0; UDQ-UI-MOD-001 r1; UDQ-OUT-SPEC-001 r1 | The corpus stated backend authority clearly, but subsystem wording still needed a direct statement that enabled controls do not equal authorization. | Authorization is backend-enforced policy. UI visibility and enabled-state are presentation choices and never constitute authorization by themselves. | UDQ-SEC-SPEC-001 r1; UDQ-OUT-SPEC-001 r2; UDQ-UI-MOD-001 r2 | RESOLVED |
| UDQ-CON-008 | AMBIGUITY | alarm acknowledgment and historical truth | UDQ-EVT-SPEC-001 r0; UDQ-HIS-SPEC-001 r1 | The event model already implied evidence retention, but the subsystem docs needed stronger cross-document wording so acknowledgment could not be mistaken for historical erasure. | Acknowledgment records recognition and attribution; it does not erase the alarm/event history. | UDQ-EVT-SPEC-001 r1; UDQ-HIS-SPEC-001 r2; UDQ-EXM-SPEC-001 r1 | RESOLVED |
| UDQ-CON-009 | RECONCILIATION | support-pack isolation versus product identity | ADR-0005 r0; UDQ-DEV-SPEC-001 r0; package proof line | Real-U6 proof could be misread as platform identity drift. | Real-U6 proof is a bounded support-pack specimen and does not redefine the universal-core identity. | bounded proof closeout recovery run | RESOLVED |
| UDQ-CON-010 | RECONCILIATION | governed actions versus hidden direct-write paths | UDQ-LOG-SPEC-001 r2; UDQ-SEQ-SPEC-001 r2; UDQ-OUT-SPEC-001 r2 | Rules/sequences could be mistaken for bypass channels. | Rules and sequences emit governed command intent only through command admission; they are not hidden direct-write paths. | bounded proof closeout recovery run | RESOLVED |
| UDQ-CON-011 | RECONCILIATION | duplicate emitters on one governed action | runtime action-claim implementation; UDQ-LOG-SPEC-001 r2 | Multiple emitters targeting one action could create contradictory behavior. | Governed-action claims suppress competing emitters and keep the first accepted claimant authoritative within the bounded implementation. | bounded proof closeout recovery run | RESOLVED |
| UDQ-CON-012 | RECONCILIATION | record identity versus chain correlation | runtime command/event journals; reviewer proof bundle | Unique record identifiers and business-level linkage could be conflated. | `command_id` and `event_id` remain unique record identifiers; `correlation_id` links related records within one governed-action chain. | bounded proof closeout recovery run | RESOLVED |
| UDQ-CON-013 | RECONCILIATION | runtime events versus domain events / alarm transitions | runtime metrics and proof docs | Runtime events and domain event/alarm transitions could be misread as one counter family. | Runtime events and domain event/alarm transitions remain distinct and shall be labeled separately in diagnostics and review artifacts. | bounded proof closeout recovery run | RESOLVED |

