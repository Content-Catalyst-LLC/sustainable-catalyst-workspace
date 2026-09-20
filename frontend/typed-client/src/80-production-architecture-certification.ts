/* Workspace v3.0.0 — Production Architecture Certification browser boundary. */
const SCWorkspaceProductionArchitectureBoundary=Object.freeze({
  schema:'sc-workspace-production-architecture-certification-client/1.0',
  version:'3.0.0',
  backendAuthoritative:true,
  browserCanSelfCertify:false,
  architectureCertification:'backend-profile-and-release-gates',
  liveProductionCertification:'manual-field-checks-required',
  migrationRequired:false,
  migrationLineage:'031_backend_policy_identity_authorization_consolidation.sql',
  rollbackBaseline:'2.36.0',
  arbitraryCodeExecution:false
});
(window as unknown as {SCWorkspaceProductionArchitectureBoundary?:typeof SCWorkspaceProductionArchitectureBoundary}).SCWorkspaceProductionArchitectureBoundary=SCWorkspaceProductionArchitectureBoundary;
