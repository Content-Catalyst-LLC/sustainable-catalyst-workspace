(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceWorkflowGuidance=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-workflow-guidance/1.0';
  const REPORT_SCHEMA='sc-workspace-workflow-guidance-report/1.0';
  const EMPTY_SCHEMA='sc-workspace-empty-state-guidance/1.0';
  const n=v=>Math.max(0,Number(v)||0);
  const clean=(v,max=240)=>String(v==null?'':v).trim().slice(0,max);
  function snapshot(input={}){
    return Object.freeze({
      schema:SCHEMA,
      hasProject:Boolean(input.hasProject),
      projectCount:n(input.projectCount),
      questions:n(input.questions),
      sources:n(input.sources),
      evidence:n(input.evidence),
      claims:n(input.claims),
      notebookBlocks:n(input.notebookBlocks),
      researchRecords:n(input.researchRecords),
      researchTasks:n(input.researchTasks),
      documents:n(input.documents)
    });
  }
  function nextStep(input={}){
    const s=snapshot(input);
    if(!s.hasProject)return Object.freeze({id:'choose-project',stage:'ORIENT',title:'Choose or create a project first.',detail:'Research guidance becomes project-specific once Workspace has an active local project.',view:'start',mode:'',surface:'',action:'Go to Start'});
    if(!s.questions)return Object.freeze({id:'frame-question',stage:'FRAME',title:'Frame the question before collecting material.',detail:'Write one explicit research question so sources and evidence have a visible purpose.',view:'projects',mode:'research',surface:'',action:'Open Research Questions'});
    if(!s.sources)return Object.freeze({id:'capture-source',stage:'GATHER',title:'Add a source for the active question.',detail:'Capture a source or reading item and keep its provenance attached before extracting evidence.',view:'projects',mode:'research',surface:'',action:'Open Source Capture'});
    if(!s.evidence)return Object.freeze({id:'extract-evidence',stage:'EXTRACT',title:'Extract evidence from the material you gathered.',detail:'Create an evidence object and link it back to the source instead of jumping directly from source to conclusion.',view:'projects',mode:'research',surface:'',action:'Open Evidence'});
    if(!s.claims)return Object.freeze({id:'test-claim',stage:'CONNECT',title:'State a claim and connect the evidence.',detail:'Create a claim, keep its status explicit, and attach the evidence that supports or contests it.',view:'projects',mode:'research',surface:'',action:'Open Claims'});
    if(!s.notebookBlocks)return Object.freeze({id:'synthesize-notes',stage:'SYNTHESIZE',title:'Synthesize what the evidence is saying.',detail:'Use Notebook to combine notes, source context, and linked Workspace objects without rewriting the canonical records.',view:'notebook',mode:'',surface:'',action:'Open Notebook'});
    if(!s.documents)return Object.freeze({id:'compose',stage:'COMPOSE',title:'Turn stable research into a document.',detail:'Move into Composition when the research is ready to be organized into an explicit draft.',view:'research',mode:'',surface:'composition',action:'Open Composition'});
    return Object.freeze({id:'review-next',stage:'REVIEW',title:'Review what still needs attention.',detail:'Use Research Tasks and Review surfaces to make unresolved work explicit before export or handoff.',view:'research',mode:'',surface:'tasks',action:'Open Research Tasks'});
  }
  const EMPTY=Object.freeze({
    research:Object.freeze({title:'No research records yet.',body:'Begin with a project question or capture a source. Research Home will populate from canonical local records as the work develops.',action:'Open active project'}),
    notebook:Object.freeze({title:'No Notebook material yet.',body:'Create a notebook when you need working notes, excerpts, synthesis, or a place to connect research before promotion.',action:'Create or open Notebook'}),
    knowledge:Object.freeze({title:'Nothing matches this Knowledge view yet.',body:'Knowledge is derived from canonical Workspace Objects. Create project objects or broaden the current filters; this view does not invent records.',action:'Open Projects'}),
    graph:Object.freeze({title:'No explicit relationships to graph yet.',body:'The graph appears as projects accumulate provenance, links, promotions, citations, and other recorded relationships.',action:'Open Research'}),
    tasks:Object.freeze({title:'No research tasks yet.',body:'Select a canonical research result first, then create a task only when a concrete review, verification, sourcing, or follow-up action exists.',action:'Find research'}),
    citations:Object.freeze({title:'No citation references yet.',body:'Add references from source material when citation context is needed; Workspace does not create citations merely because a source exists.',action:'Open Citations'}),
    composition:Object.freeze({title:'No composition draft yet.',body:'Start a draft when selected research is stable enough to organize. Draft creation does not mark the underlying research complete.',action:'Open Composition'})
  });
  function emptyState(kind){
    const key=clean(kind,40);
    const item=EMPTY[key]||EMPTY.research;
    return Object.freeze({schema:EMPTY_SCHEMA,kind:key||'research',...item});
  }
  function report(workspaceVersion,input={}){
    const s=snapshot(input),step=nextStep(s);
    return {schema:REPORT_SCHEMA,workspaceVersion:clean(workspaceVersion||'0.72.0',40),generatedAt:new Date().toISOString(),nextStepId:step.id,stage:step.stage,counts:{projectCount:s.projectCount,questions:s.questions,sources:s.sources,evidence:s.evidence,claims:s.claims,notebookBlocks:s.notebookBlocks,researchRecords:s.researchRecords,researchTasks:s.researchTasks,documents:s.documents},privacy:{projectTitleIncluded:false,projectDescriptionIncluded:false,projectContentIncluded:false,queryTextIncluded:false,sourceUrlsIncluded:false,deviceIdentifierIncluded:false,automaticSubmission:false},governance:{advisoryOnly:true,hiddenReadinessScore:false,automaticCompletion:false,automaticMutation:false,automaticTaskCreation:false,automaticAi:false,automaticNavigation:false}};
  }
  function contract(){return {schema:SCHEMA,emptyStateSchema:EMPTY_SCHEMA,reportSchema:REPORT_SCHEMA,guidanceMode:'derived-contextual-advisory',canonicalMutation:false,automaticCompletion:false,automaticTaskCreation:false,automaticAi:false,hiddenReadinessScore:false,behavioralTracking:false,telemetry:false,schemaMigration:false};}
  return Object.freeze({SCHEMA,EMPTY_SCHEMA,REPORT_SCHEMA,snapshot,nextStep,emptyState,report,contract});
});
