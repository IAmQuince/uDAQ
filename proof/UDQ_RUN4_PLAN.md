# UDQ Run 4 Plan — Command Admission Spine

Run name
--------
`20260323_06_command_admission_spine`

Purpose
-------
Create the one official bounded path by which command intent enters the platform.

Predicates carried forward
--------------------------
- Runtime spine remains bounded and measurable.
- Bounded live-value slice remains green on the U6 path.
- Events/alarms remain transition-based and journal-backed.
- Optional support-pack isolation remains intact.

Run scope
---------
1. Add a canonical command-intent model.
2. Add a bounded command-admission record/service layer.
3. Route alarm acknowledgment through the command-admission path.
4. Add one bounded dry-run adapter-point command path.
5. Journal admitted and rejected commands through the canonical runtime journal.
6. Expose thin review-bundle command summary surfaces.
7. Prove one bounded U6 command scenario.

Bounded proof scenario
----------------------
- Prepare the bounded U6 live-value slice.
- Force the degraded-state alarm to raise via disconnect.
- Acknowledge the alarm through the command-admission path.
- Reconnect the device path to clear the alarm.
- Submit one dry-run adapter-point command to a non-writable U6 point.
- Observe a clear `unsupported_capability` rejection.

Explicitly out of scope
-----------------------
- Broad real-hardware write support
- Multi-actor arbitration/ownership
- Rules/sequence dispatch
- Rich UI/console work
- Remote-client coordination
