---
document_id: DOC-055
title: "Monolithic Prototype Code Example"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-055
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Monolithic Prototype Code Example

from __future__ import print_function

# =============================================================================
# PROJECT:
# FILE:
# DATE:
# PHASE: Monolithic prototype / exploratory implementation
# TARGET RUNTIME:
# TARGET OS:
# AUTHOR/AGENT:
#
# PURPOSE:
# This file is an intentionally monolithic prototype used for early workflow,
# UI, data-handling, device, visualization, or architecture testing.
#
# CURRENT STATUS:
# Draft / runnable / partially tested / accepted prototype / superseded
#
# IMPORTANT:
# This file is intentionally monolithic for early testing.
# It is not the final architecture.
# If accepted, it should be split later according to the project module-boundary
# document and acceptance-tested after each extraction.
#
# DO NOT REMOVE WITHOUT APPROVAL:
# - Existing user workflows
# - Existing UI controls
# - Existing data fields
# - Existing settings/state persistence
# - Existing diagnostics and smoke-test behavior
# - Existing safe-state / shutdown behavior, if hardware is involved
#
# KNOWN LIMITATIONS:
# - This is a prototype scaffold.
# - Project-specific data model, UI, device, and workflow logic must be filled in.
# - Hardware-specific behavior must start safe and fail safe.
#
# EXTRACTION TARGETS:
# - compatibility helpers      -> project/compat.py
# - paths/settings/logging     -> project/paths.py, project/settings.py, project/logging.py
# - data model/defaults        -> project/model.py
# - storage/load/save          -> project/storage.py
# - scanning/import/parsing    -> project/scanner.py
# - business logic/actions     -> project/actions.py
# - UI/view rendering          -> project/ui/*.py or project/views/*.py
# - diagnostics/smoke tests    -> project/diagnostics.py and tools/diagnostic_harness.py
# - entry point                -> main.py
# =============================================================================

# =============================================================================
# 1. IMPORTS AND COMPATIBILITY
# =============================================================================

import os
import sys
import json
import time
import shutil
import tempfile
import traceback
import platform
import argparse

try:
    import io
except ImportError:
    io = None

IS_PY2 = sys.version_info[0] == 2
IS_PY3 = sys.version_info[0] == 3

def ensure_text(value):
    """
    Centralized text conversion.

    Keep this boring and conservative.
    This is an early extraction candidate for project/compat.py.
    """
    if value is None:
        return u""

    if IS_PY2:
        try:
            basestring_type = basestring
        except NameError:
            basestring_type = str

        if isinstance(value, unicode):  # noqa: F821  # Python 2 only
            return value
        if isinstance(value, str):
            try:
                return value.decode("utf-8")
            except Exception:
                return value.decode("utf-8", "replace")
        return unicode(value)  # noqa: F821  # Python 2 only

    if isinstance(value, bytes):
        return value.decode("utf-8", "replace")
    return str(value)

def ensure_bytes(value):
    """
    Centralized byte conversion.

    Useful for legacy paths, serial devices, sockets, and older APIs.
    """
    if value is None:
        return b""

    if IS_PY2:
        if isinstance(value, str):
            return value
        try:
            return value.encode("utf-8")
        except Exception:
            return str(value)

    if isinstance(value, bytes):
        return value
    return ensure_text(value).encode("utf-8")

def safe_makedirs(path):
    """
    Create a directory if it does not exist.
    Safe for repeated calls.
    """
    if not path:
        return
    if not os.path.isdir(path):
        os.makedirs(path)

def now_iso():
    """
    Local timestamp suitable for logs and JSON records.
    """
    return time.strftime("%Y-%m-%d %H:%M:%S")

def safe_repr(value):
    try:
        return repr(value)
    except Exception:
        return "<unrepresentable value>"

# =============================================================================
# 2. CONSTANTS AND VERSION INFO
# =============================================================================

APP_NAME = "ProjectName"
APP_VERSION = "yyyymmdd_00_projectname_monolithic_prototype"
APP_PHASE = "monolithic_prototype"
SCHEMA_VERSION = 1

