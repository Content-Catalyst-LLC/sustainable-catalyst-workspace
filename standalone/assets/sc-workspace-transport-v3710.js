(function (root, factory) {
  'use strict';
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  root.SCWorkspaceTransportFactory=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='sc-workspace-transport/1.0', VERSION='3.71.0';
  function join(base,path){const raw=String(path||'');if(/^https?:\/\//i.test(raw))return raw;const b=String(base||'').replace(/\/+$/,'');return b?b+'/'+raw.replace(/^\/+/, ''):raw;}
  async function parse(response){const type=String(response.headers&&response.headers.get?response.headers.get('content-type')||'':'');if(type.includes('application/json'))return response.json();const text=await response.text();if(!text)return null;try{return JSON.parse(text);}catch(_){return text;}}
  function createDirect(options){
    const source=options&&typeof options==='object'?options:{};
    const baseUrl=String(source.baseUrl||'').trim();
    const fetchImpl=source.fetchImpl||(typeof fetch==='function'?fetch.bind(globalThis):null);
    if(!fetchImpl)throw new Error('Workspace direct transport requires fetch');
    return Object.freeze({schema:SCHEMA,version:VERSION,name:String(source.name||'direct-backend'),mode:String(source.mode||'direct'),baseUrl,
      async request(request){
        const input=request&&typeof request==='object'?request:{}; const method=String(input.method||'GET').toUpperCase();
        const headers=Object.assign({Accept:'application/json'},input.headers||{}); const init={method,headers,credentials:String(input.credentials||'include')};
        if(input.signal)init.signal=input.signal;
        if(input.body!==undefined&&input.body!==null){
          if(typeof input.body==='string'||(typeof Blob!=='undefined'&&input.body instanceof Blob)||(typeof FormData!=='undefined'&&input.body instanceof FormData))init.body=input.body;
          else{if(!headers['Content-Type']&&!headers['content-type'])headers['Content-Type']='application/json';init.body=JSON.stringify(input.body);}
        }
        const response=await fetchImpl(join(baseUrl,input.path||''),init); const payload=await parse(response);
        if(!response.ok){const error=new Error(`Workspace transport request failed: HTTP ${response.status}`);error.status=response.status;error.payload=payload;throw error;}
        return payload;
      },
      inspect(){return Object.freeze({schema:'sc-workspace-transport-state/1.0',version:VERSION,name:String(source.name||'direct-backend'),mode:String(source.mode||'direct'),baseUrl,hostRequired:false,authenticationEmbedded:false});}
    });
  }
  return Object.freeze({schema:SCHEMA,version:VERSION,createDirect});
});
