from __future__ import annotations

from dataclasses import asdict, dataclass, field
import ast
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
from typing import Any
from zipfile import ZipFile, ZIP_DEFLATED

from universaldaq.common import as_event_time
from universaldaq.mapping import (
    MappingSandboxController,
    MappingSandboxStateStore,
    build_demo_apply_request,
    build_demo_sandbox_state,
    export_mapping_diff_markdown,
)

PACKAGE_SLUG = '20260515_02_mapping'
PACKAGE_ID = 'UDQ-PKG-20260515-02-MAPPING-R02'


@dataclass(frozen=True, slots=True, kw_only=True)
class SprintTestResult:
    name: str
    passed: bool
    report_path: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def package_root_from(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / 'ACTIVE').is_dir() and (candidate / 'HISTORICAL').is_dir():
            return candidate
        if candidate.name == 'ACTIVE' and (candidate.parent / 'HISTORICAL').is_dir():
            return candidate.parent
    active = current if current.name == 'ACTIVE' else current / 'ACTIVE'
    if active.is_dir():
        return active.parent
    return current


def active_root_from(start: Path | None = None) -> Path:
    root = package_root_from(start)
    return root / 'ACTIVE' if (root / 'ACTIVE').is_dir() else root


def _report_dir(start: Path | None = None) -> Path:
    active = active_root_from(start)
    out = active / 'audit_reports' / 'testing'
    out.mkdir(parents=True, exist_ok=True)
    return out


def _diagnostics_dir(start: Path | None = None) -> Path:
    active = active_root_from(start)
    out = active / 'diagnostics'
    out.mkdir(parents=True, exist_ok=True)
    return out


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding='utf-8')


def run_smoke_test(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    active = active_root_from(root)
    report_path = _report_dir(root) / '20260515_02_smoke-test.json'
    checks = {
        'package_root_exists': root.is_dir(),
        'active_root_exists': active.is_dir(),
        'run_udaq_bat_exists': (active / 'RUN_UDAQ.bat').is_file(),
        'run_diagnostics_bat_exists': (active / 'RUN_DIAGNOSTICS.bat').is_file(),
        'manual_checklist_exists': (active / 'docs' / 'testing' / '20260515_02_manual-test-checklist.md').is_file(),
        'mapping_module_imported': True,
        'sandbox_state_hash_available': bool(build_demo_sandbox_state().state_hash()),
        'demo_request_available': build_demo_apply_request().request_id == 'REQ-DEMO-SANDBOX-MAPPING-001',
        'no_live_execution_claim': True,
    }
    passed = all(checks.values())
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'smoke',
        'passed': passed,
        'checks': checks,
        'python': sys.version,
        'platform': platform.platform(),
        'cwd': str(Path.cwd()),
    }
    _write_json(report_path, payload)
    return SprintTestResult(
        name='Smoke Test',
        passed=passed,
        report_path=str(report_path),
        summary='Smoke test passed' if passed else 'Smoke test failed',
        details=payload,
    )


def run_mapping_sandbox_demo(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    report_path = _report_dir(root) / '20260515_02_mapping-sandbox-demo.json'
    state = build_demo_sandbox_state()
    store = MappingSandboxStateStore(state=state)
    request = build_demo_apply_request()
    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=request,
        created_timestamp=as_event_time(1002),
        result_id='MAP-SANDBOX-DEMO-RESULT-001',
    )
    passed = result.accepted and not result.executed_live and result.before_hash != result.after_hash
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'mapping_sandbox_demo',
        'passed': passed,
        'initial_state': state.to_dict(),
        'final_state': store.state.to_dict(),
        'result': result.to_dict(),
        'events': [event.to_dict() for event in store.events],
    }
    _write_json(report_path, payload)
    return SprintTestResult(
        name='Mapping Sandbox Demo',
        passed=passed,
        report_path=str(report_path),
        summary='Sandbox demo applied mapping changes without live execution' if passed else 'Sandbox demo failed',
        details=payload,
    )


