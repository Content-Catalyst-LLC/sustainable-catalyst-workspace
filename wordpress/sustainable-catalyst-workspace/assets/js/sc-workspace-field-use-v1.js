(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceFieldUse=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-field-use-profile/1.0';
  const CONTRACT='sc-workspace-field-use-contract/1.0';
  const TARGETS=Object.freeze({wide:1200,narrow:760,short:700});
  const clamp=(n,min,max)=>Math.min(max,Math.max(min,Number(n)||0));
  function media(win,query){try{return Boolean(win&&typeof win.matchMedia==='function'&&win.matchMedia(query).matches);}catch(_){return false;}}
  function dimensions(env=globalThis,rootEl=null){
    const win=env.window||env,doc=win.document||{},vv=win.visualViewport;
    const rect=rootEl&&typeof rootEl.getBoundingClientRect==='function'?rootEl.getBoundingClientRect():null;
    const width=Math.round(clamp(rect&&rect.width||vv&&vv.width||win.innerWidth||doc.documentElement?.clientWidth||0,0,10000));
    const height=Math.round(clamp(vv&&vv.height||win.innerHeight||doc.documentElement?.clientHeight||0,0,10000));
    return {width,height};
  }
  function inputProfile(env=globalThis){
    const win=env.window||env,nav=win.navigator||{};
    const coarse=media(win,'(pointer: coarse)'),fine=media(win,'(pointer: fine)');
    const touch=Number(nav.maxTouchPoints||0)>0||('ontouchstart' in win);
    return {touch,coarse,fine,profile:coarse&&fine?'mixed':coarse||touch?'coarse':'fine'};
  }
  function classify(width,height){
    const w=Number(width)||0,h=Number(height)||0;
    return {viewport:w>=TARGETS.wide?'wide':w>=TARGETS.narrow?'compact':'narrow',shortViewport:Boolean(h&&h<TARGETS.short),orientation:w&&h?(w>=h?'landscape':'portrait'):'unknown'};
  }
  function profile(env=globalThis,rootEl=null){
    const size=dimensions(env,rootEl),kind=classify(size.width,size.height),input=inputProfile(env);
    return {schema:SCHEMA,width:size.width,height:size.height,viewport:kind.viewport,orientation:kind.orientation,shortViewport:kind.shortViewport,input:input.profile,touch:input.touch,coarsePointer:input.coarse,finePointer:input.fine,privacy:{rawUserAgentIncluded:false,deviceIdentifierIncluded:false,persisted:false,automaticTelemetry:false,automaticSubmission:false},governance:{featureDetectionPrimary:true,canonicalMutation:false,deviceFingerprinting:false}};
  }
  function apply(rootEl,env=globalThis){
    if(!rootEl||!rootEl.dataset)return null;
    const p=profile(env,rootEl);
    rootEl.dataset.scwViewport=p.viewport;
    rootEl.dataset.scwInput=p.input;
    rootEl.dataset.scwOrientation=p.orientation;
    rootEl.dataset.scwShortViewport=p.shortViewport?'1':'0';
    if(rootEl.style&&typeof rootEl.style.setProperty==='function'){
      rootEl.style.setProperty('--scw-field-width',`${p.width}px`);
      rootEl.style.setProperty('--scw-field-height',`${p.height}px`);
    }
    return p;
  }
  function observe(rootEl,env=globalThis){
    const win=env.window||env;if(!rootEl)return function(){};
    let frame=0,observer=null;
    const schedule=()=>{if(frame)return;const run=()=>{frame=0;apply(rootEl,win);};if(typeof win.requestAnimationFrame==='function')frame=win.requestAnimationFrame(run);else run();};
    apply(rootEl,win);
    if(typeof win.ResizeObserver==='function'){observer=new win.ResizeObserver(schedule);try{observer.observe(rootEl);}catch(_){observer=null;}}
    if(typeof win.addEventListener==='function'){win.addEventListener('resize',schedule,{passive:true});win.addEventListener('orientationchange',schedule,{passive:true});}
    const vv=win.visualViewport;if(vv&&typeof vv.addEventListener==='function'){vv.addEventListener('resize',schedule,{passive:true});vv.addEventListener('scroll',schedule,{passive:true});}
    return function(){if(observer&&typeof observer.disconnect==='function')observer.disconnect();if(typeof win.removeEventListener==='function'){win.removeEventListener('resize',schedule);win.removeEventListener('orientationchange',schedule);}if(vv&&typeof vv.removeEventListener==='function'){vv.removeEventListener('resize',schedule);vv.removeEventListener('scroll',schedule);}if(frame&&typeof win.cancelAnimationFrame==='function')win.cancelAnimationFrame(frame);};
  }
  function boot(env=globalThis){const win=env.window||env,doc=win.document;if(!doc||typeof doc.querySelectorAll!=='function')return [];return [...doc.querySelectorAll('[data-sc-workspace]')].map(el=>observe(el,win));}
  function contract(){return {schema:CONTRACT,profileSchema:SCHEMA,targets:{...TARGETS},viewportClasses:['wide','compact','narrow'],inputProfiles:['fine','coarse','mixed'],phonePriority:'capture-review-light-editing',denseSurfacesRemainAvailable:true,shortViewportDetection:true,touchSafeTargets:true,tabletReflow:true,narrowWindowReflow:true,deviceFingerprinting:false,profilePersistence:false,automaticUpload:false,telemetry:false,canonicalMutation:false,manualDeviceQaRequired:true};}
  return Object.freeze({SCHEMA,CONTRACT,TARGETS,dimensions,inputProfile,classify,profile,apply,observe,boot,contract});
});
