---
document_id: DOC-180
title: "Hardware DAQ, Control, and Interface Doctrine"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-180
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Hardware DAQ, Control, and Interface Doctrine

## 0. Purpose

This document formalizes the engineering lessons learned from the Genesys+ power-supply control project, LabJack-based data acquisition work, and the broader universal DAQ/control direction.

It defines how we design software that:

- reads many analog/digital inputs;
- maps physical channels to meaningful engineering signals;
- graphs large amounts of time-series data;
- controls outputs safely;
- communicates with power supplies and instruments;
- preserves data under faults;
- handles disconnects and degraded operation;
- provides useful diagnostics;
- remains maintainable enough to become a professional package.

This document applies to projects involving:

- LabJack U3/U6/T-series devices;
- MUX80 or other channel expansion;
- Genesys+ programmable power supplies;
- PyVISA / SCPI instruments;
- Raspberry Pi DAQ systems;
- Arduino / ESP32 sensor networks;
- local historians;
- CSV/SQLite logging;
- engineering GUIs;
- hardware-control GUIs;
- universal DAQ/control architecture;
- test stations;
- electrolyzer stack and BoP test tools.

The central rule is:

Data must be preserved.
Hardware must fail safe.
The operator must know what the system is doing.
The software must never hide uncertainty.

---

## 1. Core Doctrine

Hardware DAQ/control software is not ordinary desktop software.

It has four simultaneous responsibilities:

1. **Acquire truthfully**
   - Read signals correctly.
   - Timestamp honestly.
   - Preserve raw data.
   - Distinguish missing data from zero data.
   - Distinguish measured values from commanded setpoints.

2. **Control safely**
   - Start safe.
   - Fail safe.
   - Shut down deterministically.
   - Never auto-enable dangerous outputs without explicit operator action.
   - Make manual safe-state override obvious and always reachable.

3. **Explain itself**
   - Log what happened.
   - Show device health.
   - Show command state.
   - Show telemetry age.
   - Produce diagnostics that can be copied back for troubleshooting.

4. **Remain maintainable**
   - Keep device adapters separate from UI.
   - Keep raw data separate from plotted/decimated data.
   - Keep settings separate from runtime state.
   - Keep acquisition separate from command/control logic.
   - Use clear module boundaries and staged refactors.

A system that reads data but cannot explain whether the data is valid is incomplete.

A system that controls outputs but cannot prove its shutdown behavior is unsafe.

A system that graphs beautifully but corrupts or drops raw data is not acceptable.

---

## 2. Safety Principles

### 2.1 Start Safe

On startup, the software shall not assume the hardware is in a known or safe state.

Startup behavior should be:

