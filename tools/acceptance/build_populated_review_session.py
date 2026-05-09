from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import mean


def _prepare_import_path(package_root: Path) -> None:
    src_root = package_root / "src"
    if str(src_root) not in sys.path:
        sys.path.insert(0, str(src_root))


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_markdown(path: Path, payload: dict[str, object]) -> None:
    history = payload["history_tier_summary"]
    replay = payload["replay_report"]
    depth = payload["session_depth_summary"]
    checkpoint_summary = payload["checkpoint_summary"]
    characterization = payload["characterization_summary"]
    lines = [
        "# UniversalDAQ Populated Session Review Summary",
        "",
        f"- session_id: {payload['session_id']}",
        f"- hot_recent_sample_count: {history['hot']['recent_sample_count']}",
        f"- warm_variable_row_count: {history['warm']['variable_row_count']}",
        f"- warm_cycle_row_count: {history['warm']['cycle_row_count']}",
        f"- warm_runtime_event_count: {history['warm']['runtime_event_count']}",
        f"- cold_segment_count: {history['cold']['segment_count']}",
        f"- replay_tail_record_count: {replay['tail_record_count']}",
        f"- replay_tail_record_type_count: {replay['tail_record_type_count']}",
        f"- replay_tail_contains_multiple_record_types: {replay['tail_contains_multiple_record_types']}",
        "",
        "## Session depth",
        "",
        f"- total_persisted_records: {depth['total_persisted_records']}",
        f"- checkpoint_count: {depth['checkpoint_count']}",
        f"- valid_checkpoint_count: {depth['valid_checkpoint_count']}",
        f"- checkpoint_sequence_ids: {depth['checkpoint_sequence_ids']}",
        "",
        "## Checkpoint spacing",
        "",
        f"- min_sequence_gap: {checkpoint_summary['checkpoint_spacing']['min_sequence_gap']}",
        f"- max_sequence_gap: {checkpoint_summary['checkpoint_spacing']['max_sequence_gap']}",
        f"- average_sequence_gap: {checkpoint_summary['checkpoint_spacing']['average_sequence_gap']}",
        "",
        "## Long-run characterization",
        "",
        f"- planned_cycle_count: {characterization['planned_cycle_count']}",
        f"- average_records_per_segment: {characterization['average_records_per_segment']}",
        f"- checkpoint_density_per_cycle: {characterization['checkpoint_density_per_cycle']}",
        f"- bounded_run_window_ticks: {characterization['bounded_run_window_ticks']}",
        "",
        "## Sample counts by point",
        "",
    ]
    for point_key, count in payload["history_index_report"]["sample_counts_by_point"].items():
        lines.append(f"- {point_key}: {count}")
    lines.extend(["", "## Replay tail counts by type", ""])
    for record_type, count in replay["tail_record_counts_by_type"].items():
        lines.append(f"- {record_type}: {count}")
    lines.extend(["", "## Recent samples", ""])
    for row in payload["recent_sample_rows"]:
        lines.append(f"- t={row['timestamp']} {row['point_key']} value={row['value']} quality={row['quality']}")
    lines.extend(["", "## Recent variables", ""])
    for row in payload["recent_variable_rows"]:
        lines.append(
            f"- t={row['timestamp']} {row['variable_id']} value={row['value']} state={row['state']} quality={row['quality']}"
        )
    lines.extend(["", "## Recent runtime events", ""])
    for row in payload["recent_runtime_event_rows"]:
        event_type = row.get("event_type", row.get("record_type", "unknown"))
        lines.append(f"- t={row['timestamp']} {event_type}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")



def _write_replay_detail(output_root: Path, review_summary: dict[str, object]) -> None:
    replay_report = dict(review_summary["replay_report"])
    _write_json(output_root / "replay_detail.json", replay_report)
    lines = [
        "# UniversalDAQ Replay Detail",
        "",
        f"- checkpoint_id: {replay_report.get('checkpoint_id')}",
        f"- tail_record_count: {replay_report['tail_record_count']}",
        f"- tail_first_sequence_id: {replay_report['tail_first_sequence_id']}",
        f"- tail_last_sequence_id: {replay_report['tail_last_sequence_id']}",
        f"- tail_record_type_count: {replay_report['tail_record_type_count']}",
        f"- tail_contains_multiple_record_types: {replay_report['tail_contains_multiple_record_types']}",
        "",
        "## Tail counts by type",
        "",
    ]
    for record_type, count in replay_report["tail_record_counts_by_type"].items():
        lines.append(f"- {record_type}: {count}")
    (output_root / "replay_detail.md").write_text("\n".join(lines) + "\n", encoding="utf-8")



