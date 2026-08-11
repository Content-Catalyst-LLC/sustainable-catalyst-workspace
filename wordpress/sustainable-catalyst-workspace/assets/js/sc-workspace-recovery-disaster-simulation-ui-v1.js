(function(){
  'use strict';
  function init(){
    const root=document.querySelector('[data-sc-workspace]'),section=root&&root.querySelector('[data-scw-recovery-drills]'),api=window.SCWorkspaceRecoveryDisasterSimulation;if(!root||!section||!api)return;
    const q=s=>section.querySelector(s),deps=()=>({workspaceVersion:root.dataset.version||'0.71.0',persistence:window.SCWorkspacePersistenceIntegrity||null,compatibility:window.SCWorkspaceImportExportCompatibility||null,continuity:window.SCWorkspaceCrossDeviceContinuity||null});
    let last=null;
    function render(report){last=report;const badge=q('[data-scw-recovery-drills-badge]');if(badge)badge.textContent=report.state==='pass'?'PASS':'ATTENTION';const status=q('[data-scw-recovery-drills-status]');if(status)status.textContent=`Recovery drill suite: ${report.passed}/${report.total} scenarios passed. Simulations use isolated in-memory fixtures and do not inject failures into canonical Workspace data.`;const grid=q('[data-scw-recovery-drills-grid]');if(!grid)return;grid.innerHTML='';report.scenarios.forEach(s=>{const card=document.createElement('article');card.className='scw-recovery-drill-card';card.dataset.state=s.result.pass?'pass':'fail';const h=document.createElement('h3');h.textContent=s.label;const p=document.createElement('p');p.textContent=s.goal;const r=document.createElement('p');r.className='scw-recovery-drill-result';r.textContent=`${s.result.pass?'PASS':'ATTENTION'} — observed: ${s.result.observed}; expected: ${s.result.expected}.`;card.append(h,p,r);grid.appendChild(card);});}
    function run(){render(api.runAll(deps()));}
    q('[data-scw-recovery-drills-run]')?.addEventListener('click',run);
    q('[data-scw-recovery-drills-export]')?.addEventListener('click',()=>{if(!last)run();const out=window.SCWorkspaceBrowserCompatibility?.downloadJson?.('sustainable-catalyst-workspace-recovery-drills.json',last),status=q('[data-scw-recovery-drills-status]');if(status)status.textContent=out?.ok?'Recovery drill report exported. It contains scenario outcomes and policy metadata, not project content.':'Recovery drill report could not be exported in this browser.';});
    run();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else setTimeout(init,0);
})();