```text
1. Initialize logging.
2. Load configuration.
3. Load persisted UI/settings state.
4. Start diagnostics.
5. Detect devices.
6. Mark devices as unknown / disconnected / detected / verified.
7. Do not enable outputs automatically.
8. Do not resume a prior command automatically unless explicitly designed and confirmed.
9. Present operator with current state.
10. Require explicit operator action before energizing controlled outputs.

For power supplies, pumps, relays, heaters, valves, motors, and load banks:
Default startup output state: OFF / disabled / safe / idle.

Any exception must be explicitly documented and justified.

2.2 Fail Safe
If the program crashes, loses communication, receives malformed telemetry, loses the GUI, or encounters an unhandled exception, it should attempt to enter a safe state.
Safe-state behavior must be project-specific, but typical actions include:
* turn PSU output off;
* stop active sequence;
* stop ramp;
* disable output relays;
* stop motor command;
* close or park valves where appropriate;
* stop sending new setpoints;
* preserve last known telemetry;
* flush data buffers;
* write fault log;
* write diagnostic report;
* mark shutdown as abnormal.
The safe-state handler should be centralized.
Example concept:
safe_state_now(reason, severity, source)

Required fields:
reason:
severity:
source:
timestamp:
attempted_actions:
successful_actions:
failed_actions:
device_state_before:
device_state_after:
diagnostic_report_path:

2.3 Manual Safe-State Control Must Be Persistent
Any engineering-control GUI should have a visible manual safe-state control.
For the Genesys+/DAQ style interface:
SAFE STATE NOW

or:
OUTPUT OFF / SAFE STATE

should be visible from all major screens.
It should not be buried in a settings dialog.
It should not depend on the current tab.
It should interrupt active ramps/sequences.
It should write a clear log entry.
It should update the command state immediately.

2.4 Commanded State and Measured State Are Different
The software must always distinguish:
commanded_voltage
measured_voltage
commanded_current
measured_current
output_enable_command
output_enable_readback
sequence_target
sequence_active_step
actual_device_state

Do not graph setpoint and measurement as if they are the same signal.
Do not use measured telemetry to imply a command succeeded unless the device readback confirms it.
Do not hide disagreement between command and measurement.
A disagreement should be visible, logged, and diagnosable.

2.5 No Ambiguous Output State
The UI should never leave the operator wondering:
* Is the PSU output on?
* Is the ramp still active?
* Is the sequence paused, stopped, failed, or complete?
* Is the last value a real measurement or stale telemetry?
* Is the device connected or disconnected?
* Is the graph live or paused?
* Is the system in manual mode, sequence mode, or safe mode?
Every controlled output should have an explicit state.
Suggested command states:
UNKNOWN
DISCONNECTED
IDLE_SAFE
CONNECTED_OUTPUT_OFF
MANUAL_READY
MANUAL_ACTIVE
SEQUENCE_ARMED
SEQUENCE_RUNNING
SEQUENCE_PAUSED
SEQUENCE_COMPLETE
FAULTED
SAFE_STATE_REQUESTED
SAFE_STATE_CONFIRMED
SHUTTING_DOWN

3. Data Preservation Doctrine
3.1 Raw Data Is Sacred
Raw acquired data must be preserved as faithfully as practical.
Rules:
* Do not overwrite raw data with filtered data.
* Do not overwrite raw data with decimated data.
* Do not silently drop rows.
* Do not silently change units.
* Do not silently rename channels.
* Do not silently rewrite timestamps.
* Do not mix command data and measurement data without clear labels.
* Do not treat missing data as zero.
* Do not treat stale data as current.
Display transformations are allowed, but they must be downstream of raw storage.

3.2 Separate Raw, Derived, and Display Data
Use three conceptual layers:
raw_data
    Direct acquisition records.

derived_data
    Calculated values, calibrated values, filtered values, efficiency, power, resistance, etc.

display_data
    Decimated, windowed, downsampled, or rescaled data used only for plotting/UI.

The plot may decimate.
The historian should not.
The export should clearly state whether it contains raw or processed values.

3.3 Sliding Window and Full History Must Be Different Modes
For live plotting:
Sliding window:
- recent time range;
- full fidelity if practical;
- optimized for live operation;
- should not be contaminated by full-history decimation.

Full history:
- may be decimated for performance;
- must be labeled as decimated if so;
- should allow raw export separately;
- should avoid freezing the UI.

Known failure to avoid:
Full-history decimation affecting sliding-window fidelity.

Acceptance check:
1. Run or replay a long dataset.
2. View sliding window.
3. Confirm recent points are full fidelity or explicitly configured.
4. Switch to full history.
5. Confirm full-history decimation is labeled.
6. Switch back to sliding window.
7. Confirm sliding-window behavior is restored.

3.4 Timestamps Must Be Honest
Each record should distinguish timestamps when relevant:
measurement_timestamp
receive_timestamp
write_timestamp
display_timestamp
device_timestamp
sequence_timestamp

For distributed systems:
* Arduino/ESP32 should timestamp or sequence data where practical.
* Raspberry Pi should not pretend receive time equals measurement time if delays occur.
* Logs should allow reconstruction of stalls, bursts, and reconnects.
Minimum DAQ row fields:
record_id
run_id
timestamp
timestamp_source
device_id
channel_id
signal_name
value
units
quality
raw_value
calibrated_value
sequence_id
command_state
fault_state

3.5 Missing, Faulty, and Stale Data Must Be Labeled
Quality flags should be explicit.
Recommended quality values:
GOOD
MISSING
STALE
DEVICE_DISCONNECTED
PARSE_ERROR
OUT_OF_RANGE
CALIBRATION_MISSING
SATURATED
USER_DISABLED
SIMULATED
UNKNOWN

Graphing behavior:
* Missing data should create gaps, not fake zeros.
* Fault periods should be visually marked.
* Stale telemetry should be shown differently or excluded.
* Simulated data must be clearly identified.

3.6 Fault Periods Should Be Logged as Events
Do not spam logs with every repeated threshold breach.
Use event-style logging:
FAULT_START
FAULT_UPDATE
FAULT_END

Example:
FAULT_START
timestamp:
signal:
threshold:
value:
state:

FAULT_END
timestamp:
signal:
duration:
min_value:
max_value:
sample_count:

This preserves useful evidence without flooding logs.

4. Historian and File Structure
4.1 Preferred Runtime Data Structure
For DAQ/control projects:
runtime_data/
├── config/
│   ├── settings.json
│   ├── channel_map.json
│   ├── device_map.json
│   ├── calibration.json
│   └── ui_state.json
│
├── runs/
│   └── RUN_ID/
│       ├── run_manifest.json
│       ├── raw_data.csv
│       ├── events.csv
│       ├── commands.csv
│       ├── faults.csv
│       ├── derived_data.csv
│       ├── notes.md
│       └── snapshots/
│
├── historian/
│   └── project_historian.sqlite
│
├── logs/
│   ├── app.log
│   ├── device.log
│   ├── command.log
│   └── fault.log
│
├── diagnostics/
│   ├── diagnostic_report.txt
│   ├── package_smoke_test_report.txt
│   └── device_diagnostics_report.txt
│
├── autosave/
│   ├── last_session.json
│   └── recovery_state.json
│
└── exports/
    ├── csv/
    ├── png/
    └── reports/

Runtime data should usually not be bundled in release packages unless explicitly included for debugging.

4.2 Run Manifest
Every test run should have a manifest.
{
  "run_id": "",
  "project": "",
  "app_version": "",
  "started_at": "",
  "ended_at": "",
  "operator": "",
  "purpose": "",
  "hardware_profile": "",
  "device_map_path": "",
  "channel_map_path": "",
  "calibration_path": "",
  "settings_path": "",
  "historian_path": "",
  "raw_data_path": "",
  "events_path": "",
  "commands_path": "",
  "faults_path": "",
  "notes": "",
  "shutdown_status": "",
  "abnormal_shutdown_detected": false
}

The manifest is the anchor for reconstructing what happened.

4.3 CSV and SQLite Roles
CSV is good for:
* simple inspection;
* raw append-only logging;
* transfer to other tools;
* recovery;
* low-dependency environments;
* debugging.
SQLite is good for:
* post-run exploration;
* large datasets;
* querying by time range;
* filtering by run/sequence/channel;
* cross-comparison;
* metadata-rich history;
* viewer applications.
Preferred approach:
During acquisition:
- write append-only CSV or buffered raw records;
- optionally mirror into SQLite if stable.

After or during safe intervals:
- ingest/sync into SQLite historian.

For viewing:
- use SQLite for efficient filtering and querying.
- preserve CSV/raw source as recovery layer.

For critical tests, do not rely on only one storage path.

4.4 Atomic-ish Writes and Backups
Settings, channel maps, calibration files, and manifests should use safer write patterns:
1. Write temp file.
2. Flush/close temp file.
3. Back up existing file.
4. Replace destination.
5. Verify file can be read.

Before schema migrations:
backup original
write migrated copy
verify migrated copy
only then mark migration successful

Never silently discard unknown fields.

4.5 Autosave and Recovery
DAQ/control GUIs should preserve enough state to recover after a crash.
Autosaved state may include:
last run id
active devices
active channel map
visible traces
window layout
current plot mode
last command state
sequence state
last telemetry timestamp
last successfully flushed row
abnormal shutdown flag

On restart after abnormal shutdown:
1. Detect abnormal shutdown.
2. Do not auto-resume hardware output.
3. Show recovery warning.
4. Offer to open last run/logs.
5. Confirm whether data files were flushed.
6. Generate diagnostic report.

5. LabJack Integration Doctrine
5.1 Device Identity Must Be Explicit
Do not assume that “the first LabJack found” is the correct device.
Device records should include:
device_id
device_type
serial_number
connection_type
nickname
role
firmware_version
last_seen
expected_channels
enabled

Example roles:
primary_daq
temperature_daq
voltage_monitor
pressure_monitor
control_io
spare

5.2 Channel Mapping Must Be Separate From Physical Acquisition
Raw hardware channel names are not enough.
Separate:
physical_channel
logical_signal
engineering_name
units
calibration
display_group
alarm_rules
plot_axis

Example channel map entry:
{
  "physical_channel": "AIN0",
  "logical_signal": "stack_voltage",
  "display_name": "Stack Voltage",
  "device_id": "labjack_u6_primary",
  "units": "V",
  "raw_units": "V",
  "scale": 1.0,
  "offset": 0.0,
  "calibration_id": "cal_stack_voltage_v1",
  "enabled": true,
  "plot_default": true,
  "axis_group": "voltage",
  "quality_rules": {
    "min_valid": -1.0,
    "max_valid": 100.0
  }
}

Rules:
* The acquisition layer reads physical channels.
* The mapping layer assigns meaning.
* The calibration layer converts raw readings.
* The UI shows engineering names.
* The historian stores enough information to reconstruct both raw and engineering values.

5.3 MUX/Expansion Channel Indexing Must Be Verified
Large input-count systems are vulnerable to off-by-one mapping errors.
For MUX80 or equivalent channel expansion:
Do not trust the channel map until verified with known physical stimuli.

Required verification table:
VERIFY-CH-001
Physical input:
Expected logical signal:
Injected/known stimulus:
Observed raw value:
Observed engineering value:
Correct? Yes/No
Verified by:
Date:
Notes:

Acceptance test:
1. Apply known signal to each physical input.
2. Confirm displayed channel name.
3. Confirm logged channel ID.
4. Confirm graph trace.
5. Confirm exported data field.
6. Confirm historian query.

A channel is not accepted until acquisition, display, and storage agree.

5.4 Acquisition Timing Must Be Observable
The system should report:
target_sample_interval
actual_sample_interval
last_sample_timestamp
loop_duration
read_duration
write_duration
plot_update_duration
dropped_sample_count
stale_channel_count
device_error_count

Do not just display values.
Display health of the acquisition loop.

5.5 Hardware Disconnect Handling
Disconnect must be treated as expected behavior.
When a LabJack disconnects:
1. Stop treating readings as current.
2. Mark affected signals stale/disconnected.
3. Log disconnect event.
4. Preserve previous data.
5. Keep UI responsive.
6. Attempt reconnect only according to configured policy.
7. Do not corrupt channel mapping.
8. Do not clear graph history unless explicitly commanded.

Reconnect should verify identity before restoring readings.
serial number matches expected?
channel map still valid?
calibration still valid?
device role unchanged?

6. Genesys+ / Programmable PSU Control Doctrine
6.1 PSU Control Is Safety-Critical
A programmable PSU can source dangerous energy.
Software must not treat PSU commands as ordinary UI events.
Required command principles:
* explicit connect;
* explicit output enable;
* explicit output disable;
* safe-state command always available;
* command log always written;
* readback verification where possible;
* no hidden auto-ramping;
* no ambiguous sequence state.

6.2 Command / Readback Pairing
Every PSU command should be paired with expected confirmation where practical.
Command record:
command_id
timestamp
operator_action
device_id
command_type
requested_voltage
requested_current
output_enable_requested
sequence_id
step_id
sent_to_device
send_success
readback_voltage
readback_current
readback_output_state
verification_status
error

Verification statuses:
NOT_SENT
SENT_NOT_VERIFIED
VERIFIED
READBACK_MISMATCH
DEVICE_ERROR
TIMEOUT
ABORTED_BY_SAFE_STATE

6.3 Ramp and Sequence Discipline
Ramps and sequences must have explicit ownership of setpoints.
The system should not allow manual setpoints and sequence setpoints to fight.
Modes:
MANUAL_CONTROL
SEQUENCE_CONTROL
RAMP_CONTROL
SAFE_STATE
FAULTED

Rules:
* Only one mode owns PSU setpoints at a time.
* Manual override should either abort or pause sequence according to documented policy.
* Safe-state overrides everything.
* Stop behavior must be explicit.
Stop behavior options:
STOP_HOLD_LAST_SETPOINT
STOP_OUTPUT_OFF
STOP_RAMP_TO_SAFE
STOP_REQUIRE_OPERATOR_DECISION

The selected policy must be visible and logged.

6.4 Sequence Preview and Execution Must Agree
A sequence preview is a contract with the operator.
Preview should show:
* time axis;
* voltage setpoint;
* current setpoint;
* holds;
* ramps;
* expected duration;
* active control variable;
* output enable/disable events;
* safe-state or stop behavior.
During execution:
* show progress marker;
* show current step;
* show elapsed and remaining time;
* show commanded vs measured traces;
* show whether the PSU accepted commands;
* show any mismatch between preview and actual execution.
Acceptance test:
1. Create ramp up / hold / ramp down sequence.
2. Preview sequence.
3. Execute sequence.
4. Confirm command log matches preview.
5. Confirm graph shows setpoint and measured values separately.
6. Confirm hold duration is correct.
7. Confirm stop/safe behavior matches configured policy.

6.5 Shutdown Must Be Deterministic
On normal app shutdown:
1. Stop active sequence/ramp.
2. Apply configured shutdown policy.
3. If hardware-control project, default should be output off unless explicitly configured otherwise.
4. Flush command queue.
5. Flush data buffers.
6. Write shutdown event.
7. Write final state.
8. Close device handles.
9. Confirm clean shutdown in state file.

On abnormal shutdown:
1. Attempt safe-state.
2. Flush what can be flushed.
3. Write abnormal shutdown marker.
4. Write traceback.
5. Write diagnostic report.

The next startup should detect abnormal shutdown.

7. UI / Operator Interface Doctrine
7.1 Main Layout
For engineering DAQ/control GUIs:
Main graph/work area dominates.
Controls are docked or panelized.
Diagnostics/logs are accessible.
Safe-state control is always visible.
Settings persist.
Layout is restorable.

Recommended default layout:
Top:
- menu bar
- status strip
- safe-state button
- connection/health summary

Center:
- large live graph / main workspace

Left or right dock:
- device explorer
- signal explorer
- trace controls
- sequence controls
- output controls

Bottom dock:
- logs
- event table
- diagnostics
- command history

Important panels should be dockable/reconfigurable where the toolkit allows.

7.2 Menus
Standard menus:
File
View
Settings
Tools
Help

Recommended items:
File:
- New run
- Open historian
- Open run folder
- Save current configuration
- Export visible data CSV
- Export graph PNG
- Exit safely

View:
- Reset layout
- Toggle device explorer
- Toggle signal explorer
- Toggle sequence panel
- Toggle diagnostics/logs
- Sliding window
- Full history
- Explore/pause mode

Settings:
- UI scale
- Theme
- Autosave
- Data path
- Sample interval
- Plot update interval
- Safe shutdown policy
- Trace defaults

Tools:
- Diagnostic report
- Package smoke test
- Device scan
- Channel verification
- Calibration manager
- Fault/event viewer
- Safe state now

Help:
- Run instructions
- Test instructions
- Known limitations
- About/version

7.3 Status Strip
The UI should continuously expose operational truth.
Status strip fields:
app version
run id
current time
acquisition state
PSU/control state
device connection state
last telemetry age
sample interval
write status
historian status
fault count
safe-state status

A status strip is not decorative.
It is a diagnostic surface.

7.4 Graphing Requirements
The graph should support:
* live mode;
* explore/pause mode;
* sliding-window mode;
* full-history mode;
* trace visibility controls;
* trace names editable or mapped to engineering names;
* units in axis labels;
* multiple y-axis groups where practical;
* setpoint vs measured traces;
* fault markers;
* sequence step markers;
* export PNG;
* export visible data CSV;
* decimation labels when used.
Trace categories should be visually distinct:
measured values
commanded setpoints
derived values
fault/event markers
sequence boundaries
quality/staleness indicators

Known convention from Genesys-style work:
Voltage: blue family
Current: red family

But the user should be able to override colors where practical.

7.5 Signal Explorer vs Device Explorer
Separate physical devices from logical signals.
Device Explorer:
LabJack U6
Genesys+ PSU
Arduino hub
ESP32 node
Serial adapter
VISA instrument

Signal Explorer:
Stack Voltage
Stack Current
Cell Temperature 01
Cell Temperature 02
Anode Pressure
Cathode Pressure
Flow Rate
Calculated Power
Calculated Resistance

Reason:
The operator thinks in signals.
The hardware layer thinks in channels.
The software must bridge them without confusing them.

7.6 Trace Controls
Trace controls should include:
visible
display name
units
color
line width
line style
axis group
alarm enabled
min/max display range
smoothing/display filter
raw/derived selection

For many-channel systems, trace controls must be searchable/filterable.
Do not force the operator to manage 80 channels in one flat, cramped list.
Useful grouping:
Voltage
Current
Temperature
Pressure
Flow
Digital Inputs
Digital Outputs
Derived
Faults
Setpoints

8. Configuration Doctrine
8.1 Separate Configuration Types
Do not put everything into one settings file.
Recommended split:
settings.json
    User preferences and app behavior.

device_map.json
    Known devices, serial numbers, roles.

channel_map.json
    Physical channel to logical signal mapping.

calibration.json
    Calibration coefficients and metadata.

ui_state.json
    Window layout, visible traces, panel positions.

sequence_library.json
    Saved ramps/sequences.

safety_policy.json
    Shutdown behavior, output-enable policy, limits.

This makes configuration auditable.

8.2 Settings Are Not Runtime Data
Settings answer:
What does the user prefer?

Runtime state answers:
What was happening when the app last ran?

Run data answers:
What happened during this test?

Keep these separate.

8.3 Configuration Must Be Versioned
Every config file should include:
{
  "schema_version": 1,
  "created_at": "",
  "updated_at": "",
  "app_version": ""
}

Migration policy:
Backup before migration.
Preserve unknown fields where practical.
Never silently discard user configuration.
Log migration result.

9. Architecture Doctrine
9.1 Preferred Layer Model
Recommended architecture:
compat/constants
        ↓
paths/settings/logging
        ↓
device adapters / protocols
        ↓
signal mapping / calibration
        ↓
acquisition engine
        ↓
historian / storage
        ↓
business actions / control services
        ↓
sequence engine
        ↓
diagnostics / health model
        ↓
UI view models
        ↓
GUI shell

The UI should not directly command raw hardware except through control services.
The acquisition layer should not directly render UI.
The device adapter should not know graph colors.
The historian should not depend on GUI widgets.

9.2 Recommended Modules
project_name/
├── __init__.py
├── constants.py
├── compat.py
├── paths.py
├── settings.py
├── logging_utils.py
│
├── devices/
│   ├── base.py
│   ├── labjack_adapter.py
│   ├── genesys_adapter.py
│   ├── visa_adapter.py
│   ├── serial_adapter.py
│   └── simulated_devices.py
│
├── signals/
│   ├── channel_map.py
│   ├── calibration.py
│   ├── quality.py
│   └── derived.py
│
├── acquisition/
│   ├── engine.py
│   ├── scheduler.py
│   ├── buffers.py
│   └── packet_validation.py
│
├── control/
│   ├── command_model.py
│   ├── safety.py
│   ├── output_manager.py
│   └── state_machine.py
│
├── sequences/
│   ├── model.py
│   ├── preview.py
│   ├── executor.py
│   └── validation.py
│
├── storage/
│   ├── csv_logger.py
│   ├── sqlite_historian.py
│   ├── manifest.py
│   └── recovery.py
│
├── diagnostics/
│   ├── health.py
│   ├── report.py
│   ├── smoke.py
│   └── device_checks.py
│
├── ui/
│   ├── main_window.py
│   ├── graph_panel.py
│   ├── device_explorer.py
│   ├── signal_explorer.py
│   ├── sequence_panel.py
│   ├── diagnostics_panel.py
│   └── settings_dialog.py
│
└── app.py

9.3 Device Adapter Contract
Every device adapter should expose a consistent shape.
connect()
disconnect()
is_connected()
read_identity()
read_telemetry()
write_command(command)
enter_safe_state(reason)
diagnostics()

Adapter diagnostics should include:
device type
serial number
connection status
last successful read
last successful write
last error
error count
firmware/version if available
communication backend
safe-state status

9.4 Simulation Mode
Every hardware-control package should eventually support simulated devices.
Simulation mode allows:
* UI testing without hardware;
* sequence preview testing;
* long-duration graph replay;
* diagnostics testing;
* CI/smoke testing;
* development when hardware is unavailable.
Simulated data must be clearly labeled.
Never let simulated data be mistaken for real test data.

10. Diagnostics Doctrine
10.1 Required Diagnostic Reports
For these projects, diagnostics should include:
diagnostic_report.txt
device_diagnostics_report.txt
package_smoke_test_report.txt
structure_audit_report.txt
dependency_audit_report.txt
channel_map_audit_report.txt
historian_integrity_report.txt
safe_shutdown_test_report.txt

10.2 Diagnostic Harness Contents
Minimum diagnostic report:
App name/version
Python version
OS/platform
Working directory
Package root
Runtime data path
Settings path
Historian path
Log path
Display/screen info
GUI toolkit version
Dependency imports
Device adapter imports
Detected devices
Expected devices
Connection status
Last telemetry age
Acquisition loop status
Command/control state
Safe-state status
File read/write test
SQLite open/write/read test if applicable
CSV append test
Channel map loaded?
Calibration loaded?
Recent errors
Tracebacks
Pass/fail summary

10.3 Backend Diagnostics Must Be Reachable From UI
The UI should have a Diagnostics panel or Tools menu item that requests backend diagnostics.
The UI should not invent health status from stale local assumptions.
For multi-process systems:
frontend requests backend diagnostics
backend returns authoritative status
frontend displays status and saves report

10.4 Noise Control
Avoid log spam.
Known issue to avoid:
Repeated config GET chatter every second in logs.

Policy:
* high-rate routine events should be summarized;
* state changes should be logged;
* faults should be logged;
* repeated status pings should be debug-level or summarized;
* command events should always be traceable.

11. Acceptance Tests
11.1 Minimum Hardware-Control Acceptance Tests
ACCEPT-HW-001
Test: App starts with hardware disconnected.
Expected:
App opens or diagnostics run in degraded mode. No crash. Missing devices are reported clearly.

ACCEPT-HW-002
Test: App starts with hardware connected.
Expected:
Devices are detected but outputs remain disabled until explicit operator action.

ACCEPT-HW-003
Test: Manual safe-state button.
Expected:
Active command/sequence is interrupted and safe-state command is logged.

ACCEPT-HW-004
Test: Normal shutdown.
Expected:
Active acquisition stops cleanly, buffers flush, outputs enter documented shutdown state, clean shutdown marker written.

ACCEPT-HW-005
Test: Simulated abnormal exception.
Expected:
Safe-state handler runs, traceback is logged, diagnostic report is written, abnormal shutdown marker is written.

ACCEPT-HW-006
Test: Device disconnect during acquisition.
Expected:
UI remains responsive, data history preserved, affected signals marked stale/disconnected, fault event logged.

ACCEPT-HW-007
Test: Device reconnect.
Expected:
Device identity is checked before readings resume. Channel map is not silently changed.

ACCEPT-HW-008
Test: Long-duration replay.
Expected:
Plot remains responsive, raw data preserved, full-history decimation labeled, sliding-window behavior correct.

ACCEPT-HW-009
Test: Channel verification.
Expected:
Known stimulus appears on expected logical signal, graph trace, export column, and historian field.

ACCEPT-HW-010
Test: Sequence execution.
Expected:
Preview, command log, setpoint graph, measured graph, and sequence state agree.

11.2 Data Integrity Acceptance Tests
ACCEPT-DATA-001
Test: CSV append under normal acquisition.
Expected:
Rows append with correct column count and parseable timestamps.

ACCEPT-DATA-002
Test: Malformed packet/input.
Expected:
Malformed record is rejected or flagged. Master data file is not corrupted.

ACCEPT-DATA-003
Test: Historian write/read.
Expected:
Inserted records can be queried by run, time, device, and signal.

ACCEPT-DATA-004
Test: Abnormal shutdown during logging.
Expected:
Last flushed row is known. Recovery state is written. Existing data remains readable.

ACCEPT-DATA-005
Test: Export visible plot data.
Expected:
Export clearly identifies raw/derived/display-decimated status.

ACCEPT-DATA-006
Test: Calibration change.
Expected:
New calibration is versioned. Prior data remains traceable to prior calibration.

11.3 UI Acceptance Tests
ACCEPT-UI-001
Test: Launch at target screen resolution.
Expected:
Main graph is visible. Safe-state button is visible. Critical status is visible.

ACCEPT-UI-002
Test: Resize window.
Expected:
Main graph and panels resize without overlapping controls.

ACCEPT-UI-003
Test: Toggle trace visibility.
Expected:
Trace visibility changes immediately and persists if configured.

ACCEPT-UI-004
Test: Reset layout.
Expected:
Panels return to usable default positions.

ACCEPT-UI-005
Test: Diagnostics from UI.
Expected:
Diagnostic report can be generated without leaving the app.

ACCEPT-UI-006
Test: Explore/pause mode.
Expected:
Graph can be inspected without corrupting acquisition or logging.

12. Common Risks
RISK-HW-001
Title: Output remains energized after software fault
Likelihood: Medium
Impact: Critical
Detection:
Safe-state fault injection test.
Mitigation:
Central safe-state handler, top-level exception handling, explicit shutdown policy.
Fallback:
Manual hardware cutoff / physical E-stop / PSU front-panel output off.
Status: Open

RISK-HW-002
Title: Channel map mismatch
Likelihood: Medium
Impact: High
Detection:
Channel verification test with known stimulus.
Mitigation:
Device/channel map audit, calibration records, clear signal explorer.
Fallback:
Disable unverified channels.
Status: Open

RISK-HW-003
Title: Stale telemetry displayed as current
Likelihood: Medium
Impact: High
Detection:
Telemetry age indicator and disconnect test.
Mitigation:
Quality flags, stale timeout, visible telemetry age.
Fallback:
Mark signal stale and stop plotting as live.
Status: Open

RISK-HW-004
Title: Data loss during crash or power loss
Likelihood: Medium
Impact: High
Detection:
Abnormal shutdown test.
Mitigation:
Buffered writes, frequent flush, append-only raw log, recovery state.
Fallback:
Recover from last flushed row and event log.
Status: Open

RISK-HW-005
Title: UI freezes during long run
Likelihood: Medium
Impact: Medium/High
Detection:
Long-duration replay/stress test.
Mitigation:
Separate acquisition from plotting, sliding window, decimated full-history mode.
Fallback:
Disable live full-history plotting and preserve raw logging.
Status: Open

RISK-HW-006
Title: Manual and sequence commands conflict
Likelihood: Medium
Impact: High
Detection:
Mode ownership test.
Mitigation:
Explicit command state machine and setpoint ownership.
Fallback:
Abort sequence on manual override or enter safe state.
Status: Open

13. Technical Debt Patterns
DEBT-HW-001
Title: UI directly controls hardware adapter
Category: Architecture
Impact:
Hard to test, hard to simulate, unsafe command paths.
Resolution:
Route commands through control service/state machine.

DEBT-HW-002
Title: Channel names hardcoded in plotting code
Category: Maintainability
Impact:
Channel map changes require code edits.
Resolution:
Use channel_map.json and signal explorer.

DEBT-HW-003
Title: Raw data and display data mixed
Category: Data integrity
Impact:
Plot decimation may contaminate exports or analysis.
Resolution:
Separate raw, derived, and display data layers.

DEBT-HW-004
Title: No simulated hardware layer
Category: Testing
Impact:
UI and sequence behavior cannot be tested without physical setup.
Resolution:
Add simulated device adapters.

DEBT-HW-005
Title: Shutdown behavior implicit
Category: Safety
Impact:
Unclear what happens on exit/fault.
Resolution:
Document and implement deterministic shutdown policy.

14. Package Requirements for DAQ/Control Projects
A professional package should include:
README_START_HERE.md
RUN_INSTRUCTIONS.md
TEST_INSTRUCTIONS.md
CHANGELOG.md
KNOWN_LIMITATIONS.md

docs/
├── 010_PRODUCT_REQUIREMENTS.md
├── 020_CURRENT_FEATURE_INVENTORY.md
├── 025_PUBLIC_INTERFACE_FREEZE.md
├── 030_FOLDER_STRUCTURE_SPEC.md
├── 040_ARCHITECTURE_SPEC.md
├── 050_MODULE_BOUNDARY_SPEC.md
├── 060_DATA_SCHEMA_SPEC.md
├── 070_UI_LAYOUT_SPEC.md
├── 080_ACCEPTANCE_TEST_PLAN.md
├── 090_DIAGNOSTICS_SPEC.md
├── 100_RISK_REGISTER.md
├── 110_TECHNICAL_DEBT_REGISTER.md
├── 120_DECISION_LOG.md
├── 130_OPEN_QUESTIONS.md
├── 140_REFACTOR_SEQUENCE_PLAN.md
├── 170_COMPATIBILITY_LESSONS_LEARNED.md
└── 180_HARDWARE_DAQ_CONTROL_INTERFACE_DOCTRINE.md

tools/
├── diagnostic_harness.py
├── package_smoke_test.py
├── structure_audit.py
├── dependency_audit.py
├── channel_map_audit.py
├── historian_integrity_check.py
└── safe_shutdown_test.py

15. Definition of Done
A hardware DAQ/control package is not done merely because the GUI launches.
It is acceptable only when:
[ ] Hardware starts safe.
[ ] Outputs are not auto-enabled unexpectedly.
[ ] Manual safe-state control is visible.
[ ] Safe-state behavior is logged.
[ ] Normal shutdown is deterministic.
[ ] Abnormal shutdown writes recovery/diagnostics.
[ ] Raw data is preserved.
[ ] Display decimation does not corrupt raw data.
[ ] Channel mapping is explicit.
[ ] Calibration is explicit.
[ ] Device identity is explicit.
[ ] Disconnect handling is tested.
[ ] Reconnect behavior is defined.
[ ] Historian/storage is tested.
[ ] Diagnostics can run without the GUI.
[ ] GUI shows telemetry age and command state.
[ ] Sequence preview and execution agree.
[ ] Feature inventory exists.
[ ] Risk register exists.
[ ] Technical debt register exists.
[ ] Acceptance tests are documented.
[ ] Package can be reviewed without chat history.

16. Core Rule
For DAQ/control software:
The graph is not the product.
The control panel is not the product.
The device adapter is not the product.
The product is the complete system of:
truthful acquisition
safe control
durable storage
clear operator feedback
diagnosable behavior
recoverable failures
maintainable structure

If any one of those fails, the system is not finished.

DAQ and Safety Examples
I’d make this a companion appendix to the hardware-control doctrine:
