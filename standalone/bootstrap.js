(() => {
  'use strict';

  const RELEASE = '3.75.0';
  const config = window.SCWorkspaceStandaloneConfig || {};

  const status = (message, state = 'loading') => {
    const node = document.querySelector('[data-scws-shell-status]');
    if (node) {
      node.textContent = message;
      node.dataset.state = state;
    }
  };

  function asset(path) {
    const base = String(config.assetBase || './assets/').replace(/\/+$/, '') + '/';
    return base + String(path || '').replace(/^\/+/, '') + '?ver=' + encodeURIComponent(RELEASE);
  }

  function loadScriptUrl(url, marker) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = String(url);
      script.async = false;
      script.dataset.scwsAsset = marker;
      script.onload = () => resolve(true);
      script.onerror = () => reject(new Error('Standalone Workspace asset failed: ' + marker));
      document.head.appendChild(script);
    });
  }

  async function loadManifest() {
    await loadScriptUrl(asset('sc-workspace-runtime-asset-manifest-v3750.js'), 'runtime-manifest');
    const manifest = window.SCWorkspaceRuntimeAssetManifest;
    if (!manifest || manifest.schema !== 'sc-workspace-runtime-asset-manifest/1.0' || manifest.version !== RELEASE || manifest.host !== 'standalone') {
      throw new Error('Standalone Workspace runtime asset manifest is invalid');
    }
    return manifest;
  }

  async function boot() {
    status('Loading Workspace runtime manifest…');
    const manifest = await loadManifest();

    status('Loading Workspace application kernel…');
    for (const id of manifest.loadOrder) {
      const entry = manifest.assets[id];
      if (!entry || !entry.file) throw new Error('Standalone Workspace manifest entry unavailable: ' + id);
      await loadScriptUrl(asset(entry.file), id);
    }

    const runtime = await window.SCWorkspaceStandaloneRuntimeFactory.create({
      config: Object.freeze(Object.assign({}, config, { assetManifest: manifest })),
      storage: window.localStorage,
      hostContract: window.SCWorkspaceHostAdapterContract,
      hostAdapterFactory: window.SCWorkspaceStandaloneHostAdapter,
      transportFactory: window.SCWorkspaceTransportFactory,
      authFactory: window.SCWorkspaceAuthContextFactory,
      apiFactory: window.SCWorkspaceApiClientFactory,
      persistenceFactory: window.SCWorkspacePersistenceRuntimeFactory,
      stateStoreFactory: window.SCWorkspaceStateStoreFactory,
      projectFactory: window.SCWorkspaceProjectRuntimeFactory,
      moduleRegistryFactory: window.SCWorkspaceModuleRegistryFactory,
      kernelFactory: window.SCWorkspaceApplicationKernelFactory,
      serverProjectBridgeFactory: window.SCWorkspaceServerProjectBridgeFactory,
      navigationLauncherFactory: window.SCWorkspaceNavigationLauncherFactory,
      researchObjectBrowserFactory: window.SCWorkspaceResearchObjectBrowserFactory,
      sourceEvidenceCitationFactory: window.SCWorkspaceSourceEvidenceCitationFactory,
      confirmDelete(project) {
        return window.confirm(`Delete “${project.title}” from this browser?`);
      },
      notifyFailure(message) {
        window.alert(message);
      },
      onIssue(issue) {
        console.warn('[Workspace standalone]', issue);
      }
    });

    window.SCWorkspaceStandaloneRuntime = runtime;
    window.SCWorkspaceApplicationKernel = runtime.kernel;
    window.SCWorkspaceModuleRegistry = runtime.moduleRegistry;
    window.SCWorkspaceProjectRuntime = runtime.projectRuntime;
    window.SCWorkspaceCanonicalStateStore = runtime.stateStore;
    window.SCWorkspaceCanonicalPersistence = runtime.persistence;

    document.documentElement.dataset.scWorkspaceHost = 'standalone';
    document.documentElement.dataset.scWorkspaceVersion = RELEASE;

    if (window.SCWorkspaceStandaloneShell && typeof window.SCWorkspaceStandaloneShell.boot === 'function') {
      await window.SCWorkspaceStandaloneShell.boot(runtime);
    }

    status('Workspace ready', 'ready');
    document.dispatchEvent(new CustomEvent('sc-workspace-standalone:ready', {
      detail: {
        version: RELEASE,
        host: 'standalone',
        hostAgnosticAssetPipeline: true,
        wordpressRequired: false
      }
    }));
  }

  boot().catch((error) => {
    console.error(error);
    status('Workspace failed to initialize: ' + String(error && error.message || error), 'error');
  });
})();
