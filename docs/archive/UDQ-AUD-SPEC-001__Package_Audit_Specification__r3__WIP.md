---
document_id: UDQ-AUD-SPEC-001
title: Package Audit Specification
revision: r3
status: WIP
document_class: audit_spec
owner: UniversalDAQ
depends_on:
  - UDQ-GOV-STD-001
  - UDQ-GOV-SPEC-002
  - UDQ-AUD-SPEC-002
  - UDQ-REL-SPEC-001
supersedes:
  - UDQ-AUD-SPEC-001__Package_Audit_Specification__r2__WIP.md
---
# UDQ-AUD-SPEC-001 Package Audit Specification

## 1. Purpose [SEC:UDQ-AUD-SPEC-001::1]
This specification defines what the UniversalDAQ package audit shall check, how findings shall be classified, and how audit results shall be used in package disposition decisions.

## 2. Audit Objectives [SEC:UDQ-AUD-SPEC-001::2]
The package audit shall verify package structural integrity, controlled-document integrity, registry and cross-reference integrity, dependency presence and non-emptiness, package-composition compliance, draft-residue and anti-pattern compliance, and readiness disposition by package class/profile.

## 3. Severity Model [SEC:UDQ-AUD-SPEC-001::3]
Audit outputs shall classify results as PASS, PASS WITH WARNINGS, or FAIL.

### 3.1 Failure-level findings [SEC:UDQ-AUD-SPEC-001::3.1]
A finding shall be failure-level if it affects identity, integrity, dependency correctness, or required package composition.

### 3.2 Warning-level findings [SEC:UDQ-AUD-SPEC-001::3.2]
A finding may be warning-level if it does not invalidate the package but should be corrected before a tighter release class.

### 3.3 Allowed-pattern hits [SEC:UDQ-AUD-SPEC-001::3.3]
Allowed-pattern hits are informational only and shall not be treated as warnings or failures.

## 4. Non-waivable Audit Domains [SEC:UDQ-AUD-SPEC-001::4]
The following audit domains are non-waivable: file existence for required artifacts, parseability of governed machine-readable artifacts, YAML/front matter integrity where required, controlled-document identity consistency, required dependency existence, required file non-emptiness, and registry/doc alignment for declared controlled documents.

## 5. Allowed-Pattern Interaction [SEC:UDQ-AUD-SPEC-001::5]
The package audit shall use UDQ-AUD-SPEC-002 to distinguish prohibited drafting residue, controlled form fields in governed templates, and allowed template prompt structures. The audit shall not use broad document-level suppression.

## 6. Package Profiles [SEC:UDQ-AUD-SPEC-001::6]
The audit shall support at minimum foundation, working-package, and release-candidate profiles.

## 7. Human and Historical Outputs [SEC:UDQ-AUD-SPEC-001::7]
The audit shall produce immediate human-readable console output, a human-readable report artifact, a machine-readable report artifact, and a findings export suitable for sorting and review.

## 8. Disposition Rules [SEC:UDQ-AUD-SPEC-001::8]
Package disposition shall be based on the combination of selected audit profile, finding severity, package class, and reviewer judgment where permitted by governance.

## 9. Governance Constraint [SEC:UDQ-AUD-SPEC-001::9]
Audit results shall not be made green by undocumented suppression. If a rule needs refinement, the governing policy shall be revised.

## 10. Revision History [SEC:UDQ-AUD-SPEC-001::10]
- r1: Tightened allowed-pattern treatment, prohibited broad audit exceptions, and clarified non-waivable domains.
- r0: Initial issue.
