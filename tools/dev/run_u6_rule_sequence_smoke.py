from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a bounded UniversalDAQ LabJack U6 rules/sequences smoke test.')
    parser.add_argument('--package-root', default='.')
    parser.add_argument('--summary', default='proof/U6_RULE_SEQUENCE_SUMMARY.txt')
    parser.add_argument('--journal', default='proof/U6_RULE_SEQUENCE_JOURNAL.jsonl')
    parser.add_argument('--serial-number', default='AUTO')
    parser.add_argument('--real-hardware', action='store_true')
    parser.add_argument('--cycles', type=int, default=8)
    args = parser.parse_args()

    package_root = Path(args.package_root).resolve()
    summary_path = (package_root / args.summary).resolve() if not Path(args.summary).is_absolute() else Path(args.summary)
    journal_path = (package_root / args.journal).resolve() if not Path(args.journal).is_absolute() else Path(args.journal)
    src_root = package_root / 'src'
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))

    from tools.dev._u6_live_support import (
        bootstrap_controller,
        build_services,
        install_labjack_support_pack,
        prepare_u6_live_value_slice,
        run_poll_cycles,
    )
    from universaldaq.common import as_event_time
    from universaldaq.rules import RuleDefinition
    from universaldaq.sequences import SequenceDefinition, SequenceStep

    lines: list[str] = []
    exit_code = 0
    try:
        services = build_services(journal_path=journal_path)
        install_labjack_support_pack(
            services,
            real_hardware=args.real_hardware,
            serial_number=None if args.serial_number == 'AUTO' else args.serial_number,
            simulated_serial_number='470277',
        )
        controller = bootstrap_controller(services=services, profile_id='PROF-U6-RULESEQ', actor_id='u6-rule-seq')
        prepared = prepare_u6_live_value_slice(controller, timestamp_start=3)
        controller.register_rule_definition(
            definition=RuleDefinition(
                rule_id='RULE-U6-AUTOACK',
                condition_kind='alarm_active_unacknowledged',
                condition_payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'},
                action_kind='ack_alarm',
                action_payload={'alarm_id': 'ALM-U6-AVG-DEGRADED'},
                cooldown_ticks=0,
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
        run_poll_cycles(controller, timestamp_start=25, cycles=args.cycles)
        controller.mark_active_device_disconnected(timestamp=as_event_time(1000))
        controller.evaluate_automation(timestamp=as_event_time(1001))
        controller.reconnect_active_device(timestamp=as_event_time(1002))
        run_poll_cycles(controller, timestamp_start=1003, cycles=1)
        controller.evaluate_automation(timestamp=as_event_time(1004))
        bundle = controller.lifecycle_review_bundle()
        summary_payload = {
            'phase': controller.session.ui_session.device_lifecycle_phase.value,
            'runtime_status': bundle['runtime_status'],
            'event_alarm_summary': bundle['event_alarm_summary'],
            'command_summary': bundle['command_summary'],
            'action_claim_summary': bundle['action_claim_summary'],
            'rule_summary': bundle['rule_summary'],
            'sequence_summary': bundle['sequence_summary'],
            'active_alarm_rows': bundle['active_alarm_rows'],
            'recent_event_rows': bundle['recent_event_rows'],
            'recent_command_rows': bundle['recent_command_rows'],
            'recent_action_claim_rows': bundle['recent_action_claim_rows'],
            'recent_rule_rows': bundle['recent_rule_rows'],
            'recent_sequence_rows': bundle['recent_sequence_rows'],
            'incremental_runtime_summary': bundle['incremental_runtime_summary'],
        }
        lines.extend(['UDQ U6 Rules/Sequences Smoke', '===========================', json.dumps(summary_payload, indent=2, sort_keys=True)])
    except Exception as exc:
        exit_code = 2
        lines.extend(['ERROR', '-----', str(exc), '', traceback.format_exc()])

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'udq-u6-rule-sequence-smoke: wrote {summary_path}')
    return exit_code


if __name__ == '__main__':
    raise SystemExit(main())
