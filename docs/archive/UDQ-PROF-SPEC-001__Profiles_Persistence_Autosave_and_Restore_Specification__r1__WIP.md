---
document_id: UDQ-PROF-SPEC-001
title: Profiles, Persistence, Autosave, and Restore Specification
revision: r1
status: WIP
document_class: subsystem_spec
owner: UniversalDAQ
depends_on:
  - "UDQ-GOV-STD-001"
  - "UDQ-REL-SPEC-001"
  - "UDQ-UI-ARCH-001"
  - "UDQ-UI-MOD-001"
  - "UDQ-UI-NAR-001"
  - "UDQ-GOV-GLO-001"
  - "UDQ-GOV-STD-002"
supersedes:
  - "UDQ-PROF-SPEC-001__Profiles_Persistence_Autosave_and_Restore_Specification__r0__WIP.md"
revision_history:
  - "r1 | 2026-03-21 | Subsystem reconciliation pass: clarified restore boundaries, live revalidation, and anti-conflation rules."
  - "r0 | 2026-03-21 | Prior active revision carried forward before subsystem reconciliation pass."
---
# Profiles, Persistence, Autosave, and Restore Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r1 | 2026-03-21 | WIP | Subsystem reconciliation pass: clarified restore boundaries, live revalidation, and anti-conflation rules. |
| r0 | 2026-03-21 | WIP | Initial issue defining user/session persistence, named profiles, autosave behavior, and restore continuity boundaries. |

# 1. Purpose [SEC:UDQ-PROF-SPEC-001::1]

This specification defines how UniversalDAQ shall persist UI/session state and governed configuration artifacts, and how it shall restore them without misrepresenting live runtime truth.

# 2. Scope [SEC:UDQ-PROF-SPEC-001::2]

This specification applies to:

- window/layout/workspace persistence
- user-editable profile objects
- autosave snapshots
- startup restore and crash/restart continuity
- configuration versus runtime-state boundaries
- export/import of profile-like artifacts when supported

# 2A. Semantic Closure and Anti-Conflation Rule [SEC:UDQ-PROF-SPEC-001::2A]

This specification shall preserve the glossary-owned separation between **profile**, **autosave**, **restore**, **workspace state**, and **machine state**. Restore reconstructs local/session/configuration context. Restore does **not** by itself reassert live machine state, output ownership, device connectivity, or command completion. Any restored view that depends on live truth shall be revalidated from backend-authoritative publication.

# 3. Canonical object classes [SEC:UDQ-PROF-SPEC-001::3]

UniversalDAQ shall distinguish at minimum:

- **session state**: ephemeral UI/workspace state from the most recent run
- **named profile**: user-intended saved configuration set
- **autosave snapshot**: machine-created preservation of recent edited state or session continuity
- **governed configuration artifact**: versioned configuration subject to stronger change control than ordinary local preferences

# 4. Persistence boundaries [SEC:UDQ-PROF-SPEC-001::4]

## 4.1 What may be persisted [SEC:UDQ-PROF-SPEC-001::4.1]

The platform may persist, under policy:

- window positions, dock layout, selected workspaces, and graph preferences
- signal naming, visibility, grouping, and presentation preferences
- device/protocol configuration objects
- rules, conditions, and sequences in their governed representations
- export/review preferences
- selected diagnostics or service view filters

## 4.2 What shall not be implied by persistence [SEC:UDQ-PROF-SPEC-001::4.2]

Restored persistence shall not imply restoration of live machine state, output ownership, active commands, or device connectivity. The UI shall make clear what was restored from saved state and what has been freshly revalidated from the live backend.

# 5. Session restore model [SEC:UDQ-PROF-SPEC-001::5]

## 5.1 Last-session continuity [SEC:UDQ-PROF-SPEC-001::5.1]

The platform should restore the most recent reasonable UI/session state on startup when policy allows, including layout and inspection context, provided that restored state is clearly separable from live runtime truth.

## 5.2 Revalidation boundary [SEC:UDQ-PROF-SPEC-001::5.2]

