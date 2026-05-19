from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RegistryPaths:
    requirement_json: str = 'registries/active/universalDAQ_requirement_registry_r9.json'
    requirement_csv: str = 'registries/active/universalDAQ_requirement_registry_r9.csv'
    invariant_json: str = 'registries/active/universalDAQ_invariant_registry_r2.json'
    invariant_csv: str = 'registries/active/universalDAQ_invariant_registry_r2.csv'
    readme_json: str = 'registries/active/universalDAQ_readme_registry_r0.json'
    readme_csv: str = 'registries/active/universalDAQ_readme_registry_r0.csv'
    document_json: str = 'registries/active/universalDAQ_document_registry_r21.json'
    document_csv: str = 'registries/active/universalDAQ_document_registry_r21.csv'
    consistency_json: str = 'registries/active/universalDAQ_consistency_findings_r10.json'
    consistency_csv: str = 'registries/active/universalDAQ_consistency_findings_r10.csv'
    contradiction_json: str = 'registries/active/universalDAQ_contradiction_register_r4.json'
    contradiction_csv: str = 'registries/active/universalDAQ_contradiction_register_r4.csv'
    duplication_json: str = 'registries/active/universalDAQ_duplication_register_r4.json'
    duplication_csv: str = 'registries/active/universalDAQ_duplication_register_r4.csv'
    execution_contract_json: str = 'registries/active/universalDAQ_execution_contract_r2.json'
    execution_contract_csv: str = 'registries/active/universalDAQ_execution_contract_r2.csv'
    governance_model_json: str = 'registries/active/universalDAQ_governance_model_r2.json'
    implementation_coverage_json: str = 'registries/active/universalDAQ_implementation_coverage_matrix_r2.json'
    implementation_coverage_csv: str = 'registries/active/universalDAQ_implementation_coverage_matrix_r2.csv'
    term_usage_json: str = 'registries/active/universalDAQ_term_usage_matrix_r4.json'
    term_usage_csv: str = 'registries/active/universalDAQ_term_usage_matrix_r4.csv'
    test_inventory_json: str = 'registries/active/universalDAQ_test_inventory_r0.json'
    test_inventory_csv: str = 'registries/active/universalDAQ_test_inventory_r0.csv'
    tool_inventory_json: str = 'registries/active/universalDAQ_tool_inventory_r0.json'
    tool_inventory_csv: str = 'registries/active/universalDAQ_tool_inventory_r0.csv'
    cross_reference_edges_csv: str = 'registries/active/universalDAQ_cross_reference_edges_r17.csv'
    decision_log_json: str = 'registries/active/universalDAQ_decision_log_r1.json'
    decision_log_csv: str = 'registries/active/universalDAQ_decision_log_r1.csv'

    def resolve(self, root: Path, attribute_name: str) -> Path:
        return root / getattr(self, attribute_name)


ACTIVE_REGISTRIES = RegistryPaths()


def active_registry_path(root: Path, attribute_name: str) -> Path:
    return ACTIVE_REGISTRIES.resolve(root, attribute_name)
