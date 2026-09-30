(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceHostAdapterContract = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-host-adapter-contract/1.0';
  const VERSION = '3.46.1.0';
  const REQUIRED_METHODS = Object.freeze([
    'name',
    'configuration',
    'resolveAsset',
    'request',
    'identity',
    'capabilities'
  ]);

  function normalizeName(value) {
    const name = String(value || 'standalone').trim().toLowerCase();
    return name || 'standalone';
  }

  function validate(adapter) {
    const missing = [];
    if (!adapter || typeof adapter !== 'object') {
      return { ok: false, schema: SCHEMA, version: VERSION, missing: [...REQUIRED_METHODS] };
    }
    REQUIRED_METHODS.forEach((key) => {
      if (key === 'name') {
        if (!String(adapter.name || '').trim()) missing.push(key);
      } else if (typeof adapter[key] !== 'function') {
        missing.push(key);
      }
    });
    return { ok: missing.length === 0, schema: SCHEMA, version: VERSION, missing };
  }

  function create(config) {
    const source = config && typeof config === 'object' ? config : {};
    const hostName = normalizeName(source.host);
    const assetBase = String(source.assetBase || '').trim();
    const apiBase = String(source.apiBase || '').trim();

    const adapter = {
      schema: SCHEMA,
      version: VERSION,
      name: hostName,
      configuration() {
        return Object.freeze({
          host: hostName,
          workspaceVersion: String(source.workspaceVersion || VERSION),
          assetBase,
          apiBase,
          transport: String(source.transport || 'direct'),
          authenticated: Boolean(source.authenticated)
        });
      },
      resolveAsset(path) {
        const value = String(path || '').replace(/^\/+/, '');
        if (!assetBase) return value;
        try {
          return new URL(value, assetBase.endsWith('/') ? assetBase : assetBase + '/').href;
        } catch (_) {
          return assetBase.replace(/\/+$/, '') + '/' + value;
        }
      },
      async request(path, options) {
        const fetchImpl = source.fetchImpl || (typeof fetch === 'function' ? fetch.bind(globalThis) : null);
        if (!fetchImpl) throw new Error('Workspace host adapter has no fetch implementation');
        const raw = String(path || '');
        let url = raw;
        if (!/^https?:\/\//i.test(raw) && apiBase) {
          url = apiBase.replace(/\/+$/, '') + '/' + raw.replace(/^\/+/, '');
        }
        return fetchImpl(url, options || {});
      },
      identity() {
        return Object.freeze({
          authenticated: Boolean(source.authenticated),
          displayName: String(source.displayName || ''),
          host: hostName
        });
      },
      capabilities() {
        return Object.freeze({
          hostConfiguration: true,
          assetResolution: true,
          transport: Boolean(apiBase || source.fetchImpl || typeof fetch === 'function'),
          authenticationContext: true,
          applicationRuntimeRequired: false
        });
      }
    };

    const result = validate(adapter);
    if (!result.ok) throw new Error('Invalid Workspace host adapter: ' + result.missing.join(', '));
    return Object.freeze(adapter);
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    requiredMethods: REQUIRED_METHODS,
    validate,
    create
  });
});
