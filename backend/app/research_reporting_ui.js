'use strict';
const root='/v1/private-research/reporting-studio', projectsRoot='/v1/private-research/reporting-studio/catalog/projects';
const el=id=>document.getElementById(id), say=s=>{el('status').textContent=s};
let project=null, source=null, saved=null, currentView=null, imageURL=null;
async function api(url,body){const response=await fetch(url,{credentials:'same-origin',cache:'no-store',...(body?{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)}:{})});if(!response.ok)throw Error('Request '+response.status+': '+(await response.text()).slice(0,300));return response.json()}
function task(fn){return async()=>{try{await fn()}catch(e){say(e.message)}}}
function disableExports(){saved=null;el('png').disabled=true;el('svg').disabled=true;el('pdf').disabled=true;el('save').disabled=true}
function show(view){currentView=view;if(imageURL)URL.revokeObjectURL(imageURL);el('preview').replaceChildren();el('provenance').textContent=JSON.stringify(view,null,2);if(view.svg){imageURL=URL.createObjectURL(new Blob([view.svg],{type:'image/svg+xml'}));const img=document.createElement('img');img.alt='Scientific figure with source evidence classification';img.src=imageURL;el('preview').append(img)}else{el('preview').textContent=view.source.projection} }
const lines=id=>el(id).value.split('\n').map(v=>v.trim()).filter(Boolean);
function reference(){if(!source||!project)throw Error('Select a project artifact first.');return{artifact_id:source.artifactId,sha256:source.sha256,source_revision:source.revision,expected_project_revision:project.project.revision,dataset_refs:lines('datasets'),computation_refs:lines('computations'),evidence_refs:lines('evidence'),rights_ref:el('rights').value.trim(),reproduction:el('reproduction').value.trim(),heatmap_unit:el('heatmapUnit').value.trim()||null,evidence_classification:el('classification').value,composition:JSON.parse(el('composition').value),display:{color:el('color').value,line_width:Number(el('width').value),frame_index:Number(el('frame').value),palette:el('palette').value,color_transform:el('colorTransform').value}}}
async function openProject(id){
  if(!id){disableExports();return;}
  disableExports();source=null;currentView=null;el('preview').replaceChildren();
  project=await api(projectsRoot+'/'+encodeURIComponent(id));
  el('assets').replaceChildren();
  const eligible=new Set(project.eligibleSourceIds||[]);
  for(const file of project.files){
    if(!eligible.has(file.artifactId))continue;
    const option=document.createElement('option');option.value=file.artifactId;
    option.textContent=file.filename;el('assets').append(option);
  }
  el('saved').replaceChildren();
  for(const item of project.package?.project?.objects||[]){
    if(item.type!=='research-report-reference'||!item.report)continue;
    const button=document.createElement('button');
    button.textContent=item.id+' · revision '+item.report.revision_id;
    button.onclick=task(()=>reopen(item.report));el('saved').append(button);
  }
  // Existing private-research attachments remain in their original storage.
  // Display them without impersonating the native figure source contract.
  const legacy=project.legacyFiles||[];
  if(legacy.length){
    const heading=document.createElement('p');
    heading.textContent='Existing research files (read-only; not figure-editor inputs)';
    el('saved').append(heading);
    for(const f of legacy){
      const line=document.createElement('div');
      const link=document.createElement('a');
      link.href=f.downloadUrl;link.textContent=f.filename;
      link.setAttribute('download','');line.append(link);el('saved').append(line);
    }
  }
  const nativeOther=project.files.filter(f=>!eligible.has(f.artifactId));
  if(nativeOther.length){
    const heading=document.createElement('p');
    heading.textContent='Additional native research files (not figure-editor inputs)';
    el('saved').append(heading);
    for(const f of nativeOther){
      const line=document.createElement('div');line.textContent=f.filename;
      el('saved').append(line);
    }
  }
  if(!eligible.size){
    say('Project opened. No compatible scientific JSON export in the native artifact store. Existing files are listed read-only; no migration performed.');
  }else{
    say('Project opened. Select an eligible scientific JSON export.');
  }
}
function reportURL(report){return root+'/projects/'+encodeURIComponent(report.project_id)+'/revisions/'+report.revision_id+'/reports/'+encodeURIComponent(report.asset_id)}
async function reopen(report){const d=await api(reportURL(report));saved=d.report;source=project.files.find(f=>f.artifactId===report.reference.artifact_id);const ref=report.reference;if(source)el('assets').value=source.artifactId;for(const [id,key] of [['datasets','dataset_refs'],['computations','computation_refs'],['evidence','evidence_refs']])el(id).value=ref[key].join('\n');el('rights').value=ref.rights_ref;el('reproduction').value=ref.reproduction;el('composition').value=JSON.stringify(ref.composition||{},null,2);el('color').value=ref.display.color;el('width').value=ref.display.line_width;el('frame').value=ref.display.frame_index;el('palette').value=ref.display.palette||'sequential';el('colorTransform').value=ref.display.color_transform||'linear';el('heatmapUnit').value=ref.heatmap_unit||'';el('classification').value=ref.evidence_classification||'unverified';show(d.view);el('pdf').disabled=!d.view.svg;el('png').disabled=!d.view.svg;el('svg').disabled=!d.view.svg;el('save').disabled=false;say('Saved revision reopened; source SHA256 verified.')}
el('projects').onchange=task(()=>openProject(el('projects').value));
el('open').onclick=task(async()=>{disableExports();source=project.files.find(f=>f.artifactId===el('assets').value);if(!source)throw Error('No scientific JSON artifact selected.');el('rights').value='Unknown — private research only';el('reproduction').value='Not yet supplied; source origin and reproduction require review.';await update()});
async function update(){disableExports();const view=await api(root+'/projects/'+encodeURIComponent(project.project.projectId)+'/preview',reference());show(view);el('save').disabled=false;say('Read-only preview. Save a reporting revision before export.')}
el('previewButton').onclick=task(update);
for(const id of ['color','width','frame','datasets','computations','evidence','rights','reproduction','composition','palette','heatmapUnit','classification','colorTransform'])el(id).addEventListener('input',disableExports);
el('save').onclick=task(async()=>{const d=await api(root+'/projects/'+encodeURIComponent(project.project.projectId)+'/reports',reference());await openProject(project.project.projectId);await reopen(d.report);say('Immutable reporting revision '+d.report.revision_id+' saved. Scientific source unchanged.')});
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
async function exportView(){if(!saved)throw Error('Save or reopen an immutable revision first.');const d=await api(reportURL(saved));if(!d.view.svg)throw Error('This source needs a native scene runtime adapter.');return d.view}
el('svg').onclick=task(async()=>{const view=await exportView();download(new Blob([view.svg],{type:'image/svg+xml'}),saved.asset_id+'.svg')});
el('png').onclick=task(async()=>{const view=await exportView();const url=URL.createObjectURL(new Blob([view.svg],{type:'image/svg+xml'}));try{const img=new Image();img.src=url;await img.decode();const canvas=document.createElement('canvas');canvas.width=2580;canvas.height=Math.round(2580*img.naturalHeight/img.naturalWidth);const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(img,0,0,canvas.width,canvas.height);const blob=await new Promise(resolve=>canvas.toBlob(resolve,'image/png'));if(!blob)throw Error('PNG export unavailable');download(blob,saved.asset_id+'.png');say('Saved revision exported as high-resolution PNG. Rights review remains required.')}finally{URL.revokeObjectURL(url)}});
task(async()=>{
  const d=await api(projectsRoot);
  el('projects').replaceChildren();
  const placeholder=document.createElement('option');
  placeholder.value='';placeholder.textContent='Select project';el('projects').append(placeholder);
  for(const p of d.projects){
    const option=document.createElement('option');option.value=p.projectId;
    option.textContent=p.title;el('projects').append(option);
  }
  say(d.projects.length+' owned Workspace project(s) available. Select a project.');
  if(d.projects.length===1){el('projects').value=d.projects[0].projectId;await openProject(d.projects[0].projectId);}
})();

el('pdf').onclick=task(async()=>{await exportView();const a=document.createElement('a');a.href=reportURL(saved)+'/export.pdf';a.download=saved.asset_id+'.pdf';a.click()});

// RD-01.2: navigation to the full manuscript editor (figure editor remains intact).
const publicationLink=document.createElement('a');
publicationLink.href='/v1/private-research/reporting-studio/publication';
publicationLink.textContent='Open full Publication Studio — edit manuscripts, insert figures, export reports';
publicationLink.style.cssText='display:block;padding:12px 16px;background:#e6f2ed;color:#164637;font-weight:650;border-bottom:1px solid #c6d9cc';
document.body.insertBefore(publicationLink,document.body.firstChild);
el('projects').addEventListener('change',()=>{const id=el('projects').value;publicationLink.href='/v1/private-research/reporting-studio/publication'+(id?'?project='+encodeURIComponent(id):'')});
