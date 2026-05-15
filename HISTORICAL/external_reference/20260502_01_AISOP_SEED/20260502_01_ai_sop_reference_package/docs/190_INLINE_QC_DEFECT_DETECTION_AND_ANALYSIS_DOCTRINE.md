---
document_id: DOC-190
title: "Inline QC, Defect Detection, and Analysis Doctrine"
version: 0.1.0
revision: REV-001
status: DRAFT-REFERENCE
last_updated: 2026-05-02
package_id: 20260502_01_ai_sop_reference_package
machine_reference_prefix: DOC-190
normative_status: Informative
source: "Generalized AI-assisted coding SOP source text"
---

# Inline QC, Defect Detection, and Analysis Doctrine

This should follow the same AISOP principles: define requirements before implementation, use stable IDs, preserve data, include diagnostics, define schema/persistence explicitly, and make the package independently reviewable without chat history.
# 190_INLINE_QC_DEFECT_DETECTION_AND_ANALYSIS_DOCTRINE

## 0. Purpose

This document formalizes our approach to inline quality control, live defect detection, error analysis, review workflows, and long-term defect/performance traceability.

It applies to software systems that inspect, classify, record, and analyze quality events during manufacturing, assembly, test, or experimental workflows.

Typical use cases include:

- inline visual inspection;
- image-based defect detection;
- sensor-based anomaly detection;
- operator-reviewed quality events;
- automated threshold detection;
- part/lot/sample tracking;
- MEA or stack-component QC;
- production-process monitoring;
- defect database creation;
- linking QC records to later test performance;
- identifying process variables that correlate with failures;
- building searchable historical quality records.

The central goal is:

Capture quality evidence at the moment it occurs, preserve it with enough context to be useful later, and make it possible to correlate defects with future performance data.

---

## 1. Core Doctrine

Inline QC software is not just a defect counter.

It is a traceability system.

A useful system must preserve:

- what was detected;
- when it was detected;
- where it was detected;
- how it was detected;
- what physical item it belongs to;
- what evidence supports it;
- who or what classified it;
- how confident the classification was;
- whether a human reviewed it;
- whether it was accepted, rejected, repaired, reworked, or ignored;
- what downstream performance resulted later.

The defect event itself is only one layer.

The long-term value comes from connecting:

