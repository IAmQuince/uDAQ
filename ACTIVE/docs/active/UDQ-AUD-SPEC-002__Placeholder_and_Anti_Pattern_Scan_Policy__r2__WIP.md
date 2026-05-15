---
document_id: UDQ-AUD-SPEC-002
title: Placeholder and Anti-Pattern Scan Policy
revision: r2
status: WIP
document_class: scan_policy
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-SPEC-002
  - UDQ-AUD-SPEC-001
  - UDQ-REL-SPEC-001
supersedes:
  - UDQ-AUD-SPEC-002__Placeholder_and_Anti_Pattern_Scan_Policy__r1__WIP.md
---
# UDQ-AUD-SPEC-002 Placeholder and Anti-Pattern Scan Policy

## 1. Purpose [SEC:UDQ-AUD-SPEC-002::1]
This policy defines how drafting residue and documentation anti-patterns shall be detected, classified, and reported in UniversalDAQ packages.

## 2. Core Position [SEC:UDQ-AUD-SPEC-002::2]
UniversalDAQ shall not use broad audit exceptions as a substitute for fixing defects. The scan system shall distinguish between prohibited unfinished content in normative documents and explicitly allowed blank or prompt-like content inherent to a controlled template or form.

## 3. Prohibited Use of Exceptions [SEC:UDQ-AUD-SPEC-002::3]
No scan allowance, override, waiver, or exception shall be used to bypass findings related to broken YAML front matter, missing required metadata, missing required files, empty required files, broken dependencies, broken cross-references, malformed registries, or incorrect document identity or revision alignment.

## 4. Allowed-Pattern Model [SEC:UDQ-AUD-SPEC-002::4]
UniversalDAQ shall use an allowed-pattern model rather than a broad exception model.

### 4.1 Rule-scoped allowances [SEC:UDQ-AUD-SPEC-002::4.1]
Any allowance shall be scoped to a specific scan rule, a specific document class, and optionally a specific section or field pattern.

### 4.2 Document-class allowances [SEC:UDQ-AUD-SPEC-002::4.2]
Allowed pattern behavior shall be determined by document class:
- normative specifications and standards: no class-scoped allowed-pattern handling except explicitly defined tokens in machine-readable examples
- reports: limited WIP markers may be allowed only in designated draft/result sections
- templates/forms: controlled placeholder fields are allowed where the template requires user completion
- machine-readable artifacts: no class-scoped allowed-pattern handling except schema-declared null/default fields

### 4.3 Transparency [SEC:UDQ-AUD-SPEC-002::4.3]
Every allowance shall be visible in policy and traceable by rule name and document class. Hidden or ad hoc per-file carve-outs are prohibited.

## 5. Placeholder Categories [SEC:UDQ-AUD-SPEC-002::5]
The scan policy shall classify drafting-residue-like content into the following categories:
- controlled form field placeholder
- instructional prompt text
- unfinished normative text
- temporary drafting marker
- template token/example token
- prohibited ambiguity marker

Only the first two categories are allowed by design, and only in approved document classes and locations.

## 6. Anti-Pattern Categories [SEC:UDQ-AUD-SPEC-002::6]
The scan shall identify at minimum TODO/TBD/FIXME style drafting residue, unresolved placeholder brackets intended for manual fill, contradictory revision language, “to be written later” style normative gaps, narrative-only requirement language that evades traceability, and cross-reference text that names a controlled document but omits its identifier where required.

## 7. Reporting Rules [SEC:UDQ-AUD-SPEC-002::7]
The scan report shall separate allowed pattern hits, warning-level findings, and failure-level findings. Allowed pattern hits shall not be counted as defects.

## 8. Governance Rules [SEC:UDQ-AUD-SPEC-002::8]
Broad document waivers are prohibited. Per-file hidden suppression lists are prohibited. Rule/document-class allowances shall be declared in controlled policy or manifest data. Any new allowance rule shall require revision of this policy or an explicitly governed companion artifact.

## 9. Auditor Expectations [SEC:UDQ-AUD-SPEC-002::9]
The package-root auditor shall implement this policy so that structural integrity checks remain non-waivable, allowed patterns are shown separately from findings, and the auditor never silently suppresses a finding without a declared governing rule.

## 10. Current Design Intent [SEC:UDQ-AUD-SPEC-002::10]
At the current stage of the UniversalDAQ corpus:
- template documents may contain controlled placeholders in declared form fields
- normative docs shall be held to a no-placeholder standard
- draft reports may contain limited result-pending language only where explicitly structured as draft outcome fields

## 11. Revision History [SEC:UDQ-AUD-SPEC-002::11]
- r1: Replaced broad audit-exception concept with rule-scoped, document-class-based allowed-pattern model and explicitly prohibited structural-integrity waivers.
- r0: Initial issue.
