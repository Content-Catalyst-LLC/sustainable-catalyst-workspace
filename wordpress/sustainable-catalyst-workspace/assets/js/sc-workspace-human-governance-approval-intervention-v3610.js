(function (global) {
  "use strict";
  const feature = Object.freeze({
    schema: "sc-workspace-human-governance-approval-intervention-client/1.0",
    version: "3.61.0",
    title: "Human Governance, Approval & Intervention Runtime",
    runtimeProfileEndpoint: "/v1/human-governance-approval-intervention-runtime",
    runtimeOperationsEndpoint: "/v1/human-governance-approval-intervention-runtime/operations",
    runtimeExecuteEndpoint: "/v1/human-governance-approval-intervention-runtime/execute",
    boundedOperationsOnly: true,
    humanAuthorityRequired: true,
    automaticApprovalEnabled: false,
    agentApprovalAuthorityEnabled: false,
    selfApprovalEnabled: false,
    approvalBypassEnabled: false,
    automaticResumeEnabled: false,
    arbitraryCodeExecution: false,
    decisionImmutability: true,
    provenancePreserved: true
  });
  global.SustainableCatalystWorkspaceHumanGovernanceApprovalInterventionV3610 = feature;
})(typeof window !== "undefined" ? window : globalThis);
