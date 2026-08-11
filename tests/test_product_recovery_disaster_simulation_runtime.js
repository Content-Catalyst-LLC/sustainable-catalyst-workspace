const assert=require('assert');
const api=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-recovery-disaster-simulation-v1.js');
const persistence=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-persistence-integrity-v1.js');
const compatibility=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js');
require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-cross-device-continuity-v1.js');
const continuity=global.SCWorkspaceCrossDeviceContinuity;
const report=api.runAll({workspaceVersion:'0.69.0',persistence,compatibility,continuity});
assert.equal(report.schema,'sc-workspace-recovery-disaster-report/1.0'); assert.equal(report.total,8); assert.equal(report.passed,8); assert.equal(report.state,'pass');
assert.equal(report.governance.sandboxedSimulation,true); assert.equal(report.governance.canonicalMutation,false); assert.equal(report.governance.backgroundNetwork,false); assert.equal(report.privacy.projectContentIncluded,false);
for(const row of report.scenarios){assert.equal(row.result.pass,true,row.id);assert.equal(row.result.canonicalMutation,false,row.id);}
const q=api.memoryStorage({x:'old'},{failWrites:true});let threw=false;try{q.setItem('x','new')}catch(e){threw=e.name==='QuotaExceededError'}assert.equal(threw,true);assert.equal(q.getItem('x'),'old');
console.log('PASS - v0.69.0 recovery disaster simulation runtime');
