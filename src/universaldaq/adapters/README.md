# Active package baseline

This package now holds the bounded adapter-preparation slice.

Current in-scope contents:
- typed adapter capability, health, and point-snapshot models
- command handoff request/result contracts
- adapter manager lifecycle seam
- simulated reference adapters for proof and tests
- diagnostics-friendly inventory structures

Still out of scope in this slice:
- real Modbus/TCP or RTU implementation
- LabJack or PLC-specific drivers
- remote adapter orchestration
- uncontrolled physical I/O expansion
