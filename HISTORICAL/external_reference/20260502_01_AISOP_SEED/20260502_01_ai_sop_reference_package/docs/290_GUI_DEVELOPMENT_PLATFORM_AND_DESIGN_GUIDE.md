---
document_id: DOC-290
title: "GUI Development Platform and Design Guide"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-290
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# GUI Development Platform and Design Guide

290_GUI_DEVELOPMENT_PLATFORM_AND_DESIGN_GUIDE
0. Purpose
This document explains how we choose and design graphical user interfaces for Python projects across Windows, Windows XP, Raspberry Pi, Android/Pydroid, touchscreen systems, DAQ/control systems, simulations, and engineering tools.
It covers:
the major GUI options
what each GUI framework is good at
what each framework is bad at
platform compatibility issues
screen-size and DPI problems
Pydroid/mobile caveats
Raspberry Pi touchscreen caveats
Windows XP caveats
our preferred interface philosophy
our standard GUI layout patterns
diagnostics and acceptance tests

The goal is to stop treating GUI choice as an afterthought.
A GUI is not just decoration. In our projects, the GUI often determines whether the user can safely operate hardware, understand data, diagnose problems, recover from faults, and trust the software.

1. Core GUI Rule
Choose the GUI framework based on the target device and the interaction style.
Do not choose a GUI framework just because it is familiar.
Engineering desktop app:
    Prefer PyQt/PySide.

Simple utility:
    Tkinter may be enough.

Touchscreen/mobile app:
    Prefer Kivy.

Game/simulation canvas:
    Prefer Pygame.

Browser dashboard:
    Use Flask/FastAPI + HTML/JS or Streamlit-style tools if appropriate.

Windows XP legacy tool:
    Prefer old Tkinter, PyQt4, or known-good installed stack.

Pydroid Android app:
    Prefer Kivy or Pygame, avoid desktop GUI assumptions.

2. GUI Framework Overview
2.1 Tkinter
Tkinter is the standard GUI toolkit that ships with many Python installations.
Best for:
simple desktop tools
forms
buttons
labels
basic menus
small utilities
legacy Python compatibility
quick internal tools
low-dependency projects

Strengths:
included with Python in many environments
simple to start
works on Windows/Linux/macOS
reasonable for small tools
good for legacy systems

Weaknesses:
not visually modern by default
dockable interfaces are not natural
complex layouts can become awkward
high-DPI polish requires care
not ideal for mobile/touch
not ideal for high-performance live plotting

Use Tkinter when:
the app is small
dependencies must be minimal
the target is old or constrained
the UI is mostly forms and buttons

Avoid Tkinter when:
the app needs complex dockable panels
professional DAQ interface behavior
large live plots
modern styling
tablet/mobile touch behavior

2.2 ttk / ttkbootstrap / customtkinter
These improve the look of Tkinter-style apps.
Best for:
simple modernized desktop tools
forms
small dashboards
configuration utilities
beginner-friendly apps

Strengths:
easier to make Tkinter look better
still simpler than Qt
good for small-to-medium tools

Weaknesses:
still not as powerful as Qt
complex dockable interfaces remain awkward
not ideal for heavy plotting/control systems
platform differences still exist

Use these when:
a plain Tkinter app is enough but should look less old-fashioned

2.3 PyQt / PySide
PyQt and PySide are Python bindings for Qt.
In modern work:
PySide6 = official Qt for Python binding
PyQt5 / PyQt6 = widely used alternative bindings

Best for:
serious desktop applications
engineering tools
DAQ/control software
dockable panels
menus/toolbars/status bars
settings persistence
large forms
tables
plots
multi-panel interfaces
instrument-control GUIs
professional operator consoles

Strengths:
mature desktop framework
excellent widgets
dockable panels
menus and toolbars
status bars
settings through QSettings
threading patterns through signals/slots
good for complex apps
good for our DAQ/control style

