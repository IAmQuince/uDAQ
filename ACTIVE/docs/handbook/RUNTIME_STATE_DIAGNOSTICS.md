# Runtime state diagnostics

## Purpose

`tools.diagnostics.dump_runtime_state_snapshot` emits a runtime-state diagnostic JSON artifact that is safe in headless, no-hardware environments.

This tool is diagnostic-only:
- does not write to hardware,
- does not apply live mappings,
- does not treat sandbox mapping state as authoritative runtime truth.

## Commands

From `ACTIVE/`:

- Print JSON to stdout:
  - `python3 -m tools.diagnostics.dump_runtime_state_snapshot --package-root . --pretty`
- Print JSON and write to file:
  - `python3 -m tools.diagnostics.dump_runtime_state_snapshot --package-root . --pretty --output audit_reports/testing/runtime_state_snapshot.json`
- Enforce runtime API presence:
  - `python3 -m tools.diagnostics.dump_runtime_state_snapshot --package-root . --strict`
- Include git metadata:
  - `python3 -m tools.diagnostics.dump_runtime_state_snapshot --package-root . --include-git`

## Copy/paste review workflow

1. Run with `--pretty`.
2. Copy stdout JSON directly into review chat.
3. Include any generated output path if `--output` was used.

The JSON structure is deterministic by key and always contains required safety flags:
- `hardware_mutation_enabled: false`
- `live_mapping_apply_enabled: false`
- `sandbox_is_authoritative: false`

## Pending-authoritative API behavior

Before GPT-5.5 runtime-state integration is merged, the tool emits an explicit placeholder artifact with:
- `runtime_state_api_available: false`
- warning text stating authoritative API integration is pending.

`--strict` converts that missing API condition into a non-zero exit code.

## Wiring after GPT-5.5 merge

When the authoritative runtime snapshot API is available, expose a callable provider that returns a mapping payload with runtime counts/posture fields and one of these references:
- `universaldaq.runtime.state_snapshot:get_authoritative_runtime_state_snapshot`
- `universaldaq.runtime.state_snapshot:build_authoritative_runtime_state_snapshot`
- `universaldaq.runtime.state_snapshot:get_runtime_state_snapshot`

Or pass the provider explicitly:
- `python3 -m tools.diagnostics.dump_runtime_state_snapshot --package-root . --provider your.module:get_snapshot`

No local runtime-model synthesis should be added here; this helper should only consume the leader-defined runtime-state snapshot API.
