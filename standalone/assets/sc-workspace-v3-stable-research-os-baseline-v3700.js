(function(root){
'use strict';
const VERSION='3.70.0';
const BASE_PATH='/v1/workspace-v3-stable-baseline';
function baseUrl(){const cfg=root.SCWorkspaceStandaloneConfig||root.SCWorkspaceConfig||{};return String(cfg.apiBase||'https://workspace-api.sustainablecatalyst.com').replace(/\/+$/,'');}
async function request(path){const response=await fetch(baseUrl()+BASE_PATH+String(path||''),{method:'GET',credentials:'omit',headers:{'Accept':'application/json'}});if(!response.ok)throw new Error('Workspace stable baseline request failed: '+response.status);return response.json();}
root.SCWorkspaceStableResearchOSBaselineV3700=Object.freeze({schema:'sc-workspace-standalone-stable-research-os-baseline-client/1.0',version:VERSION,authority:Object.freeze({mutate:false,execute:false,approve:false,publish:false,restore:false,decide:false}),profile:()=>request(''),runtimeChain:()=>request('/runtime-chain'),capabilities:()=>request('/capabilities'),authoritySummary:()=>request('/authority'),portability:()=>request('/portability'),compatibility:()=>request('/compatibility'),certification:()=>request('/certification'),operations:()=>request('/operations'),snapshot:()=>request('/snapshot'),validate:()=>request('/validate')});
})(typeof globalThis!=='undefined'?globalThis:this);
