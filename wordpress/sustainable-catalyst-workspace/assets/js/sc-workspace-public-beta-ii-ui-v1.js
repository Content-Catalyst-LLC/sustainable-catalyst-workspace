(()=>{
'use strict';
const download=(name,payload)=>{const blob=new Blob([JSON.stringify(payload,null,2)+'\n'],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),500);};
function init(){
 const root=document.querySelector('[data-sc-workspace]'),panel=root?.querySelector('[data-scw-public-beta-ii]'),helper=globalThis.SCWorkspacePublicBetaII;if(!root||!panel||!helper)return;
 const q=s=>panel.querySelector(s), list=q('[data-scw-beta-ii-checks]'), status=q('[data-scw-beta-ii-status]'), badge=q('[data-scw-beta-ii-badge]'); let latest=null;
 const run=()=>{const caps=helper.capability(window),routes=helper.routeHealth(root),rec=helper.recovery(window);latest=helper.assess({capabilities:caps,routeHealth:routes,recovery:rec,performanceAvailable:Boolean(globalThis.SCWorkspaceScalePerformance),securityAvailable:Boolean(globalThis.SCWorkspaceSecurityPrivacy),workspaceVersion:root.dataset.version,expectedVersion:'0.60.0',versionCurrent:root.dataset.version==='0.60.0'});const sum=helper.summary(latest);if(badge)badge.textContent=String(latest.state).toUpperCase();if(list){list.innerHTML='';latest.checks.forEach(item=>{const row=document.createElement('article');row.className=`scw-beta-ii-check is-${item.state}`;row.innerHTML=`<span>${item.state.toUpperCase()}</span><strong>${item.label}</strong><p>${item.detail}</p>`;if(item.route){const b=document.createElement('button');b.type='button';b.className='scw-card-action';b.textContent='Inspect';b.addEventListener('click',()=>root.querySelector(`[data-scw-workspace-view="${item.route}"]`)?.click());row.appendChild(b);}list.appendChild(row);});}if(status)status.textContent=`Beta gate: ${sum.ready}/${sum.total} checks ready${sum.attention?` · ${sum.attention} attention`:''}${sum.limited?` · ${sum.limited} limited`:''}. This is a checklist, not a readiness score.`;return latest;};
 q('[data-scw-beta-ii-run]')?.addEventListener('click',run);
 q('[data-scw-beta-ii-export]')?.addEventListener('click',()=>{const gate=latest||run();let diag=null;try{diag=globalThis.SCWorkspaceFieldDiagnostics?.diagnostic(root,window)||null;}catch(_){}download(`workspace-public-beta-ii-v${root.dataset.version}.json`,helper.fieldSnapshot(root.dataset.version,gate,diag));if(status)status.textContent='Privacy-minimized beta field snapshot exported locally. Nothing was submitted automatically.';});
 q('[data-scw-beta-ii-diagnostics]')?.addEventListener('click',()=>root.querySelector('[data-scw-open-field-diagnostics]')?.click());
 q('[data-scw-beta-ii-security]')?.addEventListener('click',()=>root.querySelector('[data-scw-workspace-view="security"]')?.click());
 run();
}
globalThis.SCWorkspacePublicBetaIIUI=Object.freeze({init});if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else setTimeout(init,0);
})();
