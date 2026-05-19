# Baseline selection ledger

Current package ID: `UDQ-PKG-20260515-HANDOFF-BASELINE-REFURBISHMENT-R01`

## Decision

Use `20260330_10_controller-authorized-mapping-apply-dry-run-commit-boundary` as the source baseline for the current handoff package.

## Rationale

- `_10` supersedes the `_09` controlled mapping apply preflight/review path.
- `_10` contains the controller-authorized dry-run commit boundary.
- `_10` has a cleaner active/historical release posture than `_06`.
- The May uploaded package uses a stale `_09` internal identity and is therefore not appropriate as the active baseline.

## Baseline source

- Source package: `UDQ-PKG-20260330-CONTROLLER-AUTHORIZED-MAPPING-APPLY-DRY-RUN-COMMIT-BOUNDARY-R01`
- New package: `UDQ-PKG-20260515-HANDOFF-BASELINE-REFURBISHMENT-R01`

## Package archives retained

Original uploaded packages are retained under `HISTORICAL/package_archives/`.
