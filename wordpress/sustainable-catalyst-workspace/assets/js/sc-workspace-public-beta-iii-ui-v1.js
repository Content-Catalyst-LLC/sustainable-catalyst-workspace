(function(){
  'use strict';
  function init(){
    const root=document.querySelector('[data-sc-workspace]'),section=root?.querySelector('[data-scw-public-beta-iii]'),api=globalThis.SCWorkspacePublicBetaIII;
    if(!root||!section||!api)return;
    const q=s=>section.querySelector(s),grid=q('[data-scw-beta-iii-grid]'),status=q('[data-scw-beta-iii-status]'),topologyBadge=q('[data-scw-beta-iii-topology]'),walkBadge=q('[data-scw-beta-iii-walkthrough]');
    let topology=null,manual=api.readManual(window.sessionStorage);
    function openStage(step){
      if(step.external){const link=root.querySelector('a[href*="/knowledge-libraries/"]');if(link){window.location.href=link.href;}return;}
      const route=root.querySelector(`[data-scw-workspace-view="${step.view}"]`);if(route)route.click();
      if(step.surface)setTimeout(()=>root.querySelector(`[data-scw-research-surface="${step.surface}"]`)?.click(),0);
    }
    function render(){
      topology=api.assess(root);manual=api.readManual(window.sessionStorage);
      if(topologyBadge)topologyBadge.textContent=`${topology.ready}/${topology.total} PATHS`;
      if(walkBadge)walkBadge.textContent=`${manual.reviewedCount}/${manual.total} REVIEWED`;
      if(grid){grid.innerHTML='';topology.checks.forEach(check=>{
        const step=api.STEPS.find(x=>x.id===check.id);const card=document.createElement('article');card.className='scw-beta-iii-step';card.dataset.state=check.state;
        const head=document.createElement('div');head.className='scw-beta-iii-step-head';head.innerHTML=`<span>${check.number}</span><div><strong>${check.label}</strong><small>${check.state==='ready'?'PATH AVAILABLE':'CHECK REQUIRED'}</small></div>`;
        const p=document.createElement('p');p.textContent=check.purpose;
        const facts=document.createElement('div');facts.className='scw-beta-iii-step-facts';facts.innerHTML=`<span>Route ${check.routePresent?'ready':'missing'}</span><span>Surface ${check.surfacePresent?'ready':'missing'}</span><span>Action ${check.actionPresent?'ready':'missing'}</span>`;
        const acts=document.createElement('div');acts.className='scw-beta-iii-step-actions';const open=document.createElement('button');open.type='button';open.className='scw-button';open.textContent=step?.actionLabel||'Open stage';open.addEventListener('click',()=>openStage(step));
        const mark=document.createElement('label');mark.className='scw-beta-iii-review-toggle';const box=document.createElement('input');box.type='checkbox';box.checked=Boolean(manual.reviewed[check.id]);box.addEventListener('change',()=>{manual=api.setReviewed(window.sessionStorage,check.id,box.checked);render();});const text=document.createElement('span');text.textContent='Reviewed in this session';mark.append(box,text);acts.append(open,mark);card.append(head,p,facts,acts);grid.appendChild(card);
      });}
      if(status)status.textContent=topology.state==='ready'?`All ${topology.total} product-journey paths are present. Manual walkthrough: ${manual.reviewedCount}/${manual.total} stages reviewed in this browser session. This is a checklist, not a productivity or readiness score.`:`${topology.ready}/${topology.total} product-journey paths are available. Review the attention items before treating Beta III as a coherent end-to-end product.`;
    }
    q('[data-scw-beta-iii-run]')?.addEventListener('click',render);
    q('[data-scw-beta-iii-reset]')?.addEventListener('click',()=>{manual=api.resetManual(window.sessionStorage);render();});
    q('[data-scw-beta-iii-start]')?.addEventListener('click',()=>root.querySelector('[data-scw-workspace-view="start"]')?.click());
    q('[data-scw-beta-iii-export]')?.addEventListener('click',()=>{topology=topology||api.assess(root);manual=api.readManual(window.sessionStorage);const payload=api.report(root.dataset.version||'0.70.0',topology,manual);const compat=globalThis.SCWorkspaceBrowserCompatibility;const out=compat?.downloadJson?.('sustainable-catalyst-workspace-public-beta-iii-journey.json',payload,window);if(status)status.textContent=out?.ok?'Beta III product-journey report exported. It contains topology and manual-review state only, not project content.':'The product-journey report could not be exported in this browser.';});
    root.querySelectorAll('[data-scw-open-product-journey]').forEach(button=>button.addEventListener('click',()=>root.querySelector('[data-scw-workspace-view="journey"]')?.click()));
    render();
  }
  globalThis.SCWorkspacePublicBetaIIIUI=Object.freeze({init});
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else setTimeout(init,0);
})();
