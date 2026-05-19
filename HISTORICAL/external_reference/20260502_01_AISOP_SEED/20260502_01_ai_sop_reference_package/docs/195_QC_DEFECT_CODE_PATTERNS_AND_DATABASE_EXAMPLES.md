---
document_id: DOC-195
title: "QC/Defect Code Patterns and Database Examples"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-195
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# QC/Defect Code Patterns and Database Examples

This is the code-specific appendix to the QC doctrine: detection queues, evidence capture, SQLite schema, defect/review records, performance linking, audits, and safe threading patterns. It follows the AISOP style of making diagnostics, schema, persistence, acceptance tests, and package structure explicit rather than relying on memory.
# 195_QC_DEFECT_CODE_PATTERNS_AND_DATABASE_EXAMPLES

## 0. Purpose

This document provides concrete code patterns for inline QC, defect detection, evidence capture, review workflows, database storage, and later performance correlation.

It supports systems that:

- detect defects live;
- save evidence artifacts;
- classify candidate defects;
- allow operator/engineer review;
- preserve raw evidence;
- store structured records in SQLite;
- cross-reference QC data with later performance data;
- audit database/evidence integrity;
- diagnose failures on machines we cannot directly inspect.

This is not a full application.

It is a pattern library.

The goal is to show how a QC/defect system should be structured in code so the generalized doctrine can be implemented consistently.

---

## 1. Preferred Architecture

The recommended structure is:

