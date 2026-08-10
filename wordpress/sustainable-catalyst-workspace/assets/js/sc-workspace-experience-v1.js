(function(root,factory){
  var api=factory();
  if(typeof module==='object'&&module.exports){module.exports=api;}
  if(root){root.SCWorkspaceExperienceV1=api;}
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  var PREF_SCHEMA='sc-workspace-experience-preferences/1.0';
  var EXPERIENCE_SCHEMA='sc-workspace-experience/1.0';
  var STORAGE_KEY='sc_workspace_experience_v0500';
  var ROUTES=[
    {id:'start',area:'start',label:'Start',description:'Begin, resume, or orient the Workspace.',keywords:'home begin resume orientation'},
    {id:'projects',area:'projects',label:'Projects',description:'Create, open, archive, import, and manage local projects.',keywords:'projects project local work'},
    {id:'research',area:'research',label:'Research home',description:'Search, collect, compose, cite, and work across research.',keywords:'research retrieval search collections citations composition'},
    {id:'notebook',area:'research',label:'Notebook',description:'Capture working notes, sources, synthesis, and grounded questions.',keywords:'notebook notes capture synthesis assistance'},
    {id:'knowledge',area:'research',label:'Knowledge',description:'Search and reuse canonical Workspace knowledge across projects.',keywords:'knowledge objects collections reuse'},
    {id:'graph',area:'research',label:'Graph',description:'Inspect recorded research relationships and provenance.',keywords:'graph relationships provenance links'},
    {id:'activity',area:'review',label:'Activity',description:'Review recorded project activity and next actions.',keywords:'review activity timeline next action'},
    {id:'lifecycle',area:'review',label:'Lifecycle',description:'Inspect explicit project readiness milestones.',keywords:'review lifecycle readiness milestones'},
    {id:'history',area:'review',label:'History',description:'Inspect named restore points and version history.',keywords:'review history restore versions'},
    {id:'changes',area:'review',label:'Changes',description:'Compare current work with recorded project states.',keywords:'review changes diff compare'},
    {id:'reconcile',area:'review',label:'Reconcile',description:'Selectively carry reviewed changes into a new project copy.',keywords:'review reconcile selective apply'},
    {id:'safety',area:'review',label:'Safety',description:'Inspect explicit action gates for high-impact operations.',keywords:'review safety gate preflight'},
    {id:'audit',area:'review',label:'Audit',description:'Inspect authoritative audit and governance records.',keywords:'review audit governance provenance'},
    {id:'interoperability',area:'exchange',label:'Import & Interoperability',description:'Stage and review research/project interchange.',keywords:'exchange import export interoperability markdown csv zotero obsidian notion'},
    {id:'collaboration',area:'exchange',label:'Collaborate',description:'Prepare and exchange structured asynchronous reviews.',keywords:'exchange collaborate review comments'},
    {id:'api-embed',area:'exchange',label:'API & Embed',description:'Create explicit static read-only projections and durable references.',keywords:'exchange api embed reference readonly projection integration'},
    {id:'institutional',area:'exchange',label:'Institutional',description:'Prepare explicit institutional handoff packages.',keywords:'exchange institutional handoff promotion'},
    {id:'share',area:'exchange',label:'Share',description:'Create portable project or static review copies.',keywords:'exchange share portable package'}
  ];
  var AREAS=['start','projects','research','review','exchange'];
  var DEFAULTS={schema:PREF_SCHEMA,density:'comfortable',commandHints:true};

  function clone(v){return JSON.parse(JSON.stringify(v));}
  function normalizePreferences(raw){
    var value=raw&&typeof raw==='object'?raw:{};
    return {schema:PREF_SCHEMA,density:value.density==='compact'?'compact':'comfortable',commandHints:value.commandHints!==false};
  }
  function serializePreferences(prefs){return JSON.stringify(normalizePreferences(prefs));}
  function routeForShortcut(key){
    var index=parseInt(String(key||''),10)-1;
    if(index<0||index>=AREAS.length){return null;}
    return AREAS[index];
  }
  function commands(query){
    var q=String(query||'').trim().toLowerCase();
    var items=ROUTES.map(function(route){return clone(route);});
    if(!q){return items;}
    return items.filter(function(route){
      return [route.label,route.description,route.keywords,route.area,route.id].join(' ').toLowerCase().indexOf(q)!==-1;
    });
  }
  function terminology(){
    return [
      {term:'Project',meaning:'The canonical local container for a body of work and its structured objects.'},
      {term:'Research',meaning:'The unified environment for retrieval, Notebook work, Knowledge, citations, composition, and Graph exploration.'},
      {term:'Notebook',meaning:'A working research surface for notes, source captures, links, synthesis, and grounded questions.'},
      {term:'Knowledge',meaning:'A derived view over canonical Workspace records for finding and reusing existing work.'},
      {term:'Review',meaning:'Activity, lifecycle, history, change comparison, reconciliation, safety, and audit.'},
      {term:'Exchange',meaning:'Deliberate import, collaboration, read-only API/embed projections, institutional handoff, and portable sharing.'}
    ];
  }
  function governanceState(){
    return {
      schema:EXPERIENCE_SCHEMA,
      preferencesSchema:PREF_SCHEMA,
      preferencesStorage:'browser-local',
      schemaMigration:false,
      canonicalDataMutation:false,
      automaticNavigation:false,
      automaticProjectCreation:false,
      automaticAi:false,
      commandPalette:'explicit-user-command',
      keyboardShortcuts:'navigation-only',
      densityPreference:'presentation-only',
      editorialHeaderRulePx:4
    };
  }
  function safeStorage(){try{return window.localStorage;}catch(e){return null;}}
  function loadPreferences(){
    var store=safeStorage(); if(!store){return clone(DEFAULTS);} try{return normalizePreferences(JSON.parse(store.getItem(STORAGE_KEY)||'{}'));}catch(e){return clone(DEFAULTS);}
  }
  function savePreferences(prefs){
    var normalized=normalizePreferences(prefs),store=safeStorage();
    if(store){try{store.setItem(STORAGE_KEY,JSON.stringify(normalized));}catch(e){}}
    return normalized;
  }
  function isVisible(el){return !!(el&&el.getClientRects&&el.getClientRects().length&&!el.hidden);}
  function findRouteButton(shell,id){
    var selector='[data-scw-workspace-view="'+String(id).replace(/"/g,'')+'"]';
    var candidates=shell.querySelectorAll(selector);
    for(var i=0;i<candidates.length;i++){if(isVisible(candidates[i])){return candidates[i];}}
    return candidates.length?candidates[0]:null;
  }
  function activateRoute(shell,id){var button=findRouteButton(shell,id);if(button){button.click();button.focus({preventScroll:true});return true;}return false;}
  function applyDensity(shell,density){
    var normalized=density==='compact'?'compact':'comfortable';
    shell.dataset.scwDensity=normalized;
    shell.classList.toggle('scw-density-compact',normalized==='compact');
    shell.classList.toggle('scw-density-comfortable',normalized!=='compact');
    var button=shell.querySelector('[data-scw-density-toggle]');
    if(button){button.setAttribute('aria-pressed',normalized==='compact'?'true':'false');var label=button.querySelector('[data-scw-density-label]');if(label){label.textContent=normalized==='compact'?'Compact':'Comfortable';}}
    return normalized;
  }
  function focusCurrentSearch(shell){
    var sections=shell.querySelectorAll('[data-scw-workspace-section]');
    for(var i=0;i<sections.length;i++){
      if(!sections[i].hidden&&isVisible(sections[i])){
        var search=sections[i].querySelector('input[type="search"], [data-scw-knowledge-search], [data-scw-advanced-search-query]');
        if(search&&!search.disabled){search.focus();return true;}
      }
    }
    return false;
  }
  function renderCommands(shell,palette,query){
    var list=palette.querySelector('[data-scw-command-results]'); if(!list){return;}
    list.innerHTML='';
    var items=commands(query).slice(0,18);
    if(!items.length){var empty=document.createElement('div');empty.className='scw-command-empty';empty.textContent='No matching Workspace routes.';list.appendChild(empty);return;}
    items.forEach(function(item){
      var button=document.createElement('button');button.type='button';button.dataset.scwCommandRoute=item.id;
      button.innerHTML='<span>'+item.area.toUpperCase()+'</span><strong>'+item.label+'</strong><small>'+item.description+'</small>';
      button.addEventListener('click',function(){activateRoute(shell,item.id);closeDialog(palette);});
      list.appendChild(button);
    });
  }
  function openDialog(dialog,focusTarget){if(!dialog){return;}dialog.hidden=false;document.body.classList.add('scw-dialog-open');var target=focusTarget||dialog.querySelector('input,button,[tabindex="0"]');if(target){setTimeout(function(){target.focus();},0);}}
  function closeDialog(dialog){if(!dialog){return;}dialog.hidden=true;document.body.classList.remove('scw-dialog-open');}
  function init(shell){
    if(!shell||shell.dataset.scwExperienceReady==='1'){return governanceState();}
    shell.dataset.scwExperienceReady='1';
    var prefs=loadPreferences();applyDensity(shell,prefs.density);
    var density=shell.querySelector('[data-scw-density-toggle]');
    if(density){density.addEventListener('click',function(){prefs.density=applyDensity(shell,prefs.density==='compact'?'comfortable':'compact');prefs=savePreferences(prefs);});}
    var palette=shell.querySelector('[data-scw-command-palette]');
    var paletteInput=palette?palette.querySelector('[data-scw-command-query]'):null;
    var openCommand=function(){if(!palette){return;}if(paletteInput){paletteInput.value='';renderCommands(shell,palette,'');}openDialog(palette,paletteInput);};
    var commandOpen=shell.querySelector('[data-scw-command-open]');if(commandOpen){commandOpen.addEventListener('click',openCommand);}
    if(paletteInput){paletteInput.addEventListener('input',function(){renderCommands(shell,palette,paletteInput.value);});}
    if(palette){palette.querySelectorAll('[data-scw-dialog-close]').forEach(function(btn){btn.addEventListener('click',function(){closeDialog(palette);});});}
    var help=shell.querySelector('[data-scw-experience-help]');
    var helpOpen=shell.querySelector('[data-scw-help-open]');if(helpOpen){helpOpen.addEventListener('click',function(){openDialog(help);});}
    if(help){help.querySelectorAll('[data-scw-dialog-close]').forEach(function(btn){btn.addEventListener('click',function(){closeDialog(help);});});}
    document.addEventListener('keydown',function(event){
      if((event.metaKey||event.ctrlKey)&&String(event.key).toLowerCase()==='k'){event.preventDefault();openCommand();return;}
      if(event.key==='Escape'){if(palette&&!palette.hidden){closeDialog(palette);return;}if(help&&!help.hidden){closeDialog(help);return;}}
      if(event.altKey&&!event.metaKey&&!event.ctrlKey){var area=routeForShortcut(event.key);if(area){event.preventDefault();activateRoute(shell,area);return;}}
      if(event.key==='/'&&!event.metaKey&&!event.ctrlKey&&!event.altKey){var tag=(event.target&&event.target.tagName||'').toLowerCase();if(tag!=='input'&&tag!=='textarea'&&tag!=='select'&&event.target&&event.target.isContentEditable!==true){if(focusCurrentSearch(shell)){event.preventDefault();}}}
    });
    var routeButtons=shell.querySelectorAll('[data-scw-workspace-view]');
    routeButtons.forEach(function(button){button.addEventListener('click',function(){var status=shell.querySelector('[data-scw-experience-status]');if(status){var route=ROUTES.find(function(r){return r.id===button.dataset.scwWorkspaceView;});status.textContent=route?'Opened '+route.label+'.':'Workspace view changed.';}});});
    return governanceState();
  }
  function boot(){document.querySelectorAll('[data-sc-workspace]').forEach(init);}
  if(typeof document!=='undefined'){if(document.readyState==='loading'){document.addEventListener('DOMContentLoaded',boot);}else{boot();}}
  return {PREF_SCHEMA:PREF_SCHEMA,EXPERIENCE_SCHEMA:EXPERIENCE_SCHEMA,STORAGE_KEY:STORAGE_KEY,ROUTES:ROUTES,AREAS:AREAS,DEFAULTS:DEFAULTS,normalizePreferences:normalizePreferences,serializePreferences:serializePreferences,routeForShortcut:routeForShortcut,commands:commands,terminology:terminology,governanceState:governanceState,init:init};
});
