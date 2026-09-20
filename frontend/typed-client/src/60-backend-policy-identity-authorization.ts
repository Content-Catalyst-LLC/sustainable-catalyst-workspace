/* Workspace v2.36.0 — Backend Policy, Identity & Authorization Consolidation. */
const SCWorkspaceAuthorizationRuntime=Object.freeze({
  schema:'sc-workspace-backend-authorization-client/1.0',
  version:'2.36.0',
  backendAuthoritative:true,
  browserAuthoritativeAuthorization:false,
  serverResolvedPrincipal:true,
  defaultEffect:'deny',
  routePolicyEnforcement:true,
  durableDecisionReceipts:true,
  clientSuppliedRolesTrusted:false,
  clientSuppliedScopesTrusted:false
});
(window as unknown as {SCWorkspaceAuthorization?:typeof SCWorkspaceAuthorizationRuntime}).SCWorkspaceAuthorization=SCWorkspaceAuthorizationRuntime;
