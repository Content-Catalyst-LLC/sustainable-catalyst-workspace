/* Workspace v2.30.0 thin-client state runtime. Canonical state is never persisted by this store. */
type WorkspaceTransientKey = 'activeRoute'|'activeProjectId'|'activeNotebookId'|'activeObjectId'|'selection'|'openPanels'|'draftBuffers'|'filters'|'sort'|'viewport'|'density'|'optimisticRequests'|'offlineQueueMetadata';
type WorkspaceTransientState = Partial<Record<WorkspaceTransientKey, unknown>>;
interface ThinClientBootstrapEnvelope extends WorkspaceApiEnvelope { canonical?:unknown; projectionFingerprint?:unknown; clientPolicy?:unknown; }
const SCW_TRANSIENT_KEYS:readonly WorkspaceTransientKey[] = Object.freeze(['activeRoute','activeProjectId','activeNotebookId','activeObjectId','selection','openPanels','draftBuffers','filters','sort','viewport','density','optimisticRequests','offlineQueueMetadata']);
const SCW_TRANSIENT_KEY_SET = new Set<string>(SCW_TRANSIENT_KEYS as readonly string[]);
class WorkspaceThinClientStateStore {
  private readonly api:WorkspaceTypedApiClient;
  private readonly storage:Storage|null;
  private readonly storageKey='sc_workspace_transient_v2300';
  private transient:WorkspaceTransientState={};
  private canonicalCache:Map<string,unknown>=new Map();
  private projectionFingerprint='';
  constructor(api:WorkspaceTypedApiClient,storage:Storage|null=typeof window!=='undefined'?window.localStorage:null){this.api=api;this.storage=storage;this.transient=this.readTransient();}
  private readTransient():WorkspaceTransientState{if(!this.storage)return{};try{const raw=JSON.parse(this.storage.getItem(this.storageKey)||'{}') as Record<string,unknown>;const out:WorkspaceTransientState={};for(const key of SCW_TRANSIENT_KEYS){if(Object.prototype.hasOwnProperty.call(raw,key))out[key]=raw[key];}return out;}catch(_){return{};}}
  private persistTransient():void{if(!this.storage)return;const safe:WorkspaceTransientState={};for(const key of SCW_TRANSIENT_KEYS){if(Object.prototype.hasOwnProperty.call(this.transient,key))safe[key]=this.transient[key];}this.storage.setItem(this.storageKey,JSON.stringify(safe));}
  setTransient(key:WorkspaceTransientKey,value:unknown):void{if(!SCW_TRANSIENT_KEY_SET.has(key))throw new Error('Workspace thin-state rejected non-transient key');this.transient[key]=value;this.persistTransient();}
  getTransient<T=unknown>(key:WorkspaceTransientKey):T|undefined{return this.transient[key] as T|undefined;}
  transientSnapshot():WorkspaceTransientState{return JSON.parse(JSON.stringify(this.transient)) as WorkspaceTransientState;}
  async hydrate(projectId?:string):Promise<ThinClientBootstrapEnvelope>{const envelope=await this.api.thinClientBootstrap(projectId) as ThinClientBootstrapEnvelope;this.canonicalCache.clear();this.canonicalCache.set('bootstrap',envelope.canonical||null);const canonical=envelope.canonical;if(canonical&&typeof canonical==='object'){const c=canonical as Record<string,unknown>;if(c.overview!==undefined)this.canonicalCache.set('overview',c.overview);if(c.project!==undefined&&c.project!==null)this.canonicalCache.set('project',c.project);if(c.revisionVector!==undefined)this.canonicalCache.set('revisionVector',c.revisionVector);}this.projectionFingerprint=typeof envelope.projectionFingerprint==='string'?envelope.projectionFingerprint:'';return envelope;}
  canonical<T=unknown>(key:'bootstrap'|'overview'|'project'|'revisionVector'):T|undefined{return this.canonicalCache.get(key) as T|undefined;}
  invalidateCanonical():void{this.canonicalCache.clear();this.projectionFingerprint='';}
  diagnostics(){return Object.freeze({schema:'sc-workspace-thin-client-state-diagnostics/1.0',version:'2.30.0',backendAuthoritative:true,browserAuthoritativeState:false,persistentBrowserState:'transient-only',canonicalCache:'memory-only-rehydratable',canonicalCachePersistent:false,canonicalMutationPath:'command-api-only',transientKeys:[...SCW_TRANSIENT_KEYS],canonicalCacheKeys:[...this.canonicalCache.keys()],projectionFingerprint:this.projectionFingerprint});}
}
const SCWorkspaceThinClientStateRuntime=Object.freeze({schema:'sc-workspace-thin-client-state-runtime/1.0',version:'2.30.0',backendAuthoritative:true,browserAuthoritativeState:false,persistentBrowserState:'transient-only',canonicalCache:'memory-only-rehydratable',canonicalCachePersistent:false,offlineCacheAuthoritative:false,transientKeys:SCW_TRANSIENT_KEYS,createStore(api:WorkspaceTypedApiClient,storage?:Storage|null){return new WorkspaceThinClientStateStore(api,storage===undefined?(typeof window!=='undefined'?window.localStorage:null):storage);}});
const scwThinGlobal=window as unknown as {SCWorkspaceThinClientState?:typeof SCWorkspaceThinClientStateRuntime;SCWorkspaceApi?:WorkspaceTypedApiClient;SCWorkspaceState?:WorkspaceThinClientStateStore;};
scwThinGlobal.SCWorkspaceThinClientState=SCWorkspaceThinClientStateRuntime;if(scwThinGlobal.SCWorkspaceApi){scwThinGlobal.SCWorkspaceState=SCWorkspaceThinClientStateRuntime.createStore(scwThinGlobal.SCWorkspaceApi);}
