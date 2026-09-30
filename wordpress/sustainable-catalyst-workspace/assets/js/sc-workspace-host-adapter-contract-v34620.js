(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceHostAdapterContract = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const SCHEMA = 'sc-workspace-host-adapter-contract/1.1';
  const VERSION = '3.46.2.0';
  const REQUIRED_METHODS = Object.freeze(['name','configuration','resolveAsset','capabilities']);
  function validate(adapter) {
    const missing=[];
    if(!adapter||typeof adapter!=='object') return {ok:false,schema:SCHEMA,version:VERSION,missing:[...REQUIRED_METHODS]};
    REQUIRED_METHODS.forEach((key)=>{
      if(key==='name'){if(!String(adapter.name||'').trim())missing.push(key);}
      else if(typeof adapter[key]!=='function')missing.push(key);
    });
    return {ok:missing.length===0,schema:SCHEMA,version:VERSION,missing};
  }
  function create(config){
    const source=config&&typeof config==='object'?config:{};
    const hostName=String(source.host||'standalone').trim().toLowerCase()||'standalone';
    const assetBase=String(source.assetBase||'').trim();
    const adapter={
      schema:SCHEMA,version:VERSION,name:hostName,
      configuration(){return Object.freeze({host:hostName,workspaceVersion:String(source.workspaceVersion||VERSION),assetBase});},
      resolveAsset(path){
        const value=String(path||'').replace(/^\/+/, '');
        if(!assetBase)return value;
        try{return new URL(value,assetBase.endsWith('/')?assetBase:assetBase+'/').href;}
        catch(_){return assetBase.replace(/\/+$/,'')+'/'+value;}
      },
      capabilities(){return Object.freeze({hostConfiguration:true,assetResolution:true,transportOwnedByHost:false,authenticationOwnedByHost:false,apiClientOwnedByHost:false,applicationRuntimeRequired:false});}
    };
    const result=validate(adapter); if(!result.ok)throw new Error('Invalid Workspace host adapter: '+result.missing.join(', '));
    return Object.freeze(adapter);
  }
  return Object.freeze({schema:SCHEMA,version:VERSION,requiredMethods:REQUIRED_METHODS,validate,create});
});
