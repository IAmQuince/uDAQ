---
document_id: DOC-000-KNOWN-LIMITATIONS
title: "Known Limitations"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-000-KNOWN-LIMITATIONS
normative_status: Normative
source: "Generalized AI-assisted coding SOP source text"
---

# Known Limitations

LIMIT-001
Title: First-pass reference package
Description: This package is a structured reference seed, not a finished production application.
Impact: The package demonstrates expected structure and documentation patterns but does not ship an executable product beyond audit/smoke-test tools.
Status: Current

LIMIT-002
Title: Informative technical guides
Description: Most long technical guides in `docs/` are informative reference material. The authoritative package requirements are centralized in `docs/005_PRODUCT_REQUIREMENTS.md`.
Impact: Future projects should create their own project-specific requirements rather than treating every sentence in the reference guides as normative.
Status: Current

LIMIT-003
Title: Manual editorial review still recommended
Description: The source text was cleaned and generalized, but a human editorial pass is still recommended before public distribution.
Impact: Tone and wording may still need refinement for a specific audience.
Status: Current

LIMIT-004
Title: No external dependency validation
Description: The package does not download or validate the current status of all third-party tools described in the guides.
Impact: Users should verify installer sources and package versions when applying the instructions.
Status: Current
