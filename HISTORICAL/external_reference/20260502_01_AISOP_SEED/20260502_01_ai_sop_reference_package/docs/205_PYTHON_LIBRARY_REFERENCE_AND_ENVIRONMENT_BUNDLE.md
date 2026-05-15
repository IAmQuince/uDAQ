---
document_id: DOC-205
title: "Python Library Reference and Environment Bundle"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-205
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Python Library Reference and Environment Bundle

This section defines a reusable Python environment bundle and library reference for AI-assisted coding projects.
It includes:
README_START_HERE.md
RUN_INSTRUCTIONS.md
KNOWN_LIMITATIONS.md
PACKAGE_MANIFEST.txt
library_manifest.json

tools/
├── ai_toolkit_installer.py
├── ai_toolkit_diagnostic.py
└── ai_toolkit_xp_py27_reference_check.py

requirements/
├── requirements_modern_core.txt
├── requirements_data_science.txt
├── requirements_gui_modern.txt
├── requirements_daq_control.txt
├── requirements_qc_defect.txt
├── requirements_web_tools.txt
├── requirements_office_files.txt
├── requirements_cad_mesh.txt
├── requirements_audio_midi.txt
├── requirements_raspberry_pi.txt
├── requirements_pydroid_reference.txt
├── requirements_xp_reference.txt
├── requirements_dev_tools.txt
└── requirements_everything_modern.txt

docs/
├── AI_TOOLKIT_LIBRARY_REFERENCE.md
└── AI_TOOLKIT_PROFILES.md

Basic use:
python tools/ai_toolkit_installer.py --list-profiles
python tools/ai_toolkit_installer.py --action diagnostic
python tools/ai_toolkit_installer.py --profile modern_core --action install

Broad modern install:
python tools/ai_toolkit_installer.py --profile everything_modern --action install

Offline wheel download:
python tools/ai_toolkit_installer.py --profile daq_control --action download --wheelhouse wheelhouse_daq

Then on the offline machine:
python -m pip install --no-index --find-links=wheelhouse_daq -r requirements/requirements_daq_control.txt

Important caveat: this is not a universal one-click installer for XP, Raspberry Pi, and Pydroid. Python packaging officially supports requirements files as lists of pip install arguments, and venv/pip workflows are the standard modern approach, but target environments still matter heavily. (Python Packaging)
For Windows XP / Python 2.7, use the included reference diagnostic instead of the modern installer:
python tools\ai_toolkit_xp_py27_reference_check.py

The current library list is best-effort based on our project history. It includes DAQ/control, LabJack, PyVISA, QC/defect detection, GUI, plotting, Raspberry Pi, Pydroid, CAD/meshing, office-file generation, web/download tools, MIDI/audio, diagnostics, and dev tooling.

# AI Coding Toolkit Python Library Reference — Installable Third-Party Libraries

pip — Python package installer used to install packages from PyPI, local wheels, source folders, and requirements files.

setuptools — Build/install support library used by many Python packages.

wheel — Builds and installs Python wheel packages, useful for offline bundles.

virtualenv — Creates isolated Python environments, especially useful where modern venv is unavailable.

numpy — Core numerical array library for calculations, simulation, signal processing, image arrays, and plotting pipelines.

scipy — Scientific computing library for optimization, interpolation, signal processing, statistics, and numerical methods.

pandas — Table/dataframe library for CSV/SQLite analysis, exports, and QC/performance correlation.

python-dateutil — Date/time parsing and relative date utilities.

pytz — Time-zone definitions used by older datetime and pandas workflows.

sympy — Symbolic math library for derivations, algebra, calculus, and equation manipulation.

statsmodels — Statistical modeling package for regression, time-series analysis, and experimental data analysis.

scikit-learn — Machine-learning and statistical modeling toolkit for classifiers, clustering, anomaly detection, and QC analysis.

matplotlib — General plotting library used for live graphs, reports, exports, and engineering plots.

pyqtgraph — Fast plotting widgets for Qt applications, useful for responsive live DAQ graphing.

plotly — Interactive plotting library for browser-based charts and exploratory analysis.

bokeh — Interactive web plotting/server visualization library.

PyQt5 — Qt GUI binding for modern desktop apps with dockable panels, menus, status bars, and complex interfaces.

PySide6 — Official Qt for Python binding for modern Qt6 GUI applications.

customtkinter — Modern themed layer over Tkinter for simpler desktop GUIs.

ttkbootstrap — Themed ttk/Tkinter widgets for more polished standard-library-style GUIs.

kivy — Cross-platform GUI framework used for Android/Pydroid touchscreen apps and experimental visual tools.

pygame — 2D graphics/game/simulation library used for particle simulations and interactive visual prototypes.

Pillow — Image loading, saving, conversion, cropping, thumbnails, and simple annotations.

opencv-python — Computer vision library for image processing, camera frames, thresholding, contours, and defect detection.

scikit-image — Image-processing algorithms useful for measurements, segmentation, filters, and analysis.

imageio — Read/write images and some video formats.

pyserial — Serial port communication for Arduino, ESP32, instruments, and microcontroller bridges.