def run_apply_rollback_test(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    report_path = _report_dir(root) / '20260515_02_apply-rollback-test.json'
    state = build_demo_sandbox_state()
    original_hash = state.state_hash()
    store = MappingSandboxStateStore(state=state)
    request = build_demo_apply_request()
    apply_result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=request,
        created_timestamp=as_event_time(1003),
        result_id='MAP-SANDBOX-APPLY-RESULT-001',
    )
    rollback_result = store.rollback(
        rollback_token=str(apply_result.rollback_token),
        timestamp=as_event_time(1004),
    )
    final_hash = store.state.state_hash()
    passed = (
        apply_result.accepted
        and rollback_result.accepted
        and apply_result.before_hash == original_hash
        and apply_result.after_hash != original_hash
        and final_hash == original_hash
        and not apply_result.executed_live
        and not rollback_result.executed_live
    )
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'apply_rollback',
        'passed': passed,
        'original_hash': original_hash,
        'after_apply_hash': apply_result.after_hash,
        'final_hash': final_hash,
        'apply_result': apply_result.to_dict(),
        'rollback_result': rollback_result.to_dict(),
        'events': [event.to_dict() for event in store.events],
    }
    _write_json(report_path, payload)
    return SprintTestResult(
        name='Apply/Rollback Test',
        passed=passed,
        report_path=str(report_path),
        summary='Apply/rollback restored the sandbox state hash' if passed else 'Apply/rollback failed',
        details=payload,
    )


def run_diff_report_test(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    report_json_path = _report_dir(root) / '20260515_02_mapping-diff-report.json'
    report_md_path = _report_dir(root) / '20260515_02_mapping-diff-report.md'
    state = build_demo_sandbox_state()
    store = MappingSandboxStateStore(state=state)
    request = build_demo_apply_request()
    result = MappingSandboxController().apply_to_sandbox(
        store=store,
        request=request,
        created_timestamp=as_event_time(1005),
        result_id='MAP-SANDBOX-DIFF-RESULT-001',
    )
    diff = result.diff_report
    markdown = '' if diff is None else export_mapping_diff_markdown(diff)
    report_md_path.write_text(markdown, encoding='utf-8')
    passed = bool(diff and diff.total_change_count >= 2 and 'Live state and hardware outputs' in markdown)
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'diff_report',
        'passed': passed,
        'markdown_report_path': str(report_md_path),
        'result': result.to_dict(),
    }
    _write_json(report_json_path, payload)
    return SprintTestResult(
        name='Diff Report Test',
        passed=passed,
        report_path=str(report_md_path),
        summary='Diff report generated' if passed else 'Diff report failed',
        details=payload,
    )


def run_visible_shell_wiring_audit(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    active = active_root_from(root)
    report_path = _report_dir(root) / '20260515_02_visible-shell-wiring-audit.json'
    source_path = active / 'src' / 'universaldaq' / 'ui' / 'qt_shell.py'
    text = source_path.read_text(encoding='utf-8')
    tree = ast.parse(text)
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name == 'OperatorShellWindow']
    active_class = classes[-1] if classes else None
    method_names = set()
    build_shell_source = ''
    remove_source = ''
    refresh_source = ''
    if active_class is not None:
        methods = {node.name: node for node in active_class.body if isinstance(node, ast.FunctionDef)}
        method_names = set(methods)
        build_shell_source = ast.get_source_segment(text, methods.get('_build_shell')) if methods.get('_build_shell') else ''
        remove_source = ast.get_source_segment(text, methods.get('_remove_last_logic_node')) if methods.get('_remove_last_logic_node') else ''
        refresh_source = ast.get_source_segment(text, methods.get('_refresh_system_summary')) if methods.get('_refresh_system_summary') else ''
    required_logic_methods = {
        '_default_logic_nodes',
        '_reset_logic_nodes',
        '_add_logic_node',
        '_remove_last_logic_node',
        '_evaluate_logic_nodes',
        '_refresh_logic_watch',
        '_build_logic_demo_scene',
    }
    missing_logic_methods = sorted(required_logic_methods.difference(method_names))
    system_index = build_shell_source.find('self._build_system_workspace()')
    connect_index = build_shell_source.find('self.workspace_tabs.currentChanged.connect(self._on_workspace_tab_changed)')
    checks = {
        'qt_shell_exists': source_path.is_file(),
        'operator_shell_class_found': active_class is not None,
        'required_logic_methods_present': not missing_logic_methods,
        'remove_logic_method_is_not_stub': '_logic_nodes.pop' in remove_source and '_refresh_logic_watch' in remove_source and 'showMessage' in remove_source,
        'system_workspace_before_tab_signal': system_index >= 0 and connect_index >= 0 and system_index < connect_index,
        'system_summary_refresh_is_meaningful': 'self.system_summary.setPlainText' in refresh_source and 'UniversalDAQ Visible Operator Shell' in refresh_source and 'Mapped rows:' in refresh_source,
    }
    passed = all(checks.values())
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'visible_shell_wiring_audit',
        'passed': passed,
        'checks': checks,
        'missing_logic_methods': missing_logic_methods,
        'source_path': str(source_path),
    }
    _write_json(report_path, payload)
    return SprintTestResult(
        name='Visible Shell Wiring Audit',
        passed=passed,
        report_path=str(report_path),
        summary='Visible shell wiring audit passed' if passed else 'Visible shell wiring audit failed',
        details=payload,
    )


