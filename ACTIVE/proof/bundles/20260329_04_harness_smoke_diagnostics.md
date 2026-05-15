# UniversalDAQ Desktop Bench Runbook

- Package root: `/mnt/data/udq_run04`
- Diagnostics output: `/mnt/data/udq_run04/proof/bundles/20260329_04_harness_smoke_diagnostics.json`
- Launch command: `python -m tools.ui.run_desktop_bench_harness --package-root "/mnt/data/udq_run04" --diagnostics-path "/mnt/data/udq_run04/proof/bundles/20260329_04_harness_smoke_diagnostics.json"`

## Checklist
1. Launch the shell and confirm it fits entirely within the usable screen.
2. Resize the left explorer, center region, right control column, and bottom events region.
3. Switch to Logic Designer and confirm the graph enters Compact PiP mode.
4. Drag and resize the PiP graph; then switch back to Operate and confirm Primary graph mode returns.
5. Use Restore Default Layout, Reset Panel Sizes, and Reset Layout Cache; confirm each behaves distinctly.
6. Inspect the System workspace and confirm Mapping Drafts remain explicitly non-authoritative.
7. Close the shell normally so the desktop bench diagnostics artifact is written automatically.

## Notes
- This harness is intended for a real desktop with the optional UI dependencies installed.
- The diagnostics file is written on normal shell exit and can be pasted back for troubleshooting.
- This bench run does not make the shell authoritative for backend-applied mappings; it verifies shell behavior and surfaces authority boundaries.