pyvisa — VISA instrument-control interface used for SCPI devices such as programmable power supplies and lab instruments.

pyvisa-py — Pure-Python VISA backend for PyVISA for some USB/LAN/GPIB instrument workflows.

LabJackPython — LabJack Python library for U3/U6-era devices; historically exposes modules such as u3 and u6.

labjack-ljm — LabJack LJM Python package for newer T-series devices.

paho-mqtt — MQTT client for Raspberry Pi/ESP32 sensor networks and lightweight telemetry messaging.

pyzmq — ZeroMQ bindings used for frontend/backend messaging patterns in DAQ/control apps.

psutil — System diagnostics such as CPU, memory, process, disk, and process health info.

requests — HTTP client used for downloads, APIs, and web requests.

beautifulsoup4 — HTML/XML parsing helper for scraping, local archive processing, and extracting links/content.

lxml — Fast XML/HTML parser used by BeautifulSoup and document/web parsing workflows.

selenium — Browser automation toolkit for websites that require real browser interaction.

Flask — Lightweight local web app/server framework.

waitress — Pure-Python WSGI server for serving Flask/Wsgi apps locally.

tqdm — Progress bars for downloads, batch processing, and command-line utilities.

openpyxl — Read/write modern Excel .xlsx files.

XlsxWriter — Create Excel .xlsx reports with formatting/charts.

python-docx — Create and edit Word .docx documents.

python-pptx — Create and edit PowerPoint .pptx presentations.

reportlab — Programmatic PDF generation.

PyPDF2 — PDF reading, splitting, and merging utilities.

pypdf — Modern PDF manipulation library for reading, splitting, and merging PDFs.

PyYAML — Read/write YAML configuration files.

platformdirs — Cross-platform user config/cache/data folder locations.

appdirs — Older cross-platform app directory helper.

gmsh — Python API for Gmsh mesh generation.

meshio — Read/write many mesh formats, useful for converting meshes between tools.

numpy-stl — Read/write STL files using NumPy arrays.

trimesh — 3D mesh loading, inspection, repair helpers, and geometry utilities.

pyvista — 3D visualization and mesh analysis based on VTK.

mido — MIDI message parsing and sending, useful for controllers and MIDI experiments.

python-rtmidi — Realtime MIDI backend used by mido for hardware MIDI ports.

sounddevice — Audio input/output via PortAudio for signal/audio experiments.

soundfile — Read/write audio files via libsndfile.

watchdog — Monitor filesystem changes for auto-refresh/reload workflows.

rich — Pretty terminal output, tables, tracebacks, and progress displays.

pytest — Testing framework for unit, smoke, and acceptance tests.

black — Python code formatter.

ruff — Fast Python linter/formatter useful for modern code quality checks.

# Built-In Python Standard Library Modules We Commonly Use

os — Filesystem paths, directories, environment variables, and process utilities.

sys — Python runtime information, command-line args, exit codes, and import path behavior.

time — Timestamps, sleeps, timing loops, and simple elapsed-time logic.

datetime — Human-readable timestamps and date/time objects.

json — JSON settings, manifests, configuration, and runtime state files.

csv — CSV logging, exports, imports, and lightweight data exchange.

sqlite3 — Local SQLite database/historian storage.

threading — Worker threads, Events, Locks, and deterministic shutdown coordination.

queue / Queue — Thread-safe queues for telemetry, commands, database writes, and GUI updates.

subprocess — Running external tools, scripts, diagnostics, and package commands.

traceback — Capturing useful exception reports.

logging — Application logs, fault logs, command logs, and diagnostics.

argparse — Command-line flags such as --diagnostics, --smoke-test, and --safe-mode.

shutil — Copying files, backups, folder operations, and package preparation.

tempfile — Temporary files/folders for atomic-ish writes and diagnostics.

hashlib — File hashes for evidence integrity, package checks, and audit trails.

uuid — Stable unique IDs for runs, detections, defects, evidence, and records.

platform — OS/platform diagnostics.

socket — Basic networking and device communication checks.

signal — Graceful handling of Ctrl+C, SIGTERM, and shutdown events.

atexit — Last-chance cleanup and shutdown hooks.

collections — deque and structured containers for graph buffers and runtime state.

math — Basic math functions for simulation, signal generation, and calculations.

random — Simulated data, randomized tests, and prototype behavior.

re — Regular expressions for parsing, validation, and cleanup.

glob — File matching for scans, imports, and batch operations.

configparser — INI-style configuration files, especially for legacy/simple tools.

io — Text/binary file handling with encoding control.

zipfile — Creating and inspecting zip packages.

pathlib — Modern path handling; avoid for Windows XP/Python 2.7 targets.

unittest — Built-in test framework for simple compatibility tests.

http.server / SimpleHTTPServer — Local test servers and simple offline web serving.

tkinter / Tkinter — Built-in GUI toolkit for simple desktop interfaces.

multiprocessing — Separate processes where threads are not appropriate.

enum — Named constants and state definitions; modern Python only unless backported.

dataclasses — Lightweight structured data classes; modern Python only.

Pygame
