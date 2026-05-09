---
document_id: UDQ-PROF-SPEC-001
title: Profiles, Persistence, Autosave, and Restore Specification
revision: r4
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
  - "UDQ-PROF-SPEC-001__Profiles_Persistence_Autosave_and_Restore_Specification__r2__WIP.md"
revision_history:
  - "r4 | 2026-03-28 | Docs-only UI alignment pass: added saved graph setups, trace-style persistence, legend preferences, autosave toggle requirements, and in-app save/load/edit expectations for settings and profiles."
  - "r3 | 2026-03-27 | Added bench-continuity persistence seams for safe historical restore, persisted session summaries, and operator notes."
---
# Profiles, Persistence, Autosave, and Restore Specification

## 1. Purpose [SEC:UDQ-PROF-SPEC-001::1]

This specification defines how UniversalDAQ shall persist UI/session state, graph setups, trace styles, and governed configuration artifacts, and how it shall restore them without misrepresenting live runtime truth.

## 2. Canonical object classes [SEC:UDQ-PROF-SPEC-001::2]

UniversalDAQ shall distinguish at minimum:
- **session state**
- **named profile**
- **autosave snapshot**
- **graph setup**
- **trace-style preset**
- **governed configuration artifact**

## 3. Anti-conflation rule [SEC:UDQ-PROF-SPEC-001::3]

Restore reconstructs local/session/configuration context. Restore does **not** by itself reassert live machine state, output ownership, device connectivity, alarm truth, signal freshness, or command completion.

## 4. Graph- and shell-related persistence [SEC:UDQ-PROF-SPEC-001::4]

The persistence model may include:
- layout and dock arrangement
- preferred workspace and explorer posture
- preferred adapter/device/channel continuity
- graph setups
- per-trace presentation settings
- legend mode and legend preferences
- alarm-visual preferences where user-configurable
- recent/favorite signal collections
- operator notes and persisted session summaries

## 5. Autosave requirement [SEC:UDQ-PROF-SPEC-001::5]

Autosave shall be a user-visible and user-editable setting. The user shall be able to:
- enable or disable autosave
- adjust autosave cadence where applicable
- understand what object classes autosave covers

## 6. Save / load / edit requirement [SEC:UDQ-PROF-SPEC-001::6]

All major settings and profiles relevant to the operator shell shall be savable, loadable, and editable from inside the application. The user shall not be forced into raw file editing for ordinary settings management.

## 7. Historical-only restore requirement [SEC:UDQ-PROF-SPEC-001::7]

Persisted session summaries, graph setups, prior values, and other historical context may be restored as convenience state, but they shall remain clearly historical until a live session re-establishes current truth.

## 8. Human Review Focus [SEC:UDQ-PROF-SPEC-001::8]

A reviewer should quickly confirm that:
- graph setups and trace styles are first-class persisted objects
- autosave is user-toggleable
- settings and profiles are editable in-app
- restored historical graph context is not misrepresented as current live truth

## 2026-03-28 implementation addendum — shell quick views
- Shell quick views may persist dock/widget arrangement, panel visibility, selected workspace, and panel/tab emphasis without claiming full scenario serialization.
- Autosave and restore behavior shall preserve last known shell arrangement and the user’s current trace-style state independently of named quick views.
