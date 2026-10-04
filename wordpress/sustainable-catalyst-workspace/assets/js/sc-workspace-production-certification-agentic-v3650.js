(function(g){"use strict";
const V="3.65.0",B="/v1/production-certification-agentic-runtime";
const O=["workspace.production-certification.validate","workspace.production-certification.certify-runtime-chain","workspace.production-certification.route-inventory","workspace.production-certification.compatibility","workspace.production-certification.host-parity","workspace.production-certification.recovery-readiness","workspace.production-certification.package-integrity","workspace.production-certification.snapshot"];
async function q(p,o){const r=await fetch(B+p,Object.assign({credentials:"same-origin",headers:{"Content-Type":"application/json"}},o||{}));if(!r.ok)throw new Error("Workspace production certification request failed: "+r.status);return r.json();}
g.SCWorkspaceProductionCertificationAgenticV3650=Object.freeze({
version:V,operations:Object.freeze(O),
authority:Object.freeze({execution:false,approval:false,publication:false,mutation:false,governanceBypass:false}),
profile:()=>q("",{method:"GET"}),operationIndex:()=>q("/operations",{method:"GET"}),report:()=>q("/report",{method:"GET"}),
execute:(operation,payload)=>{if(!O.includes(operation))throw new Error("Unsupported v3.65 certification operation");return q("/execute",{method:"POST",body:JSON.stringify({operation,payload:payload||{}})});}
});})(window);
