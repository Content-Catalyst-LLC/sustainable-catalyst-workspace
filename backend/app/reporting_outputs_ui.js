// SC-PUB-ENDTOEND-01: Outputs & Publishing. Every state shown is Research's confirmed response; controls follow the
// server's `controls`, and the server and Research re-check each action. No credential ever reaches this page.
const OUT={open:false,objects:null};
const DIMS=['scientific','rights','ownership','publication'];
function el(tag,text,cls){const n=document.createElement(tag);if(text!==undefined&&text!==null)n.textContent=String(text);if(cls)n.className=cls;return n}
function field(label,input){const w=el('label',label,'out-field');w.append(input);return w}
function input(ph,max=150){const i=el('input');i.type='text';i.maxLength=max;i.placeholder=ph;return i}
function outPath(doc,s=''){return pub+'/projects/'+encodeURIComponent(state.project)+'/outputs'+(doc?'/'+encodeURIComponent(doc):'')+s}
function act(label,fn,enabled=true,cls){const b=el('button',label,cls);b.type='button';b.disabled=!enabled;b.addEventListener('click',run(async()=>{b.disabled=true;try{await fn()}finally{b.disabled=false}await loadOutputs()}));return b}
function lastAction(o){const r=(o.binding&&o.binding.receipts)||[];const x=r[r.length-1];return x?x.action+' · '+x.at.slice(0,19).replace('T',' ')+' UTC'+(x.receipt&&x.receipt.eventSha256?' · receipt '+x.receipt.eventSha256.slice(0,12):''):'—'}
async function researchObjects(){if(!OUT.objects){try{OUT.objects=(await api(pub+'/research-objects')).items}catch(e){OUT.objects=[]}}return OUT.objects}
function bindForm(o){
 const area=input('research-area-slug',120),slug=input('article-slug');
 const box=el('div',null,'out-actions');
 box.append(field('Research area',area),field('Research article identifier',slug),act('Create Research article',async()=>{
  await api(outPath(o.documentId,'/bind'),{areaSlug:area.value.trim(),articleSlug:slug.value.trim(),title:o.title});
  status('Bound to Research article '+slug.value.trim()+' (confirmed by Research).')}));
 return box}
async function revisionForm(o){
 const box=el('div',null,'out-actions');
 const rev=el('select');for(let n=o.revision;n>=1;n--){const op=el('option','Studio revision '+n);op.value=n;rev.append(op)}
 const type=el('select');for(const t of ['report','working-paper','policy-brief','interactive-analysis']){const op=el('option',t);op.value=t;if(t===o.publicationType)op.selected=true;type.append(op)}
 const summary=input('Public summary (abstract)',10000);
 const refs=el('select');refs.multiple=true;refs.size=4;refs.setAttribute('aria-label','Verified Research objects to cite');
 for(const x of await researchObjects()){const op=el('option',x.kind+' · '+x.title+(x.reviewState?' · '+x.reviewState:''));op.value=x.id;op.dataset.kind=x.kind;refs.append(op)}
 const role=k=>({figure:'figure',dataset:'dataset',model:'model',notebook:'notebook',source:'citation',publication:'citation'}[k]||'result');
 box.append(field('Revision',rev),field('Type',type),field('Summary',summary),field('Cite verified Research objects',refs),
  act('Send this exact revision to Research',async()=>{
   const out=await api(outPath(o.documentId,'/research-revisions'),{studioRevision:+rev.value,publicationType:type.value,summary:summary.value,
     references:[...refs.selectedOptions].map(op=>({objectId:op.value,role:role(op.dataset.kind)}))});
   const nc=out.notCarried||{};
   status((out.created?'Research revision '+out.researchRevision+' created':'Research already holds this exact revision ('+out.researchRevision+')')+
     (nc.figures?' · '+nc.figures+' figure(s) not carried: cite them as released figure objects':''))},o.controls.pushRevision));
 return box}
async function approvalsBlock(o){
 const r=o.research,box=el('div',null,'out-approvals');const n=r.submittedRevision;
 if(!n){box.append(el('p','No revision is in review.','hint'));return box}
 const rev=r.revisions.find(x=>x.revision===n)||{};const signed=rev.signedApprovals||{};
 box.append(el('p','Review subject: '+(rev.subjectRef||'—'),'out-subject'));
 let requests=[];try{requests=(await api(outPath(o.documentId,'/approval-requests'))).items.filter(x=>x.subjectRef===rev.subjectRef)}catch(e){}
 const table=el('table','', 'out-table');
 for(const d of DIMS){const tr=el('tr');tr.append(el('th',d),el('td',signed[d]?'Signed approval recorded in Research':'Not recorded'));
  const td=el('td');const req=requests.filter(x=>x.dimension===d);
  for(const q of req){td.append(el('span',q.status+(q.decider?' by '+q.decider:'')+' '));
   if(q.status==='approved'&&!signed[d])td.append(act('Record in Research',async()=>{await api(outPath(o.documentId,'/approvals/attach'),{researchRevision:n,approvalId:q.approvalId});status(d+' approval recorded by Research.')}))}
  if(!signed[d]&&!req.some(q=>q.status==='pending'||q.status==='approved'))td.append(act('Request review',async()=>{await api(outPath(o.documentId,'/approval-requests'),{researchRevision:n,dimension:d});status(d+' review requested from your granted reviewers.')},o.controls.requestApproval));
  tr.append(td);table.append(tr)}
 box.append(table);return box}
