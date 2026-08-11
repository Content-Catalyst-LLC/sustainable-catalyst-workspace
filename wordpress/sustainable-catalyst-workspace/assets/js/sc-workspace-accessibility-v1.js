(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceAccessibility=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-accessibility/1.0';
  const REPORT_SCHEMA='sc-workspace-accessibility-report/1.0';
  const CHECKLIST_SCHEMA='sc-workspace-accessibility-checklist/1.0';
  const TARGET='WCAG 2.2 AA';
  const FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]):not([type="hidden"]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"]),[contenteditable="true"]';
  function now(){return new Date().toISOString();}
  function text(value,max=180){return String(value==null?'':value).replace(/\s+/g,' ').trim().slice(0,max);}
  function visible(el){if(!el||el.hidden||el.getAttribute?.('aria-hidden')==='true')return false;if(el.disabled)return false;return !(el.closest&&el.closest('[hidden],[aria-hidden="true"]'));}
  function focusable(container){if(!container||!container.querySelectorAll)return[];return [...container.querySelectorAll(FOCUSABLE)].filter(visible);}
  function safeFocus(el){if(!el||typeof el.focus!=='function')return false;try{el.focus({preventScroll:true});return true;}catch(_){try{el.focus();return true;}catch(__){return false;}}}
  function nextIndex(length,current,key){if(length<=0)return-1;let i=Math.max(0,Math.min(length-1,Number.isFinite(current)?current:0));if(key==='ArrowRight'||key==='ArrowDown')return(i+1)%length;if(key==='ArrowLeft'||key==='ArrowUp')return(i<=0?length-1:i-1);if(key==='Home')return 0;if(key==='End')return length-1;return i;}
  function wireKeyboardGroup(group,doc){
    if(!group||group.dataset?.scwKeyboardReady==='1')return false;
    if(group.dataset)group.dataset.scwKeyboardReady='1';
    group.addEventListener?.('keydown',event=>{
      if(!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown','Home','End'].includes(event.key))return;
      const items=focusable(group).filter(item=>item.matches?.('button,[role="tab"],[role="menuitem"],[data-scw-workspace-view],[data-scw-research-surface]'));
      if(!items.length)return;
      const active=(doc||globalThis.document)?.activeElement;const current=Math.max(0,items.indexOf(active));const next=nextIndex(items.length,current,event.key);
      event.preventDefault?.();safeFocus(items[next]);
    });
    return true;
  }
  function openDialogs(root){return root&&root.querySelectorAll?[...root.querySelectorAll('[role="dialog"][aria-modal="true"]')].filter(el=>!el.hidden&&el.getAttribute('aria-hidden')!=='true'):[];}
  function containTab(dialog,event){const items=focusable(dialog);if(!items.length){event.preventDefault?.();if(!dialog.hasAttribute?.('tabindex'))dialog.setAttribute?.('tabindex','-1');safeFocus(dialog);return true;}const doc=dialog.ownerDocument||globalThis.document;const active=doc?.activeElement;let index=items.indexOf(active);if(event.shiftKey){if(index<=0){event.preventDefault?.();safeFocus(items[items.length-1]);return true;}}else if(index===items.length-1||index<0){event.preventDefault?.();safeFocus(items[0]);return true;}return false;}
  function installDialogGuard(root,env=globalThis){
    const win=env.window||env,doc=win.document;if(!root||!doc||root.dataset?.scwDialogGuardReady==='1')return{dispose(){}};
    if(root.dataset)root.dataset.scwDialogGuardReady='1';let lastOutside=null;let activeDialog=null;let opener=null;
    const focusListener=event=>{const dialogs=openDialogs(root);if(!dialogs.some(d=>d.contains?.(event.target)))lastOutside=event.target;};
    const sync=()=>{const dialogs=openDialogs(root);const next=dialogs[dialogs.length-1]||null;if(next&&!activeDialog){opener=lastOutside||doc.activeElement;activeDialog=next;const items=focusable(next);if(!next.contains?.(doc.activeElement))safeFocus(items[0]||next);}else if(!next&&activeDialog){const restore=opener;activeDialog=null;opener=null;if(restore&&restore.isConnected!==false)safeFocus(restore);}else if(next)activeDialog=next;};
    const keyListener=event=>{const dialogs=openDialogs(root);const dialog=dialogs[dialogs.length-1];if(!dialog)return;if(event.key==='Tab'){containTab(dialog,event);return;}if(event.key==='Escape'){const close=dialog.querySelector?.('[data-scw-dialog-close],[data-scw-action-gate-cancel],[data-scw-modal-close]');if(close&&typeof close.click==='function'){event.preventDefault?.();close.click();}}};
    doc.addEventListener?.('focusin',focusListener,true);doc.addEventListener?.('keydown',keyListener,true);
    let observer=null;if(typeof win.MutationObserver==='function'){observer=new win.MutationObserver(sync);try{observer.observe(root,{subtree:true,attributes:true,attributeFilter:['hidden','aria-hidden']});}catch(_){observer=null;}}
    sync();
    return{dispose(){doc.removeEventListener?.('focusin',focusListener,true);doc.removeEventListener?.('keydown',keyListener,true);observer?.disconnect?.();}};
  }
  function reducedMotion(env=globalThis){const win=env.window||env;try{return Boolean(win.matchMedia?.('(prefers-reduced-motion: reduce)').matches);}catch(_){return false;}}
  function forcedColors(env=globalThis){const win=env.window||env;try{return Boolean(win.matchMedia?.('(forced-colors: active)').matches);}catch(_){return false;}}
  function viewportAllowsZoom(doc){const meta=doc?.querySelector?.('meta[name="viewport"]');if(!meta)return{state:'manual',detail:'Viewport metadata is controlled by the host page; verify 200% zoom and 400% reflow manually.'};const content=String(meta.getAttribute('content')||'').toLowerCase();const blocked=/user-scalable\s*=\s*no/.test(content)||/maximum-scale\s*=\s*(?:1(?:\.0*)?)(?:\s|,|$)/.test(content);return{state:blocked?'attention':'ready',detail:blocked?'The host viewport metadata appears to restrict user zoom.':'No explicit user-zoom restriction was detected in host viewport metadata.'};}
  function finding(id,state,label,detail,manual=false){return{id,state,label,detail,manual:Boolean(manual)};}
  function audit(root,env=globalThis){
    const win=env.window||env,doc=win.document||root?.ownerDocument;const findings=[];
    const skip=root?.querySelector?.('.scw-skip-link[href="#scw-workspace-main"]');findings.push(finding('skip-link',skip?'ready':'attention','Skip navigation',skip?'A Workspace skip link targets the primary application navigation.':'No Workspace skip link to the primary application navigation was detected.'));
    const nav=root?.querySelector?.('[data-scw-workspace-view-nav]');findings.push(finding('primary-navigation',nav&&nav.getAttribute?.('aria-label')?'ready':'attention','Primary navigation semantics',nav?'Workspace primary navigation has a programmatic label.':'Workspace primary navigation was not detected.'));
    const sections=root?.querySelectorAll?[...root.querySelectorAll('[data-scw-workspace-section]')]:[];const unlabeled=sections.filter(section=>{const id=section.getAttribute?.('aria-labelledby');return !id||!doc?.getElementById?.(id);});findings.push(finding('section-labels',unlabeled.length?'attention':'ready','Section labels',unlabeled.length?`${unlabeled.length} Workspace section(s) lack a resolvable aria-labelledby heading.`:`All ${sections.length} Workspace sections expose a resolvable heading label.`));
    const dialogs=root?.querySelectorAll?[...root.querySelectorAll('[role="dialog"]')]:[];const badDialogs=dialogs.filter(d=>d.getAttribute?.('aria-modal')!=='true'||!d.getAttribute?.('aria-labelledby'));findings.push(finding('dialogs',badDialogs.length?'attention':'ready','Dialog semantics and containment',badDialogs.length?`${badDialogs.length} dialog(s) need modal/label review.`:`${dialogs.length} dialog(s) expose modal semantics; v0.64 adds Tab containment, Escape close where available, and opener focus restoration.`));
    const live=root?.querySelectorAll?[...root.querySelectorAll('[role="status"][aria-live], [role="alert"]')]:[];findings.push(finding('status-messages',live.length?'ready':'attention','Status announcements',live.length?`${live.length} live status/alert region(s) are available for non-modal feedback.`:'No live status regions were detected.'));
    const labels=root?.querySelectorAll?[...root.querySelectorAll('input:not([type="hidden"]),select,textarea')]:[];const unlabeledControls=labels.filter(control=>{if(control.getAttribute?.('aria-label')||control.getAttribute?.('aria-labelledby'))return false;const id=control.id;if(id&&doc?.querySelector?.(`label[for="${id}"]`))return false;return !control.closest?.('label');});findings.push(finding('form-labels',unlabeledControls.length?'attention':'ready','Form control labels',unlabeledControls.length?`${unlabeledControls.length} form control(s) need an explicit accessible-name review.`:`All ${labels.length} detected form controls have an associated label or accessible name.`));
    findings.push(finding('reduced-motion','ready','Reduced motion',reducedMotion(win)?'Reduced-motion preference is active; Workspace suppresses smooth scrolling and transition/animation motion in the v0.64 layer.':'Workspace includes a reduced-motion presentation path.'));
    findings.push(finding('forced-colors','manual','Forced colors / high contrast',forcedColors(win)?'Forced-colors mode is active; verify every current surface remains legible.':'Forced-colors mode is not active in this session; verify it manually.',true));
    const zoom=viewportAllowsZoom(doc);findings.push(finding('zoom-reflow',zoom.state,'Zoom and reflow',zoom.detail,true));
    findings.push(finding('screen-reader','manual','Screen-reader workflow','Automated DOM checks cannot certify reading order, control announcements, virtual-cursor behavior, or task completion with VoiceOver, NVDA, JAWS, or Narrator.',true));
    const attention=findings.filter(x=>x.state==='attention').length,manual=findings.filter(x=>x.state==='manual').length,ready=findings.filter(x=>x.state==='ready').length;
    return{schema:SCHEMA,generatedAt:now(),target:TARGET,state:attention?'attention':manual?'manual-review':'ready',summary:{ready,attention,manual,total:findings.length},findings,governance:{automatedCertification:false,manualAuditRequired:true,canonicalMutation:false,automaticUpload:false,telemetry:false,hiddenScore:false}};
  }
  function report(workspaceVersion,result){const r=result||{summary:{},findings:[]};return{schema:REPORT_SCHEMA,generatedAt:now(),workspaceVersion:text(workspaceVersion,40),target:TARGET,assessment:r,privacy:{projectContentIncluded:false,objectContentIncluded:false,sourceContentIncluded:false,sourceUrlsIncluded:false,deviceIdentifierIncluded:false,rawUserAgentIncluded:false,automaticSubmission:false},governance:{automatedCertification:false,manualAuditRequired:true,canonicalMutation:false,automaticRepair:false,automaticUpload:false,telemetry:false,hiddenScore:false}};}
  function checklist(){return{schema:CHECKLIST_SCHEMA,target:TARGET,claimBoundary:'Automated checks and this checklist support field QA; they do not by themselves establish WCAG conformance or accessibility certification.',requiredManualChecks:[
    {id:'keyboard-complete',label:'Keyboard-only completion',procedure:'Complete Start → Project → Research → Review → Exchange workflows without a pointer; verify no unreachable control and no unexpected keyboard trap.'},
    {id:'focus-order',label:'Focus order and restoration',procedure:'Tab through each major surface and every modal; verify focus order follows reading order and returns to the invoking control after close.'},
    {id:'visible-focus',label:'Visible focus',procedure:'Verify focus indicators remain clearly visible on links, buttons, form fields, cards, nav controls, dialogs, and custom controls.'},
    {id:'zoom-200',label:'200% zoom',procedure:'At 200% browser zoom, verify content and controls remain operable without loss of information or functionality.'},
    {id:'reflow-400',label:'400% / 320 CSS px reflow',procedure:'Verify primary workflows reflow without two-dimensional scrolling except where intrinsically required by content.'},
    {id:'screen-reader-voiceover',label:'VoiceOver + Safari',procedure:'Verify landmarks, headings, control names/states, status messages, dialogs, and main research workflows on macOS/iPadOS where applicable.'},
    {id:'screen-reader-windows',label:'NVDA/JAWS/Narrator + Windows',procedure:'Verify landmarks, headings, control names/states, status messages, dialogs, and main workflows with at least one Windows screen reader.'},
    {id:'forced-colors',label:'Forced colors / high contrast',procedure:'Verify visible focus, boundaries, buttons, inputs, selected states, alerts, and charts/relationship views do not rely on color alone.'},
    {id:'reduced-motion',label:'Reduced motion',procedure:'Enable reduced motion and verify route changes, dialogs, scrolling, and dynamic panels do not require unnecessary motion.'},
    {id:'touch-targets',label:'Touch target access',procedure:'On tablet-class touch devices, verify primary actions, navigation, dismiss controls, and form targets are comfortably operable.'},
    {id:'contrast',label:'Contrast review',procedure:'Measure text, controls, focus indicators, selected states, and essential graphical objects against WCAG 2.2 AA requirements.'},
    {id:'errors',label:'Errors and validation',procedure:'Trigger import, form, persistence, and recovery errors; verify messages identify the problem programmatically and do not rely on color alone.'}
  ],governance:{manualReviewRequired:true,automaticCertification:false,telemetry:false,canonicalMutation:false}};}
  function enhance(root,env=globalThis){const win=env.window||env,doc=win.document;if(!root||root.dataset?.scwAccessibilityReady==='1')return{dispose(){}};if(root.dataset)root.dataset.scwAccessibilityReady='1';root.dataset.scwMotion=reducedMotion(win)?'reduce':'standard';
    const groups=[root.querySelector?.('[data-scw-workspace-view-nav]'),...((root.querySelectorAll&&[...root.querySelectorAll('[data-scw-navigation-context] nav,[data-scw-research-tool-nav]')])||[])].filter(Boolean);groups.forEach(group=>{group.setAttribute?.('data-scw-keyboard-nav','1');wireKeyboardGroup(group,doc);});
    root.querySelectorAll?.('[data-scw-workspace-section]').forEach(section=>{const h=section.querySelector?.('h1,h2,h3');if(h&&!h.hasAttribute?.('tabindex'))h.setAttribute?.('tabindex','-1');});
    const guard=installDialogGuard(root,win);return{dispose(){guard.dispose?.();}};}
  return Object.freeze({SCHEMA,REPORT_SCHEMA,CHECKLIST_SCHEMA,TARGET,FOCUSABLE,text,visible,focusable,safeFocus,nextIndex,wireKeyboardGroup,openDialogs,containTab,installDialogGuard,reducedMotion,forcedColors,viewportAllowsZoom,audit,report,checklist,enhance});
});
