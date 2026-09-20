/* Workspace v2.32.0 unified scientific object projection. Read-only generic discovery; mutations remain bounded domain APIs. */
interface WorkspaceScientificObject extends WorkspaceApiEnvelope { kind?:WorkspaceScientificObjectKind; objectId?:string; projectId?:string; name?:string; revision?:number|null; fingerprint?:string; objectFingerprint?:string; }
class WorkspaceScientificObjectStore {
  private readonly api:WorkspaceTypedApiClient; private cache:Map<string,WorkspaceScientificObject>=new Map();
  constructor(api:WorkspaceTypedApiClient){this.api=api;}
  private key(kind:WorkspaceScientificObjectKind,id:string){return kind+':'+id;}
  async list(kind?:WorkspaceScientificObjectKind,projectId?:string,q?:string,limit=100):Promise<WorkspaceScientificObject[]>{const envelope=await this.api.scientificObjects(kind,projectId,q,limit);const items=Array.isArray(envelope.items)?envelope.items as WorkspaceScientificObject[]:[];for(const item of items){if(item.kind&&item.objectId)this.cache.set(this.key(item.kind,item.objectId),item);}return items;}
  async get(kind:WorkspaceScientificObjectKind,objectId:string):Promise<WorkspaceScientificObject|undefined>{const envelope=await this.api.scientificObject(kind,objectId);const item=envelope.item as WorkspaceScientificObject|undefined;if(item)this.cache.set(this.key(kind,objectId),item);return item;}
  history(kind:WorkspaceScientificObjectKind,objectId:string,limit=100):Promise<WorkspaceApiEnvelope>{return this.api.scientificObjectHistory(kind,objectId,limit);}
  relations(kind:WorkspaceScientificObjectKind,objectId:string):Promise<WorkspaceApiEnvelope>{return this.api.scientificObjectRelations(kind,objectId);}
  cached(kind:WorkspaceScientificObjectKind,objectId:string):WorkspaceScientificObject|undefined{return this.cache.get(this.key(kind,objectId));}
  invalidate():void{this.cache.clear();}
  diagnostics(){return Object.freeze({schema:'sc-workspace-scientific-object-client/1.0',version:'2.32.0',backendAuthoritative:true,browserAuthoritativeState:false,canonicalCachePersistent:false,genericMutation:false,cachedObjectCount:this.cache.size});}
}
const SCWorkspaceScientificObjectRuntime=Object.freeze({schema:'sc-workspace-scientific-object-client-runtime/1.0',version:'2.32.0',backendAuthoritative:true,browserAuthoritativeState:false,canonicalCachePersistent:false,genericMutation:false,create(api:WorkspaceTypedApiClient){return new WorkspaceScientificObjectStore(api);}});
const scwObjectGlobal=window as unknown as {SCWorkspaceScientificObjects?:typeof SCWorkspaceScientificObjectRuntime;SCWorkspaceApi?:WorkspaceTypedApiClient;SCWorkspaceScientificObjectStore?:WorkspaceScientificObjectStore;};
scwObjectGlobal.SCWorkspaceScientificObjects=SCWorkspaceScientificObjectRuntime;if(scwObjectGlobal.SCWorkspaceApi){scwObjectGlobal.SCWorkspaceScientificObjectStore=SCWorkspaceScientificObjectRuntime.create(scwObjectGlobal.SCWorkspaceApi);}
