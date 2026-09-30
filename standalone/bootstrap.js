(() => {
  'use strict';

  const RELEASE = '3.46.6.0';
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

  function loadScript(path, marker) {
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = asset(path);
      script.async = false;
      script.dataset.scwsAsset = marker;
      script.onload = () => resolve(true);
      script.onerror = () => reject(new Error('Standalone Workspace asset failed: ' + marker));
      document.head.appendChild(script);
    });
  }

  async function boot() {
    status('Loading Workspace application kernel…');

    const assets = [
      ['sc-workspace-host-adapter-contract-v34620.js', 'host-contract'],
      ['sc-workspace-transport-v34620.js', 'transport'],
      ['sc-workspace-auth-context-v34620.js', 'auth'],
      ['sc-workspace-api-client-v34620.js', 'api-client'],
      ['sc-workspace-persistence-runtime-v34640.js', 'persistence'],
      ['sc-workspace-state-store-v34640.js', 'state-store'],
      ['sc-workspace-project-runtime-v34630.js', 'project-runtime'],
      ['sc-workspace-module-registry-v34650.js', 'module-registry'],
      ['sc-workspace-application-kernel-v34660.js', 'application-kernel'],
      ['sc-workspace-standalone-host-adapter-v34660.js', 'standalone-host-adapter'],
      ['sc-workspace-standalone-runtime-v34660.js', 'standalone-runtime'],
      ['workspace-standalone-shell-v34660.js', 'standalone-shell']
    ];

    for (const [path, marker] of assets) {
      await loadScript(path, marker);
    }

    const runtime = await window.SCWorkspaceStandaloneRuntimeFactory.create({
      config,
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
        wordpressRequired: false
      }
    }));
  }

  boot().catch((error) => {
    console.error(error);
    status('Workspace failed to initialize: ' + String(error && error.message || error), 'error');
  });
})();
