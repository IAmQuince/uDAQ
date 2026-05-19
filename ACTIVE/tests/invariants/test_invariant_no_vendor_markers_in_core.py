from __future__ import annotations

import pytest

from tests.conftest import PACKAGE_ROOT

TEST_DECLARATION = {
    "test_id": "UDQ-TST-INV-016",
    "verifies_requirements": ["UDQ-REQ-ARCH-001", "UDQ-REQ-ARCH-002"],
    "checks_invariants": ["UDQ-INV-STATE-004"],
    "worked_example_reference": None,
    "expected_proof_output": "vendor-specific markers do not leak into universal core python modules",
}
pytestmark = pytest.mark.invariants

FORBIDDEN_MARKERS = (
    "LabJack",
    "labjack",
    "\bu6\b",
    "AIN0",
    "AIN1",
    "Arduino",
    "Raspberry Pi",
    "RPi",
)


def test_universal_core_contains_no_vendor_markers_in_python_modules():
    failures: list[str] = []
    for path in sorted((PACKAGE_ROOT / "src" / "universaldaq").rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        lowered = text.lower()
        if "labjack" in lowered or "arduino" in text or "raspberry pi" in lowered or "rpi" in text:
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
            continue
        if "AIN0" in text or "AIN1" in text:
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
            continue
        # keep a separate word-boundary check for raw 'u6' tokens
        import re

        if re.search(r"\bu6\b", text):
            failures.append(str(path.relative_to(PACKAGE_ROOT)))
    assert not failures, failures
