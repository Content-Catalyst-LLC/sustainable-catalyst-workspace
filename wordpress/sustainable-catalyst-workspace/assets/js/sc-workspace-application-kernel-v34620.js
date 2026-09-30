(function (root, factory) {
  'use strict';
  const api=factory(root);
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.SCWorkspaceApplicationKernelFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const SCHEMA='sc-workspace-application-kernel/1.1', VERSION='3.46.2.0';
  const nowIso=()=>new Date().toISOString();
  function createKernel(options){
    const settings=options&&typeof options==='object'?options:{}; const listeners=new Map(),capabilities=new Map();
    let hostAdapter=null,transport=null,auth=null,apiClient=null,lifecycle=null,booted=false,bootedAt=null;
    function emit(type,detail){const event=Object.freeze({schema:'sc-workspace-kernel-event/1.0',version:VERSION,type:String(type||'event'),at:nowIso(),detail:detail&&typeof detail==='object'?detail:{}});(listeners.get(event.type)||[]).slice().forEach((h)=>{try{h(event);}catch(_){}});return event;}
    function on(type,handler){const key=String(type||'');if(!key||typeof handler!=='function')throw new Error('Kernel event subscription requires a type and handler');const list=listeners.get(key)||[];list.push(handler);listeners.set(key,list);return()=>listeners.set(key,(listeners.get(key)||[]).filter((x)=>x!==handler));}
    function registerHostAdapter(adapter){const contract=root.SCWorkspaceHostAdapterContract;if(contract&&typeof contract.validate==='function'){const r=contract.validate(adapter);if(!r.ok)throw new Error('Workspace host adapter contract failed: '+r.missing.join(', '));}if(!adapter||typeof adapter!=='object'||!String(adapter.name||'').trim())throw new Error('Workspace host adapter is required');hostAdapter=adapter;emit('host-adapter-registered',{host:adapter.name});return adapter;}
    function registerTransport(provider){if(!provider||typeof provider.request!=='function')throw new Error('Workspace transport provider is required');transport=provider;emit('transport-registered',{name:String(provider.name||''),mode:String(provider.mode||'')});return provider;}
    function registerAuth(provider){if(!provider||typeof provider.headers!=='function'||typeof provider.identity!=='function')throw new Error('Workspace auth provider is required');auth=provider;emit('auth-registered',{name:String(provider.name||''),mode:String(provider.mode||'')});return provider;}
    function registerApiClient(client){if(!client||typeof client.request!=='function')throw new Error('Workspace API client is required');apiClient=client;emit('api-client-registered',{transport:String(client.transportName||''),auth:String(client.authName||'')});return client;}
    function registerProjectLifecycle(provider){const required=['listProjects','createProject','openProject','deleteProject'];const missing=required.filter((key)=>!provider||typeof provider[key]!=='function');if(missing.length)throw new Error('Project lifecycle provider missing: '+missing.join(', '));lifecycle=provider;emit('project-lifecycle-registered',{provider:String(provider.name||provider.schema||'project-lifecycle'),version:String(provider.version||'')});return provider;}
    function registerCapability(name,capability){const key=String(name||'').trim();if(!key)throw new Error('Capability name is required');capabilities.set(key,capability);emit('capability-registered',{name:key});return capability;}
    function capability(name){return capabilities.get(String(name||''))||null;}
    async function boot(input){const value=input&&typeof input==='object'?input:{};if(value.hostAdapter)registerHostAdapter(value.hostAdapter);if(value.transport)registerTransport(value.transport);if(value.auth)registerAuth(value.auth);if(value.apiClient)registerApiClient(value.apiClient);if(value.projectLifecycle)registerProjectLifecycle(value.projectLifecycle);if(!hostAdapter){const contract=root.SCWorkspaceHostAdapterContract;if(!contract||typeof contract.create!=='function')throw new Error('Workspace host-adapter contract unavailable');hostAdapter=contract.create(settings.hostConfig||{host:'standalone'});}if(!transport||!auth||!apiClient)throw new Error('Workspace kernel requires transport, auth, and API client before boot');booted=true;bootedAt=nowIso();emit('booted',{host:hostAdapter.name,transport:String(transport.name||''),auth:String(auth.name||''),lifecycleAvailable:Boolean(lifecycle)});return inspect();}
    function requireLifecycle(){if(!lifecycle)throw new Error('Workspace project lifecycle provider unavailable');return lifecycle;}
    async function listProjects(){return Promise.resolve(requireLifecycle().listProjects());}
    async function createProject(input){const result=await Promise.resolve(requireLifecycle().createProject(input||{}));emit('project-created',{projectId:result&&result.id?String(result.id):''});return result;}
    async function openProject(id){const result=await Promise.resolve(requireLifecycle().openProject(String(id||'')));emit('project-opened',{projectId:String(id||'')});return result;}
    async function deleteProject(id,options){const result=await Promise.resolve(requireLifecycle().deleteProject(String(id||''),options||{}));emit('project-deleted',{projectId:String(id||''),result:Boolean(result)});return result;}
    function inspect(){return Object.freeze({schema:'sc-workspace-application-kernel-state/1.1',version:VERSION,booted,bootedAt,host:hostAdapter?String(hostAdapter.name||''):'',hostAdapterRegistered:Boolean(hostAdapter),transportRegistered:Boolean(transport),authRegistered:Boolean(auth),apiClientRegistered:Boolean(apiClient),projectLifecycleRegistered:Boolean(lifecycle),capabilityCount:capabilities.size,capabilityNames:[...capabilities.keys()],wordpressRequired:false,backendAuthoritative:true});}
    return Object.freeze({schema:SCHEMA,version:VERSION,registerHostAdapter,registerTransport,registerAuth,registerApiClient,registerProjectLifecycle,registerCapability,capability,on,boot,api(){return apiClient;},authentication(){return auth;},transport(){return transport;},listProjects,createProject,openProject,deleteProject,inspect});
  }
  return Object.freeze({schema:SCHEMA,version:VERSION,createKernel});
});