Weaknesses:
larger dependency
version compatibility matters
packaging can be more complex
not ideal on Pydroid
not appropriate for Windows XP unless using old PyQt4-style stack
can become over-engineered if used for tiny tools

Use Qt when:
the app needs to feel like real software
the user needs many panels
the app controls hardware
the app plots live data
the app needs persistent settings/layouts
the app needs a professional long-term structure

Avoid Qt when:
the project is a tiny one-file script
the target is Pydroid
the target is old Windows XP without a known installed Qt stack
the app is just a game/simulation canvas

2.4 Kivy
Kivy is a Python GUI framework designed around multi-touch and cross-platform interactive apps.
Best for:
Android/Pydroid apps
touchscreen apps
tablet interfaces
phone interfaces
large touch buttons
simple dashboards
interactive controls
mobile-first tools
Raspberry Pi touchscreen apps

Strengths:
touch-friendly
works conceptually across desktop and Android
good for large controls
good for phone/tablet UI
better fit for Pydroid than Qt
supports gestures and mobile-style interaction

Weaknesses:
not native desktop widgets
layout behavior differs from desktop frameworks
packaging to Android APK is a separate workflow
can show black-screen/log issues on Android if imports or graphics fail
desktop-to-phone sizing often needs work
not as natural for dense engineering desktop apps

Use Kivy when:
the app is touch-first
the app targets Android/Pydroid
the app targets a small touchscreen
the interface is buttons/sliders/status panels

Avoid Kivy when:
the app needs native desktop menus/docking/tables
the app is a high-performance 2D simulation canvas
the app is intended only for Windows engineering desktop use

2.5 Pygame
Pygame is for multimedia, games, simulations, and canvas-style interactive programs.
Best for:
games
particle simulations
falling-rain simulations
touch/click canvas apps
2D visualization
teaching demos
interactive physics toys
animated experiments

Strengths:
direct control over drawing
simple game loop
good for motion and collisions
good for simulations
works well for one-canvas visual programs
fast enough for many 2D experiments

Weaknesses:
not a normal widget toolkit
menus/forms/tables are manual
text input is awkward
desktop GUI features are not built in
professional settings dialogs are not natural

Use Pygame when:
the main interface is the animated canvas
objects move and collide
the user explores a simulation visually

Avoid Pygame when:
the app is mostly forms
the app needs dockable panels
the app needs lots of tables/settings dialogs

2.6 Web GUI
A web GUI means the Python backend serves a browser interface.
Common stack:
Flask or FastAPI backend
HTML/CSS/JavaScript frontend
browser as GUI

Best for:
remote dashboards
Raspberry Pi web interfaces
phone-accessible monitoring pages
multi-device viewing
local network tools
simple control/status pages

Strengths:
viewable from phone/laptop/tablet
works over network
good for Raspberry Pi headless tools
separates backend from display
no desktop GUI installation needed on viewer device

Weaknesses:
web frontend adds another language/tooling layer
real-time updates need polling/websockets/MQTT/etc.
browser compatibility matters
safety-critical controls need careful design
not ideal for offline standalone desktop apps unless packaged carefully

Use web GUI when:
the data should be viewed remotely
multiple devices should view the same system
the Raspberry Pi is headless
phone viewing matters

Avoid web GUI when:
the app must be a native offline desktop tool
the user needs rich dockable engineering panels
the control loop must not depend on browser behavior

2.7 Streamlit / Dash / Gradio-style Apps
These are higher-level web app frameworks.
Best for:
quick data dashboards
analysis tools
plots
internal demos
simple parameter controls

Strengths:
fast to build
good for data visualization
little frontend code

Weaknesses:
less control over professional operator UI
not ideal for hardware safety
not ideal for complex local desktop behavior
can become awkward for custom interaction

Use these for analysis dashboards, not as the default for hardware-control operator software.

2.8 wxPython
wxPython is a mature desktop GUI toolkit.
Best for:
native-ish desktop apps
legacy GUI projects
cross-platform desktop tools

