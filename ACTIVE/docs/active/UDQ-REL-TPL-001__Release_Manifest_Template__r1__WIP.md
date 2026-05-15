---
document_id: UDQ-REL-TPL-001
title: Release Manifest Template
revision: r1
status: WIP
document_class: release_template
classification:
  domain: REL
  type: TPL
  sequence: '001'
effective_date: '2026-03-21'
authoring_context: UniversalDAQ
depends_on:
- UDQ-REL-SPEC-001
- UDQ-SCM-STD-001
- UDQ-GOV-SPEC-002
supersedes: []
superseded_by: []
machine_readable_artifacts: []
---
# Release Manifest Template

## Revision History

| Revision | Date | Status | Summary |
|---|---|---|---|
| r0 | 2026-03-21 | WIP | Revision that cleans scan-noise wording while preserving the governed manifest form. |

# 1. Purpose [SEC:UDQ-REL-TPL-001::1]

This template defines the minimum manifest content for a governed UniversalDAQ send-out package. The manifest is intended to be readable by both humans and package-audit tooling.

# 2. Template Usage Rules [SEC:UDQ-REL-TPL-001::2]

The manifest shall be placed at package root unless the package specification explicitly states otherwise. The manifest shall be completed rather than left with unresolved template markers. If a field does not apply, it shall be explicitly marked `N/A` or an equivalent governed null value.

# 3. Recommended Filename [SEC:UDQ-REL-TPL-001::3]

Recommended manifest filename:

`docs/release/RELEASE_MANIFEST.yaml`

Alternative names are allowed only if the package-root auditor and release notes explicitly identify them.

# 4. Template [SEC:UDQ-REL-TPL-001::4]

```yaml
manifest_version: "1.0"
package_release_id: "UDQ-PKG-precode-20260321-01-WIP"
package_class: "PRECODE_BASELINE"
package_status: "WIP"
issue_date: "2026-03-21"
comparison_baseline: "N/A"

code_baseline_id: "NO_CODE_SCOPE"
documentation_baseline_id: "UDQ-DOC-BASELINE-20260321-01"

auditor:
  file: "udq_doc_audit_v2.py"
  expected_profile: "working-package"
  expected_minimum_result: "PASS_WITH_WARNINGS"

compatibility:
  python: "3.11+"
  operating_systems: ["Windows 10/11", "Linux"]
  devices_or_protocols_in_scope: ["Documentation-only baseline"]
  backward_compatibility_statement: "N/A"
  known_incompatibilities: []

source_of_truth:
  documents:
    controlled_index: "UDQ-GOV-LOG-001__Controlled_Document_Index__r4__WIP.md"
    document_registry_json: "universalDAQ_document_registry_r5.json"
    document_registry_csv: "universalDAQ_document_registry_r5.csv"
    cross_reference_edges_csv: "universalDAQ_cross_reference_edges_r3.csv"
    requirement_registry_json: "universalDAQ_requirement_registry_r2.json"
    requirement_registry_csv: "universalDAQ_requirement_registry_r2.csv"
  code:
    entry_points: []
    backend_authority_modules: []
    frontend_shell_modules: []
    schema_or_config_sources: []

included_artifacts:
  required_root_files:
    - "udq_doc_audit_v2.py"
    - "docs/release/RELEASE_MANIFEST.yaml"
    - "docs/release/RELEASE_NOTES.md"
  required_directories:
    - "audit_reports/"
  controlled_documents:
    - "UDQ-GOV-LOG-001__Controlled_Document_Index__r4__WIP.md"
    - "UDQ-GOV-STD-001__Document_Control_Scheme__r2__WIP.md"

exceptions:
  - artifact: "N/A"
    reason: "N/A"
    impact: "N/A"
    mitigation: "N/A"

known_issues:
  - "Replace with package-specific issue list."

notes:
  reviewer_attention_items:
    - "Replace with package-specific reviewer guidance."
  execution_guidance:
    - "Run the package-root auditor from package root after unzip."
```

# 5. Field Notes [SEC:UDQ-REL-TPL-001::5]

## 5.1 Identity Fields [SEC:UDQ-REL-TPL-001::5.1]

The identity block shall uniquely identify the package, class, date, and comparison point.

## 5.2 Compatibility Block [SEC:UDQ-REL-TPL-001::5.2]

The compatibility block shall state runtime and scope assumptions rather than leaving them implicit.

## 5.3 Source-of-Truth Block [SEC:UDQ-REL-TPL-001::5.3]

The source-of-truth block shall identify the actual files a reviewer should trust first when interpreting the package.

## 5.4 Included Artifacts Block [SEC:UDQ-REL-TPL-001::5.4]

The included-artifacts block shall list what is expected to be present, not just what happened to be copied into the package.

# 6. Anti-Patterns [SEC:UDQ-REL-TPL-001::6]

The following are prohibited:

- leaving unresolved template IDs in a sent package
- omitting the source-of-truth declaration
- listing files in the manifest that are absent from the package
- using a manifest whose stated auditor filename does not exist at package root
