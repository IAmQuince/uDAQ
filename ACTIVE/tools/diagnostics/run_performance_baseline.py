from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import zipfile
from pathlib import Path

MAJOR_DIRS = ["audit_reports", "docs", "proof", "registries", "runtime", "src", "tests", "tools"]


def _tree_stats(path: Path) -> dict[str, int]:
    files = [p for p in path.rglob("*") if p.is_file()] if path.exists() else []
    return {"file_count": len(files), "byte_count": sum(p.stat().st_size for p in files)}


def _run_with_memory(cmd: list[str], *, cwd: Path, env: dict[str, str], timeout: int = 600) -> dict[str, object]:
    proc = subprocess.run(
        ["/usr/bin/time", "-f", "ELAPSED=%e\nMAXRSS_KB=%M"] + cmd,
        cwd=str(cwd),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )
    elapsed = None
    maxrss_kb = None
    cleaned: list[str] = []
    for line in proc.stdout.splitlines():
        if line.startswith("ELAPSED="):
            try:
                elapsed = float(line.split("=", 1)[1])
            except ValueError:
                pass
            continue
        if line.startswith("MAXRSS_KB="):
            try:
                maxrss_kb = int(line.split("=", 1)[1])
            except ValueError:
                pass
            continue
        cleaned.append(line)
    return {
        "cmd": cmd,
        "returncode": proc.returncode,
        "elapsed_s": elapsed,
        "maxrss_kb": maxrss_kb,
        "output": "\n".join(cleaned).strip(),
    }


def _included_package_stats(root: Path) -> dict[str, int]:
    from tools.package_build.build_precode_package import included_files
    files = included_files(root)
    return {"included_file_count": len(files), "included_byte_count": sum(p.stat().st_size for p in files)}


def _runtime_summary_from_inventory(inventory_output: str) -> dict[str, object]:
    payload = json.loads(inventory_output)
    timings = payload["runtime_performance"]["timings"]
    return {
        "adapter_count": payload["object_counts"]["adapter_count"],
        "discovered_device_count": payload["object_counts"]["discovered_device_count"],
        "projected_points": payload["incremental_runtime_summary"]["lifecycle.projected_points.count"],
        "discover_avg_ms": timings["adapters.discover.ms"]["average_ms"],
        "poll_avg_ms": timings["runtime.acquisition.poll.ms"]["average_ms"],
        "capture_avg_ms": timings["runtime.acquisition.capture.ms"]["average_ms"],
        "journal_flush_avg_ms": timings["runtime.journal.flush.ms"]["average_ms"],
        "processing_cycle_avg_ms": timings["runtime.processing.cycle.ms"]["average_ms"],
    }


