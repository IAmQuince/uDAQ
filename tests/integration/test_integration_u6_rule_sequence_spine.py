from __future__ import annotations

from tools.dev._u6_live_support import bootstrap_controller, build_services, install_labjack_support_pack, prepare_u6_live_value_slice, run_poll_cycles
from universaldaq.common import as_event_time
from universaldaq.rules import RuleDefinition
from universaldaq.sequences import SequenceDefinition, SequenceStep

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-INT-023',
    'verifies_requirements': ['UDQ-REQ-EVT-002', 'UDQ-REQ-OUT-002'],
    'checks_invariants': ['UDQ-INV-STATE-001', 'UDQ-INV-EVID-004'],
    'worked_example_reference': None,
    'expected_proof_output': 'bounded U6 orchestration spine emits one admitted acknowledgment command and one rejected dry-run command without bypassing command admission',
}


def test_integration_u6_rules_sequences_spine():
    services = build_services()
    install_labjack_support_pack(services, real_hardware=False, simulated_serial_number='470199')
    controller = bootstrap_controller(services=services, profile_id='PROF-U6-RSEQ-INT', actor_id='u6-rule-seq')
    prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
    controller.register_rule_definition(
        definition=RuleDefinition(
            rule_id='RULE-U6-AUTOACK',
            condition_kind='alarm_active_unacknowledged',
            condition_payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'},
            action_kind='ack_alarm',
            action_payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'},
        ),
        timestamp=as_event_time(20),
    )
    controller.register_sequence_definition(
        definition=SequenceDefinition(
            sequence_id='SEQ-U6-AUTOACK',
            steps=(
                SequenceStep(step_id='STEP-1', step_kind='wait_alarm_active_unacknowledged', payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'}),
                SequenceStep(step_id='STEP-2', step_kind='emit_ack_alarm', payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'}),
            ),
        ),
        timestamp=as_event_time(21),
    )
    controller.register_sequence_definition(
        definition=SequenceDefinition(
            sequence_id='SEQ-U6-DRYRUN',
            steps=(
                SequenceStep(step_id='STEP-1', step_kind='wait_alarm_active', payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'}),
                SequenceStep(step_id='STEP-2', step_kind='wait_alarm_inactive', payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'}),
                SequenceStep(
                    step_id='STEP-3',
                    step_kind='emit_dry_run_adapter_command',
                    payload={
                        'command_id': 'CMD-U6-SEQ-DRY-001',
                        'adapter_id': prepared.active_adapter_id,
                        'point_id': 'analog_in_0',
                        'requested_value': '1.5',
                    },
                ),
            ),
        ),
        timestamp=as_event_time(22),
    )
    controller.start_sequence(sequence_id='SEQ-U6-AUTOACK', timestamp=as_event_time(23))
    controller.start_sequence(sequence_id='SEQ-U6-DRYRUN', timestamp=as_event_time(24))
    run_poll_cycles(controller, timestamp_start=25, cycles=2)
    controller.mark_active_device_disconnected(timestamp=as_event_time(1000))
    controller.evaluate_automation(timestamp=as_event_time(1001))
    controller.reconnect_active_device(timestamp=as_event_time(1002))
    run_poll_cycles(controller, timestamp_start=1003, cycles=1)
    controller.evaluate_automation(timestamp=as_event_time(1004))

    bundle = controller.lifecycle_review_bundle()
    assert bundle['command_summary']['command_count'] == 2
    assert bundle['command_summary']['admitted_count'] == 1
    assert bundle['command_summary']['rejected_count'] == 1
    assert bundle['rule_summary']['rule_count'] == 1
    assert bundle['sequence_summary']['sequence_count'] == 2
    assert bundle['sequence_summary']['failed_count'] == 1
    assert bundle['sequence_summary']['completed_count'] == 1
    assert any(row['suppression_reason'] == 'already_satisfied' for row in bundle['recent_rule_rows'])
    assert any(row['event'] == 'completed' and row['sequence_id'] == 'SEQ-U6-AUTOACK' for row in bundle['recent_sequence_rows'])
    assert bundle['recent_sequence_rows'][-1]['event'] == 'command_rejected'
    ack_rows = [row for row in bundle['recent_command_rows'] if row['command_kind'] == 'ack_alarm']
    assert len(ack_rows) == 1
    assert ack_rows[0]['correlation_id'] is not None
    assert bundle['action_claim_summary']['suppressed_count'] >= 1
