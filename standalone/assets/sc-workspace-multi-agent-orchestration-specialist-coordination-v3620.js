(function (global) {
  "use strict";
  const VERSION = "3.62.0";
  const schema = "sc-workspace-multi-agent-orchestration-specialist-coordination-runtime/1.0";
  const roles = [
    "research_evidence",
    "data_quantitative_analysis",
    "modeling_forecasting",
    "scientific_computing",
    "linguistics_corpus",
    "investigation_provenance",
    "visualization",
    "synthesis"
  ];
  const boundaries = Object.freeze({
    coordinatorApprovalAuthorityEnabled: false,
    specialistApprovalAuthorityEnabled: false,
    automaticGovernanceBypassEnabled: false,
    automaticExternalSideEffectsEnabled: false,
    arbitraryCodeExecution: false,
    automaticTruthDeterminationEnabled: false,
    automaticEvidenceRankingEnabled: false,
    dissentPreserved: true,
    provenancePreserved: true
  });
  global.SCWorkspaceMultiAgentOrchestrationV3620 = Object.freeze({
    version: VERSION,
    schema: schema,
    specialistRoleFamilies: Object.freeze(roles.slice()),
    boundaries: boundaries,
    endpoint: "/v1/multi-agent-orchestration-specialist-coordination-runtime",
    operationsEndpoint: "/v1/multi-agent-orchestration-specialist-coordination-runtime/operations",
    executeEndpoint: "/v1/multi-agent-orchestration-specialist-coordination-runtime/execute",
    upstream: Object.freeze({
      agentic: "sc-workspace-agentic-research-workflow-runtime/1.0",
      governance: "sc-workspace-human-governance-approval-intervention-runtime/1.0"
    })
  });
})(typeof globalThis !== "undefined" ? globalThis : window);