def _write_checkpoint_ladder(output_root: Path, review_summary: dict[str, object]) -> None:
    checkpoint_summary = dict(review_summary["checkpoint_summary"])
    _write_json(output_root / "checkpoint_ladder.json", checkpoint_summary)
    lines = [
        "# UniversalDAQ Checkpoint Ladder",
        "",
        f"- checkpoint_available: {checkpoint_summary['checkpoint_available']}",
        f"- valid_checkpoint_count: {checkpoint_summary['valid_checkpoint_count']}",
        f"- latest_checkpoint_id: {checkpoint_summary.get('checkpoint_id')}",
        f"- last_committed_sequence_id: {checkpoint_summary.get('last_committed_sequence_id')}",
        "",
        "## Spacing",
        "",
        f"- min_sequence_gap: {checkpoint_summary['checkpoint_spacing']['min_sequence_gap']}",
        f"- max_sequence_gap: {checkpoint_summary['checkpoint_spacing']['max_sequence_gap']}",
        f"- average_sequence_gap: {checkpoint_summary['checkpoint_spacing']['average_sequence_gap']}",
        "",
        "## Ladder",
        "",
    ]
    for row in checkpoint_summary["checkpoint_ladder"]:
        lines.append(
            f"- {row['checkpoint_id']}: sequence={row['last_committed_sequence_id']} hash_valid={row['hash_valid']} path={row['display_path']}"
        )
    (output_root / "checkpoint_ladder.md").write_text("\n".join(lines) + "\n", encoding="utf-8")



def _write_session_timeline(output_root: Path, review_summary: dict[str, object]) -> None:
    depth = review_summary["session_depth_summary"]
    index = review_summary["history_index_report"]
    timeline = {
        "checkpoint_sequence_ids": list(depth.get("checkpoint_sequence_ids", [])),
        "segment_sequence_ranges": list(depth.get("segment_sequence_ranges", [])),
        "time_range": dict(index.get("time_range", {})),
        "runtime_event_counts_by_type": dict(index.get("runtime_event_counts_by_type", {})),
        "cycle_counts_by_phase": dict(index.get("cycle_counts_by_phase", {})),
    }
    _write_json(output_root / "session_timeline.json", timeline)
    lines = [
        "# UniversalDAQ Session Timeline",
        "",
        f"- checkpoint_sequence_ids: {timeline['checkpoint_sequence_ids']}",
        f"- time_range: {timeline['time_range']}",
        "",
        "## Segment ranges",
        "",
    ]
    for row in timeline["segment_sequence_ranges"]:
        lines.append(
            f"- {row['segment_id']}: {row['first_sequence_id']} -> {row['last_sequence_id']} ({row['record_count']} records)"
        )
    lines.extend(["", "## Runtime event counts", ""])
    for key, count in timeline["runtime_event_counts_by_type"].items():
        lines.append(f"- {key}: {count}")
    lines.extend(["", "## Cycle counts by phase", ""])
    for key, count in timeline["cycle_counts_by_phase"].items():
        lines.append(f"- {key}: {count}")
    (output_root / "session_timeline.md").write_text("\n".join(lines) + "\n", encoding="utf-8")



def _write_longrun_characterization(output_root: Path, review_summary: dict[str, object]) -> None:
    characterization = dict(review_summary["characterization_summary"])
    _write_json(output_root / "longrun_characterization.json", characterization)
    lines = [
        "# UniversalDAQ Long-Run Characterization",
        "",
        f"- planned_cycle_count: {characterization['planned_cycle_count']}",
        f"- average_records_per_segment: {characterization['average_records_per_segment']}",
        f"- checkpoint_density_per_cycle: {characterization['checkpoint_density_per_cycle']}",
        f"- bounded_run_window_ticks: {characterization['bounded_run_window_ticks']}",
        f"- runtime_event_diversity: {characterization['runtime_event_diversity']}",
        f"- queryable_sample_points: {characterization['queryable_sample_points']}",
        f"- queryable_variable_count: {characterization['queryable_variable_count']}",
        "",
        "## Thresholds",
        "",
        f"- meets_min_checkpoint_depth: {characterization['meets_min_checkpoint_depth']}",
        f"- meets_min_segment_depth: {characterization['meets_min_segment_depth']}",
        f"- meets_min_record_depth: {characterization['meets_min_record_depth']}",
    ]
    (output_root / "longrun_characterization.md").write_text("\n".join(lines) + "\n", encoding="utf-8")



