from __future__ import annotations

import pytest

from universaldaq.common import AuthorizationState
from universaldaq.ui import AuthoritySurface

TEST_DECLARATION = {'test_id': 'UDQ-TST-CON-005', 'verifies_requirements': ['UDQ-REQ-ARCH-002', 'UDQ-REQ-SEC-001', 'UDQ-REQ-SEC-002', 'UDQ-REQ-UI-001'], 'checks_invariants': ['UDQ-INV-STATE-004'], 'worked_example_reference': 'UDQ-EXM-001', 'expected_proof_output': 'authorization vs UI enablement trace'}
pytestmark = pytest.mark.contract


def test_contract_authorization_vs_ui_enablement():
    view_only_surface = AuthoritySurface(authorization_state=AuthorizationState.VIEW_ONLY, ui_enabled=False)
    interactive_surface = AuthoritySurface(authorization_state=AuthorizationState.ALLOWED, ui_enabled=True)
    assert view_only_surface.status_label == 'disabled'
    assert view_only_surface.presents_false_authority is False
    assert interactive_surface.status_label == 'interactive'
    assert interactive_surface.presents_false_authority is False
