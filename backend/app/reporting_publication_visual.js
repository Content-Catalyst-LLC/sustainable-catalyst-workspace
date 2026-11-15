'use strict';
// SC-PUB-VIS-01: visual block authoring over the canonical Markdown manuscript.
// The server remains responsible for revision locking, provenance and exports.
// Unsupported scientific syntax is locked in visual mode; source mode preserves it.

let visualMode=true;
let visualParts=[];
let visualPrefix='';
let visualPreviewTimer=null;

function parseVisualParts(source){
 const parts=[];let prefix='',body='',inFence=false,inMath=false;
 for(const line of source.match(/[^\n]*\n|[^\n]+$/g)||[]){
  const trimmed=line.trim();
  if(!body&&!trimmed){if(parts.length)parts[parts.length-1].sep+=line;else prefix+=line;continue}
  if(!inFence&&!inMath&&!trimmed){
   if(body){parts.push({raw:body,sep:line});body=''}
   else if(parts.length)parts[parts.length-1].sep+=line;
   continue;
  }
  body+=line;
  if(/^(\x60{3,}|~{3,})/.test(trimmed))inFence=!inFence;
  if(!inFence&&trimmed==='$$')inMath=!inMath;
 }
 if(body)parts.push({raw:body,sep:''});
 return {prefix,parts};
}
function classifyVisual(raw){
 const text=raw.replace(/\n$/,'');
 let m=text.match(/^(#{1,2}) ([^\n]*)$/);
 if(m)return {type:m[1].length===1?'heading1':'heading2',value:m[2]};
 if(text&&text.split('\n').every(l=>/^[-*] /.test(l)))return {type:'list',value:text.split('\n').map(l=>l.slice(2)).join('\n')};
 if(text&&text.split('\n').every(l=>/^> ?/.test(l)))return {type:'quote',value:text.split('\n').map(l=>l.replace(/^> ?/,'')).join('\n')};
 if(/(^|\n)(\s*[!|]|\s*\$\$|\s*\\\[|\s*\x60{3,}|\s*~{3,})/.test(text)||
     /^\s{4}/m.test(text)||/^#{3,6} /.test(text)||/<[A-Za-z][^>]*>/.test(text)||
     /\n#{1,6} /.test(text))return {type:'technical',value:raw};
 return {type:'paragraph',value:text};
}
function blockMarkdown(type,value,original){
 const tail=original.endsWith('\n')?'\n':'';
 if(type==='heading1')return '# '+value.replace(/\n/g,' ')+tail;
 if(type==='heading2')return '## '+value.replace(/\n/g,' ')+tail;
 if(type==='list')return value.split('\n').map(x=>'- '+x).join('\n')+tail;
 if(type==='quote')return value.split('\n').map(x=>'> '+x).join('\n')+tail;
 return value+tail;
}
function syncVisualSource(){
 E('manuscript').value=visualPrefix+visualParts.map(p=>p.raw+p.sep).join('');
 markDirty();
 if(visualPreviewTimer)clearTimeout(visualPreviewTimer);
 visualPreviewTimer=setTimeout(()=>preview().catch(err=>status(err.message,true)),550);
}
function renderVisualBlocks(){
 const parsed=parseVisualParts(E('manuscript').value);
 visualPrefix=parsed.prefix;visualParts=parsed.parts;E('visualBlocks').replaceChildren();
 if(!visualParts.length){
  const p=document.createElement('p');p.className='hint';
  p.textContent='Add a section, paragraph, or open an existing report.';
  E('visualBlocks').append(p);
 }
 for(const part of visualParts){
  const spec=classifyVisual(part.raw);
  const box=document.createElement('section');box.className='sc-block '+spec.type;
  const label=document.createElement('label');
  label.textContent=({heading1:'Title',heading2:'Section heading',paragraph:'Paragraph',
                     list:'List',quote:'Quotation',technical:'Preserved scientific block'})[spec.type];
  if(spec.type==='technical'){
   const pre=document.createElement('pre');pre.textContent=spec.value;
   const note=document.createElement('div');note.className='preserved';
   note.textContent='Equation, figure, table, code or complex Markdown: preserved exactly. Edit in source mode.';
   const b=document.createElement('button');b.type='button';b.textContent='Edit in Markdown';
   b.onclick=()=>{setEditorMode('source');E('manuscript').focus()};
   box.append(label,pre,note,b);
  }else{
   const t=document.createElement('textarea');t.value=spec.value;t.spellcheck=true;
   t.rows=Math.max(2,Math.min(12,spec.value.split('\n').length+1));
   t.setAttribute('aria-label',label.textContent);
   t.addEventListener('input',()=>{
    part.raw=blockMarkdown(spec.type,t.value,part.raw);
    syncVisualSource();
   });
   box.append(label,t);
  }
  E('visualBlocks').append(box);
 }
}
function setEditorMode(mode){
 visualMode=mode==='visual';
 if(visualMode)renderVisualBlocks();
 E('visualBlocks').hidden=!visualMode;
 E('visualTools').hidden=!visualMode;
 E('manuscript').hidden=visualMode;
 E('visualMode').setAttribute('aria-pressed',String(visualMode));
 E('sourceMode').setAttribute('aria-pressed',String(!visualMode));
}
function addVisualMarkdown(snippet){
 const t=E('manuscript');
 t.value=t.value.replace(/\s*$/,'')+'\n\n'+snippet;
 markDirty();renderVisualBlocks();
 preview().catch(err=>status(err.message,true));
}
E('visualMode').onclick=()=>setEditorMode('visual');
E('sourceMode').onclick=()=>setEditorMode('source');
E('addHeading').onclick=()=>addVisualMarkdown('## New section');
E('addParagraph').onclick=()=>addVisualMarkdown('New paragraph');
E('addList').onclick=()=>addVisualMarkdown('- New item');
E('addQuote').onclick=()=>addVisualMarkdown('> Quoted passage');
E('addEquation').onclick=()=>{
 addVisualMarkdown('$$\n\n$$');
 setEditorMode('source');
 E('manuscript').focus();
};
setEditorMode('visual');
