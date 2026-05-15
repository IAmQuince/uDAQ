---
document_id: DOC-185
title: "DAQ/Control Code Patterns and Threading"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-185
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# DAQ/Control Code Patterns and Threading

It should be explicitly code-oriented: not a full application, but a library of proven patterns for acquisition threads, command queues, GUI-safe updates, historian writes, shutdown, safe-state handling, and diagnostics. This directly supports the AISOP rules that engineering GUIs should keep diagnostics/logs accessible, persist settings, handle device disconnects, preserve data integrity, and start/fail safe for hardware-control software.
# 185_DAQ_CONTROL_CODE_PATTERNS_AND_THREADING

## 0. Purpose

This document gives concrete code patterns for hardware DAQ/control applications.

It supports projects involving:

- LabJack U3/U6/T-series acquisition;
- many-channel analog input systems;
- MUX/channel expansion;
- programmable power supplies;
- PyVISA/SCPI instruments;
- Raspberry Pi data loggers;
- Arduino/ESP32 sensor networks;
- live graphing;
- CSV/SQLite historians;
- deterministic shutdown;
- safe-state behavior;
- GUI operator interfaces.

This is not a full application.

It is a pattern library.

The goal is to show how the earlier DAQ/control doctrine should actually be expressed in code.

---

## 1. Preferred Library Layers

### 1.1 Standard-library baseline

Use the Python standard library for the safety-critical skeleton wherever practical.

Recommended baseline imports:

