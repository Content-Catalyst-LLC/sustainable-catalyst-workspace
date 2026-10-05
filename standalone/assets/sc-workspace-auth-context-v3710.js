(function(root,factory){
'use strict';
const api=factory(root);
if(typeof module==='object'&&module.exports)module.exports=api;
root.SCWorkspaceAuthContextFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(root){
'use strict';
const SCHEMA='sc-workspace-auth-context/2.0', VERSION='3.71.0';
function join(base,path){const b=String(base||'').replace(/\/+$/,'');return b+'/'+String(path||'').replace(/^\/+/,'');}
function anonymous(){return Object.freeze({authenticated:false,displayName:'',subject:'',authenticationMethod:'anonymous'});}
function create(options){
 const source=options&&typeof options==='object'?options:{};
 const headerProvider=typeof source.headerProvider==='function'?source.headerProvider:()=>({});
 const identityProvider=typeof source.identityProvider==='function'?source.identityProvider:()=>anonymous();
 return Object.freeze({schema:SCHEMA,version:VERSION,name:String(source.name||'auth-context'),mode:String(source.mode||'anonymous'),
  async headers(){const value=await Promise.resolve(headerProvider());return Object.assign({},value||{});},
  identity(){const value=identityProvider()||{};return Object.freeze({authenticated:Boolean(value.authenticated),displayName:String(value.displayName||''),subject:String(value.subject||''),authenticationMethod:String(value.authenticationMethod||'')});},
  async refresh(){return this.identity();},
  inspect(){const id=this.identity();return Object.freeze({schema:'sc-workspace-auth-context-state/2.0',version:VERSION,name:String(source.name||'auth-context'),mode:String(source.mode||'anonymous'),authenticated:id.authenticated,sessionAware:false,serviceCredentialsBrowserVisible:false});}
 });
}
function createAnonymous(){return create({name:'anonymous',mode:'anonymous'});}
function createSessionAware(options){
 const source=options&&typeof options==='object'?options:{};
 const apiBase=String(source.apiBase||'').trim();
 const fetchImpl=source.fetchImpl||(typeof fetch==='function'?fetch.bind(globalThis):null);
 if(!fetchImpl)throw new Error('Workspace session auth requires fetch');
 let current=anonymous();
 async function refresh(){
  try{
   const response=await fetchImpl(join(apiBase,'/v1/session'),{method:'GET',credentials:'include',headers:{Accept:'application/json'}});
   if(!response.ok){current=anonymous();return current;}
   const payload=await response.json();
   current=Object.freeze({
    authenticated:Boolean(payload&&payload.authenticated),
    displayName:String(payload&&payload.displayName||''),
    subject:String(payload&&payload.subject||''),
    authenticationMethod:String(payload&&payload.authenticationMethod||'anonymous')
   });
  }catch(_){current=anonymous();}
  return current;
 }
 return Object.freeze({
  schema:SCHEMA,version:VERSION,name:'standalone-session',mode:'signed-http-only-session-cookie',
  async headers(){return {};},
  identity(){return current;},
  refresh,
  inspect(){return Object.freeze({schema:'sc-workspace-auth-context-state/2.0',version:VERSION,name:'standalone-session',mode:'signed-http-only-session-cookie',authenticated:current.authenticated,sessionAware:true,httpOnlyCookie:true,serviceCredentialsBrowserVisible:false});}
 });
}
return Object.freeze({schema:SCHEMA,version:VERSION,create,createAnonymous,createSessionAware});
});
