(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  if(root) root.SCWorkspaceSafeActions=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-safe-actions/1.0';
  const GATE_SCHEMA='sc-workspace-action-gate/1.0';
  const ACTIONS={
    'restore-copy':{label:'Restore as copy',ack:'I understand this restore creates a new local project copy and does not overwrite the current project.'},
    'sync-resolve-local':{label:'Keep local as sync head',ack:'I reviewed the local/cloud differences and understand the local project will become a new cloud synchronization revision.'},
    'sync-resolve-cloud':{label:'Use cloud here',ack:'I reviewed the local/cloud differences and understand Workspace will preserve the divergent local state as a conflict copy before applying cloud here.'},
    'share-portable':{label:'Export portable project',ack:'I reviewed the project changes and sharing scope and understand this action creates a portable copy outside the local Workspace boundary.'},
    'share-review-copy':{label:'Export static review copy',ack:'I reviewed the project changes and understand this readable HTML copy leaves the local Workspace boundary.'},
    'institutional-promotion':{label:'Export institutional promotion',ack:'I reviewed the project changes and promotion scope and understand institutional governance begins only after the receiving system accepts the promoted copy.'}
  };
  function cleanSummary(review){const s=review&&review.summary||{};return {added:Math.max(0,Number(s.added)||0),removed:Math.max(0,Number(s.removed)||0),modified:Math.max(0,Number(s.modified)||0),total:Math.max(0,Number(s.total)||0),relationshipsChanged:Math.max(0,Number(s.relationshipsChanged)||0),categoriesChanged:Math.max(0,Number(s.categoriesChanged)||0)};}
  function buildGate(input={}){
    const action=String(input.action||''); if(!ACTIONS[action]) throw new Error('Unsupported safe action.');
    const review=input.review&&typeof input.review==='object'?input.review:null;
    return {schema:GATE_SCHEMA,id:String(input.id||''),action,actionLabel:ACTIONS[action].label,projectId:String(input.projectId||''),projectTitle:String(input.projectTitle||''),baseline:input.baseline&&typeof input.baseline==='object'?input.baseline:{kind:'none',label:'No comparison baseline'},target:input.target&&typeof input.target==='object'?input.target:{kind:'current-project',label:'Current project'},reviewAvailable:Boolean(review),reviewSummary:cleanSummary(review),attention:Array.isArray(review?.attention)?review.attention.map(String).slice(0,20):[],checkpointRestorePointId:String(input.checkpointRestorePointId||''),requiredAcknowledgement:ACTIONS[action].ack,createdAt:String(input.createdAt||new Date().toISOString()),governance:{automaticProceed:false,automaticApply:false,automaticMerge:false,hiddenRiskScore:false,humanAcknowledgementRequired:true}};
  }
  function canProceed(gate,acknowledged){return Boolean(gate&&gate.schema===GATE_SCHEMA&&ACTIONS[gate.action]&&acknowledged===true);}
  function historyRecord(gate,outcome,at){return {schema:SCHEMA,id:String(gate?.id||''),action:String(gate?.action||''),actionLabel:String(gate?.actionLabel||''),projectId:String(gate?.projectId||''),projectTitle:String(gate?.projectTitle||''),outcome:['proceeded','cancelled','blocked'].includes(outcome)?outcome:'blocked',reviewAvailable:Boolean(gate?.reviewAvailable),reviewSummary:cleanSummary({summary:gate?.reviewSummary||{}}),baseline:gate?.baseline||{kind:'none',label:'No comparison baseline'},target:gate?.target||{kind:'current-project',label:'Current project'},checkpointRestorePointId:String(gate?.checkpointRestorePointId||''),acknowledged:outcome==='proceeded',at:String(at||new Date().toISOString())};}
  return {SCHEMA,GATE_SCHEMA,ACTIONS,buildGate,canProceed,historyRecord,cleanSummary};
});