```text
input acquisition
    ↓
input validation
    ↓
raw evidence capture
    ↓
detection engine
    ↓
candidate detection record
    ↓
database writer
    ↓
review queue
    ↓
defect confirmation / false positive / disposition
    ↓
performance-data linking
    ↓
correlation analysis

Separate these responsibilities:
acquisition
    gets images/sensor data/files

detection
    finds candidate defects

evidence store
    saves raw/processed/annotated evidence

database layer
    writes structured records

review layer
    records human decisions

performance-link layer
    imports and joins downstream performance results

analysis layer
    computes trends/correlations

UI layer
    displays records and evidence; does not own truth

Core rule:
A detection does not become truth just because the algorithm produced it.

Candidate detections, confirmed defects, evidence artifacts, and review decisions should be separate database concepts.

2. Recommended Libraries
2.1 Conservative baseline
import os
import sys
import time
import json
import csv
import uuid
import sqlite3
import hashlib
import shutil
import queue
import threading
import traceback
from datetime import datetime

For Python 2 compatibility:
try:
    import queue
except ImportError:
    import Queue as queue

try:
    text_type = unicode
except NameError:
    text_type = str

2.2 Optional libraries
Use only when target-tested:
Pillow / PIL:
    image loading, crops, thumbnails, annotations

OpenCV:
    image processing, contours, thresholds, camera feeds

numpy:
    numeric image/signal processing

pandas:
    offline analysis, exports, correlation tables

matplotlib:
    plots/reports

PyQt / Tkinter / Kivy:
    review UI depending on target environment

Rule:
The database, evidence audit, and diagnostic harness should not require the GUI.

3. Runtime Folder Structure
Recommended runtime layout:
runtime_data/
├── qc_database/
│   └── inline_qc.sqlite
│
├── evidence/
│   ├── raw/
│   ├── processed/
│   ├── annotated/
│   └── imported/
│
├── exports/
│   ├── csv/
│   ├── reports/
│   └── plots/
│
├── logs/
│   ├── qc_app.log
│   ├── detection.log
│   ├── review.log
│   └── database.log
│
├── diagnostics/
│   ├── qc_diagnostic_report.txt
│   ├── qc_db_integrity_report.txt
│   └── qc_evidence_audit_report.txt
│
└── autosave/
    └── review_session_state.json

Helper:
def safe_makedirs(path):
    if path and not os.path.isdir(path):
        os.makedirs(path)

def get_runtime_root():
    return os.path.join(os.getcwd(), "runtime_data")

def get_qc_db_path():
    return os.path.join(get_runtime_root(), "qc_database", "inline_qc.sqlite")

def get_evidence_root():
    return os.path.join(get_runtime_root(), "evidence")

def initialize_qc_runtime_folders():
    folders = [
        os.path.join(get_runtime_root(), "qc_database"),
        os.path.join(get_evidence_root(), "raw"),
        os.path.join(get_evidence_root(), "processed"),
        os.path.join(get_evidence_root(), "annotated"),
        os.path.join(get_evidence_root(), "imported"),
        os.path.join(get_runtime_root(), "exports", "csv"),
        os.path.join(get_runtime_root(), "exports", "reports"),
        os.path.join(get_runtime_root(), "exports", "plots"),
        os.path.join(get_runtime_root(), "logs"),
        os.path.join(get_runtime_root(), "diagnostics"),
        os.path.join(get_runtime_root(), "autosave"),
    ]

    for folder in folders:
        safe_makedirs(folder)

4. IDs and Timestamps
Use stable IDs everywhere.
def new_id(prefix):
    return "%s_%s" % (prefix, uuid.uuid4().hex)

def now_iso():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def now_epoch():
    return time.time()

Recommended prefixes:
lot_
part_
inspection_
detection_
defect_
evidence_
review_
perf_
algorithm_
analysis_

5. SQLite Schema Pattern
5.1 Database initialization
SCHEMA_VERSION = 1

def open_qc_db(db_path=None):
    if db_path is None:
        db_path = get_qc_db_path()

    safe_makedirs(os.path.dirname(os.path.abspath(db_path)))

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    initialize_qc_schema(conn)
    return conn

5.2 Schema
def initialize_qc_schema(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_info (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    conn.execute("""
        INSERT OR REPLACE INTO schema_info (key, value)
        VALUES ('schema_version', ?)
    """, (str(SCHEMA_VERSION),))

    conn.execute("""
        CREATE TABLE IF NOT EXISTS lots (
            lot_id TEXT PRIMARY KEY,
            product_name TEXT,
            created_at TEXT,
            notes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            part_id TEXT PRIMARY KEY,
            lot_id TEXT,
            serial_number TEXT,
            part_type TEXT,
            created_at TEXT,
            status TEXT,
            notes TEXT,
            FOREIGN KEY(lot_id) REFERENCES lots(lot_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS algorithm_versions (
            algorithm_version_id TEXT PRIMARY KEY,
            detector_name TEXT NOT NULL,
            detector_type TEXT,
            version TEXT NOT NULL,
            parameter_json TEXT,
            code_version TEXT,
            created_at TEXT,
            notes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS inspection_events (
            inspection_event_id TEXT PRIMARY KEY,
            part_id TEXT,
            lot_id TEXT,
            station_id TEXT,
            process_step TEXT,
            started_at TEXT,
            ended_at TEXT,
            operator_id TEXT,
            notes TEXT,
            FOREIGN KEY(part_id) REFERENCES parts(part_id),
            FOREIGN KEY(lot_id) REFERENCES lots(lot_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS evidence_artifacts (
            evidence_id TEXT PRIMARY KEY,
            linked_record_type TEXT,
            linked_record_id TEXT,
            artifact_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            relative_path TEXT,
            content_hash TEXT,
            hash_algorithm TEXT,
            file_size_bytes INTEGER,
            captured_at TEXT,
            created_at TEXT,
            source_device TEXT,
            format TEXT,
            width INTEGER,
            height INTEGER,
            is_raw INTEGER,
            is_processed INTEGER,
            processing_version TEXT,
            notes TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            detection_id TEXT PRIMARY KEY,
            inspection_event_id TEXT,
            part_id TEXT,
            lot_id TEXT,
            timestamp TEXT NOT NULL,
            detector_name TEXT NOT NULL,
            detector_type TEXT,
            algorithm_version_id TEXT,
            candidate_type TEXT NOT NULL,
            location_x REAL,
            location_y REAL,
            location_z REAL,
            location_units TEXT,
            region_id TEXT,
            severity_estimate TEXT,
            confidence REAL,
            raw_score REAL,
            threshold_value REAL,
            measurement_value REAL,
            measurement_units TEXT,
            quality_flag TEXT,
            evidence_id TEXT,
            review_status TEXT NOT NULL,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY(inspection_event_id) REFERENCES inspection_events(inspection_event_id),
            FOREIGN KEY(part_id) REFERENCES parts(part_id),
            FOREIGN KEY(lot_id) REFERENCES lots(lot_id),
            FOREIGN KEY(algorithm_version_id) REFERENCES algorithm_versions(algorithm_version_id),
            FOREIGN KEY(evidence_id) REFERENCES evidence_artifacts(evidence_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS defects (
            defect_id TEXT PRIMARY KEY,
            source_detection_id TEXT,
            part_id TEXT,
            lot_id TEXT,
            defect_family TEXT,
            defect_type TEXT NOT NULL,
            defect_subtype TEXT,
            severity TEXT NOT NULL,
            criticality TEXT,
            confidence REAL,
            location_description TEXT,
            location_x REAL,
            location_y REAL,
            location_z REAL,
            location_units TEXT,
            area REAL,
            length REAL,
            width REAL,
            depth REAL,
            count INTEGER,
            review_status TEXT,
            disposition TEXT,
            rework_status TEXT,
            evidence_primary_id TEXT,
            created_by TEXT,
            created_at TEXT,
            updated_at TEXT,
            closed_at TEXT,
            notes TEXT,
            FOREIGN KEY(source_detection_id) REFERENCES detections(detection_id),
            FOREIGN KEY(part_id) REFERENCES parts(part_id),
            FOREIGN KEY(lot_id) REFERENCES lots(lot_id),
            FOREIGN KEY(evidence_primary_id) REFERENCES evidence_artifacts(evidence_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS review_decisions (
            review_id TEXT PRIMARY KEY,
            linked_record_type TEXT NOT NULL,
            linked_record_id TEXT NOT NULL,
            reviewer_id TEXT,
            reviewed_at TEXT,
            review_outcome TEXT NOT NULL,
            review_confidence REAL,
            prior_classification TEXT,
            new_classification TEXT,
            prior_severity TEXT,
            new_severity TEXT,
            reason TEXT,
            notes TEXT,
            supersedes_review_id TEXT,
            accepted_as_current INTEGER
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS performance_results (
            performance_result_id TEXT PRIMARY KEY,
            part_id TEXT,
            lot_id TEXT,
            test_id TEXT,
            test_type TEXT,
            test_station TEXT,
            started_at TEXT,
            ended_at TEXT,
            metric_name TEXT NOT NULL,
            metric_value REAL,
            metric_units TEXT,
            operating_condition TEXT,
            run_id TEXT,
            data_file_path TEXT,
            historian_reference TEXT,
            quality_flag TEXT,
            notes TEXT,
            FOREIGN KEY(part_id) REFERENCES parts(part_id),
            FOREIGN KEY(lot_id) REFERENCES lots(lot_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS event_log (
            event_id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            severity TEXT,
            event_type TEXT,
            message TEXT,
            details_json TEXT
        )
    """)

    conn.commit()

Indexes:
def initialize_qc_indexes(conn):
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_detections_part ON detections(part_id)",
        "CREATE INDEX IF NOT EXISTS idx_detections_lot ON detections(lot_id)",
        "CREATE INDEX IF NOT EXISTS idx_detections_review ON detections(review_status)",
        "CREATE INDEX IF NOT EXISTS idx_detections_algorithm ON detections(algorithm_version_id)",
        "CREATE INDEX IF NOT EXISTS idx_defects_part ON defects(part_id)",
        "CREATE INDEX IF NOT EXISTS idx_defects_lot ON defects(lot_id)",
        "CREATE INDEX IF NOT EXISTS idx_defects_type ON defects(defect_type)",
        "CREATE INDEX IF NOT EXISTS idx_perf_part ON performance_results(part_id)",
        "CREATE INDEX IF NOT EXISTS idx_perf_metric ON performance_results(metric_name)",
    ]

    for sql in indexes:
        conn.execute(sql)

    conn.commit()

6. Evidence Store Pattern
6.1 File hashing
def hash_file(path, chunk_size=1024 * 1024):
    h = hashlib.sha256()

    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)

    return h.hexdigest()

6.2 Evidence path generation
def evidence_subfolder(kind, lot_id, part_id):
    lot_id = lot_id or "unknown_lot"
    part_id = part_id or "unknown_part"
    folder = os.path.join(get_evidence_root(), kind, lot_id, part_id)
    safe_makedirs(folder)
    return folder

def make_evidence_filename(evidence_id, extension):
    extension = extension.lower().lstrip(".")
    return "%s.%s" % (evidence_id, extension)

6.3 Save evidence artifact
def save_evidence_artifact(
    conn,
    source_path,
    artifact_type,
    linked_record_type="",
    linked_record_id="",
    lot_id="",
    part_id="",
    evidence_kind="raw",
    notes="",
):
    """
    Copies evidence into managed runtime evidence storage and records metadata.

    Does not modify the source file.
    """
    if not os.path.isfile(source_path):
        raise IOError("Evidence source file does not exist: %s" % source_path)

    evidence_id = new_id("evidence")
    _, ext = os.path.splitext(source_path)
    if not ext:
        ext = ".bin"

    target_folder = evidence_subfolder(evidence_kind, lot_id, part_id)
    target_name = make_evidence_filename(evidence_id, ext)
    target_path = os.path.join(target_folder, target_name)

    shutil.copy2(source_path, target_path)

    content_hash = hash_file(target_path)
    file_size = os.path.getsize(target_path)

    relative_path = os.path.relpath(target_path, get_runtime_root())

    conn.execute("""
        INSERT INTO evidence_artifacts (
            evidence_id,
            linked_record_type,
            linked_record_id,
            artifact_type,
            file_path,
            relative_path,
            content_hash,
            hash_algorithm,
            file_size_bytes,
            captured_at,
            created_at,
            source_device,
            format,
            is_raw,
            is_processed,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        evidence_id,
        linked_record_type,
        linked_record_id,
        artifact_type,
        target_path,
        relative_path,
        content_hash,
        "sha256",
        file_size,
        now_iso(),
        now_iso(),
        "",
        ext.lower().lstrip("."),
        1 if evidence_kind == "raw" else 0,
        1 if evidence_kind != "raw" else 0,
        notes,
    ))

    conn.commit()

    return evidence_id, target_path

Rule:
Raw evidence is copied into managed storage.
Processed/annotated evidence becomes a separate artifact.
Never overwrite raw evidence.

7. Detection Record Pattern
7.1 Register algorithm version
def register_algorithm_version(
    conn,
    detector_name,
    version,
    detector_type="rule_based",
    parameters=None,
    code_version="",
    notes="",
):
    algorithm_version_id = new_id("algorithm")

    conn.execute("""
        INSERT INTO algorithm_versions (
            algorithm_version_id,
            detector_name,
            detector_type,
            version,
            parameter_json,
            code_version,
            created_at,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        algorithm_version_id,
        detector_name,
        detector_type,
        version,
        json.dumps(parameters or {}, sort_keys=True),
        code_version,
        now_iso(),
        notes,
    ))

    conn.commit()
    return algorithm_version_id

7.2 Insert candidate detection
def insert_detection(
    conn,
    inspection_event_id,
    part_id,
    lot_id,
    detector_name,
    detector_type,
    algorithm_version_id,
    candidate_type,
    confidence,
    evidence_id=None,
    location_x=None,
    location_y=None,
    location_z=None,
    location_units="px",
    severity_estimate="UNKNOWN",
    raw_score=None,
    threshold_value=None,
    measurement_value=None,
    measurement_units="",
    quality_flag="GOOD",
):
    detection_id = new_id("detection")

    conn.execute("""
        INSERT INTO detections (
            detection_id,
            inspection_event_id,
            part_id,
            lot_id,
            timestamp,
            detector_name,
            detector_type,
            algorithm_version_id,
            candidate_type,
            location_x,
            location_y,
            location_z,
            location_units,
            severity_estimate,
            confidence,
            raw_score,
            threshold_value,
            measurement_value,
            measurement_units,
            quality_flag,
            evidence_id,
            review_status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        detection_id,
        inspection_event_id,
        part_id,
        lot_id,
        now_iso(),
        detector_name,
        detector_type,
        algorithm_version_id,
        candidate_type,
        location_x,
        location_y,
        location_z,
        location_units,
        severity_estimate,
        confidence,
        raw_score,
        threshold_value,
        measurement_value,
        measurement_units,
        quality_flag,
        evidence_id,
        "UNREVIEWED",
        now_iso(),
        now_iso(),
    ))

    conn.commit()
    return detection_id

8. Simple Detector Patterns
8.1 Base detector
class DetectorBase(object):
    detector_name = "base_detector"
    detector_type = "base"
    version = "0.0.0"

    def detect(self, input_record):
        """
        Return a list of candidate detection dictionaries.
        """
        raise NotImplementedError

    def parameter_snapshot(self):
        return {}

8.2 Threshold detector for scalar data
class ThresholdDetector(DetectorBase):
    detector_name = "threshold_detector"
    detector_type = "scalar_threshold"
    version = "1.0.0"

    def __init__(self, signal_name, high_limit=None, low_limit=None):
        self.signal_name = signal_name
        self.high_limit = high_limit
        self.low_limit = low_limit

    def parameter_snapshot(self):
        return {
            "signal_name": self.signal_name,
            "high_limit": self.high_limit,
            "low_limit": self.low_limit,
        }

    def detect(self, input_record):
        detections = []

        if input_record.get("signal_name") != self.signal_name:
            return detections

        value = input_record.get("value")
        if value is None:
            return detections

        if self.high_limit is not None and value > self.high_limit:
            detections.append({
                "candidate_type": "HIGH_THRESHOLD_EXCURSION",
                "confidence": 1.0,
                "severity_estimate": "MODERATE",
                "raw_score": value,
                "threshold_value": self.high_limit,
                "measurement_value": value,
                "measurement_units": input_record.get("units", ""),
            })

        if self.low_limit is not None and value < self.low_limit:
            detections.append({
                "candidate_type": "LOW_THRESHOLD_EXCURSION",
                "confidence": 1.0,
                "severity_estimate": "MODERATE",
                "raw_score": value,
                "threshold_value": self.low_limit,
                "measurement_value": value,
                "measurement_units": input_record.get("units", ""),
            })

        return detections

8.3 Image detector placeholder
class BrightSpotImageDetector(DetectorBase):
    detector_name = "bright_spot_detector"
    detector_type = "image_rule"
    version = "1.0.0"

    def __init__(self, threshold=240, min_area_px=5):
        self.threshold = threshold
        self.min_area_px = min_area_px

    def parameter_snapshot(self):
        return {
            "threshold": self.threshold,
            "min_area_px": self.min_area_px,
        }

    def detect(self, input_record):
        """
        Example expects input_record to include:
        - image_path
        - part_id
        - lot_id

        Real implementation may use PIL/OpenCV.
        """
        image_path = input_record.get("image_path")
        if not image_path or not os.path.isfile(image_path):
            return []

        # Placeholder: real image processing would go here.
        # Return one fake detection to show structure.
        return [{
            "candidate_type": "BRIGHT_SPOT",
            "confidence": 0.75,
            "severity_estimate": "MINOR",
            "location_x": 100,
            "location_y": 200,
            "location_units": "px",
            "raw_score": 250,
            "threshold_value": self.threshold,
            "measurement_value": 250,
            "measurement_units": "intensity",
            "source_image_path": image_path,
        }]

9. Detection Pipeline Pattern
The detection pipeline should:
1. validate input;
2. preserve evidence;
3. run detector;
4. write candidate detection;
5. publish event/update.
def process_input_record(
    conn,
    input_record,
    detectors,
    algorithm_version_ids,
    inspection_event_id,
):
    """
    Processes one image/sensor/file input record through one or more detectors.
    """
    part_id = input_record.get("part_id", "")
    lot_id = input_record.get("lot_id", "")

    created_detection_ids = []

    for detector in detectors:
        candidates = detector.detect(input_record)

        for candidate in candidates:
            evidence_id = None

            source_image_path = candidate.get("source_image_path") or input_record.get("image_path")
            if source_image_path:
                evidence_id, _ = save_evidence_artifact(
                    conn,
                    source_path=source_image_path,
                    artifact_type="IMAGE_RAW",
                    linked_record_type="detection",
                    linked_record_id="pending",
                    lot_id=lot_id,
                    part_id=part_id,
                    evidence_kind="raw",
                    notes="Raw evidence captured during detection."
                )

            algorithm_version_id = algorithm_version_ids.get(detector.detector_name)

            detection_id = insert_detection(
                conn=conn,
                inspection_event_id=inspection_event_id,
                part_id=part_id,
                lot_id=lot_id,
                detector_name=detector.detector_name,
                detector_type=detector.detector_type,
                algorithm_version_id=algorithm_version_id,
                candidate_type=candidate.get("candidate_type", "UNKNOWN"),
                confidence=candidate.get("confidence"),
                evidence_id=evidence_id,
                location_x=candidate.get("location_x"),
                location_y=candidate.get("location_y"),
                location_z=candidate.get("location_z"),
                location_units=candidate.get("location_units", ""),
                severity_estimate=candidate.get("severity_estimate", "UNKNOWN"),
                raw_score=candidate.get("raw_score"),
                threshold_value=candidate.get("threshold_value"),
                measurement_value=candidate.get("measurement_value"),
                measurement_units=candidate.get("measurement_units", ""),
                quality_flag="GOOD",
            )

            if evidence_id:
                conn.execute("""
                    UPDATE evidence_artifacts
                    SET linked_record_id = ?
                    WHERE evidence_id = ?
                """, (detection_id, evidence_id))
                conn.commit()

            created_detection_ids.append(detection_id)

    return created_detection_ids

10. Threaded QC Pipeline
10.1 Queue layout
input_queue = queue.Queue(maxsize=10000)
detection_queue = queue.Queue(maxsize=10000)
db_write_queue = queue.Queue(maxsize=50000)
ui_event_queue = queue.Queue(maxsize=10000)

shutdown_event = threading.Event()

Recommended flow:
acquisition thread
    → input_queue

detection thread
    → db_write_queue
    → ui_event_queue

database writer thread
    → SQLite

review UI thread
    → database actions through review service

10.2 Input acquisition thread
class InputAcquisitionThread(threading.Thread):
    def __init__(self, input_queue, ui_event_queue, shutdown_event, input_source):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.ui_event_queue = ui_event_queue
        self.shutdown_event = shutdown_event
        self.input_source = input_source
        self.daemon = False
        self.count = 0
        self.last_error = ""

    def run(self):
        while not self.shutdown_event.is_set():
            try:
                record = self.input_source.get_next_record()

                if record is None:
                    time.sleep(0.05)
                    continue

                record["acquired_at"] = now_iso()

                try:
                    self.input_queue.put(record, timeout=1.0)
                    self.count += 1
                except queue.Full:
                    self.ui_event_queue.put({
                        "type": "event",
                        "severity": "CRITICAL",
                        "message": "Input queue full. QC pipeline falling behind.",
                        "timestamp": now_iso(),
                    })

            except Exception as exc:
                self.last_error = repr(exc)
                self.ui_event_queue.put({
                    "type": "event",
                    "severity": "ERROR",
                    "message": "Input acquisition error.",
                    "timestamp": now_iso(),
                    "details": traceback.format_exc(),
                })
                time.sleep(0.5)

    def diagnostics(self):
        return {
            "thread": "InputAcquisitionThread",
            "alive": self.is_alive(),
            "count": self.count,
            "last_error": self.last_error,
            "input_queue_size": self.input_queue.qsize(),
        }

10.3 Detection thread
class DetectionThread(threading.Thread):
    def __init__(
        self,
        input_queue,
        db_write_queue,
        ui_event_queue,
        shutdown_event,
        detectors,
        inspection_event_id,
        algorithm_version_ids,
    ):
        threading.Thread.__init__(self)
        self.input_queue = input_queue
        self.db_write_queue = db_write_queue
        self.ui_event_queue = ui_event_queue
        self.shutdown_event = shutdown_event
        self.detectors = detectors
        self.inspection_event_id = inspection_event_id
        self.algorithm_version_ids = algorithm_version_ids
        self.daemon = False
        self.inputs_processed = 0
        self.candidates_found = 0
        self.last_error = ""

    def run(self):
        while not self.shutdown_event.is_set() or not self.input_queue.empty():
            try:
                input_record = self.input_queue.get(timeout=0.25)
            except queue.Empty:
                continue

            try:
                for detector in self.detectors:
                    candidates = detector.detect(input_record)

                    for candidate in candidates:
                        message = {
                            "type": "candidate_detection",
                            "inspection_event_id": self.inspection_event_id,
                            "input_record": input_record,
                            "candidate": candidate,
                            "detector_name": detector.detector_name,
                            "detector_type": detector.detector_type,
                            "algorithm_version_id": self.algorithm_version_ids.get(detector.detector_name),
                            "created_at": now_iso(),
                        }

                        self.db_write_queue.put(message, timeout=1.0)
                        self.candidates_found += 1

                        self.ui_event_queue.put({
                            "type": "candidate_detection",
                            "timestamp": now_iso(),
                            "candidate_type": candidate.get("candidate_type"),
                            "part_id": input_record.get("part_id"),
                            "lot_id": input_record.get("lot_id"),
                        })

                self.inputs_processed += 1

            except Exception as exc:
                self.last_error = repr(exc)
                self.ui_event_queue.put({
                    "type": "event",
                    "severity": "ERROR",
                    "message": "Detection thread error.",
                    "timestamp": now_iso(),
                    "details": traceback.format_exc(),
                })

    def diagnostics(self):
        return {
            "thread": "DetectionThread",
            "alive": self.is_alive(),
            "inputs_processed": self.inputs_processed,
            "candidates_found": self.candidates_found,
            "last_error": self.last_error,
            "input_queue_size": self.input_queue.qsize(),
            "db_write_queue_size": self.db_write_queue.qsize(),
        }

10.4 Database writer thread
Use one thread to own the SQLite connection.
class QCDatabaseWriterThread(threading.Thread):
    def __init__(self, db_path, db_write_queue, ui_event_queue, shutdown_event):
        threading.Thread.__init__(self)
        self.db_path = db_path
        self.db_write_queue = db_write_queue
        self.ui_event_queue = ui_event_queue
        self.shutdown_event = shutdown_event
        self.daemon = False
        self.records_written = 0
        self.last_error = ""

    def run(self):
        conn = None

        try:
            conn = open_qc_db(self.db_path)

            while not self.shutdown_event.is_set() or not self.db_write_queue.empty():
                try:
                    message = self.db_write_queue.get(timeout=0.25)
                except queue.Empty:
                    continue

                try:
                    self._handle_message(conn, message)
                    self.records_written += 1

                    if self.records_written % 50 == 0:
                        conn.commit()

                except Exception as exc:
                    self.last_error = repr(exc)
                    self.ui_event_queue.put({
                        "type": "event",
                        "severity": "CRITICAL",
                        "message": "QC database write failed.",
                        "timestamp": now_iso(),
                        "details": traceback.format_exc(),
                    })

            conn.commit()

        except Exception as exc:
            self.last_error = repr(exc)
            self.ui_event_queue.put({
                "type": "event",
                "severity": "CRITICAL",
                "message": "QC database writer fatal error.",
                "timestamp": now_iso(),
                "details": traceback.format_exc(),
            })

        finally:
            if conn is not None:
                try:
                    conn.commit()
                    conn.close()
                except Exception:
                    pass

    def _handle_message(self, conn, message):
        msg_type = message.get("type")

        if msg_type == "candidate_detection":
            self._write_candidate_detection(conn, message)
        elif msg_type == "event":
            self._write_event(conn, message)
        else:
            raise ValueError("Unknown DB write message type: %s" % msg_type)

    def _write_candidate_detection(self, conn, message):
        input_record = message["input_record"]
        candidate = message["candidate"]

        evidence_id = None

        source_path = candidate.get("source_image_path") or input_record.get("image_path")
        if source_path and os.path.isfile(source_path):
            evidence_id, _ = save_evidence_artifact(
                conn,
                source_path=source_path,
                artifact_type="IMAGE_RAW",
                linked_record_type="detection",
                linked_record_id="pending",
                lot_id=input_record.get("lot_id", ""),
                part_id=input_record.get("part_id", ""),
                evidence_kind="raw",
                notes="Raw evidence captured by DB writer."
            )

        detection_id = insert_detection(
            conn=conn,
            inspection_event_id=message.get("inspection_event_id", ""),
            part_id=input_record.get("part_id", ""),
            lot_id=input_record.get("lot_id", ""),
            detector_name=message.get("detector_name", ""),
            detector_type=message.get("detector_type", ""),
            algorithm_version_id=message.get("algorithm_version_id", ""),
            candidate_type=candidate.get("candidate_type", "UNKNOWN"),
            confidence=candidate.get("confidence"),
            evidence_id=evidence_id,
            location_x=candidate.get("location_x"),
            location_y=candidate.get("location_y"),
            location_z=candidate.get("location_z"),
            location_units=candidate.get("location_units", ""),
            severity_estimate=candidate.get("severity_estimate", "UNKNOWN"),
            raw_score=candidate.get("raw_score"),
            threshold_value=candidate.get("threshold_value"),
            measurement_value=candidate.get("measurement_value"),
            measurement_units=candidate.get("measurement_units", ""),
            quality_flag="GOOD",
        )

        if evidence_id:
            conn.execute("""
                UPDATE evidence_artifacts
                SET linked_record_id = ?
                WHERE evidence_id = ?
            """, (detection_id, evidence_id))

    def _write_event(self, conn, message):
        conn.execute("""
            INSERT INTO event_log (
                event_id,
                timestamp,
                severity,
                event_type,
                message,
                details_json
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            new_id("event"),
            message.get("timestamp", now_iso()),
            message.get("severity", "INFO"),
            message.get("event_type", message.get("type", "event")),
            message.get("message", ""),
            json.dumps(message.get("details", {}), sort_keys=True),
        ))

    def diagnostics(self):
        return {
            "thread": "QCDatabaseWriterThread",
            "alive": self.is_alive(),
            "db_path": self.db_path,
            "records_written": self.records_written,
            "last_error": self.last_error,
            "db_write_queue_size": self.db_write_queue.qsize(),
        }

Rule:
Detection threads may generate candidate messages.
The database writer owns SQLite writes.

11. Review Workflow Code
11.1 Fetch unreviewed detections
def fetch_unreviewed_detections(conn, limit=100):
    rows = conn.execute("""
        SELECT
            d.*,
            e.file_path AS evidence_file_path,
            e.artifact_type AS evidence_artifact_type
        FROM detections d
        LEFT JOIN evidence_artifacts e
            ON d.evidence_id = e.evidence_id
        WHERE d.review_status = 'UNREVIEWED'
        ORDER BY d.timestamp ASC
        LIMIT ?
    """, (limit,)).fetchall()

    return [dict(row) for row in rows]

11.2 Mark false positive
def mark_detection_false_positive(
    conn,
    detection_id,
    reviewer_id,
    reason="",
    notes="",
):
    review_id = new_id("review")

    row = conn.execute("""
        SELECT candidate_type, severity_estimate
        FROM detections
        WHERE detection_id = ?
    """, (detection_id,)).fetchone()

    if row is None:
        raise ValueError("Detection not found: %s" % detection_id)

    conn.execute("""
        INSERT INTO review_decisions (
            review_id,
            linked_record_type,
            linked_record_id,
            reviewer_id,
            reviewed_at,
            review_outcome,
            review_confidence,
            prior_classification,
            new_classification,
            prior_severity,
            new_severity,
            reason,
            notes,
            accepted_as_current
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review_id,
        "detection",
        detection_id,
        reviewer_id,
        now_iso(),
        "FALSE_POSITIVE",
        1.0,
        row["candidate_type"],
        "FALSE_POSITIVE",
        row["severity_estimate"],
        "NONE",
        reason,
        notes,
        1,
    ))

    conn.execute("""
        UPDATE detections
        SET review_status = 'FALSE_POSITIVE',
            updated_at = ?
        WHERE detection_id = ?
    """, (now_iso(), detection_id))

    conn.commit()
    return review_id

11.3 Confirm detection as defect
def confirm_detection_as_defect(
    conn,
    detection_id,
    reviewer_id,
    defect_family,
    defect_type,
    severity,
    disposition="PENDING",
    notes="",
):
    row = conn.execute("""
        SELECT *
        FROM detections
        WHERE detection_id = ?
    """, (detection_id,)).fetchone()

    if row is None:
        raise ValueError("Detection not found: %s" % detection_id)

    defect_id = new_id("defect")
    review_id = new_id("review")

    conn.execute("""
        INSERT INTO defects (
            defect_id,
            source_detection_id,
            part_id,
            lot_id,
            defect_family,
            defect_type,
            severity,
            confidence,
            location_x,
            location_y,
            location_z,
            location_units,
            review_status,
            disposition,
            evidence_primary_id,
            created_by,
            created_at,
            updated_at,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        defect_id,
        detection_id,
        row["part_id"],
        row["lot_id"],
        defect_family,
        defect_type,
        severity,
        row["confidence"],
        row["location_x"],
        row["location_y"],
        row["location_z"],
        row["location_units"],
        "CONFIRMED",
        disposition,
        row["evidence_id"],
        reviewer_id,
        now_iso(),
        now_iso(),
        notes,
    ))

    conn.execute("""
        INSERT INTO review_decisions (
            review_id,
            linked_record_type,
            linked_record_id,
            reviewer_id,
            reviewed_at,
            review_outcome,
            review_confidence,
            prior_classification,
            new_classification,
            prior_severity,
            new_severity,
            reason,
            notes,
            accepted_as_current
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        review_id,
        "detection",
        detection_id,
        reviewer_id,
        now_iso(),
        "CONFIRMED_DEFECT",
        1.0,
        row["candidate_type"],
        defect_type,
        row["severity_estimate"],
        severity,
        "Confirmed during review.",
        notes,
        1,
    ))

    conn.execute("""
        UPDATE detections
        SET review_status = 'CONFIRMED_DEFECT',
            updated_at = ?
        WHERE detection_id = ?
    """, (now_iso(), detection_id))

    conn.commit()

    return defect_id, review_id

Rule:
Review decisions are appended.
The original detection remains.
The confirmed defect becomes a separate linked record.

12. Performance Linking Code
12.1 Insert performance result
def insert_performance_result(
    conn,
    part_id,
    lot_id,
    test_type,
    metric_name,
    metric_value,
    metric_units,
    test_station="",
    operating_condition="",
    run_id="",
    data_file_path="",
    notes="",
):
    performance_result_id = new_id("perf")

    conn.execute("""
        INSERT INTO performance_results (
            performance_result_id,
            part_id,
            lot_id,
            test_id,
            test_type,
            test_station,
            started_at,
            ended_at,
            metric_name,
            metric_value,
            metric_units,
            operating_condition,
            run_id,
            data_file_path,
            historian_reference,
            quality_flag,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        performance_result_id,
        part_id,
        lot_id,
        new_id("test"),
        test_type,
        test_station,
        now_iso(),
        now_iso(),
        metric_name,
        metric_value,
        metric_units,
        operating_condition,
        run_id,
        data_file_path,
        "",
        "GOOD",
        notes,
    ))

    conn.commit()
    return performance_result_id

12.2 QC/performance join query
def fetch_qc_performance_summary(conn):
    rows = conn.execute("""
        SELECT
            p.part_id,
            p.lot_id,
            COUNT(DISTINCT d.defect_id) AS confirmed_defect_count,
            COUNT(DISTINCT det.detection_id) AS total_detection_count,
            SUM(CASE WHEN det.review_status = 'UNREVIEWED' THEN 1 ELSE 0 END) AS unreviewed_count,
            pr.metric_name,
            pr.metric_value,
            pr.metric_units,
            pr.test_type
        FROM parts p
        LEFT JOIN defects d
            ON p.part_id = d.part_id
        LEFT JOIN detections det
            ON p.part_id = det.part_id
        LEFT JOIN performance_results pr
            ON p.part_id = pr.part_id
        GROUP BY
            p.part_id,
            p.lot_id,
            pr.metric_name,
            pr.metric_value,
            pr.metric_units,
            pr.test_type
        ORDER BY p.lot_id, p.part_id
    """).fetchall()

    return [dict(row) for row in rows]

12.3 Defect type vs metric query
def fetch_defect_type_vs_metric(conn, defect_type, metric_name):
    rows = conn.execute("""
        SELECT
            p.part_id,
            p.lot_id,
            COUNT(d.defect_id) AS defect_count,
            pr.metric_value,
            pr.metric_units
        FROM parts p
        LEFT JOIN defects d
            ON p.part_id = d.part_id
           AND d.defect_type = ?
        JOIN performance_results pr
            ON p.part_id = pr.part_id
           AND pr.metric_name = ?
        GROUP BY
            p.part_id,
            p.lot_id,
            pr.metric_value,
            pr.metric_units
        ORDER BY p.lot_id, p.part_id
    """, (defect_type, metric_name)).fetchall()

    return [dict(row) for row in rows]

13. Evidence Audit
def audit_evidence_files(conn):
    rows = conn.execute("""
        SELECT evidence_id, file_path, content_hash, hash_algorithm
        FROM evidence_artifacts
    """).fetchall()

    results = {
        "checked": 0,
        "missing": [],
        "hash_mismatch": [],
        "ok": [],
    }

    for row in rows:
        results["checked"] += 1
        path = row["file_path"]

        if not os.path.isfile(path):
            results["missing"].append({
                "evidence_id": row["evidence_id"],
                "file_path": path,
            })
            continue

        if row["content_hash"]:
            current_hash = hash_file(path)
            if current_hash != row["content_hash"]:
                results["hash_mismatch"].append({
                    "evidence_id": row["evidence_id"],
                    "file_path": path,
                    "expected_hash": row["content_hash"],
                    "current_hash": current_hash,
                })
                continue

        results["ok"].append(row["evidence_id"])

    return results

Write report:
def write_evidence_audit_report(conn, report_path):
    audit = audit_evidence_files(conn)

    lines = []
    lines.append("QC EVIDENCE AUDIT REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % now_iso())
    lines.append("checked: %s" % audit["checked"])
    lines.append("ok: %s" % len(audit["ok"]))
    lines.append("missing: %s" % len(audit["missing"]))
    lines.append("hash_mismatch: %s" % len(audit["hash_mismatch"]))
    lines.append("")

    if audit["missing"]:
        lines.append("MISSING FILES")
        lines.append("-" * 72)
        for item in audit["missing"]:
            lines.append("%s | %s" % (item["evidence_id"], item["file_path"]))
        lines.append("")

    if audit["hash_mismatch"]:
        lines.append("HASH MISMATCH")
        lines.append("-" * 72)
        for item in audit["hash_mismatch"]:
            lines.append("%s | %s" % (item["evidence_id"], item["file_path"]))
            lines.append("expected: %s" % item["expected_hash"])
            lines.append("current:  %s" % item["current_hash"])
        lines.append("")

    safe_makedirs(os.path.dirname(os.path.abspath(report_path)))

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path

14. Database Integrity Audit
def audit_qc_database(conn):
    results = {
        "orphan_detections_missing_evidence": [],
        "orphan_defects_missing_detection": [],
        "detections_without_algorithm": [],
        "unreviewed_count": 0,
        "confirmed_defect_count": 0,
    }

    rows = conn.execute("""
        SELECT d.detection_id, d.evidence_id
        FROM detections d
        LEFT JOIN evidence_artifacts e
            ON d.evidence_id = e.evidence_id
        WHERE d.evidence_id IS NOT NULL
          AND e.evidence_id IS NULL
    """).fetchall()
    results["orphan_detections_missing_evidence"] = [dict(r) for r in rows]

    rows = conn.execute("""
        SELECT def.defect_id, def.source_detection_id
        FROM defects def
        LEFT JOIN detections d
            ON def.source_detection_id = d.detection_id
        WHERE def.source_detection_id IS NOT NULL
          AND d.detection_id IS NULL
    """).fetchall()
    results["orphan_defects_missing_detection"] = [dict(r) for r in rows]

    rows = conn.execute("""
        SELECT detection_id, detector_name
        FROM detections
        WHERE algorithm_version_id IS NULL
           OR algorithm_version_id = ''
    """).fetchall()
    results["detections_without_algorithm"] = [dict(r) for r in rows]

    results["unreviewed_count"] = conn.execute("""
        SELECT COUNT(*) AS c
        FROM detections
        WHERE review_status = 'UNREVIEWED'
    """).fetchone()["c"]

    results["confirmed_defect_count"] = conn.execute("""
        SELECT COUNT(*) AS c
        FROM defects
    """).fetchone()["c"]

    return results

15. Diagnostic Harness
def write_qc_diagnostic_report(db_path=None):
    initialize_qc_runtime_folders()

    if db_path is None:
        db_path = get_qc_db_path()

    report_path = os.path.join(
        get_runtime_root(),
        "diagnostics",
        "qc_diagnostic_report.txt"
    )

    lines = []
    lines.append("QC DIAGNOSTIC REPORT")
    lines.append("=" * 72)
    lines.append("timestamp: %s" % now_iso())
    lines.append("python: %s" % sys.version)
    lines.append("platform: %s" % sys.platform)
    lines.append("cwd: %s" % os.getcwd())
    lines.append("runtime_root: %s" % get_runtime_root())
    lines.append("database_path: %s" % db_path)
    lines.append("evidence_root: %s" % get_evidence_root())
    lines.append("")

    try:
        conn = open_qc_db(db_path)
        integrity = audit_qc_database(conn)
        evidence = audit_evidence_files(conn)

        lines.append("DATABASE")
        lines.append("-" * 72)
        lines.append("open: PASS")
        lines.append("schema_version: %s" % SCHEMA_VERSION)
        lines.append("confirmed_defect_count: %s" % integrity["confirmed_defect_count"])
        lines.append("unreviewed_detection_count: %s" % integrity["unreviewed_count"])
        lines.append("detections_without_algorithm: %s" % len(integrity["detections_without_algorithm"]))
        lines.append("orphan_detections_missing_evidence: %s" % len(integrity["orphan_detections_missing_evidence"]))
        lines.append("orphan_defects_missing_detection: %s" % len(integrity["orphan_defects_missing_detection"]))
        lines.append("")

        lines.append("EVIDENCE")
        lines.append("-" * 72)
        lines.append("checked: %s" % evidence["checked"])
        lines.append("ok: %s" % len(evidence["ok"]))
        lines.append("missing: %s" % len(evidence["missing"]))
        lines.append("hash_mismatch: %s" % len(evidence["hash_mismatch"]))
        lines.append("")

        conn.close()

    except Exception:
        lines.append("DATABASE")
        lines.append("-" * 72)
        lines.append("open: FAIL")
        lines.append(traceback.format_exc())
        lines.append("")

    safe_makedirs(os.path.dirname(os.path.abspath(report_path)))

    with open(report_path, "w") as f:
        f.write("\n".join(lines))

    return report_path

16. Smoke Test
This verifies the full minimum QC loop without real hardware.
def run_qc_smoke_test():
    initialize_qc_runtime_folders()

    db_path = os.path.join(
        get_runtime_root(),
        "qc_database",
        "qc_smoke_test.sqlite"
    )

    if os.path.isfile(db_path):
        os.remove(db_path)

    conn = open_qc_db(db_path)

    lot_id = "lot_smoke"
    part_id = "part_smoke_001"
    inspection_event_id = new_id("inspection")

    conn.execute("""
        INSERT INTO lots (lot_id, product_name, created_at, notes)
        VALUES (?, ?, ?, ?)
    """, (lot_id, "Smoke Test Product", now_iso(), "QC smoke test lot."))

    conn.execute("""
        INSERT INTO parts (part_id, lot_id, serial_number, part_type, created_at, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (part_id, lot_id, "SMOKE-001", "test_part", now_iso(), "ACTIVE", ""))

    conn.execute("""
        INSERT INTO inspection_events (
            inspection_event_id, part_id, lot_id, station_id, process_step,
            started_at, operator_id, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inspection_event_id,
        part_id,
        lot_id,
        "station_smoke",
        "smoke_inspection",
        now_iso(),
        "smoke_operator",
        "",
    ))

    detector = ThresholdDetector(
        signal_name="test_signal",
        high_limit=10.0
    )

    algorithm_version_id = register_algorithm_version(
        conn,
        detector_name=detector.detector_name,
        detector_type=detector.detector_type,
        version=detector.version,
        parameters=detector.parameter_snapshot(),
        code_version="smoke_test",
    )

    input_record = {
        "part_id": part_id,
        "lot_id": lot_id,
        "signal_name": "test_signal",
        "value": 12.5,
        "units": "V",
    }

    candidates = detector.detect(input_record)

    if not candidates:
        return {
            "passed": False,
            "failures": ["Detector produced no candidates."],
            "db_path": db_path,
        }

    candidate = candidates[0]

    detection_id = insert_detection(
        conn=conn,
        inspection_event_id=inspection_event_id,
        part_id=part_id,
        lot_id=lot_id,
        detector_name=detector.detector_name,
        detector_type=detector.detector_type,
        algorithm_version_id=algorithm_version_id,
        candidate_type=candidate["candidate_type"],
        confidence=candidate["confidence"],
        severity_estimate=candidate["severity_estimate"],
        raw_score=candidate["raw_score"],
        threshold_value=candidate["threshold_value"],
        measurement_value=candidate["measurement_value"],
        measurement_units=candidate["measurement_units"],
    )

    defect_id, review_id = confirm_detection_as_defect(
        conn,
        detection_id=detection_id,
        reviewer_id="smoke_reviewer",
        defect_family="Process anomaly",
        defect_type="High threshold excursion",
        severity="MODERATE",
        disposition="PENDING",
        notes="Smoke test confirmation."
    )

    perf_id = insert_performance_result(
        conn,
        part_id=part_id,
        lot_id=lot_id,
        test_type="smoke_performance_test",
        metric_name="example_metric",
        metric_value=0.87,
        metric_units="arb",
    )

    summary = fetch_qc_performance_summary(conn)

    failures = []

    if not detection_id:
        failures.append("Detection ID missing.")

    if not defect_id:
        failures.append("Defect ID missing.")

    if not review_id:
        failures.append("Review ID missing.")

    if not perf_id:
        failures.append("Performance result ID missing.")

    if not summary:
        failures.append("QC/performance summary returned no rows.")

    integrity = audit_qc_database(conn)

    if integrity["detections_without_algorithm"]:
        failures.append("Detection missing algorithm version.")

    conn.close()

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "db_path": db_path,
        "detection_id": detection_id,
        "defect_id": defect_id,
        "review_id": review_id,
        "performance_result_id": perf_id,
    }

17. Review UI Pattern
The GUI should not directly edit database rows ad hoc.
Bad:
def on_confirm_clicked(self):
    conn.execute("UPDATE detections SET review_status='CONFIRMED'")

Better:
def on_confirm_clicked(self):
    defect_id, review_id = confirm_detection_as_defect(
        conn=self.conn,
        detection_id=self.current_detection_id,
        reviewer_id=self.current_user,
        defect_family=self.defect_family_combo.currentText(),
        defect_type=self.defect_type_combo.currentText(),
        severity=self.severity_combo.currentText(),
        disposition=self.disposition_combo.currentText(),
        notes=self.notes_text.toPlainText(),
    )
    self.reload_review_queue()

Best:
UI → review service → database transaction → event log → UI refresh

The UI requests a review action.
The review service owns the database semantics.

18. Export Patterns
18.1 Export defect summary CSV
def export_defect_summary_csv(conn, csv_path):
    rows = conn.execute("""
        SELECT
            d.defect_id,
            d.part_id,
            d.lot_id,
            d.defect_family,
            d.defect_type,
            d.defect_subtype,
            d.severity,
            d.disposition,
            d.created_at,
            d.notes
        FROM defects d
        ORDER BY d.lot_id, d.part_id, d.created_at
    """).fetchall()

    safe_makedirs(os.path.dirname(os.path.abspath(csv_path)))

    fieldnames = [
        "defect_id",
        "part_id",
        "lot_id",
        "defect_family",
        "defect_type",
        "defect_subtype",
        "severity",
        "disposition",
        "created_at",
        "notes",
    ]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(dict(row))

    return csv_path

18.2 Export QC/performance join
def export_qc_performance_summary_csv(conn, csv_path):
    rows = fetch_qc_performance_summary(conn)

    if not rows:
        return None

    safe_makedirs(os.path.dirname(os.path.abspath(csv_path)))

    fieldnames = sorted(rows[0].keys())

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return csv_path

19. Threading Rules for QC Systems
QC-THREAD-RULE-001
Do not let the UI be the only owner of detection records.

QC-THREAD-RULE-002
Do not write SQLite from many uncontrolled threads.

QC-THREAD-RULE-003
Use queues between acquisition, detection, database writing, and UI.

QC-THREAD-RULE-004
Raw evidence should be saved before or at the same time as detection records.

QC-THREAD-RULE-005
If evidence save fails, the detection should be marked with an evidence failure quality flag.

QC-THREAD-RULE-006
Candidate detections and reviewed defects are different database records.

QC-THREAD-RULE-007
Review actions should be transactional.

QC-THREAD-RULE-008
Algorithm version must be recorded for every automated detection.

QC-THREAD-RULE-009
Performance-link tests should be automated early.

QC-THREAD-RULE-010
Diagnostics must run without camera/sensor/GUI dependencies where possible.

20. Package Placement
Recommended formal package structure:
project_name/
├── __init__.py
├── constants.py
├── paths.py
├── settings.py
├── logging_utils.py
│
├── qc/
│   ├── schema.py
│   ├── database.py
│   ├── ids.py
│   ├── evidence_store.py
│   ├── detection_records.py
│   ├── defect_records.py
│   ├── review_service.py
│   ├── performance_link.py
│   ├── exports.py
│   └── audits.py
│
├── detectors/
│   ├── base.py
│   ├── threshold_detector.py
│   ├── image_detector.py
│   ├── signal_detector.py
│   ├── simulated_detector.py
│   └── registry.py
│
├── pipeline/
│   ├── acquisition_thread.py
│   ├── detection_thread.py
│   ├── database_writer_thread.py
│   └── messages.py
│
├── ui/
│   ├── qc_dashboard.py
│   ├── review_queue.py
│   ├── evidence_viewer.py
│   └── trend_analysis.py
│
├── diagnostics/
│   ├── qc_diagnostics.py
│   ├── db_integrity.py
│   └── evidence_audit.py
│
└── app.py

Tools:
tools/
├── qc_diagnostic_harness.py
├── qc_smoke_test.py
├── qc_db_integrity_check.py
├── qc_evidence_audit.py
├── qc_export_summary.py
└── qc_performance_join_test.py

21. Core Pattern
The safest QC software pattern is:
input source
    → acquisition thread
        → input queue

detectors
    → detection thread
        → candidate messages

database/evidence storage
    → DB writer thread
        → SQLite records
        → managed evidence files

operator review
    → review service
        → review_decisions
        → defects
        → dispositions

downstream test data
    → performance importer
        → performance_results

analysis
    → QC/performance joins
        → reports
        → plots
        → engineering decisions

The system is not finished when it detects defects.
It is finished only when it can preserve evidence, support review, survive audits, and explain later performance outcomes.

MIDI
I checked the current official/reference docs before writing this. The modern baseline remains: Mido is the main high-level Python MIDI library for MIDI 1.0 messages, ports, and files; python-rtmidi/RtMidi is the preferred backend for many live-port workflows; pygame.midi remains a useful fallback/legacy-style MIDI I/O layer based on PortMidi; and loopMIDI is still a common Windows virtual loopback-port tool. (Mido)
