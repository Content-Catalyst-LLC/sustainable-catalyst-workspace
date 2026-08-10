const fs=require('fs'),vm=require('vm'),path=require('path');
const code=fs.readFileSync(path.join(__dirname,'../wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-notebook-assistance-adapter-v1.js'),'utf8');
const store=new Map();let posted=null;const window={sessionStorage:{getItem:k=>store.get(k)||null,setItem:(k,v)=>store.set(k,v),removeItem:k=>store.delete(k)},location:{origin:'https://sustainablecatalyst.com'},opener:{closed:false,postMessage:(msg,origin)=>posted={msg,origin}}};window.window=window;
const request={schema:'sc-workspace-notebook-assistance-request-export/1.0',workspaceVersion:'0.37.0',project:{id:'p1'},request:{id:'a1',question:'What?',entries:[{number:1,ref:{schema:'sc-workspace-notebook-ref/1.0',kind:'block',id:'b1',notebookId:'n1',sectionId:'s1',label:'Source'},label:'Source',citation:'Study A'}]}};
store.set('sc_workspace_notebook_assistance_request_v1',JSON.stringify(request));vm.runInNewContext(code,{window,JSON,Set,Map,Number,String,Array,Date,Error});const A=window.SCWorkspaceNotebookAssistanceAdapter;if(!A)throw new Error('adapter missing');
let threw=false;try{A.buildResponse({response:'Unsupported [2].'});}catch(_){threw=true}if(!threw)throw new Error('invalid citation accepted');
threw=false;try{A.buildResponse({response:'No citation.'});}catch(_){threw=true}if(!threw)throw new Error('uncited response accepted');
const packet=A.returnToWorkspace({response:'Supported by selected source [1].',sourceTitle:'Research Librarian'});if(packet.citations.length!==1||packet.citations[0].number!==1)throw new Error('citation derivation failed');if(!posted||posted.msg.type!=='sc-workspace-notebook-assistance-response')throw new Error('postMessage return missing');
console.log('PASS - v0.37.0 notebook assistance adapter runtime');
