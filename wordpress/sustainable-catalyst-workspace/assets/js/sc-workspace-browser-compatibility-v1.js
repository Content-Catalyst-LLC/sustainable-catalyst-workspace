(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceBrowserCompatibility=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-browser-compatibility/1.0';
  const MATRIX_SCHEMA='sc-workspace-browser-compatibility-matrix/1.0';
  const REPORT_SCHEMA='sc-workspace-browser-compatibility-report/1.0';
  const TARGET_SCHEMA='sc-workspace-browser-targets/1.0';
  const MAX_DATA_URI_BYTES=1024*1024;
  const text=(v,max=240)=>String(v==null?'':v).trim().slice(0,max);
  const now=()=>new Date().toISOString();
  const bytes=(value)=>{try{return new TextEncoder().encode(String(value==null?'':value)).length;}catch(_){return unescape(encodeURIComponent(String(value==null?'':value))).length;}};
  function safeProperty(object,key){try{return object?object[key]:undefined;}catch(_){return undefined;}}
  function touchCapable(win,nav=win.navigator||{}){return Number(nav.maxTouchPoints||0)>0||'ontouchstart' in win;}
  function storageProbe(storage,key){
    const result={available:false,writable:false,reason:'unavailable'};
    if(!storage||typeof storage.getItem!=='function'||typeof storage.setItem!=='function')return result;
    try{const old=storage.getItem(key),token=`${Date.now()}-${Math.random()}`;storage.setItem(key,token);result.available=true;result.writable=storage.getItem(key)===token;result.reason=result.writable?'ready':'readback-mismatch';if(old===null)storage.removeItem(key);else storage.setItem(key,old);}catch(error){result.reason=text(error?.name||error?.message||'blocked',80);}
    return result;
  }
  function browserFamily(ua=''){
    const s=String(ua||'');
    if(/Edg\//.test(s))return 'Edge';
    if(/Firefox\//.test(s)||/FxiOS\//.test(s))return 'Firefox';
    if(/CriOS\//.test(s))return 'Chrome iOS';
    if(/Chrome\//.test(s)||/Chromium\//.test(s))return 'Chrome / Chromium';
    if(/Safari\//.test(s)&&/Version\//.test(s))return 'Safari';
    return 'Other / unknown';
  }
  function platformFamily(nav={}){
    const ua=String(nav.userAgent||''),platform=String(nav.platform||'');
    if(/iPad|iPhone|iPod/.test(ua)||(/Mac/.test(platform)&&Number(nav.maxTouchPoints||0)>1))return 'iOS / iPadOS';
    if(/Android/.test(ua))return 'Android';
    if(/Win/.test(platform)||/Windows/.test(ua))return 'Windows';
    if(/Mac/.test(platform)||/Macintosh/.test(ua))return 'macOS';
    if(/Linux/.test(platform)||/Linux/.test(ua))return 'Linux';
    return 'Other / unknown';
  }
  function viewport(env=globalThis){
    const win=env.window||env,doc=win.document||{},vv=win.visualViewport;
    const width=Math.max(0,Math.round(Number(vv?.width||win.innerWidth||doc.documentElement?.clientWidth||0)));
    const height=Math.max(0,Math.round(Number(vv?.height||win.innerHeight||doc.documentElement?.clientHeight||0)));
    const deviceClass=width&&width<680?'compact':width&&width<1024?'tablet':'desktop';
    return {width,height,deviceClass,orientation:width&&height?(width>=height?'landscape':'portrait'):'unknown',visualViewport:Boolean(vv)};
  }
  function embedded(env=globalThis){
    const win=env.window||env;
    try{return Boolean(win.self&&win.top&&win.self!==win.top);}catch(_){return true;}
  }
  function capability(env=globalThis){
    const win=env.window||env,nav=win.navigator||{},doc=win.document||{};
    const local=storageProbe(safeProperty(win,'localStorage'),'__scw_compat_local__');
    const session=storageProbe(safeProperty(win,'sessionStorage'),'__scw_compat_session__');
    const filePrototype=win.File&&win.File.prototype;
    const fileText=Boolean(filePrototype&&typeof filePrototype.text==='function');
    const fileReader=typeof win.FileReader==='function';
    const blob=typeof win.Blob==='function';
    const objectUrl=Boolean(win.URL&&typeof win.URL.createObjectURL==='function'&&typeof win.URL.revokeObjectURL==='function');
    const anchorDownload=(()=>{try{return 'download' in doc.createElement('a');}catch(_){return false;}})();
    const historyApi=Boolean(win.history&&typeof win.history.pushState==='function'&&typeof win.history.replaceState==='function');
    const resizeObserver=typeof win.ResizeObserver==='function';
    const requestAnimationFrame=typeof win.requestAnimationFrame==='function';
    const cssSupports=Boolean(win.CSS&&typeof win.CSS.supports==='function');
    const webCryptoSha256=Boolean(win.crypto?.subtle&&typeof win.crypto.subtle.digest==='function');
    const structuredClone=typeof win.structuredClone==='function';
    const pointerEvents='PointerEvent' in win;
    const touch=touchCapable(win,nav);
    const vp=viewport(win);
    return {
      schema:SCHEMA,
      generatedAt:now(),
      environment:{browserFamily:browserFamily(nav.userAgent),platformFamily:platformFamily(nav),embedded:embedded(win),online:typeof nav.onLine==='boolean'?nav.onLine:null,language:text(nav.language,40)},
      viewport:vp,
      storage:{local,session},
      navigation:{historyApi,mode:historyApi?'history-api':'in-app-only'},
      import:{fileApi:Boolean(win.File),fileText,fileReader,mode:fileText?'file-text':fileReader?'file-reader':'unavailable'},
      export:{blob,objectUrl,anchorDownload,msSaveOrOpenBlob:typeof nav.msSaveOrOpenBlob==='function',mode:(blob&&objectUrl&&anchorDownload)?'object-url':anchorDownload?'data-uri-fallback':'unavailable'},
      runtime:{resizeObserver,requestAnimationFrame,cssSupports,webCryptoSha256,structuredClone,pointerEvents,touch}
    };
  }
  function assess(caps={}){
    const findings=[];const add=(id,state,label,detail,fallback='')=>findings.push({id,state,label,detail,fallback});
    const local=Boolean(caps.storage?.local?.writable),session=Boolean(caps.storage?.session?.writable);
    const importMode=String(caps.import?.mode||'unavailable'),exportMode=String(caps.export?.mode||'unavailable');
    add('local-storage',local?'ready':'attention','Local project persistence',local?'Browser-local persistence passed a write/read/remove probe.':'Browser-local persistence is not writable; Workspace cannot safely guarantee local saves.','No automatic substitute for canonical local project persistence.');
    add('session-storage',session?'ready':'limited','Tab navigation memory',session?'Session storage is writable for non-canonical route memory.':'Session storage is unavailable; Workspace can continue but route position may reset after reload.','Start route fallback.');
    add('file-import',importMode!=='unavailable'?(importMode==='file-text'?'ready':'limited'):'attention','File import',importMode==='file-text'?'Native File.text() is available.':importMode==='file-reader'?'File.text() is unavailable; Workspace can use FileReader instead.':'Neither File.text() nor FileReader is available.','FileReader fallback when needed.');
    add('file-export',exportMode!=='unavailable'?(exportMode==='object-url'?'ready':'limited'):'attention','File export',exportMode==='object-url'?'Blob/object-URL downloads are available.':exportMode==='data-uri-fallback'?'Object URLs are unavailable; small text exports can use a data URI fallback.':'No supported client-side download path was detected.','Data URI fallback is capped at 1 MiB.');
    add('history-api',caps.navigation?.historyApi?'ready':'limited','Back / forward navigation',caps.navigation?.historyApi?'History API is available with guarded state writes.':'Workspace will keep in-app routing but will not attempt browser-history state writes.','In-app-only navigation.');
    add('viewport',caps.viewport?.width&&caps.viewport?.height?'ready':'limited','Viewport measurement',caps.viewport?.width?`${caps.viewport.width}×${caps.viewport.height} ${caps.viewport.deviceClass} viewport detected.`:'Viewport dimensions were unavailable; CSS defaults remain active.','Window/document size fallback.');
    add('pointer-input','ready','Pointer / touch input',caps.runtime?.touch?'Touch-capable environment detected; controls retain full-size interaction targets.':'Pointer/keyboard environment detected.','CSS interaction targets do not depend on hover.');
    add('embed-context','ready','WordPress embed context',caps.environment?.embedded?'Embedded browsing context detected; sizing is root-bound rather than assuming full-window ownership.':'Top-level browsing context detected.','Root-bound viewport variables.');
    const attention=findings.filter(x=>x.state==='attention').length,limited=findings.filter(x=>x.state==='limited').length;
    return {schema:MATRIX_SCHEMA,generatedAt:now(),state:attention?'attention':limited?'limited':'ready',findings,summary:{ready:findings.filter(x=>x.state==='ready').length,limited,attention,total:findings.length},governance:{featureDetectionPrimary:true,userAgentGating:false,canonicalMutation:false,automaticUpload:false,telemetry:false}};
  }
  function readFileText(file,env=globalThis){
    const win=env.window||env;
    if(!file)return Promise.reject(new Error('No file was provided.'));
    if(typeof file.text==='function')return Promise.resolve().then(()=>file.text()).then(v=>String(v));
    if(typeof win.FileReader==='function')return new Promise((resolve,reject)=>{const reader=new win.FileReader();reader.onload=()=>resolve(String(reader.result||''));reader.onerror=()=>reject(reader.error||new Error('FileReader could not read the file.'));try{reader.readAsText(file);}catch(error){reject(error);}});
    return Promise.reject(new Error('This browser does not provide a supported text-file reader.'));
  }
  function safeHistory(env=globalThis,mode='push',state=null,url){
    const win=env.window||env,h=win.history;
    if(!h)return {ok:false,mode:'in-app-only',reason:'history-unavailable'};
    const fn=mode==='replace'?'replaceState':'pushState';
    if(typeof h[fn]!=='function')return {ok:false,mode:'in-app-only',reason:'history-api-unavailable'};
    try{if(typeof url==='string')h[fn](state,'',url);else h[fn](state,'');return {ok:true,mode:'history-api',operation:fn};}catch(error){return {ok:false,mode:'in-app-only',reason:text(error?.name||error?.message||'history-write-failed',120)};}
  }
  function triggerDownload(anchor,doc){const parent=doc.body||doc.documentElement;if(!parent||typeof parent.appendChild!=='function')throw new Error('download-target-unavailable');parent.appendChild(anchor);anchor.click();anchor.remove();}
  function downloadText(filename,value,type='text/plain;charset=utf-8',env=globalThis){
    const win=env.window||env,doc=win.document,nav=win.navigator||{};if(!doc)return {ok:false,mode:'unavailable',reason:'document-unavailable'};
    const data=String(value==null?'':value),name=text(filename||'workspace-export.txt',180)||'workspace-export.txt';
    if(typeof win.Blob==='function'){
      try{const blob=new win.Blob([data],{type});if(typeof nav.msSaveOrOpenBlob==='function'){nav.msSaveOrOpenBlob(blob,name);return {ok:true,mode:'ms-save-blob'};}if(win.URL&&typeof win.URL.createObjectURL==='function'){
        const url=win.URL.createObjectURL(blob),a=doc.createElement('a');a.href=url;a.download=name;a.rel='noopener';triggerDownload(a,doc);win.setTimeout(()=>{try{win.URL.revokeObjectURL(url);}catch(_){}},1500);return {ok:true,mode:'object-url'};
      }}catch(_){}
    }
    if(bytes(data)<=MAX_DATA_URI_BYTES){try{const a=doc.createElement('a');a.href=`data:${type},${encodeURIComponent(data)}`;a.download=name;a.rel='noopener';triggerDownload(a,doc);return {ok:true,mode:'data-uri-fallback'};}catch(error){return {ok:false,mode:'unavailable',reason:text(error?.message||'download-failed',120)};}}
    return {ok:false,mode:'unavailable',reason:'no-download-path-for-payload-size'};
  }
  function downloadJson(filename,payload,env=globalThis){return downloadText(filename,JSON.stringify(payload,null,2)+'\n','application/json;charset=utf-8',env);}
  function applyViewport(root,env=globalThis){
    const win=env.window||env;if(!root||!root.style)return {dispose:()=>{},viewport:viewport(win)};
    let disposed=false,pending=false,observer=null;
    const update=()=>{if(disposed)return;pending=false;const vp=viewport(win),box=root.getBoundingClientRect?root.getBoundingClientRect():null,width=Math.max(0,Math.round(Number(box?.width||vp.width||0)));root.style.setProperty('--scw-viewport-height',`${vp.height||0}px`);root.style.setProperty('--scw-viewport-width',`${width||vp.width||0}px`);root.dataset.scwDeviceClass=width&&width<680?'compact':width&&width<1024?'tablet':'desktop';root.dataset.scwTouch=touchCapable(win,win.navigator||{})?'1':'0';root.dataset.scwEmbedded=embedded(win)?'1':'0';return vp;};
    const schedule=()=>{if(pending||disposed)return;pending=true;if(typeof win.requestAnimationFrame==='function')win.requestAnimationFrame(update);else win.setTimeout(update,16);};
    update();
    try{win.addEventListener('resize',schedule,{passive:true});win.addEventListener('orientationchange',schedule,{passive:true});win.visualViewport?.addEventListener?.('resize',schedule,{passive:true});}catch(_){}
    if(typeof win.ResizeObserver==='function'){try{observer=new win.ResizeObserver(schedule);observer.observe(root);}catch(_){observer=null;}}
    return {viewport:viewport(win),dispose:()=>{disposed=true;try{win.removeEventListener('resize',schedule);win.removeEventListener('orientationchange',schedule);win.visualViewport?.removeEventListener?.('resize',schedule);observer?.disconnect?.();}catch(_){}}};
  }
  function report(workspaceVersion,caps,matrix){
    const c=caps||capability(globalThis),m=matrix||assess(c);
    return {schema:REPORT_SCHEMA,generatedAt:now(),workspaceVersion:text(workspaceVersion,40),environment:{browserFamily:c.environment?.browserFamily||'Other / unknown',platformFamily:c.environment?.platformFamily||'Other / unknown',embedded:Boolean(c.environment?.embedded),online:c.environment?.online,language:c.environment?.language||''},viewport:c.viewport,capabilities:{storage:c.storage,navigation:c.navigation,import:c.import,export:c.export,runtime:c.runtime},assessment:m,privacy:{rawUserAgentIncluded:false,deviceIdentifierIncluded:false,projectContentIncluded:false,objectContentIncluded:false,sourceUrlsIncluded:false,queryStringIncluded:false,pageFragmentIncluded:false,automaticTelemetry:false,automaticSubmission:false},governance:{featureDetectionPrimary:true,userAgentUsedForDisplayLabelOnly:true,canonicalMutation:false,automaticRepair:false,automaticUpload:false}};
  }
  function targetMatrix(){return {schema:TARGET_SCHEMA,targetPolicy:'current-and-previous-major-browser-releases-plus-modern-tablet-class-browsers',browserFamilies:['Chromium / Chrome','Microsoft Edge','Safari / WebKit','Firefox / Gecko'],platformFamilies:['macOS','Windows','iPadOS / iOS tablet-class','Android tablet-class'],viewports:['desktop','tablet','compact/narrow'],requiredPaths:['browser-local persistence','session route memory or safe reset','in-app navigation','browser back/forward when History API is available','text-file import','portable client-side export','WordPress embedded rendering'],claimBoundary:'Runtime probes and automated capability fixtures do not replace manual browser/device QA.'};}
  return Object.freeze({SCHEMA,MATRIX_SCHEMA,REPORT_SCHEMA,TARGET_SCHEMA,MAX_DATA_URI_BYTES,bytes,safeProperty,touchCapable,storageProbe,browserFamily,platformFamily,viewport,embedded,capability,assess,readFileText,safeHistory,downloadText,downloadJson,applyViewport,report,targetMatrix});
});
