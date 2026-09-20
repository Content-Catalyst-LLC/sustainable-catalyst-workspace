/* Workspace v2.36.0 typed browser client. Service credentials remain server-side in WordPress. */
interface WorkspaceTypedClientConfig { baseUrl:string; nonce?:string; authenticated?:boolean; }
interface WorkspaceClientRequestOptions { method?:'GET'|'POST'|'DELETE'; body?:unknown; }
class WorkspaceTypedApiError extends Error { readonly status:number; readonly payload:unknown; constructor(status:number,message:string,payload:unknown){super(message);this.name='WorkspaceTypedApiError';this.status=status;this.payload=payload;} }
class WorkspaceTypedApiClient {
  readonly config:WorkspaceTypedClientConfig;
  constructor(config:WorkspaceTypedClientConfig){this.config={...config,baseUrl:String(config.baseUrl||'').replace(/\/$/,'')};}
  private async request<T extends WorkspaceApiEnvelope>(path:string,options:WorkspaceClientRequestOptions={}):Promise<T>{
    const headers:Record<string,string>={'Accept':'application/json'}; if(this.config.nonce) headers['X-WP-Nonce']=this.config.nonce; if(options.body!==undefined) headers['Content-Type']='application/json';
    const response=await fetch(this.config.baseUrl+path,{method:options.method||'GET',credentials:'same-origin',headers,body:options.body===undefined?undefined:JSON.stringify(options.body)});
    let payload:unknown=null; try{payload=await response.json();}catch(_){payload=null;} if(!response.ok){const message=payload&&typeof payload==='object'&&'message' in payload?String((payload as {message?:unknown}).message||'Workspace API request failed'):'Workspace API request failed';throw new WorkspaceTypedApiError(response.status,message,payload);} if(!payload||typeof payload!=='object') throw new WorkspaceTypedApiError(502,'Workspace API returned a non-object envelope',payload); return payload as T;
  }
  authorizationProfile():Promise<WorkspaceApiEnvelope>{return this.request('/authorization');}
  authorizationIdentity():Promise<WorkspaceApiEnvelope>{return this.request('/authorization/identity');}
  evaluateAuthorization(request:WorkspaceAuthorizationEvaluateRequest):Promise<WorkspaceApiEnvelope>{return this.request('/authorization/evaluate',{method:'POST',body:request});}
  authorizationDecisions():Promise<WorkspaceApiEnvelope>{return this.request('/authorization/decisions');}
  frontendRuntime():Promise<WorkspaceApiEnvelope>{return this.request('/frontend-runtime');}
  productionCertification():Promise<WorkspaceApiEnvelope>{return this.request('/production-certification');}
  clientContracts():Promise<WorkspaceApiEnvelope>{return this.request('/client-contracts');}
  thinClientStateProfile():Promise<WorkspaceApiEnvelope>{return this.request('/thin-client-state');}
  thinClientBootstrap(projectId?:string):Promise<WorkspaceApiEnvelope>{const q=projectId?'?projectId='+encodeURIComponent(projectId):'';return this.request('/thin-client-state/bootstrap'+q);}
  syncProfile():Promise<WorkspaceApiEnvelope>{return this.request('/sync');}
  syncBootstrap():Promise<WorkspaceApiEnvelope>{return this.request('/sync/bootstrap');}
  syncEnvelope(request:WorkspaceSyncEnvelope):Promise<WorkspaceApiEnvelope>{return this.request('/sync/envelopes',{method:'POST',body:request});}
  syncReconcile(request:WorkspaceSyncReconcileRequest):Promise<WorkspaceApiEnvelope>{return this.request('/sync/reconcile',{method:'POST',body:request});}
  syncReceipts():Promise<WorkspaceApiEnvelope>{return this.request('/sync/receipts');}
  scientificObjectProfile():Promise<WorkspaceApiEnvelope>{return this.request('/scientific-objects/profile');}
  scientificObjects(kind?:WorkspaceScientificObjectKind,projectId?:string,q?:string,limit=100):Promise<WorkspaceApiEnvelope>{const params=new URLSearchParams();if(kind)params.set('kind',kind);if(projectId)params.set('projectId',projectId);if(q)params.set('q',q);params.set('limit',String(limit));return this.request('/scientific-objects?'+params.toString());}
  scientificObject(kind:WorkspaceScientificObjectKind,objectId:string):Promise<WorkspaceApiEnvelope>{return this.request('/scientific-objects/'+encodeURIComponent(kind)+'/'+encodeURIComponent(objectId));}
  scientificObjectHistory(kind:WorkspaceScientificObjectKind,objectId:string,limit=100):Promise<WorkspaceApiEnvelope>{return this.request('/scientific-objects/'+encodeURIComponent(kind)+'/'+encodeURIComponent(objectId)+'/revisions?limit='+encodeURIComponent(String(limit)));}
  scientificObjectRelations(kind:WorkspaceScientificObjectKind,objectId:string):Promise<WorkspaceApiEnvelope>{return this.request('/scientific-objects/'+encodeURIComponent(kind)+'/'+encodeURIComponent(objectId)+'/relations');}
  handoffProfile():Promise<WorkspaceApiEnvelope>{return this.request('/handoffs/profile');}
  createHandoff(request:WorkspaceResearchHandoffRequest):Promise<WorkspaceApiEnvelope>{return this.request('/handoffs',{method:'POST',body:request});}
  handoff(handoffId:string):Promise<WorkspaceApiEnvelope>{return this.request('/handoffs/'+encodeURIComponent(handoffId));}
  acceptHandoff(handoffId:string,request:WorkspaceResearchHandoffAcceptRequest):Promise<WorkspaceApiEnvelope>{return this.request('/handoffs/'+encodeURIComponent(handoffId)+'/accept',{method:'POST',body:request});}
  handoffReceipts():Promise<WorkspaceApiEnvelope>{return this.request('/handoff-receipts');}
  domainAuthority():Promise<WorkspaceApiEnvelope>{return this.request('/domain-authority');}
  commandQueryProfile():Promise<WorkspaceApiEnvelope>{return this.request('/command-query');}
  executeCommand<C extends WorkspaceCommand>(request:WorkspaceCommandRequest&{command:C}):Promise<WorkspaceApiEnvelope>{return this.request('/commands/execute',{method:'POST',body:request});}
  executeQuery<Q extends WorkspaceQuery>(request:WorkspaceQueryRequest&{query:Q}):Promise<WorkspaceApiEnvelope>{return this.request('/queries/execute',{method:'POST',body:request});}
  workspaceOverview():Promise<WorkspaceApiEnvelope>{return this.request('/read-models/workspace-overview');}
  notebookOrchestration():Promise<WorkspaceApiEnvelope>{return this.request('/notebook-orchestration');}
  createNotebookPlan(request:NotebookExecutionPlanRequest):Promise<WorkspaceApiEnvelope>{return this.request('/notebook-execution-plans',{method:'POST',body:request});}
  studyPackageProfile():Promise<WorkspaceApiEnvelope>{return this.request('/scientific-study-packages/profile');}
  createStudyPackage(request:ScientificStudyPackageRequest):Promise<WorkspaceApiEnvelope>{return this.request('/scientific-study-packages',{method:'POST',body:request});}
  visualizationProfile():Promise<WorkspaceApiEnvelope>{return this.request('/visualization-specs/profile');}
  storeVisualization(request:VisualizationSpecRequest):Promise<WorkspaceApiEnvelope>{return this.request('/visualization-specs',{method:'POST',body:request});}
  visualizationReceipts():Promise<WorkspaceApiEnvelope>{return this.request('/visualization-spec-receipts');}
}
const SCWorkspaceTypedClientRuntime=Object.freeze({schema:'sc-workspace-typed-client-runtime/1.0',version:SCW_TYPED_CONTRACT_VERSION,contractSchema:SCW_TYPED_CONTRACT_SCHEMA,openApiProjectionSha256:SCW_OPENAPI_PROJECTION_SHA256,endpoints:SCW_TYPED_ENDPOINTS,backendAuthoritative:true,browserAuthoritativeState:false,browserDirectBackendAccess:false,serviceCredentialsBrowserVisible:false,strictTypeScript:true,createClient(config:WorkspaceTypedClientConfig):WorkspaceTypedApiClient{return new WorkspaceTypedApiClient(config);}});
const scwGlobal=window as unknown as {SCWorkspaceTypedClient?:typeof SCWorkspaceTypedClientRuntime;SCWorkspaceTypedClientConfig?:WorkspaceTypedClientConfig;SCWorkspaceApi?:WorkspaceTypedApiClient;};
scwGlobal.SCWorkspaceTypedClient=SCWorkspaceTypedClientRuntime; if(scwGlobal.SCWorkspaceTypedClientConfig&&scwGlobal.SCWorkspaceTypedClientConfig.baseUrl){scwGlobal.SCWorkspaceApi=SCWorkspaceTypedClientRuntime.createClient(scwGlobal.SCWorkspaceTypedClientConfig);}