Strengths:
native widget style
mature desktop toolkit

Weaknesses:
less common in our current workflow
not our standard style
packaging/version issues still exist

Use only when there is a clear reason or existing codebase.

3. Platform Compatibility Summary
3.1 Modern Windows
Good choices:
PySide6 / PyQt5 / PyQt6
Tkinter
Kivy
Pygame
Flask/FastAPI web UI
Streamlit/Dash for analysis

Preferred for serious engineering tools:
PyQt/PySide

Preferred for simulations:
Pygame

Preferred for phone-like touchscreen prototypes:
Kivy

3.2 Windows XP / Python 2.7 Legacy
Likely choices:
Tkinter
PyQt4, if already installed
old matplotlib
old Pygame
known-good legacy packages

Avoid:
PySide6
PyQt6
modern PyQt5
modern Kivy
modern Pygame
modern pip assumptions
modern type hints / f-strings / pathlib

XP rule:
Use the actual installed stack.
Do not design around modern Python packages.
Keep GUI code simple and explicit.

3.3 Raspberry Pi Desktop
Good choices:
Tkinter
Kivy
Pygame
PyQt5/PySide, if installed and performance is acceptable
web UI

For small touchscreen:
Kivy or Tkinter

For graph-heavy DAQ:
PyQt/PySide or Tkinter + matplotlib, depending on hardware

For lightweight monitoring:
web UI

Pi caveats:
limited CPU/GPU compared with desktop
screen resolution may be small
touch calibration matters
OpenGL/Kivy issues can happen
matplotlib live plotting can be slow
avoid excessive redraws

3.4 Android / Pydroid
Good choices:
Kivy
Pygame, for canvas/game/simulation
console scripts
simple web clients

Usually avoid:
PyQt/PySide
desktop Tkinter assumptions
desktop file paths
right-click behavior
tiny controls
keyboard-required workflow

Pydroid rule:
Tell the AI and the code that the target is Pydroid on Android before code is written.

3.5 Web Browser / Phone Viewer
Good choices:
Flask or FastAPI backend
simple HTML dashboard
MQTT/HTTP data viewer

Best for:
remote Raspberry Pi dashboards
sensor monitors
phone/tablet viewing
headless devices

Caveat:
A web dashboard is good for monitoring.
Be more careful if it can command hardware.

4. Our GUI Design Philosophy
Our GUI style is operator-focused, diagnostic-heavy, and designed to preserve function over appearance.
The interface should:
make the current system state obvious
make dangerous actions deliberate
keep safe-state controls visible
preserve data
show diagnostics
make errors recoverable
avoid hiding important state
remember layout/settings
support long-running use

The GUI is successful when the user can answer:
What is connected?
What is running?
What is being measured?
What is being controlled?
What is the current state?
What changed recently?
Is the data being saved?
Is anything faulted?
How do I stop safely?
Where are the logs?

5. Our Standard Engineering GUI Layout
For serious desktop engineering tools, use this pattern:
Top menu bar
    File | View | Settings | Tools | Help

Persistent top/status strip
    connection state
    run state
    data-save state
    last event timestamp
    warnings/errors

Main central area
    graph / live display / primary workspace

Dockable side panels
    Inputs
    Outputs
    Results
    Controls
    Logs
    Diagnostics
    Settings

Bottom status bar
    backend status
    file path
    queue sizes
    telemetry age
    last error

For DAQ/control tools:
Safe State Now button should be visible from all main screens.

For viewers/analyzers:
Open File, Export, Reset View, Diagnostics should be obvious.

For touchscreen/mobile apps:
Use fewer panels.
Use large buttons.
Use one screen at a time.
Use simple navigation.

6. Dockable Panels
Dockable panels are important for complex engineering tools.
Typical panels:
Inputs
Outputs
Controls
Graph Settings
Trace List
Alarms
Sequence Preview
Logs
Diagnostics
Data Export
Device Explorer
Signal Explorer

