(function(){
  'use strict';
  const helper=globalThis.SCWorkspaceBrowserCompatibility;if(!helper)return;
  function boot(root){
    if(!root||root.dataset.scwCompatibilityReady==='1')return;root.dataset.scwCompatibilityReady='1';
    const version=String(root.dataset.version||'');
    const section=root.querySelector('[data-scw-browser-compatibility]');
    const badge=root.querySelector('[data-scw-compat-badge]'),summary=root.querySelector('[data-scw-compat-summary]'),findings=root.querySelector('[data-scw-compat-findings]'),status=root.querySelector('[data-scw-compat-status]');
    const runButton=root.querySelector('[data-scw-compat-run]'),exportButton=root.querySelector('[data-scw-compat-export]'),matrixButton=root.querySelector('[data-scw-compat-export-matrix]');
    const viewportBinding=helper.applyViewport(root,window);let latest=null;
    function download(name,payload){const result=helper.downloadJson(name,payload,window);if(!result.ok&&status)status.textContent=`Export could not start (${result.reason}).`;
      return result;
    }
    function run(){
      const caps=helper.capability(window),matrix=helper.assess(caps);latest={caps,matrix};
      if(badge)badge.textContent=matrix.state.toUpperCase();
      if(summary)summary.innerHTML=`<div><span>BROWSER</span><strong>${caps.environment.browserFamily}</strong><small>${caps.environment.platformFamily}${caps.environment.embedded?' · embedded':''}</small></div><div><span>VIEWPORT</span><strong>${caps.viewport.deviceClass.toUpperCase()}</strong><small>${caps.viewport.width}×${caps.viewport.height} · ${caps.viewport.orientation}</small></div><div><span>IMPORT</span><strong>${String(caps.import.mode).replaceAll('-',' ').toUpperCase()}</strong><small>Feature-detected file-reading path.</small></div><div><span>EXPORT</span><strong>${String(caps.export.mode).replaceAll('-',' ').toUpperCase()}</strong><small>Client-side download path.</small></div>`;
      if(findings){findings.innerHTML='';matrix.findings.forEach(item=>{const row=document.createElement('article');row.className=`scw-compat-finding is-${item.state}`;row.innerHTML=`<span>${item.state.toUpperCase()}</span><div><strong>${item.label}</strong><p>${item.detail}</p>${item.fallback?`<small>Fallback: ${item.fallback}</small>`:''}</div>`;findings.appendChild(row);});}
      if(status)status.textContent=`Compatibility audit: ${matrix.summary.ready}/${matrix.summary.total} ready${matrix.summary.limited?` · ${matrix.summary.limited} limited`:''}${matrix.summary.attention?` · ${matrix.summary.attention} attention`:''}. Feature probes are local and do not transmit browser data.`;
      return latest;
    }
    runButton?.addEventListener('click',run);
    exportButton?.addEventListener('click',()=>{const r=run();download(`workspace-v${version}-browser-compatibility-report.json`,helper.report(version,r.caps,r.matrix));});
    matrixButton?.addEventListener('click',()=>download(`workspace-v${version}-compatibility-target-matrix.json`,helper.targetMatrix()));
    window.addEventListener('pageshow',()=>run());
    window.addEventListener('online',()=>run());window.addEventListener('offline',()=>run());
    run();if(section)section.dataset.scwCompatibilityInitialized='1';
    root.addEventListener('scw:dispose',()=>viewportBinding.dispose?.(),{once:true});
  }
  const start=()=>document.querySelectorAll('[data-sc-workspace]').forEach(boot);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
