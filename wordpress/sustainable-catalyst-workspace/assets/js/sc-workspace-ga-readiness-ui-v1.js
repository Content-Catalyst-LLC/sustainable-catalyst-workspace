(function(global){
  'use strict';
  function init(){
    const root=document.querySelector('[data-scw-ga-readiness]');
    const api=global.SCWorkspaceGAReadiness;
    if(!root||!api)return;
    const grid=root.querySelector('[data-scw-ga-checks]'),owner=root.querySelector('[data-scw-ga-owner]'),url=root.querySelector('[data-scw-ga-url]'),attest=root.querySelector('[data-scw-ga-attest]'),status=root.querySelector('[data-scw-ga-status]'),badge=root.querySelector('[data-scw-ga-badge]'),evidence=root.querySelector('[data-scw-ga-signoff-evidence]');
    let record=api.load();
    function esc(v){return String(v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
    function cert(){return api.productionCertificate();}
    function renderEvidence(){const c=cert();const ok=api.validProductionCertificate(c);evidence.innerHTML='<strong>v0.83.0 production evidence</strong><span>'+(ok?('SIGNED OFF'+(c.signedAt?' · '+esc(c.signedAt):'')):'NOT YET VALID')+'</span><span>'+(ok?'The signed production certificate satisfies the prerequisite evidence boundary.':'Complete and sign the v0.83.0 Production Sign-Off record before this dossier can become READY.')+'</span>';}
    function renderChecks(){const c=cert();grid.innerHTML=api.REQUIREMENTS.map(r=>{const prerequisite=r.id==='production-signoff-certificate';const checked=prerequisite?api.validProductionCertificate(c):record.checks[r.id];return '<label class="scw-ga-readiness-check"><input type="checkbox" data-scw-ga-check="'+esc(r.id)+'" '+(checked?'checked':'')+' '+(prerequisite?'disabled':'')+'><span><strong>'+esc(r.label)+'</strong><span>'+esc(r.description)+'</span></span></label>';}).join('');}
    function syncFields(){owner.value=record.releaseOwner||'';url.value=record.productionUrl||'';attest.checked=record.attestation===true;renderEvidence();renderChecks();updateStatus();}
    function read(){record.releaseOwner=owner.value.trim();record.productionUrl=url.value.trim();record.attestation=attest.checked;root.querySelectorAll('[data-scw-ga-check]:not([disabled])').forEach(el=>record.checks[el.getAttribute('data-scw-ga-check')]=el.checked);record=api.save(record);updateStatus();}
    function updateStatus(message){const e=api.evaluate(record,cert());badge.textContent=e.ready?'READY':'HOLD';status.textContent=message||(e.ready&&record.recordedAt?('1.0 readiness decision recorded '+record.recordedAt+'.'):e.completedCount+' of '+e.requiredCount+' readiness requirements complete. Dossier remains on HOLD.');}
    function download(name,obj){const blob=new Blob([JSON.stringify(obj,null,2)+'\n'],{type:'application/json'});const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);}
    root.addEventListener('change',e=>{if(e.target.matches('[data-scw-ga-check],[data-scw-ga-owner],[data-scw-ga-url],[data-scw-ga-attest]'))read();});
    root.querySelector('[data-scw-ga-complete]').addEventListener('click',()=>{read();const result=api.complete(record,cert());record=result.record;if(!result.evaluation.ready){api.save(record);updateStatus('Readiness remains on HOLD: a signed v0.83.0 production certificate, every v0.84.0 readiness check, release owner, production URL, and final attestation are required.');return;}api.save(record);badge.textContent='READY';status.textContent='1.0 readiness decision recorded '+record.recordedAt+'. This does not publish or promote v1.0.0 automatically.';});
    root.querySelector('[data-scw-ga-export]').addEventListener('click',()=>{read();download('sustainable-catalyst-workspace-v0.84.0-1.0-readiness-dossier.json',api.dossier(record,cert()));updateStatus('1.0 readiness dossier exported. HOLD status remains explicit when any prerequisite is incomplete.');});
    root.querySelector('[data-scw-ga-reset]').addEventListener('click',()=>{record=api.clear();syncFields();updateStatus('Local readiness record reset. Production sign-off evidence and project data were not changed.');});
    syncFields();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})(window);
