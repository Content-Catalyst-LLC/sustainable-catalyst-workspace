(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.SCWorkspaceAuditTrail=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const TRAIL_SCHEMA='sc-workspace-audit-trail/1.0';
  const EVENT_SCHEMA='sc-workspace-audit-event/1.0';
  const EXPORT_SCHEMA='sc-workspace-audit-export/1.0';
  const SOURCES=['project-activity','version-history','account-recovery','cross-device-sync','safe-actions','reconciliation','collaboration','institutional-handoff','share','interoperability'];
  const SOURCE_LABELS={
    'project-activity':'Project activity','version-history':'Version history','account-recovery':'Account recovery','cross-device-sync':'Cross-device sync','safe-actions':'Safe Actions','reconciliation':'Reconciliation','collaboration':'Collaboration','institutional-handoff':'Institutional handoff','share':'Share & portability','interoperability':'Import & interoperability'
  };
  const iso=(v)=>{try{const d=new Date(v);return Number.isNaN(d.getTime())?'':d.toISOString();}catch(_){return '';}};
  const text=(v,n=240)=>String(v==null?'':v).slice(0,n);
  const event=(source,raw={})=>({
    schema:EVENT_SCHEMA,
    id:text(raw.id||`${source}:${raw.at||''}:${raw.action||raw.kind||''}`,180),
    source,
    sourceLabel:SOURCE_LABELS[source]||source,
    action:text(raw.action||raw.kind||'event',80),
    title:text(raw.title||raw.summary||raw.actionLabel||'Workspace event',220),
    detail:text(raw.detail||'',1600),
    projectId:text(raw.projectId||'',160),
    projectTitle:text(raw.projectTitle||'',220),
    actorLabel:text(raw.actorLabel||'',160),
    outcome:text(raw.outcome||raw.status||'',80),
    sourceRef:text(raw.sourceRef||raw.id||'',180),
    at:iso(raw.at)||new Date(0).toISOString(),
    derived:true,
    editable:false
  });
  const projectMap=(state)=>new Map((state.projects||[]).map(p=>[String(p.id||''),String(p.title||'Workspace project')]));
  function derive(state,options={}){
    const s=state&&typeof state==='object'?state:{}, projects=projectMap(s), out=[];
    const wanted=new Set(Array.isArray(options.sources)&&options.sources.length?options.sources:SOURCES);
    const projectId=text(options.projectId||'',160);
    const push=(source,raw)=>{if(!wanted.has(source))return;const e=event(source,raw);if(projectId&&e.projectId!==projectId)return;out.push(e);};
    if(wanted.has('project-activity'))(s.projects||[]).forEach(p=>(p.activity||[]).forEach(a=>push('project-activity',{id:a.id,action:a.type,title:a.summary,projectId:p.id,projectTitle:p.title,at:a.at,sourceRef:a.id})));
    (s.versionHistory?.history||[]).forEach(h=>push('version-history',{id:h.id,action:h.action,title:`${h.action==='create'?'Restore point created':h.action==='restore-copy'?'Restore point restored as copy':h.action==='verify'?'Restore point verified':h.action==='export'?'Restore point exported':h.action==='delete'?'Restore point deleted':'Version-history event'}${h.label?`: ${h.label}`:''}`,detail:h.label?`Restore point: ${h.label}`:'',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',at:h.at,sourceRef:h.restorePointId||h.id}));
    (s.accountPersistence?.history||[]).forEach(h=>push('account-recovery',{id:h.id,action:h.action,title:h.action==='backup'?'Account backup created':h.action==='restore'?'Account backup restored as copy':h.action==='delete'?'Account backup deleted':'Account backup index refreshed',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',at:h.at,sourceRef:h.id}));
    (s.crossDeviceSync?.history||[]).forEach(h=>push('cross-device-sync',{id:h.id,action:h.action,title:`Sync: ${String(h.action||'event').replaceAll('-',' ')}`,detail:h.revision?`Server revision ${h.revision}`:'',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.action==='conflict'?'conflict':'',at:h.at,sourceRef:h.id}));
    (s.safeActions?.history||[]).forEach(h=>push('safe-actions',{id:h.id,action:h.action,title:h.actionLabel||'Safe action',detail:`Outcome: ${h.outcome||'unknown'}${h.reviewAvailable?` · Reviewed ${Number(h.reviewSummary?.total||0)} explicit change(s)`:''}`,projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.outcome,at:h.at,sourceRef:h.id}));
    (s.reconciliation?.history||[]).forEach(h=>push('reconciliation',{id:h.id,action:'reconciled-copy',title:`Reconciled project created: ${h.outputProjectTitle||'Workspace project'}`,detail:`${Number(h.selectedChangeCount||0)} of ${Number(h.availableChangeCount||0)} changes selected${h.receiptId?` · receipt ${h.receiptId}`:''}`,projectId:h.sourceProjectId,projectTitle:h.sourceProjectTitle||projects.get(h.sourceProjectId)||'',actorLabel:h.reviewerLabel||'',outcome:'created',at:h.at,sourceRef:h.receiptId||h.id}));
    (s.reconciliation?.receipts||[]).forEach(r=>push('reconciliation',{id:`receipt:${r.id}`,action:'decision-receipt',title:'Reconciliation Decision Receipt',detail:`${Number(r.decision?.acceptedCount||0)} accepted · ${Number(r.decision?.declinedCount||0)} declined${r.decision?.rationale?` · ${text(r.decision.rationale,360)}`:''}`,projectId:r.source?.projectId||r.sourceProjectId||'',projectTitle:r.source?.projectTitle||r.sourceProjectTitle||projects.get(r.source?.projectId||r.sourceProjectId)||'',actorLabel:r.reviewerLabel||r.decision?.reviewerLabel||'',outcome:r.integrity?.fingerprint?'fingerprinted':'recorded',at:r.createdAt,sourceRef:r.id}));
    (s.collaboration?.history||[]).forEach(h=>push('collaboration',{id:h.id,action:`${h.direction||''}-${h.kind||''}`.replace(/^-|-$/g,''),title:h.kind==='response'?'Collaboration review response exchanged':'Collaboration review request exchanged',detail:h.fileName?`Package: ${h.fileName}${h.threadCount?` · ${h.threadCount} thread(s)`:''}`:'',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.direction||'',at:h.at,sourceRef:h.sessionId||h.id}));
    (s.institutional?.history||[]).forEach(h=>push('institutional-handoff',{id:h.id,action:h.kind||h.direction||'handoff',title:h.kind==='receipt'?'Institutional handoff receipt imported':'Institutional promotion package exported',detail:`${h.organizationLabel||'Catalyst Intelligence'}${h.status?` · ${h.status}`:''}`,projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.status||h.direction||'',at:h.at,sourceRef:h.handoffId||h.id}));
    (s.share?.history||[]).forEach(h=>push('share',{id:h.id,action:`${h.direction||''}-${h.kind||''}`.replace(/^-|-$/g,''),title:h.kind==='portable-project'?'Portable project exchanged':'Static review copy exported',detail:h.fileName?`File: ${h.fileName}`:'',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.direction||'',at:h.at,sourceRef:h.id}));
    (s.interoperability?.history||[]).forEach(h=>push('interoperability',{id:h.id,action:`${h.direction||''}-${h.format||''}`.replace(/^-|-$/g,''),title:`${h.direction==='import'?'Imported':'Exported'} ${String(h.format||'interchange').toUpperCase()} interoperability package`,detail:h.fileName?`File: ${h.fileName}${h.objectCount?` · ${h.objectCount} object(s)`:''}`:'',projectId:h.projectId,projectTitle:h.projectTitle||projects.get(h.projectId)||'',outcome:h.direction||'',at:h.at,sourceRef:h.id}));
    out.sort((a,b)=>new Date(b.at).getTime()-new Date(a.at).getTime()||a.id.localeCompare(b.id));
    const limit=Math.max(1,Math.min(1000,Number(options.limit)||500));
    return out.slice(0,limit);
  }
  function summary(events){const list=Array.isArray(events)?events:[], projects=new Set(),sources=new Set();list.forEach(e=>{if(e.projectId)projects.add(e.projectId);if(e.source)sources.add(e.source);});return {eventCount:list.length,projectCount:projects.size,sourceCount:sources.size,newestAt:list[0]?.at||null};}
  function exportPackage(events,meta={}){return {schema:EXPORT_SCHEMA,trailSchema:TRAIL_SCHEMA,generatedAt:new Date().toISOString(),filter:{projectId:text(meta.projectId||'',160),source:text(meta.source||'',80)},governance:{derivedFromAuthoritativeLedgers:true,storedShadowDatabase:false,hiddenScore:false,projectContentIncluded:false,editable:false},summary:summary(events),events:(events||[]).map(e=>({...e}))};}
  return {TRAIL_SCHEMA,EVENT_SCHEMA,EXPORT_SCHEMA,SOURCES,SOURCE_LABELS,derive,summary,exportPackage};
});
