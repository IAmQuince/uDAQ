# Tests and Tools

**Controlled document**  
ID: UDQ-HANDBOOK-TESTS-001  
Status: ACTIVE  
Revision: r15  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-GOV-REG-003, UDQ-GOV-LOG-001

## Package identity
- Package ID: `UDQ-PKG-20260330-CONTROLLED-MAPPING-APPLY-PREFLIGHT-AND-REVIEW-PATH-R01`

## Current focused tools
- `python -m tools.governance.validate_package_entry_surfaces --package-root .`
- `python -m tools.governance.validate_readme_control --package-root .`
- `python -m tools.governance.validate_document_completeness --package-root .`
- `python -m tools.governance.validate_document_classification --package-root .`
- `python -m tools.governance.validate_document_impact --package-root .`
- `python -m tools.audit.run_master_audit --package-root .`
