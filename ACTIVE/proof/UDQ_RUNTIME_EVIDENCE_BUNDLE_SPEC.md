# UniversalDAQ — Canonical Runtime Evidence Bundle v1

## Required top-level sections
- identity
- runtime state
- reviewer rollup
- summaries
- recent runtime events
- recent alarm events
- recent operator actions
- recent automation claims
- diagnostic snapshots
- metric layers
- provenance

## Design note
The canonical bundle is additive. Existing lifecycle review bundle sections remain present for compatibility, while the new `canonical_runtime_evidence_bundle_v1` gives one semantically organized path through the same truth.
