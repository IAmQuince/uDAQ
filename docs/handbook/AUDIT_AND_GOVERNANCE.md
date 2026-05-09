# Audit and Governance

**Controlled document**  
ID: UDQ-HANDBOOK-AUDIT-001  
Status: ACTIVE  
Revision: r14  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-REG-003, UDQ-GOV-LOG-001

## Package identity
- Package ID: `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`

## Common commands
- package-entry: `python -m tools.governance.validate_package_entry_surfaces --package-root .`
- readme-control: `python -m tools.governance.validate_readme_control --package-root .`
- docs completeness: `python -m tools.governance.validate_document_completeness --package-root .`
- docs classification: `python -m tools.governance.validate_document_classification --package-root .`
- docs impact: `python -m tools.governance.validate_document_impact --package-root .`
- master audit: `python -m tools.audit.run_master_audit --package-root .`
