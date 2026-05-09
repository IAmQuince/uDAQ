# Sprint 3C — Startup/Open Diagnostic Correction

## Scope
- Separate startup/open failure from mid-run reconnect failure.
- Harden real-U6 startup/open against serial-matching and enumeration timing issues.
- Gate unplug/replug validation behind a healthy baseline startup smoke.
- Enforce the `yyyymmdd_00_description-of-run` artifact naming convention for new generated run assets.

## Planned validation order
1. Startup/open smoke reaches `live / ready / healthy`.
2. Guided unplug/replug validation runs only after the startup gate passes.
3. Package integrity checks pass: package-entry, document completeness, Windows path budget, truncation guard, and artifact naming validation.
