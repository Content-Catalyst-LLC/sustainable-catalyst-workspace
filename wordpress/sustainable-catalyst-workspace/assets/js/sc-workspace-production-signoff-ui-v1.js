(function(global){
  'use strict';
  function init(){
    const root=document.querySelector('[data-scw-production-signoff]');
    const api=global.SCWorkspaceProductionSignoff;
    if(!root||!api)return;
    const grid=root.querySelector('[data-scw-signoff-checks]'),reviewer=root.querySelector('[data-scw-signoff-reviewer]'),url=root.querySelector('[data-scw-signoff-url]'),attest=root.querySelector('[data-scw-signoff-attest]'),status=root.querySelector('[data-scw-signoff-status]'),badge=root.querySelector('[data-scw-signoff-badge]');
    let record=api.load();
    function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
    function renderChecks(){grid.innerHTML=api.REQUIREMENTS.map(r=>'<label class="scw-production-signoff-check"><input type="checkbox" data-scw-signoff-check="'+esc(r.id)+'" '+(record.checks[r.id]?'checked':'')+'><span><strong>'+esc(r.label)+'</strong><span>'+esc(r.description)+'</span></span></label>').join('');}
    function syncFields(){reviewer.value=record.reviewerLabel||'';url.value=record.productionUrl||'';attest.checked=record.attestation===true;renderChecks();updateStatus();}
    function read(){record.reviewerLabel=reviewer.value.trim();record.productionUrl=url.value.trim();record.attestation=attest.checked;root.querySelectorAll('[data-scw-signoff-check]').forEach(el=>record.checks[el.getAttribute('data-scw-signoff-check')]=el.checked);record=api.save(record);updateStatus();}
    function updateStatus(message){const e=api.evaluate(record);badge.textContent=e.complete?'READY TO SIGN':'PENDING';status.textContent=message||((record.signedAt&&e.complete)?('Production sign-off recorded '+record.signedAt+'.'):e.completedCount+' of '+e.requiredCount+' live checks attested. Sign-off remains pending.');}
    function download(name,obj){const blob=new Blob([JSON.stringify(obj,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);}
    root.addEventListener('change',e=>{if(e.target.matches('[data-scw-signoff-check],[data-scw-signoff-reviewer],[data-scw-signoff-url],[data-scw-signoff-attest]'))read();});
    root.querySelector('[data-scw-signoff-complete]').addEventListener('click',()=>{read();const result=api.complete(record);record=result.record;if(!result.evaluation.complete){api.save(record);updateStatus('Sign-off blocked: complete every field check, reviewer label, production URL, and final attestation.');return;}api.save(record);badge.textContent='SIGNED OFF';status.textContent='Production sign-off recorded '+record.signedAt+'. Export the certificate and retain it with the release evidence.';});
    root.querySelector('[data-scw-signoff-export]').addEventListener('click',()=>{read();download('sustainable-catalyst-workspace-v0.83.0-production-signoff.json',api.certificate(record));updateStatus('Production sign-off certificate exported. Pending checks remain visible in the certificate if sign-off is incomplete.');});
    root.querySelector('[data-scw-signoff-reset]').addEventListener('click',()=>{record=api.clear();syncFields();updateStatus('Local production sign-off evidence reset. No project data was touched.');});
    syncFields();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})(window);
