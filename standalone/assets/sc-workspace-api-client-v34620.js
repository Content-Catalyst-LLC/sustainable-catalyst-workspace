(function (root, factory) {
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.SCWorkspaceApiClientFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-api-client/1.0', VERSION='3.46.2.0';
  function create(options){
    const source=options&&typeof options==='object'?options:{}; const transport=source.transport, auth=source.auth;
    if(!transport||typeof transport.request!=='function')throw new Error('Workspace API client requires a transport');
    if(!auth||typeof auth.headers!=='function')throw new Error('Workspace API client requires an auth context');
    async function request(method,path,body,options){const opts=options&&typeof options==='object'?options:{};const authHeaders=await auth.headers();const headers=Object.assign({},authHeaders||{},opts.headers||{});return transport.request({method,path,body,headers,signal:opts.signal,credentials:opts.credentials});}
    return Object.freeze({schema:SCHEMA,version:VERSION,transportName:String(transport.name||''),authName:String(auth.name||''),request,
      get(path,options){return request('GET',path,undefined,options);},post(path,body,options){return request('POST',path,body,options);},put(path,body,options){return request('PUT',path,body,options);},patch(path,body,options){return request('PATCH',path,body,options);},delete(path,options){return request('DELETE',path,undefined,options);},
      inspect(){return Object.freeze({schema:'sc-workspace-api-client-state/1.0',version:VERSION,transport:transport.inspect?transport.inspect():{name:transport.name||''},auth:auth.inspect?auth.inspect():{name:auth.name||''},hostRequired:false});}
    });
  }
  return Object.freeze({schema:SCHEMA,version:VERSION,create});
});
