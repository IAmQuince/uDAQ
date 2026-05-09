---
document_id: UDQ-EXP-SPEC-001
title: Export, Review, and Evidence Bundle Specification
revision: r0
status: WIP
classification:
  domain: EXP
  type: SPEC
  sequence: '001'
effective_date: '2026-03-22'
authoring_context: UniversalDAQ
depends_on:
- UDQ-AUD-SPEC-001
- UDQ-GOV-STD-001
- UDQ-HIS-SPEC-001
- UDQ-REL-SPEC-001
- UDQ-SCM-STD-001
supersedes: []
superseded_by: []
machine_readable_artifacts: []
audit_exceptions: []
---
# Export, Review, and Evidence Bundle Specification

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-22 | WIP | Updated in place to reflect the bounded historian/export implementation slice: explicit export intents, manifest-backed bundle generation, review artifact serialization, and export attribution seams. |

# 1. Purpose [SEC:UDQ-EXP-SPEC-001::1]

This specification defines how UniversalDAQ shall create, identify, and govern exports, review artifacts, and evidence bundles.

# 2. Scope [SEC:UDQ-EXP-SPEC-001::2]

This specification applies to:

- ad hoc user exports
- governed review exports
- audit/evidence bundles
- historian-derived extracts
- diagnostic and configuration snapshots
- package-ready review artifacts generated from runtime or pre-code documentation baselines

# 3. Canonical artifact classes [SEC:UDQ-EXP-SPEC-001::3]

UniversalDAQ shall distinguish at minimum:

- **simple export**: a user-requested output such as CSV, image, or selected report extract
- **review artifact**: a structured output prepared for human review with traceable scope and context
- **evidence bundle**: a governed collection of artifacts sufficient to support a claim, diagnosis, audit, or release decision
- **diagnostic snapshot**: a structured payload emitted by a bounded diagnostic harness for review or package inclusion

# 4. Export doctrine [SEC:UDQ-EXP-SPEC-001::4]

## 4.1 Explicit scope [SEC:UDQ-EXP-SPEC-001::4.1]

Exports shall preserve or declare their scope clearly, including time range, selected objects, filters, overlays, and source baseline where relevant.

## 4.2 Provenance [SEC:UDQ-EXP-SPEC-001::4.2]

Exports should carry enough provenance to identify:

- when they were generated
- by whom or by what client/session
- from which runtime or documentation baseline context
- what inputs and filters were used
- what authority posture was active when export was requested

## 4.3 Non-destructive generation [SEC:UDQ-EXP-SPEC-001::4.3]

Export generation shall not mutate the underlying governed records merely because an export was produced.

# 5. Bounded implemented slice [SEC:UDQ-EXP-SPEC-001::5]

The current bounded implementation now includes:

- typed `ExportScope` and `ExportIntent` models
- typed `ArtifactManifest`, `ArtifactDescriptor`, and `ReviewArtifact` models
- deterministic manifest-backed bundle assembly from command, restore, alarm, and shell-session evidence records
- JSON manifest serialization, CSV evidence record serialization, and Markdown review artifact serialization
- optional inclusion of profile snapshots and diagnostic snapshots inside the serialized artifact set
- shell-facing export preview and last-export result state

# 6. Evidence bundle model [SEC:UDQ-EXP-SPEC-001::6]

## 6.1 Bundle contents [SEC:UDQ-EXP-SPEC-001::6.1]

Evidence bundles may include, as appropriate:

- selected historian extracts
- event/alarm timelines
- diagnostic summaries
- configuration/profile snapshots
- rule or sequence definitions and runtime traces
- audit results
- release manifests and notes
- explanatory summary documents

## 6.2 Bundle identity [SEC:UDQ-EXP-SPEC-001::6.2]

Evidence bundles shall have stable identity and timestamped creation metadata. Where tied to a baseline/package decision, the associated package release ID or documentation baseline ID should be preserved.

## 6.3 Bundle integrity [SEC:UDQ-EXP-SPEC-001::6.3]

Evidence-bundle composition shall be deterministic enough that another reviewer can understand what was included and what was not. A manifest inside the bundle is preferred, and the current bounded implementation now emits one by default.

# 7. Output formats [SEC:UDQ-EXP-SPEC-001::7]

The platform may support multiple output formats such as CSV, JSON, Markdown, images, or packaged zip bundles. Format support shall remain secondary to scope/provenance clarity.

# 8. UI obligations [SEC:UDQ-EXP-SPEC-001::8]

The UI shall support, at minimum:

- clear selection of export scope
- visibility of what source data/configuration is being exported
- preview or summary of the export intent where practical
- review-oriented export pathways distinct from quick ad hoc export where the consequences differ
- visibility of generated artifact location and identity
- visibility of omission notes and warning count where scope is partial or empty

# 9. Evidence and audit alignment [SEC:UDQ-EXP-SPEC-001::9]

Exports and bundles used to support governed claims shall align with the implementation-proof and package-audit model. The platform should support attaching or linking audit results and manifest information when export artifacts are intended for package inclusion.

# 10. Security and authorization implications [SEC:UDQ-EXP-SPEC-001::10]

The platform shall apply authorization policy to export surfaces so that users cannot automatically export data/configuration beyond their allowed scope. The current bounded implementation only preserves actor identity, session identity, origin, and authority state for future enforcement; it does not yet implement full runtime authorization gating.

# 11. Validation and test obligations [SEC:UDQ-EXP-SPEC-001::11]

Export and bundle behavior shall be testable for:

- scope correctness
- provenance completeness
- bundle manifest completeness
- deterministic inclusion/exclusion behavior
- large-range historian export handling
- package-ready artifact generation when required by governance
- empty-scope warnings without destructive side effects

# 12. Anti-patterns [SEC:UDQ-EXP-SPEC-001::12]

The platform shall avoid:

- exports with ambiguous time range or source scope
- evidence bundles that omit manifest/provenance information
- “review” artifacts that cannot be traced back to governed sources
- ad hoc export paths that bypass authorization or evidence policy
- bundle generation that silently mutates the underlying governed state

## 7. Canonical runtime evidence bundle v1 [SEC:UDQ-EXP-SPEC-001::7]
The bounded lifecycle review bundle may now expose `canonical_runtime_evidence_bundle_v1` as an additive semantic route through existing runtime truth. That route shall preserve identity, runtime state, reviewer rollup, summaries, recent runtime/alarm/operator evidence, diagnostic snapshots, metric layers, and provenance.

## 13. Lightweight session review reports [SEC:UDQ-EXP-SPEC-001::13]

The bounded review slice may emit deterministic lightweight session reports composed from persisted session summaries, operator notes, control/alarm posture digests, and compact signal review context. These reports are historical review artifacts, not claims of current live device state.

The initial bounded implementation should prefer text-first artifacts such as Markdown plus compact JSON payloads over rich designer-driven reports.
