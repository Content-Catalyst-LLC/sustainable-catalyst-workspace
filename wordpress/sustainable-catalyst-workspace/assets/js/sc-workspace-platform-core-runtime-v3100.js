(function(w){
  'use strict';
  var root='/wp-json/sc-workspace/v1/backend/platform-core-runtime';
  function request(path, options){
    var opts=Object.assign({credentials:'same-origin',headers:{'Content-Type':'application/json','X-WP-Nonce':(w.scWorkspaceApi&&w.scWorkspaceApi.nonce)||''}},options||{});
    return fetch(root+(path||''),opts).then(function(r){return r.json().then(function(b){if(!r.ok) throw b; return b;});});
  }
  w.SustainableCatalystWorkspacePlatformCore={
    schema:'sc-workspace-platform-core-v3-browser-boundary/1.0',
    workspaceVersion:'3.1.0', referenceFirst:true, backendAuthoritative:true, browserAuthoritative:false,
    browserDirectCoreAccess:false, coreCredentialBrowserVisible:false,
    profile:function(){return request('');}, readiness:function(){return request('/readiness');},
    project:function(id){return request('/projects/'+encodeURIComponent(id));},
    receipts:function(projectId){return request('/receipts'+(projectId?'?projectId='+encodeURIComponent(projectId):''));}
  };
})(window);
