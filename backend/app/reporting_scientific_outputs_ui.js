// SC-OUTPUT-01: Insert -> Scientific output. Lists this project's registered outputs (server-verified), shows the chart,
// table and full provenance of one exact version, and inserts it at the cursor. The server re-checks rights and
// artifact hashes before it returns the insertion and again when the revision is saved.
// SC-OUTPUT-02: outputs from other Sustainable Catalyst applications (filter by source application), their common source
// reference, and an explicit "Update to vN" for an output already in the draft; saved revisions keep their version.
const SCO={open:false,selected:null};
function scoPath(s=''){return pub+'/scientific-outputs/projects/'+encodeURIComponent(state.project)+s}
function scoRow(dl,label,value){dl.append(el('dt',label),el('dd',value===undefined||value===null||value===''?'—':value))}
async function scoSearch(){
 if(!state.project)throw Error('Select a project');
 const app=E('scoApp').value;
 const r=await api(scoPath('?q='+encodeURIComponent(E('scoQuery').value.trim())+(app?'&application='+encodeURIComponent(app):'')));
 const pickApp=E('scoApp');pickApp.replaceChildren(el('option','All sources'));pickApp.firstChild.value='';
 for(const a of r.applications||[]){const op=el('option',a.label+' ('+a.outputs+')');op.value=a.application;pickApp.append(op)}
 pickApp.value=app;
 const list=E('scoResults');list.replaceChildren();
 if(!r.outputs.length){list.append(el('div','No registered scientific outputs match in this project. Register one from a verified notebook run.','empty'));return}
 const placed=new Set(figureAssets(E('manuscript').value));
 for(const o of r.outputs){
  const card=el('div',null,'asset');const badge=el('span',o.latest.applicationLabel,'sco-app');
  const title=el('b');title.append(badge,document.createTextNode(o.latest.title));
  card.append(title,el('small',o.outputId+' · '+o.versions.length+' version(s), latest v'+o.latestVersion+' · '+o.latest.evidenceClass+' · '+o.latest.visibility));
  const inDraft=o.versions.filter(v=>placed.has(v.chart.artifactId)).map(v=>v.version);
  if(inDraft.length){
   card.append(el('small','In this draft: v'+inDraft.join(', v')));
   const older=Math.max(...inDraft);
   if(older<o.latestVersion&&!inDraft.includes(o.latestVersion)){
    const up=el('button','Update v'+older+' → v'+o.latestVersion+' in the draft','sco-update');up.type='button';
    const chart=o.versions.find(v=>v.version===older).chart.artifactId;
    up.onclick=run(async()=>scoUpdate(o.outputId,older,o.latestVersion,chart));card.append(up);
   }
  }
  const pick=el('select');pick.setAttribute('aria-label','Version of '+o.outputId);
  for(const v of o.versions){const op=el('option','v'+v.version+' · '+v.registeredAt.slice(0,16).replace('T',' ')+(v.insertable?'':' · rights pending'));op.value=v.version;pick.append(op)}
  const open=el('button','Preview');open.type='button';
  open.onclick=run(async()=>scoInspect(o.outputId,+pick.value));
  const row=el('div',null,'asset-row');row.append(pick,open);card.append(row);list.append(card);
 }
}
async function scoInspect(id,version){
 const v=await api(scoPath('/outputs/'+encodeURIComponent(id)+'/versions/'+version));
 const ref=v.sourceReference;
 SCO.selected=v;const box=E('scoPreview');box.replaceChildren();
 const fig=el('figure');const img=el('img');img.src=path('/assets/'+encodeURIComponent(v.artifacts.chart.artifactId)+'/image');img.alt=v.altText;
 fig.append(img,el('figcaption',v.caption));box.append(fig);
 if(v.version<v.latestVersion)box.append(el('p','A newer version (v'+v.latestVersion+') of this output is registered. This preview is v'+v.version+'.','hint warn'));
 const table=el('table',null,'out-table');const cap=el('caption',v.table.caption);const head=el('tr');
 for(const h of v.table.headers){const th=el('th',h);th.scope='col';head.append(th)}
 const thead=el('thead');thead.append(head);const tbody=el('tbody');
 for(const r of v.table.rows.slice(0,12)){const tr=el('tr');for(const c of r)tr.append(el('td',c));tbody.append(tr)}
 table.append(cap,thead,tbody);box.append(table);
 if(v.table.rows.length>12)box.append(el('p','Showing 12 of '+v.table.rows.length+' rows; all rows are inserted.','hint'));
 const ok=Object.values(v.integrity).every(x=>x==='verified');
 const dl=el('dl',null,'out-meta');
 scoRow(dl,'Output',v.outputId+' version '+v.version+' of '+v.latestVersion+' (registered '+v.registeredAt.slice(0,19).replace('T',' ')+' UTC)');
 scoRow(dl,'Source application',ref.applicationLabel+(ref.application==='workspace-notebook'?'':' · '+ref.computedBy.operation+' through its governed Workspace adapter'));
 scoRow(dl,'Verification',ref.verification.statement);
 scoRow(dl,'Integrity',Object.entries(v.integrity).map(([k,s])=>k+' '+s+' ('+v.artifacts[k].sha256.slice(0,12)+')').join(' · '));
 scoRow(dl,'Evidence class',v.evidenceClass+' · '+v.scientificContext.measurementStatus);
 scoRow(dl,'Units',Object.entries(v.asset.units).map(([k,u])=>k+': '+u).join(' · '));
 scoRow(dl,'Uncertainty',v.asset.uncertainty.statement);
 scoRow(dl,'Dataset',v.dataset.map(s=>s.sourceId+(s.sha256?' · sha256 '+s.sha256.slice(0,12):'')+' · '+s.identityStatus).join('; '));
 if(v.library)scoRow(dl,'Library descriptor',v.library.title+' · '+v.library.profileId+' (sha256 '+v.library.profileSha256.slice(0,12)+', Library '+v.library.libraryVersion+') · '+
  v.library.variables.map(x=>x.name+(x.unit?' ['+x.unit+']':'')+' '+x.role).join(', '));
 scoRow(dl,'Calculation',v.calculation.map(c=>c.method).join(' | '));
 scoRow(dl,'Run',v.run.runId+' · receipt '+v.run.receiptId+' · '+v.run.verification+' · result sha256 '+v.run.resultSha256.slice(0,12));
 scoRow(dl,'Notebook',v.notebook.notebookId+' r'+v.notebook.revision+' cell '+v.notebook.cellId);
 scoRow(dl,'Renderer',v.renderer.name+' '+v.renderer.version);
 scoRow(dl,'Rights',v.rights.map(r=>r.status+' · '+r.license+' · '+r.rightsHolder+' ('+r.declaredAt.slice(0,10)+')').join(' → '));
 scoRow(dl,'Citation',v.citation);
 scoRow(dl,'Visibility',v.asset.visibility+' · public approval: '+v.publicApproval);
 box.append(dl);
 const csv=el('a','Full-precision CSV');csv.href=scoPath('/outputs/'+encodeURIComponent(v.outputId)+'/versions/'+v.version+'/table.csv');csv.setAttribute('download','');
 const insert=el('button','Insert at cursor','primary');insert.type='button';insert.disabled=!(ok&&v.insertable);
 insert.onclick=run(scoInsert);
 const row=el('div',null,'asset-row');row.append(insert,csv);box.append(row);
 if(!v.insertable)box.append(el('p','Not insertable: '+v.blockers.join(' '),'hint warn'));
 if(!ok)box.append(el('p','Integrity check failed: this version cannot be inserted.','hint warn'));
}
async function scoUpdate(id,from,to,chart){
 const old=await api(scoPath('/outputs/'+encodeURIComponent(id)+'/versions/'+from));
 const r=await api(scoPath('/outputs/'+encodeURIComponent(id)+'/versions/'+to+'/insertion'));
 if(figureAssets(E('manuscript').value).includes(r.chartArtifactId))throw Error('Version '+to+' of '+id+' is already in the draft. Nothing was changed.');
 replaceManuscriptOutput(chart,from,old.table.rows,r.markdown.trim());
 await preview();await scoSearch();
 status('Scientific output '+id+' updated from v'+from+' to v'+to+' in the draft. '+(state.documentRevision?'Saved revision '+state.documentRevision+' still pins v'+from+'; saving creates a new revision that pins v'+to+'.':'Saving pins v'+to+'.'));
}
async function scoInsert(){
 const v=SCO.selected;if(!v)return;
 const r=await api(scoPath('/outputs/'+encodeURIComponent(v.outputId)+'/versions/'+v.version+'/insertion'));
 // Figure, caption, table and source note go in together at the cursor, or not at all (SC-FIG-PLACE-01).
 insertManuscriptBlocks(r.markdown.trim());
 await preview();
 status('Scientific output '+v.outputId+' v'+v.version+' inserted. Saving pins this exact version to the revision.');
}
E('scoOpen').onclick=run(async()=>{SCO.open=!SCO.open;E('scoPanel').hidden=!SCO.open;E('scoOpen').setAttribute('aria-expanded',String(SCO.open));if(SCO.open)await scoSearch()});
E('scoSearch').onclick=run(scoSearch);
E('scoApp').onchange=run(scoSearch);
E('scoQuery').addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();run(scoSearch)()}});
