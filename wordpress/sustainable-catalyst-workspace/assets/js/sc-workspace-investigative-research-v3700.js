(function (window) {
  'use strict';
  var root = '/wp-json/sc-workspace/v1/backend/investigative-research-workspace';
  function request(path, options) {
    options = options || {};
    options.credentials = 'same-origin';
    options.headers = Object.assign({'Content-Type':'application/json','X-WP-Nonce':(window.scWorkspaceConfig||{}).nonce||''}, options.headers||{});
    return window.fetch(path, options).then(function (response) {
      return response.json().then(function (body) {
        if (!response.ok) { var error = new Error((body && (body.message || body.detail)) || 'Workspace investigative research request failed'); error.status = response.status; error.body = body; throw error; }
        return body;
      });
    });
  }
  function enc(value){ return encodeURIComponent(String(value)); }
  function qs(params){ var q=Object.keys(params).filter(function(k){return params[k]!==undefined && params[k]!==null && params[k]!=='';}).map(function(k){return enc(k)+'='+enc(params[k]);}).join('&'); return q ? '?'+q : ''; }
  window.SCWorkspaceInvestigativeResearch = Object.freeze({
    version: '3.7.0', schema: 'sc-workspace-claims-evidence-investigative-research-workspace/1.0',
    profile: function(){ return request(root); },
    project: function(projectId, includeVisualGraph){ return request(root + '/projects/' + enc(projectId) + qs({includeVisualGraph: includeVisualGraph === false ? 'false' : 'true'})); },
    statements: function(projectId, statementType, limit){ return request(root + '/statements' + qs({projectId:projectId,statementType:statementType,limit:limit||250})); },
    statement: function(statementId){ return request(root + '/statements/' + enc(statementId)); },
    statementRevisions: function(statementId, limit){ return request(root + '/statements/' + enc(statementId) + '/revisions' + qs({limit:limit||100})); },
    storeStatement: function(payload){ return request(root + '/statements', {method:'POST', body:JSON.stringify(payload)}); },
    evidenceLinks: function(projectId, statementId, limit){ return request(root + '/evidence-links' + qs({projectId:projectId,statementId:statementId,limit:limit||500})); },
    createEvidenceLink: function(payload){ return request(root + '/evidence-links', {method:'POST', body:JSON.stringify(payload)}); },
    statementRelations: function(projectId, statementId, limit){ return request(root + '/statement-relations' + qs({projectId:projectId,statementId:statementId,limit:limit||500})); },
    createStatementRelation: function(payload){ return request(root + '/statement-relations', {method:'POST', body:JSON.stringify(payload)}); },
    snapshot: function(projectId, payload){ return request(root + '/projects/' + enc(projectId) + '/snapshots', {method:'POST', body:JSON.stringify(payload)}); },
    snapshots: function(projectId, limit){ return request(root + '/projects/' + enc(projectId) + '/snapshots' + qs({limit:limit||100})); }
  });
})(window);
