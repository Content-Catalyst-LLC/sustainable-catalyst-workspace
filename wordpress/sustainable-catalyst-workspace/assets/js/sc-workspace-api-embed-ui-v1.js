(function(){
'use strict';
const WORKSPACE_KEY='sc_workspace';
const parse=(k,f)=>{try{const x=JSON.parse(localStorage.getItem(k)||'null');return x&&typeof x==='object'?x:f;}catch(_){return f;}};
const save=(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v));return true;}catch(_){return false;}};
const esc=v=>String(v??'').replace(/[&<>'"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
const uid=()=>`projection-${window.crypto?.randomUUID?.()||`${Date.now()}-${Math.random().toString(16).slice(2)}`}`;
async function sha256(s){const value=String(s);if(window.crypto?.subtle){const data=new TextEncoder().encode(value),h=await crypto.subtle.digest('SHA-256',data);return `sha256:${[...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,'0')).join('')}`;}let h=2166136261;for(let i=0;i<value.length;i++){h^=value.charCodeAt(i);h=Math.imul(h,16777619);}return `fnv1a32:${(h>>>0).toString(16).padStart(8,'0')}`;}
const download=(name,data,type='application/json')=>{const body=typeof data==='string'?data:JSON.stringify(data,null,2)+'\n',blob=new Blob([body],{type}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);};
function init(){
 const root=document.querySelector('[data-scw-api-embed]'),A=window.SCWorkspaceApiEmbed,I=window.SCWorkspaceIntegratedKnowledge;if(!root||!A||!I)return;
 const q=s=>root.querySelector(s),state=()=>parse(WORKSPACE_KEY,{projects:[]}),records=()=>I.derive(state()).filter(e=>!e.projectArchived),select=q('[data-scw-api-record]'),summary=q('[data-scw-api-summary]'),tags=q('[data-scw-api-tags]'),prov=q('[data-scw-api-provenance]'),content=q('[data-scw-api-content]'),create=q('[data-scw-api-create]'),list=q('[data-scw-api-list]'),preview=q('[data-scw-api-preview]'),refOut=q('[data-scw-api-reference]'),apiOut=q('[data-scw-api-json]'),embedOut=q('[data-scw-api-html]'),status=q('[data-scw-api-status]'),exportJson=q('[data-scw-api-export-json]'),copyRef=q('[data-scw-api-copy-ref]'),copyEmbed=q('[data-scw-api-copy-embed]'),deleteBtn=q('[data-scw-api-delete]');
 let ledger=A.normalizeLedger(parse(A.STORAGE_KEY,{})),activeId=ledger.projections[0]?.id||'';
 const rendererUrl=()=>root.dataset.rendererUrl||'';
 function persist(){save(A.STORAGE_KEY,ledger);}
 function active(){return ledger.projections.find(p=>p.id===activeId)||null;}
 function fill(){const old=select.value;select.innerHTML='<option value="">Choose canonical research</option>'+records().map(e=>`<option value="${esc(e.key)}">${esc(e.projectTitle)} · ${esc(e.kind)} · ${esc(e.title)}</option>`).join('');if(records().some(e=>e.key===old))select.value=old;}
 function renderList(){list.innerHTML=ledger.projections.length?ledger.projections.map(p=>`<button type="button" class="scw-api-row${p.id===activeId?' is-active':''}" data-id="${esc(p.id)}"><span>PUBLIC READ-ONLY</span><strong>${esc(p.data.title)}</strong><small>${esc(p.durableRef.uri)}</small></button>`).join(''):'<div class="scw-api-empty">No explicit projections created yet.</div>';list.querySelectorAll('[data-id]').forEach(b=>b.onclick=()=>{activeId=b.dataset.id;render();});}
 function renderActive(){const p=active(),desc=p?A.embedDescriptor(p,document.querySelector('[data-sc-workspace]')?.dataset.version||'0.55.0',rendererUrl()):null,env=p?A.apiEnvelope(p,document.querySelector('[data-sc-workspace]')?.dataset.version||'0.55.0'):null,html=desc?A.embedHtml(desc,rendererUrl()):'';refOut.textContent=p?.durableRef.uri||'No projection selected.';apiOut.textContent=env?JSON.stringify(env,null,2):'No API envelope selected.';embedOut.value=html;preview.innerHTML='';if(desc)A.renderElement(preview,desc);else preview.innerHTML='<div class="scw-api-empty">Create or select a projection to preview its read-only embed.</div>';exportJson.disabled=!p;copyRef.disabled=!p;copyEmbed.disabled=!p;deleteBtn.disabled=!p;}
 function render(){fill();renderList();renderActive();}
 create.onclick=async()=>{const e=records().find(x=>x.key===select.value);if(!e){status.textContent='Choose a canonical research record first.';return;}const fields={summary:summary.checked,tags:tags.checked,provenance:prov.checked,content:content.checked};let p=A.createProjection(e,{fields},()=>new Date().toISOString(),uid);if(!p)return;const fp=await sha256(A.fingerprintPayload(p));p=A.withFingerprint(p,fp);ledger=A.upsert(ledger,p);activeId=p.id;persist();status.textContent='Explicit public-readonly projection created locally. Canonical Workspace research was not changed or uploaded.';render();};
 exportJson.onclick=()=>{const p=active();if(!p)return;download(`workspace-readonly-api-${p.id}.json`,A.apiEnvelope(p,document.querySelector('[data-sc-workspace]')?.dataset.version||'0.55.0'));status.textContent='Static read-only API envelope exported.';};
 copyRef.onclick=async()=>{const p=active();if(!p)return;await navigator.clipboard?.writeText(p.durableRef.uri);status.textContent='Durable reference copied. It identifies the record but grants no access.';};
 copyEmbed.onclick=async()=>{if(!embedOut.value)return;await navigator.clipboard?.writeText(embedOut.value);status.textContent='Static embed HTML copied. The copied payload contains exactly the fields shown in the projection.';};
 deleteBtn.onclick=()=>{if(!activeId)return;ledger=A.remove(ledger,activeId);activeId=ledger.projections[0]?.id||'';persist();status.textContent='Projection removed from this browser. Canonical research was unchanged.';render();};
 render();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else init();
})();
