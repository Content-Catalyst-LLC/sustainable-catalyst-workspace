/* Workspace v3.1.0 — Backend-Native Scientific Workspace browser boundary. */
const SCWorkspaceBackendNativeScientificWorkspace=Object.freeze({
  schema:'sc-workspace-backend-native-scientific-workspace-client/1.0',
  version:'3.1.0',
  backendNative:true,
  backendAuthoritative:true,
  browserAuthoritativeState:false,
  browserAuthoritativeAuthorization:false,
  signedInLocalCanonicalFallback:false,
  canonicalStore:'postgresql',
  canonicalDomainRuntime:'python',
  canonicalClientCachePersistent:false,
  scientificExecutionAuthority:'bounded-internal-runtime-services',
  runtimeArbitraryCodeExecution:false,
  transport:'wordpress-server-proxy',
  bootstrap:'/backend-native-workspace/bootstrap'
});
(window as unknown as {SCWorkspaceBackendNativeScientificWorkspace?:typeof SCWorkspaceBackendNativeScientificWorkspace}).SCWorkspaceBackendNativeScientificWorkspace=SCWorkspaceBackendNativeScientificWorkspace;
