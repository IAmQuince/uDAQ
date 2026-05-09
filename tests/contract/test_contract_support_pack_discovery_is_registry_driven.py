from __future__ import annotations

import pytest

from universaldaq.adapters import discover_optional_support_pack_modules

TEST_DECLARATION = {
    "test_id": "UDQ-TST-CON-031",
    "verifies_requirements": ["UDQ-REQ-ARCH-001", "UDQ-REQ-DEV-001"],
    "checks_invariants": ["UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "support-pack discovery resolves through generic module discovery rather than a hard-coded vendor list",
}
pytestmark = pytest.mark.contract


def test_support_pack_discovery_finds_available_plugin_modules_without_static_vendor_list():
    modules = set(discover_optional_support_pack_modules())
    assert {
        "universaldaq_labjack.plugin",
        "universaldaq_arduino.plugin",
        "universaldaq_rpi.plugin",
    } <= modules
