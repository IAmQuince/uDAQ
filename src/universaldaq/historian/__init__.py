"""Historian evidence-bundle models and services for the bounded save-point baseline."""

from .models import (
    ArtifactDescriptor,
    ArtifactManifest,
    BundleBuildResult,
    BundleIntegrityWarning,
    EvidenceBundle,
    ExportIntent,
    ExportScope,
    ReviewArtifact,
    SerializedArtifact,
)
from .proof_bundle import BundleInventory, ManifestSummary, ProofBundleSummary, build_bundle_inventory, summarize_bundle, summarize_manifest
from .services import EvidenceBundleService

MODULE_DECLARATION = {
    'module_id': 'UDQ-CODE-PKG-HISTORIAN',
    'implements_requirements': [
        'UDQ-REQ-HIS-001',
        'UDQ-REQ-HIS-002',
        'UDQ-REQ-EXP-001',
        'UDQ-REQ-EXP-002',
        'UDQ-REQ-SEC-002',
    ],
    'governed_by': [
        'UDQ-HIS-SPEC-001',
        'UDQ-EXP-SPEC-001',
        'UDQ-SEC-SPEC-001',
        'UDQ-IMP-MAP-001',
        'UDQ-IMP-GUIDE-001',
    ],
    'subsystem': 'Historian',
    'invariant_hooks': [
        'UDQ-INV-EVID-002',
        'UDQ-INV-EVID-004',
    ],
    'proof_scope': 'review/export evidence bundle scaffolding, manifest-backed assembly, authorization-aware export outcomes, review artifacts, and bounded service-level serialization',
}

__all__ = [
    'ArtifactDescriptor',
    'ArtifactManifest',
    'BundleBuildResult',
    'BundleIntegrityWarning',
    'BundleInventory',
    'EvidenceBundle',
    'EvidenceBundleService',
    'ExportIntent',
    'ExportScope',
    'MODULE_DECLARATION',
    'ManifestSummary',
    'ProofBundleSummary',
    'ReviewArtifact',
    'SerializedArtifact',
    'build_bundle_inventory',
    'summarize_bundle',
    'summarize_manifest',
]
