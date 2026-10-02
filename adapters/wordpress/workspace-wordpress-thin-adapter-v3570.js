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
    api.boot(root.SCWorkspaceWordPressBridge, { root, document: root.document }).catch((error) => {
      root.console && root.console.error && root.console.error('[Workspace thin adapter]', error);
      const node = root.document && root.document.querySelector ? root.document.querySelector('[data-sc-workspace]') : null;
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

  const SCHEMA = 'sc-workspace-wordpress-thin-adapter/1.1';
  const BRIDGE_SCHEMA = 'sc-workspace-wordpress-thin-bridge/1.1';
  const MANIFEST_SCHEMA = 'sc-workspace-runtime-asset-manifest/1.0';
  const VERSION = '3.57.0';

  function assertBridge(bridge) {
    if (!bridge || typeof bridge !== 'object') throw new Error('Workspace WordPress thin bridge is unavailable');
    if (String(bridge.schema || '') !== BRIDGE_SCHEMA) throw new Error('Workspace WordPress thin bridge schema mismatch');
    if (!String(bridge.assetManifestUrl || '').trim()) throw new Error('Workspace runtime asset manifest URL is unavailable');
    return bridge;
  }

  function browserScriptLoader(documentObject, url, marker) {
    return new Promise((resolve, reject) => {
      const documentRef = documentObject;
      if (!documentRef || typeof documentRef.createElement !== 'function') {
        reject(new Error('Workspace WordPress thin adapter requires a browser document'));
        return;
      }

      const selector = `script[data-scw-wordpress-thin-asset="${String(marker || 'asset')}"]`;
      const existing = documentRef.querySelector ? documentRef.querySelector(selector) : null;
      if (existing) {
        if (existing.dataset && existing.dataset.scwLoaded === '1') {
          resolve(true);
          return;
        }
        existing.addEventListener('load', () => resolve(true), { once: true });
        existing.addEventListener('error', () => reject(new Error('Workspace thin-adapter asset failed')), { once: true });
        return;
      }

      const script = documentRef.createElement('script');
      script.src = String(url);
      script.async = false;
      script.dataset.scwWordpressThinAsset = String(marker || 'asset');
      script.addEventListener('load', () => {
        script.dataset.scwLoaded = '1';
        resolve(true);
      }, { once: true });
      script.addEventListener('error', () => reject(new Error('Workspace thin-adapter asset failed: ' + marker)), { once: true });

      const target = documentRef.head || documentRef.body || documentRef.documentElement;
      if (!target || typeof target.appendChild !== 'function') {
        reject(new Error('Workspace thin-adapter asset has no document target'));
        return;
      }
      target.appendChild(script);
    });
  }

  function resolveAsset(base, manifest, id) {
    const entry = manifest && manifest.assets ? manifest.assets[id] : null;
    if (!entry || !entry.file) throw new Error('Workspace runtime asset missing from manifest: ' + id);
    try {
      return new URL(entry.file, String(base || '')).href;
    } catch (_) {
      return String(base || '') + String(entry.file);
    }
  }

  function buildConfig(bridge, manifest) {
    const source = bridge.config && typeof bridge.config === 'object' ? bridge.config : {};
    return Object.freeze(Object.assign({}, source, {
      host: 'wordpress',
      workspaceVersion: VERSION,
      assetManifest: manifest,
      assetManifestUrl: String(bridge.assetManifestUrl),
      hostAdapterMode: 'explicit-contract',
      wordpressRequired: false,
      wordpressThinAdapter: true,
      legacyPhpScriptGraphRetired: true,
      hostAgnosticAssetPipeline: true
    }));
  }

  function buildIdentity(bridge) {
    const source = bridge.identity && typeof bridge.identity === 'object' ? bridge.identity : {};
    return Object.freeze(Object.assign({}, source, {
      workspaceVersion: VERSION,
      frontendMode: 'host-neutral-core-with-wordpress-thin-adapter'
    }));
  }

  async function boot(bridgeInput, environment) {
    const bridge = assertBridge(bridgeInput);
    const env = environment && typeof environment === 'object' ? environment : {};
    const root = env.root || (typeof globalThis !== 'undefined' ? globalThis : {});
    const documentRef = env.document || root.document || null;
    const loadScript = typeof env.loadScript === 'function'
      ? env.loadScript
      : (url, marker) => browserScriptLoader(documentRef, url, marker);

    if (!(root.SCWorkspaceRuntimeAssetManifest && root.SCWorkspaceRuntimeAssetManifest.version === VERSION)) {
      await loadScript(String(bridge.assetManifestUrl), 'runtime-manifest');
    }

    const manifest = root.SCWorkspaceRuntimeAssetManifest;
    if (!manifest || manifest.schema !== MANIFEST_SCHEMA || manifest.version !== VERSION || manifest.host !== 'wordpress') {
      throw new Error('Workspace WordPress runtime asset manifest is invalid');
    }

    const config = buildConfig(bridge, manifest);
    const identity = buildIdentity(bridge);
    root.SCWorkspaceConfig = config;
    root.SCWorkspaceIdentity = identity;

    const entryPointUrl = resolveAsset(config.assetBase, manifest, 'application.entry');
    const state = {
      schema: 'sc-workspace-wordpress-thin-adapter-state/1.1',
      version: VERSION,
      host: 'wordpress',
      assetManifestUrl: String(bridge.assetManifestUrl),
      entryPointUrl,
      entryPointLoaded: false,
      runtimeManifestLoaded: true,
      phpScriptGraphRetired: true,
      applicationModuleBootOwnedByJavaScript: true,
      hostAgnosticAssetPipeline: true,
      wordpressRequiredByCore: false
    };
    root.SCWorkspaceWordPressThinAdapterState = state;

    const workspaceRoot = documentRef && documentRef.querySelector ? documentRef.querySelector('[data-sc-workspace]') : null;
    if (workspaceRoot) {
      workspaceRoot.dataset.scwHostAdapter = 'wordpress-thin';
      workspaceRoot.dataset.scwThinAdapterState = 'loading';
    }

    if (!(root.SCWorkspaceFrontendRuntime && String(root.SCWorkspaceFrontendRuntime.version || '') === VERSION)) {
      await loadScript(entryPointUrl, 'application-entry');
    }

    state.entryPointLoaded = true;

    if (workspaceRoot) {
      workspaceRoot.dataset.scwThinAdapterState = 'ready';
      workspaceRoot.dataset.scwThinAdapterVersion = VERSION;
    }

    return Object.freeze({
      schema: state.schema,
      version: VERSION,
      host: 'wordpress',
      runtimeManifestLoaded: true,
      entryPointLoaded: true,
      hostAgnosticAssetPipeline: true,
      wordpressRequiredByCore: false
    });
  }

  function inspect(rootInput) {
    const root = rootInput || (typeof globalThis !== 'undefined' ? globalThis : {});
    const state = root.SCWorkspaceWordPressThinAdapterState || {};
    return Object.freeze({
      schema: 'sc-workspace-wordpress-thin-adapter-inspection/1.1',
      version: VERSION,
      host: 'wordpress',
      bridgeReady: Boolean(root.SCWorkspaceWordPressBridge),
      runtimeManifestReady: Boolean(root.SCWorkspaceRuntimeAssetManifest),
      entryPointLoaded: Boolean(state.entryPointLoaded),
      hostAgnosticAssetPipeline: true,
      phpScriptGraphRetired: true,
      wordpressRequiredByCore: false
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    bridgeSchema: BRIDGE_SCHEMA,
    version: VERSION,
    resolveAsset,
    buildConfig,
    buildIdentity,
    boot,
    inspect
  });
});
