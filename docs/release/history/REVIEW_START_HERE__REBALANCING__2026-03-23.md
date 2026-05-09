# Historical Review Entry

**HISTORICAL ENTRY DOCUMENT — SUPERSEDED — DO NOT USE AS PRIMARY REVIEW PATH**

- Historical package ID: `UDQ-PKG-20260323-REBALANCING-R01`
- Entry status: `historical`
- Package status: `superseded`
- Superseded by: `UDQ-PKG-20260325-DOC-ALIGNMENT-REVIEW-READY-R01`
- Canonical replacement: `docs/release/REVIEW_START_HERE__UDQ-PKG-20260325-DOC-ALIGNMENT-REVIEW-READY-R01__ACTIVE.md`

# Review Start Here — Rebalancing Sprint

**Controlled document**  
ID: UDQ-REL-REVIEW-REBALANCE-001  
Status: ACTIVE  
Revision: r0  
Owner: Core Architecture  
Authority: DERIVED  
Source docs: UDQ-REL-SUM-REBALANCE-001, UDQ-README-ROOT-001  

## Start with these proofs
1. `python -m tools.dev.run_labjack_u6_smoke --package-root .`
2. `python -m tools.dev.run_labjack_u6_smoke --package-root . --real-hardware` when a U6 is attached
3. `pytest -q`
4. `python -m tools.dev.run_local_gate --package-root .`

## Then inspect these modules
- `src/universaldaq_labjack/real_u6.py`
- `src/universaldaq_labjack/discovery.py`
- `src/universaldaq/app/device_lifecycle_handler.py`
- `src/universaldaq/app/binding_variable_handler.py`
- `src/universaldaq/signals/variables.py`
- `tools/_registry_paths.py`
- `tools/_shared.py`

## Reviewer expectations
This package now proves a narrow real-device path, but it is still intentionally bounded. Review it as a disciplined early implementation slice, not as a full runtime or UI delivery.
