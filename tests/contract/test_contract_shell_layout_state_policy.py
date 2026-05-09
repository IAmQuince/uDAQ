from __future__ import annotations

import pytest

from universaldaq.ui.layout_state import (
    Rect,
    clamp_pip_rect,
    clamp_window_rect,
    default_graph_presentation_for_workspace,
    default_pip_rect,
    default_window_rect,
    normalize_splitter_sizes,
)

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-065',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-006'],
    'checks_invariants': ['UDQ-INV-EVID-006'],
    'worked_example_reference': None,
    'expected_proof_output': 'shell geometry policy clamps restored bounds, normalizes splitter sizes, and assigns workspace-aware graph presentations',
}
pytestmark = pytest.mark.contract


def test_default_window_rect_stays_inside_available_geometry() -> None:
    available = Rect(x=0, y=0, width=1920, height=1040)
    rect = default_window_rect(available=available)
    assert rect.x >= available.x
    assert rect.y >= available.y
    assert rect.right <= available.right
    assert rect.bottom <= available.bottom


def test_clamp_window_rect_brings_offscreen_window_back_into_bounds() -> None:
    available = Rect(x=0, y=0, width=1920, height=1040)
    requested = Rect(x=1600, y=50, width=1500, height=920)
    decision = clamp_window_rect(requested=requested, available=available)
    assert decision.clamped is True
    assert decision.resolved.right <= available.right
    assert decision.resolved.bottom <= available.bottom


def test_splitter_normalization_respects_minimums() -> None:
    normalized = normalize_splitter_sizes(total=1600, requested=(300, 1200, 400), minimums=(220, 760, 260))
    assert sum(normalized) == 1600
    assert normalized[0] >= 220
    assert normalized[1] >= 760
    assert normalized[2] >= 260


def test_workspace_graph_presentations_are_workspace_aware() -> None:
    assert default_graph_presentation_for_workspace('operate') == 'primary'
    assert default_graph_presentation_for_workspace('logic_designer') == 'compact_pip'
    assert default_graph_presentation_for_workspace('session_review') == 'primary'
    assert default_graph_presentation_for_workspace('system') == 'compact_pip'


def test_pip_rect_is_clamped_inside_bounds() -> None:
    bounds = Rect(x=220, y=90, width=1200, height=800)
    decision = clamp_pip_rect(requested=Rect(x=1500, y=850, width=500, height=320), bounds=bounds)
    assert decision.clamped is True
    assert decision.resolved.right <= bounds.right - 12
    assert decision.resolved.bottom <= bounds.bottom - 12


def test_default_pip_rect_positions_compact_and_primary_views_inside_bounds() -> None:
    bounds = Rect(x=0, y=0, width=1400, height=900)
    compact = default_pip_rect(bounds=bounds, mode='compact_pip')
    primary = default_pip_rect(bounds=bounds, mode='primary')
    assert compact.right <= bounds.right
    assert compact.bottom <= bounds.bottom
    assert primary.right <= bounds.right
    assert primary.bottom <= bounds.bottom
    assert primary.width > compact.width
    assert primary.height > compact.height
