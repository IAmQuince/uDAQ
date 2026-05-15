# Audit and Governance

**Controlled document**  
ID: UDQ-HANDBOOK-AUDIT-001  
Status: ACTIVE  
Revision: r15  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-REG-003, UDQ-GOV-LOG-001, UDQ-SPRINT-SOP-001  
Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## Package identity

- Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`
- Package status: Sprint Zero roadmap/governance stabilization baseline
- Runtime behavior changes: none

## Common governance commands

Run these from `ACTIVE/` unless otherwise noted.

- package-entry: `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_package_entry_surfaces --package-root .`
- readme-control: `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_readme_control --package-root .`
- docs completeness: `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_completeness --package-root .`
- docs classification: `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_classification --package-root .`
- docs debt: `PYTHONDONTWRITEBYTECODE=1 python -m tools.governance.validate_document_debt --package-root .`
- active-lane boundedness: `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_active_lane_boundedness --package-root .`
- Windows path budget: `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.validate_windows_path_budget --package-root . --delivery-root 20260515_02_mapping`
- generated cleanup: `PYTHONDONTWRITEBYTECODE=1 python -m tools.package_build.clean_generated_artifacts`

## Closeout rule

Governance validators are package gates when package identity, docs, registries, release surfaces, or entry surfaces change. Feature sprints should still select changed-area tests deliberately rather than treating every diagnostic utility as a mandatory inner-loop gate.
