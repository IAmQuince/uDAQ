# 20260323_10 cleanup hardening

## Goals
- Harden universality at the code boundary.
- Add explicit invariants that catch vendor leakage early.
- Clean small reviewer-facing rough edges without expanding feature scope.
- Preserve the bounded real-U6 proof chain unchanged in behavior.

## Included cleanup work
1. Generic support-pack discovery
   - no static vendor module list in core loader
   - entry-point and namespace-based discovery only
2. Core/bootstrap boundary hardening
   - no vendor-specific quick start in universal lifecycle code
3. Universality tests
   - forbidden vendor markers in `src/universaldaq/*.py`
   - zero-support-pack core boot path
   - missing-dependency resilience path
   - generic support-pack discovery contract
4. Reviewer-surface cleanup
   - cleaner rule suppression rows in same-cycle claim contention
5. Packaging cleanup
   - remove transient proof outputs and `__pycache__`

## Explicitly out of scope
- new device capabilities
- real hardware output/control expansion
- new automation features
- UI/editor work
- documentation closeout beyond this run's proof notes