After restore, the backend shall revalidate live devices, signals, outputs, health, and command ownership before the UI presents them as active/authoritative.

## 5.3 Crash recovery [SEC:UDQ-PROF-SPEC-001::5.3]

Crash or abnormal shutdown recovery shall prefer preserving operator continuity without claiming unverified runtime continuity. Autosave snapshots should help reconstruct recent editing state and review context.

# 6. Named profile model [SEC:UDQ-PROF-SPEC-001::6]

## 6.1 Profile identity [SEC:UDQ-PROF-SPEC-001::6.1]

Named profiles shall have stable identity and user-facing names distinct from mere filenames.

## 6.2 Profile contents [SEC:UDQ-PROF-SPEC-001::6.2]

Profiles may include, under policy:

- workspace/layout state
- device selections or logical configuration sets
- rules/conditions enablement state
- sequence parameter sets
- graph/review preferences
- local non-governed preferences

The platform shall clearly differentiate a profile that changes only presentation from one that changes operational behavior.

## 6.3 Save/load/apply semantics [SEC:UDQ-PROF-SPEC-001::6.3]

Loading a profile shall not silently apply live commands unless the profile class explicitly includes governed operational changes and the actor is authorized to apply them. Preview/review before apply is preferred when operational consequences exist.

# 7. Autosave doctrine [SEC:UDQ-PROF-SPEC-001::7]

## 7.1 Autosave purpose [SEC:UDQ-PROF-SPEC-001::7.1]

Autosave exists to reduce loss of editing, layout, and recent review context. It is not a hidden substitute for explicit governed save/apply behavior.

## 7.2 Autosave cadence and scope [SEC:UDQ-PROF-SPEC-001::7.2]

The platform shall be capable of periodic autosave for selected object classes. Autosave scope shall be explicit and reviewable.

## 7.3 Autosave retention [SEC:UDQ-PROF-SPEC-001::7.3]

Autosave snapshots shall have bounded retention and a predictable cleanup policy.

# 8. Restore UX obligations [SEC:UDQ-PROF-SPEC-001::8]

The UI shall make it clear:

- what was restored from saved state
- what has been revalidated live
- what remains unavailable because devices or services are offline
- whether the current state is dirty/edited relative to the last saved profile
- whether the operator is viewing a historical/autosaved snapshot versus live current configuration

# 9. Versioning and compatibility [SEC:UDQ-PROF-SPEC-001::9]

Saved profiles and autosave artifacts shall carry enough schema/version identity to support:

- forward/backward compatibility statements where possible
- migration handling when formats evolve
- safe rejection with explanation when an artifact cannot be loaded faithfully

# 10. Historian and evidence implications [SEC:UDQ-PROF-SPEC-001::10]

Material save/load/apply/restore actions that affect governed operational behavior shall be evidence-bearing. Purely cosmetic local preference changes may be excluded from heavy evidence trails, but the policy shall be explicit.

# 11. Remote and multi-client implications [SEC:UDQ-PROF-SPEC-001::11]

Where multiple clients exist, the platform shall distinguish:

- client-local session state
- shared governed configuration
- shared runtime truth published by backend authority

A remote client restoring its own layout shall not rewrite another client’s local view by accident.

# 12. Validation and test obligations [SEC:UDQ-PROF-SPEC-001::12]

Profiles/persistence/restore behavior shall be testable for:

- last-session restore correctness
- startup revalidation boundaries
- autosave continuity after abnormal shutdown
- schema/version migration handling
- explicit distinction between local preference restore and operational apply
- multi-client separation of local versus shared state

# 13. Anti-patterns [SEC:UDQ-PROF-SPEC-001::13]

The platform shall avoid:

- restoring UI state in a way that implies unverified live machine state
- silently applying operational changes merely because a profile was loaded
- mixing local preferences and governed operational configuration without clear boundaries
- losing recent user edits because autosave scope or retention was undefined
- one client’s local restore overwriting another client’s local workspace unexpectedly
