(function(root,factory){'use strict';const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;root.SCWorkspaceWordPressHostAdapter=api;})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict';
  const SCHEMA='sc-workspace-wordpress-host-adapter/1.1',VERSION='3.46.2.0';
  function create(config){
    const source=config&&typeof config==='object'?config:(root.SCWorkspaceConfig||{});
    const contract=root.SCWorkspaceHostAdapterContract;
    if(!contract||typeof contract.create!=='function')throw new Error('Workspace host adapter contract is unavailable');
    const base=contract.create({host:'wordpress',workspaceVersion:source.workspaceVersion||VERSION,assetBase:source.assetBase||''});
    return Object.freeze({
      schema:SCHEMA,version:VERSION,name:base.name,configuration:base.configuration,resolveAsset:base.resolveAsset,
      capabilities(){return Object.freeze(Object.assign({},base.capabilities(),{
        serverProxyAvailable:Boolean(source.apiBase),authenticationContextAvailable:true,
        transportOwnedByHost:false,authenticationOwnedByHost:false,apiClientOwnedByHost:false,
        applicationRuntimeRequired:false,hostOwnsPresentationShellOnly:true
      }));},
      inspect(){return Object.freeze({
        schema:'sc-workspace-wordpress-host-adapter-state/1.0',version:VERSION,host:'wordpress',
        assetBase:String(source.assetBase||''),serverProxyConfigured:Boolean(source.apiBase),
        transportDelegated:true,authenticationDelegated:true,apiClientDelegated:true,
        applicationKernelOwnedByHost:false,projectLifecycleOwnedByHost:false
      });}
    });
  }
  return Object.freeze({schema:SCHEMA,version:VERSION,create});
});
