---
document_id: UDQ-SEC-BASELINE-001
title: Security and Trust Boundary Baseline
revision: r0
status: WIP
document_class: security_baseline
owner: UniversalDAQ
depends_on:
  - "UDQ-SEC-SPEC-001"
  - "UDQ-GOV-STD-001"
revision_history:
  - "r0 | 2026-03-23 | Registered and normalized for the documentation closeout governance pass."
---
# UDQ-SEC-BASELINE-001 — Security and Trust Boundary Baseline

## Purpose
Capture the minimum security posture that must exist before adapters, remote control, or credential-bearing integrations are implemented.

## Primary trust boundaries
- operator workstation / local UI
- domain runtime truth and command arbitration
- future device adapters
- future remote clients and observation surfaces
- proof, export, and audit artifacts

## Baseline rules
- UI enablement is not authorization
- command acceptance must remain backend-authoritative even if a control is visible or hidden in the UI
- secrets and credentials must not be embedded in source-controlled sample files
- future remote surfaces must be treated as untrusted requesters until authenticated and authorized
- outputs must fail safe; restore/profile loading must not silently reassert physical machine state
- audit and proof artifacts should preserve integrity and avoid leaking secrets or sensitive endpoints

## Must-resolve before adapter or remote implementation
- credential loading/storage approach
- device-adapter privilege boundaries
- remote authentication and authorization model
- evidence tamper expectations
- redaction policy for logs and exported proof bundles
