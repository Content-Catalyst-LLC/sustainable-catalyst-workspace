'use strict';
const base='/v1/private-research/reporting-studio';
const pub=base+'/publication';
const E=id=>document.getElementById(id);
const state={project:null,catalog:null,documentId:null,documentRevision:0,sourceId:null,saved:false,dirty:false,figures:[]};
function status(s,error=false){E('status').textContent=s;E('status').classList.toggle('warn',error)}
function path(s){return pub+'/projects/'+encodeURIComponent(state.project)+s}
async function api(url,body){
 const opt={credentials:'same-origin',cache:'no-store'};
 if(body!==undefined){opt.method='POST';opt.headers={'Content-Type':'application/json'};opt.body=JSON.stringify(body)}
 const r=await fetch(url,opt);const text=await r.text();
 if(!r.ok)throw Error('HTTP '+r.status+': '+text.slice(0,250));
 try{return JSON.parse(text)}catch{throw Error('Unexpected server response')}
}
function run(fn){return async()=>{try{await fn()}catch(err){status(err.message,true);console.error(err)}}}
function refreshExport(){for(const id of ['html','pdf','docx'])E(id).disabled=!state.saved||state.dirty}
function markDirty(){state.dirty=true;state.saved=false;E('dirty').textContent='Unsaved changes';refreshExport();E('length').textContent=E('manuscript').value.length.toLocaleString()+' characters'}
function setDraft(title,markdown,sourceId=null,docId=null,version=0){
 E('title').value=title;E('manuscript').value=markdown;
 state.sourceId=sourceId;state.documentId=docId;state.documentRevision=version;
 state.saved=!!docId;state.dirty=false;E('dirty').textContent=docId?'Saved · revision '+version:'New unsaved draft';
 E('length').textContent=markdown.length.toLocaleString()+' characters';
 refreshExport(); E('provenance').textContent=sourceId?'Source ID: '+sourceId+' · original bytes immutable':'New document. Source not yet linked.';
}
async function selectProject(id){
 if(!id)return;state.project=id;state.catalog=await api(base+'/catalog/projects/'+encodeURIComponent(id));
 E('assets').replaceChildren();E('versions').replaceChildren();
 const files=[...(state.catalog.legacyFiles||[]),...(state.catalog.files||[])];
 E('fileCount').textContent=files.length+' files';
 const figureFiles=files.filter(f=>f.filename.toLowerCase().endsWith('.svg'));
 state.figures=figureFiles;
 for(const file of files){
  const container=document.createElement('div');container.className='asset';
  const title=document.createElement('b');title.textContent=file.filename.split('/').pop();container.append(title);
  const meta=document.createElement('small');meta.textContent=file.filename;container.append(meta);
  const row=document.createElement('div');row.className='asset-row';
  if(/\.(md|txt|docx)$/i.test(file.filename)){
   const open=document.createElement('button');open.textContent='Edit as draft';
   open.onclick=run(async()=>{const d=await api(path('/sources/'+encodeURIComponent(file.artifactId)));
     setDraft(state.catalog.project.title,d.markdown,file.artifactId);await preview();
     status(d.conversion==='exact-utf8-source'?'Original Markdown opened as an editable draft. Source unchanged.':'DOCX extracted as editable text. Original formatting is not round-trip preserved.');});
   row.append(open);
  }
  if(/\.svg$/i.test(file.filename)){
   const insert=document.createElement('button');insert.textContent='Insert figure';
   insert.onclick=run(async()=>{const caption=file.filename.split('/').pop().replace(/\.svg$/i,'').replace(/_/g,' ');
    const textarea=E('manuscript');const snippet='\n\n!['+caption+'](asset:'+file.artifactId+')\n\n';
    const pos=textarea.selectionStart;textarea.setRangeText(snippet,pos,textarea.selectionEnd,'end');markDirty();await preview();});
   row.append(insert);
  }
  if(file.downloadUrl){const a=document.createElement('a');a.href=file.downloadUrl;a.textContent='Original';a.setAttribute('download','');a.style.fontSize='11px';row.append(a)}
  container.append(row);E('assets').append(container);
 }
 const docs=await api(path('/documents'));
 await renderHistoryButtons(docs.documents);
 if(!docs.documents.length){const p=document.createElement('div');p.className='empty';p.textContent='No saved publications yet.';E('versions').append(p)}
 // Prefer the preserved manuscript when there is no saved publication to reopen.
 if(docs.documents.length){const last=docs.documents[0];const r=await api(path('/documents/'+encodeURIComponent(last.documentId)));
  setDraft(r.document.title,r.document.markdown,r.document.source?.artifactId||null,r.document.documentId,r.document.revision);
  state.saved=true;refreshExport();await preview();status('Saved scientific publication opened.');
 }else{
  const candidate=files.find(f=>/\/final_manuscript\.md$/i.test(f.filename))||files.find(f=>/\.md$/i.test(f.filename));
  if(candidate){const d=await api(path('/sources/'+encodeURIComponent(candidate.artifactId)));
    setDraft(state.catalog.project.title,d.markdown,candidate.artifactId);await preview();
    status('Preserved manuscript loaded into editable publication preview. Save a revision to enable exports.');
  }else{setDraft(state.catalog.project.title,'# Introduction\n\n',null);await preview();status('New publication draft. Existing research files remain available in the asset panel.')}
 }
}
function manuscript(){return{title:E('title').value.trim(),markdown:E('manuscript').value,sourceArtifactId:state.sourceId}}
async function preview(){
 if(!state.project)return;
 const data=await api(path('/preview'),manuscript());
 const article=E('preview');article.innerHTML=data.html;
 E('proof').textContent=data.figures.length+' source figures verified · computations not executed';
 return data;
}
async function save(){
 if(!state.project)throw Error('Select a project');
 const head=await api(base+'/catalog/projects/'+encodeURIComponent(state.project));
 const latest=await api(path('/documents'));
 // Conflict detection uses the most recently fetched project revision but never silently rebase.
 if(state.projectRevision!==undefined && state.projectRevision!==head.project.revision){
    throw Error('Project changed since loading. Reopen before saving to avoid overwriting other work.');
 }
 const body={...manuscript(),expectedProjectRevision:head.project.revision,
             documentId:state.documentId,expectedDocumentRevision:state.documentRevision};
 const response=await api(path('/documents'),body);
 state.documentId=response.document.documentId;state.documentRevision=response.document.revision;
 state.projectRevision=response.project.revision;
 state.saved=true;state.dirty=false;E('dirty').textContent='Saved · revision '+state.documentRevision;
 refreshExport();status('Publication revision '+state.documentRevision+' saved immutably. Manuscript source unchanged.');
 await updateVersions();
}
async function renderHistoryButtons(documents){
  E('versions').replaceChildren();
  for(const doc of documents){
    const history=await api(path('/documents/'+encodeURIComponent(doc.documentId)+'/history'));
    for(const version of (history.versions||[]).slice().reverse()){
      const button=document.createElement('button');button.className='revision';
      button.textContent=doc.title+' · v'+version.revision;
      button.onclick=run(async()=>{
        const r=await api(path('/documents/'+encodeURIComponent(doc.documentId)+'?revision='+version.revision));
        setDraft(r.document.title,r.document.markdown,r.document.source?.artifactId||null,
                 r.document.documentId,r.document.revision);
        // Older snapshots may be viewed and exported. Saving from an older
        // version is rejected by server's optimistic document-revision gate.
        state.projectRevision=r.projectRevision;
        await preview();status('Saved publication version '+version.revision+' reopened.');
      });
      E('versions').append(button);
    }
  }
}

