(function (global) {
  "use strict";
  const feature = Object.freeze({
    schema: "sc-workspace-agentic-research-workflow-client/1.0",
    version: "3.60.0",
    title: "Agentic Research Workflow Runtime",
    runtimeProfileEndpoint: "/v1/agentic-research-workflow-runtime",
    runtimeOperationsEndpoint: "/v1/agentic-research-workflow-runtime/operations",
    runtimeExecuteEndpoint: "/v1/agentic-research-workflow-runtime/execute",
    boundedOperationsOnly: true,
    humanReviewSupported: true,
    automaticClaimPromotionEnabled: false,
    automaticEvidenceMutationEnabled: false,
    automaticModelApprovalEnabled: false,
    automaticExternalSideEffectsEnabled: false,
    arbitraryCodeExecution: false,
    provenancePreserved: true
  });
  global.SustainableCatalystWorkspaceAgenticResearchWorkflowV3600 = feature;
})(typeof window !== "undefined" ? window : globalThis);
