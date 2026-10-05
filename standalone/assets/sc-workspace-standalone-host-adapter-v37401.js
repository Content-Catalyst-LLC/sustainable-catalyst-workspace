(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceStandaloneHostAdapter = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-standalone-host-adapter/1.0';
  const VERSION = '3.74.0.1';

  function create(config, contract) {
    const source = config && typeof config === 'object' ? config : {};
    const hostContract = contract && typeof contract.create === 'function' ? contract : null;

    if (hostContract) {
      const base = hostContract.create({
        host: 'standalone',
        workspaceVersion: String(source.workspaceVersion || VERSION),
        assetBase: String(source.assetBase || './assets/')
      });
      return Object.freeze({
        schema: SCHEMA,
        version: VERSION,
        name: 'standalone',
        configuration: base.configuration,
        resolveAsset: base.resolveAsset,
        capabilities() {
          return Object.freeze(Object.assign({}, base.capabilities(), {
            standaloneWebShell: true,
            directBackendTransport: true,
            wordpressRequired: false,
            hostAuthenticationRequired: false
          }));
        }
      });
    }

    const assetBase = String(source.assetBase || './assets/');
    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      name: 'standalone',
      configuration() {
        return Object.freeze({
          host: 'standalone',
          workspaceVersion: String(source.workspaceVersion || VERSION),
          assetBase
        });
      },
      resolveAsset(path) {
        const value = String(path || '').replace(/^\/+/, '');
        return assetBase.replace(/\/+$/, '') + '/' + value;
      },
      capabilities() {
        return Object.freeze({
          standaloneWebShell: true,
          directBackendTransport: true,
          wordpressRequired: false,
          hostAuthenticationRequired: false
        });
      }
    });
  }

  return Object.freeze({ schema: SCHEMA, version: VERSION, create });
});
