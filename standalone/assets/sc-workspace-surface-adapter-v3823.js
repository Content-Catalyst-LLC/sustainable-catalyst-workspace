(function(root){'use strict';
function boot(){try{root.SCSharedResearchSurface?.installStandalone()}catch(e){console.warn('Shared research surface context unavailable',e)}}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else queueMicrotask(boot);
})(globalThis);