---
document_id: UDQ-PROF-SPEC-001
title: Profiles, Persistence, Autosave, and Restore Specification
revision: r3
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
  - "UDQ-PROF-SPEC-001__Profiles_Persistence_Autosave_and_Restore_Specification__r1__WIP.md"
revision_history:
  - "r3 | 2026-03-27 | Added bench-continuity persistence seams for safe historical restore, persisted session summaries, and operator notes."
  - "r2 | 2026-03-22 | Added bounded implementation notes for restore origin metadata, autosave/session checkpoints, and shell-facing restore safety state."
  - "r1 | 2026-03-21 | Subsystem reconciliation pass: clarified restore boundaries, live revalidation, and anti-conflation rules."
---
# Profiles, Persistence, Autosave, and Restore Specification

## 1. Purpose [SEC:UDQ-PROF-SPEC-001::1]

This specification defines how UniversalDAQ shall persist UI/session state and governed configuration artifacts, and how it shall restore them without misrepresenting live runtime truth.

## 2. Canonical object classes [SEC:UDQ-PROF-SPEC-001::2]

UniversalDAQ shall distinguish at minimum:
- **session state**: ephemeral UI/workspace state from the most recent run
- **named profile**: user-intended saved configuration set
- **autosave snapshot**: machine-created preservation of recent edited state or session continuity
- **governed configuration artifact**: versioned configuration subject to stronger change control than ordinary local preferences

## 3. Anti-conflation rule [SEC:UDQ-PROF-SPEC-001::3]

Restore reconstructs local/session/configuration context.
Restore does **not** by itself reassert live machine state, output ownership, device connectivity, or command completion.

## 4. Bounded implemented slice [SEC:UDQ-PROF-SPEC-001::4]

The current bounded implementation now includes:
- restore results that preserve restore origin, profile identity, and restore timestamp
- shell-facing UI session state that preserves restore origin and restore safety posture
- explicit autosave and last-session checkpoint identifiers at the controller layer
- continued default `machine_write_intent = false` for restore execution in the bounded slice

## 5. Human review focus [SEC:UDQ-PROF-SPEC-001::5]

A human pass should verify that restored state is clearly separable from live runtime truth and that saved profile/autosave/session flows remain visibly non-actuating.

## 6. Session persistence and bench continuity seam [SEC:UDQ-PROF-SPEC-001::6]

The bounded bench-continuity slice may persist convenience state such as preferred adapter identity, preferred device identity, preferred channel binding, panel/workspace posture, pending operator note draft, and a bounded historical session summary.

The persisted bench state shall be treated as **historical context only** until a new live session confirms device presence, signal freshness, and current values.

## 7. Operator notes and persisted session summaries [SEC:UDQ-PROF-SPEC-001::7]

Operator-authored notes shall remain distinct from system-generated events. Persisted session summaries may carry operator notes, control posture, alarm posture digest, and last known signal presentation, but they shall not be presented as restored live truth.

## 8. Restore rejection and fallback [SEC:UDQ-PROF-SPEC-001::8]

If a preferred device, preferred channel, or other persisted convenience item is unavailable at restore time, the UI shall degrade gracefully, explain the skipped continuity item in diagnostics, and remain in a safe non-live posture.

## 9. Recent-session review and lightweight reporting seam [SEC:UDQ-PROF-SPEC-001::9]

Persisted session summaries shall remain structured enough to support a bounded recent-session review list, a historical session detail view, and a deterministic lightweight session report without reloading raw device-layer objects.

The persisted summary seam may therefore carry compact historical fields such as provenance label, bounded trace preview, completeness label, and last event digest, provided those fields remain clearly historical and are never re-presented as current live truth.
