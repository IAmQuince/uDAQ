---
document_id: UDQ-UI-SPEC-001
title: Workspace and Page Specifications
revision: r1
status: WIP
document_class: ui-detail-spec
owner: UniversalDAQ
depends_on:
  - UDQ-UI-ARCH-001
  - UDQ-UI-SPEC-000
  - UDQ-UI-SPEC-006
  - UDQ-DEV-SPEC-001
  - UDQ-SIG-SPEC-001
  - UDQ-OUT-SPEC-001
  - UDQ-LOG-SPEC-001
  - UDQ-SEQ-SPEC-001
  - UDQ-DIAG-SPEC-001
  - UDQ-HIS-SPEC-001
supersedes:
  - UDQ-UI-SPEC-001__Workspace_Page_Specifications__r0__WIP.md
revision_history:
  - revision: r1
    date: 2026-03-25
    summary: Docs-only UI refinement pass. Replaced the flat page inventory with a four-workspace contract and explicitly defined the Control workspace subtab set.
  - revision: r0
    date: 2026-03-21
    summary: Defines the primary workspace/page set and what each surface contains.
---
# Workspace and Page Specifications [SEC:UDQ-UI-SPEC-001::0]

## 1. Purpose [SEC:UDQ-UI-SPEC-001::1]

This document defines the major workspaces in the primary UniversalDAQ UI and the required content expectations for each.

## 2. Workspace Set [SEC:UDQ-UI-SPEC-001::2]

The core workspace set is:
- Run
- Control
- Review
- System

Each workspace answers a different family of operator questions. No workspace shall exist without a clear primary question set.

## 3. Run Workspace [SEC:UDQ-UI-SPEC-001::3]

Run answers:
- What is happening now?
- What is healthy or degraded?
- What is active?
- What may I do right now?

Run shall keep visible:
- live graph
- selected key values and status
- active protections/interlocks summary
- active sequence snapshot when relevant
- bounded command controls where authorized
- obvious return-to-live posture if detached

Run shall avoid becoming a deep authoring workspace.

## 4. Control Workspace [SEC:UDQ-UI-SPEC-001::4]

Control answers:
- How is behavior defined?
- What dependencies exist?
- What will happen if this logic is used?
- Is the authored control system valid, testable, and deployable?

Control shall include the following subtabs or equivalent sub-surfaces:
- Overview
- Variables
- Logic
- Sequence
- Interlocks / Protections
- Actions / Bindings
- Modes / States
- Test / Simulation
- Audit / History

The Sequence subtab remains a supporting feature for convenient procedural changes to outputs, setpoints, and internal or virtual variables even when a full broader control model is not required.

## 5. Review Workspace [SEC:UDQ-UI-SPEC-001::5]

Review answers:
- What happened over time?
- What actions, events, and state changes correlate with this range?
- What evidence should be exported or recorded?

Review shall provide:
- historical graph access
- timeline and table evidence
- event/alarm/command/annotation review
- selected-range evidence correlation
- compare/bookmark/export capabilities where governed

## 6. System Workspace [SEC:UDQ-UI-SPEC-001::6]

System answers:
- What devices exist?
- What capabilities and identities are known?
- How are bindings, diagnostics, and profiles configured?
- What service or dependency issues exist?

System shall provide:
- device onboarding/discovery
- capability and identity views
- diagnostics and health
- profiles/settings
- advanced service detail when appropriate

## 7. Always-Visible versus Drill-Down Rule [SEC:UDQ-UI-SPEC-001::7]

Each workspace shall define:
- what is always visible
- what is contextual
- what belongs in the inspector
- what belongs in the lower pane

High-value current truth, current authoring validity, and immediate return-to-live affordances shall not be hidden behind deep drill-down paths.

## 8. Cross-Workspace Handoffs [SEC:UDQ-UI-SPEC-001::8]

Required handoffs include:
- Run → Control for dependency and authored-behavior inspection
- Run → Review for evidence correlation
- System → Control for newly discovered devices and variable sources
- Review → Run via explicit return-to-live
- Review → Control when historical evidence motivates authoring changes

## 9. What Not to Do [SEC:UDQ-UI-SPEC-001::9]

The UI shall not:
- flatten all concerns into one endless tab strip
- hide critical trust state in secondary popups only
- treat sequences as the only control-authoring concept
- mix device onboarding, logic authoring, and forensic review into one ambiguous screen

## 10. Human Review Focus [SEC:UDQ-UI-SPEC-001::10]

A reviewer should quickly confirm that:
- the workspace structure is Run / Control / Review / System
- Control is broader than a rules page or sequencer page
- Sequence remains preserved as a useful, bounded feature
- Run, Review, and System each have a distinct purpose
