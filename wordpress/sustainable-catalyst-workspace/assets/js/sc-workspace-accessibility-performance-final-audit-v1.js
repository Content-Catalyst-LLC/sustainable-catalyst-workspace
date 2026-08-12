(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceAccessibilityPerformanceFinalAudit=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-accessibility-performance-final-audit/1.0';
  const REPORT_SCHEMA='sc-workspace-accessibility-performance-final-audit-report/1.0';
  const CHECKLIST_SCHEMA='sc-workspace-accessibility-performance-final-checklist/1.0';
  const TARGET='WCAG 2.2 AA + bounded field-performance budgets';
  const BUDGETS=Object.freeze({
    domAttention:7000,
    domCritical:10000,
    interactiveAttention:1500,
    renderP95AttentionMs:32,
    renderP95CriticalMs:100,
    indexP95AttentionMs:250,
    indexP95CriticalMs:1000,
    longTaskAttentionCount:1,
    longTaskCriticalCount:5,
    heapAttentionRatio:.72,
    heapCriticalRatio:.90
  });
  const stamp=()=>new Date().toISOString();
  const finite=v=>Number.isFinite(Number(v))?Number(v):0;
  const clean=(v,max=180)=>String(v==null?'':v).replace(/\s+/g,' ').trim().slice(0,max);
  function item(id,category,state,label,detail,manual=false){return{id,category,state,label,detail:clean(detail,420),manual:Boolean(manual)};}
  function accessibleName(el,doc){
    if(!el)return'';
    const aria=clean(el.getAttribute?.('aria-label')||'',200);if(aria)return aria;
    const labelled=clean(el.getAttribute?.('aria-labelledby')||'',200);if(labelled&&doc?.getElementById){const names=labelled.split(/\s+/).map(id=>clean(doc.getElementById(id)?.textContent||'',200)).filter(Boolean);if(names.length)return names.join(' ');}
    const id=el.id;if(id&&doc?.querySelector){const label=doc.querySelector(`label[for="${String(id).replace(/"/g,'\\"')}"]`);if(label)return clean(label.textContent,200);}
    const wrap=el.closest?.('label');if(wrap)return clean(wrap.textContent,200);
    if(el.tagName==='INPUT'&&String(el.type||'').toLowerCase()==='image')return clean(el.alt||'',200);
    return clean(el.textContent||el.value||el.title||'',200);
  }
  function visible(el){if(!el||el.hidden||el.disabled||el.getAttribute?.('aria-hidden')==='true')return false;return !(el.closest&&el.closest('[hidden],[aria-hidden="true"]'));}
  function duplicateIds(root){const seen=new Set(),dupes=new Set();for(const el of (root?.querySelectorAll?.('[id]')||[])){const id=String(el.id||'').trim();if(!id)continue;if(seen.has(id))dupes.add(id);else seen.add(id);}return[...dupes];}
  function unnamedInteractive(root){const doc=root?.ownerDocument||globalThis.document,selectors='button,a[href],input:not([type="hidden"]),select,textarea,[role="button"],[role="link"],[role="tab"],[role="menuitem"]';return [...(root?.querySelectorAll?.(selectors)||[])].filter(visible).filter(el=>!accessibleName(el,doc));}
  function structuralAccessibility(root,env=globalThis,engine){
    const out=[];let base=null;
    if(engine&&typeof engine.audit==='function'){
      try{base=engine.audit(root,env);}catch(_){base=null;}
    }
    if(base?.findings){for(const f of base.findings){const state=f.state==='ready'?'pass':f.state==='attention'?'blocked':'manual';out.push(item(`a11y-${f.id}`,'accessibility',state,f.label,f.detail,f.manual));}}
    else out.push(item('a11y-engine','accessibility','blocked','Accessibility engine','The v0.64 accessibility audit runtime is unavailable.'));
    const dupes=duplicateIds(root);out.push(item('duplicate-ids','accessibility',dupes.length?'blocked':'pass','Unique DOM identifiers',dupes.length?`${dupes.length} duplicate id value(s) were detected in the Workspace root.`:'No duplicate DOM id values were detected in the Workspace root.'));
    const unnamed=unnamedInteractive(root);out.push(item('interactive-names','accessibility',unnamed.length?'blocked':'pass','Interactive accessible names',unnamed.length?`${unnamed.length} visible interactive control(s) have no detectable accessible name.`:'Every detected visible interactive control has a detectable accessible name.'));
    const doc=root?.ownerDocument||env?.document;const lang=clean(doc?.documentElement?.getAttribute?.('lang')||'',40);out.push(item('document-language','accessibility',lang?'pass':'attention','Document language',lang?`Host document language is declared as ${lang}.`:'The host document does not expose a language declaration in this fixture/context. Verify the production WordPress document language.'));
    return out;
  }
  function performanceFindings(root,summary){
    const out=[],nodes=root?.querySelectorAll?.('*')?.length||0,interactive=root?.querySelectorAll?.('button,a[href],input,select,textarea,[tabindex],[role="button"],[role="tab"]')?.length||0;
    const nodeState=nodes>=BUDGETS.domCritical?'blocked':nodes>=BUDGETS.domAttention?'attention':'pass';out.push(item('dom-size','performance',nodeState,'Workspace DOM size',`${nodes.toLocaleString()} descendant nodes detected; attention begins at ${BUDGETS.domAttention.toLocaleString()} and the audit blocks at ${BUDGETS.domCritical.toLocaleString()}.`));
    out.push(item('interactive-density','performance',interactive>=BUDGETS.interactiveAttention?'attention':'pass','Interactive-control density',`${interactive.toLocaleString()} interactive/focusable candidates are present; attention begins at ${BUDGETS.interactiveAttention.toLocaleString()}.`));
    if(!summary){out.push(item('session-profile','performance','manual','Long-session performance profile','No active long-session profile was available. Run the Performance session profile during representative work before release.',true));return out;}
    const rp95=finite(summary.render?.p95Ms),ip95=finite(summary.index?.p95Ms),longs=finite(summary.counters?.longTaskCount),heap=summary.memory?.supported?finite(summary.memory.ratio):null;
    const rstate=rp95>=BUDGETS.renderP95CriticalMs?'blocked':rp95>=BUDGETS.renderP95AttentionMs?'attention':'pass';out.push(item('render-p95','performance',rstate,'Render p95',`${rp95.toFixed(1)} ms p95; attention ${BUDGETS.renderP95AttentionMs} ms, block ${BUDGETS.renderP95CriticalMs} ms.`));
    const istate=ip95>=BUDGETS.indexP95CriticalMs?'blocked':ip95>=BUDGETS.indexP95AttentionMs?'attention':'pass';out.push(item('index-p95','performance',istate,'Derived-index p95',`${ip95.toFixed(1)} ms p95; attention ${BUDGETS.indexP95AttentionMs} ms, block ${BUDGETS.indexP95CriticalMs} ms.`));
    const lstate=longs>=BUDGETS.longTaskCriticalCount?'blocked':longs>=BUDGETS.longTaskAttentionCount?'attention':'pass';out.push(item('long-tasks','performance',lstate,'Long tasks',`${longs} observed task(s) at or above the 50 ms long-task threshold in this bounded session sample.`));
    if(heap==null)out.push(item('heap-pressure','performance','manual','Heap pressure','Portable heap measurement is unavailable in this browser; verify representative long-session behavior manually.',true));
    else{const hstate=heap>=BUDGETS.heapCriticalRatio?'blocked':heap>=BUDGETS.heapAttentionRatio?'attention':'pass';out.push(item('heap-pressure','performance',hstate,'Heap pressure',`${(heap*100).toFixed(0)}% of the browser-reported JavaScript heap limit is in use.`));}
    return out;
  }
  function summarize(findings){const summary={pass:0,attention:0,blocked:0,manual:0,total:findings.length};for(const f of findings){if(summary[f.state]!=null)summary[f.state]++;}return summary;}
  function run(root,options={}){
    const env=options.env||globalThis,accessibilityEngine=options.accessibilityEngine||env.SCWorkspaceAccessibility||null,performanceSummary=options.performanceSummary||null;
    const findings=[...structuralAccessibility(root,env,accessibilityEngine),...performanceFindings(root,performanceSummary)];const summary=summarize(findings);const automatedReleaseGate=summary.blocked===0;
    const state=!automatedReleaseGate?'blocked':summary.attention?'attention':summary.manual?'manual-review':'ready';
    return{schema:SCHEMA,generatedAt:stamp(),target:TARGET,state,automatedReleaseGate,summary,findings,budgets:{...BUDGETS},claimBoundary:'Automated release gates can block structural accessibility or critical performance regressions. Manual screen-reader, measured contrast, zoom/reflow, touch-device, and representative long-session verification remain required before any accessibility or performance certification claim.',governance:{manualFieldAuditRequired:true,automatedCertification:false,hiddenScore:false,canonicalMutation:false,automaticRepair:false,automaticOptimization:false,automaticDeletion:false,automaticUpload:false,telemetry:false}};
  }
  function report(workspaceVersion,result){const r=result||{summary:{},findings:[]};return{schema:REPORT_SCHEMA,generatedAt:stamp(),workspaceVersion:clean(workspaceVersion,40),target:TARGET,assessment:r,privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,queryTextIncluded:false,accountIdentityIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{manualFieldAuditRequired:true,automatedCertification:false,canonicalMutation:false,automaticRepair:false,automaticOptimization:false,automaticUpload:false,telemetry:false,hiddenScore:false}};}
  function checklist(){return{schema:CHECKLIST_SCHEMA,target:TARGET,claimBoundary:'This field checklist complements automated gates; completion by qualified human reviewers is required before any conformance/certification claim.',requiredManualChecks:[
    {id:'keyboard-end-to-end',category:'accessibility',label:'Keyboard-only complete workflow',procedure:'Complete Start → Project → Research → Review → Exchange without a pointer; verify no unreachable control, unexpected trap, or lost focus.'},
    {id:'screen-reader-voiceover',category:'accessibility',label:'VoiceOver + Safari',procedure:'Verify landmarks, headings, names/states, live regions, dialogs, table/list reading, and complete core workflows.'},
    {id:'screen-reader-windows',category:'accessibility',label:'Windows screen reader',procedure:'Verify at least NVDA or Narrator with Edge/Firefox across the same core workflow.'},
    {id:'contrast-measured',category:'accessibility',label:'Measured contrast',procedure:'Measure text, controls, selected states, focus indicators, alerts, and essential graphics against WCAG 2.2 AA.'},
    {id:'zoom-200',category:'accessibility',label:'200% zoom',procedure:'Verify no loss of content or functionality at 200% browser zoom.'},
    {id:'reflow-400',category:'accessibility',label:'400% / 320 CSS px reflow',procedure:'Verify primary workflows reflow without two-dimensional page scrolling except intrinsically two-dimensional content.'},
    {id:'forced-colors',category:'accessibility',label:'Forced colors / high contrast',procedure:'Verify focus, boundaries, selection, warnings, and status do not rely on color alone.'},
    {id:'reduced-motion',category:'accessibility',label:'Reduced motion',procedure:'Verify navigation, scrolling, dialogs, and dynamic surfaces remain usable with reduced motion enabled.'},
    {id:'touch-tablet',category:'accessibility',label:'Tablet touch operation',procedure:'Verify primary actions and dismiss controls on a physical coarse-pointer tablet-class device.'},
    {id:'long-session-4h',category:'performance',label:'Representative four-hour session',procedure:'Use a representative large project for at least four hours; inspect render/index p95, long tasks, memory trend, and route responsiveness.'},
    {id:'large-project',category:'performance',label:'Very large project',procedure:'Exercise a representative high-object/high-notebook project and confirm bounded lists, derived caches, graph/research navigation, import/export, and recovery remain responsive.'},
    {id:'low-resource',category:'performance',label:'Lower-resource browser/device',procedure:'Verify core workflows on a lower-resource supported device/browser without destructive memory pressure or persistent interface stalls.'},
    {id:'background-foreground',category:'performance',label:'Background/foreground lifecycle',procedure:'Background and restore the tab repeatedly; confirm BFCache/page lifecycle handling does not duplicate observers, handlers, or session samples.'},
    {id:'production-wordpress',category:'combined',label:'Production WordPress smoke test',procedure:'Run the final audit on the deployed WordPress page and verify the page reaches the site footer with no PHP/JS critical error.'}
  ],governance:{manualReviewRequired:true,automatedCertification:false,canonicalMutation:false,automaticOptimization:false,telemetry:false}};}
  function contract(){return{schema:SCHEMA,reportSchema:REPORT_SCHEMA,checklistSchema:CHECKLIST_SCHEMA,target:TARGET,budgets:{...BUDGETS},features:{combinedAccessibilityPerformanceAudit:true,criticalAutomatedGate:true,manualFieldChecklist:true,privacyMinimizedReport:true,existingAccessibilityEngineReused:true,existingLongSessionMonitorReused:true},governance:{manualFieldAuditRequired:true,automatedCertification:false,hiddenScore:false,canonicalMutation:false,automaticRepair:false,automaticOptimization:false,automaticDeletion:false,automaticUpload:false,telemetry:false,schemaMigrationRequired:false,storageSchemaVersion:35,projectSchema:'sc-workspace-project/20.0'}};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,CHECKLIST_SCHEMA,TARGET,BUDGETS,clean,accessibleName,duplicateIds,unnamedInteractive,structuralAccessibility,performanceFindings,summarize,run,report,checklist,contract});
});
