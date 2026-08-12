(function(){
  'use strict';
  function init(){
    const root=document.querySelector('[data-sc-workspace]');
    const section=root&&root.querySelector('[data-scw-security-audit-ii]');
    const api=globalThis.SCWorkspaceSecurityPrivacyAuditII;
    if(!root||!section||!api)return;
    const q=s=>section.querySelector(s);
    let latest=null;
    function env(){return {protocol:location.protocol,isSecureContext:window.isSecureContext===true,topEqualsSelf:(()=>{try{return window.top===window.self;}catch(_){return false;}})(),cookieEnabled:navigator.cookieEnabled,crossOriginIsolated:window.crossOriginIsolated===true,referrerPresent:Boolean(document.referrer)};}
    function fmtBytes(n){const v=Number(n||0);return v>=1048576?`${(v/1048576).toFixed(2)} MB`:`${(v/1024).toFixed(1)} KB`;}
    function download(name,obj){const c=globalThis.SCWorkspaceBrowserCompatibility;if(c&&c.downloadJson)return c.downloadJson(name,obj,window);const blob=new Blob([JSON.stringify(obj,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;document.body.appendChild(a);a.click();setTimeout(()=>{URL.revokeObjectURL(a.href);a.remove();},0);}
    function render(){
      let local=null,session=null;try{local=window.localStorage;}catch(_){}try{session=window.sessionStorage;}catch(_){}
      latest=api.buildReport(local,session,env(),{cookieString:document.cookie,workspaceVersion:root.dataset.version||'',now:new Date().toISOString()});
      const set=(s,v)=>{const el=q(s);if(el)el.textContent=v;};
      set('[data-scw-sec2-local]',latest.storage.local.count);
      set('[data-scw-sec2-session]',latest.storage.session.count);
      set('[data-scw-sec2-bytes]',fmtBytes(latest.storage.local.bytes+latest.storage.session.bytes));
      set('[data-scw-sec2-unknown]',latest.storage.local.unknown+latest.storage.session.unknown);
      const f=q('[data-scw-sec2-findings]');if(f){f.innerHTML='';latest.findings.forEach(x=>{const li=document.createElement('li');li.className=`scw-sec2-${x.severity}`;const b=document.createElement('strong');b.textContent=x.code.replace(/-/g,' ');const s=document.createElement('span');s.textContent=x.message;li.append(b,s);f.appendChild(li);});}
      const g=q('[data-scw-sec2-gates]');if(g){g.innerHTML='';Object.entries(latest.releaseGates).forEach(([k,v])=>{const row=document.createElement('div');const b=document.createElement('strong');b.textContent=v?'PASS':'REVIEW';const s=document.createElement('span');s.textContent=k.replace(/([A-Z])/g,' $1').replace(/^./,c=>c.toUpperCase());row.append(b,s);g.appendChild(row);});}
      const b=q('[data-scw-sec2-browser]');if(b){b.innerHTML='';[['Secure context',latest.browser.secureContext],['HTTPS',latest.browser.https],['Embedded',latest.browser.embedded?'YES':'NO'],['Script-readable Workspace cookies',latest.cookies.accessibleWorkspaceCookieCount]].forEach(([label,value])=>{const row=document.createElement('div');const strong=document.createElement('strong');strong.textContent=String(value);const span=document.createElement('span');span.textContent=label;row.append(strong,span);b.appendChild(row);});}
      const status=q('[data-scw-sec2-status]');if(status)status.textContent='Audit II complete. Storage values, project content, URLs, query text, cookie names/values, account identity, and device identity were excluded from this report.';
    }
    q('[data-scw-sec2-run]')?.addEventListener('click',render);
    q('[data-scw-sec2-export]')?.addEventListener('click',()=>{if(!latest)render();download(`workspace-security-privacy-audit-ii-${new Date().toISOString().slice(0,10)}.json`,latest);const status=q('[data-scw-sec2-status]');if(status)status.textContent='Privacy-minimized Security & Privacy Audit II report exported. No Workspace storage values were included.';});
    render();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init,{once:true});else setTimeout(init,0);
})();