```python id="9msp59"
import os
import sys
import time
import json
import csv
import sqlite3
import queue
import threading
import traceback
import logging
import signal
import atexit
from dataclasses import dataclass, field
from collections import deque

For Python 2.7 / Windows XP compatibility, adjust:
try:
    import queue
except ImportError:
    import Queue as queue

try:
    time_monotonic = time.monotonic
except AttributeError:
    time_monotonic = time.time

For XP/Python 2.7:
* do not use dataclasses;
* do not use type annotations;
* do not use f-strings;
* do not use pathlib;
* keep imports conservative.

1.2 Optional project libraries
Use these only when the target environment supports them.
LabJack U6:
    import u6

PyVISA:
    import pyvisa

Modern Qt GUI:
    PyQt5, PySide6, or PyQt6 depending on project target.

Windows XP GUI:
    PyQt4 or Tkinter, depending on known-good stack.

Plotting:
    matplotlib for conservative compatibility.
    pyqtgraph can be useful for high-rate modern Qt plotting, but should be optional and target-tested.

Storage:
    sqlite3 for local historian.
    csv for raw append/recovery/export.

Device/network:
    pyserial for serial devices.
    socket / socketserver for simple TCP/UDP if needed.
    zmq only if already accepted as a dependency.

Rule:
The safety skeleton must not depend on optional plotting or GUI libraries.

The diagnostic harness should run even if the GUI toolkit, plotting library, VISA backend, or LabJack library is missing.

2. Threading Philosophy
2.1 Use threads for blocking I/O, not for random structure
Use separate threads for:
acquisition loop
command/control loop
historian writer
device health monitor
optional slow diagnostics

Do not use worker threads to directly update GUI widgets.
The GUI/main thread should own GUI widgets.
Worker threads should communicate through:
queue.Queue
threading.Event
threading.Lock
Qt signals
timer-driven polling

2.2 Recommended thread model
Main GUI thread
    owns windows, controls, graph widgets, menus, status bar

Acquisition thread
    reads LabJack/sensors/devices
    timestamps records
    pushes records to telemetry_queue and writer_queue

Command thread
    serializes all hardware output commands
    owns PSU command order
    handles safe-state commands with highest priority

Writer thread
    writes raw records, events, commands, and faults to disk/database
    flushes frequently
    avoids blocking acquisition/UI

Health thread
    checks telemetry age, heartbeat age, reconnect status
    emits health events

GUI timer
    periodically drains telemetry_queue
    updates graph/status safely from GUI thread

Core rule:
Only one thread should own each hardware command path.

For a PSU, the command thread owns setpoints and output-enable commands.
For a LabJack acquisition device, the acquisition thread owns reads.
For the historian, the writer thread owns file/database writes.

3. Core Message Types
Use small message objects or dictionaries.
For compatibility, dictionaries are fine.
def make_telemetry_record(
    run_id,
    device_id,
    channel_id,
    signal_name,
    value,
    units,
    timestamp,
    quality="GOOD",
    raw_value=None,
    command_state="",
):
    return {
        "type": "telemetry",
        "run_id": run_id,
        "device_id": device_id,
        "channel_id": channel_id,
        "signal_name": signal_name,
        "value": value,
        "units": units,
        "timestamp": timestamp,
        "quality": quality,
        "raw_value": raw_value,
        "command_state": command_state,
    }

def make_event_record(run_id, event_type, message, severity="INFO", details=None):
    return {
        "type": "event",
        "run_id": run_id,
        "timestamp": time.time(),
        "event_type": event_type,
        "severity": severity,
        "message": message,
        "details": details or {},
    }

def make_command_record(run_id, command_id, device_id, command_type, payload):
    return {
        "type": "command",
        "run_id": run_id,
        "timestamp": time.time(),
        "command_id": command_id,
        "device_id": device_id,
        "command_type": command_type,
        "payload": payload,
        "status": "QUEUED",
    }

Keep telemetry, events, commands, and faults distinct.
Do not jam everything into one untyped queue.

4. Thread Coordination Primitives
4.1 Shared events
shutdown_event = threading.Event()
safe_state_event = threading.Event()
pause_acquisition_event = threading.Event()
writer_flush_event = threading.Event()

Meanings:
shutdown_event:
    All threads should finish as soon as safely possible.

safe_state_event:
    Output-control paths should enter safe state immediately.

pause_acquisition_event:
    Acquisition may pause without shutting down the whole app.

writer_flush_event:
    Writer should flush buffers to disk promptly.

4.2 Queues
telemetry_queue = queue.Queue(maxsize=10000)
writer_queue = queue.Queue(maxsize=50000)
command_queue = queue.PriorityQueue()
event_queue = queue.Queue(maxsize=10000)

Queue purposes:
telemetry_queue:
    Recent records for GUI/status display.

writer_queue:
    Raw records for durable storage.

command_queue:
    Serialized hardware output commands.
    Use priority so safe-state can outrank normal commands.

event_queue:
    Faults, warnings, state changes, UI notifications.

4.3 Non-blocking queue put with loss policy
For GUI telemetry, dropping old display records can be acceptable.
For raw data writing, dropping records is usually not acceptable unless explicitly marked.
def put_gui_telemetry(q, record):
    """
    GUI telemetry queue may drop oldest display records if overloaded.
    This must never be the only raw data path.
    """
    try:
        q.put_nowait(record)
        return True
    except queue.Full:
        try:
            q.get_nowait()
        except queue.Empty:
            pass
        try:
            q.put_nowait(record)
            return True
        except queue.Full:
            return False

def put_writer_record(q, record, timeout=1.0):
    """
    Writer queue should apply backpressure rather than silently drop data.
    """
    try:
        q.put(record, timeout=timeout)
        return True
    except queue.Full:
        return False

Policy:
GUI display queue may drop display data.
Raw writer queue should not silently drop data.
If raw writer queue is full, raise a fault and preserve that fact.

5. Device Adapter Pattern
5.1 Base device adapter
class DeviceAdapter(object):
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def is_connected(self):
        raise NotImplementedError

    def read_identity(self):
        raise NotImplementedError

    def read_telemetry(self):
        """
        Return a list of telemetry records or low-level readings.
        """
        raise NotImplementedError

    def write_command(self, command):
        """
        Only command thread should normally call this.
        """
        raise NotImplementedError

    def enter_safe_state(self, reason):
        """
        Must be safe to call more than once.
        """
        raise NotImplementedError

    def diagnostics(self):
        return {
            "connected": self.is_connected(),
            "adapter": self.__class__.__name__,
        }

5.2 Simulated adapter
Always build this early.
import math
import random

class SimulatedLabJackAdapter(DeviceAdapter):
    def __init__(self, device_id="sim_labjack", channels=None):
        self.device_id = device_id
        self.channels = channels or ["AIN0", "AIN1", "AIN2", "AIN3"]
        self.connected = False
        self.started = time.time()

    def connect(self):
        self.connected = True
        return True

    def disconnect(self):
        self.connected = False

    def is_connected(self):
        return self.connected

    def read_identity(self):
        return {
            "device_id": self.device_id,
            "device_type": "SIMULATED_LABJACK",
            "serial_number": "SIM-0001",
        }

    def read_telemetry(self):
        if not self.connected:
            raise RuntimeError("Simulated device disconnected")

        t = time.time() - self.started
        records = []

        for idx, channel in enumerate(self.channels):
            value = 1.0 + idx + 0.1 * math.sin(t / 5.0) + random.uniform(-0.01, 0.01)
            records.append({
                "device_id": self.device_id,
                "channel_id": channel,
                "raw_value": value,
                "value": value,
                "units": "V",
                "timestamp": time.time(),
                "quality": "SIMULATED",
            })

        return records

    def write_command(self, command):
        return {
            "ok": True,
            "simulated": True,
            "command": command,
        }

    def enter_safe_state(self, reason):
        return {
            "ok": True,
            "safe": True,
            "reason": reason,
        }

Reason:
Simulation mode lets us test the GUI, graph, writer, sequence preview, diagnostics, and shutdown without real hardware.

5.3 LabJack U6 adapter sketch
This is intentionally conservative. The exact channel setup depends on the installed LabJackPython version and hardware wiring.
class LabJackU6Adapter(DeviceAdapter):
    def __init__(self, device_id="labjack_u6_primary", channels=None):
        self.device_id = device_id
        self.channels = channels or ["AIN0", "AIN1", "AIN2", "AIN3"]
        self.handle = None
        self.last_error = ""

    def connect(self):
        try:
            import u6
            self.handle = u6.U6()
            return True
        except Exception as exc:
            self.handle = None
            self.last_error = repr(exc)
            return False

    def disconnect(self):
        if self.handle is not None:
            try:
                self.handle.close()
            except Exception:
                pass
        self.handle = None

    def is_connected(self):
        return self.handle is not None

    def read_identity(self):
        if self.handle is None:
            return {
                "device_id": self.device_id,
                "connected": False,
            }

        # Exact fields depend on LabJackPython/device support.
        return {
            "device_id": self.device_id,
            "device_type": "LabJack U6",
            "connected": True,
        }

    def read_telemetry(self):
        if self.handle is None:
            raise RuntimeError("LabJack U6 is not connected")

        records = []
        ts = time.time()

        for channel in self.channels:
            try:
                # Example assumes channel names like AIN0, AIN1...
                ain_index = int(channel.replace("AIN", ""))
                value = self.handle.getAIN(ain_index)

                records.append({
                    "device_id": self.device_id,
                    "channel_id": channel,
                    "raw_value": value,
                    "value": value,
                    "units": "V",
                    "timestamp": ts,
                    "quality": "GOOD",
                })

            except Exception as exc:
                records.append({
                    "device_id": self.device_id,
                    "channel_id": channel,
                    "raw_value": None,
                    "value": None,
                    "units": "V",
                    "timestamp": ts,
                    "quality": "READ_ERROR",
                    "error": repr(exc),
                })

        return records

    def write_command(self, command):
        # For analog/digital outputs, implement only through command thread.
        raise NotImplementedError("Write command not implemented for this adapter")

    def enter_safe_state(self, reason):
        # If LJ controls relays/outputs, set known safe outputs here.
        return {
            "ok": True,
            "reason": reason,
            "note": "No LabJack output safe-state commands configured.",
        }

    def diagnostics(self):
        return {
            "device_id": self.device_id,
            "adapter": "LabJackU6Adapter",
            "connected": self.is_connected(),
            "channels": list(self.channels),
            "last_error": self.last_error,
        }

Rule:
Do not bury channel meaning inside the LabJack adapter.

The adapter reads physical channels.
The channel map assigns engineering meaning.

6. Channel Mapping Pattern
CHANNEL_MAP = {
    "labjack_u6_primary:AIN0": {
        "signal_name": "stack_voltage",
        "display_name": "Stack Voltage",
        "units": "V",
        "scale": 1.0,
        "offset": 0.0,
        "axis_group": "voltage",
        "plot_default": True,
    },
    "labjack_u6_primary:AIN1": {
        "signal_name": "stack_current_monitor",
        "display_name": "Stack Current Monitor",
        "units": "A",
        "scale": 10.0,
        "offset": 0.0,
        "axis_group": "current",
        "plot_default": True,
    },
}

def apply_channel_map(low_level_record, channel_map):
    key = "%s:%s" % (
        low_level_record.get("device_id"),
        low_level_record.get("channel_id"),
    )

    mapping = channel_map.get(key)

    if mapping is None:
        record = dict(low_level_record)
        record["signal_name"] = key
        record["display_name"] = key
        record["quality"] = "UNMAPPED"
        return record

    raw = low_level_record.get("raw_value")

    if raw is None:
        value = None
    else:
        value = raw * mapping.get("scale", 1.0) + mapping.get("offset", 0.0)

    record = dict(low_level_record)
    record["signal_name"] = mapping["signal_name"]
    record["display_name"] = mapping["display_name"]
    record["units"] = mapping["units"]
    record["value"] = value
    record["axis_group"] = mapping.get("axis_group", "")
    return record

Acceptance check:
A physical channel must match the same logical signal in:
- live display;
- raw data file;
- historian;
- graph trace;
- export;
- diagnostics.

7. Acquisition Thread Pattern
class AcquisitionThread(threading.Thread):
    def __init__(
        self,
        adapter,
        channel_map,
        telemetry_queue,
        writer_queue,
        event_queue,
        shutdown_event,
        sample_interval_s=1.0,
        run_id="default_run",
    ):
        threading.Thread.__init__(self)
        self.daemon = False
        self.adapter = adapter
        self.channel_map = channel_map
        self.telemetry_queue = telemetry_queue
        self.writer_queue = writer_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.sample_interval_s = sample_interval_s
        self.run_id = run_id
        self.last_sample_time = None
        self.error_count = 0
        self.connected = False

    def run(self):
        self.event_queue.put(make_event_record(
            self.run_id,
            "ACQUISITION_THREAD_START",
            "Acquisition thread started."
        ))

        self.connected = self.adapter.connect()

        if not self.connected:
            self.event_queue.put(make_event_record(
                self.run_id,
                "DEVICE_CONNECT_FAILED",
                "Acquisition device failed to connect.",
                severity="ERROR",
                details=self.adapter.diagnostics()
            ))

        next_sample = time_monotonic()

        while not self.shutdown_event.is_set():
            now = time_monotonic()

            if now < next_sample:
                time.sleep(min(0.05, next_sample - now))
                continue

            next_sample += self.sample_interval_s

            try:
                if not self.adapter.is_connected():
                    self.connected = self.adapter.connect()
                    if not self.connected:
                        self._publish_device_disconnected()
                        continue

                low_level_records = self.adapter.read_telemetry()
                self.last_sample_time = time.time()

                for low in low_level_records:
                    mapped = apply_channel_map(low, self.channel_map)
                    mapped["run_id"] = self.run_id
                    mapped["type"] = "telemetry"

                    put_gui_telemetry(self.telemetry_queue, mapped)

                    ok = put_writer_record(self.writer_queue, mapped, timeout=1.0)
                    if not ok:
                        self.event_queue.put(make_event_record(
                            self.run_id,
                            "WRITER_QUEUE_FULL",
                            "Writer queue full. Raw data may be at risk.",
                            severity="CRITICAL"
                        ))

            except Exception as exc:
                self.error_count += 1
                self.event_queue.put(make_event_record(
                    self.run_id,
                    "ACQUISITION_ERROR",
                    "Acquisition loop error.",
                    severity="ERROR",
                    details={
                        "error": repr(exc),
                        "traceback": traceback.format_exc(),
                    }
                ))
                time.sleep(0.5)

        try:
            self.adapter.disconnect()
        except Exception:
            pass

        self.event_queue.put(make_event_record(
            self.run_id,
            "ACQUISITION_THREAD_STOP",
            "Acquisition thread stopped."
        ))

    def _publish_device_disconnected(self):
        self.event_queue.put(make_event_record(
            self.run_id,
            "DEVICE_DISCONNECTED",
            "Acquisition device disconnected or unavailable.",
            severity="WARNING",
            details=self.adapter.diagnostics()
        ))
        time.sleep(1.0)

    def diagnostics(self):
        return {
            "thread": "AcquisitionThread",
            "alive": self.is_alive(),
            "connected": self.connected,
            "last_sample_time": self.last_sample_time,
            "error_count": self.error_count,
            "sample_interval_s": self.sample_interval_s,
            "adapter": self.adapter.diagnostics(),
        }

Key points:
- Acquisition thread does not update GUI widgets.
- Acquisition thread does not directly write files.
- Acquisition thread publishes telemetry and events.
- Device reconnect is attempted carefully.
- Read errors become quality/event records, not silent failures.

8. Writer Thread Pattern
8.1 CSV writer thread
class CsvWriterThread(threading.Thread):
    def __init__(self, writer_queue, event_queue, shutdown_event, csv_path, flush_interval_s=2.0):
        threading.Thread.__init__(self)
        self.daemon = False
        self.writer_queue = writer_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.csv_path = csv_path
        self.flush_interval_s = flush_interval_s
        self.rows_written = 0
        self.last_flush_time = 0
        self.last_error = ""

        self.fieldnames = [
            "type",
            "run_id",
            "timestamp",
            "device_id",
            "channel_id",
            "signal_name",
            "display_name",
            "value",
            "raw_value",
            "units",
            "quality",
            "command_state",
        ]

    def run(self):
        folder = os.path.dirname(os.path.abspath(self.csv_path))
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

        file_exists = os.path.isfile(self.csv_path)

        try:
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames, extrasaction="ignore")

                if not file_exists:
                    writer.writeheader()
                    f.flush()

                self.last_flush_time = time.time()

                while not self.shutdown_event.is_set() or not self.writer_queue.empty():
                    try:
                        record = self.writer_queue.get(timeout=0.25)
                    except queue.Empty:
                        self._periodic_flush(f)
                        continue

                    try:
                        writer.writerow(record)
                        self.rows_written += 1
                    except Exception as exc:
                        self.last_error = repr(exc)
                        self.event_queue.put(make_event_record(
                            record.get("run_id", ""),
                            "CSV_WRITE_ERROR",
                            "Failed writing record to CSV.",
                            severity="CRITICAL",
                            details={
                                "error": repr(exc),
                                "record": repr(record),
                            }
                        ))

                    self._periodic_flush(f)

                f.flush()

        except Exception as exc:
            self.last_error = repr(exc)
            self.event_queue.put(make_event_record(
                "",
                "CSV_WRITER_THREAD_FATAL",
                "CSV writer thread failed.",
                severity="CRITICAL",
                details={
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                    "csv_path": self.csv_path,
                }
            ))

    def _periodic_flush(self, file_obj):
        now = time.time()
        if now - self.last_flush_time >= self.flush_interval_s:
            file_obj.flush()
            self.last_flush_time = now

    def diagnostics(self):
        return {
            "thread": "CsvWriterThread",
            "alive": self.is_alive(),
            "csv_path": self.csv_path,
            "rows_written": self.rows_written,
            "last_flush_time": self.last_flush_time,
            "last_error": self.last_error,
            "queue_size": self.writer_queue.qsize(),
        }

Policy:
The writer thread drains the queue during shutdown.
Shutdown waits for writer drain or logs that it failed.

8.2 SQLite writer pattern
For SQLite, one writer thread should own the connection.
class SQLiteWriterThread(threading.Thread):
    def __init__(self, writer_queue, event_queue, shutdown_event, db_path):
        threading.Thread.__init__(self)
        self.daemon = False
        self.writer_queue = writer_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.db_path = db_path
        self.rows_written = 0
        self.last_error = ""

    def run(self):
        folder = os.path.dirname(os.path.abspath(self.db_path))
        if folder and not os.path.isdir(folder):
            os.makedirs(folder)

        conn = None

        try:
            conn = sqlite3.connect(self.db_path)
            self._initialize_schema(conn)

            while not self.shutdown_event.is_set() or not self.writer_queue.empty():
                try:
                    record = self.writer_queue.get(timeout=0.25)
                except queue.Empty:
                    continue

                try:
                    self._write_record(conn, record)
                    self.rows_written += 1

                    if self.rows_written % 100 == 0:
                        conn.commit()

                except Exception as exc:
                    self.last_error = repr(exc)
                    self.event_queue.put(make_event_record(
                        record.get("run_id", ""),
                        "SQLITE_WRITE_ERROR",
                        "Failed writing record to SQLite.",
                        severity="CRITICAL",
                        details={
                            "error": repr(exc),
                            "record": repr(record),
                        }
                    ))

            conn.commit()

        except Exception as exc:
            self.last_error = repr(exc)
            self.event_queue.put(make_event_record(
                "",
                "SQLITE_WRITER_THREAD_FATAL",
                "SQLite writer thread failed.",
                severity="CRITICAL",
                details={
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                    "db_path": self.db_path,
                }
            ))

        finally:
            if conn is not None:
                try:
                    conn.commit()
                    conn.close()
                except Exception:
                    pass

    def _initialize_schema(self, conn):
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telemetry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                timestamp REAL,
                device_id TEXT,
                channel_id TEXT,
                signal_name TEXT,
                value REAL,
                raw_value REAL,
                units TEXT,
                quality TEXT,
                command_state TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                timestamp REAL,
                event_type TEXT,
                severity TEXT,
                message TEXT,
                details_json TEXT
            )
        """)
        conn.commit()

    def _write_record(self, conn, record):
        if record.get("type") == "telemetry":
            conn.execute("""
                INSERT INTO telemetry (
                    run_id, timestamp, device_id, channel_id, signal_name,
                    value, raw_value, units, quality, command_state
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                record.get("run_id"),
                record.get("timestamp"),
                record.get("device_id"),
                record.get("channel_id"),
                record.get("signal_name"),
                record.get("value"),
                record.get("raw_value"),
                record.get("units"),
                record.get("quality"),
                record.get("command_state"),
            ))

        elif record.get("type") == "event":
            conn.execute("""
                INSERT INTO events (
                    run_id, timestamp, event_type, severity, message, details_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                record.get("run_id"),
                record.get("timestamp"),
                record.get("event_type"),
                record.get("severity"),
                record.get("message"),
                json.dumps(record.get("details", {})),
            ))

    def diagnostics(self):
        return {
            "thread": "SQLiteWriterThread",
            "alive": self.is_alive(),
            "db_path": self.db_path,
            "rows_written": self.rows_written,
            "last_error": self.last_error,
            "queue_size": self.writer_queue.qsize(),
        }

SQLite rule:
Do not share one SQLite connection casually across many threads.
Prefer one writer owner thread or short-lived connections with clear locking policy.

9. Command Thread and Safe-State Priority
9.1 Command priority constants
PRIORITY_SAFE_STATE = 0
PRIORITY_OPERATOR_STOP = 10
PRIORITY_MANUAL_COMMAND = 50
PRIORITY_SEQUENCE_COMMAND = 100
PRIORITY_BACKGROUND = 200

Lower number means higher priority.

9.2 Command object
def make_priority_command(priority, command):
    return (
        priority,
        time.time(),
        command,
    )

def make_safe_state_command(reason):
    return make_priority_command(
        PRIORITY_SAFE_STATE,
        {
            "command_type": "SAFE_STATE",
            "reason": reason,
            "timestamp": time.time(),
        }
    )

9.3 Command thread
class CommandThread(threading.Thread):
    def __init__(
        self,
        control_adapter,
        command_queue,
        writer_queue,
        event_queue,
        shutdown_event,
        safe_state_event,
        run_id="default_run",
    ):
        threading.Thread.__init__(self)
        self.daemon = False
        self.control_adapter = control_adapter
        self.command_queue = command_queue
        self.writer_queue = writer_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.safe_state_event = safe_state_event
        self.run_id = run_id
        self.command_state = "IDLE_SAFE"
        self.last_error = ""

    def run(self):
        self.event_queue.put(make_event_record(
            self.run_id,
            "COMMAND_THREAD_START",
            "Command thread started."
        ))

        connected = self.control_adapter.connect()

        if not connected:
            self.command_state = "DISCONNECTED"
            self.event_queue.put(make_event_record(
                self.run_id,
                "CONTROL_DEVICE_CONNECT_FAILED",
                "Control device failed to connect.",
                severity="ERROR",
                details=self.control_adapter.diagnostics()
            ))

        while not self.shutdown_event.is_set():
            if self.safe_state_event.is_set():
                self._enter_safe_state("safe_state_event set")
                self.safe_state_event.clear()

            try:
                priority, queued_at, command = self.command_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            try:
                if command.get("command_type") == "SAFE_STATE":
                    self._enter_safe_state(command.get("reason", "safe-state command"))
                    continue

                if self.command_state in ("FAULTED", "SAFE_STATE_CONFIRMED"):
                    self.event_queue.put(make_event_record(
                        self.run_id,
                        "COMMAND_REJECTED",
                        "Command rejected because system is faulted or safe.",
                        severity="WARNING",
                        details={"command": command}
                    ))
                    continue

                self._execute_command(command)

            except Exception as exc:
                self.last_error = repr(exc)
                self.command_state = "FAULTED"
                self.event_queue.put(make_event_record(
                    self.run_id,
                    "COMMAND_THREAD_ERROR",
                    "Command execution failed. Entering safe state.",
                    severity="CRITICAL",
                    details={
                        "error": repr(exc),
                        "traceback": traceback.format_exc(),
                        "command": command,
                    }
                ))
                self._enter_safe_state("command exception")

        self._enter_safe_state("command thread shutdown")

        try:
            self.control_adapter.disconnect()
        except Exception:
            pass

        self.event_queue.put(make_event_record(
            self.run_id,
            "COMMAND_THREAD_STOP",
            "Command thread stopped."
        ))

    def _execute_command(self, command):
        self.command_state = "COMMAND_ACTIVE"

        record = make_command_record(
            self.run_id,
            command.get("command_id", ""),
            command.get("device_id", ""),
            command.get("command_type", ""),
            command.get("payload", {})
        )
        record["status"] = "SENT"

        result = self.control_adapter.write_command(command)

        record["result"] = result
        record["status"] = "COMPLETE" if result.get("ok") else "FAILED"

        put_writer_record(self.writer_queue, record, timeout=1.0)

        self.event_queue.put(make_event_record(
            self.run_id,
            "COMMAND_COMPLETE",
            "Command completed.",
            details=record
        ))

        self.command_state = "IDLE_SAFE"

    def _enter_safe_state(self, reason):
        self.command_state = "SAFE_STATE_REQUESTED"

        event = make_event_record(
            self.run_id,
            "SAFE_STATE_REQUESTED",
            "Safe state requested.",
            severity="WARNING",
            details={"reason": reason}
        )
        put_writer_record(self.writer_queue, event, timeout=1.0)
        self.event_queue.put(event)

        try:
            result = self.control_adapter.enter_safe_state(reason)
            self.command_state = "SAFE_STATE_CONFIRMED" if result.get("ok") else "FAULTED"

            event2 = make_event_record(
                self.run_id,
                "SAFE_STATE_RESULT",
                "Safe state result.",
                severity="WARNING",
                details=result
            )
            put_writer_record(self.writer_queue, event2, timeout=1.0)
            self.event_queue.put(event2)

        except Exception as exc:
            self.command_state = "FAULTED"
            self.last_error = repr(exc)
            self.event_queue.put(make_event_record(
                self.run_id,
                "SAFE_STATE_FAILED",
                "Safe-state command failed.",
                severity="CRITICAL",
                details={
                    "reason": reason,
                    "error": repr(exc),
                    "traceback": traceback.format_exc(),
                }
            ))

    def diagnostics(self):
        return {
            "thread": "CommandThread",
            "alive": self.is_alive(),
            "command_state": self.command_state,
            "last_error": self.last_error,
            "control_adapter": self.control_adapter.diagnostics(),
        }

Key rule:
Safe-state commands must outrank sequence/manual commands.

10. Genesys+ / PSU Adapter Sketch
Exact SCPI commands depend on the PSU model/configuration. This pattern shows where they belong.
class GenesysPSUAdapter(DeviceAdapter):
    def __init__(self, resource_name, device_id="genesys_psu"):
        self.resource_name = resource_name
        self.device_id = device_id
        self.rm = None
        self.inst = None
        self.last_error = ""

    def connect(self):
        try:
            import pyvisa
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource(self.resource_name)
            self.inst.timeout = 2000
            return True
        except Exception as exc:
            self.last_error = repr(exc)
            self.inst = None
            return False

    def disconnect(self):
        if self.inst is not None:
            try:
                self.inst.close()
            except Exception:
                pass
        self.inst = None

    def is_connected(self):
        return self.inst is not None

    def read_identity(self):
        if self.inst is None:
            return {"connected": False}
        try:
            return {
                "connected": True,
                "idn": self.inst.query("*IDN?").strip(),
            }
        except Exception as exc:
            self.last_error = repr(exc)
            return {
                "connected": False,
                "error": repr(exc),
            }

    def read_telemetry(self):
        if self.inst is None:
            raise RuntimeError("PSU not connected")

        ts = time.time()

        # Replace these with validated commands for the actual Genesys+ model.
        voltage = float(self.inst.query("MEAS:VOLT?"))
        current = float(self.inst.query("MEAS:CURR?"))

        return [
            {
                "device_id": self.device_id,
                "channel_id": "MEAS_VOLT",
                "signal_name": "psu_measured_voltage",
                "raw_value": voltage,
                "value": voltage,
                "units": "V",
                "timestamp": ts,
                "quality": "GOOD",
            },
            {
                "device_id": self.device_id,
                "channel_id": "MEAS_CURR",
                "signal_name": "psu_measured_current",
                "raw_value": current,
                "value": current,
                "units": "A",
                "timestamp": ts,
                "quality": "GOOD",
            },
        ]

    def write_command(self, command):
        if self.inst is None:
            return {"ok": False, "error": "PSU not connected"}

        payload = command.get("payload", {})
        ctype = command.get("command_type")

        if ctype == "SET_VOLTAGE_CURRENT":
            voltage = float(payload["voltage"])
            current = float(payload["current"])

            # Replace with model-verified commands.
            self.inst.write("VOLT %s" % voltage)
            self.inst.write("CURR %s" % current)

            return {
                "ok": True,
                "voltage": voltage,
                "current": current,
            }

        if ctype == "OUTPUT_ON":
            self.inst.write("OUTP ON")
            return {"ok": True, "output": "ON"}

        if ctype == "OUTPUT_OFF":
            self.inst.write("OUTP OFF")
            return {"ok": True, "output": "OFF"}

        return {
            "ok": False,
            "error": "Unknown command type: %s" % ctype,
        }

    def enter_safe_state(self, reason):
        if self.inst is None:
            return {
                "ok": False,
                "reason": reason,
                "error": "PSU not connected",
            }

        # Default safe-state policy: output off.
        self.inst.write("OUTP OFF")

        return {
            "ok": True,
            "reason": reason,
            "action": "OUTP OFF",
        }

    def diagnostics(self):
        return {
            "device_id": self.device_id,
            "adapter": "GenesysPSUAdapter",
            "resource_name": self.resource_name,
            "connected": self.is_connected(),
            "last_error": self.last_error,
        }

Rule:
All PSU output commands should go through the command thread, not directly from GUI button handlers.

11. GUI Integration Pattern
11.1 GUI-safe queue polling
For Tkinter/PyQt-style GUIs, update the GUI from the GUI thread.
Pseudo-pattern:
def gui_timer_tick():
    drain_telemetry_queue()
    drain_event_queue()
    update_status_bar()
    update_graph_if_due()

Do not do this from the acquisition thread:
graph_widget.plot(...)
label.setText(...)
button.setEnabled(...)

11.2 PyQt-style timer pattern
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, telemetry_queue, event_queue, command_queue, safe_state_event):
        super(MainWindow, self).__init__()

        self.telemetry_queue = telemetry_queue
        self.event_queue = event_queue
        self.command_queue = command_queue
        self.safe_state_event = safe_state_event

        self.recent_records = []
        self.max_recent_records = 10000

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.on_gui_timer)
        self.timer.start(100)  # ms

    def on_gui_timer(self):
        self._drain_telemetry()
        self._drain_events()
        self._update_status()
        self._update_graph()

    def _drain_telemetry(self):
        drained = 0

        while drained < 1000:
            try:
                record = self.telemetry_queue.get_nowait()
            except queue.Empty:
                break

            self.recent_records.append(record)
            drained += 1

        if len(self.recent_records) > self.max_recent_records:
            self.recent_records = self.recent_records[-self.max_recent_records:]

    def _drain_events(self):
        while True:
            try:
                event = self.event_queue.get_nowait()
            except queue.Empty:
                break

            self._append_log_line(event)

    def _append_log_line(self, event):
        # Update GUI log widget here.
        pass

    def _update_status(self):
        # Update status strip here.
        pass

    def _update_graph(self):
        # Plot only at controlled rate.
        # Do not redraw full history on every telemetry packet.
        pass

    def on_safe_state_button_clicked(self):
        self.safe_state_event.set()
        self.command_queue.put(make_safe_state_command("operator button"))

This preserves the thread boundary:
Workers produce data.
GUI consumes data.
GUI sends commands by queue/event.
Command thread talks to hardware.

12. Graph Buffer Pattern
Use bounded buffers per signal.
class SignalBuffer(object):
    def __init__(self, max_points=20000):
        self.max_points = max_points
        self.t = deque(maxlen=max_points)
        self.y = deque(maxlen=max_points)
        self.quality = deque(maxlen=max_points)

    def append(self, timestamp, value, quality="GOOD"):
        self.t.append(timestamp)
        self.y.append(value)
        self.quality.append(quality)

    def get_window(self, seconds):
        if not self.t:
            return [], []

        cutoff = self.t[-1] - seconds
        xs = []
        ys = []

        for t, y in zip(self.t, self.y):
            if t >= cutoff:
                xs.append(t)
                ys.append(y)

        return xs, ys

class GraphBufferManager(object):
    def __init__(self, max_points_per_signal=20000):
        self.buffers = {}
        self.max_points_per_signal = max_points_per_signal

    def add_record(self, record):
        signal = record.get("signal_name")
        if not signal:
            return

        if record.get("value") is None:
            return

        if signal not in self.buffers:
            self.buffers[signal] = SignalBuffer(self.max_points_per_signal)

        self.buffers[signal].append(
            record.get("timestamp"),
            record.get("value"),
            record.get("quality", "GOOD"),
        )

    def get_signal_window(self, signal_name, seconds):
        buf = self.buffers.get(signal_name)
        if buf is None:
            return [], []
        return buf.get_window(seconds)

Rule:
The graph buffer is display memory.
It is not the historian.

13. Decimation Pattern for Full-History View
def decimate_min_max(points, max_points=5000):
    """
    points: list of (x, y)
    Preserves rough envelope by keeping min/max per bucket.
    Useful for display only.
    """
    n = len(points)
    if n <= max_points:
        return points

    bucket_count = max_points // 2
    bucket_size = float(n) / float(bucket_count)

    output = []

    for i in range(bucket_count):
        start = int(i * bucket_size)
        end = int((i + 1) * bucket_size)
        bucket = points[start:end]

        if not bucket:
            continue

        min_point = min(bucket, key=lambda p: p[1])
        max_point = max(bucket, key=lambda p: p[1])

        if min_point[0] <= max_point[0]:
            output.extend([min_point, max_point])
        else:
            output.extend([max_point, min_point])

    return output

Label the result:
FULL HISTORY VIEW — DISPLAY DECIMATED
Raw data unchanged.

14. Deterministic Shutdown Manager
class ShutdownManager(object):
    def __init__(
        self,
        shutdown_event,
        safe_state_event,
        threads,
        event_queue,
        writer_queue,
        run_id,
        join_timeout_s=5.0,
    ):
        self.shutdown_event = shutdown_event
        self.safe_state_event = safe_state_event
        self.threads = threads
        self.event_queue = event_queue
        self.writer_queue = writer_queue
        self.run_id = run_id
        self.join_timeout_s = join_timeout_s
        self.shutdown_started = False

    def request_shutdown(self, reason="normal shutdown"):
        if self.shutdown_started:
            return

        self.shutdown_started = True

        self.event_queue.put(make_event_record(
            self.run_id,
            "SHUTDOWN_REQUESTED",
            "Shutdown requested.",
            severity="WARNING",
            details={"reason": reason}
        ))

        # Safe-state first.
        self.safe_state_event.set()

        # Then tell all loops to exit.
        self.shutdown_event.set()

        # Wait for threads.
        for name, thread in self.threads:
            try:
                thread.join(self.join_timeout_s)
            except Exception:
                pass

            if thread.is_alive():
                self.event_queue.put(make_event_record(
                    self.run_id,
                    "THREAD_JOIN_TIMEOUT",
                    "Thread did not stop within timeout.",
                    severity="ERROR",
                    details={"thread": name}
                ))

        self.event_queue.put(make_event_record(
            self.run_id,
            "SHUTDOWN_COMPLETE",
            "Shutdown manager completed.",
            severity="WARNING",
            details={"reason": reason}
        ))

Hook it:
shutdown_manager = None

def handle_signal(signum, frame):
    if shutdown_manager is not None:
        shutdown_manager.request_shutdown("signal %s" % signum)

signal.signal(signal.SIGINT, handle_signal)

if hasattr(signal, "SIGTERM"):
    signal.signal(signal.SIGTERM, handle_signal)

atexit.register(lambda: shutdown_manager and shutdown_manager.request_shutdown("atexit"))

Rule:
Shutdown is a sequence, not a boolean.

15. Top-Level Main Pattern
def main():
    run_id = time.strftime("run_%Y%m%d_%H%M%S")

    shutdown_event = threading.Event()
    safe_state_event = threading.Event()

    telemetry_queue = queue.Queue(maxsize=10000)
    writer_queue = queue.Queue(maxsize=50000)
    event_queue = queue.Queue(maxsize=10000)
    command_queue = queue.PriorityQueue()

    acquisition_adapter = SimulatedLabJackAdapter(
        channels=["AIN0", "AIN1", "AIN2", "AIN3"]
    )

    control_adapter = SimulatedLabJackAdapter(device_id="sim_control")

    acquisition_thread = AcquisitionThread(
        adapter=acquisition_adapter,
        channel_map=CHANNEL_MAP,
        telemetry_queue=telemetry_queue,
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        sample_interval_s=1.0,
        run_id=run_id,
    )

    writer_thread = CsvWriterThread(
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        csv_path=os.path.join("runtime_data", "runs", run_id, "raw_data.csv"),
    )

    command_thread = CommandThread(
        control_adapter=control_adapter,
        command_queue=command_queue,
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        safe_state_event=safe_state_event,
        run_id=run_id,
    )

    threads = [
        ("writer", writer_thread),
        ("acquisition", acquisition_thread),
        ("command", command_thread),
    ]

    manager = ShutdownManager(
        shutdown_event=shutdown_event,
        safe_state_event=safe_state_event,
        threads=threads,
        event_queue=event_queue,
        writer_queue=writer_queue,
        run_id=run_id,
    )

    try:
        writer_thread.start()
        command_thread.start()
        acquisition_thread.start()

        # Replace this loop with GUI event loop in GUI apps.
        while not shutdown_event.is_set():
            try:
                event = event_queue.get(timeout=0.5)
                print("[EVENT]", event.get("event_type"), event.get("message"))
            except queue.Empty:
                pass

    except KeyboardInterrupt:
        manager.request_shutdown("KeyboardInterrupt")

    except Exception:
        event_queue.put(make_event_record(
            run_id,
            "MAIN_EXCEPTION",
            "Unhandled exception in main.",
            severity="CRITICAL",
            details={"traceback": traceback.format_exc()}
        ))
        manager.request_shutdown("main exception")
        return 1

    finally:
        manager.request_shutdown("main finally")

    return 0

Startup order:
1. Writer first.
2. Command/safe-state path early.
3. Acquisition after writer exists.
4. GUI after backend queues/threads exist, or GUI first with backend start controlled.

For real hardware, never auto-enable outputs during startup.

16. Diagnostic Harness Snippet
def collect_thread_diagnostics(threads):
    report = {}

    for name, thread in threads:
        diag = {
            "alive": thread.is_alive(),
            "class": thread.__class__.__name__,
        }

        if hasattr(thread, "diagnostics"):
            try:
                diag.update(thread.diagnostics())
            except Exception as exc:
                diag["diagnostics_error"] = repr(exc)

        report[name] = diag

    return report

def write_diagnostic_report(path, threads, queues, extra=None):
    lines = []
    lines.append("DAQ CONTROL DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("python: %s" % sys.version)
    lines.append("platform: %s" % sys.platform)
    lines.append("cwd: %s" % os.getcwd())
    lines.append("")

    lines.append("THREADS")
    lines.append("-" * 72)
    thread_diag = collect_thread_diagnostics(threads)
    lines.append(json.dumps(thread_diag, indent=2, sort_keys=True))
    lines.append("")

    lines.append("QUEUES")
    lines.append("-" * 72)
    for name, q in queues:
        try:
            lines.append("%s: qsize=%s" % (name, q.qsize()))
        except Exception as exc:
            lines.append("%s: qsize error=%s" % (name, repr(exc)))
    lines.append("")

    if extra:
        lines.append("EXTRA")
        lines.append("-" * 72)
        lines.append(json.dumps(extra, indent=2, sort_keys=True))
        lines.append("")

    folder = os.path.dirname(os.path.abspath(path))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    with open(path, "w") as f:
        f.write("\n".join(lines))

    return path

Diagnostics should be callable without launching the full GUI.

17. Safe GUI Button Pattern
A GUI button should not command hardware directly.
Bad:
def on_output_off_clicked(self):
    self.psu.write("OUTP OFF")

Better:
def on_output_off_clicked(self):
    self.command_queue.put(make_priority_command(
        PRIORITY_OPERATOR_STOP,
        {
            "command_type": "OUTPUT_OFF",
            "device_id": "genesys_psu",
            "payload": {},
            "command_id": "operator_output_off_%s" % int(time.time()),
        }
    ))

Best for emergency/safe state:
def on_safe_state_clicked(self):
    self.safe_state_event.set()
    self.command_queue.put(make_safe_state_command("operator safe-state button"))

The GUI requests.
The command thread executes.
The writer records.
The status panel confirms.

18. Sequence Executor Pattern
class SequenceExecutorThread(threading.Thread):
    def __init__(self, sequence, command_queue, event_queue, shutdown_event, safe_state_event, run_id):
        threading.Thread.__init__(self)
        self.daemon = False
        self.sequence = sequence
        self.command_queue = command_queue
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.safe_state_event = safe_state_event
        self.run_id = run_id
        self.active_step_index = None
        self.state = "IDLE"

    def run(self):
        self.state = "SEQUENCE_RUNNING"
        self.event_queue.put(make_event_record(
            self.run_id,
            "SEQUENCE_START",
            "Sequence started.",
            details={"steps": len(self.sequence)}
        ))

        try:
            for index, step in enumerate(self.sequence):
                if self.shutdown_event.is_set() or self.safe_state_event.is_set():
                    self.state = "ABORTED"
                    break

                self.active_step_index = index
                self._execute_step(index, step)

            if self.state != "ABORTED":
                self.state = "SEQUENCE_COMPLETE"
                self.event_queue.put(make_event_record(
                    self.run_id,
                    "SEQUENCE_COMPLETE",
                    "Sequence completed."
                ))

        except Exception:
            self.state = "FAULTED"
            self.safe_state_event.set()
            self.event_queue.put(make_event_record(
                self.run_id,
                "SEQUENCE_FAULT",
                "Sequence fault. Safe state requested.",
                severity="CRITICAL",
                details={"traceback": traceback.format_exc()}
            ))

    def _execute_step(self, index, step):
        step_type = step.get("type")

        if step_type == "hold":
            self._hold(step.get("duration_s", 0))

        elif step_type == "set":
            self.command_queue.put(make_priority_command(
                PRIORITY_SEQUENCE_COMMAND,
                {
                    "command_type": "SET_VOLTAGE_CURRENT",
                    "device_id": "genesys_psu",
                    "payload": {
                        "voltage": step["voltage"],
                        "current": step["current"],
                    },
                    "command_id": "seq_%s_step_%s" % (self.run_id, index),
                }
            ))

        else:
            raise ValueError("Unknown step type: %s" % step_type)

    def _hold(self, duration_s):
        end_time = time_monotonic() + duration_s

        while time_monotonic() < end_time:
            if self.shutdown_event.is_set() or self.safe_state_event.is_set():
                return
            time.sleep(0.05)

    def diagnostics(self):
        return {
            "thread": "SequenceExecutorThread",
            "alive": self.is_alive(),
            "state": self.state,
            "active_step_index": self.active_step_index,
        }

Rule:
The sequence executor should request commands.
It should not directly write to the PSU.

19. Health Monitor Pattern
class HealthMonitorThread(threading.Thread):
    def __init__(self, monitored_threads, event_queue, shutdown_event, run_id, check_interval_s=1.0):
        threading.Thread.__init__(self)
        self.daemon = False
        self.monitored_threads = monitored_threads
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.run_id = run_id
        self.check_interval_s = check_interval_s
        self.last_status = {}

    def run(self):
        while not self.shutdown_event.is_set():
            for name, thread in self.monitored_threads:
                alive = thread.is_alive()

                previous = self.last_status.get(name)

                if previous is not None and previous is True and alive is False:
                    self.event_queue.put(make_event_record(
                        self.run_id,
                        "THREAD_DIED",
                        "Monitored thread stopped unexpectedly.",
                        severity="CRITICAL",
                        details={"thread": name}
                    ))

                self.last_status[name] = alive

            time.sleep(self.check_interval_s)

Useful additions:
- telemetry age check;
- writer queue backlog check;
- command queue backlog check;
- device heartbeat age;
- disk free space check;
- historian write age;
- GUI update age.

20. Fault Handling Pattern
class FaultManager(object):
    def __init__(self, event_queue, safe_state_event, run_id):
        self.event_queue = event_queue
        self.safe_state_event = safe_state_event
        self.run_id = run_id
        self.active_faults = {}

    def raise_fault(self, fault_id, message, severity="ERROR", details=None, safe_state=False):
        if fault_id not in self.active_faults:
            self.active_faults[fault_id] = {
                "started_at": time.time(),
                "message": message,
                "severity": severity,
                "count": 1,
            }

            self.event_queue.put(make_event_record(
                self.run_id,
                "FAULT_START",
                message,
                severity=severity,
                details=details or {}
            ))

        else:
            self.active_faults[fault_id]["count"] += 1

        if safe_state:
            self.safe_state_event.set()

    def clear_fault(self, fault_id):
        fault = self.active_faults.pop(fault_id, None)

        if fault is not None:
            duration = time.time() - fault["started_at"]
            self.event_queue.put(make_event_record(
                self.run_id,
                "FAULT_END",
                fault["message"],
                severity=fault["severity"],
                details={
                    "fault_id": fault_id,
                    "duration_s": duration,
                    "count": fault["count"],
                }
            ))

This avoids log spam while preserving fault start/end evidence.

21. Run Manifest Pattern
def create_run_manifest(run_folder, app_version, settings_path):
    if not os.path.isdir(run_folder):
        os.makedirs(run_folder)

    run_id = os.path.basename(run_folder)

    manifest = {
        "run_id": run_id,
        "app_version": app_version,
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ended_at": "",
        "settings_path": settings_path,
        "raw_data_path": os.path.join(run_folder, "raw_data.csv"),
        "events_path": os.path.join(run_folder, "events.csv"),
        "commands_path": os.path.join(run_folder, "commands.csv"),
        "shutdown_status": "RUNNING",
        "abnormal_shutdown_detected": False,
    }

    path = os.path.join(run_folder, "run_manifest.json")

    with open(path, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    return path, manifest

def update_run_manifest(path, **updates):
    try:
        with open(path, "r") as f:
            manifest = json.load(f)
    except Exception:
        manifest = {}

    manifest.update(updates)

    tmp = path + ".tmp"

    with open(tmp, "w") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    if os.path.exists(path):
        os.remove(path)

    os.rename(tmp, path)

At shutdown:
update_run_manifest(
    manifest_path,
    ended_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    shutdown_status="CLEAN"
)

On exception:
update_run_manifest(
    manifest_path,
    ended_at=time.strftime("%Y-%m-%d %H:%M:%S"),
    shutdown_status="ABNORMAL",
    abnormal_shutdown_detected=True
)

22. Minimal Acceptance Test Harness
def run_threading_smoke_test():
    run_id = "smoke_%s" % time.strftime("%Y%m%d_%H%M%S")

    shutdown_event = threading.Event()
    safe_state_event = threading.Event()

    telemetry_queue = queue.Queue(maxsize=1000)
    writer_queue = queue.Queue(maxsize=5000)
    event_queue = queue.Queue(maxsize=1000)
    command_queue = queue.PriorityQueue()

    adapter = SimulatedLabJackAdapter(channels=["AIN0", "AIN1"])
    control = SimulatedLabJackAdapter(device_id="sim_control")

    acq = AcquisitionThread(
        adapter=adapter,
        channel_map=CHANNEL_MAP,
        telemetry_queue=telemetry_queue,
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        sample_interval_s=0.1,
        run_id=run_id,
    )

    writer_path = os.path.join("runtime_data", "test_reports", run_id + "_raw.csv")

    writer = CsvWriterThread(
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        csv_path=writer_path,
        flush_interval_s=0.5,
    )

    cmd = CommandThread(
        control_adapter=control,
        command_queue=command_queue,
        writer_queue=writer_queue,
        event_queue=event_queue,
        shutdown_event=shutdown_event,
        safe_state_event=safe_state_event,
        run_id=run_id,
    )

    writer.start()
    cmd.start()
    acq.start()

    time.sleep(2.0)

    command_queue.put(make_safe_state_command("smoke test"))

    time.sleep(0.5)

    shutdown_event.set()
    safe_state_event.set()

    acq.join(3.0)
    cmd.join(3.0)
    writer.join(3.0)

    passed = True
    failures = []

    if acq.is_alive():
        passed = False
        failures.append("Acquisition thread did not stop.")

    if cmd.is_alive():
        passed = False
        failures.append("Command thread did not stop.")

    if writer.is_alive():
        passed = False
        failures.append("Writer thread did not stop.")

    if not os.path.isfile(writer_path):
        passed = False
        failures.append("Writer CSV was not created.")

    return {
        "passed": passed,
        "failures": failures,
        "writer_path": writer_path,
        "run_id": run_id,
    }

This should become:
tools/package_smoke_test.py

23. Threading Rules Summary
THREAD-RULE-001
Do not update GUI widgets from acquisition, command, writer, or health threads.

THREAD-RULE-002
Only one thread owns a hardware command path.

THREAD-RULE-003
Only one writer owns a file/database connection unless a locking policy is explicit.

THREAD-RULE-004
Safe-state must have priority over normal commands.

THREAD-RULE-005
Shutdown must drain or explicitly abandon queues with a logged reason.

THREAD-RULE-006
GUI queues may drop display data.
Raw data queues must not silently drop records.

THREAD-RULE-007
Simulated devices should be available before real-device-only testing.

THREAD-RULE-008
Every long-running thread should expose diagnostics.

THREAD-RULE-009
Thread failure should be visible in the UI/logs.

THREAD-RULE-010
A thread that catches exceptions must report them.
Silent except blocks are not allowed in acquisition/control paths.

24. Practical Folder Placement
Recommended code placement after formalization:
project_name/
├── threading_utils.py
├── messages.py
├── devices/
│   ├── base.py
│   ├── labjack_u6.py
│   ├── genesys_psu.py
│   └── simulated.py
├── acquisition/
│   ├── acquisition_thread.py
│   └── channel_map.py
├── control/
│   ├── command_thread.py
│   ├── safety.py
│   └── sequence_executor.py
├── storage/
│   ├── csv_writer.py
│   ├── sqlite_writer.py
│   └── run_manifest.py
├── diagnostics/
│   ├── report.py
│   └── health_monitor.py
└── ui/
    ├── main_window.py
    ├── graph_panel.py
    └── status_panel.py

In a monolithic prototype, these should still exist as clearly separated sections.

25. Core Pattern
The safest general structure is:
hardware reads
    → acquisition thread
        → telemetry queue for GUI
        → writer queue for raw storage

operator actions
    → GUI event
        → command queue / safe-state event
            → command thread
                → hardware command
                → command record to writer

storage
    → writer thread
        → CSV/SQLite
        → flush/recovery

health
    → health monitor
        → event queue
        → UI/log/diagnostics

shutdown
    → safe-state first
    → stop acquisition/control
    → drain writer
    → write manifest
    → write diagnostic report if abnormal

That is the architecture we should keep returning to for DAQ/control work.

QC and Defect Detection
Yes. I’d make this a dedicated document because inline QC / defect detection is its own software doctrine. It overlaps with DAQ and historian design, but it has different core problems: defect taxonomy, evidence capture, review/adjudication, database traceability, algorithm versioning, and later correlation with performance data.
Recommended file:
