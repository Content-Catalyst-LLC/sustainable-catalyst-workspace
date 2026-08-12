(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceProductHelp=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-product-help/1.0';
  const REPORT_SCHEMA='sc-workspace-product-help-report/1.0';
  const TOPICS=[
    {id:'first-project',category:'Start',title:'Create your first project',summary:'Projects are created only when you explicitly submit a project form or guided starter.',route:'start',steps:['Name the work.','Choose Blank, Research, Analysis, Decision, or Publication.','Submit to create the local project.']},
    {id:'local-first',category:'Storage',title:'Understand local-first storage',summary:'Guest projects stay in this browser by default. Signing in does not silently upload project content.',route:'start',steps:['Use Workspace without an account if you prefer.','Export important projects for portable copies.','Use explicit backup or sync actions only when you intend to.']},
    {id:'backup',category:'Recovery',title:'Create a recovery backup',summary:'Account recovery backup is an explicit off-device copy; it is separate from sync enrollment.',route:'reliability',steps:['Confirm the project saves locally.','Create an explicit recovery backup.','Keep a portable project export for an independent copy when the work is important.']},
    {id:'restore',category:'Recovery',title:'Restore without overwriting the source',summary:'Workspace recovery paths prefer restore-as-copy so the existing local source remains independently inspectable.',route:'integrity',steps:['Inspect persistence integrity first.','Use a verified recovery candidate or restore point.','Restore as a new local copy and compare before deleting anything.']},
    {id:'save-failed',category:'Recovery',title:'A save did not verify',summary:'Do not keep editing blindly after an integrity failure. Preserve the last verified state and inspect the journal.',route:'integrity',steps:['Open Persistence Integrity.','Export a recovery candidate if offered.','Avoid clearing browser storage until you have a portable copy.']},
    {id:'import-rejected',category:'Exchange',title:'An import was rejected',summary:'Imports are staged and assessed before commit; malformed or unsupported future schemas are intentionally blocked.',route:'interoperability',steps:['Review the import assessment.','Confirm the file is a supported Workspace package.','Do not edit schema/version fields just to force acceptance.']},
    {id:'sync-conflict',category:'Sync',title:'Resolve a cross-device sync conflict',summary:'Workspace refuses silent last-write-wins when local and cloud revisions diverge.',route:'reconcile',steps:['Preserve both versions.','Compare the competing revisions.','Choose the state deliberately or keep a separate copy.']},
    {id:'move-device',category:'Sync',title:'Move work to another device',summary:'Device migration creates a new local copy and does not transfer sync enrollment automatically.',route:'interoperability',steps:['Export a device-migration or portable project package.','Import it on the receiving device.','Review the new local copy before enrolling it in sync.']},
    {id:'review-response',category:'Review',title:'Reconcile a reviewer response',summary:'Returned review packages are assessed for source-revision drift and duplicates before reconciliation.',route:'collaboration',steps:['Stage the response.','Review whether it is current, stale, or legacy/unverifiable.','Acknowledge stale/unverifiable state explicitly before reconciliation.']},
    {id:'institutional-handoff',category:'Handoff',title:'Prepare an institutional handoff',summary:'Institutional transfer creates a separate disclosure package; the personal Workspace remains independent.',route:'institutional',steps:['Define recipient and purpose.','Validate package scope and source revision.','Export only after the transfer checklist is clear.']}
  ];
  const RECOVERY_CODES={
    'save-verification-failed':'save-failed',
    'storage-write-failed':'save-failed',
    'corrupt-state':'restore',
    'malformed-import':'import-rejected',
    'future-version':'import-rejected',
    'sync-conflict':'sync-conflict',
    'stale-review':'review-response',
    'institutional-stale':'institutional-handoff'
  };
  function clone(v){return JSON.parse(JSON.stringify(v));}
  function topics(){return clone(TOPICS);}
  function topic(id){return clone(TOPICS.find(x=>x.id===String(id||''))||null);}
  function search(query){const q=String(query||'').trim().toLowerCase();if(!q)return topics();return TOPICS.filter(t=>[t.id,t.category,t.title,t.summary].concat(t.steps).join(' ').toLowerCase().includes(q)).map(clone);}
  function guidanceFor(code){const id=RECOVERY_CODES[String(code||'')]||'';return id?topic(id):null;}
  function report(input,now){input=input||{};const selected=topic(input.topicId);return {schema:REPORT_SCHEMA,workspaceVersion:String(input.workspaceVersion||''),generatedAt:typeof now==='function'?now():new Date().toISOString(),context:{view:String(input.view||''),topicId:selected?selected.id:'',category:selected?selected.category:''},privacy:{projectContentIncluded:false,projectTitleIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,deviceIdentifierIncluded:false,accountIdentityIncluded:false},governance:{advisoryOnly:true,canonicalMutation:false,automaticRecovery:false,automaticRestore:false,automaticUpload:false,telemetry:false}};}
  return {SCHEMA,REPORT_SCHEMA,TOPICS:topics(),topics,topic,search,guidanceFor,report};
});
