# Cross-Device Tag and Acquisition Spine Sprint — Scope Boundary

## In scope
- canonical tag model
- bounded multi-adapter read-side acquisition broker
- mixed-source ingest proof using the existing evidence/review lane
- read-only mixed-source variable proof
- acceptance and review artifacts for mixed-source sessions
- architectural tests preventing support-pack leakage into the universal core

## Out of scope
- cross-device outputs
- command arbitration
- write ownership and acknowledgements
- stale-command protection
- broad workbench authoring surfaces
- broad hardware generalization claims

## No-touch zones
- historian/recovery core semantics already closed by repeatable proof
- existing one-command acceptance entry
- existing bounded simulated and real-hardware bridge surfaces
