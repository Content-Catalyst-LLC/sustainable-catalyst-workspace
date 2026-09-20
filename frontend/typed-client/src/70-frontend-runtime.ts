/* Workspace v3.0.0 — Frontend Logic Reduction & Legacy JS Retirement. */
const SCWorkspaceFrontendBoundary=Object.freeze({
  schema:'sc-workspace-frontend-runtime-client/1.0',
  version:'3.0.0',
  backendAuthoritative:true,
  browserAuthoritativeState:false,
  browserAuthoritativeAuthorization:false,
  primaryResponsibilities:Object.freeze(['presentation','interaction-routing','transient-ui-state','explicit-local-draft-outbox']),
  canonicalReads:'server-read-models',
  canonicalWrites:'bounded-backend-commands',
  legacyLocalCompatibility:true,
  legacyCompatibilityMode:'lazy-browser-local-only',
  legacyCompatibilityAuthoritative:false,
  historicalVersionedFrontendAssetsRetired:true,
  packageAssetNamesVersionDerived:true
});
(window as unknown as {SCWorkspaceFrontendBoundary?:typeof SCWorkspaceFrontendBoundary}).SCWorkspaceFrontendBoundary=SCWorkspaceFrontendBoundary;