Rules:
Panels should be movable when framework supports it.
Panels should be hideable/showable from the View menu.
Panel layout should be restorable to default.
Panel sizes should persist between sessions.
The main graph/workspace should not be permanently squeezed.

Best framework for this:
PyQt/PySide

Tkinter/Kivy/Pygame can imitate panels, but true dockable professional panel behavior is much more natural in Qt.

7. Settings Persistence
A serious GUI should remember:
window size
window position
dock layout
visible panels
trace visibility
trace colors
font scale
theme
recent files
autosave preference
last used folder
selected device/profile
plot time window

Qt preferred mechanism:
QSettings

General fallback:
settings.json

Rule:
The user should not have to rebuild their workspace every time the program opens.

8. Screen Size and DPI Rules
Problems we have repeatedly seen:
buttons off-screen
panels too large
text too small
text too large
phone layout copied from desktop
desktop layout copied from phone
Raspberry Pi touchscreen squeezed
high-DPI Windows scaling breaks fixed pixel sizes
graphs crush the controls
controls crush the graph

Rules:
Detect screen size.
Use relative layout where possible.
Use scroll areas for long forms.
Use resizable panels.
Set reasonable minimum sizes.
Avoid fixed 1920x1080 assumptions.
Avoid fixed phone-only assumptions.
Provide UI scale setting.
Persist UI scale.

For desktop apps:
start at about 80 percent of screen width/height
center the window
allow resize
remember size next time

For touchscreen apps:
large touch targets
large fonts
minimal typing
avoid hover/right-click

9. Scrolling Rules
Any form longer than the screen must scroll.
Use scroll areas for:
settings forms
long device configuration
channel maps
calibration entries
large lists of traces
logs
diagnostic output

Rule:
If a user cannot reach a control because the screen is too small, the GUI is broken.

10. Graphing Rules
For engineering graphing:
plot area should be the main visual focus
trace names should be clear
units should be visible
axis units should auto-scale sensibly
time axes should not show awkward ksec labels if min/hr/day is clearer
trace visibility should be controllable
selected trace should stand out
alarms should be visually obvious
raw vs decimated data must be labeled

Common graph modes:
live sliding window
entire history
paused/explore mode
post-run viewer
exported plot

Rules:
Sliding window should show actual recent data.
Entire history may decimate for performance, but must say so.
Decimation should not contaminate sliding-window mode.
User should be warned before plotting extremely dense raw data.

Best tools:
PyQtGraph for fast Qt live plots
matplotlib for reports/static plots/moderate live plots
Pygame for custom simulation visuals
browser plotting for web dashboards

11. Threading and GUI Safety
Do not block the GUI thread.
Bad:
GUI button directly reads slow hardware.
GUI thread waits on serial/network/hardware.
GUI freezes during file open.
GUI directly runs long analysis.

Better:
GUI thread
    → command queue
        → worker/backend thread
            → result/event queue
                → GUI updates safely

For Qt:
use signals/slots or queued updates

For Kivy:
use Clock.schedule_interval or Clock.schedule_once for UI updates

For Tkinter:
use root.after to poll queues

For Pygame:
poll queues inside main loop

Rule:
Worker threads may collect data.
Only the GUI/main thread should update GUI widgets.

12. Diagnostics Are Part of the GUI
A serious GUI should have a diagnostics area or menu item.
Minimum diagnostics:
Python version
package versions
platform/OS
screen size
DPI or scale if available
window geometry
settings path
log path
data path
connected devices
backend process state
queue sizes
last telemetry timestamp
last command timestamp
last error
autosave state

A diagnostics button should write a file the user can copy back.
Example diagnostic output:
diagnostics/gui_diagnostic_report.txt

Rule:
If the GUI fails on a target machine, it should help explain why.

13. Menus We Usually Want
Standard desktop menu:
File
    New
    Open
    Save
    Save As
    Export CSV
    Export PNG
    Recent Files
    Exit