async function updateVersions(){
 const docs=await api(path('/documents'));
 await renderHistoryButtons(docs.documents);
}

function exportAs(ext){
 if(!state.saved||state.dirty||!state.documentId)throw Error('Save the current manuscript before exporting.');
 const a=document.createElement('a');a.href=path('/documents/'+encodeURIComponent(state.documentId)+'/export.'+ext+'?revision='+state.documentRevision);
 a.download='scientific-publication-v'+state.documentRevision+'.'+ext;document.body.append(a);a.click();a.remove();
}
E('projects').onchange=run(async()=>{state.projectRevision=undefined;await selectProject(E('projects').value);state.projectRevision=state.catalog.project.revision});
E('title').addEventListener('input',markDirty);E('manuscript').addEventListener('input',markDirty);
E('new').onclick=run(async()=>{if(!state.project)throw Error('Select a project');setDraft(state.catalog.project.title,'# Introduction\n\n',null);await preview();status('Blank publication draft opened. Existing source material remains preserved.')});
E('previewButton').onclick=run(async()=>{await preview();status('Publication preview updated. Research source hashes verified where used.')});
E('save').onclick=run(save);
for(const ext of ['html','pdf','docx'])E(ext).onclick=run(async()=>exportAs(ext));
run(async()=>{
 const result=await api(base+'/catalog/projects');E('projects').replaceChildren();
 const opt=document.createElement('option');opt.textContent='Select research project';opt.value='';E('projects').append(opt);
 for(const p of result.projects){const o=document.createElement('option');o.value=p.projectId;o.textContent=p.title;E('projects').append(o)}
 const params=new URLSearchParams(location.search);const desired=params.get('project');
 const id=result.projects.some(p=>p.projectId===desired)?desired:result.projects.length===1?result.projects[0].projectId:null;
 if(id){E('projects').value=id;await selectProject(id);state.projectRevision=state.catalog.project.revision}
 else status(result.projects.length+' project(s) available. Select a project to open the manuscript editor.');
})();
