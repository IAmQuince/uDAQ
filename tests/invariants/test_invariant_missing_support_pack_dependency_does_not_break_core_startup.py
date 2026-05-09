from __future__ import annotations

import pytest

from universaldaq.adapters import SupportPackLoadState
from universaldaq.app import build_default_service_registry
from universaldaq.common import as_event_time

TEST_DECLARATION = {
    "test_id": "UDQ-TST-INV-015",
    "verifies_requirements": ["UDQ-REQ-ARCH-001", "UDQ-REQ-REL-001"],
    "checks_invariants": ["UDQ-INV-STATE-001", "UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "missing support-pack dependencies degrade to load reports without breaking core startup",
}
pytestmark = pytest.mark.invariants


def test_missing_support_pack_dependency_does_not_break_core_startup(tmp_path, monkeypatch):
    package_root = tmp_path / "universaldaq_brokenpack"
    package_root.mkdir()
    (package_root / "__init__.py").write_text("", encoding="utf-8")
    (package_root / "plugin.py").write_text(
        "import missing_vendor_dependency\n",
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    services = build_default_service_registry(
        load_support_packs=True,
        support_pack_module_names=("universaldaq_brokenpack.plugin",),
    )
    reports = services.adapters.support_pack_load_inventory()
    assert len(reports) == 1
    report = reports[0]
    assert report.pack_id == "universaldaq_brokenpack"
    assert report.state == SupportPackLoadState.ERROR
    assert "ModuleNotFoundError" in report.summary

    discovered = services.adapters.discover_devices(timestamp=as_event_time(41))
    assert discovered
    assert {"generic_adapter_inventory"} == {device.provider_id for device in discovered}
