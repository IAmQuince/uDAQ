from __future__ import annotations

import pytest

from tools.diagnostics.validate_runtime_evidence_consistency import evaluate_runtime_evidence_consistency

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INTEG-025',
    'verifies_requirements': ['UDQ-REQ-SIG-001', 'UDQ-REQ-SIG-002', 'UDQ-REQ-HIS-002'],
    'checks_invariants': ['UDQ-INV-EVID-005'],
    'worked_example_reference': 'UDQ-EXM-002',
    'expected_proof_output': 'runtime evidence consistency verdict',
}

pytestmark = pytest.mark.integration


def test_startup_smoke_can_pass_without_recent_startup_rows_when_startup_counters_confirm_success():
    verdict = evaluate_runtime_evidence_consistency(
        session_metadata={
            "requested_mode": "real",
            "validation_flow": "startup_open_smoke",
        },
        phase_records=[
            {
                "phase_name": "baseline",
                "status": "PASS",
                "observed_state_family": "live_ready_healthy",
            }
        ],
        operator_events=[
            {
                "event_type": "harness_preflight",
            }
        ],
        final_review_bundle={
            "active_adapter_status": {
                "has_successful_startup_open": True,
                "startup_open_attempts": 1,
                "startup_open_success_count": 1,
            },
            "reviewer_runtime_rollup": {
                "state_family": "live_ready_healthy",
                "summary": "Runtime posture is live / ready / healthy; alarms=0, disconnects=0, recoveries=0.",
                "disconnect_count": 0,
                "recovery_count": 0,
            },
            "canonical_runtime_evidence_bundle_v1": {
                "runtime_state": {
                    "canonical_state_family": "live_ready_healthy",
                },
                "reviewer_rollup": {
                    "summary": "Runtime posture is live / ready / healthy; alarms=0, disconnects=0, recoveries=0.",
                },
            },
            "recent_runtime_event_rows": [],
        },
    )

    assert verdict["verdict"] == "PASS"
    startup_check = next(check for check in verdict["checks"] if check["name"] == "startup_open_has_runtime_evidence")
    assert startup_check["status"] == "PASS"
    assert "startup-open success counters" in startup_check["message"]
