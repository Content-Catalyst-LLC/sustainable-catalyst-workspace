(function(){
  'use strict';
  function boot(){
    const root=document.querySelector('[data-sc-workspace]'),api=window.SCWorkspaceWorkflowGuidance;
    if(!root||!api)return;
    const q=s=>root.querySelector(s),num=s=>Number(q(s)?.textContent||0)||0;
    const guidance=q('[data-scw-workflow-guidance]'),stage=q('[data-scw-workflow-guidance-stage]'),title=q('[data-scw-workflow-guidance-title]'),detail=q('[data-scw-workflow-guidance-detail]'),action=q('[data-scw-workflow-guidance-action]');
    const compact=q('[data-scw-project-research-guidance]'),compactStage=q('[data-scw-project-guidance-stage]'),compactTitle=q('[data-scw-project-guidance-title]'),compactDetail=q('[data-scw-project-guidance-detail]'),compactAction=q('[data-scw-project-guidance-action]');
    function current(){
      const active=q('[data-scw-active-project]');
      return api.snapshot({hasProject:Boolean(active&&!active.hidden),projectCount:num('[data-scw-beta-projects]'),questions:num('[data-scw-research-metric-questions]'),sources:num('[data-scw-research-metric-sources]'),evidence:num('[data-scw-research-metric-evidence]'),claims:num('[data-scw-research-metric-claims]'),notebookBlocks:num('[data-scw-notebook-metric-blocks]'),researchRecords:num('[data-scw-integrated-records]'),researchTasks:num('[data-scw-task-open]')+num('[data-scw-task-progress]')+num('[data-scw-task-blocked]'),documents:root.querySelectorAll('[data-scw-composition-card]').length});
    }
    function apply(elStage,elTitle,elDetail,elAction,step){if(elStage)elStage.textContent=`${step.stage} / CONTEXTUAL NEXT STEP`;if(elTitle)elTitle.textContent=step.title;if(elDetail)elDetail.textContent=step.detail;if(elAction){elAction.textContent=step.action;elAction.dataset.scwGuidanceView=step.view||'';elAction.dataset.scwGuidanceMode=step.mode||'';elAction.dataset.scwGuidanceSurface=step.surface||'';}}
    function refresh(){const step=api.nextStep(current());apply(stage,title,detail,action,step);apply(compactStage,compactTitle,compactDetail,compactAction,step);if(guidance)guidance.dataset.scwGuidanceStep=step.id;if(compact)compact.dataset.scwGuidanceStep=step.id;}
    function activate(button){const view=button.dataset.scwGuidanceView||'',mode=button.dataset.scwGuidanceMode||'',surface=button.dataset.scwGuidanceSurface||'';if(view){const b=q(`[data-scw-workspace-view="${view}"]`);b?.click();}if(mode){setTimeout(()=>q(`[data-scw-project-mode="${mode}"]`)?.click(),0);}if(surface){setTimeout(()=>q(`[data-scw-research-surface="${surface}"]`)?.click(),20);}setTimeout(refresh,50);}
    [action,compactAction].forEach(button=>button?.addEventListener('click',()=>activate(button)));
    root.addEventListener('click',()=>setTimeout(refresh,40));
    root.addEventListener('change',()=>setTimeout(refresh,40));
    window.addEventListener('sc-workspace-state-updated',refresh);
    refresh();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
