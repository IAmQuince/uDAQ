---
document_id: DOC-170
title: "Compatibility Lessons Learned"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-170
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Compatibility Lessons Learned

## 0. Purpose

This document records practical compatibility, environment, hardware, GUI, and deployment lessons learned across prior projects.

It exists because many of our projects run in constrained or unusual environments:

- Windows XP / Python 2.7;
- Raspberry Pi / Linux;
- Arduino / ESP32 / embedded C++;
- LabJack devices;
- serial devices;
- PyVISA / instrument control;
- Android / Pydroid / Kivy;
- offline computers;
- legacy browsers;
- small touchscreens;
- USB devices and drivers;
- local data logging;
- GUI-heavy engineering tools.

These lessons should be used before writing code, before choosing libraries, before packaging, and before refactoring.

The goal is not to preserve trivia.

The goal is to prevent us from repeatedly rediscovering the same compatibility failures.

## 1. Core Principle

Do not assume the development machine represents the target machine.

A program that runs on a modern Windows laptop may fail on:

- Windows XP;
- Raspberry Pi OS;
- Python 2.7;
- offline machines;
- Android Pydroid;
- low-resolution touchscreens;
- systems without GPU acceleration;
- machines without modern browser support;
- machines with old USB drivers;
- machines with missing C/C++ build chains;
- systems where hardware is disconnected or intermittently available.

Every serious project should explicitly define:

- target OS;
- target Python/runtime;
- target GUI toolkit;
- target hardware;
- allowed dependencies;
- forbidden dependencies;
- offline/online assumptions;
- driver assumptions;
- screen/display assumptions;
- file-transfer assumptions;
- diagnostic requirements.

## 2. Documentation Rule

Every compatibility lesson should be recorded in this format:

