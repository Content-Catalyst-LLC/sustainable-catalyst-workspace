const assert=require('assert');const H=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-v1.js');
const root={querySelectorAll:()=>[{hidden:false,getAttribute:()=> 'start'},{hidden:true,getAttribute:()=> 'research'}]};
const rh=H.routeHealth(root);assert.equal(rh.isolated,true);assert.equal(rh.visibleCount,1);
const gate=H.assess({capabilities:{localStorage:true,webCryptoSha256:true,fileApi:true},routeHealth:rh,recovery:{available:true},performanceAvailable:true,securityAvailable:true,workspaceVersion:'0.60.0',expectedVersion:'0.60.0',versionCurrent:true});
assert.equal(gate.state,'ready');assert.equal(gate.checks.length,8);assert.equal(gate.governance.hiddenScore,false);assert.equal(gate.governance.automaticRepair,false);
const limited=H.assess({capabilities:{localStorage:false,webCryptoSha256:false,fileApi:false},routeHealth:{isolated:false,visibleCount:3},recovery:{available:false},performanceAvailable:false,securityAvailable:false,workspaceVersion:'0.59.1',expectedVersion:'0.60.0',versionCurrent:false});assert.equal(limited.state,'limited');assert(limited.attention.includes('shell'));
const snap=H.fieldSnapshot('0.60.0',gate,{status:'ready'});assert.equal(snap.privacy.automaticTelemetry,false);assert.equal(snap.privacy.projectContentIncluded,false);console.log('PASS - Workspace v0.60.0 Public Product Beta II runtime');
