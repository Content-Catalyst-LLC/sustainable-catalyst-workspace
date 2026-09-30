(function (root, factory) {
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.SCWorkspaceAuthContextFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-auth-context/1.0', VERSION='3.46.2.0';
  function create(options){
    const source=options&&typeof options==='object'?options:{};
    const headerProvider=typeof source.headerProvider==='function'?source.headerProvider:()=>({});
    const identityProvider=typeof source.identityProvider==='function'?source.identityProvider:()=>({authenticated:Boolean(source.authenticated),displayName:String(source.displayName||''),subject:String(source.subject||'')});
    return Object.freeze({schema:SCHEMA,version:VERSION,name:String(source.name||'auth-context'),mode:String(source.mode||'anonymous'),
      async headers(){const value=await Promise.resolve(headerProvider());return Object.assign({},value||{});},
      identity(){const value=identityProvider()||{};return Object.freeze({authenticated:Boolean(value.authenticated),displayName:String(value.displayName||''),subject:String(value.subject||'')});},
      inspect(){const id=this.identity();return Object.freeze({schema:'sc-workspace-auth-context-state/1.0',version:VERSION,name:String(source.name||'auth-context'),mode:String(source.mode||'anonymous'),authenticated:id.authenticated,hostRequired:false,transportEmbedded:false});}
    });
  }
  function createAnonymous(){return create({name:'anonymous',mode:'anonymous',authenticated:false});}
  return Object.freeze({schema:SCHEMA,version:VERSION,create,createAnonymous});
});