DEFAULT_SETTINGS_FILENAME = "settings.json"
DEFAULT_STATE_FILENAME = "state.json"
DEFAULT_LOG_FILENAME = "prototype.log"
DEFAULT_DIAGNOSTIC_FILENAME = "diagnostic_report.txt"

# Centralize magic strings here.
STATUS_DRAFT = "draft"
STATUS_RUNNABLE = "runnable"
STATUS_PARTIALLY_TESTED = "partially_tested"
STATUS_ACCEPTED_PROTOTYPE = "accepted_prototype"
STATUS_SUPERSEDED = "superseded"

APP_STATUS = STATUS_DRAFT

# Project-specific allowed values go here.
ITEM_STATUSES = [
    "untested",
    "tested",
    "broken",
    "unsupported",
]

ITEM_KINDS = [
    "unknown",
    "data",
    "device",
    "media",
    "measurement",
    "configuration",
    "other",
]

def get_app_info():
    """
    Single source of truth for app identity.

    Diagnostics, UI, logs, and reports should use this rather than duplicating
    labels manually.
    """
    try:
        file_path = os.path.abspath(__file__)
    except Exception:
        file_path = "<unknown>"

    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "phase": APP_PHASE,
        "status": APP_STATUS,
        "schema_version": SCHEMA_VERSION,
        "file": file_path,
        "python_version": sys.version,
        "platform": platform.platform(),
    }

# =============================================================================
# 3. PATHS, SETTINGS, AND LOGGING
# =============================================================================

def get_app_dir():
    """
    Directory containing this prototype file.
    """
    try:
        return os.path.dirname(os.path.abspath(__file__))
    except Exception:
        return os.getcwd()

def get_appdata_dir():
    """
    Package-local runtime data folder.

    For early prototypes, package-local AppData is convenient and portable.
    Later, this can be changed deliberately if the product requires OS-level
    user data locations.
    """
    return os.path.join(get_app_dir(), "runtime_data")

def get_logs_dir():
    return os.path.join(get_appdata_dir(), "logs")

def get_reports_dir():
    return os.path.join(get_appdata_dir(), "reports")

def get_config_path():
    return os.path.join(get_appdata_dir(), DEFAULT_SETTINGS_FILENAME)

def get_state_path():
    return os.path.join(get_appdata_dir(), DEFAULT_STATE_FILENAME)

def get_log_path():
    return os.path.join(get_logs_dir(), DEFAULT_LOG_FILENAME)

def get_diagnostic_report_path():
    return os.path.join(get_reports_dir(), DEFAULT_DIAGNOSTIC_FILENAME)