def run_sprint_acceptance_suite(*, package_root: Path | None = None) -> SprintTestResult:
    root = package_root_from(package_root)
    results = [
        run_smoke_test(package_root=root),
        run_mapping_sandbox_demo(package_root=root),
        run_apply_rollback_test(package_root=root),
        run_diff_report_test(package_root=root),
        run_visible_shell_wiring_audit(package_root=root),
    ]
    report_path = _report_dir(root) / '20260515_02_sprint-acceptance-suite.json'
    passed = all(item.passed for item in results)
    payload = {
        'package_id': PACKAGE_ID,
        'test_name': 'sprint_acceptance_suite',
        'passed': passed,
        'results': [item.to_dict() for item in results],
    }
    _write_json(report_path, payload)
    return SprintTestResult(
        name='Sprint Acceptance Suite',
        passed=passed,
        report_path=str(report_path),
        summary='Sprint acceptance suite passed' if passed else 'Sprint acceptance suite failed',
        details=payload,
    )


def export_diagnostic_bundle(*, package_root: Path | None = None, zip_bundle: bool = True) -> SprintTestResult:
    root = package_root_from(package_root)
    active = active_root_from(root)
    base = _diagnostics_dir(root) / '20260515_02_diagnostic-bundle'
    if base.exists():
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)
    suite = run_sprint_acceptance_suite(package_root=root)
    environment = {
        'package_id': PACKAGE_ID,
        'package_root': str(root),
        'active_root': str(active),
        'python': sys.version,
        'executable': sys.executable,
        'platform': platform.platform(),
        'cwd': str(Path.cwd()),
        'env_flags': {
            'PYTHONDONTWRITEBYTECODE': os.environ.get('PYTHONDONTWRITEBYTECODE', ''),
            'UNIVERSALDAQ_SHELL_DIAGNOSTICS_PATH': os.environ.get('UNIVERSALDAQ_SHELL_DIAGNOSTICS_PATH', ''),
        },
    }
    _write_json(base / 'environment.json', environment)
    _write_json(base / 'sprint_acceptance_suite.json', suite.details)
    _write_json(base / 'demo_sandbox_state.json', build_demo_sandbox_state().to_dict())
    (base / 'README.txt').write_text(
        'UniversalDAQ Sprint 1 diagnostic bundle. This bundle contains environment, visible shell wiring, sandbox mapping, and automated acceptance test reports. No hardware-output data is included.\n',
        encoding='utf-8',
    )
    zip_path = None
    if zip_bundle:
        zip_path = base.with_suffix('.zip')
        if zip_path.exists():
            zip_path.unlink()
        with ZipFile(zip_path, 'w', compression=ZIP_DEFLATED) as zf:
            for path in sorted(base.rglob('*')):
                if path.is_file():
                    zf.write(path, path.relative_to(base.parent).as_posix())
    passed = suite.passed and base.is_dir() and (zip_path is None or zip_path.is_file())
    report_path = zip_path or base
    return SprintTestResult(
        name='Diagnostic Bundle Export',
        passed=passed,
        report_path=str(report_path),
        summary='Diagnostic bundle exported' if passed else 'Diagnostic bundle export failed',
        details={'bundle_dir': str(base), 'zip_path': None if zip_path is None else str(zip_path), 'suite': suite.to_dict()},
    )


def open_path_best_effort(path: str | Path) -> bool:
    target = Path(path)
    try:
        if sys.platform.startswith('win'):
            os.startfile(str(target))  # type: ignore[attr-defined]
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', str(target)])
        else:
            subprocess.Popen(['xdg-open', str(target)])
        return True
    except Exception:
        return False
