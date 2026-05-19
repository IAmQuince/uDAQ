# UDQ Run 9 Plan — Action Claims and Identity Hardening

## Package
`20260323_09_action_claims_identity`

## Goal
Eliminate duplicate governed actions across rule/sequence emitters while hardening command/event identity and preserving a clean bounded real-U6 proof.

## Scope
- governed action claim/dedup semantics
- unique command ids for alarm acknowledgments
- unique event ids for alarm acknowledgments
- correlation ids for business-action linkage
- explicit suppression outcomes in rule/sequence review rows
- preserve one completed sequence and one failed sequence

## Acceptance criteria
- one canonical claimant for the degraded-alarm acknowledgment
- competing orchestration path is explicitly suppressed
- one admitted ack command in rule/sequence smoke
- no duplicate command_id values for the same ack action
- no duplicate event_id values for the same ack action
- real-U6 runtime remains bounded and healthy

## Out of scope
- broad output/control proof
- multi-device orchestration
- remote supervision
- notifications/routing
- rich orchestration UI/editor work
