(function(){
  'use strict';
  function esc(v){return String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function init(root){
    const H=window.SCWorkspaceProductHelp;if(!root||!H||root.dataset.scwProductHelpReady==='1')return;
    root.dataset.scwProductHelpReady='1';
    const section=root.querySelector('[data-scw-product-help]');if(!section)return;
    const input=section.querySelector('[data-scw-help-search]');const list=section.querySelector('[data-scw-help-list]');const status=section.querySelector('[data-scw-help-status]');const exportBtn=section.querySelector('[data-scw-help-export]');
    let active='';
    function render(items){
      if(!list)return;list.innerHTML='';
      if(!items.length){list.innerHTML='<div class="scw-help-empty">No help topics match that search.</div>';return;}
      items.forEach(t=>{const article=document.createElement('article');article.className='scw-help-topic';article.dataset.scwHelpTopic=t.id;article.innerHTML='<div class="scw-help-topic-head"><span>'+esc(t.category)+'</span><h3>'+esc(t.title)+'</h3></div><p>'+esc(t.summary)+'</p><ol>'+t.steps.map(s=>'<li>'+esc(s)+'</li>').join('')+'</ol><button class="scw-button" type="button" data-scw-help-route="'+esc(t.route)+'">Open related Workspace area</button>';article.addEventListener('focusin',()=>{active=t.id;});article.addEventListener('click',e=>{active=t.id;const b=e.target.closest('[data-scw-help-route]');if(b){const route=b.dataset.scwHelpRoute;const target=root.querySelector('[data-scw-workspace-view="'+route+'"]');if(target)target.click();}});list.appendChild(article);});
    }
    function filter(){const items=H.search(input?input.value:'');render(items);if(status)status.textContent=items.length+' help topic'+(items.length===1?'':'s')+' shown.';}
    if(input)input.addEventListener('input',filter);
    if(exportBtn)exportBtn.addEventListener('click',()=>{const report=H.report({workspaceVersion:(window.SCWorkspaceIdentity&&window.SCWorkspaceIdentity.workspaceVersion)||'',view:'help',topicId:active});const blob=new Blob([JSON.stringify(report,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='workspace-product-help-report.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),0);if(status)status.textContent='Privacy-minimized help context report exported.';});
    render(H.topics());
  }
  const boot=()=>document.querySelectorAll('[data-sc-workspace]').forEach(init);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
