(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.SCWorkspaceProjectLifecycle=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-project-lifecycle/1.0';
  const MILESTONE_SCHEMA='sc-workspace-governance-milestone/1.0';
  const STAGES=[
    {key:'draft',label:'Draft',description:'Work is being framed and assembled.'},
    {key:'evidence-ready',label:'Evidence-ready',description:'The inquiry has a visible evidence base and provenance.'},
    {key:'analysis-ready',label:'Analysis-ready',description:'Evidence and analytical structure are ready for substantive analysis.'},
    {key:'decision-ready',label:'Decision-ready',description:'Analysis and alternatives are sufficiently structured for a human decision.'},
    {key:'review-ready',label:'Review-ready',description:'The project has a coherent reviewable record with traceable support.'},
    {key:'publication-ready',label:'Publication-ready',description:'A briefing/publication artifact is assembled and ready for editorial release work.'},
    {key:'institutional-ready',label:'Institutional-ready',description:'The project is prepared for an explicit governed handoff into Catalyst Intelligence.'}
  ];
  const STAGE_KEYS=new Set(STAGES.map(s=>s.key));
  const labelFor=(key)=>STAGES.find(s=>s.key===key)?.label||'Draft';
  const arr=(v)=>Array.isArray(v)?v:[];
  const text=(v)=>String(v==null?'':v).trim();
  const check=(id,label,met,detail,source,required=true)=>({id,label,met:Boolean(met),detail:text(detail),source:text(source),required:Boolean(required)});
  const projectSessions=(state,projectId)=>arr(state?.collaboration?.sessions).filter(s=>String(s?.localProjectId||'')===String(projectId||''));
  const projectHandoffs=(state,projectId)=>arr(state?.institutional?.handoffs).filter(h=>String(h?.projectId||'')===String(projectId||''));
  function evidenceObjects(project){return arr(project?.objects).filter(o=>!o?.archivedAt&&['source','evidence'].includes(o?.type));}
  function provenanceComplete(o){const p=o?.provenance||{};return Boolean(text(p.sourceTitle)||text(p.sourceUrl)||p.capturedAt);}
  function baseFacts(project,state={}){
    const evidence=evidenceObjects(project), questions=arr(project?.research?.questions), assumptions=arr(project?.analysis?.assumptions), findings=arr(project?.analysis?.findings), methods=arr(project?.analysis?.methods), analyses=arr(project?.objects).filter(o=>!o?.archivedAt&&o?.type==='analysis'), datasets=arr(project?.objects).filter(o=>!o?.archivedAt&&o?.type==='dataset'), decisions=arr(project?.decision?.decisions), options=arr(project?.decision?.options), criteria=arr(project?.decision?.criteria), lineage=arr(project?.traceability?.lineage), evidenceLinks=arr(project?.research?.evidenceLinks), repro=arr(project?.traceability?.reproducibility), drafts=arr(project?.briefing?.drafts), documents=arr(project?.objects).filter(o=>!o?.archivedAt&&o?.type==='document'), sessions=projectSessions(state,project?.id), handoffs=projectHandoffs(state,project?.id);
    return {
      evidence,questions,assumptions,findings,methods,analyses,datasets,decisions,options,criteria,lineage,evidenceLinks,repro,drafts,documents,sessions,handoffs,
      highOpen:questions.filter(q=>q?.priority==='high'&&q?.status==='open'),
      challenged:assumptions.filter(a=>a?.status==='challenged'),
      contested:findings.filter(f=>f?.status==='contested'),
      decided:decisions.filter(d=>d?.status==='decided'),
      staleRepro:repro.filter(r=>r?.status==='stale'),
      openReviewThreads:sessions.flatMap(s=>arr(s?.threads)).filter(t=>t?.status==='open'),
      readyDrafts:drafts.filter(d=>['ready','exported'].includes(d?.status)&&arr(d?.sections).some(s=>text(s?.body)||text(s?.heading))),
      substantiveDrafts:drafts.filter(d=>arr(d?.sections).some(s=>text(s?.body)||text(s?.heading))),
      readyDocuments:documents.filter(d=>d?.status==='ready')
    };
  }
  function checksFor(project,state,stage){
    const f=baseFacts(project,state), inquiry=Boolean(f.questions.length||text(project?.description).length>=20), evidencePresent=f.evidence.length>0, evidenceProvenance=evidencePresent&&f.evidence.every(provenanceComplete), analysisQuestion=arr(project?.analysis?.questions).length>0, analysisMaterial=Boolean(f.findings.length||f.analyses.length), decisionOptions=f.options.length>=2, reviewable=Boolean(f.decided.length||f.substantiveDrafts.length||f.readyDocuments.length), traceable=Boolean(f.lineage.length||f.evidenceLinks.length), briefingReady=Boolean(f.readyDrafts.length||f.readyDocuments.length), institutionalMaterial=Boolean(f.decided.length||briefingReady);
    const byStage={
      'draft':[
        check('project-exists','Project record exists',Boolean(project?.id),'Workspace project identity is present.','Project')
      ],
      'evidence-ready':[
        check('inquiry-defined','Inquiry or project purpose is defined',inquiry,inquiry?'Research question or substantive project description is present.':'Add a research question or a substantive project description.','Research'),
        check('evidence-present','Evidence/source material is present',evidencePresent,evidencePresent?`${f.evidence.length} source/evidence object(s) available.`:'Add at least one Source or Evidence object.','Objects'),
        check('evidence-provenance','Evidence provenance is recorded',evidenceProvenance,evidenceProvenance?'All current Source/Evidence objects have recorded provenance context.':'Review Source/Evidence provenance; at least one item is incomplete.','Provenance'),
        check('high-priority-questions','No high-priority research question is still open',f.highOpen.length===0,f.highOpen.length?`${f.highOpen.length} high-priority question(s) remain open.`:'No high-priority open questions detected.','Research')
      ],
      'analysis-ready':[
        check('evidence-present','Evidence/source material is present',evidencePresent,evidencePresent?`${f.evidence.length} source/evidence object(s) available.`:'Add evidence before analysis.','Evidence'),
        check('analysis-question','An analysis question is defined',analysisQuestion,analysisQuestion?'At least one analysis question is present.':'Define the analytical question.','Analysis'),
        check('analysis-method','An analysis method is recorded',f.methods.length>0,f.methods.length?`${f.methods.length} method record(s) available.`:'Record the method or analytical approach.','Analysis'),
        check('analysis-inputs','Dataset or evidence inputs are available',Boolean(f.datasets.length||f.evidence.length),`${f.datasets.length} dataset(s) · ${f.evidence.length} evidence/source object(s).`,'Analysis'),
        check('assumptions-reviewed','No assumption is currently marked challenged',f.challenged.length===0,f.challenged.length?`${f.challenged.length} challenged assumption(s) need attention.`:'No challenged assumptions detected.','Analysis')
      ],
      'decision-ready':[
        check('analysis-material','Analysis findings or Analysis objects exist',analysisMaterial,analysisMaterial?`${f.findings.length} finding(s) · ${f.analyses.length} Analysis object(s).`:'Record analysis findings or create an Analysis object.','Analysis'),
        check('decision-record','A decision case exists',f.decisions.length>0,f.decisions.length?`${f.decisions.length} decision record(s) available.`:'Create a Decision record.','Decision'),
        check('decision-options','At least two options are explicit',decisionOptions,`${f.options.length} option(s) recorded.`,'Decision'),
        check('decision-criteria','Decision criteria are explicit',f.criteria.length>0,`${f.criteria.length} criterion/criteria recorded.`,'Decision'),
        check('contested-findings','No analytical finding is currently contested',f.contested.length===0,f.contested.length?`${f.contested.length} contested finding(s) remain.`:'No contested findings detected.','Analysis')
      ],
      'review-ready':[
        check('reviewable-output','A decision, briefing draft, or ready Document is reviewable',reviewable,reviewable?'Reviewable project output is present.':'Create a decision record, substantive briefing, or ready Document.','Decision / Briefing'),
        check('traceability-visible','Evidence-to-work relationships are visible',traceable,traceable?`${f.lineage.length} lineage relationship(s) · ${f.evidenceLinks.length} research evidence link(s).`:'Add traceability or research evidence links.','Traceability'),
        check('high-priority-questions','No high-priority research question is still open',f.highOpen.length===0,f.highOpen.length?`${f.highOpen.length} high-priority question(s) remain open.`:'No high-priority open questions detected.','Research'),
        check('reproducibility-current','No reproducibility record is marked stale',f.staleRepro.length===0,f.staleRepro.length?`${f.staleRepro.length} stale reproducibility record(s).`:'No stale reproducibility records detected.','Traceability')
      ],
      'publication-ready':[
        check('briefing-output','A briefing/publication output is ready',briefingReady,briefingReady?`${f.readyDrafts.length} ready/exported briefing(s) · ${f.readyDocuments.length} ready Document(s).`:'Mark a briefing ready/exported or materialize a ready Document.','Briefing'),
        check('evidence-provenance','Evidence provenance is recorded',evidenceProvenance,evidenceProvenance?'Evidence provenance is complete for current Source/Evidence objects.':'Review Source/Evidence provenance before publication.','Provenance'),
        check('traceability-visible','Supporting relationships are visible',traceable,traceable?'Traceability or evidence links are present.':'Add traceability/evidence links so the output can be audited.','Traceability'),
        check('contested-findings','No analytical finding is currently contested',f.contested.length===0,f.contested.length?`${f.contested.length} contested finding(s) remain.`:'No contested findings detected.','Analysis')
      ],
      'institutional-ready':[
        check('institutional-material','A decided or publication-ready artifact exists',institutionalMaterial,institutionalMaterial?'Decision/publication material is present.':'Prepare a decided outcome or publication-ready artifact.','Decision / Briefing'),
        check('evidence-provenance','Evidence provenance is recorded',evidenceProvenance,evidenceProvenance?'Evidence provenance is visible.':'Review Source/Evidence provenance before institutional handoff.','Provenance'),
        check('review-threads','No open collaboration review thread remains',f.openReviewThreads.length===0,f.openReviewThreads.length?`${f.openReviewThreads.length} open review thread(s) remain.`:'No open review threads detected.','Collaboration'),
        check('high-priority-questions','No high-priority research question is still open',f.highOpen.length===0,f.highOpen.length?`${f.highOpen.length} high-priority question(s) remain open.`:'No high-priority open questions detected.','Research'),
        check('institutional-scope','Institutional handoff can be prepared explicitly',true,f.handoffs.length?`${f.handoffs.length} institutional handoff record(s) already exist.`:'No institutional handoff is required to declare readiness; promotion remains a separate explicit action.','Institutional Handoff')
      ]
    };
    return byStage[STAGE_KEYS.has(stage)?stage:'draft']||byStage.draft;
  }
  function assess(project,state={},stage='draft'){
    const key=STAGE_KEYS.has(stage)?stage:'draft', checks=checksFor(project,state,key), required=checks.filter(c=>c.required), metCount=required.filter(c=>c.met).length;
    return {schema:SCHEMA,stage:key,label:labelFor(key),generatedAt:new Date().toISOString(),checks,totalCount:required.length,metCount,unmetCount:required.length-metCount,ready:required.every(c=>c.met),governance:{score:null,automaticAdvance:false,humanDeclarationRequired:true,readinessIsCertification:false}};
  }
  function normalizeLifecycle(raw={}){
    const value=raw&&typeof raw==='object'?raw:{}, now=new Date().toISOString(), state=STAGE_KEYS.has(value.state)?value.state:'draft';
    return {schema:SCHEMA,state,milestones:arr(value.milestones).map(m=>({schema:MILESTONE_SCHEMA,id:text(m?.id).slice(0,160),fromState:STAGE_KEYS.has(m?.fromState)?m.fromState:'draft',toState:STAGE_KEYS.has(m?.toState)?m.toState:'draft',rationale:text(m?.rationale).slice(0,4000),acknowledged:Boolean(m?.acknowledged),readiness:m?.readiness&&typeof m.readiness==='object'?m.readiness:{},declaredAt:text(m?.declaredAt)||now})).filter(m=>m.id).slice(0,80),updatedAt:text(value.updatedAt)||now};
  }
  return {SCHEMA,MILESTONE_SCHEMA,STAGES,STAGE_KEYS,labelFor,assess,normalizeLifecycle};
});