function projPath(s){return pub+'/projects/'+encodeURIComponent(state.project)+s}
async function evidenceBlock(o){
 const box=el('div',null,'out-approvals');const refs=o.research.headReferences||[];
 if(!refs.length){box.append(el('p','The current Research revision cites no evidence. Cite at least one verified run, figure or source before review.','hint'));return box}
 for(const ref of refs){
  let info;try{info=await api(projPath('/research-objects/'+encodeURIComponent(ref.objectId)))}catch(e){box.append(el('p',ref.role+' '+ref.objectId+': '+e.message,'hint warn'));continue}
  const obj=info.object,row=el('div',null,'out-card');
  row.append(el('strong',ref.role+' · '+(obj.title||obj.id)),el('p','Status for publication: '+(ref.status||'?')+((ref.problems||[]).length?' — '+ref.problems.join(', '):''),'hint'),el('p','Exact subject: '+obj.subjectRef,'out-subject'));
  const signed=obj.approvals||{};
  for(const d of DIMS){const line=el('div',null,'out-actions');line.append(el('span',d+': '+(signed[d]?'signed approval recorded in Research':'not recorded')));
   const req=info.requests.filter(q=>q.dimension===d);
   for(const q of req)if(q.status==='approved'&&!signed[d])line.append(act('Record in Research',async()=>{await api(projPath('/research-objects/'+encodeURIComponent(obj.id)+'/approvals/attach'),{approvalId:q.approvalId});status(d+' approval recorded for the cited object.')}));
   if(!signed[d]&&!req.some(q=>q.status==='pending'||q.status==='approved'))line.append(act('Request review',async()=>{await api(projPath('/research-objects/'+encodeURIComponent(obj.id)+'/approval-requests'),{dimension:d});status(d+' review requested for the cited object.')}));
   row.append(line)}
  if(obj.visibility!=='public-approved')row.append(act('Release for citation',async()=>{await api(projPath('/research-objects/'+encodeURIComponent(obj.id)+'/release'));status('Research released the object for citation; it stays invisible until the article and area are published.')},DIMS.every(d=>signed[d])));
  box.append(row)}
 return box}
async function areaBlock(o){
 const box=el('div',null,'out-actions');let info;
 try{info=await api(outPath(o.documentId,'/area'))}catch(e){box.append(el('p',e.message,'hint warn'));return box}
 const a=info.area;box.append(el('span','Area '+a.slug+': '+(a.visibility==='approved'||a.visibility==='public-approved'?'published':'not published')));
 if(a.visibility==='approved'||a.visibility==='public-approved')return box;
 const approved=info.requests.filter(q=>q.status==='approved');
 if(!info.requests.some(q=>q.status==='pending')&&!approved.length)box.append(act('Request area publication review',async()=>{await api(outPath(o.documentId,'/area/approval-requests'),{});status('Area publication review requested.')}));
 for(const q of info.requests)if(q.status==='pending')box.append(el('span','review pending'));
 if(approved.length){const c=input('Type '+a.slug+' to confirm',120);box.append(field('Confirm area identifier',c),act('Publish Research area',async()=>{await api(outPath(o.documentId,'/area/publish'),{approvalId:approved[approved.length-1].approvalId,confirmAreaSlug:c.value.trim()});status('Research area published (confirmed by Research).')}))}
 return box}
function releaseBlock(o){
 const r=o.research,box=el('div',null,'out-actions');const slug=o.binding.articleSlug;
 const confirm=input('Type '+slug+' to confirm');
 box.append(field('Confirm article identifier',confirm),
  act(r.publishedRevision?'Publish reviewed update':'Publish approved revision',async()=>{
   const out=await api(outPath(o.documentId,'/publish'),{researchRevision:r.submittedRevision,confirmArticleSlug:confirm.value.trim()});
   status('Published revision '+out.publishedRevision+' · Research receipt '+((out.receipt||{}).eventSha256||'').slice(0,16))},o.controls.publish,'primary'));
 const reason=input('Reason (recorded in the audit chain)',2000);
 box.append(field('Reason',reason),
  act('Unlist',async()=>{await api(outPath(o.documentId,'/unlist'),{reason:reason.value});status('Unlisted (confirmed by Research).')},o.controls.unlist),
  act('Relist',async()=>{await api(outPath(o.documentId,'/relist'),{reason:reason.value});status('Relisted (confirmed by Research).')},o.controls.relist));
 const notice=input('Public withdrawal notice',2000);
 box.append(field('Public notice',notice),act('Withdraw (final)',async()=>{
   await api(outPath(o.documentId,'/withdraw'),{reason:reason.value,publicNotice:notice.value,confirmArticleSlug:confirm.value.trim()});
   status('Withdrawn. The public page now shows the withdrawal notice.')},o.controls.withdraw,'danger'));
 return box}