View
    Show/Hide Panels
    Reset Layout
    Full Screen
    UI Scale
    Theme

Settings
    Preferences
    Device Settings
    Plot Settings
    Autosave
    Data Storage
    Safety Behavior

Tools
    Diagnostics
    Smoke Test
    Device Scan
    Export Logs
    Open Data Folder

Help
    User Guide
    Keyboard Shortcuts
    About

For small touchscreen/mobile apps, use fewer menus and more large buttons.

14. Our Visual Style
Preferred general style:
dark navy base
thin lighter-blue accents
clear white/light text
strong contrast
rounded cards only where helpful
not overly decorative
status colors used consistently

Status colors conceptually:
green = connected/good/running
yellow = warning/attention
red = fault/danger/stopped unsafe
blue = informational/selected/control
gray = disabled/inactive

Do not rely on color alone.
Also use:
text labels
icons
border changes
status messages
tooltips

15. Touchscreen Design Principles
Touchscreen apps need a different design than desktop apps.
Rules:
large buttons
large fonts
large spacing
no tiny checkboxes
no hover-only behavior
no right-click-required behavior
minimal text input
clear back/quit buttons
simple screens
scrollable long content

For phones/Pydroid:
assume portrait or handle rotation
assume keyboard may cover the screen
assume no mouse
assume limited screen space

For Raspberry Pi touchscreens:
detect resolution
provide UI scale
make scroll areas large
avoid tiny controls
test on the actual screen

16. Pydroid-Specific GUI Rules
When targeting Pydroid:
say Pydroid 3 on Android before code is written
prefer Kivy for touch UI
prefer Pygame for canvas/simulation
avoid PyQt/PySide
avoid desktop file paths
include a Quit button
include startup diagnostics
write errors to a text file
detect screen size
use large controls
keep first pass single-file

Common Pydroid failure patterns:
black screen
missing package
desktop GUI library used accidentally
fixed desktop resolution
keyboard/mouse assumptions
blocking loop freezes UI
file path invalid
touch regions too small

Correct AI prompt language:
This must run in Pydroid 3 on Android.
Use Kivy for touch UI or Pygame for canvas simulation.
Keep it single-file.
Detect screen size.
Use large touch controls.
Add diagnostics and error logging.
Avoid PyQt/PySide.
Do not assume desktop paths.

17. Raspberry Pi GUI Rules
For Raspberry Pi:
test on actual Pi model
test on actual display
avoid excessive redraws
avoid huge live plots
use modest default resolution
use hardware-friendly dependencies
include a headless mode when possible

Recommended patterns:
Tkinter for simple local tools
Kivy for touch-first Pi interfaces
PyQt/PySide for richer tools if performance/dependencies are acceptable
web dashboard for headless/remote monitoring
Pygame for simulations or simple canvas displays

For DAQ/logger Pi tools:
data acquisition should keep running even if the GUI stutters
writer thread should protect data
GUI should show telemetry age and save state

18. Windows XP GUI Rules
For XP/Python 2.7:
use known-good installed stack
avoid modern dependencies
avoid modern syntax
prefer simple layouts
prefer Tkinter or PyQt4 if available
avoid high-DPI assumptions
avoid modern web/front-end build tools

Do not give XP code:
f-strings
type annotations
dataclasses
pathlib
PyQt6/PySide6
modern Kivy assumptions
modern Pygame assumptions

XP UI should prioritize:
clarity
large enough fonts
simple menus
basic logging
basic diagnostics
graceful failure

19. GUI Architecture for Serious Apps
Preferred architecture:
main.py
    launches app

ui/
    windows, widgets, dialogs, panels

core/
    business logic, calculations, state machine

devices/
    hardware adapters

storage/
    CSV, SQLite, settings, autosave

diagnostics/
    diagnostic reports

tests/
    smoke tests and acceptance checks

Rule:
The GUI should not own the truth.