```text
LESSON-000
Title:
Environment:
Category:
Status: Solved / Partially solved / Unresolved / Avoid / Unknown
Observed problem:
Root cause:
Working solution:
Fallback:
Prevention rule:
Diagnostic check:
Applies to:
Related risks:
Related debt:
Last verified:

This prevents vague notes like:
Python issue on Raspberry Pi.
Instead, we want:
LESSON-PI-001
Title: Avoid assuming modern Python packages install cleanly on Raspberry Pi
Environment: Raspberry Pi / Linux / Python
Category: Dependency compatibility
Status: Solved by prevention
Observed problem:
Some modern Python packages are too heavy, unavailable, slow, or difficult to build on the target Pi.
Root cause:
Raspberry Pi hardware, OS package versions, Python version, wheel availability, and native build dependencies may not match desktop assumptions.
Working solution:
Prefer standard library or already-installed packages when possible. Keep dependency list short. Add dependency diagnostics before GUI launch.
Fallback:
Provide degraded mode without optional plotting/device/UI feature.
Prevention rule:
No new dependency may be added without target-environment justification and import diagnostics.
Diagnostic check:
tools/dependency_audit.py and tools/diagnostic_harness.py must report import availability and versions.
Applies to:
Raspberry Pi DAQ, garage monitor, LabJack GUI, uDAQ-style tools.

3. Solved / Reliable Patterns
LESSON-GEN-001 — Diagnostic harnesses are not optional for remote/hardware testing
Environment:
All serious projects.
Category:
Diagnostics / supportability.
Status:
Solved pattern.
Observed problem:
When code fails on a target machine we cannot directly access, ordinary error descriptions are often incomplete.
Root cause:
The real issue may be Python version, package availability, working directory, file paths, display size, hardware connection, permissions, driver installation, or stale runtime data.
Working solution:
Include a diagnostic harness that writes a copy/pasteable report.
Minimum report contents:
* app version;
* Python version;
* OS/platform;
* working directory;
* package root;
* expected files/folders;
* config paths;
* data paths;
* dependency/import checks;
* GUI/display assumptions;
* file read/write test;
* hardware availability if relevant;
* recent errors;
* traceback;
* pass/fail summary.
Fallback:
If GUI fails, diagnostics must still run from command line.
Prevention rule:
Every package should include tools/diagnostic_harness.py.
Diagnostic check:
Run:
python tools/diagnostic_harness.py

Applies to:
All projects.

LESSON-GEN-002 — Start from the actual target environment, not modern best practice
Environment:
Windows XP, Raspberry Pi, Pydroid, embedded boards, offline machines.
Category:
Architecture / compatibility.
Status:
Solved by discipline.
Observed problem:
Code using modern Python features, modern UI assumptions, or modern libraries can be unusable on the actual target.
Root cause:
Default coding habits tend to target current desktop Python, not the deployment environment.
Working solution:
Define the target environment before coding.
Prevention rule:
No code should be written until these are known:
* OS;
* Python version;
* GUI toolkit;
* allowed dependencies;
* offline/online status;
* screen size;
* hardware drivers;
* file-transfer method.
Diagnostic check:
The diagnostic report must print all of the above.
Applies to:
All projects.

LESSON-GEN-003 — Avoid dependency bloat until the target machine proves it can support it
Environment:
Raspberry Pi, Windows XP, Pydroid, offline systems.
Category:
Dependencies.
Status:
Solved by conservative defaults.
Observed problem:
Libraries that are easy to install on a modern machine can fail on older systems, small Linux boards, or Android Python environments.
Root cause:
Missing wheels, compiler requirements, OS-level shared libraries, old Python versions, and architecture-specific issues.
Working solution:
Use standard library first. Add dependencies only when they clearly justify their maintenance burden.
Prevention rule:
Every dependency must be classified:
Dependency:
Required or optional:
Why needed:
Target environment support:
Install method:
Fallback if missing:
Diagnostic check:

Fallback:
Disable optional feature and report missing dependency clearly.
Applies to:
Raspberry Pi, XP, Pydroid, engineering GUIs.

LESSON-GEN-004 — Use feature inventory to prevent compatibility fixes from deleting features
Environment:
All projects.
Category:
Refactor / preservation.
Status:
Solved pattern.
Observed problem:
While fixing compatibility issues, features can be silently removed.
Root cause:
The person refactoring focuses on the immediate failure and forgets small UI controls, settings, exports, logs, hotkeys, or workflow details.
Working solution:
Maintain docs/020_CURRENT_FEATURE_INVENTORY.md.
Prevention rule:
Before compatibility edits, list existing features. After edits, run feature inventory check.
Diagnostic check:
tools/feature_inventory_check.py.
Applies to:
All package formalization work.

4. Windows XP / Python 2.7 Lessons
LESSON-XP-001 — Python 2.7 syntax must be enforced deliberately
Environment:
Windows XP / Python(x,y) 2.7.6.1.
Category:
Language compatibility.
Status:
Solved.
Observed problem:
Modern Python code fails immediately on XP-targeted Python.
Root cause:
Python 2.7 does not support modern syntax or standard-library features.
Forbidden unless explicitly proven compatible:
* f-strings;
* pathlib;
* dataclasses;
* type annotations;
* keyword-only arguments;
* modern async / await;
* Python 3-only standard-library modules;
* many current PyPI package versions.
Working solution:
Use Python 2.7-compatible syntax.
Prevention rule:
For XP projects, include a Python 2 syntax/import smoke test.
Diagnostic check:
python tools/compat_smoke_test.py

Applies to:
XP finance planner, XP retro tools, XP LabJack tests.

LESSON-XP-002 — Prefer known-good old stacks over modern replacements
Environment:
Windows XP.
Category:
Dependency compatibility.
Status:
Solved by environment freeze.
Observed problem:
Modern Python GUI/data libraries are not installable or not compatible with XP.
Root cause:
Windows XP is no longer supported by most modern package builds.
Working solution:
Use the known XP stack unless explicitly changed:
* Python(x,y) 2.7.6.1;
* PyQt4 where available;
* older matplotlib;
* old LabJackPython where needed;
* standard library when possible.
Prevention rule:
Do not introduce modern package requirements into XP-targeted projects.
Diagnostic check:
Dependency audit must report exact imported packages and versions.
Applies to:
XP GUI tools, finance planner, LabJack testing.

LESSON-XP-003 — Offline installation must be treated as a design constraint
Environment:
Offline Windows XP machine.
Category:
Deployment.
Status:
Solved by packaging discipline.
Observed problem:
A tool may technically work but be impossible to install cleanly on the offline XP computer.
Root cause:
The target machine cannot fetch dependencies, installers, docs, or drivers online.
Working solution:
Package all required installers, source files, launchers, docs, and instructions for USB transfer.
Prevention rule:
Every XP package must include:
* README_START_HERE;
* RUN_INSTRUCTIONS;
* TEST_INSTRUCTIONS;
* known dependency list;
* offline install notes;
* no internet-required install steps unless explicitly marked.
Diagnostic check:
Run package from transferred folder without internet.
Applies to:
XP software projects.

LESSON-XP-004 — Legacy browsers cannot be treated as modern web runtimes
Environment:
Windows XP / RetroZilla / old browsers.
Category:
Browser compatibility.
Status:
Partially solved / avoid modern web assumptions.
Observed problem:
Modern HTML/CSS/JavaScript features do not work reliably in XP-era browsers.
Root cause:
Old browser engines lack support for modern media codecs, layout systems, JavaScript features, and security APIs.
Avoid:
* CSS Grid;
* modern Flexbox reliance for critical layout;
* ES6+ JavaScript;
* modern video playback assumptions;
* modern TLS/web service assumptions;
* complex frontend frameworks.
Working solution:
Use simple HTML, table/block layouts if necessary, minimal JavaScript, and graceful fallback.
Prevention rule:
If the target is XP browser-based, test in the actual browser early.
Diagnostic check:
Include browser name/version and render test page.
Applies to:
XP local web tools, retro offline archive tools.

LESSON-XP-005 — Media/codecs are a weak point on XP browsers
Environment:
Windows XP / legacy browser / local media.
Category:
Media compatibility.
Status:
Partially solved.
Observed problem:
Some media files do not play in the browser even if the file exists locally.
Root cause:
Browser codec support, OS codec installation, plugin availability, and file format support are inconsistent.
Working solution:
Do not assume browser playback. Provide external-open fallback where possible.
Fallback options:
* open file in associated local player;
* provide file path link;
* classify unsupported media;
* record tested/broken/unsupported status.
Prevention rule:
Media browser projects must separate “file exists” from “file playable in embedded/browser view.”
Diagnostic check:
Test known sample files by extension and record playback status.
Applies to:
Retro archive/browser projects.

LESSON-XP-006 — Drivers are often the real blocker, not the application code
Environment:
Windows XP / USB devices / audio / MIDI / LabJack.
Category:
Drivers.
Status:
Partially solved.
Observed problem:
A program can be correct but the hardware still does not appear or function.
Root cause:
Missing XP-era drivers, wrong driver version, unsupported newer hardware, USB stack limitations, or device class incompatibility.
Working solution:
Identify exact hardware model and driver version before coding against it.
Prevention rule:
Create a driver verification step before application testing.
Diagnostic check:
Device model:
USB VID/PID if available:
Driver installed:
Driver version:
Device Manager status:
Vendor utility works? Yes/No:
Application can see device? Yes/No:

Applies to:
MIDI interfaces, audio interfaces, LabJack, USB devices.

5. Raspberry Pi / Linux Lessons
LESSON-PI-001 — Raspberry Pi projects need degraded mode
Environment:
Raspberry Pi / Python / hardware devices.
Category:
Reliability.
Status:
Solved pattern.
Observed problem:
A project may fail to launch if hardware, GUI, display, or optional libraries are unavailable.
Root cause:
Pi systems are often headless, display-constrained, hardware-dependent, or missing optional packages.
Working solution:
Design degraded modes:
* no hardware mode;
* no GUI mode;
* logging-only mode;
* simulation mode;
* diagnostics-only mode;
* safe mode.
Prevention rule:
Application startup should not require every optional component to succeed.
Diagnostic check:
Run with hardware disconnected and verify diagnostics still complete.
Applies to:
Raspberry Pi DAQ, garage monitor, LabJack GUI, uDAQ.

LESSON-PI-002 — Heavy GUI libraries can be a poor fit on Raspberry Pi
Environment:
Raspberry Pi with touchscreen or modest display.
Category:
GUI performance.
Status:
Solved by conservative UI choices.
Observed problem:
Some GUI stacks or plotting libraries feel sluggish, fail to install, or overload the Pi.
Root cause:
Limited CPU/GPU/RAM, package build issues, and display-driver quirks.
Working solution:
Prefer simpler GUI stacks and controlled plotting. Use matplotlib carefully if it is already known-good. Avoid heavy real-time redraws.
Prevention rule:
Benchmark UI update rate early on the target Pi.
Diagnostic check:
Report:
* display resolution;
* DPI/scaling;
* plot update interval;
* CPU load if available;
* memory use if available;
* average redraw time if measurable.
Applies to:
Pi data logger, garage monitor, touchscreen apps.

LESSON-PI-003 — Data integrity requires buffering and failover
Environment:
Raspberry Pi DAQ / sensor logging.
Category:
Data integrity.
Status:
Solved pattern.
Observed problem:
Communication stalls, MQTT failures, or sensor dropouts can corrupt or interrupt data logging.
Root cause:
Networks, serial links, sensor boards, or services may drop intermittently.
Working solution:
Use local CSV buffering, periodic flushes, backup files, and clear fault markers.
Prevention rule:
Never rely on one live communication path as the only data record.
Diagnostic check:
Simulate communication loss and verify:
* buffered data is retained;
* master CSV is not corrupted;
* re-entry is graceful;
* fault period is marked.
Applies to:
Garage monitor, Pi sensor logging, uDAQ.

LESSON-PI-004 — Device disconnect/reconnect must be normal behavior
Environment:
Raspberry Pi / LabJack / Arduino / ESP32 / USB devices.
Category:
Hardware reliability.
Status:
Partially solved / must design explicitly.
Observed problem:
Unplugging/replugging devices can break the live graph, data history, or device mapping.
Root cause:
Device handles, serial ports, USB enumeration, and channel mappings can change after reconnect.
Working solution:
Implement heartbeat, reconnect detection, device identity checks, and explicit degraded state.
Prevention rule:
Hardware code must treat disconnect as expected, not exceptional.
Diagnostic check:
Manual test:
1. Start app.
2. Confirm device connected.
3. Unplug device.
4. Verify warning/log entry.
5. Replug device.
6. Verify reconnect or explicit recovery instruction.
7. Confirm data history is not silently corrupted.

Applies to:
LabJack U3/U6, Arduino, ESP32, serial sensors.

LESSON-PI-005 — Plotting raw long-duration data can freeze the UI
Environment:
Raspberry Pi / Python plotting / DAQ.
Category:
Performance.
Status:
Partially solved.
Observed problem:
Long-term plots become sluggish or freeze after many hours of data.
Root cause:
Rendering too many points, replotting entire history too frequently, or mixing decimated/full-resolution modes incorrectly.
Working solution:
Separate modes:
* sliding window: full fidelity within recent window;
* entire history: decimated and clearly labeled;
* export/raw data: full data preserved.
Prevention rule:
Do not let decimation contaminate the raw data or the sliding-window display unless explicitly selected.
Diagnostic check:
Run replay test with large synthetic dataset and verify:
* sliding window updates quickly;
* full history is labeled as decimated;
* raw export remains complete;
* axis units remain readable.
Applies to:
DAQ graphing, LabJack viewer, SQLite viewer.

6. LabJack / Instrument-Control Lessons
LESSON-LJ-001 — LabJack imports and versions must match the environment
Environment:
LabJack U3/U6 / Python.
Category:
Driver/library compatibility.
Status:
Solved by explicit import policy.
Observed problem:
LabJack code fails when using the wrong import style or wrong library version for the machine.
Root cause:
Different LabJackPython installs expose different modules and APIs.
Known working pattern in prior work:
Use:
import u6

for U6-focused code where that is the installed module.
Prevention rule:
Do not assume from labjack import u6 unless verified on the target.
Diagnostic check:
Diagnostic harness should attempt:
import u6

and report success/failure.
Applies to:
LabJack U6 projects.

LESSON-LJ-002 — MUX/channel indexing must be verified with real signals
Environment:
LabJack U6 / MUX80 / analog channels.
Category:
Hardware mapping.
Status:
Partially solved.
Observed problem:
Channels can be offset or mislabeled, causing wrong temperature/voltage traces.
Root cause:
MUX expansion indexing and wiring assumptions can differ from code assumptions.
Working solution:
Create an explicit channel map and verify each channel with known stimulus.
Prevention rule:
No DAQ package should treat channel names as trusted until channel verification is complete.
Diagnostic check:
Channel:
Physical wire:
Expected signal:
Observed signal:
Units:
Calibration:
Verified by:
Date:

Applies to:
LabJack U6/MUX80, multi-sensor DAQ.

LESSON-LJ-003 — Hardware-control software must start safe and fail safe
Environment:
LabJack, PSU, pumps, motors, relays, heaters, control systems.
Category:
Safety.
Status:
Solved principle / must implement per project.
Observed problem:
Startup, crash, or disconnect could leave hardware in an ambiguous state.
Root cause:
Software state, device state, and physical output state can diverge.
Working solution:
Make safe-state behavior explicit:
* no dangerous auto-connect;
* no output enable on startup unless explicitly commanded;
* safe shutdown hook;
* visible safe-state button;
* command-state logging;
* fault-state logging.
Prevention rule:
Every hardware/control project must define startup, shutdown, exception, and disconnect behavior before implementation.
Diagnostic check:
Manual safe-state test.
Applies to:
Genesys+, LabJack, uDAQ, motors, heaters.

7. Arduino / ESP32 / Embedded C++ Lessons
LESSON-EMB-001 — Timestamps should be captured at the device when measurement truth matters
Environment:
Arduino / ESP32 / Raspberry Pi sensor network.
Category:
Data integrity.
Status:
Solved principle.
Observed problem:
If the Pi timestamps data only when received, graph timing can be misleading during stalls.
Root cause:
Communication delay is not the same as measurement time.
Working solution:
Each device should timestamp or sequence its own measurements where practical.
Prevention rule:
DAQ protocols should distinguish:
* measurement timestamp;
* receive timestamp;
* log-write timestamp.
Diagnostic check:
Induce serial/network delay and verify plotted time reflects measurement time.
Applies to:
Distributed sensor networks.

LESSON-EMB-002 — Packets must be validated before being forwarded or logged
Environment:
Arduino / ESP32 / serial / UART.
Category:
Data integrity.
Status:
Solved pattern.
Observed problem:
Malformed data can corrupt CSV logs or break parsers.
Root cause:
Serial noise, partial reads, buffer overflow, reset messages, or mixed debug/data output.
Working solution:
Use structured packets and validate before forwarding.
Minimum packet policy:
* start marker or recognizable prefix;
* field count check;
* numeric parsing check;
* checksum if needed;
* timestamp/sequence if needed;
* reject malformed packets;
* log reject count.
Prevention rule:
Debug text and data packets should be clearly separable.
Diagnostic check:
Send malformed packet and confirm it is rejected without corrupting data file.
Applies to:
Arduino, ESP32, Pi serial hub.

LESSON-EMB-003 — Serial buffering must be designed, not assumed
Environment:
Arduino / ESP32 / Raspberry Pi serial links.
Category:
Communication reliability.
Status:
Partially solved.
Observed problem:
Data can be lost or reordered during stalls, high-rate bursts, or reconnects.
Root cause:
Limited serial buffers and blocking code.
Working solution:
Use ring buffers or short message queues, avoid long blocking delays, and include sequence numbers.
Prevention rule:
Embedded firmware should define:
* message rate;
* buffer size;
* overflow behavior;
* retry behavior;
* heartbeat behavior;
* sequence counter behavior.
Diagnostic check:
Stress test with temporarily blocked receiver.
Applies to:
ESP32 hub, Arduino bridge, Pi serial logger.

LESSON-EMB-004 — Heartbeat messages are useful for field diagnosis
Environment:
Pi / Arduino / ESP32 networks.
Category:
Diagnostics.
Status:
Solved pattern.
Observed problem:
It is difficult to tell whether a device is dead, disconnected, stalled, or simply not producing new data.
Root cause:
No explicit health signal.
Working solution:
Use heartbeat messages with device ID, uptime, sequence counter, and status.
Prevention rule:
Any distributed sensor/control system should include heartbeat reporting.
Diagnostic check:
Diagnostic report should show last heartbeat age per device.
Applies to:
Pi/Arduino/ESP32 systems.

LESSON-EMB-005 — Logic-level wiring matters
Environment:
Raspberry Pi / ESP32 / Arduino UART.
Category:
Hardware interface.
Status:
Solved by wiring discipline.
Observed problem:
Serial communication can fail or hardware can be stressed if voltage levels are mismatched.
Root cause:
Raspberry Pi GPIO is 3.3 V logic; Arduino boards may use 5 V logic depending on model.
Working solution:
Use level shifting or voltage divider where needed.
Prevention rule:
Every serial hardware doc must include a wiring table and voltage-level note.
Diagnostic check:
TX device:
RX device:
TX voltage:
RX tolerance:
Level shifting used:
Ground common:
Verified:

Applies to:
Pi / ESP32 / Arduino UART chains.

8. Android / Pydroid / Kivy Lessons
LESSON-ANDROID-001 — Pydroid is useful but not a normal desktop Python environment
Environment:
Android / Pydroid.
Category:
Runtime compatibility.
Status:
Partially solved.
Observed problem:
Python code that works on Windows/Linux may fail or behave differently in Pydroid.
Root cause:
Android permissions, filesystem layout, package availability, GUI backend behavior, and mobile GPU/input handling differ from desktop.
Working solution:
Treat Pydroid as its own target environment.
Prevention rule:
Do not assume desktop filesystem paths, desktop window behavior, or full package availability.
Diagnostic check:
Report:
* Android device model if available;
* Python version;
* Pydroid path;
* Kivy version if used;
* storage path;
* display size;
* OpenGL info if available;
* log file path.
Applies to:
Pydroid/Kivy projects.

LESSON-ANDROID-002 — Kivy black-screen failures need log-first diagnosis
Environment:
Android / Pydroid / Kivy.
Category:
GUI diagnostics.
Status:
Partially solved.
Observed problem:
Kivy app may show a black screen or return without visible error.
Root cause:
Kivy errors can be buried in logs; OpenGL, layout, import, or event-loop failures may not display clearly.
Working solution:
Find and inspect Kivy logs before rewriting code.
Prevention rule:
Kivy projects should include a visible startup log and an external diagnostic mode.
Diagnostic check:
Record Kivy log location and include latest relevant traceback.
Applies to:
Android Kivy apps.

LESSON-ANDROID-003 — Touch gestures and screen geometry must be tested on the device
Environment:
Android phone/tablet / Kivy / Pydroid.
Category:
UI behavior.
Status:
Partially solved.
Observed problem:
Gestures, scaling, and layout may behave differently from desktop testing.
Root cause:
Touch input, density scaling, GPU backend, and aspect ratio differ.
Working solution:
Design touch-first controls and test on actual device early.
Prevention rule:
Do not finalize a mobile UI from desktop behavior alone.
Diagnostic check:
Report:
* screen resolution;
* density/DPI if available;
* orientation;
* widget sizes;
* input provider;
* touch event coordinates during test.
Applies to:
Kivy visualizers, CD explorer, 3D/gesture projects.

9. GUI / Display / Screen-Size Lessons
LESSON-GUI-001 — Auto screen detection must have fallback values
Environment:
Tkinter, PyQt, Kivy, Raspberry Pi touchscreens, Windows XP.
Category:
GUI layout.
Status:
Solved pattern.
Observed problem:
Auto-detected screen size or DPI may be wrong, unavailable, or inconsistent.
Root cause:
Different GUI toolkits and OS/display drivers report geometry differently.
Working solution:
Detect screen size where practical, but always provide fallback defaults and user-adjustable scaling.
Prevention rule:
GUI startup should not fail because screen detection failed.
Diagnostic check:
Diagnostic report should include:
* screen width;
* screen height;
* DPI or scale factor if available;
* selected UI scale;
* window geometry;
* whether fallback was used.
Applies to:
All GUI projects.

LESSON-GUI-002 — Fixed-size layouts eventually fail
Environment:
Desktop, XP, Raspberry Pi, Android.
Category:
UI layout.
Status:
Solved principle.
Observed problem:
Controls overlap, disappear, or become unusable on different displays.
Root cause:
Hardcoded window sizes and absolute placement do not generalize.
Working solution:
Use resizable layouts, scrollable panels, splitters/docks where practical, and sensible minimum sizes.
Prevention rule:
Every GUI should define:
* default window size;
* minimum usable size;
* scroll behavior;
* panel resizing behavior;
* persistent layout behavior;
* reset-layout option.
Diagnostic check:
Manual test at small resolution, normal resolution, and high-DPI scale.
Applies to:
All GUI projects.

LESSON-GUI-003 — Important content should not require accidental scrolling
Environment:
Engineering GUIs, media viewers, touchscreen tools.
Category:
UX.
Status:
Solved principle.
Observed problem:
Headers, badges, or controls can push the main content out of view.
Root cause:
Top-heavy layouts and unbounded metadata sections.
Working solution:
Keep critical content visible. Use compact headers, collapsible detail panes, and scrollable side panels.
Prevention rule:
Define what must be visible without scrolling.
Diagnostic check:
Manual test at target resolution.
Applies to:
Media tools, plotting apps, DAQ interfaces.

LESSON-GUI-004 — Settings persistence prevents repeated user friction
Environment:
GUI tools.
Category:
Usability.
Status:
Solved principle.
Observed problem:
Users repeatedly resize windows, reset paths, reselect traces, or restore layouts.
Root cause:
No persistent settings/state.
Working solution:
Persist:
* window size;
* dock/panel layout;
* last paths;
* UI scale;
* theme;
* trace visibility;
* autosave preference;
* recent files;
* user labels where relevant.
Prevention rule:
Every serious GUI should include settings persistence unless the environment makes it impractical.
Diagnostic check:
Change settings, restart, verify restoration.
Applies to:
PyQt, Tkinter, Kivy, engineering GUIs.

10. Data Logging / Plotting Lessons
LESSON-DATA-001 — Raw data must remain separate from display-decimated data
Environment:
DAQ, plotting, SQLite viewer, CSV logs.
Category:
Data integrity.
Status:
Solved principle.
Observed problem:
Display optimizations can accidentally alter what the user believes is raw data.
Root cause:
Decimation logic gets mixed with storage or analysis logic.
Working solution:
Keep raw storage immutable. Apply decimation only in view/query layer and label it clearly.
Prevention rule:
Never overwrite raw data with decimated data.
Diagnostic check:
Compare raw row count to displayed point count and report both.
Applies to:
DAQ tools, SQLite viewer, plotting apps.

LESSON-DATA-002 — Long-running logs need fault-period markers, not spam
Environment:
Sensor logging.
Category:
Logging.
Status:
Solved principle.
Observed problem:
Threshold breaches or device failures can flood logs.
Root cause:
Logging every bad sample instead of state transitions.
Working solution:
Log start and end of fault periods, plus summary counts.
Prevention rule:
For repeated faults, log transitions and periodic summaries.
Diagnostic check:
Simulate threshold violation and verify only start/end/summary are logged.
Applies to:
Garage monitoring, DAQ, hardware monitoring.

LESSON-DATA-003 — CSV is useful but needs strict format discipline
Environment:
Raspberry Pi, Arduino, ESP32, XP.
Category:
Data persistence.
Status:
Solved with constraints.
Observed problem:
CSV files are easy to corrupt with malformed lines, commas in fields, partial writes, or changing column counts.
Root cause:
Loose writes and inconsistent packet formatting.
Working solution:
Use a fixed schema, headers, validation, append discipline, and backup/buffer strategy.
Prevention rule:
Do not append unvalidated sensor packets directly to master CSV.
Diagnostic check:
CSV validator verifies:
* header exists;
* row length matches header;
* numeric fields parse;
* timestamps parse;
* malformed rows are counted.
Applies to:
Sensor networks and DAQ logs.

11. OpenFOAM / CAD / Engineering Toolchain Lessons
LESSON-ENG-001 — External engineering tools require version-specific generated files
Environment:
OpenFOAM, Gmsh, WSL, CAD/export workflows.
Category:
Toolchain compatibility.
Status:
Partially solved.
Observed problem:
Generated dictionaries or files fail because the assumed syntax does not match the installed tool version.
Root cause:
OpenFOAM versions and distributions differ; tutorials and examples may not match the installed environment.
Working solution:
Generate files according to the actual installed version and preserve working templates.
Prevention rule:
Before generating automation, record:
* tool name;
* version;
* install path;
* OS/WSL environment;
* known working case;
* required dictionary syntax;
* forbidden fields.
Diagnostic check:
Run a minimal known-good case before running the full automation.
Applies to:
OpenFOAM/snappyHexMesh/Gmsh automation.

LESSON-ENG-002 — Do not move user CAD/input files unless explicitly intended
Environment:
CAD/STL/STEP/IPT/OpenFOAM pipelines.
Category:
Data safety.
Status:
Solved principle.
Observed problem:
Automation may relocate or modify user source files.
Root cause:
Scripts treat inputs as temporary working files.
Working solution:
Copy source files into a case folder rather than moving them.
Prevention rule:
Input files are read-only unless the user explicitly approves modification.
Diagnostic check:
After run, verify original file still exists unchanged.
Applies to:
Meshing and simulation setup tools.

12. Problems Without Great General Solutions Yet
These are not fully solved. They require project-specific handling.
OPEN-COMPAT-001 — Perfect cross-platform GUI behavior
Status:
Unresolved as a universal solution.
Problem:
No single GUI layout behaves perfectly across Windows XP, modern Windows, Raspberry Pi touchscreens, and Android/Pydroid.
Current best approach:
Use toolkit-specific policies, screen diagnostics, user-adjustable scaling, scrollable panels, and target-device testing.
Prevention:
Do not promise pixel-perfect cross-platform layout.

OPEN-COMPAT-002 — Universal Python dependency compatibility
Status:
Unresolved.
Problem:
There is no reliable way to choose one Python dependency stack that works across XP, modern Windows, Raspberry Pi, and Pydroid.
Current best approach:
Use environment-specific dependency profiles.
Example:
profile_xp_py27
profile_modern_py3
profile_raspberry_pi
profile_android_pydroid

Prevention:
Do not design one package install process until target profiles are defined.

OPEN-COMPAT-003 — Reliable hardware auto-detection across all devices
Status:
Partially solved, not universal.
Problem:
USB, serial, LabJack, VISA, MIDI, audio, and embedded devices expose identity differently.
Current best approach:
Use layered detection:
1. list ports/devices;
2. identify by vendor/product/serial if possible;
3. probe safely;
4. require manual selection if ambiguous;
5. persist user mapping;
6. revalidate on startup.
Prevention:
Do not assume device order or port name is stable.

OPEN-COMPAT-004 — Browser media playback on legacy systems
Status:
Partially solved / often avoid.
Problem:
Old browsers cannot reliably play modern media formats.
Current best approach:
Treat embedded playback as optional. Provide external-open fallback and classify unsupported files.
Prevention:
Do not make browser playback the only access path.

OPEN-COMPAT-005 — Android/Pydroid GUI reliability
Status:
Partially solved.
Problem:
Kivy/Pydroid apps can fail due to device-specific graphics, permissions, package state, or input behavior.
Current best approach:
Keep Android projects small, diagnostic-heavy, and tested directly on the target device.
Prevention:
Do not assume desktop Kivy success predicts Android Kivy success.

OPEN-COMPAT-006 — Long-duration live plotting without eventual performance issues
Status:
Partially solved.
Problem:
Live plots can degrade after hours or days depending on update strategy, data size, and UI toolkit.
Current best approach:
Separate raw data from display data, use sliding windows, decimate full-history views, and stress-test with synthetic long-duration data.
Prevention:
Every plotting app needs replay/stress tests before trusting overnight behavior.

13. Required Compatibility Checklist for Future Projects
Before coding:
[ ] Target OS defined.
[ ] Target Python/runtime defined.
[ ] Target GUI toolkit defined.
[ ] Target hardware defined.
[ ] Offline/online assumption defined.
[ ] Allowed dependencies listed.
[ ] Forbidden dependencies listed.
[ ] Known-good versions listed.
[ ] Screen/display assumptions listed.
[ ] File path/storage assumptions listed.
[ ] Driver requirements listed.
[ ] Safe-state requirements listed, if hardware/control project.
[ ] Diagnostic report requirements listed.
[ ] Smoke-test requirements listed.
[ ] Fallback/degraded modes listed.

Before packaging:
[ ] Dependency audit passes.
[ ] Structure audit passes.
[ ] Diagnostic harness runs.
[ ] Smoke test runs.
[ ] Feature inventory check runs.
[ ] Runtime paths are correct.
[ ] No private runtime data included accidentally.
[ ] Target environment instructions are included.
[ ] Known limitations are updated.
[ ] Compatibility risks are listed.

Before refactoring:
[ ] Frozen baseline exists.
[ ] Feature inventory exists.
[ ] Public interfaces are frozen.
[ ] Compatibility shims are planned.
[ ] Environment-specific tests exist.
[ ] Rollback plan exists.

14. Standard Compatibility Risk Entries
Use these in project risk registers when applicable.
RISK-COMPAT-001
Title: Target runtime incompatibility
Likelihood: Medium
Impact: High
Detection:
Syntax/import smoke test on target runtime.
Mitigation:
Freeze target runtime early. Avoid unsupported language features.
Fallback:
Revert to known-good runtime-compatible baseline.
Status: Open

RISK-COMPAT-002
Title: Optional dependency unavailable on target machine
Likelihood: Medium
Impact: Medium
Detection:
Dependency audit and diagnostic harness.
Mitigation:
Make dependency optional or provide degraded mode.
Fallback:
Disable feature and report missing dependency clearly.
Status: Open

RISK-COMPAT-003
Title: GUI layout unusable on target display
Likelihood: Medium
Impact: High
Detection:
Manual test at target resolution and DPI.
Mitigation:
Resizable layout, scrollable panels, UI scale setting, reset layout option.
Fallback:
Safe-mode/simple layout.
Status: Open

RISK-COMPAT-004
Title: Hardware disconnect corrupts state or data
Likelihood: Medium
Impact: High/Critical
Detection:
Disconnect/reconnect acceptance test.
Mitigation:
Heartbeat, reconnect logic, safe-state handling, buffered writes.
Fallback:
Enter safe degraded state and preserve data.
Status: Open

RISK-COMPAT-005
Title: Offline target cannot install dependencies
Likelihood: Medium
Impact: High
Detection:
Dry-run install from package media without internet.
Mitigation:
Bundle required installers or avoid external dependencies.
Fallback:
Use standard-library-only mode or older known-good package.
Status: Open

15. Core Takeaways
1. Compatibility is a design requirement, not a cleanup task.
2. The target environment must be defined before code.
3. Diagnostics must run even when the main app fails.
4. Hardware disconnects are normal events, not rare exceptions.
5. GUI layout must be tested on the actual display class.
6. Raw data and display data must stay separate.
7. XP and Pydroid require their own assumptions.
8. Raspberry Pi projects need degraded modes.
9. Embedded systems need packet validation, heartbeat, and timestamp discipline.
10. Every solved compatibility problem should become a reusable prevention rule.

Software Package Installs
