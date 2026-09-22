(function (global) {
  'use strict';
  const root = '/wp-json/sc-workspace/v1/backend/analytics';
  function request(path, options) {
    const opts = Object.assign({ credentials: 'same-origin', headers: {} }, options || {});
    if (opts.body && !opts.headers['Content-Type']) opts.headers['Content-Type'] = 'application/json';
    return fetch(root + path, opts).then(async function (response) {
      const body = await response.json().catch(function () { return {}; });
      if (!response.ok) throw new Error(body.message || body.detail || ('Workspace Analytics R HTTP ' + response.status));
      return body;
    });
  }
  global.SCWorkspaceCatalystAnalyticsR = Object.freeze({
    version: '3.5.0', providerKey: 'catalystanalyticsr', providerVersion: '2.1.0',
    profile: function () { return request('/providers/catalystanalyticsr'); },
    validate: function (envelope) { return request('/providers/catalystanalyticsr/validate', { method: 'POST', body: JSON.stringify(envelope) }); },
    execute: function (envelope) { return request('/providers/catalystanalyticsr/execute', { method: 'POST', body: JSON.stringify(envelope) }); },
    receipts: function (limit) { return request('/provider-receipts?limit=' + encodeURIComponent(limit || 100)); },
    receipt: function (receiptId) { return request('/provider-receipts/' + encodeURIComponent(receiptId)); }
  });
})(window);