async function outputCard(o){
 const card=el('article',null,'out-card');const r=o.research;
 const head=el('header');head.append(el('strong',o.title),el('span',' · '+o.publicationType+' · Studio revision '+o.revision,'minor'));card.append(head);
 const dl=el('dl','', 'out-meta');
 const row=(k,v)=>{dl.append(el('dt',k),el('dd',v))};
 row('Research article',o.binding?o.binding.areaSlug+' / '+o.binding.articleSlug:'Not bound (private to Workspace)');
 if(o.researchError)row('Research','Unavailable: '+o.researchError.message);
 if(r){row('Research revision',(r.headRevision||0)+(r.headStudioRevision?' (from Studio revision '+r.headStudioRevision.revision+', '+String(r.headStudioRevision.documentSha256||'').slice(0,12)+')':''));
  row('Review status',r.reviewStatus+(r.submittedRevision?' · revision '+r.submittedRevision+' in review':''));
  row('Publication state',r.publicationStatus+(r.publishedRevision?' · public revision '+r.publishedRevision:''));}
 row('Rights (Studio)',o.rightsStatus||'see Research approvals');
 row('Latest verified action',lastAction(o));
 card.append(dl);
 if(r&&r.publicUrl){const a=el('a','View public research page');a.href=r.publicUrl;a.target='_blank';a.rel='noopener';card.append(a)}
 if(!o.binding){if(o.controls.bind)card.append(bindForm(o));return card}
 if(!r)return card;
 card.append(el('h4','Revision'),await revisionForm(o));
 if(o.controls.submit)card.append(act('Submit Research revision '+r.headRevision+' for review',async()=>{await api(outPath(o.documentId,'/submit'),{researchRevision:r.headRevision});status('Submitted for review (confirmed by Research).')}));
 card.append(el('h4','Cited evidence'),await evidenceBlock(o),el('h4','Review and rights'),await approvalsBlock(o),
  el('h4','Research area'),await areaBlock(o),el('h4','Release'),releaseBlock(o));
 return card}
async function reviewerInbox(){
 const box=el('section',null,'out-inbox');box.append(el('h3','Reviews assigned to you'));
 let items=[];try{items=(await api(pub+'/research-approvals/inbox')).items}catch(e){box.append(el('p',e.message,'hint'));return box}
 if(!items.length){box.append(el('p','No pending reviews.','hint'));return box}
 for(const q of items){const d=el('div',null,'out-card');d.append(el('strong',q.dimension+' · '+q.subjectTitle),el('p','Exact subject: '+q.subjectRef,'out-subject'),el('p','Requested by '+q.requester,'hint'));
  const note=input('Decision note',2000);d.append(field('Note',note));
  for(const [label,decision] of [['Approve this exact revision','approve'],['Request revision','request_revision'],['Reject','reject']])
   d.append(act(label,async()=>{await api(pub+'/research-approvals/'+encodeURIComponent(q.approvalId)+'/decide',{decision,note:note.value,expectedSubjectRef:q.subjectRef});status('Decision signed by Workspace.')}));
  box.append(d)}
 return box}
async function loadOutputs(){
 if(!OUT.open)return;const host=E('outputs');
 if(!state.project){host.replaceChildren(el('p','Select a research project.','hint'));return}
 const data=await api(outPath(''));
 const list=el('div');
 if(!data.researchConfigured)list.append(el('p','Research publishing is not configured for this Workspace; outputs stay private.','hint warn'));
 if(!data.outputs.length)list.append(el('p','Save a manuscript revision to create an output.','hint'));
 for(const o of data.outputs)list.append(await outputCard(o));
 host.replaceChildren(list,await reviewerInbox());
}
E('outputsOpen').addEventListener('click',run(async()=>{OUT.open=!OUT.open;E('outputsPanel').hidden=!OUT.open;E('outputsOpen').setAttribute('aria-expanded',String(OUT.open));OUT.objects=null;await loadOutputs()}));
E('projects').addEventListener('change',run(async()=>{OUT.objects=null;await loadOutputs()}));
