
# UDQ LabJack Core Boundary Verification

## Boundary claim
LabJack remains an optional support-pack edge integration. It is not baked into the universal core.

## Structural evidence
- LabJack implementation code lives under `src/universaldaq_labjack/`.
- The universal core lives under `src/universaldaq/`.
- Optional support-pack loading is handled generically in `src/universaldaq/adapters/support_pack_loader.py` through dynamic discovery/import rather than direct hard-coded LabJack imports.
- A direct search of `src/universaldaq/**/*.py` found no `import universaldaq_labjack` or `from universaldaq_labjack` statements.
- The only LabJack mention inside the core source tree outside the support-pack boundary is a README note under `src/universaldaq/adapters/README.md` describing driver classes that belong at the edge.

## Behavioral evidence
- `tests/invariants/test_invariant_no_direct_labjack_imports_in_core.py` verifies that the universal core contains no direct LabJack imports.
- `tests/invariants/test_invariant_no_direct_optional_support_pack_imports_in_core.py` verifies that the universal core contains no direct optional support-pack imports at all.
- `tests/invariants/test_invariant_missing_support_pack_dependency_does_not_break_core_startup.py` verifies that a broken optional support pack degrades to load reports without breaking core startup and that generic discovery remains available.
- `tests/contract/test_contract_optional_support_pack_loader.py` verifies that optional support packs load lazily while generic discovery remains intact.
- `python -m tools.dev.run_shell_smoke --package-root .` remains green on the current package line.

## Terminology audit result
- The package now treats the real-U6 line as a bounded specimen rather than the default identity of the platform.
- The current package summaries state explicitly that U6 success does not imply broad device parity or generalized hot-plug semantics.
- Remaining LabJack-specific wording is confined to support-pack proof, support-pack tooling, and bounded specimen descriptions.

## Conclusion
The LabJack support pack remains outside the universal core in structure, behavior, and package narrative. The current package proves a bounded real-U6 specimen while preserving a vendor-neutral core architecture.
