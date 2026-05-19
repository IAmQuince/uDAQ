# Cost Center Summary — Performance Baseline and Usability Gate

- package_id: `UDQ-PKG-20260327-PERFORMANCE-BASELINE-AND-USABILITY-GATE-R01`

## Top cost centers by byte count
- `proof` — `5839560` bytes across `395` files
- `registries` — `1832971` bytes across `100` files
- `src` — `1481952` bytes across `233` files
- `docs` — `1068509` bytes across `214` files
- `audit_reports` — `1011368` bytes across `134` files

## Top cost centers by file count
- `proof` — `395` files totaling `5839560` bytes
- `src` — `233` files totaling `1481952` bytes
- `tests` — `231` files totaling `534192` bytes
- `docs` — `214` files totaling `1068509` bytes
- `audit_reports` — `134` files totaling `1011368` bytes

## Measured timing highlights
- focused pytest gate: `34.54` s external
- package build: `5.96` s external
- shell smoke: `5.08` s external
- runtime inventory: `5.09` s external
- package-entry validator: `4.55` s external

## Interpretation
The dominant weight remains in `proof/`, followed by `registries/`, `src/`, and `docs/`. The dominant measured elapsed path in this sprint is the focused pytest gate rather than the runtime baseline path. That points to continued package/history weight and validation cost as the main efficiency concerns, not a catastrophic first-signal runtime blocker.