The GUI displays state and requests actions.
The backend/core owns:
device state
data storage
safety rules
control logic
diagnostics

20. Prototype vs Formal GUI
20.1 Prototype GUI
A prototype GUI can be:
single file
quick layout
minimal settings
manual controls
simple graph
basic diagnostics

Purpose:
prove behavior
test interaction
learn requirements
discover layout problems

20.2 Formal GUI
A formal GUI should have:
module structure
settings persistence
logs
diagnostics
safe shutdown
acceptance tests
clear file layout
user guide
error handling
state save/restore

Rule:
Do not pretend a prototype is production.
Do not over-formalize before behavior is understood.

21. Avoiding Interface Drift
Common problem:
A new version fixes one thing but removes old working features.

Prevention:
freeze public method/class names early
keep a golden runnable baseline
maintain a feature checklist
use smoke tests
use compatibility shims during refactors
record changed files/classes/methods
do not remove features unless explicitly requested

For GUI updates, maintain a checklist:
menus still exist
safe-state button still visible
plots still work
settings still persist
diagnostics still run
autosave still works
open/save still works
all panels still accessible

22. GUI Diagnostic Harness
Every serious GUI should have a diagnostic mode.
Example command:
python main.py --diagnostics

or menu:
Tools → Diagnostics → Write Diagnostic Report

Diagnostic report should include:
app version
Python version
OS/platform
GUI framework/version
screen size
DPI/scale
window geometry
settings file path
data folder path
log folder path
available devices
backend connection state
last errors
recent events

For cross-platform GUI work, this is not optional.
It is how we debug machines we cannot directly inspect.

23. GUI Smoke Tests
Minimum GUI smoke tests:
launch app
close app cleanly
open diagnostics
write diagnostic report
resize window
open each panel
hide/show each panel
reset layout
save settings
restart app
confirm settings restored
open sample data or simulation
export CSV/PNG if supported

Hardware GUI smoke tests:
launch with hardware disconnected
show disconnected state
connect hardware
show connected state
start simulated acquisition
stop acquisition
safe-state command works
close app safely

24. GUI Acceptance Gates
A GUI is acceptable when:
it starts reliably
it exits cleanly
it does not freeze during normal operations
it scales to the target screen
important controls are reachable
settings persist
errors are visible
logs are written
diagnostics are available
data is not lost
safe-state behavior works if hardware is involved

For touchscreen apps:
all controls are finger-sized
no keyboard/mouse-only actions are required
orientation/resolution issues are handled

For desktop engineering apps:
menus are complete
dock panels work
plots are readable
status is always visible

25. Framework Decision Guide
Use this decision guide:
Need a serious desktop engineering app?
    Use PyQt/PySide.

Need a simple low-dependency desktop utility?
    Use Tkinter.

Need a phone/tablet/Pydroid touch app?
    Use Kivy.

Need a 2D game or simulation?
    Use Pygame.

Need a Raspberry Pi headless dashboard?
    Use web UI.

Need a quick data analysis dashboard?
    Consider Streamlit/Dash-style approach.

Need Windows XP support?
    Use the known installed legacy stack; usually Tkinter/PyQt4/old Pygame.

26. Standard GUI Planning Checklist
Before writing GUI code, answer:
Target platform:
    Windows / XP / Raspberry Pi / Pydroid / browser / other

Primary interaction:
    mouse/keyboard / touchscreen / remote browser / hardware operator

Main purpose:
    data entry / plotting / control / simulation / monitoring / configuration

Framework:
    Tkinter / PyQt/PySide / Kivy / Pygame / Web / other

Screen:
    expected resolution
    DPI/scaling
    portrait/landscape
    resizable?

Data:
    what is displayed?
    what is saved?
    what is exported?

Safety:
    can the GUI command hardware?
    what is the safe stop behavior?
    what happens on close?

Diagnostics:
    how does the user report failures?

Persistence:
    what settings/layouts are remembered?

