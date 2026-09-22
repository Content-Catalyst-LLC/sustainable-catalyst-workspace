/* Workspace v3.2.0 Unified Research Project Context browser adapter. */
(function(){
  'use strict';
  const root='/wp-json/sc-workspace/v1/backend/research-context';
  async function request(path, options){
    const opts=Object.assign({credentials:'same-origin',headers:{'Accept':'application/json'}},options||{});
    if(opts.body && typeof opts.body!=='string'){ opts.headers=Object.assign({},opts.headers,{'Content-Type':'application/json'}); opts.body=JSON.stringify(opts.body); }
    const res=await fetch(root+path,opts); const body=await res.json().catch(()=>({}));
    if(!res.ok) throw Object.assign(new Error('Workspace research context request failed'),{status:res.status,body});
    return body;
  }
  window.SCWorkspaceUnifiedResearchContext=Object.freeze({
    schema:'sc-workspace-unified-research-project-context-browser-adapter/1.0',version:'3.2.0',backendAuthoritative:true,browserAuthoritativeState:false,referenceFirst:true,
    profile:()=>request(''),
    project:(projectId)=>request('/projects/'+encodeURIComponent(projectId)),
    snapshot:(projectId,includeCoreViews=true)=>request('/projects/'+encodeURIComponent(projectId)+'/snapshots',{method:'POST',body:{schema:'sc-workspace-unified-research-project-context-snapshot-request/1.0',includeCoreViews}}),
    snapshots:(projectId,limit=100)=>request('/projects/'+encodeURIComponent(projectId)+'/snapshots?limit='+encodeURIComponent(String(limit)))
  });
})();