def get_default_settings():
    """
    Default settings for the prototype.

    Keep these stable and documented. Do not silently rename keys once real user
    data exists.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),

        # User/session behavior
        "autosave_enabled": True,
        "restore_previous_state": True,
        "safe_mode": False,

        # Paths
        "last_input_folder": "",
        "last_output_folder": "",

        # UI defaults
        "theme": "dark_navy",
        "ui_scale": 1.0,
        "window_width": 1200,
        "window_height": 800,
        "window_maximized": False,

        # Diagnostics
        "log_level": "INFO",
        "write_diagnostics_on_startup": False,
    }

def merge_defaults(settings, defaults):
    """
    Preserve unknown fields while filling in missing default keys.
    """
    result = {}
    for key in defaults:
        result[key] = defaults[key]
    if isinstance(settings, dict):
        for key in settings:
            result[key] = settings[key]
    return result

def load_json_file(path, default_value):
    """
    Load JSON safely.

    Does not crash the whole prototype on corrupt JSON.
    """
    if not os.path.isfile(path):
        return default_value

    try:
        if io is not None:
            with io.open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        log_exception("Failed to load JSON file: %s" % path)
        return default_value

def atomic_write_text(path, text):
    """
    Write text using a temp file + replace pattern.

    This is not a perfect database transaction, but it is safer than writing
    directly over the destination file.
    """
    folder = os.path.dirname(os.path.abspath(path))
    safe_makedirs(folder)

    fd, temp_path = tempfile.mkstemp(prefix=".tmp_", suffix=".txt", dir=folder)
    try:
        if IS_PY2:
            os.write(fd, ensure_bytes(text))
            os.close(fd)
            fd = None
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                fd = None
                f.write(ensure_text(text))

        if os.path.exists(path):
            backup_path = path + ".bak"
            try:
                shutil.copy2(path, backup_path)
            except Exception:
                pass

        if IS_PY2 and os.path.exists(path):
            os.remove(path)
        os.rename(temp_path, path)
    finally:
        if fd is not None:
            try:
                os.close(fd)
            except Exception:
                pass
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass

def save_json_file(path, data):
    text = json.dumps(data, indent=2, sort_keys=True)
    atomic_write_text(path, text)

def load_settings():
    defaults = get_default_settings()
    loaded = load_json_file(get_config_path(), {})
    settings = merge_defaults(loaded, defaults)
    return settings

def save_settings(settings):
    settings = merge_defaults(settings, get_default_settings())
    settings["updated_at"] = now_iso()
    save_json_file(get_config_path(), settings)

def log_message(message, level="INFO"):
    """
    Simple file + console logger.

    Keep this intentionally boring so it works in early environments.
    """
    safe_makedirs(get_logs_dir())
    line = "[%s] [%s] %s" % (now_iso(), level, ensure_text(message))

    try:
        print(line)
    except Exception:
        pass

    try:
        if io is not None:
            with io.open(get_log_path(), "a", encoding="utf-8") as f:
                f.write(ensure_text(line) + u"\n")
        else:
            with open(get_log_path(), "a") as f:
                f.write(ensure_bytes(line + "\n"))
    except Exception:
        pass

def log_exception(message):
    log_message(message, "ERROR")
    try:
        tb = traceback.format_exc()
        log_message(tb, "ERROR")
    except Exception:
        pass

# =============================================================================
# 4. DATA MODEL AND DEFAULTS
# =============================================================================

def make_default_state():
    """
    Session/runtime state.

    Separate this from settings. Settings are user preferences. State is what
    the app last did or where it last was.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "last_started_at": "",
        "last_clean_shutdown_at": "",
        "last_error": "",
        "active_item_id": "",
        "recent_items": [],
    }

