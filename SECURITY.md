# Security Policy

## Security status

uDAQ is an early-stage universal data acquisition and hardware-control framework. It is not yet hardened for unreviewed public internet exposure.

Do not deploy this software in a public, shared, or safety-critical environment without reviewing authentication, authorization, secret storage, runtime configuration, logging, firewall exposure, and safe-state behavior.

## Supported versions

Only the latest public default branch is currently supported for security review.

| Version or branch | Supported |
| --- | --- |
| Latest default branch | Yes |
| Older dated package drops | No |

## Reporting a vulnerability

Do not open a public GitHub issue containing exploit details, private paths, credentials, tokens, screenshots with secrets, or private network information.

Preferred path:

1. Use GitHub private vulnerability reporting from the repository Security page, when available.
2. Include the affected repository, commit or release folder, reproduction steps, expected impact, and whether the issue may expose credentials, files, user data, admin functions, node identities, hardware outputs, local machine paths, or network routes.
3. If private vulnerability reporting is not available, open a public issue titled `Security contact request` without technical exploit details or private information.

## Project-specific security concerns

Please report issues involving:

- Unsafe output behavior, uncontrolled actuation, or failure to enter a defined safe state.
- Logic-rule failures that could drive outputs unexpectedly.
- Corrupted, misleading, reordered, or silently dropped sensor records.
- Historian, CSV, SQLite, or export bugs that compromise traceability.
- Authentication, authorization, or remote-control defects in any future networked mode.
- Leaked device credentials, API tokens, serial numbers, private keys, or local configuration.
- Device-adapter behavior that fails open instead of degrading safely when hardware disconnects.
- Diagnostics that hide faults, overwrite logs, or make field troubleshooting unreliable.

## Email privacy

This policy intentionally does not publish a personal maintainer email address. Use GitHub's private vulnerability reporting workflow when available, or open a non-sensitive `Security contact request` issue.

## Safety and data integrity

Treat unsafe hardware output behavior, misleading logged data, and loss of timestamp truthfulness as security-relevant issues, not merely ordinary bugs.

## Disclosure

Please give the maintainer reasonable time to investigate and correct the issue before public disclosure.
