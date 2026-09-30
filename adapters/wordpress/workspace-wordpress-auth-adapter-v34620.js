(function(root,factory){'use strict';const api=factory(root);if(typeof module==='object'&&module.exports)module.exports=api;root.SCWorkspaceWordPressAuthAdapter=api;})(typeof globalThis!=='undefined'?globalThis:this,function(root){
  'use strict'; const SCHEMA='sc-workspace-wordpress-auth-adapter/1.0',VERSION='3.46.2.0';
  function create(){const factory=root.SCWorkspaceAuthContextFactory;if(!factory||typeof factory.create!=='function')throw new Error('Workspace auth context factory unavailable');return factory.create({name:'wordpress-rest-nonce',mode:'wordpress-rest-nonce',headerProvider(){const identity=root.SCWorkspaceIdentity||{};return identity.restNonce?{'X-WP-Nonce':identity.restNonce}:{};},identityProvider(){const identity=root.SCWorkspaceIdentity||{};return {authenticated:Boolean(identity.authenticated),displayName:String(identity.displayName||''),subject:''};}});}
  return Object.freeze({schema:SCHEMA,version:VERSION,create});
});