def make_default_item(item_id, path):
    """
    Example persistent object factory.

    Replace or extend this with the project-specific object model.
    Preserve unknown fields during future migrations wherever practical.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "id": ensure_text(item_id),
        "path": ensure_text(path),
        "kind": "unknown",
        "status": "untested",
        "notes": "",
        "favorite": False,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }

def load_state():
    loaded = load_json_file(get_state_path(), {})
    return merge_defaults(loaded, make_default_state())

def save_state(state):
    state = merge_defaults(state, make_default_state())
    state["updated_at"] = now_iso()
    save_json_file(get_state_path(), state)

# =============================================================================
# 5. STORAGE / LOAD / SAVE
# =============================================================================

def backup_file_if_exists(path):
    if not os.path.isfile(path):
        return ""

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    backup_path = path + "." + timestamp + ".bak"
    try:
        shutil.copy2(path, backup_path)
        return backup_path
    except Exception:
        log_exception("Failed to back up file: %s" % path)
        return ""

def initialize_runtime_folders():
    safe_makedirs(get_appdata_dir())
    safe_makedirs(get_logs_dir())
    safe_makedirs(get_reports_dir())

# =============================================================================
# 6. SCANNING / IMPORT / PARSING
# =============================================================================

def scan_inputs(settings, state):
    """
    Project-specific scanning/import/parsing goes here.

    Rules:
    - Do not render UI here.
    - Do not delete user data automatically.
    - Return a structured summary.
    - Log recoverable errors and continue where reasonable.
    """
    result = {
        "scanned": 0,
        "new": 0,
        "updated": 0,
        "missing": 0,
        "errors": [],
    }

    input_folder = settings.get("last_input_folder", "")
    if not input_folder:
        result["errors"].append("No input folder configured.")
        return result

    if not os.path.isdir(input_folder):
        result["errors"].append("Input folder does not exist: %s" % input_folder)
        return result

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            result["scanned"] += 1

    return result

# =============================================================================
# 7. BUSINESS LOGIC / ACTIONS
# =============================================================================

def update_state_field(state, key, value):
    """
    Example action function.

    UI or CLI code should call action functions rather than mutating persistent
    state from scattered locations.
    """
    state[key] = value
    state["updated_at"] = now_iso()
    return {
        "ok": True,
        "message": "Updated state field: %s" % key,
        "state": state,
    }

def safe_state_now(reason):
    """
    Hardware/control projects must replace this with real safe-state behavior.

    For non-hardware projects, this still gives us a standard emergency/cleanup
    hook.
    """
    log_message("SAFE STATE REQUESTED: %s" % reason, "WARNING")

    # Hardware examples to add in real projects:
    # - set PSU output OFF
    # - close valves
    # - stop motor
    # - disable output relays
    # - flush buffered data
    # - mark command state as safe/idle

    return {
        "ok": True,
        "message": "Safe-state hook executed.",
        "reason": reason,
    }

# =============================================================================
# 8. UI / VIEW RENDERING
# =============================================================================

def detect_screen_size():
    """
    Best-effort screen detection.

    GUI-specific projects should replace this with toolkit-specific detection:
    Tkinter, PyQt, Kivy, etc.
    """
    return {
        "width": None,
        "height": None,
        "method": "not_detected_in_base_scaffold",
    }

def calculate_default_window_geometry(settings):
    """
    Compute sensible default window geometry.

    GUI projects can use this as the starting policy before toolkit-specific
    geometry calls.
    """
    screen = detect_screen_size()

    width = int(settings.get("window_width", 1200))
    height = int(settings.get("window_height", 800))

    if screen.get("width") and screen.get("height"):
        width = min(width, int(screen["width"] * 0.90))
        height = min(height, int(screen["height"] * 0.90))

    return {
        "width": width,
        "height": height,
        "screen": screen,
    }

def render_console_summary(settings, state):
    """
    Minimal non-GUI rendering.

    GUI projects should keep UI classes/functions in this section until later
    extraction.
    """
    app_info = get_app_info()
    print("")
    print("============================================================")
    print("%s" % app_info["name"])
    print("Version: %s" % app_info["version"])
    print("Phase:   %s" % app_info["phase"])
    print("Runtime data: %s" % get_appdata_dir())
    print("Settings:     %s" % get_config_path())
    print("State:        %s" % get_state_path())
    print("Safe mode:    %s" % settings.get("safe_mode"))
    print("Last started: %s" % state.get("last_started_at"))
    print("============================================================")
    print("")

# =============================================================================
# 9. DIAGNOSTICS / SMOKE TESTS
# =============================================================================

def check_imports():
    """
    Keep this list project-specific.

    Add optional imports here as the prototype grows.
    """
    checks = []

    modules = [
        "os",
        "sys",
        "json",
        "time",
        "traceback",
        "platform",
        "argparse",
        "tempfile",
        "shutil",
    ]

    for module_name in modules:
        try:
            __import__(module_name)
            checks.append({
                "module": module_name,
                "ok": True,
                "error": "",
            })
        except Exception as exc:
            checks.append({
                "module": module_name,
                "ok": False,
                "error": safe_repr(exc),
            })

    return checks

def run_file_read_write_test():
    """
    Diagnostic temp-file test.

    Does not use real user data.
    """
    result = {
        "ok": False,
        "path": "",
        "error": "",
    }

    try:
        safe_makedirs(get_reports_dir())
        test_path = os.path.join(get_reports_dir(), "diagnostic_rw_test.txt")
        atomic_write_text(test_path, "diagnostic write test at %s\n" % now_iso())

        if io is not None:
            with io.open(test_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            with open(test_path, "r") as f:
                text = f.read()

        result["path"] = test_path
        result["ok"] = "diagnostic write test" in text
    except Exception as exc:
        result["error"] = safe_repr(exc)
        log_exception("File read/write diagnostic failed.")

    return result

def collect_diagnostics(settings=None, state=None):
    """
    Collect copy/pasteable diagnostics.
    """
    if settings is None:
        settings = load_settings()
    if state is None:
        state = load_state()

    app_info = get_app_info()
    rw_test = run_file_read_write_test()
    import_checks = check_imports()
    screen = detect_screen_size()

    diagnostics = {
        "timestamp": now_iso(),
        "app_info": app_info,
        "paths": {
            "app_dir": get_app_dir(),
            "appdata_dir": get_appdata_dir(),
            "logs_dir": get_logs_dir(),
            "reports_dir": get_reports_dir(),
            "settings_path": get_config_path(),
            "state_path": get_state_path(),
            "log_path": get_log_path(),
            "diagnostic_report_path": get_diagnostic_report_path(),
        },
        "environment": {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "platform": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor(),
            "cwd": os.getcwd(),
            "argv": sys.argv,
            "is_py2": IS_PY2,
            "is_py3": IS_PY3,
        },
        "settings_summary": {
            "schema_version": settings.get("schema_version"),
            "safe_mode": settings.get("safe_mode"),
            "autosave_enabled": settings.get("autosave_enabled"),
            "restore_previous_state": settings.get("restore_previous_state"),
            "last_input_folder": settings.get("last_input_folder"),
            "theme": settings.get("theme"),
            "ui_scale": settings.get("ui_scale"),
        },
        "state_summary": {
            "schema_version": state.get("schema_version"),
            "last_started_at": state.get("last_started_at"),
            "last_clean_shutdown_at": state.get("last_clean_shutdown_at"),
            "last_error": state.get("last_error"),
            "active_item_id": state.get("active_item_id"),
            "recent_items_count": len(state.get("recent_items", [])),
        },
        "import_checks": import_checks,
        "file_read_write_test": rw_test,
        "display": screen,
    }

    return diagnostics

def format_diagnostic_report(diagnostics):
    """
    Human-readable diagnostic report.

    Designed so the user can copy/paste it back into a conversation.
    """
    lines = []
    lines.append("DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("Timestamp: %s" % diagnostics.get("timestamp"))
    lines.append("")

    app_info = diagnostics.get("app_info", {})
    lines.append("APP INFO")
    lines.append("-" * 72)
    for key in sorted(app_info.keys()):
        lines.append("%s: %s" % (key, app_info.get(key)))
    lines.append("")

    env = diagnostics.get("environment", {})
    lines.append("ENVIRONMENT")
    lines.append("-" * 72)
    for key in sorted(env.keys()):
        lines.append("%s: %s" % (key, env.get(key)))
    lines.append("")

    paths = diagnostics.get("paths", {})
    lines.append("PATHS")
    lines.append("-" * 72)
    for key in sorted(paths.keys()):
        lines.append("%s: %s" % (key, paths.get(key)))
    lines.append("")

    settings_summary = diagnostics.get("settings_summary", {})
    lines.append("SETTINGS SUMMARY")
    lines.append("-" * 72)
    for key in sorted(settings_summary.keys()):
        lines.append("%s: %s" % (key, settings_summary.get(key)))
    lines.append("")

    state_summary = diagnostics.get("state_summary", {})
    lines.append("STATE SUMMARY")
    lines.append("-" * 72)
    for key in sorted(state_summary.keys()):
        lines.append("%s: %s" % (key, state_summary.get(key)))
    lines.append("")

    lines.append("IMPORT CHECKS")
    lines.append("-" * 72)
    for check in diagnostics.get("import_checks", []):
        status = "PASS" if check.get("ok") else "FAIL"
        lines.append("%s: %s %s" % (status, check.get("module"), check.get("error", "")))
    lines.append("")

    rw_test = diagnostics.get("file_read_write_test", {})
    lines.append("FILE READ/WRITE TEST")
    lines.append("-" * 72)
    lines.append("Status: %s" % ("PASS" if rw_test.get("ok") else "FAIL"))
    lines.append("Path: %s" % rw_test.get("path"))
    lines.append("Error: %s" % rw_test.get("error"))
    lines.append("")

    display = diagnostics.get("display", {})
    lines.append("DISPLAY")
    lines.append("-" * 72)
    for key in sorted(display.keys()):
        lines.append("%s: %s" % (key, display.get(key)))
    lines.append("")

    lines.append("SUMMARY")
    lines.append("-" * 72)
    import_ok = all([c.get("ok") for c in diagnostics.get("import_checks", [])])
    rw_ok = rw_test.get("ok")
    overall_ok = import_ok and rw_ok
    lines.append("Overall diagnostic status: %s" % ("PASS" if overall_ok else "FAIL"))
    lines.append("")

    return "\n".join(lines)

def write_diagnostic_report(path=None):
    if path is None:
        path = get_diagnostic_report_path()

    settings = load_settings()
    state = load_state()
    diagnostics = collect_diagnostics(settings, state)
    report = format_diagnostic_report(diagnostics)
    atomic_write_text(path, report)
    log_message("Wrote diagnostic report: %s" % path)
    return path

def run_smoke_test():
    """
    Basic non-destructive smoke test.

    This should grow with the prototype. Each serious feature should get at
    least one lightweight smoke check.
    """
    results = []
    overall_ok = True

    def add_result(name, ok, detail):
        nonlocal_overall = None
        results.append({
            "name": name,
            "ok": ok,
            "detail": detail,
        })

    try:
        initialize_runtime_folders()
        add_result("initialize_runtime_folders", True, "Runtime folders initialized.")
    except Exception as exc:
        overall_ok = False
        add_result("initialize_runtime_folders", False, safe_repr(exc))

    try:
        settings = load_settings()
        save_settings(settings)
        add_result("settings_load_save", True, "Settings loaded and saved.")
    except Exception as exc:
        overall_ok = False
        add_result("settings_load_save", False, safe_repr(exc))

    try:
        state = load_state()
        save_state(state)
        add_result("state_load_save", True, "State loaded and saved.")
    except Exception as exc:
        overall_ok = False
        add_result("state_load_save", False, safe_repr(exc))

    try:
        rw_result = run_file_read_write_test()
        if rw_result.get("ok"):
            add_result("file_read_write", True, rw_result.get("path"))
        else:
            overall_ok = False
            add_result("file_read_write", False, rw_result.get("error"))
    except Exception as exc:
        overall_ok = False
        add_result("file_read_write", False, safe_repr(exc))

    try:
        info = get_app_info()
        ok = bool(info.get("name")) and bool(info.get("version"))
        if not ok:
            overall_ok = False
        add_result("get_app_info", ok, json.dumps(info, sort_keys=True))
    except Exception as exc:
        overall_ok = False
        add_result("get_app_info", False, safe_repr(exc))

    print("")
    print("SMOKE TEST RESULTS")
    print("=" * 72)
    for result in results:
        status = "PASS" if result.get("ok") else "FAIL"
        print("%s: %s -- %s" % (status, result.get("name"), result.get("detail")))
    print("=" * 72)
    print("OVERALL: %s" % ("PASS" if overall_ok else "FAIL"))
    print("")

    return overall_ok

# =============================================================================
# 10. MAIN APPLICATION / ENTRY POINT
# =============================================================================

def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="%s monolithic prototype" % APP_NAME
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Print version/app information and exit."
    )

    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Run basic non-destructive smoke tests and exit."
    )

    parser.add_argument(
        "--diagnostics",
        action="store_true",
        help="Write diagnostic report and exit."
    )

    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help="Run with safe_mode=True for this session."
    )

    parser.add_argument(
        "--set-input-folder",
        default="",
        help="Set last_input_folder in settings."
    )

    return parser.parse_args(argv)

def startup_safety_check(settings):
    """
    Startup safety hook.

    For hardware/control projects:
    - do not auto-enable outputs;
    - do not resume dangerous commands automatically;
    - verify devices before commanding;
    - expose manual safe-state control.
    """
    if settings.get("safe_mode"):
        log_message("Starting in safe mode.", "WARNING")

    return {
        "ok": True,
        "message": "Startup safety check passed.",
    }

def run_application(settings, state):
    """
    Main prototype application body.

    Replace this with project-specific GUI, CLI, device, workflow, or simulation
    startup while keeping startup explicit.
    """
    render_console_summary(settings, state)

    log_message("Prototype application started.")

    # Project-specific work starts here.
    # Examples:
    # - launch GUI
    # - start local server
    # - connect to device in manual mode only
    # - load data file
    # - run simulation loop
    # - open viewer

    print("Prototype scaffold is running.")
    print("Fill in project-specific logic inside run_application().")
    print("Use --smoke-test or --diagnostics for validation modes.")

    return 0

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    initialize_runtime_folders()
    args = parse_args(argv)

    if args.version:
        print(json.dumps(get_app_info(), indent=2, sort_keys=True))
        return 0

    settings = load_settings()

    if args.safe_mode:
        settings["safe_mode"] = True

    if args.set_input_folder:
        settings["last_input_folder"] = os.path.abspath(args.set_input_folder)
        save_settings(settings)
        log_message("Updated last_input_folder: %s" % settings["last_input_folder"])

    if args.smoke_test:
        ok = run_smoke_test()
        return 0 if ok else 1

    if args.diagnostics:
        report_path = write_diagnostic_report()
        print("Diagnostic report written:")
        print(report_path)
        return 0

    state = load_state()
    state["last_started_at"] = now_iso()
    save_state(state)

    try:
        safety = startup_safety_check(settings)
        if not safety.get("ok"):
            log_message("Startup safety check failed: %s" % safety.get("message"), "ERROR")
            safe_state_now("startup safety check failed")
            return 2

        result = run_application(settings, state)

        state["last_clean_shutdown_at"] = now_iso()
        state["last_error"] = ""
        save_state(state)

        log_message("Prototype application exited cleanly.")
        return result

    except KeyboardInterrupt:
        log_message("KeyboardInterrupt received.", "WARNING")
        safe_state_now("KeyboardInterrupt")
        return 130

    except Exception as exc:
        state["last_error"] = safe_repr(exc)
        save_state(state)
        log_exception("Unhandled exception in main().")
        safe_state_now("Unhandled exception")
        try:
            write_diagnostic_report()
        except Exception:
            pass
        return 1

# =============================================================================
# PROTOTYPE DEBT REGISTER
# =============================================================================
#
# DEBT-PROTO-001
# Title: Intentional monolithic structure
# Location: Entire file
# Why debt:
#   Compatibility, paths, settings, storage, actions, UI, diagnostics, and entry
#   point are kept in one file for fast early testing.
# Impact:
#   Long-term maintainability will degrade if this becomes the permanent structure.
# Suggested resolution:
#   Split only after requirements, feature inventory, acceptance tests, and module
#   boundaries are stable.
# Target extraction phase:
#   Phase 0.5 / Phase 1
# Status:
#   Open
#
# DEBT-PROTO-002
# Title: Generic state/data model
# Location: make_default_state(), make_default_item()
# Why debt:
#   The scaffold provides generic persistence objects before the real schema is
#   known.
# Impact:
#   Later code may grow ad hoc fields unless schema rules are formalized.
# Suggested resolution:
#   Create docs/050_DATA_SCHEMA_SPEC.md before formal refactor.
# Status:
#   Open
#
# DEBT-PROTO-003
# Title: Placeholder UI/display detection
# Location: detect_screen_size(), render_console_summary()
# Why debt:
#   Toolkit-specific GUI behavior is not implemented in the base scaffold.
# Impact:
#   GUI projects must add real DPI/screen/layout handling.
# Suggested resolution:
#   Implement toolkit-specific UI policy once GUI toolkit is chosen.
# Status:
#   Open
#
# =============================================================================
# EXTRACTION MAP
# =============================================================================
#
# Section 1  Imports and compatibility       -> project/compat.py
# Section 2  Constants/version info          -> project/constants.py
# Section 3  Paths/settings/logging          -> project/paths.py, settings.py, logging.py
# Section 4  Data model/defaults             -> project/model.py
# Section 5  Storage/load/save               -> project/storage.py
# Section 6  Scanning/import/parsing         -> project/scanner.py
# Section 7  Business logic/actions          -> project/actions.py
# Section 8  UI/view rendering               -> project/ui/ or project/views/
# Section 9  Diagnostics/smoke tests         -> project/diagnostics.py, tools/
# Section 10 Main application/entry point    -> main.py
#
# Do not extract until:
# - current feature inventory exists;
# - public function/class/file interfaces are frozen;
# - smoke tests exist;
# - diagnostics produce copy/pasteable output;
# - rollback package/baseline exists.
# =============================================================================

if __name__ == "__main__":
    sys.exit(main())
