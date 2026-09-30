(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceWordPressHostAdapter = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';

  const SCHEMA = 'sc-workspace-wordpress-host-adapter/1.0';
  const VERSION = '3.46.1.0';

  function create(config) {
    const source = config && typeof config === 'object' ? config : (root.SCWorkspaceConfig || {});
    const contract = root.SCWorkspaceHostAdapterContract;
    if (!contract || typeof contract.create !== 'function') {
      throw new Error('Workspace host adapter contract is unavailable');
    }

    const base = contract.create({
      host: 'wordpress',
      workspaceVersion: source.workspaceVersion || VERSION,
      assetBase: source.assetBase || '',
      apiBase: source.apiBase || '',
      transport: source.transport || 'wordpress-server-proxy',
      authenticated: Boolean(source.authenticated),
      displayName: String(source.displayName || ''),
      fetchImpl: async (url, options) => {
        const init = Object.assign({}, options || {});
        const headers = new Headers(init.headers || {});
        const identity = root.SCWorkspaceIdentity || {};
        if (identity.restNonce) headers.set('X-WP-Nonce', identity.restNonce);
        if (!headers.has('Accept')) headers.set('Accept', 'application/json');
        init.headers = headers;
        return fetch(url, init);
      }
    });

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      name: base.name,
      configuration: base.configuration,
      resolveAsset: base.resolveAsset,
      request: base.request,
      identity: base.identity,
      capabilities() {
        return Object.freeze(Object.assign({}, base.capabilities(), {
          serverProxyTransport: true,
          nonceAuthentication: Boolean((root.SCWorkspaceIdentity || {}).restNonce),
          applicationRuntimeRequired: false
        }));
      }
    });
  }

  return Object.freeze({ schema: SCHEMA, version: VERSION, create });
});
