(function (window) {
  'use strict';
  var root = '/wp-json/sc-workspace/v1/backend/visual-research-workspace';
  function request(path, options) {
    options = options || {};
    options.credentials = 'same-origin';
    options.headers = Object.assign({'Content-Type':'application/json','X-WP-Nonce':(window.scWorkspaceConfig||{}).nonce||''}, options.headers||{});
    return window.fetch(path, options).then(function (response) {
      return response.json().then(function (body) {
        if (!response.ok) { var error = new Error((body && body.message) || 'Workspace visual research request failed'); error.status = response.status; error.body = body; throw error; }
        return body;
      });
    });
  }
  function enc(value){ return encodeURIComponent(String(value)); }
  window.SCWorkspaceVisualResearch = Object.freeze({
    version: '3.6.0', schema: 'sc-workspace-platform-core-visual-analysis-research-object-workspace/1.0',
    profile: function(){ return request(root); },
    project: function(projectId){ return request(root + '/projects/' + enc(projectId)); },
    visualization: function(projectId, visualizationId){ return request(root + '/projects/' + enc(projectId) + '/visualizations/' + enc(visualizationId)); },
    bind: function(projectId, visualizationId, payload){ return request(root + '/projects/' + enc(projectId) + '/visualizations/' + enc(visualizationId) + '/bind', {method:'POST', body:JSON.stringify(payload)}); },
    snapshot: function(projectId, payload){ return request(root + '/projects/' + enc(projectId) + '/snapshots', {method:'POST', body:JSON.stringify(payload)}); },
    snapshots: function(projectId, limit){ return request(root + '/projects/' + enc(projectId) + '/snapshots?limit=' + enc(limit || 100)); }
  });
})(window);
