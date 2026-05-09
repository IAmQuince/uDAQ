# Contributing

uDAQ is a device-agnostic data acquisition and hardware-control framework. Contributions should preserve universality, data integrity, graceful degradation, safe-state behavior, and clear diagnostics.

## Before opening an issue or pull request

- Do not post secrets, private lab configuration, device credentials, real historian files, private keys, or logs containing private network details.
- Do not post exploit details publicly. Use the security process in `SECURITY.md`.
- State the operating system, Python version, device/adapter, driver/library version, and whether hardware was connected.

## Development principles

- Keep the core device-agnostic. Do not bake one vendor or board into the central architecture.
- Preserve existing public APIs unless a breaking change is explicitly approved and documented.
- Preserve existing features unless removal is explicitly requested.
- Prefer adapter-based hardware support with graceful fallback when optional libraries are missing.
- Treat data ordering, timestamps, historian writes, and exports as integrity-critical.
- Treat outputs, actuation, shutdown, and disconnect handling as safety-critical.
- Include diagnostics that help reproduce field failures without requiring private lab information.

## Pull request checklist

Before requesting review, confirm:

- Imports and startup smoke tests pass.
- The app or package still runs without optional hardware libraries installed.
- Hardware-output changes define safe-state behavior.
- Historian/export changes preserve timestamp truthfulness and data ordering.
- No generated DBs, logs, local profiles, secrets, or private paths were committed.
- README or docs were updated for user-visible behavior changes.

## Testing

Run the available smoke tests and any relevant adapter diagnostics. If hardware is not available, document that limitation and include simulated-mode results when possible.
