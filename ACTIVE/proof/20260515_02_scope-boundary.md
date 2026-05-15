# Sprint 1 scope boundary

Package ID: `UDQ-PKG-20260515-02-MAPPING-R02`

## In scope

- Sandbox-only mapping state mutation.
- Before/after diff.
- Rollback token and state restoration.
- GUI Testing menu wiring.
- No-hardware diagnostic bundle.

## Out of scope

- Live mapping apply.
- Physical output writes.
- Adapter mutation.
- Production historian.
- Modbus.
- Runtime logic deployment.

## Safety statement

Sprint 1 does not grant live hardware authority. The sandbox controller mutates only `MappingSandboxStateStore`.
