# Implementation Summary — 20260328_04_shell-ergonomics-and-mapping-clarity-hardening

## Intent
This sprint hardens the visible operator shell around the first real usability feedback: panel ergonomics, saved views, raw-device versus internal-signal clarity, and an explicit Mapping Editor surface.

## Implemented scope
- extended the View menu with save/manage view actions, panel reset, and explicit panel visibility controls for Device Explorer, Signal Explorer, Trace Inspector, and Notes
- added pure helper models in `src/universaldaq/ui/shell_views.py` for named shell views, mapping rows, mapping summaries, and structured event-console rows
- refreshed `src/universaldaq/ui/visible_shell.py` so the shell specification now claims saved views, mapping-editor separation, and panel visibility control explicitly
- hardened `src/universaldaq/ui/qt_shell.py` to:
  - give the explorer, control column, and events console stronger dock behavior and default sizing
  - expose built-in quick views and shell-view persistence hooks
  - distinguish raw hardware rows from internal signal rows in the explorers
  - surface a Mapping Editor in the System workspace with editable binding fields and explicit mapped/unmapped status
  - provide a structured Events / Diagnostics console with filter and search controls
  - improve trace-style discoverability with guidance text and reset-style affordance
- updated stale package-entry/meta tests so they resolve the current canonical review entry from the active package registry rather than hard-coding an old package filename
- removed the duplicate release wrapper directory (`udq_work/`) from the working package root before packaging

## Important implementation notes
- the Mapping Editor remains deliberately narrow: binding rows, direction, scale/offset/invert, enable/disable, and notes. It does not attempt to become a transform or logic authoring engine.
- built-in quick views are provided as shell-state presets. Custom saved views are persisted through shell-owned JSON state in settings.
- the structured Events / Diagnostics console is derived from the runtime event log and remains bounded and searchable.
- the shell still guards against optional GUI dependencies being absent in this environment.

## Files materially changed
- `src/universaldaq/ui/qt_shell.py`
- `src/universaldaq/ui/visible_shell.py`
- `src/universaldaq/ui/shell_views.py`
- `src/universaldaq/ui/__init__.py`
- `tests/contract/test_contract_visible_shell_spec.py`
- `tests/contract/test_contract_shell_views_and_mapping_helpers.py`
- `tests/meta/test_meta_package_entry_surfaces.py`
- `tests/meta/test_meta_pass2_reviewer_guide_present.py`

## Controlled-document follow-through
This sprint also appends explicit implementation addenda to the active UI shell, workspace, UI-state, signal, and persistence specs so the package claim is not ahead of the governed document lane.
