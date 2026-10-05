(function(root,factory){
'use strict';
const api=factory();
if(typeof module==='object'&&module.exports)module.exports=api;
root.SCWorkspaceServerProjectBridgeFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const VERSION='3.72.0',SCHEMA='sc-workspace-server-project-bridge/1.0';
function clone(v){return v==null?v:JSON.parse(JSON.stringify(v));}
function create(options){
 const source=options&&typeof options==='object'?options:{};
 const api=source.apiClient;
 const auth=source.auth;
 if(!api||typeof api.get!=='function')throw new Error('Server project bridge requires Workspace API client');
 function authenticated(){const id=auth&&typeof auth.identity==='function'?auth.identity():{};return Boolean(id&&id.authenticated);}
 async function bootstrap(){
  if(!authenticated())return Object.freeze({schema:'sc-workspace-server-project-bridge-bootstrap/1.0',version:VERSION,authenticated:false,projects:[],notebooks:[]});
  const response=await api.get('/v1/user-workspace/bootstrap');
  const item=response&&response.item?response.item:{};
  return Object.freeze({schema:'sc-workspace-server-project-bridge-bootstrap/1.0',version:VERSION,authenticated:true,projects:clone(item.projects||[]),notebooks:clone(item.notebooks||[]),serverAuthoritativeWhenAuthenticated:true});
 }
 async function fetchProject(projectId){
  if(!authenticated())return null;
  const response=await api.get('/v1/user-workspace/projects/'+encodeURIComponent(String(projectId||'')));
  return response&&response.item?clone(response.item):null;
 }
 async function hydrateProject(projectId){
  const result=await fetchProject(projectId);
  if(!result||!result.package)return null;
  const pkg=result.package;
  return clone(pkg.project||pkg);
 }
 function inspect(){return Object.freeze({schema:'sc-workspace-server-project-bridge-state/1.0',version:VERSION,authenticated:authenticated(),serverAuthoritativeWhenAuthenticated:true,anonymousLocalFirstSupported:true,automaticDestructiveMerge:false,explicitReconciliation:true});}
 return Object.freeze({schema:SCHEMA,version:VERSION,bootstrap,fetchProject,hydrateProject,inspect});
}
return Object.freeze({schema:SCHEMA,version:VERSION,create});
});
