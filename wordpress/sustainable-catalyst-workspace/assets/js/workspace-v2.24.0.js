/* Workspace v2.23.0 — Reliability, Survival & Failure-Time Analysis */
window.SCWorkspaceReliabilityAnalysis={version:'2.23.0',bounded:true,operations:8};


/* Workspace v2.24.0: thin-client backend-authority contract. */
window.SCWorkspaceBackendAuthority = Object.freeze({
  schema: 'sc-workspace-domain-authority-client/1.0',
  workspaceVersion: '2.24.0',
  canonicalState: 'backend',
  canonicalStore: 'postgresql',
  clientRole: 'presentation-interaction-local-drafts',
  browserAuthoritativeState: false,
  profileEndpoint: '/v1/domain-authority',
  validationEndpoint: '/v1/domain-authority/validate',
  mutationReceiptsEndpoint: '/v1/domain-mutation-receipts'
});