def _generated_profile(*, start_tick: int, cycle_count: int) -> list[tuple[int, dict[str, tuple[str, str, str]]]]:
    profile: list[tuple[int, dict[str, tuple[str, str, str]]]] = []
    pressure = 1.0
    temperature = 22.0
    for offset in range(cycle_count):
        tick = start_tick + offset
        pressure += 0.22 + (0.02 if offset % 3 == 0 else 0.0)
        temperature += 0.27 + (0.03 if offset % 4 == 0 else 0.0)
        profile.append(
            (
                tick,
                {
                    "PT-101": (f"{pressure:.1f}", f"{pressure:.1f}", "psi"),
                    "TT-101": (f"{temperature:.1f}", f"{temperature:.1f}", "C"),
                },
            )
        )
    return profile



def _populate_runtime(runtime, *, start_tick: int, cycle_count: int, checkpoint_offsets: set[int], window_name: str) -> None:
    from universaldaq.adapters import SimulatedReadAdapter
    from universaldaq.common import SignalQuality, VariableId, as_event_time
    from universaldaq.signals import VariableEvaluationResult, VariableSnapshot, VariableState
    from universaldaq.ui.models import DeviceLifecycleSummary, VariableHealthSummary

    profile = _generated_profile(start_tick=start_tick, cycle_count=cycle_count)
    previous_variable_snapshots: dict[VariableId, VariableSnapshot] = {}
    for offset, (tick, values) in enumerate(profile, start=1):
        adapter = SimulatedReadAdapter.from_values(adapter_id="SIM-HIST-001", values=values, timestamp=tick)
        poll_result = adapter.poll(timestamp=tick)
        ts = as_event_time(tick)
        runtime.capture_acquisition(adapter_id="SIM-HIST-001", timestamp=ts, poll_result=poll_result)
        runtime.record_state_event(timestamp=ts, event_type="operator_note", attributes={"message": f"cycle-{tick}"})
        runtime.record_state_event(
            timestamp=ts,
            event_type="mode_transition",
            attributes={"mode": "live", "cycle": tick, "window": window_name},
        )
        runtime.record_state_event(
            timestamp=ts,
            event_type="quality_transition",
            attributes={"quality": "good", "tick": tick, "window": window_name},
        )
        if offset in checkpoint_offsets:
            runtime.record_state_event(
                timestamp=ts,
                event_type="checkpoint_boundary",
                attributes={"boundary": "planned", "cycle": tick, "offset": offset},
            )
        pressure = values["PT-101"][1]
        temperature = values["TT-101"][1]
        variable_results = (
            VariableEvaluationResult(
                snapshot=VariableSnapshot(
                    variable_id=VariableId("VAR-PT-AVG"),
                    value=pressure,
                    quality=SignalQuality.GOOD,
                    state=VariableState.HEALTHY,
                    timestamp=ts,
                    dependency_values={"PT-101": pressure},
                ),
                resolved_dependencies={"PT-101": pressure},
            ),
            VariableEvaluationResult(
                snapshot=VariableSnapshot(
                    variable_id=VariableId("VAR-TT-MEAN"),
                    value=temperature,
                    quality=SignalQuality.GOOD,
                    state=VariableState.HEALTHY,
                    timestamp=ts,
                    dependency_values={"TT-101": temperature},
                ),
                resolved_dependencies={"TT-101": temperature},
            ),
        )
        runtime.record_variable_results(timestamp=ts, results=variable_results, previous_snapshots=previous_variable_snapshots)
        previous_variable_snapshots = {result.snapshot.variable_id: result.snapshot for result in variable_results}
        runtime.record_processed_cycle(
            timestamp=ts,
            lifecycle_summary=DeviceLifecycleSummary(
                phase="live",
                detected_device_count=1,
                active_device_key="SIM-DEVICE-001",
                active_adapter_id="SIM-HIST-001",
                projected_point_count=2,
                published_signal_count=2,
                last_poll_snapshot_count=len(poll_result.snapshots),
                disconnected_signal_count=0,
                last_transition="poll_active_adapter",
                needs_review=False,
            ),
            variable_summary=VariableHealthSummary(total_variable_count=2, healthy_count=2),
            changed_signal_ids=("PT-101", "TT-101"),
            poll_result=poll_result,
        )

    tail_tick = start_tick + cycle_count
    runtime.record_state_event(
        timestamp=as_event_time(tail_tick),
        event_type="operator_note",
        attributes={"message": f"tail-verification-window-{window_name}"},
    )
    runtime.flush_journal(now=as_event_time(tail_tick))



