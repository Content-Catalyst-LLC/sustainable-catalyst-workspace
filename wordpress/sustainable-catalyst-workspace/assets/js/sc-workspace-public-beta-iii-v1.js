(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspacePublicBetaIII=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-public-beta-iii/1.0';
  const CHECKPOINT_SCHEMA='sc-workspace-product-journey-checkpoint/1.0';
  const REPORT_SCHEMA='sc-workspace-product-journey-report/1.0';
  const MANUAL_SCHEMA='sc-workspace-product-journey-manual/1.0';
  const SESSION_KEY='sc_workspace_public_beta_iii_journey_v0700';
  const STEPS=Object.freeze([
    Object.freeze({id:'discover',label:'Discover',number:'01',view:'start',surface:'',external:true,actionLabel:'Explore the Library',purpose:'Find relevant public knowledge before pulling material into a project.',selectors:['a[href*="/knowledge-libraries/"]']}),
    Object.freeze({id:'capture',label:'Capture',number:'02',view:'notebook',surface:'',external:false,actionLabel:'Open Notebook',purpose:'Capture a source, excerpt, note, or research question while retaining provenance.',selectors:['[data-scw-notebook-capture-form]','[data-scw-notebook-block-form]']}),
    Object.freeze({id:'organize',label:'Organize',number:'03',view:'research',surface:'collections',external:false,actionLabel:'Open Collections',purpose:'Organize canonical research into explicit collections and reusable views.',selectors:['[data-scw-research-surface="collections"]','[data-scw-research-collection-list]']}),
    Object.freeze({id:'analyze',label:'Analyze',number:'04',view:'projects',surface:'',external:false,actionLabel:'Open Projects',purpose:'Create or inspect analysis objects with methods and assumptions kept visible.',selectors:['[data-scw-object-create-form] option[value="analysis"]']}),
    Object.freeze({id:'synthesize',label:'Synthesize',number:'05',view:'notebook',surface:'',external:false,actionLabel:'Open Notebook synthesis',purpose:'Create an explicit synthesis from selected notebook material without replacing the originals.',selectors:['[data-scw-notebook-synthesis-form]']}),
    Object.freeze({id:'decide',label:'Decide',number:'06',view:'projects',surface:'',external:false,actionLabel:'Open Projects',purpose:'Record a decision or trade-off with its criteria, evidence, risk, and rationale.',selectors:['[data-scw-object-create-form] option[value="decision"]']}),
    Object.freeze({id:'compose',label:'Compose',number:'07',view:'research',surface:'composition',external:false,actionLabel:'Open Composition',purpose:'Author a document while keeping research and citation attachments explicit.',selectors:['[data-scw-research-surface="composition"]','[data-scw-composition-new]']}),
    Object.freeze({id:'review',label:'Review',number:'08',view:'activity',surface:'',external:false,actionLabel:'Open Review',purpose:'Inspect activity, lifecycle, history, changes, safety, and review context before release.',selectors:['[data-scw-workspace-view="activity"]','[data-scw-workspace-context-nav="review"]']}),
    Object.freeze({id:'export-handoff',label:'Export / Handoff',number:'09',view:'interoperability',surface:'',external:false,actionLabel:'Open Exchange',purpose:'Export or hand off selected work deliberately without silently changing the originating project.',selectors:['[data-scw-export]','[data-scw-share-export]','[data-scw-tool="lab"]']})
  ]);
  const now=()=>new Date().toISOString();
  function has(root,selector){try{return Boolean(root&&typeof root.querySelector==='function'&&root.querySelector(selector));}catch(_){return false;}}
  function availability(root){
    const out={};
    for(const step of STEPS){
      const routePresent=step.external?has(root,'a[href*="/knowledge-libraries/"]'):has(root,`[data-scw-workspace-view="${step.view}"]`);
      const surfacePresent=!step.surface||has(root,`[data-scw-research-surface="${step.surface}"]`);
      const actionPresent=step.selectors.some(selector=>has(root,selector));
      out[step.id]={routePresent,surfacePresent,actionPresent};
    }
    return out;
  }
  function assessSignals(signals={}){
    const checks=STEPS.map(step=>{
      const s=signals[step.id]||{};
      const pass=Boolean(s.routePresent&&s.surfacePresent!==false&&s.actionPresent);
      return {schema:CHECKPOINT_SCHEMA,id:step.id,label:step.label,number:step.number,state:pass?'ready':'attention',route:step.view,surface:step.surface||'',external:step.external,purpose:step.purpose,routePresent:Boolean(s.routePresent),surfacePresent:s.surfacePresent!==false,actionPresent:Boolean(s.actionPresent)};
    });
    const ready=checks.filter(x=>x.state==='ready').length;
    return {schema:SCHEMA,generatedAt:now(),state:ready===checks.length?'ready':'attention',ready,total:checks.length,checks,governance:{hiddenScore:false,automaticTelemetry:false,automaticSubmission:false,automaticMutation:false,automaticCompletion:false,behavioralTracking:false}};
  }
  function assess(root){return assessSignals(availability(root));}
  function cleanManual(raw){
    const reviewed={};
    for(const step of STEPS)reviewed[step.id]=Boolean(raw&&raw.reviewed&&raw.reviewed[step.id]);
    const count=Object.values(reviewed).filter(Boolean).length;
    return {schema:MANUAL_SCHEMA,reviewed,reviewedCount:count,total:STEPS.length,complete:count===STEPS.length,updatedAt:String(raw&&raw.updatedAt||'').slice(0,40),storage:'session-only'};
  }
  function readManual(storage){try{return cleanManual(JSON.parse(storage?.getItem?.(SESSION_KEY)||'null'));}catch(_){return cleanManual(null);}}
  function writeManual(storage,manual){const next=cleanManual({...manual,updatedAt:now()});next.updatedAt=now();try{storage?.setItem?.(SESSION_KEY,JSON.stringify(next));}catch(_){}return next;}
  function setReviewed(storage,id,value=true){const manual=readManual(storage);if(!STEPS.some(step=>step.id===id))return manual;manual.reviewed[id]=Boolean(value);manual.updatedAt=now();return writeManual(storage,manual);}
  function resetManual(storage){try{storage?.removeItem?.(SESSION_KEY);}catch(_){}return cleanManual(null);}
  function report(workspaceVersion,topology,manual){
    const t=topology&&topology.schema===SCHEMA?topology:assessSignals({});
    const m=cleanManual(manual);
    return {schema:REPORT_SCHEMA,workspaceVersion:String(workspaceVersion||'0.70.0').slice(0,40),generatedAt:now(),state:t.state==='attention'?'attention':(m.complete?'review-complete':'manual-review-pending'),topology:t,walkthrough:m,journey:STEPS.map(step=>({id:step.id,label:step.label,number:step.number,view:step.view,surface:step.surface,external:step.external,purpose:step.purpose})),privacy:{projectContentIncluded:false,objectTextIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{hiddenScore:false,automaticTelemetry:false,automaticMutation:false,automaticCompletion:false,behavioralTracking:false,manualReviewIsSessionOnly:true}};
  }
  function contract(){return {schema:SCHEMA,checkpointSchema:CHECKPOINT_SCHEMA,reportSchema:REPORT_SCHEMA,manualSchema:MANUAL_SCHEMA,stepCount:STEPS.length,steps:STEPS.map(step=>step.id),journey:'discover-capture-organize-analyze-synthesize-decide-compose-review-export-handoff',manualReviewStorage:'session-only',governance:{hiddenScore:false,automaticTelemetry:false,automaticSubmission:false,automaticMutation:false,automaticCompletion:false,behavioralTracking:false,canonicalMutation:false}};}
  return Object.freeze({SCHEMA,CHECKPOINT_SCHEMA,REPORT_SCHEMA,MANUAL_SCHEMA,SESSION_KEY,STEPS,availability,assessSignals,assess,readManual,setReviewed,resetManual,report,contract});
});
