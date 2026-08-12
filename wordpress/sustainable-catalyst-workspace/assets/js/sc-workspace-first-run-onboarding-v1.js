(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceFirstRunOnboarding=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-first-run-onboarding/1.0';
  const DRAFT_SCHEMA='sc-workspace-first-project-draft/1.0';
  const REPORT_SCHEMA='sc-workspace-first-run-onboarding-report/1.0';
  const STARTERS=Object.freeze([
    Object.freeze({id:'blank',label:'Blank project',mode:'overview',workflow:''}),
    Object.freeze({id:'research-investigation',label:'Research investigation',mode:'guide',workflow:'research-investigation'}),
    Object.freeze({id:'analytical-assessment',label:'Analytical assessment',mode:'guide',workflow:'analytical-assessment'}),
    Object.freeze({id:'decision-case',label:'Decision case',mode:'guide',workflow:'decision-case'}),
    Object.freeze({id:'publication-preparation',label:'Publication preparation',mode:'guide',workflow:'publication-preparation'})
  ]);
  const starterIds=new Set(STARTERS.map(x=>x.id));
  const clean=(v,max)=>String(v==null?'':v).trim().slice(0,max);
  function normalizeDraft(input={}){
    const starter=starterIds.has(String(input.starter||''))?String(input.starter):'blank';
    return Object.freeze({schema:DRAFT_SCHEMA,title:clean(input.title,120),description:clean(input.description,600),starter});
  }
  function validateDraft(input={}){
    const draft=normalizeDraft(input),errors=[];
    if(!draft.title)errors.push({field:'title',code:'required',message:'Give the project a name before creating it.'});
    if(!starterIds.has(draft.starter))errors.push({field:'starter',code:'unsupported',message:'Choose a supported first-project shape.'});
    return Object.freeze({ok:errors.length===0,draft,errors:Object.freeze(errors)});
  }
  function environment(input={}){
    const projectCount=Math.max(0,Number(input.projectCount)||0),activeProject=Boolean(input.activeProject);
    return Object.freeze({schema:SCHEMA,firstRun:projectCount===0,projectCount,activeProject,storageWritable:Boolean(input.storageWritable),authenticated:Boolean(input.authenticated),accountRequired:false,automaticUpload:false,automaticSync:false,automaticGuidedSelection:false,blankProjectSupported:true});
  }
  function boundary(authenticated=false){
    return authenticated
      ? 'Creating a project saves it locally on this device. Signing in does not upload it; backup and sync remain explicit actions.'
      : 'Creating a project saves it locally on this device. No account is required, and nothing is uploaded automatically.';
  }
  function creationPlan(input={}){
    const checked=validateDraft(input);
    if(!checked.ok)return Object.freeze({ok:false,draft:checked.draft,errors:checked.errors});
    const starter=STARTERS.find(x=>x.id===checked.draft.starter)||STARTERS[0];
    return Object.freeze({ok:true,draft:checked.draft,starter,createMode:starter.id==='blank'?'blank-project':'guided-project',requiresExplicitSubmit:true,automaticUpload:false,automaticSyncEnrollment:false,automaticLifecycleAdvance:false});
  }
  function report(workspaceVersion,input={}){
    const env=environment(input);
    return {schema:REPORT_SCHEMA,workspaceVersion:clean(workspaceVersion||'0.72.0',40),generatedAt:new Date().toISOString(),firstRun:env.firstRun,projectCount:env.projectCount,storageWritable:env.storageWritable,authenticated:env.authenticated,starterCount:STARTERS.length,privacy:{projectTitleIncluded:false,projectDescriptionIncluded:false,projectContentIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{accountRequired:false,automaticProjectCreation:false,automaticStarterSelection:false,automaticUpload:false,automaticSync:false,automaticLifecycleAdvance:false,blankProjectSupported:true}};
  }
  function contract(){return {schema:SCHEMA,draftSchema:DRAFT_SCHEMA,reportSchema:REPORT_SCHEMA,starterCount:STARTERS.length,starters:STARTERS.map(x=>({id:x.id,label:x.label,mode:x.mode})),projectCreation:'explicit-submit',firstRunDetection:'zero-local-projects',accountRequired:false,automaticProjectCreation:false,automaticStarterSelection:false,automaticUpload:false,automaticSync:false,automaticLifecycleAdvance:false,canonicalMutation:'only-after-explicit-create-submit',schemaMigration:false};}
  return Object.freeze({SCHEMA,DRAFT_SCHEMA,REPORT_SCHEMA,STARTERS,normalizeDraft,validateDraft,environment,boundary,creationPlan,report,contract});
});
