(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceResearchNavigation=api;
})(typeof self!=='undefined'?self:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-navigation-map/1.0';
  const AREAS={
    start:{label:'Start',defaultView:'start',description:'Begin, resume, or follow the complete product journey.',views:['start','journey','help']},
    projects:{label:'Projects',defaultView:'projects',description:'Create projects and work with canonical Workspace objects.',views:['projects']},
    research:{label:'Research',defaultView:'research',description:'Search, capture, organize, connect, and synthesize research.',views:['research','notebook','knowledge','graph']},
    review:{label:'Review',defaultView:'activity',description:'Inspect activity, lifecycle, history, changes, safety, reconciliation, audit, release, recovery, and deployment records.',views:['activity','lifecycle','history','changes','reconcile','safety','audit','automation','performance','security','beta','reliability','integrity','compatibility','accessibility','final-audit','beta-closure','release-candidate','deployment','production-certification','production-signoff','ga-readiness','recovery-drills']},
    exchange:{label:'Exchange',defaultView:'interoperability',description:'Import, collaborate, hand off institutional work, and share portable copies.',views:['interoperability','collaboration','api-embed','institutional','share']}
  };
  const LABELS={start:'Start',journey:'Product Journey',help:'Help & Recovery',projects:'Projects',research:'Research home',notebook:'Notebook',knowledge:'Knowledge',graph:'Graph',activity:'Activity',lifecycle:'Lifecycle',history:'History',changes:'Changes',reconcile:'Reconcile',safety:'Safety',audit:'Audit',automation:'Automation',performance:'Performance',security:'Security & Privacy',beta:'Beta Readiness',reliability:'Reliability',integrity:'Persistence Integrity',compatibility:'Compatibility',accessibility:'Accessibility','final-audit':'Final Audit','beta-closure':'Beta Closure','release-candidate':'Release Candidate',deployment:'Deployment','production-certification':'Production Certification','production-signoff':'Production Sign-Off','ga-readiness':'1.0 Readiness','recovery-drills':'Recovery Drills',interoperability:'Import & Interoperability',collaboration:'Collaborate','api-embed':'API & Embed',institutional:'Institutional',share:'Share'};
  const VIEW_TO_AREA=Object.keys(AREAS).reduce((map,area)=>{AREAS[area].views.forEach(view=>map[view]=area);return map;},{});
  function areaForView(view){return VIEW_TO_AREA[String(view||'')]||'start';}
  function defaultView(area){const key=String(area||'');return AREAS[key]?AREAS[key].defaultView:'start';}
  function viewsForArea(area){const key=String(area||'');return AREAS[key]?AREAS[key].views.slice():AREAS.start.views.slice();}
  function labelForView(view){return LABELS[String(view||'')]||'Start';}
  function context(view){const normalized=VIEW_TO_AREA[String(view||'')]?String(view):'start',area=areaForView(normalized),meta=AREAS[area];return {schema:SCHEMA,area,areaLabel:meta.label,view:normalized,viewLabel:labelForView(normalized),description:meta.description,path:`Workspace / ${meta.label}${normalized===meta.defaultView?'':` / ${labelForView(normalized)}`}`};}
  function primaryAreas(){return Object.keys(AREAS).map(id=>({id,label:AREAS[id].label,defaultView:AREAS[id].defaultView,description:AREAS[id].description}));}
  function map(){return {schema:SCHEMA,primaryAreas:primaryAreas(),routes:Object.fromEntries(Object.keys(AREAS).map(id=>[id,viewsForArea(id)])),governance:{derivedFromExistingSurfaces:true,movesCanonicalData:false,duplicatesCanonicalContent:false,automaticSemanticInference:false,automaticAI:false,specializedSurfacesRetained:true}};}
  return {SCHEMA,AREAS,LABELS,areaForView,defaultView,viewsForArea,labelForView,context,primaryAreas,map};
});
