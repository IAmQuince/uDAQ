# Security package

This package is now an **active bounded implementation slice** for authorization / authority enforcement.

Implemented in this sprint:
- typed actor, role, permission, action, and authorization-decision models
- a default bounded policy for the currently governed shell actions
- backend authorization evaluation for command, alarm-acknowledgment, and export requests
- attributable denial outcomes that remain distinct from downstream arbitration/runtime failures

Still intentionally out of scope:
- credentials, passwords, or tokens
- remote authentication and trust handshakes
- cryptographic signing
- device-side credential delegation
- physical actuation expansion
