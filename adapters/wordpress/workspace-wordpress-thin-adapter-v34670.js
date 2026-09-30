(function (root, factory) {
  'use strict';

  const api = factory();

  if (typeof module === 'object' && module.exports) {
    module.exports = api;
    return;
  }

  root.SCWorkspaceWordPressThinAdapter = api;

  function start() {
    if (!root.SCWorkspaceWordPressBridge) return;
    api.boot(root.SCWorkspaceWordPressBridge, {
      root,
      document: root.document
    }).catch((error) => {
      root.console && root.console.error && root.console.error('[Workspace thin adapter]', error);
      const node = root.document && root.document.querySelector
        ? root.document.querySelector('[data-sc-workspace]')
        : null;
      if (node) {
        node.dataset.scwThinAdapterState = 'failed';
        node.dataset.scwThinAdapterError = String(error && error.message || error).slice(0, 240);
      }
    });
  }

  if (root.document) {
    if (root.document.readyState === 'loading') {
      root.document.addEventListener('DOMContentLoaded', start, { once: true });
    } else {
      start();
    }
  }
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-wordpress-thin-adapter/1.0';
  const BRIDGE_SCHEMA = 'sc-workspace-wordpress-thin-bridge/1.0';
  const VERSION = '3.46.7.0';

  function assertBridge(bridge) {
    if (!bridge || typeof bridge !== 'object') {
      throw new Error('Workspace WordPress thin bridge is unavailable');
    }
    if (String(bridge.schema || '') !== BRIDGE_SCHEMA) {
      throw new Error('Workspace WordPress thin bridge schema mismatch');
    }
    if (!String(bridge.entryPointUrl || '').trim()) {
      throw new Error('Workspace WordPress application entry point is unavailable');
    }
    return bridge;
  }

  function buildConfig(bridgeInput) {
    const bridge = assertBridge(bridgeInput);
    const source = bridge.config && typeof bridge.config === 'object' ? bridge.config : {};
    return Object.freeze(Object.assign({}, source, {
      host: 'wordpress',
      workspaceVersion: String(bridge.workspaceVersion || VERSION),
      hostAdapterMode: 'explicit-contract',
      wordpressRequired: false,
      wordpressThinAdapter: true,
      legacyPhpScriptGraphRetired: true
    }));
  }

  function buildIdentity(bridgeInput) {
    const bridge = assertBridge(bridgeInput);
    const source = bridge.identity && typeof bridge.identity === 'object' ? bridge.identity : {};
    return Object.freeze(Object.assign({}, source, {
      workspaceVersion: String(bridge.workspaceVersion || VERSION),
      frontendMode: 'host-neutral-core-with-wordpress-thin-adapter'
    }));
  }

  function browserScriptLoader(documentObject, url) {
    return new Promise((resolve, reject) => {
      const documentRef = documentObject;
      if (!documentRef || typeof documentRef.createElement !== 'function') {
        reject(new Error('Workspace WordPress thin adapter requires a browser document'));
        return;
      }

      const existing = documentRef.querySelector
        ? documentRef.querySelector('script[data-scw-wordpress-thin-entry="1"]')
        : null;
      if (existing) {
        if (existing.dataset && existing.dataset.scwLoaded === '1') {
          resolve(true);
          return;
        }
        existing.addEventListener('load', () => resolve(true), { once: true });
        existing.addEventListener('error', () => reject(new Error('Workspace application entry point failed')), { once: true });
        return;
      }

      const script = documentRef.createElement('script');
      script.src = String(url);
      script.async = false;
      script.dataset.scwWordpressThinEntry = '1';
      script.addEventListener('load', () => {
        script.dataset.scwLoaded = '1';
        resolve(true);
      }, { once: true });
      script.addEventListener('error', () => reject(new Error('Workspace application entry point failed')), { once: true });

      const target = documentRef.head || documentRef.body || documentRef.documentElement;
      if (!target || typeof target.appendChild !== 'function') {
        reject(new Error('Workspace application entry point has no document target'));
        return;
      }
      target.appendChild(script);
    });
  }

  async function boot(bridgeInput, environment) {
    const bridge = assertBridge(bridgeInput);
    const env = environment && typeof environment === 'object' ? environment : {};
    const root = env.root || (typeof globalThis !== 'undefined' ? globalThis : {});
    const documentRef = env.document || root.document || null;
    const loadScript = typeof env.loadScript === 'function'
      ? env.loadScript
      : (url) => browserScriptLoader(documentRef, url);

    const config = buildConfig(bridge);
    const identity = buildIdentity(bridge);

    root.SCWorkspaceConfig = config;
    root.SCWorkspaceIdentity = identity;

    const state = {
      schema: 'sc-workspace-wordpress-thin-adapter-state/1.0',
      version: VERSION,
      host: 'wordpress',
      bridgeSchema: bridge.schema,
      entryPointUrl: String(bridge.entryPointUrl),
      bootStartedAt: new Date().toISOString(),
      bootCompletedAt: null,
      entryPointLoaded: false,
      phpScriptGraphRetired: true,
      applicationModuleBootOwnedByJavaScript: true,
      projectLogicOwnedByWordPress: false,
      stateOwnedByWordPress: false,
      wordpressRequiredByCore: false
    };

    root.SCWorkspaceWordPressThinAdapterState = state;

    const workspaceRoot = documentRef && documentRef.querySelector
      ? documentRef.querySelector('[data-sc-workspace]')
      : null;
    if (workspaceRoot) {
      workspaceRoot.dataset.scwHostAdapter = 'wordpress-thin';
      workspaceRoot.dataset.scwThinAdapterState = 'loading';
    }

    if (!(root.SCWorkspaceFrontendRuntime && String(root.SCWorkspaceFrontendRuntime.version || '') === VERSION)) {
      await loadScript(String(bridge.entryPointUrl));
    }

    state.entryPointLoaded = true;
    state.bootCompletedAt = new Date().toISOString();

    if (workspaceRoot) {
      workspaceRoot.dataset.scwThinAdapterState = 'ready';
      workspaceRoot.dataset.scwThinAdapterVersion = VERSION;
    }

    return Object.freeze({
      schema: state.schema,
      version: VERSION,
      host: 'wordpress',
      entryPointLoaded: true,
      phpScriptGraphRetired: true,
      wordpressRequiredByCore: false
    });
  }

  function inspect(rootInput) {
    const root = rootInput || (typeof globalThis !== 'undefined' ? globalThis : {});
    const state = root.SCWorkspaceWordPressThinAdapterState || {};
    return Object.freeze({
      schema: 'sc-workspace-wordpress-thin-adapter-inspection/1.0',
      version: VERSION,
      host: 'wordpress',
      bridgeReady: Boolean(root.SCWorkspaceWordPressBridge),
      configReady: Boolean(root.SCWorkspaceConfig),
      identityReady: Boolean(root.SCWorkspaceIdentity),
      entryPointLoaded: Boolean(state.entryPointLoaded),
      phpScriptGraphRetired: true,
      applicationModuleBootOwnedByJavaScript: true,
      wordpressRequiredByCore: false
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    bridgeSchema: BRIDGE_SCHEMA,
    version: VERSION,
    buildConfig,
    buildIdentity,
    boot,
    inspect
  });
});
