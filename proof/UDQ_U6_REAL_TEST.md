# Real U6 Test — Run 9

From the extracted package root with the real U6 connected, run:

```bat
 tools\dev\run_u6_diag.bat
 tools\dev\run_u6_live_smoke.bat --cycles 16 --reconnect-test
 tools\dev\run_u6_command_smoke.bat
 tools\dev\run_u6_rule_sequence_smoke.bat
```

Send back:
- `proof\U6_DIAG.txt`
- `proof\U6_LIVE_SUMMARY.txt`
- `proof\U6_COMMAND_SUMMARY.txt`
- `proof\U6_RULE_SEQUENCE_SUMMARY.txt`

What to look for in the rule/sequence summary:
- one admitted `ack_alarm` command
- one suppression outcome on the competing path
- one completed sequence
- one failed sequence
- unique `command_id` values
- unique `event_id` values
- visible shared `correlation_id` on related rows
Use `UDQ_PROOF_GUIDE.md` as the primary verification document for how these proof steps are interpreted in the broader package.
