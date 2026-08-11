(function(){
  'use strict';
  const helper=globalThis.SCWorkspacePersistenceIntegrity;if(!helper)return;
  function boot(root){
    if(!root||root.dataset.scwPersistenceIntegrityReady==='1')return;root.dataset.scwPersistenceIntegrityReady='1';
    const version=String(root.dataset.version||'');const section=root.querySelector('[data-scw-persistence-integrity]');if(!section)return;
    const badge=section.querySelector('[data-scw-pi-badge]'),metrics=section.querySelector('[data-scw-pi-metrics]'),findings=section.querySelector('[data-scw-pi-findings]'),status=section.querySelector('[data-scw-pi-status]');
    const runButton=section.querySelector('[data-scw-pi-run]'),exportCurrent=section.querySelector('[data-scw-pi-export-current]'),exportGood=section.querySelector('[data-scw-pi-export-good]'),exportDiag=section.querySelector('[data-scw-pi-export-diagnostic]'),historyButton=section.querySelector('[data-scw-pi-open-history]');
    const download=(name,payload)=>{const compat=globalThis.SCWorkspaceBrowserCompatibility;if(compat?.downloadJson)return compat.downloadJson(name,payload,window);const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);return {ok:true,mode:'legacy-object-url'};};
    function render(){
      helper.reconcileJournal(window.localStorage,{workspaceVersion:version,storageSchemaVersion:Number(root.dataset.storageVersion||0)});
      const a=helper.inspect(window.localStorage);if(badge)badge.textContent=a.state.toUpperCase();
      if(metrics)metrics.innerHTML=`<div><strong>${a.current.state.toUpperCase()}</strong><span>current state</span></div><div><strong>${a.metadata.state.toUpperCase().replaceAll('-',' ')}</strong><span>integrity baseline</span></div><div><strong>${a.lastGood.state.toUpperCase().replaceAll('-',' ')}</strong><span>last-known-good</span></div><div><strong>${a.transaction.state.toUpperCase().replaceAll('-',' ')}</strong><span>write journal</span></div>`;
      const rows=[];
      const add=(state,title,detail)=>rows.push({state,title,detail});
      add(a.current.state==='readable'?'ready':a.current.state==='missing'?'limited':'attention','Canonical state',a.current.state==='readable'?'Current browser-local Workspace state parses as a project collection.':a.current.state==='missing'?'No canonical Workspace state exists yet.':'Current Workspace state is unreadable; do not overwrite it before exporting a recovery candidate.');
      add(a.metadata.state==='verified'?'ready':a.metadata.state==='untracked'?'limited':'attention','Verified save baseline',a.metadata.state==='verified'?'Current bytes match the receipt written after the last verified save.':a.metadata.state==='untracked'?'No v0.62 integrity receipt exists yet; the next successful save will establish one.':'Current bytes no longer match the last verified-save receipt. Treat this as integrity drift until reviewed.');
      add(a.lastGood.state==='verified'?'ready':a.lastGood.available?'limited':'limited','Last-known-good snapshot',a.lastGood.state==='verified'?'The recovery snapshot is readable and checksum-bound.':a.lastGood.available?'A readable legacy recovery snapshot exists and remains usable.':'No readable last-known-good snapshot is available yet.');
      add(['clean','commit-visible','prewrite-visible'].includes(a.transaction.state)?'ready':['failed','interrupted'].includes(a.transaction.state)?'attention':'limited','Write transaction journal',a.transaction.state==='clean'?'No unresolved write transaction is present.':a.transaction.state==='failed'?'A save attempt failed and its journal was retained for diagnosis.':a.transaction.state==='interrupted'?'The current bytes match neither side of the last prepared write. Export recovery candidates before further destructive action.':'The journal can be reconciled safely without rewriting canonical research.');
      if(a.quarantine)add('limited','Quarantine copy','A previously isolated damaged Workspace payload is still present in the local recovery store.');
      if(findings){findings.innerHTML='';rows.forEach(item=>{const el=document.createElement('article');el.className=`scw-pi-finding is-${item.state}`;el.innerHTML=`<span>${item.state.toUpperCase()}</span><div><strong>${item.title}</strong><p>${item.detail}</p></div>`;findings.appendChild(el);});}
      if(status)status.textContent=`Persistence integrity: ${rows.filter(r=>r.state==='ready').length}/${rows.length} checks ready. No audit action rewrites canonical research.`;
      if(exportCurrent)exportCurrent.disabled=a.current.state==='missing';if(exportGood)exportGood.disabled=!a.lastGood.available;
      return a;
    }
    runButton?.addEventListener('click',render);
    exportCurrent?.addEventListener('click',()=>{const p=helper.recoveryCandidate(window.localStorage,'current',version);if(p)download(`workspace-v${version}-current-recovery-candidate.json`,p);});
    exportGood?.addEventListener('click',()=>{const p=helper.recoveryCandidate(window.localStorage,'last-known-good',version);if(p)download(`workspace-v${version}-last-known-good-recovery-candidate.json`,p);});
    exportDiag?.addEventListener('click',()=>download(`workspace-v${version}-persistence-integrity-report.json`,helper.diagnosticSnapshot(window.localStorage,version)));
    historyButton?.addEventListener('click',()=>{const b=root.querySelector('[data-scw-workspace-view="history"]');if(b)b.click();});
    render();
  }
  const start=()=>document.querySelectorAll('[data-sc-workspace]').forEach(boot);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
