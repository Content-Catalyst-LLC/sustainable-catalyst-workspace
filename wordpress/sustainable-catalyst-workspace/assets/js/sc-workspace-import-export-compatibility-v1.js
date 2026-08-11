(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.SCWorkspaceImportExportCompatibility=api;
})(typeof self!=='undefined'?self:this,function(){'use strict';
  const SCHEMA='sc-workspace-import-export-compatibility/1.0';
  const ASSESSMENT_SCHEMA='sc-workspace-import-assessment/1.0';
  const MATRIX_SCHEMA='sc-workspace-backward-compatibility-matrix/1.0';
  const ROUND_TRIP_SCHEMA='sc-workspace-round-trip-receipt/1.0';
  const CURRENT_PROJECT_SCHEMA='sc-workspace-project/20.0';
  const CURRENT_EXPORT_SCHEMA='sc-workspace-project-export/20.0';
  const CURRENT_STORAGE_SCHEMA=35;
  const MAX_IMPORT_BYTES=8*1024*1024;
  const PROJECT_SCHEMA_PREFIX='sc-workspace-project/';
  const EXPORT_SCHEMA_PREFIX='sc-workspace-project-export/';
  const PORTABLE_PROJECT_SCHEMA='sc-workspace-portable-project/1.0';
  const INTERCHANGE_SCHEMA='sc-workspace-interchange/2.0';
  const PROJECT_VERSIONS=['1.0','2.0','3.0','3.1','4.0','5.0','6.0','7.0','8.0','9.0','10.0','11.0','12.0','13.0','14.0','15.0','16.0','17.0','18.0','19.0','20.0'];
  const PROJECT_SCHEMAS=Object.freeze(PROJECT_VERSIONS.map(v=>PROJECT_SCHEMA_PREFIX+v));
  const EXPORT_SCHEMAS=Object.freeze(PROJECT_VERSIONS.map(v=>EXPORT_SCHEMA_PREFIX+v));
  const STORAGE_VERSIONS=Object.freeze(Array.from({length:CURRENT_STORAGE_SCHEMA},(_,i)=>i+1));
  const projectSet=new Set(PROJECT_SCHEMAS),exportSet=new Set(EXPORT_SCHEMAS);
  const clean=v=>String(v==null?'':v).trim();
  const clone=v=>JSON.parse(JSON.stringify(v));
  const isObject=v=>Boolean(v&&typeof v==='object'&&!Array.isArray(v));
  function parsedVersion(schema,prefix){
    const s=clean(schema);if(!s.startsWith(prefix))return null;
    const raw=s.slice(prefix.length),m=raw.match(/^(\d+)(?:\.(\d+))?$/);if(!m)return null;
    return {raw,major:Number(m[1]),minor:Number(m[2]||0)};
  }
  function classifySchema(schema){
    const s=clean(schema);
    if(projectSet.has(s))return {family:'project',supported:true,current:s===CURRENT_PROJECT_SCHEMA,version:parsedVersion(s,PROJECT_SCHEMA_PREFIX)};
    if(exportSet.has(s))return {family:'project-export',supported:true,current:s===CURRENT_EXPORT_SCHEMA,version:parsedVersion(s,EXPORT_SCHEMA_PREFIX)};
    if(s===PORTABLE_PROJECT_SCHEMA)return {family:'portable-project',supported:true,current:true,version:{raw:'1.0',major:1,minor:0}};
    if(s===INTERCHANGE_SCHEMA)return {family:'interchange',supported:true,current:true,version:{raw:'2.0',major:2,minor:0}};
    const p=parsedVersion(s,PROJECT_SCHEMA_PREFIX);if(p)return {family:'project',supported:false,current:false,future:p.major>20,version:p};
    const e=parsedVersion(s,EXPORT_SCHEMA_PREFIX);if(e)return {family:'project-export',supported:false,current:false,future:e.major>20,version:e};
    return {family:'unknown',supported:false,current:false,future:false,version:null};
  }
  function classifyProjectPayload(payload){
    if(!isObject(payload))return {ok:false,kind:'unknown',error:'The file does not contain a JSON object.'};
    const outer=classifySchema(payload.schema);
    if(outer.family==='project-export'){
      if(!outer.supported)return {ok:false,kind:'project-export',future:Boolean(outer.future),error:outer.future?'This project export was created by a newer Workspace project schema and cannot be safely downgraded.':'This Workspace project export schema is not supported.'};
      if(!isObject(payload.project))return {ok:false,kind:'project-export',error:'The project export envelope is missing its project payload.'};
      const inner=classifySchema(payload.project.schema);
      if(inner.family!=='project'||!inner.supported)return {ok:false,kind:'project-export',future:Boolean(inner.future),error:inner.future?'The project inside this export uses a newer schema and cannot be safely downgraded.':'The project inside this export uses an unsupported schema.'};
      return {ok:true,kind:'project-export',outerSchema:clean(payload.schema),projectSchema:clean(payload.project.schema),project:payload.project,workspaceVersion:clean(payload.workspaceVersion),legacy:clean(payload.schema)!==CURRENT_EXPORT_SCHEMA||clean(payload.project.schema)!==CURRENT_PROJECT_SCHEMA};
    }
    if(outer.family==='project'){
      if(!outer.supported)return {ok:false,kind:'raw-project',future:Boolean(outer.future),error:outer.future?'This project was created by a newer Workspace schema and cannot be safely downgraded.':'This Workspace project schema is not supported.'};
      return {ok:true,kind:'raw-project',outerSchema:'',projectSchema:clean(payload.schema),project:payload,workspaceVersion:'',legacy:clean(payload.schema)!==CURRENT_PROJECT_SCHEMA};
    }
    if(outer.family==='portable-project')return {ok:false,kind:'portable-project',error:'Portable project packages are reviewed through Exchange → Share & portable projects, not the Project Import control.'};
    if(outer.family==='interchange')return {ok:false,kind:'interchange',error:'Interchange bundles are reviewed through Exchange → Import & interoperability, not the Project Import control.'};
    return {ok:false,kind:'unknown',error:'This JSON file is not a recognized Workspace project export.'};
  }
  function assessProjectImport(payload,existingIds=[]){
    const classified=classifyProjectPayload(payload),stamp=new Date().toISOString();
    if(!classified.ok)return {schema:ASSESSMENT_SCHEMA,status:'blocked',reviewRequired:true,automaticCommit:false,automaticOverwrite:false,futureSchemaBlocked:Boolean(classified.future),kind:classified.kind||'unknown',sourceProjectSchema:'',sourceExportSchema:'',currentProjectSchema:CURRENT_PROJECT_SCHEMA,currentExportSchema:CURRENT_EXPORT_SCHEMA,upgradeRequired:false,sourceProjectId:'',title:'',objectCount:0,idCollision:false,warnings:[],errors:[classified.error||'Unsupported project import.'],createdAt:stamp};
    const project=classified.project,id=clean(project.id),title=clean(project.title)||'Untitled project',objects=Array.isArray(project.objects)?project.objects:[],collision=new Set(existingIds.map(clean)).has(id),warnings=[];
    if(classified.legacy)warnings.push(`Legacy ${classified.projectSchema}${classified.outerSchema?` in ${classified.outerSchema}`:''} will be normalized to ${CURRENT_PROJECT_SCHEMA} only after you commit the staged copy.`);
    if(collision)warnings.push('The source project ID already exists locally. Workspace will assign a new local project ID.');
    warnings.push('Import mode is always a new local copy; no existing project is overwritten.');
    return {schema:ASSESSMENT_SCHEMA,status:'ready',reviewRequired:true,automaticCommit:false,automaticOverwrite:false,futureSchemaBlocked:true,kind:classified.kind,sourceProjectSchema:classified.projectSchema,sourceExportSchema:classified.outerSchema,currentProjectSchema:CURRENT_PROJECT_SCHEMA,currentExportSchema:CURRENT_EXPORT_SCHEMA,workspaceVersion:classified.workspaceVersion,upgradeRequired:classified.projectSchema!==CURRENT_PROJECT_SCHEMA,sourceProjectId:id,title,objectCount:objects.length,idCollision:collision,warnings,errors:[],createdAt:stamp};
  }
  function compatibilityMatrix(){
    return {schema:MATRIX_SCHEMA,workspaceVersion:'0.70.0',current:{storageSchema:CURRENT_STORAGE_SCHEMA,projectSchema:CURRENT_PROJECT_SCHEMA,exportSchema:CURRENT_EXPORT_SCHEMA},projectImport:{supportedProjectSchemas:[...PROJECT_SCHEMAS],supportedExportSchemas:[...EXPORT_SCHEMAS],mode:'stage-review-import-as-new-local-copy',futureProjectSchemas:'blocked-no-downgrade',unknownJson:'blocked',automaticOverwrite:false},browserStorage:{supportedStorageVersions:[...STORAGE_VERSIONS],mode:'existing-browser-state-migration-pipeline',acceptedByProjectImport:false},portableProject:{schema:PORTABLE_PROJECT_SCHEMA,surface:'share-portable-projects',mode:'verified-import-as-copy'},interchange:{schema:INTERCHANGE_SCHEMA,surface:'import-interoperability',mode:'staged-review'},boundaries:{automaticUpgradeOnFileSelection:false,automaticCommit:false,automaticOverwrite:false,automaticTrustElevation:false,serverImportPipeline:false,externalNetworkLookup:false}};
  }
  function ordered(value){
    if(Array.isArray(value))return value.map(ordered);
    if(!isObject(value))return value;
    return Object.keys(value).sort().reduce((out,key)=>{out[key]=ordered(value[key]);return out;},{});
  }
  function stableJson(value){return JSON.stringify(ordered(value));}
  function fnv1a32(text){let h=0x811c9dc5;const s=String(text||'');for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h.toString(16).padStart(8,'0');}
  function roundTripProjection(project){
    const p=isObject(project)?clone(project):{};
    delete p.persistence;delete p.updatedAt;delete p.activeObjectId;
    if(Array.isArray(p.activity))p.activity=p.activity.map(x=>{const y=isObject(x)?clone(x):x;if(isObject(y))delete y.at;return y;});
    return p;
  }
  function roundTripCheck(project,normalizeProject){
    if(typeof normalizeProject!=='function')throw new Error('A project normalizer is required for round-trip validation.');
    const before=roundTripProjection(project),normalized=normalizeProject(clone(project));
    if(!normalized)return {schema:ROUND_TRIP_SCHEMA,ok:false,equivalent:false,reason:'Project normalization rejected the export candidate.',beforeFingerprint:fnv1a32(stableJson(before)),afterFingerprint:'',objectCount:Array.isArray(project&&project.objects)?project.objects.length:0};
    const after=roundTripProjection(normalized),a=stableJson(before),b=stableJson(after);
    return {schema:ROUND_TRIP_SCHEMA,ok:true,equivalent:a===b,reason:a===b?'Export candidate survives current project normalization without loss in the compared canonical projection.':'The export candidate changes during current project normalization; export should be reviewed.',beforeFingerprint:fnv1a32(a),afterFingerprint:fnv1a32(b),objectCount:Array.isArray(normalized.objects)?normalized.objects.length:0,checksumPurpose:'drift-detection-only-not-security'};
  }
  function currentProjectExport(project,workspaceVersion,normalizeProject){
    const receipt=roundTripCheck(project,normalizeProject);
    if(!receipt.ok||!receipt.equivalent)return {ok:false,receipt,payload:null};
    return {ok:true,receipt,payload:{schema:CURRENT_EXPORT_SCHEMA,workspaceVersion:clean(workspaceVersion),exportedAt:new Date().toISOString(),project:clone(project),compatibility:{schema:SCHEMA,projectSchema:CURRENT_PROJECT_SCHEMA,importMode:'stage-review-new-local-copy',supportedProjectSchemaFloor:'1.0',futureSchemaDowngrade:false},roundTrip:receipt}};
  }
  return {SCHEMA,ASSESSMENT_SCHEMA,MATRIX_SCHEMA,ROUND_TRIP_SCHEMA,CURRENT_PROJECT_SCHEMA,CURRENT_EXPORT_SCHEMA,CURRENT_STORAGE_SCHEMA,MAX_IMPORT_BYTES,PORTABLE_PROJECT_SCHEMA,INTERCHANGE_SCHEMA,PROJECT_SCHEMAS,EXPORT_SCHEMAS,STORAGE_VERSIONS,parsedVersion,classifySchema,classifyProjectPayload,assessProjectImport,compatibilityMatrix,stableJson,fnv1a32,roundTripProjection,roundTripCheck,currentProjectExport};
});