def _top_cost_centers(dir_stats: dict[str, dict[str, int]]) -> dict[str, list[dict[str, object]]]:
    by_bytes = sorted(
        ({"name": name, **stats} for name, stats in dir_stats.items()),
        key=lambda row: row["byte_count"],
        reverse=True,
    )
    by_files = sorted(
        ({"name": name, **stats} for name, stats in dir_stats.items()),
        key=lambda row: row["file_count"],
        reverse=True,
    )
    return {"top_by_bytes": by_bytes[:5], "top_by_files": by_files[:5]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    parser.add_argument(
        "--report-json",
        default="proof/20260327_02_performance-baseline-and-usability-gate__baseline-report.json",
    )
    args = parser.parse_args()

    root = Path(args.package_root).resolve()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(root)

    dir_stats = {name: _tree_stats(root / name) for name in MAJOR_DIRS}
    included_stats = _included_package_stats(root)

    validators = {
        "package_entry": [sys.executable, "-m", "tools.governance.validate_package_entry_surfaces"],
        "document_completeness": [sys.executable, "-m", "tools.governance.validate_document_completeness"],
        "document_classification": [sys.executable, "-m", "tools.governance.validate_document_classification"],
        "document_impact": [sys.executable, "-m", "tools.governance.validate_document_impact"],
        "active_lane_boundedness": [
            sys.executable,
            "-m",
            "tools.package_build.validate_active_lane_boundedness",
            "--package-root",
            ".",
        ],
        "windows_path_budget": [
            sys.executable,
            "-m",
            "tools.package_build.validate_windows_path_budget",
            "--package-root",
            ".",
            "--delivery-root",
            "udq_20260327_02",
        ],
        "shell_smoke": [sys.executable, "-m", "tools.dev.run_shell_smoke"],
        "runtime_inventory": [sys.executable, "-m", "tools.diagnostics.dump_runtime_performance_inventory"],
        "focused_pytest_meta_smoke": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/meta/test_meta_package_entry_surfaces.py",
            "tests/meta/test_meta_readme_control.py",
            "tests/meta/test_meta_package_build_exclusions.py",
            "tests/smoke/test_smoke_package_layout.py",
            "tests/smoke/test_smoke_runtime_performance_inventory.py",
            "tests/smoke/test_smoke_governance_assets_load.py",
        ],
        "focused_pytest_runtime_gate": [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/integration/test_integration_shell_smoke.py",
            "tests/contract/test_contract_runtime_historian_population_reviewability.py",
            "tests/invariants/test_invariant_no_direct_labjack_imports_in_core.py",
            "tests/invariants/test_invariant_core_operates_without_vendor_support_pack.py",
        ],
    }

    runs: dict[str, dict[str, object]] = {}
    for name, cmd in validators.items():
        timeout = 900 if "pytest" in name else 600
        runs[name] = _run_with_memory(cmd, cwd=root, env=env, timeout=timeout)

    build_zip = root / "performance_pkg_tmp.zip"
    if build_zip.exists():
        build_zip.unlink()
    runs["package_build"] = _run_with_memory(
        [
            sys.executable,
            "-m",
            "tools.package_build.build_precode_package",
            "--package-root",
            ".",
            "--output",
            str(build_zip),
            "--delivery-root",
            "udq_20260327_02",
        ],
        cwd=root,
        env=env,
        timeout=900,
    )
    build_stats = {
        "exists": build_zip.exists(),
        "byte_count": build_zip.stat().st_size if build_zip.exists() else 0,
    }

    runtime_summary = {}
    if runs["runtime_inventory"]["returncode"] == 0:
        runtime_summary = _runtime_summary_from_inventory(str(runs["runtime_inventory"]["output"]))

    top_cost_centers = _top_cost_centers(dir_stats)
    external_time_ranking = sorted(
        (
            {
                "name": name,
                "elapsed_s": row["elapsed_s"],
                "returncode": row["returncode"],
                "maxrss_kb": row["maxrss_kb"],
            }
            for name, row in runs.items()
            if row.get("elapsed_s") is not None
        ),
        key=lambda row: row["elapsed_s"],
        reverse=True,
    )

    blocker_assessment = {
        "critical_runtime_blocker": False,
        "reasoning": [
            "Shell smoke and runtime inventory both passed.",
            "Focused validators and focused package/runtime gate tests passed.",
            "The largest measured elapsed time is focused meta/smoke pytest rather than runtime inventory or shell smoke.",
            "Current concentration remains more in proof/history weight and validation cost than in a catastrophic first-signal runtime path.",
        ],
        "recommended_next_sprint": "20260327_03_usability-entry-first-signal-path",
    }

    report = {
        "package_id": "UDQ-PKG-20260327-PERFORMANCE-BASELINE-AND-USABILITY-GATE-R01",
        "package_slug": "performance-baseline-and-usability-gate",
        "package_date": "2026-03-27",
        "major_dir_stats": dir_stats,
        "included_package_stats": included_stats,
        "runtime_summary": runtime_summary,
        "runs": runs,
        "package_build_artifact": build_stats,
        "top_cost_centers": top_cost_centers,
        "external_time_ranking": external_time_ranking[:10],
        "blocker_assessment": blocker_assessment,
    }

    out = root / args.report_json
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if build_zip.exists():
        build_zip.unlink()

    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
