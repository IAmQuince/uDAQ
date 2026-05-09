from __future__ import annotations

import pytest

from universaldaq.ui.workspace_design import default_workspace_task_maps, workspace_task_map_by_id

TEST_DECLARATION = {
    'test_id': 'UDQ-TST-CON-066',
    'verifies_requirements': ['UDQ-REQ-UI-001', 'UDQ-REQ-UI-004'],
    'checks_invariants': ['UDQ-INV-STATE-003'],
    'worked_example_reference': None,
    'expected_proof_output': 'workspace task maps preserve one primary task surface, persistent status set, and task-appropriate graph defaults',
}
pytestmark = pytest.mark.contract


def test_workspace_task_maps_cover_primary_surface_and_status() -> None:
    maps = default_workspace_task_maps()
    assert {item.workspace_id for item in maps} == {'operate', 'logic_designer', 'system', 'session_review'}
    for item in maps:
        assert item.primary_goal
        assert item.primary_surface
        assert item.graph_mode_default in {'primary', 'compact_pip'}
        assert item.persistent_status


def test_logic_and_system_task_maps_use_secondary_graph_defaults() -> None:
    lookup = workspace_task_map_by_id()
    assert lookup['logic_designer'].graph_mode_default == 'compact_pip'
    assert lookup['system'].graph_mode_default == 'compact_pip'
    assert 'graph mode' in lookup['logic_designer'].persistent_status
    assert 'limited-access reason' in lookup['system'].persistent_status
