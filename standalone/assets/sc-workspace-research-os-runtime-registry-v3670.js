(function(g){"use strict";
const V="3.67.0",B="/v1/research-os-runtime-registry";
async function q(p,o){const r=await fetch(B+p,Object.assign({credentials:"same-origin",headers:{"Content-Type":"application/json"}},o||{}));if(!r.ok)throw new Error("Workspace runtime registry request failed: "+r.status);return r.json();}
g.SCWorkspaceResearchOSRuntimeRegistryV3670=Object.freeze({
version:V,
authority:Object.freeze({invokeRuntime:false,mutateRuntime:false,activateCapability:false,dispatchOperation:false,approve:false,publish:false,externalSideEffects:false,decide:false}),
profile:()=>q("",{method:"GET"}),runtimes:()=>q("/runtimes",{method:"GET"}),operations:()=>q("/operations",{method:"GET"}),
authorityMatrix:()=>q("/authority",{method:"GET"}),compatibility:()=>q("/compatibility",{method:"GET"}),validate:()=>q("/validate",{method:"GET"}),
discover:(kind,payload)=>q("/discover",{method:"POST",body:JSON.stringify({kind,payload:payload||{}})})
});})(window);
