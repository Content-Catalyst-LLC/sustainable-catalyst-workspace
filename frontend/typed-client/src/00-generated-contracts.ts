export const SCW_TYPED_CONTRACT_VERSION = '3.12.0';
export const SCW_TYPED_ENDPOINTS = {
  "spatialEvidenceWorkspace": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace"
  },
  "spatialObservationStore": {
    "method": "POST",
    "path": "/v1/spatial-evidence-workspace/observations"
  },
  "spatialObservations": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/observations"
  },
  "spatialObservation": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/observations/{observation_id}"
  },
  "spatialObservationRevisions": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/observations/{observation_id}/revisions"
  },
  "spatialContextLinkCreate": {
    "method": "POST",
    "path": "/v1/spatial-evidence-workspace/context-links"
  },
  "spatialContextLinks": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/context-links"
  },
  "spatialRelationCreate": {
    "method": "POST",
    "path": "/v1/spatial-evidence-workspace/relations"
  },
  "spatialRelations": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/relations"
  },
  "spatialMapProjection": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/projects/{project_id}/map"
  },
  "spatialGraph": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/projects/{project_id}/graph"
  },
  "spatialDiagnostics": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/projects/{project_id}/diagnostics"
  },
  "spatialSnapshotCreate": {
    "method": "POST",
    "path": "/v1/spatial-evidence-workspace/projects/{project_id}/snapshots"
  },
  "spatialSnapshots": {
    "method": "GET",
    "path": "/v1/spatial-evidence-workspace/projects/{project_id}/snapshots"
  },
  "documentaryEvidenceWorkspace": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace"
  },
  "documentStore": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/documents"
  },
  "documents": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/documents"
  },
  "document": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/documents/{document_id}"
  },
  "documentRevisions": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/documents/{document_id}/revisions"
  },
  "documentExcerptCreate": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/excerpts"
  },
  "documentExcerpts": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/excerpts"
  },
  "testimonyStore": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/testimonies"
  },
  "testimonies": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/testimonies"
  },
  "testimony": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/testimonies/{testimony_id}"
  },
  "testimonyRevisions": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/testimonies/{testimony_id}/revisions"
  },
  "documentaryContextLinkCreate": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/context-links"
  },
  "documentaryContextLinks": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/context-links"
  },
  "testimonyRelationCreate": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/testimony-relations"
  },
  "testimonyRelations": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/testimony-relations"
  },
  "documentaryGraph": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/projects/{project_id}/graph"
  },
  "documentaryAnalysis": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/projects/{project_id}/analysis"
  },
  "documentarySnapshotCreate": {
    "method": "POST",
    "path": "/v1/documentary-evidence-workspace/projects/{project_id}/snapshots"
  },
  "documentarySnapshots": {
    "method": "GET",
    "path": "/v1/documentary-evidence-workspace/projects/{project_id}/snapshots"
  },
  "entityResolutionWorkspace": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace"
  },
  "entityStore": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/entities"
  },
  "entities": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/entities"
  },
  "entity": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/entities/{entity_id}"
  },
  "entityRevisions": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/entities/{entity_id}/revisions"
  },
  "entityAliasCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/aliases"
  },
  "entityAliases": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/aliases"
  },
  "entityIdentifierCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/identifiers"
  },
  "entityIdentifiers": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/identifiers"
  },
  "entityRelationshipCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/relationships"
  },
  "entityRelationships": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/relationships"
  },
  "entityContextLinkCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/context-links"
  },
  "entityContextLinks": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/context-links"
  },
  "entityMatchCandidateCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/match-candidates"
  },
  "entityMatchCandidates": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/match-candidates"
  },
  "entityMatchCandidateReview": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/match-candidates/{candidate_id}/review"
  },
  "entityResolutionGraph": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/projects/{project_id}/graph"
  },
  "entityResolutionDiagnostics": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/projects/{project_id}/diagnostics"
  },
  "entityResolutionSnapshotCreate": {
    "method": "POST",
    "path": "/v1/entity-resolution-workspace/projects/{project_id}/snapshots"
  },
  "entityResolutionSnapshots": {
    "method": "GET",
    "path": "/v1/entity-resolution-workspace/projects/{project_id}/snapshots"
  },
  "investigationTimelineWorkspace": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace"
  },
  "investigationEventStore": {
    "method": "POST",
    "path": "/v1/investigation-timeline-workspace/events"
  },
  "investigationEvents": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/events"
  },
  "investigationEvent": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/events/{event_id}"
  },
  "investigationEventRevisions": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/events/{event_id}/revisions"
  },
  "investigationEventStatementLinkCreate": {
    "method": "POST",
    "path": "/v1/investigation-timeline-workspace/event-statement-links"
  },
  "investigationEventStatementLinks": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/event-statement-links"
  },
  "investigationEventRelationCreate": {
    "method": "POST",
    "path": "/v1/investigation-timeline-workspace/event-relations"
  },
  "investigationEventRelations": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/event-relations"
  },
  "investigationTimeline": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/projects/{project_id}/timeline"
  },
  "investigationReconstructionGraph": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/projects/{project_id}/reconstruction-graph"
  },
  "investigationTemporalDiagnostics": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/projects/{project_id}/temporal-diagnostics"
  },
  "investigationTimelineSnapshotCreate": {
    "method": "POST",
    "path": "/v1/investigation-timeline-workspace/projects/{project_id}/snapshots"
  },
  "investigationTimelineSnapshots": {
    "method": "GET",
    "path": "/v1/investigation-timeline-workspace/projects/{project_id}/snapshots"
  },
  "investigationGraphWorkspace": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace"
  },
  "investigationHypothesisSetStore": {
    "method": "POST",
    "path": "/v1/investigation-graph-workspace/hypothesis-sets"
  },
  "investigationHypothesisSets": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/hypothesis-sets"
  },
  "investigationHypothesisSet": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/hypothesis-sets/{hypothesis_set_id}"
  },
  "investigationGraph": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/graph"
  },
  "investigationContradictions": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/contradictions"
  },
  "investigationHypothesisMatrix": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/hypothesis-matrix"
  },
  "investigationCoverage": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/coverage"
  },
  "investigationGraphSnapshotCreate": {
    "method": "POST",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/snapshots"
  },
  "investigationGraphSnapshots": {
    "method": "GET",
    "path": "/v1/investigation-graph-workspace/projects/{project_id}/snapshots"
  },
  "investigativeResearchWorkspace": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace"
  },
  "investigationStatementStore": {
    "method": "POST",
    "path": "/v1/investigative-research-workspace/statements"
  },
  "investigationStatements": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/statements"
  },
  "investigationStatement": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/statements/{statement_id}"
  },
  "investigationStatementRevisions": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/statements/{statement_id}/revisions"
  },
  "investigationEvidenceLinkCreate": {
    "method": "POST",
    "path": "/v1/investigative-research-workspace/evidence-links"
  },
  "investigationEvidenceLinks": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/evidence-links"
  },
  "investigationStatementRelationCreate": {
    "method": "POST",
    "path": "/v1/investigative-research-workspace/statement-relations"
  },
  "investigationStatementRelations": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/statement-relations"
  },
  "investigativeResearchProject": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/projects/{project_id}"
  },
  "investigativeResearchSnapshotCreate": {
    "method": "POST",
    "path": "/v1/investigative-research-workspace/projects/{project_id}/snapshots"
  },
  "investigativeResearchSnapshots": {
    "method": "GET",
    "path": "/v1/investigative-research-workspace/projects/{project_id}/snapshots"
  },
  "visualResearchWorkspace": {
    "method": "GET",
    "path": "/v1/visual-research-workspace"
  },
  "visualResearchProject": {
    "method": "GET",
    "path": "/v1/visual-research-workspace/projects/{project_id}"
  },
  "visualResearchVisualization": {
    "method": "GET",
    "path": "/v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}"
  },
  "visualResearchVisualizationBind": {
    "method": "POST",
    "path": "/v1/visual-research-workspace/projects/{project_id}/visualizations/{visualization_id}/bind"
  },
  "visualResearchSnapshotCreate": {
    "method": "POST",
    "path": "/v1/visual-research-workspace/projects/{project_id}/snapshots"
  },
  "visualResearchSnapshots": {
    "method": "GET",
    "path": "/v1/visual-research-workspace/projects/{project_id}/snapshots"
  },
  "analyticsRProvider": {
    "method": "GET",
    "path": "/v1/analytics/providers/catalystanalyticsr"
  },
  "analyticsRProviderValidate": {
    "method": "POST",
    "path": "/v1/analytics/providers/catalystanalyticsr/validate"
  },
  "analyticsRProviderExecute": {
    "method": "POST",
    "path": "/v1/analytics/providers/catalystanalyticsr/execute"
  },
  "analyticsProviderReceipts": {
    "method": "GET",
    "path": "/v1/analytics/provider-receipts"
  },
  "analyticsProviderReceipt": {
    "method": "GET",
    "path": "/v1/analytics/provider-receipts/{receipt_id}"
  },
  "executionProvenance": {
    "method": "GET",
    "path": "/v1/execution-provenance"
  },
  "executionProvenanceProject": {
    "method": "GET",
    "path": "/v1/execution-provenance/projects/{project_id}"
  },
  "executionProvenanceRun": {
    "method": "GET",
    "path": "/v1/execution-provenance/projects/{project_id}/runs/{run_id}"
  },
  "executionProvenanceSnapshotCreate": {
    "method": "POST",
    "path": "/v1/execution-provenance/projects/{project_id}/snapshots"
  },
  "executionProvenanceSnapshots": {
    "method": "GET",
    "path": "/v1/execution-provenance/projects/{project_id}/snapshots"
  },
  "researchSessionBindings": {
    "method": "GET",
    "path": "/v1/research-bindings"
  },
  "researchSessionProjectBindings": {
    "method": "GET",
    "path": "/v1/research-bindings/projects/{project_id}"
  },
  "researchSessionBindingCreate": {
    "method": "POST",
    "path": "/v1/research-bindings/projects/{project_id}"
  },
  "researchSessionBindingsReconcile": {
    "method": "POST",
    "path": "/v1/research-bindings/projects/{project_id}/reconcile"
  },
  "unifiedResearchContext": {
    "method": "GET",
    "path": "/v1/research-context"
  },
  "unifiedResearchProjectContext": {
    "method": "GET",
    "path": "/v1/research-context/projects/{project_id}"
  },
  "unifiedResearchContextSnapshotCreate": {
    "method": "POST",
    "path": "/v1/research-context/projects/{project_id}/snapshots"
  },
  "unifiedResearchContextSnapshots": {
    "method": "GET",
    "path": "/v1/research-context/projects/{project_id}/snapshots"
  },
  "platformCoreRuntime": {
    "method": "GET",
    "path": "/v1/platform-core-runtime"
  },
  "platformCoreRuntimeReadiness": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/readiness"
  },
  "platformCoreSessionCreate": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/sessions"
  },
  "platformCoreProjectContext": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/projects/{project_id}"
  },
  "platformCoreObjectBind": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/object-bindings"
  },
  "platformCoreExecutionBind": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/execution-bindings"
  },
  "platformCoreVisualBind": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/visual-bindings"
  },
  "platformCorePackageBind": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/package-bindings"
  },
  "platformCoreHandoffBind": {
    "method": "POST",
    "path": "/v1/platform-core-runtime/handoff-bindings"
  },
  "platformCoreSessionSummary": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/sessions/{session_id}/summary"
  },
  "platformCoreSessionLineage": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/sessions/{session_id}/lineage"
  },
  "platformCoreSessionBundle": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/sessions/{session_id}/bundle"
  },
  "platformCoreRuntimeReceipts": {
    "method": "GET",
    "path": "/v1/platform-core-runtime/receipts"
  },
  "backendNativeWorkspace": {
    "method": "GET",
    "path": "/v1/backend-native-workspace"
  },
  "backendNativeBootstrap": {
    "method": "GET",
    "path": "/v1/backend-native-workspace/bootstrap"
  },
  "frontendRuntime": {
    "method": "GET",
    "path": "/v1/frontend-runtime"
  },
  "productionCertification": {
    "method": "GET",
    "path": "/v1/production-certification"
  },
  "authorizationProfile": {
    "method": "GET",
    "path": "/v1/authorization"
  },
  "authorizationIdentity": {
    "method": "GET",
    "path": "/v1/authorization/identity"
  },
  "authorizationEvaluate": {
    "method": "POST",
    "path": "/v1/authorization/evaluate"
  },
  "authorizationDecisions": {
    "method": "GET",
    "path": "/v1/authorization/decisions"
  },
  "clientContracts": {
    "method": "GET",
    "path": "/v1/client-contracts"
  },
  "thinClientState": {
    "method": "GET",
    "path": "/v1/thin-client-state"
  },
  "thinClientBootstrap": {
    "method": "GET",
    "path": "/v1/thin-client-state/bootstrap"
  },
  "syncProfile": {
    "method": "GET",
    "path": "/v1/sync"
  },
  "syncBootstrap": {
    "method": "GET",
    "path": "/v1/sync/bootstrap"
  },
  "syncEnvelope": {
    "method": "POST",
    "path": "/v1/sync/envelopes"
  },
  "syncReconcile": {
    "method": "POST",
    "path": "/v1/sync/reconcile"
  },
  "syncReceipts": {
    "method": "GET",
    "path": "/v1/sync/receipts"
  },
  "scientificObjectProfile": {
    "method": "GET",
    "path": "/v1/scientific-objects/profile"
  },
  "scientificObjects": {
    "method": "GET",
    "path": "/v1/scientific-objects"
  },
  "scientificObjectGet": {
    "method": "GET",
    "path": "/v1/scientific-objects/{kind}/{object_id}"
  },
  "scientificObjectHistory": {
    "method": "GET",
    "path": "/v1/scientific-objects/{kind}/{object_id}/revisions"
  },
  "scientificObjectRelations": {
    "method": "GET",
    "path": "/v1/scientific-objects/{kind}/{object_id}/relations"
  },
  "handoffProfile": {
    "method": "GET",
    "path": "/v1/handoffs/profile"
  },
  "handoffCreate": {
    "method": "POST",
    "path": "/v1/handoffs"
  },
  "handoffGet": {
    "method": "GET",
    "path": "/v1/handoffs/{handoff_id}"
  },
  "handoffAccept": {
    "method": "POST",
    "path": "/v1/handoffs/{handoff_id}/accept"
  },
  "handoffReceipts": {
    "method": "GET",
    "path": "/v1/handoff-receipts"
  },
  "domainAuthority": {
    "method": "GET",
    "path": "/v1/domain-authority"
  },
  "commandQuery": {
    "method": "GET",
    "path": "/v1/command-query"
  },
  "executeCommand": {
    "method": "POST",
    "path": "/v1/commands/execute"
  },
  "executeQuery": {
    "method": "POST",
    "path": "/v1/queries/execute"
  },
  "workspaceOverview": {
    "method": "GET",
    "path": "/v1/read-models/workspace-overview"
  },
  "notebookOrchestration": {
    "method": "GET",
    "path": "/v1/notebook-orchestration"
  },
  "notebookPlans": {
    "method": "POST",
    "path": "/v1/notebook-execution-plans"
  },
  "studyPackageProfile": {
    "method": "GET",
    "path": "/v1/scientific-study-packages/profile"
  },
  "studyPackages": {
    "method": "POST",
    "path": "/v1/scientific-study-packages"
  },
  "visualizationProfile": {
    "method": "GET",
    "path": "/v1/visualization-specs/profile"
  },
  "visualizationSpecs": {
    "method": "POST",
    "path": "/v1/visualization-specs"
  },
  "visualizationReceipts": {
    "method": "GET",
    "path": "/v1/visualization-spec-receipts"
  }
} as const;
export type SCWTypedEndpointKey = keyof typeof SCW_TYPED_ENDPOINTS;