def _characterization_summary(review_summary: dict[str, object], *, planned_cycle_count: int) -> dict[str, object]:
    history = review_summary["history_tier_summary"]
    checkpoint_summary = review_summary["checkpoint_summary"]
    index = review_summary["history_index_report"]
    segment_rows = review_summary["artifact_inventory"]["segment_rows"]
    persisted_records = history["cold"]["persisted_record_count"]
    segment_count = max(1, history["cold"]["segment_count"])
    runtime_event_types = index["runtime_event_counts_by_type"]
    variable_ids = index["variable_ids"]
    time_range = index["time_range"]
    bounded_window = 0
    if time_range["min_timestamp"] is not None and time_range["max_timestamp"] is not None:
        bounded_window = int(time_range["max_timestamp"]) - int(time_range["min_timestamp"])
    gaps = checkpoint_summary["checkpoint_spacing"]
    average_gap = 0.0 if gaps["average_sequence_gap"] is None else float(gaps["average_sequence_gap"])
    segment_sizes = [int(row.get("record_count", 0) or 0) for row in segment_rows]
    return {
        "planned_cycle_count": planned_cycle_count,
        "average_records_per_segment": round(persisted_records / segment_count, 2),
        "checkpoint_density_per_cycle": round(checkpoint_summary["valid_checkpoint_count"] / max(1, planned_cycle_count), 3),
        "bounded_run_window_ticks": bounded_window,
        "runtime_event_diversity": len(runtime_event_types),
        "queryable_sample_points": sorted(index["sample_counts_by_point"].keys()),
        "queryable_variable_count": len(variable_ids),
        "max_segment_record_count": max(segment_sizes) if segment_sizes else 0,
        "min_segment_record_count": min(segment_sizes) if segment_sizes else 0,
        "average_checkpoint_sequence_gap": average_gap,
        "meets_min_checkpoint_depth": checkpoint_summary["valid_checkpoint_count"] >= 4,
        "meets_min_segment_depth": history["cold"]["segment_count"] >= 20,
        "meets_min_record_depth": persisted_records >= 100,
    }



def build_populated_review_session(
    *,
    package_root: Path,
    output_root: Path,
    session_id: str = "SESSION-POPULATED-REVIEW",
    cycle_count: int = 18,
    checkpoint_interval_cycles: int = 4,
    start_tick: int = 30,
) -> dict[str, object]:
    _prepare_import_path(package_root)
    from universaldaq.runtime import RuntimeQualityService

    runtime_root = output_root / "runtime"
    runtime = RuntimeQualityService(
        journal_file_path=runtime_root / "session.jsonl",
        journal_max_segment_records=4,
        point_history_limit=160,
        event_history_limit=192,
        cycle_history_limit=192,
        variable_history_limit=192,
        presentation_interval_ticks=1,
        session_id=session_id,
        auto_checkpoint_interval_cycles=checkpoint_interval_cycles,
    )
    checkpoint_offsets = set(range(checkpoint_interval_cycles, cycle_count + 1, checkpoint_interval_cycles))
    _populate_runtime(
        runtime,
        start_tick=start_tick,
        cycle_count=cycle_count,
        checkpoint_offsets=checkpoint_offsets,
        window_name="bounded-longrun-v1",
    )
    review_summary = runtime.build_review_summary(limit=16)
    review_summary["session_root"] = str(runtime_root / "sessions" / session_id)
    review_summary["characterization_summary"] = _characterization_summary(review_summary, planned_cycle_count=cycle_count)
    _write_json(output_root / "review_summary.json", review_summary)
    _write_markdown(output_root / "review_summary.md", review_summary)
    _write_replay_detail(output_root, review_summary)
    _write_checkpoint_ladder(output_root, review_summary)
    _write_session_timeline(output_root, review_summary)
    _write_longrun_characterization(output_root, review_summary)
    return review_summary



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    parser.add_argument("--output-root", default="proof/reviewability")
    parser.add_argument("--session-id", default="SESSION-POPULATED-REVIEW")
    parser.add_argument("--cycle-count", type=int, default=18)
    parser.add_argument("--checkpoint-interval-cycles", type=int, default=4)
    args = parser.parse_args()
    package_root = Path(args.package_root).resolve()
    output_root = (package_root / args.output_root).resolve() if not Path(args.output_root).is_absolute() else Path(args.output_root).resolve()
    report = build_populated_review_session(
        package_root=package_root,
        output_root=output_root,
        session_id=args.session_id,
        cycle_count=max(1, args.cycle_count),
        checkpoint_interval_cycles=max(1, args.checkpoint_interval_cycles),
    )
    history = report["history_tier_summary"]
    replay = report["replay_report"]
    characterization = report["characterization_summary"]
    print(
        f"populated-review-session: samples={history['hot']['recent_sample_count']} variables={history['warm']['variable_row_count']} cycles={history['warm']['cycle_row_count']} checkpoints={report['checkpoint_summary']['valid_checkpoint_count']} tail={replay['tail_record_count']} records={history['cold']['persisted_record_count']} report_dir={output_root} window={characterization['bounded_run_window_ticks']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
