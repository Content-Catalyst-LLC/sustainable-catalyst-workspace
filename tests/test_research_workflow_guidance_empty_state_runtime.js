const assert=require('assert');
const api=require('../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-workflow-guidance-v1.js');
assert.equal(api.contract().schema,'sc-workspace-workflow-guidance/1.0');
assert.equal(api.nextStep({hasProject:false}).id,'choose-project');
assert.equal(api.nextStep({hasProject:true}).id,'frame-question');
assert.equal(api.nextStep({hasProject:true,questions:1}).id,'capture-source');
assert.equal(api.nextStep({hasProject:true,questions:1,sources:1}).id,'extract-evidence');
assert.equal(api.nextStep({hasProject:true,questions:1,sources:1,evidence:1}).id,'test-claim');
assert.equal(api.nextStep({hasProject:true,questions:1,sources:1,evidence:1,claims:1}).id,'synthesize-notes');
assert.equal(api.nextStep({hasProject:true,questions:1,sources:1,evidence:1,claims:1,notebookBlocks:2}).id,'compose');
assert.equal(api.nextStep({hasProject:true,questions:1,sources:1,evidence:1,claims:1,notebookBlocks:2,documents:1}).id,'review-next');
for(const k of ['research','notebook','knowledge','graph','tasks','citations','composition']){const e=api.emptyState(k);assert.ok(e.title&&e.body&&e.action);}
const r=api.report('0.72.0',{hasProject:true,questions:1,sources:1});
assert.equal(r.workspaceVersion,'0.72.0'); assert.equal(r.privacy.projectContentIncluded,false); assert.equal(r.governance.hiddenReadinessScore,false); assert.equal(r.governance.automaticMutation,false); assert.equal(r.governance.automaticTaskCreation,false); assert.equal(r.governance.automaticAi,false);
console.log('PASS - v0.72.0 workflow guidance runtime');