```text
process conditions
        ↓
inline QC observations
        ↓
defect classifications
        ↓
review decisions
        ↓
manufacturing lots / parts / assemblies
        ↓
test-station performance
        ↓
field or lifecycle behavior

A QC record that cannot be linked later is only a note.
A QC record with traceable evidence becomes engineering data.

2. Primary Design Goals
The inline QC system should:
1. Detect candidate defects during the workflow.
2. Capture evidence automatically.
3. Store records in a structured database.
4. Allow human review and correction.
5. Preserve raw evidence.
6. Track algorithm/rule versions.
7. Track operator decisions.
8. Track sample/part/lot identity.
9. Support searchable historical analysis.
10. Support later correlation with performance data.
11. Avoid silently overwriting classifications.
12. Distinguish raw detection from reviewed truth.
13. Export useful reports.
14. Provide diagnostics and database health checks.
15. Remain useful even if detection algorithms change later.

3. Definitions
3.1 Detection
A detection is an automated or semi-automated observation that something may be wrong.
Examples:
bright spot detected
scratch candidate
edge discontinuity
color anomaly
missing region
excess material
sensor excursion
pressure transient
temperature spike
out-of-range dimension
unexpected process timing

A detection is not automatically a confirmed defect.

3.2 Defect
A defect is a reviewed or accepted quality issue associated with a part, sample, region, material, process step, or test.
A defect may originate from:
* automated detection;
* operator entry;
* manual review;
* imported historical data;
* post-test failure analysis;
* engineering judgment.

3.3 Candidate Defect
A candidate defect is a detection that has not yet been reviewed.
Candidate defects should be preserved, but clearly marked as unconfirmed.

3.4 Reviewed Defect
A reviewed defect has been inspected by an operator, engineer, or approved review process.
Review outcomes:
CONFIRMED_DEFECT
FALSE_POSITIVE
ACCEPTABLE_VARIATION
NEEDS_REVIEW
REWORKED
SCRAPPED
MONITOR_ONLY
UNKNOWN

3.5 Evidence
Evidence is the raw or processed information supporting a detection or review.
Evidence may include:
* image file;
* cropped image;
* video frame;
* waveform;
* sensor time range;
* measurement values;
* threshold crossing;
* plotted snapshot;
* operator note;
* microscope image;
* instrument file;
* process log excerpt;
* test-station data segment.
Evidence must not be silently discarded.

4. Core Data Model
4.1 Required Entity Types
The database should support these conceptual entities:
Project
Product / part family
Lot / batch
Part / sample / unit
Process run
Process step
Inspection station
Inspection event
Detection event
Defect record
Evidence artifact
Review decision
Disposition
Rework action
Performance test
Performance result
Correlation analysis
Algorithm/rule version
Operator/user
Calibration/configuration snapshot

Not every prototype needs every table immediately, but the design should avoid blocking these relationships later.

4.2 Stable IDs
Every important record needs a stable ID.
Recommended ID types:
project_id
lot_id
batch_id
part_id
sample_id
process_run_id
process_step_id
inspection_event_id
detection_id
defect_id
evidence_id
review_id
disposition_id
performance_test_id
performance_result_id
algorithm_version_id
operator_id

Do not rely only on row numbers or filenames.
IDs should survive file moves, exports, imports, and later database migrations.

4.3 Detection Event Record
DATA-QC-001
Object: Detection Event
Purpose:
Stores an automated or semi-automated candidate defect observation.

Fields:
detection_id
inspection_event_id
timestamp
timestamp_source
part_id
lot_id
process_run_id
process_step_id
station_id
detector_type
detector_name
algorithm_version_id
rule_version_id
defect_candidate_type
location_type
location_x
location_y
location_z
location_units
region_id
severity_estimate
confidence
raw_score
threshold
measurement_value
measurement_units
quality_flag
evidence_id
review_status
created_at
updated_at

Required fields:
detection_id
timestamp
detector_name
defect_candidate_type
review_status

Deletion policy:
Do not delete automatically. Mark invalid, superseded, or false positive instead.

4.4 Defect Record
DATA-QC-002
Object: Defect Record
Purpose:
Stores a confirmed or operator-entered quality issue.

Fields:
defect_id
source_detection_id
part_id
lot_id
process_run_id
process_step_id
defect_type
defect_subtype
severity
criticality
location_description
location_x
location_y
location_z
location_units
area
length
width
depth
count
confidence
review_status
disposition
rework_status
evidence_primary_id
created_by
created_at
updated_at
closed_at
notes

Required fields:
defect_id
defect_type
severity
review_status
disposition

Deletion policy:
Do not physically delete during normal use. Use status fields.

4.5 Evidence Artifact Record
DATA-QC-003
Object: Evidence Artifact
Purpose:
Stores links and metadata for raw evidence supporting detections, defects, and review decisions.

Fields:
evidence_id
linked_record_type
linked_record_id
artifact_type
file_path
relative_path
content_hash
created_at
captured_at
source_device
source_station
format
width
height
duration
sample_rate
time_start
time_end
description
is_raw
is_processed
processing_version
notes

Artifact types:
IMAGE_RAW
IMAGE_CROP
IMAGE_ANNOTATED
VIDEO
WAVEFORM
CSV_SEGMENT
PLOT_SNAPSHOT
MICROSCOPE_IMAGE
OPERATOR_NOTE
INSTRUMENT_FILE
REPORT

Rule:
Raw evidence must be preserved separately from annotated or processed evidence.

4.6 Review Decision Record
DATA-QC-004
Object: Review Decision
Purpose:
Records human or authorized review of a candidate defect or defect record.

Fields:
review_id
linked_record_type
linked_record_id
reviewer_id
reviewed_at
review_outcome
review_confidence
prior_classification
new_classification
prior_severity
new_severity
reason
notes
evidence_added
requires_second_review
supersedes_review_id

Review outcomes:
CONFIRMED_DEFECT
FALSE_POSITIVE
ACCEPTABLE_VARIATION
NEEDS_REVIEW
RECLASSIFIED
ESCALATED
DOWNGRADED
REWORK_REQUIRED
SCRAP_RECOMMENDED
UNKNOWN

Rule:
Do not overwrite review history. Add a new review decision.

4.7 Performance Result Record
DATA-QC-005
Object: Performance Result
Purpose:
Stores downstream test or field performance data that may later be correlated with QC records.

Fields:
performance_result_id
part_id
sample_id
lot_id
test_id
test_type
test_station
started_at
ended_at
metric_name
metric_value
metric_units
operating_condition
sequence_id
run_id
data_file_path
historian_reference
quality_flag
notes

Examples:
cell_voltage_at_current
current_density
efficiency
pressure_drop
leak_rate
temperature_rise
degradation_rate
failure_time
resistance
power

4.8 Correlation Analysis Record
DATA-QC-006
Object: Correlation Analysis
Purpose:
Stores analysis results linking QC defects or process variables to performance outcomes.

Fields:
analysis_id
created_at
analysis_name
analysis_version
input_query
included_lots
included_parts
included_defect_types
included_performance_metrics
method
result_summary
output_file_path
script_version
operator_id
notes

Rule:
Correlation analyses are derived results. They must not replace raw QC or performance records.

5. Defect Taxonomy
5.1 Defect Classification Levels
Use hierarchical classification:
defect_family
defect_type
defect_subtype
defect_detail

Example:
Surface
    Scratch
        Linear scratch
        Curved scratch
        Clustered scratch

Material distribution
    Thin region
    Thick region
    Missing coating
    Excess coating

Geometry
    Edge defect
    Hole misalignment
    Dimensional out-of-tolerance

Contamination
    Particle
    Fiber
    Smudge
    Residue

Process anomaly
    Timing anomaly
    Pressure anomaly
    Temperature anomaly
    Flow anomaly

Electrical anomaly
    Open circuit
    Short risk
    High resistance
    Noise spike

The taxonomy should be project-specific, but the structure should stay consistent.

5.2 Severity
Recommended severity levels:
INFO
MINOR
MODERATE
MAJOR
CRITICAL
UNKNOWN

Severity should answer:
How bad is the defect if real?

5.3 Confidence
Recommended confidence levels:
LOW
MEDIUM
HIGH
CERTAIN
UNKNOWN

or numeric:
0.0 to 1.0

Confidence should answer:
How sure are we that the detection/classification is correct?

Severity and confidence are different.
A high-severity defect can have low confidence.
A low-severity defect can have high confidence.

5.4 Disposition
Recommended dispositions:
PENDING
ACCEPT_AS_IS
REWORK
SCRAP
HOLD
ENGINEERING_REVIEW
RETEST
MONITOR
UNKNOWN

Disposition should answer:
What did we do with the part or sample?

6. Inline Detection Workflow
6.1 Standard Workflow
1. Part/sample enters process or inspection station.
2. System identifies part/sample/lot/process step.
3. Sensors/images/measurements are captured.
4. Detection engine evaluates incoming data.
5. Candidate detections are generated.
6. Evidence artifacts are saved.
7. Detection records are written to database.
8. UI shows live QC status.
9. Operator reviews candidates if required.
10. Review decisions are stored without overwriting original detections.
11. Disposition/rework actions are recorded.
12. Part proceeds, is held, reworked, or rejected.
13. Later performance data is linked by part/sample/lot/run ID.
14. Analysis tools correlate QC records with performance outcomes.

6.2 Live Detection Loop
The live detection loop should separate acquisition, detection, persistence, and UI.
acquire input
    ↓
validate input
    ↓
timestamp input
    ↓
save raw evidence if required
    ↓
run detection rules/models
    ↓
create candidate detection records
    ↓
save evidence artifacts
    ↓
write database records
    ↓
publish UI update
    ↓
log summary / faults

Do not let the UI be the only place where detections exist.
A detection should be persisted even if the UI crashes after detection.

6.3 Human Review Loop
open review queue
    ↓
inspect candidate detection
    ↓
view raw evidence
    ↓
view processed/annotated evidence
    ↓
confirm / reject / reclassify
    ↓
assign severity
    ↓
assign disposition
    ↓
add notes if needed
    ↓
save review decision
    ↓
advance to next candidate

The review UI should make it clear whether the user is viewing:
raw evidence
processed evidence
annotated evidence
derived metrics
prior review decision
algorithm suggestion

7. Database Doctrine
7.1 SQLite as the Default Local QC Database
For local tools, SQLite is usually a strong default because it is:
* file-based;
* portable;
* queryable;
* good enough for many production/test workflows;
* easy to back up;
* compatible with Python standard tooling;
* suitable for later viewer applications.
CSV can be used for exports and recovery logs, but it should not be the only structure once records need relationships.

7.2 Recommended Database Tables
projects
products
lots
parts
process_runs
process_steps
inspection_stations
inspection_events
detections
defects
evidence_artifacts
review_decisions
dispositions
rework_actions
performance_tests
performance_results
algorithm_versions
calibration_snapshots
configuration_snapshots
operators
event_log
audit_log

7.3 Minimum Useful Schema
For a first serious implementation, the minimum useful tables are:
parts
lots
inspection_events
detections
defects
evidence_artifacts
review_decisions
performance_results
algorithm_versions
event_log

This is enough to support:
* defect capture;
* evidence preservation;
* review;
* performance correlation;
* traceability;
* versioned detection logic.

7.4 Database Integrity Rules
Rules:
* Use foreign keys where practical.
* Use stable IDs.
* Store timestamps consistently.
* Store schema version.
* Store algorithm version.
* Do not hard-delete defect history during normal operation.
* Do not overwrite review history.
* Do not store only file paths without content hash when evidence matters.
* Back up before migration.
* Provide database integrity checks.
* Provide export tools.
Recommended tools:
tools/qc_db_integrity_check.py
tools/qc_schema_audit.py
tools/qc_evidence_audit.py
tools/qc_export_summary.py
tools/qc_correlation_smoke_test.py

8. Evidence Storage Doctrine
8.1 Raw Evidence Preservation
Raw evidence should be immutable once captured.
If an image is annotated, cropped, normalized, thresholded, or enhanced, save that as a new artifact linked to the raw artifact.
raw_image.png
processed_image.png
annotated_image.png

Do not overwrite:
raw_image.png

8.2 Evidence Folder Structure
Recommended runtime structure:
runtime_data/
├── qc_database/
│   └── inline_qc.sqlite
│
├── evidence/
│   ├── raw/
│   │   └── LOT_ID/
│   │       └── PART_ID/
│   ├── processed/
│   │   └── LOT_ID/
│   │       └── PART_ID/
│   ├── annotated/
│   │   └── LOT_ID/
│   │       └── PART_ID/
│   └── imported/
│       └── LOT_ID/
│           └── PART_ID/
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

8.3 Content Hashes
Evidence records should include a content hash where practical.
Purpose:
* detect missing/moved/changed evidence files;
* verify evidence integrity;
* support deduplication;
* prove that annotated files did not replace raw files.
Fields:
content_hash
hash_algorithm
file_size_bytes
created_at
last_verified_at

9. Algorithm and Rule Versioning
9.1 Every Detection Needs Algorithm Provenance
A detection without algorithm provenance loses value later.
Detection records should include:
detector_name
detector_type
algorithm_version_id
rule_set_version
parameter_snapshot_id
calibration_snapshot_id
thresholds_used
input_preprocessing_version

This allows future analysis to separate:
The part got better.

from:
The detector changed.

9.2 Algorithm Version Record
DATA-QC-007
Object: Algorithm Version
Purpose:
Records the exact detection logic used to generate detections.

Fields:
algorithm_version_id
name
version
created_at
code_version
parameter_hash
rule_set_path
model_path
training_data_reference
description
known_limitations
active_from
active_to

9.3 Rule Types
Detection rules may include:
absolute_threshold
relative_threshold
moving_average
statistical_outlier
edge_detection
color/brightness anomaly
dimension tolerance
count-based rule
duration-based rule
pattern match
manual entry
machine-learning classifier
hybrid rule

Each rule should produce:
score
threshold
candidate_type
confidence
explanation
evidence reference

10. UI / Review Interface Doctrine
10.1 Main QC Dashboard
The main QC interface should show:
current lot
current part/sample
current process step
inspection station
live status
candidate defect count
confirmed defect count
unreviewed count
latest evidence
database write status
camera/sensor health
algorithm version
operator
last saved timestamp

The operator should never wonder whether a detection was saved.

10.2 Review Queue
Review queue fields:
detection_id
part_id
lot_id
timestamp
candidate_type
severity_estimate
confidence
review_status
thumbnail/evidence preview
algorithm version
station
age

Useful filters:
unreviewed
confirmed
false positive
critical
by lot
by part
by defect type
by confidence
by station
by date/time
by algorithm version

10.3 Evidence Viewer
The evidence viewer should support:
* raw image/data view;
* processed view;
* annotated view;
* zoom/pan;
* brightness/contrast adjustment if images are involved;
* side-by-side comparison;
* metadata panel;
* linked process data;
* linked performance data if available;
* review history;
* notes.
The viewer must clearly label raw vs processed vs annotated evidence.

10.4 Trend / Analysis Views
Useful QC analysis views:
defects by lot
defects by part
defects by station
defects by process step
defects by operator
defects by algorithm version
severity over time
false-positive rate over time
defect location heatmap
defect type Pareto chart
defect count vs performance metric
defect severity vs performance metric
process parameter vs defect count

11. Cross-Referencing QC With Performance Data
11.1 Required Linking Strategy
Performance correlation requires shared identifiers.
At minimum, QC and performance records should share:
part_id or sample_id
lot_id
process_run_id
test_run_id where applicable
timestamp range
product/configuration

Without shared IDs, later correlation becomes manual and fragile.

11.2 Performance Correlation Examples
Questions the system should eventually answer:
Do parts with edge defects have worse performance?
Do coating-thickness anomalies correlate with higher resistance?
Do specific lots show higher defect rates?
Do defects from a specific station correlate with later failures?
Does severity score predict performance loss?
Do false positives cluster around a process condition?
Does detector version affect apparent defect rate?
Do reworked parts perform differently?

11.3 Correlation Data Mart
For analysis, create a derived table or query view:
qc_performance_join_view

Example fields:
part_id
lot_id
defect_count_total
defect_count_by_type
max_defect_severity
confirmed_defect_count
unreviewed_detection_count
rework_count
inspection_station
algorithm_version
performance_metric_name
performance_metric_value
test_condition
test_date

This view is derived. It must not replace raw records.

12. Error Analysis Doctrine
12.1 Separate Detection Error From Process Error
A detected “problem” may mean:
1. A real manufacturing defect.
2. A sensor/camera artifact.
3. A detection algorithm false positive.
4. A calibration issue.
5. A lighting/environment issue.
6. A data synchronization issue.
7. A process excursion.
8. An operator classification inconsistency.
The system must preserve enough evidence to distinguish these later.

12.2 False Positives and False Negatives Matter
Track:
false_positive_count
confirmed_defect_count
missed_defect_count
reviewed_detection_count
unreviewed_detection_count
review_agreement_rate
algorithm_precision_estimate
algorithm_recall_estimate where possible

False negatives are harder because they require later discovery. When a defect is found downstream, record whether it was missed inline.
missed_by_inline_detection: true/false/unknown

12.3 Review Disagreement
If multiple reviewers disagree, do not overwrite.
Store multiple review decisions and mark one as current/accepted if needed.
Fields:
reviewer_id
review_outcome
review_confidence
review_notes
supersedes_review_id
accepted_as_current

This preserves institutional knowledge.

13. Diagnostics and Health Checks
Required diagnostic reports:
qc_diagnostic_report.txt
qc_db_integrity_report.txt
qc_evidence_audit_report.txt
qc_detection_smoke_test_report.txt
qc_review_workflow_test_report.txt
qc_performance_join_test_report.txt

Diagnostic harness should report:
app version
Python version
OS/platform
working directory
database path
database schema version
database open/read/write test
evidence root path
evidence write test
evidence hash test
algorithm versions available
active detector version
camera/sensor imports
camera/sensor connection status if applicable
unreviewed detection count
orphaned evidence count
missing evidence count
orphaned database records
latest detection timestamp
latest review timestamp
latest performance import timestamp
recent exceptions
pass/fail summary

14. Acceptance Tests
14.1 Detection Persistence
ACCEPT-QC-001
Test:
Generate a simulated candidate defect.

Expected result:
Detection record is written to the database with timestamp, candidate type, confidence, detector version, and evidence reference.

Manual/automated:
Automated.

Required before delivery:
Yes.

14.2 Evidence Preservation
ACCEPT-QC-002
Test:
Capture raw evidence and create an annotated version.

Expected result:
Raw evidence remains unchanged. Annotated evidence is stored as a separate artifact linked to the raw artifact.

Manual/automated:
Automated or manual.

Required before delivery:
Yes.

14.3 Review Workflow
ACCEPT-QC-003
Test:
Open an unreviewed detection and mark it false positive.

Expected result:
Review decision is added. Original detection remains. Review status updates. Review log records reviewer/time/outcome.

Manual/automated:
Manual or automated.

Required before delivery:
Yes.

14.4 Defect Confirmation
ACCEPT-QC-004
Test:
Confirm a candidate detection as a real defect.

Expected result:
Defect record is created or updated, linked to source detection and evidence, with severity and disposition.

Manual/automated:
Manual.

Required before delivery:
Yes.

14.5 Performance Linking
ACCEPT-QC-005
Test:
Import or create performance result for a part with known QC records.

Expected result:
QC/performance query returns the part, defect records, and performance metrics in one linked result.

Manual/automated:
Automated.

Required before delivery:
Yes.

14.6 Database Integrity
ACCEPT-QC-006
Test:
Run database integrity audit.

Expected result:
No orphaned detection/evidence/review records unless explicitly documented.

Manual/automated:
Automated.

Required before delivery:
Yes.

14.7 Algorithm Version Traceability
ACCEPT-QC-007
Test:
Run two detector versions on sample data.

Expected result:
Detections record the correct algorithm version and can be filtered by algorithm version.

Manual/automated:
Automated.

Required before delivery:
Yes.

15. Common Risks
RISK-QC-001
Title: Candidate detections mistaken for confirmed defects
Likelihood: Medium
Impact: High
Detection:
Review reports show unreviewed detections mixed with confirmed defects.
Mitigation:
Separate detection records from reviewed defect records. Use review_status everywhere.
Fallback:
Reclassify records and regenerate reports.
Status: Open

RISK-QC-002
Title: Raw evidence overwritten by processed evidence
Likelihood: Medium
Impact: High
Detection:
Evidence audit checks raw and processed artifact hashes.
Mitigation:
Store processed/annotated evidence as separate artifacts.
Fallback:
Restore from backup if available.
Status: Open

RISK-QC-003
Title: Defect records cannot be linked to performance data
Likelihood: Medium
Impact: High
Detection:
Performance join test fails due to missing part/sample/lot IDs.
Mitigation:
Require shared IDs before accepting QC records.
Fallback:
Manual reconciliation table.
Status: Open

RISK-QC-004
Title: Algorithm changes appear as process changes
Likelihood: Medium
Impact: High
Detection:
Defect rate shifts coincide with detector version change.
Mitigation:
Record algorithm version for every detection.
Fallback:
Analyze results by detector version separately.
Status: Open

RISK-QC-005
Title: Review history overwritten
Likelihood: Medium
Impact: Medium/High
Detection:
Audit log shows changed classification without review record.
Mitigation:
Append review decisions instead of overwriting.
Fallback:
Restore from backup or mark review history incomplete.
Status: Open

RISK-QC-006
Title: Evidence files moved or missing
Likelihood: Medium
Impact: High
Detection:
Evidence audit reports missing paths or hash mismatch.
Mitigation:
Use package/runtime evidence root, relative paths, content hashes, and backups.
Fallback:
Mark evidence missing but preserve database record.
Status: Open

16. Technical Debt Patterns
DEBT-QC-001
Title: Detection and defect concepts mixed
Category: Data model
Impact:
Unreviewed candidates may be treated as confirmed quality failures.
Resolution:
Separate detections, defects, and review decisions.

DEBT-QC-002
Title: Evidence stored only as file paths
Category: Data integrity
Impact:
Moved or modified files cannot be detected.
Resolution:
Add evidence artifact table with content hashes and verification timestamps.

DEBT-QC-003
Title: No algorithm versioning
Category: Traceability
Impact:
Future defect-rate trends may be impossible to interpret.
Resolution:
Create algorithm_versions table and link each detection to the active version.

DEBT-QC-004
Title: No performance-linking IDs
Category: Analysis
Impact:
QC records cannot be correlated with later test results.
Resolution:
Require part_id/sample_id/lot_id/process_run_id fields.

DEBT-QC-005
Title: Manual review overwrites original classification
Category: Auditability
Impact:
Loss of review history and training data.
Resolution:
Append review_decisions and preserve prior classification.

17. Recommended Package Structure
project_name/
├── __init__.py
├── constants.py
├── compat.py
├── paths.py
├── settings.py
├── logging_utils.py
│
├── qc/
│   ├── schema.py
│   ├── database.py
│   ├── detection_model.py
│   ├── defect_taxonomy.py
│   ├── evidence_store.py
│   ├── review.py
│   ├── disposition.py
│   ├── performance_link.py
│   ├── correlation.py
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
├── acquisition/
│   ├── camera_adapter.py
│   ├── sensor_adapter.py
│   ├── file_importer.py
│   └── simulated_inputs.py
│
├── ui/
│   ├── main_window.py
│   ├── qc_dashboard.py
│   ├── review_queue.py
│   ├── evidence_viewer.py
│   ├── defect_browser.py
│   ├── trend_analysis.py
│   └── settings_dialog.py
│
├── diagnostics/
│   ├── report.py
│   ├── db_checks.py
│   ├── evidence_checks.py
│   └── smoke.py
│
└── app.py

18. Required Tools
tools/
├── qc_diagnostic_harness.py
├── qc_db_integrity_check.py
├── qc_schema_audit.py
├── qc_evidence_audit.py
├── qc_detection_smoke_test.py
├── qc_review_workflow_test.py
├── qc_performance_join_test.py
├── qc_export_summary.py
└── structure_audit.py

19. Definition of Done
An inline QC / defect-analysis package is acceptable only when:
[ ] Candidate detections are stored separately from confirmed defects.
[ ] Raw evidence is preserved.
[ ] Processed/annotated evidence does not overwrite raw evidence.
[ ] Detection records include algorithm/rule version.
[ ] Review decisions are appended, not silently overwritten.
[ ] Defect taxonomy is explicit.
[ ] Severity and confidence are separate.
[ ] Disposition is tracked.
[ ] Part/sample/lot IDs are present.
[ ] QC records can be linked to performance records.
[ ] Database schema version is recorded.
[ ] Database integrity check exists.
[ ] Evidence audit exists.
[ ] Detection smoke test exists.
[ ] Review workflow test exists.
[ ] Performance join test exists.
[ ] Export/report path exists.
[ ] Known risks are documented.
[ ] Technical debt is documented.
[ ] Package can be reviewed without chat history.

20. Core Rule
Inline QC software is valuable only if it preserves context.
A defect record without evidence is weak.
Evidence without part identity is weak.
Part identity without process context is weak.
QC data without performance linkage is incomplete.
Performance data without QC history loses explanatory power.
The goal is not just to detect defects.
The goal is to build a traceable quality memory that gets more valuable as more production, inspection, and performance data accumulate.

QC and Defect Examples
Recommended companion file:
