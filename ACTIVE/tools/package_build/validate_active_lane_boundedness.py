from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools._shared import canonical_review_entry, current_package_id


def tree_stats(path: Path) -> dict[str, int]:
    files = [p for p in path.rglob("*") if p.is_file()] if path.exists() else []
    return {"file_count": len(files), "byte_count": sum(p.stat().st_size for p in files)}


def build_inventory(root: Path) -> dict[str, object]:
    release_top = root / "docs" / "release"
    package_id = current_package_id(root)
    canonical_review = canonical_review_entry(root)
    top_review_files = sorted(p.name for p in release_top.glob("REVIEW_START_HERE__*.md") if p.parent == release_top)
    active_accept = sorted(p.name for p in (root / "proof" / "acceptance").iterdir() if p.is_dir())
    archive_accept_root = root / "proof" / "archive" / "acceptance"
    archive_accept = sorted(p.name for p in archive_accept_root.iterdir() if p.is_dir()) if archive_accept_root.exists() else []
    active_audit_files = sorted(p.name for p in (root / "audit_reports" / "active").iterdir() if p.is_file() and p.name != ".gitkeep")
    release_top_files = sorted(p.name for p in release_top.iterdir() if p.is_file())
    return {
        "package_id": package_id,
        "canonical_review_entry": str(canonical_review),
        "release_top_level_review_files": top_review_files,
        "release_top_level_file_count": len(release_top_files),
        "release_top_level_files": release_top_files,
        "historical_release_file_count": len([p for p in (release_top / "history").rglob("*") if p.is_file()]) if (release_top / "history").exists() else 0,
        "active_acceptance_runs": active_accept,
        "archived_acceptance_summaries": archive_accept,
        "active_acceptance_tree": tree_stats(root / "proof" / "acceptance"),
        "active_audit_file_count": len(active_audit_files),
        "active_audit_files": active_audit_files,
    }


def validate(root: Path) -> tuple[list[str], dict[str, object]]:
    findings: list[str] = []
    inv = build_inventory(root)
    review_files = inv["release_top_level_review_files"]
    canonical_review = canonical_review_entry(root)
    if review_files != [canonical_review.name]:
        findings.append(f"top-level release review entries not bounded to canonical current doc: {review_files}")
    active_runs = inv["active_acceptance_runs"]
    if len(active_runs) != 1:
        findings.append(f"active acceptance lane must contain exactly one run: {active_runs}")
    if inv["release_top_level_file_count"] > 12:
        findings.append(f"top-level release lane too large: {inv['release_top_level_file_count']}")
    if inv["active_audit_file_count"] > 8:
        findings.append(f"active audit lane too large: {inv['active_audit_file_count']}")
    if not (root / canonical_review).exists():
        findings.append(f"missing canonical review entry: {canonical_review}")
    return findings, inv


def render_md(inv: dict[str, object]) -> str:
    lines = [
        "# Active Lane Inventory",
        "",
        f"- package_id: `{inv['package_id']}`",
        f"- canonical_review_entry: `{inv['canonical_review_entry']}`",
        f"- release_top_level_file_count: `{inv['release_top_level_file_count']}`",
        f"- historical_release_file_count: `{inv['historical_release_file_count']}`",
        f"- active_acceptance_runs: `{', '.join(inv['active_acceptance_runs'])}`",
        f"- archived_acceptance_summaries: `{', '.join(inv['archived_acceptance_summaries'])}`",
        f"- active_audit_file_count: `{inv['active_audit_file_count']}`",
        "",
        "## Active audit files",
    ]
    lines.extend(f"- `{name}`" for name in inv['active_audit_files'])
    lines.extend(["", "## Top-level release files"])
    lines.extend(f"- `{name}`" for name in inv['release_top_level_files'])
    lines.extend(["", "## Active acceptance tree", f"- file_count: `{inv['active_acceptance_tree']['file_count']}`", f"- byte_count: `{inv['active_acceptance_tree']['byte_count']}`", ""])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", default=".")
    parser.add_argument("--report-json", default="")
    parser.add_argument("--report-md", default="")
    args = parser.parse_args()
    root = Path(args.package_root).resolve()
    findings, inv = validate(root)
    if args.report_json:
        out = root / args.report_json
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(inv, indent=2) + "\n", encoding="utf-8")
    if args.report_md:
        out = root / args.report_md
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_md(inv), encoding="utf-8")
    if findings:
        for item in findings:
            print(item)
        return 1
    print("active-lane boundedness: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