27. Standard AI Prompt for GUI Code
Use this when asking an AI for GUI code:
Write Python GUI code for this target:

Target platform:
[Windows / Raspberry Pi / Pydroid Android / Windows XP / browser]

Preferred framework:
[PySide6 / PyQt5 / Tkinter / Kivy / Pygame / Flask]

Requirements:
- detect screen size
- use resizable layout
- include scroll areas for long forms
- include clear status area
- include diagnostics button/report
- include error logging
- preserve existing features
- do not remove menus or panels
- keep hardware operations out of the GUI thread
- include safe shutdown behavior if hardware is involved
- include a simple smoke-test or diagnostic harness

For Pydroid:
This must run in Pydroid 3 on Android.
Use Kivy or Pygame.
Avoid PyQt/PySide.
Use large touch controls.
Keep it single-file for the first pass.

For XP:
This must run on Windows XP with Python 2.7.
Avoid modern Python syntax.
Avoid modern GUI dependencies.
Use the known installed legacy stack.

28. Common GUI Failure Modes
28.1 Window opens too large
Fix:
detect screen size
start at 80 percent of screen
allow resize
wrap content in scroll area

28.2 Controls are off-screen
Fix:
scroll area
split into tabs
reduce default panel height
use responsive layout

28.3 App freezes
Likely cause:
blocking hardware/network/file operation in GUI thread

Fix:
use worker thread/process
use queues/signals
update GUI only on main thread

28.4 Works on desktop but fails on Pydroid
Likely cause:
desktop GUI framework
desktop path
screen-size assumption
mouse/keyboard assumption
missing package

Fix:
target Pydroid explicitly
use Kivy/Pygame
single-file first pass
add diagnostics

28.5 Works on one screen but not another
Likely cause:
fixed pixel layout
DPI scaling
font size assumptions

Fix:
relative sizing
UI scale setting
scrolling
test at multiple resolutions

28.6 Feature disappeared after rewrite
Likely cause:
rewrite not anchored to current code
no feature checklist
no smoke tests

Fix:
freeze feature list
compare old/new
preserve public APIs
use compatibility layer

29. Our GUI Definition of Done
A GUI is done enough for first release when:
[ ] launches without error
[ ] closes safely
[ ] resizes correctly
[ ] important controls remain reachable
[ ] status area is always visible
[ ] errors are visible and logged
[ ] diagnostics report can be written
[ ] settings persist
[ ] layout can reset
[ ] data can be saved/exported if applicable
[ ] hardware actions are not performed on GUI thread
[ ] safe shutdown exists if hardware is controlled
[ ] target platform was actually tested

30. Core Rules
RULE-GUI-001
Choose the GUI framework based on target platform and interaction style.

RULE-GUI-002
Do not use desktop GUI assumptions on phones.

RULE-GUI-003
Do not use phone/touch assumptions for dense engineering desktop tools.

RULE-GUI-004
The GUI should display state, not secretly own system truth.

RULE-GUI-005
Never block the GUI thread with slow hardware, network, or file operations.

RULE-GUI-006
Use diagnostics early.

RULE-GUI-007
Use screen-size detection and scrollable layouts.

RULE-GUI-008
Preserve working features during rewrites.

RULE-GUI-009
For serious engineering apps, prefer dockable panels and persistent settings.

RULE-GUI-010
For hardware-control apps, safe-state access must be obvious and persistent.

31. Closing Principle
The GUI is the operator’s mental model of the system.
A good GUI does not merely look nice. It makes the system understandable, controllable, diagnosable, and safe.
Our standard GUI progression is:
simple prototype
    → working interaction
        → diagnostics
            → layout refinement
                → settings persistence
                    → threading/safety cleanup
                        → packaging and acceptance tests

For small simulations and games, the GUI can be playful.
For hardware and DAQ systems, the GUI must be trustworthy.
The design goal is always the same:
The user should know what is happening,
what the system is doing,
what data is being saved,
what failed,
and how to stop safely.
