(function(){
  'use strict';
  function start(root){
    const section=root?.querySelector?.('[data-scw-production-certification]'),api=globalThis.SCWorkspaceProductionCertification;
    if(!root||!section||!api||section.dataset.scwProductionCertificationReady==='1')return;
    section.dataset.scwProductionCertificationReady='1';
    const q=s=>section.querySelector(s),compat=globalThis.SCWorkspaceBrowserCompatibility,version=String(root.dataset.version||''),badge=q('[data-scw-production-badge]'),status=q('[data-scw-production-status]'),checksEl=q('[data-scw-production-checks]'),manualEl=q('[data-scw-production-manual]');let latest=null;
    function download(name,payload){if(compat?.downloadJson)return compat.downloadJson(name,payload,window);try{const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);return{ok:true};}catch(error){return{ok:false,reason:String(error?.message||error)}}}
    function render(el,items,manual=false){if(!el)return;el.innerHTML='';items.forEach(item=>{const li=document.createElement('li'),flag=document.createElement('span'),body=document.createElement('div'),strong=document.createElement('strong'),p=document.createElement('p');flag.textContent=manual?'FIELD':String(item.state||'').toUpperCase();strong.textContent=item.label;p.textContent=item.detail||item.procedure||'';body.append(strong,p);li.append(flag,body);el.appendChild(li);});}
    function run(){latest=api.assess(root,{env:window,document});if(badge){badge.textContent=latest.packageAutomatedGate?'PACKAGE READY / FIELD PENDING':'PACKAGE BLOCKED';badge.classList.toggle('is-blocked',!latest.packageAutomatedGate);}render(checksEl,latest.checks,false);render(manualEl,latest.manualFieldItems,true);if(status)status.textContent=latest.packageAutomatedGate?`Packaged production gate passes. ${latest.manualFieldItems.length} live production checks remain unverified; production is not certified yet.`:`${latest.knownAutomatedBlockerCount} packaged production blocker(s) detected.`;return latest;}
    q('[data-scw-production-run]')?.addEventListener('click',run);
    q('[data-scw-production-export]')?.addEventListener('click',()=>{const out=download(`workspace-v${version}-production-certification-report.json`,api.report(version,run()));if(!out?.ok&&status)status.textContent=`Certification report export could not start (${out?.reason||'unknown error'}).`;});
    q('[data-scw-production-checklist]')?.addEventListener('click',()=>{const out=download(`workspace-v${version}-production-field-checklist.json`,api.checklist(version));if(!out?.ok&&status)status.textContent=`Production checklist export could not start (${out?.reason||'unknown error'}).`;});
    run();
  }
  const boot=()=>document.querySelectorAll('[data-sc-workspace]').forEach(start);if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
