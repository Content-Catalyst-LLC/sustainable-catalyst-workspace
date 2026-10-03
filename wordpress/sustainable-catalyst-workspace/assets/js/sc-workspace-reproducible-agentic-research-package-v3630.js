(function(g){"use strict";const V="3.63.0",B="/v1/reproducible-agentic-research-package-runtime";
const O=["workspace.research-package.validate","workspace.research-package.create","workspace.research-package.add-object",
"workspace.research-package.add-receipt","workspace.research-package.add-governance","workspace.research-package.finalize",
"workspace.research-package.verify","workspace.research-package.snapshot"];
async function q(p,o){const r=await fetch(B+p,Object.assign({credentials:"same-origin",headers:{"Content-Type":"application/json"}},o||{}));
if(!r.ok)throw new Error("Research package runtime request failed: "+r.status);return r.json();}
g.SCWorkspaceReproducibleAgenticResearchPackageV3630=Object.freeze({version:V,operations:Object.freeze(O),
authority:Object.freeze({approval:false,replay:false,governanceBypass:false,externalSideEffects:false,sourceMutation:false}),
profile:()=>q("",{method:"GET"}),operationIndex:()=>q("/operations",{method:"GET"}),
execute:(operation,payload)=>{if(!O.includes(operation))throw new Error("Unsupported v3.63 operation");
return q("/execute",{method:"POST",body:JSON.stringify({operation:operation,payload:payload||{}})});}});})(window);
