/* Workspace v3.65.0 — Standalone Frontend Runtime & Project Creation Repair */
(() => {
  'use strict';

  const WORKSPACE_RELEASE = '3.65.0';
  const rootSelector = '[data-sc-workspace]';
  const runtimeScript = document.currentScript;
  const wordpressIdentity = window.SCWorkspaceIdentity || {};
  const hostConfig = window.SCWorkspaceConfig || {};
  const identity = Object.assign({}, wordpressIdentity, hostConfig);
  const hostName = String(hostConfig.host || identity.host || (window.SCWorkspaceIdentity ? 'wordpress' : 'standalone'));

  const interactionRuntime = window.SCWorkspaceInteractionRuntime =
    window.SCWorkspaceInteractionRuntime || {
      schema: 'sc-workspace-interaction-runtime/1.0',
      version: WORKSPACE_RELEASE,
      ready: false,
      issues: [],
      unhandledErrors: []
    };

  interactionRuntime.version = WORKSPACE_RELEASE;
  interactionRuntime.issues = interactionRuntime.issues || [];
  interactionRuntime.unhandledErrors = interactionRuntime.unhandledErrors || [];

  window.SCWorkspaceHostBoundary = Object.freeze({
    schema: 'sc-workspace-host-boundary/1.0',
    version: WORKSPACE_RELEASE,
    host: hostName,
    wordpressRequiredForApplicationBoot: false,
    wordpressRequiredForProjectInteraction: false,
    hostProvidesConfigurationOnly: true,
    hostSpecificTransportMayBeProvided: true,
    applicationOwnsInteractionRuntime: true,
    optionalModuleFailureBlocksBoot: false
  });

  window.SCWorkspaceInteractionRepair = window.SCWorkspaceInteractionRepair || Object.freeze({
    schema: 'sc-workspace-interaction-repair/1.0',
    version: WORKSPACE_RELEASE,
    delegatedFallback: true
  });

  window.SCWorkspaceThinClientStateBoundary = Object.freeze({
    schema: 'sc-workspace-thin-client-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    canonicalMutations: 'command-api-only',
    persistentBrowserState: 'transient-only'
  });

  window.SCWorkspaceLocalFirstSyncBoundary = Object.freeze({
    schema: 'sc-workspace-local-first-sync-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    offlineOutboxAuthoritative: false,
    pendingMutationsAreDrafts: true,
    automaticSemanticMerge: false
  });

  window.SCWorkspaceScientificObjectBoundary = Object.freeze({
    schema: 'sc-workspace-scientific-object-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    genericMutation: false,
    canonicalCachePersistent: false
  });

  window.SCWorkspaceResearchHandoffBoundary = Object.freeze({
    schema: 'sc-workspace-research-handoff-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    genericDestinationMutation: false,
    revisionPinning: true,
    fingerprintPinning: true
  });

  window.SCWorkspaceAuthorizationBoundary = Object.freeze({
    schema: 'sc-workspace-authorization-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendAuthoritative: true,
    browserAuthoritativeAuthorization: false,
    clientSuppliedRolesTrusted: false,
    clientSuppliedScopesTrusted: false,
    defaultEffect: 'deny'
  });

  window.SCWorkspaceBackendNativeBoundary = Object.freeze({
    schema: 'sc-workspace-backend-native-scientific-workspace-client-boundary/1.0',
    version: WORKSPACE_RELEASE,
    backendNative: true,
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    browserAuthoritativeAuthorization: false,
    signedInLocalCanonicalFallback: false,
    canonicalStore: 'postgresql',
    canonicalDomainRuntime: 'python',
    scientificExecutionAuthority: 'bounded-internal-runtime-services',
    runtimeArbitraryCodeExecution: false
  });

  let compatPromise = null;
  let initPromise = null;

  const assetManifest = hostConfig.assetManifest || window.SCWorkspaceRuntimeAssetManifest || null;

  function resolveManifestAsset(logicalId) {
    const assets = assetManifest && assetManifest.assets ? assetManifest.assets : null;
    const entry = assets && logicalId ? assets[logicalId] : null;
    return entry && entry.file ? String(entry.file) : '';
  }

  function assetUrl(fileName, logicalId) {
    const manifestFile = resolveManifestAsset(logicalId);
    const resolvedFile = manifestFile || fileName;
    const configuredBase = String(hostConfig.assetBase || identity.assetBase || '').trim();
    if (configuredBase) {
      try {
        return new URL(resolvedFile, configuredBase.endsWith('/') ? configuredBase : configuredBase + '/').href;
      } catch (_) {}
    }
    if (runtimeScript && runtimeScript.src) {
      try {
        return new URL(resolvedFile, runtimeScript.src).href;
      } catch (_) {}
    }
    return 'assets/js/' + resolvedFile;
  }

  function compatibilityUrl() {
    const raw = String(
      hostConfig.legacyCompatUrl ||
      identity.legacyCompatUrl ||
      assetUrl('sc-workspace-local-project-compat-v3650.js', 'compatibility.runtime')
    ).trim();
    if (!raw) return '';
    try {
      const parsed = new URL(raw, window.location.href);
      parsed.searchParams.set('ver', WORKSPACE_RELEASE);
      return parsed.href;
    } catch (_) {
      const separator = raw.includes('?') ? '&' : '?';
      return raw + separator + 'ver=' + encodeURIComponent(WORKSPACE_RELEASE);
    }
  }

  function versionedAssetUrl(raw) {
    const value = String(raw || '').trim();
    if (!value) return '';
    try {
      const parsed = new URL(value, window.location.href);
      parsed.searchParams.set('ver', WORKSPACE_RELEASE);
      return parsed.href;
    } catch (_) {
      const separator = value.includes('?') ? '&' : '?';
      return value + separator + 'ver=' + encodeURIComponent(WORKSPACE_RELEASE);
    }
  }

  function loadScriptAsset(url, marker) {
    if (!url) return Promise.reject(new Error('Workspace application asset URL unavailable: ' + marker));
    const selector = `script[data-scw-application-asset="${marker}"]`;
    const existing = document.querySelector(selector);
    if (existing && existing.dataset.scwApplicationRelease === WORKSPACE_RELEASE) {
      return Promise.resolve(true);
    }
    if (existing) existing.remove();
    return new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = versionedAssetUrl(url);
      script.async = false;
      script.dataset.scwApplicationAsset = marker;
      script.dataset.scwApplicationRelease = WORKSPACE_RELEASE;
      script.onload = () => resolve(true);
      script.onerror = () => reject(new Error('Workspace application asset failed to load: ' + marker));
      document.head.appendChild(script);
    });
  }

  async function loadApplicationKernel() {
    const contractUrl = hostConfig.hostAdapterContractUrl || assetUrl('sc-workspace-host-adapter-contract-v34620.js', 'host.contract');
    const transportUrl = hostConfig.transportRuntimeUrl || assetUrl('sc-workspace-transport-v34620.js', 'client.transport');
    const authUrl = hostConfig.authContextRuntimeUrl || assetUrl('sc-workspace-auth-context-v34620.js', 'client.auth');
    const apiUrl = hostConfig.apiClientRuntimeUrl || assetUrl('sc-workspace-api-client-v34620.js', 'client.api');
    const persistenceRuntimeUrl = hostConfig.persistenceRuntimeUrl || assetUrl('sc-workspace-persistence-runtime-v34640.js', 'state.persistence');
    const stateStoreRuntimeUrl = hostConfig.stateStoreRuntimeUrl || assetUrl('sc-workspace-state-store-v34640.js', 'state.store');
    const projectRuntimeUrl = hostConfig.projectRuntimeUrl || assetUrl('sc-workspace-project-runtime-v34630.js', 'projects.runtime');
    const moduleRegistryUrl = hostConfig.moduleRegistryUrl || assetUrl('sc-workspace-module-registry-v34650.js', 'modules.registry');
    const kernelUrl = hostConfig.applicationKernelUrl || assetUrl('sc-workspace-application-kernel-v3650.js', 'application.kernel');
    const adapterUrl = String(hostConfig.hostAdapterUrl || '').trim();
    const transportAdapterUrl = String(hostConfig.transportAdapterUrl || '').trim();
    const authAdapterUrl = String(hostConfig.authAdapterUrl || '').trim();
    await loadScriptAsset(contractUrl, 'host-adapter-contract');
    await loadScriptAsset(transportUrl, 'transport-runtime');
    await loadScriptAsset(authUrl, 'auth-context-runtime');
    await loadScriptAsset(apiUrl, 'api-client-runtime');
    await loadScriptAsset(persistenceRuntimeUrl, 'persistence-runtime');
    await loadScriptAsset(stateStoreRuntimeUrl, 'state-store-runtime');
    await loadScriptAsset(projectRuntimeUrl, 'project-runtime');
    await loadScriptAsset(moduleRegistryUrl, 'module-registry');
    await loadScriptAsset(kernelUrl, 'application-kernel');
    if (adapterUrl) await loadScriptAsset(adapterUrl, 'host-adapter');
    if (transportAdapterUrl) await loadScriptAsset(transportAdapterUrl, 'transport-adapter');
    if (authAdapterUrl) await loadScriptAsset(authAdapterUrl, 'auth-adapter');
    const contract = window.SCWorkspaceHostAdapterContract;
    const transportFactory = window.SCWorkspaceTransportFactory;
    const authFactory = window.SCWorkspaceAuthContextFactory;
    const apiFactory = window.SCWorkspaceApiClientFactory;
    const persistenceRuntimeFactory = window.SCWorkspacePersistenceRuntimeFactory;
    const stateStoreFactory = window.SCWorkspaceStateStoreFactory;
    const projectRuntimeFactory = window.SCWorkspaceProjectRuntimeFactory;
    const moduleRegistryFactory = window.SCWorkspaceModuleRegistryFactory;
    const kernelFactory = window.SCWorkspaceApplicationKernelFactory;
    if (!contract || typeof contract.create !== 'function') throw new Error('Workspace host adapter contract unavailable after load');
    if (!transportFactory || typeof transportFactory.createDirect !== 'function') throw new Error('Workspace transport runtime unavailable after load');
    if (!authFactory || typeof authFactory.createAnonymous !== 'function') throw new Error('Workspace auth runtime unavailable after load');
    if (!apiFactory || typeof apiFactory.create !== 'function') throw new Error('Workspace API client runtime unavailable after load');
    if (!persistenceRuntimeFactory || typeof persistenceRuntimeFactory.create !== 'function') throw new Error('Workspace persistence runtime unavailable after load');
    if (!stateStoreFactory || typeof stateStoreFactory.create !== 'function') throw new Error('Workspace state store unavailable after load');
    if (!projectRuntimeFactory || typeof projectRuntimeFactory.create !== 'function') throw new Error('Workspace project runtime unavailable after load');
    if (!moduleRegistryFactory || typeof moduleRegistryFactory.create !== 'function') throw new Error('Workspace module registry unavailable after load');
    if (!kernelFactory || typeof kernelFactory.createKernel !== 'function') throw new Error('Workspace application kernel unavailable after load');
    const hostAdapter = (adapterUrl && window.SCWorkspaceWordPressHostAdapter && typeof window.SCWorkspaceWordPressHostAdapter.create === 'function') ? window.SCWorkspaceWordPressHostAdapter.create(hostConfig) : contract.create(Object.assign({}, hostConfig, { host: hostName }));
    const transport = (transportAdapterUrl && window.SCWorkspaceWordPressTransportAdapter && typeof window.SCWorkspaceWordPressTransportAdapter.create === 'function') ? window.SCWorkspaceWordPressTransportAdapter.create(hostConfig) : transportFactory.createDirect({name:'direct-backend',baseUrl:String(hostConfig.directApiBase || hostConfig.apiBase || '').trim()});
    const auth = (authAdapterUrl && window.SCWorkspaceWordPressAuthAdapter && typeof window.SCWorkspaceWordPressAuthAdapter.create === 'function') ? window.SCWorkspaceWordPressAuthAdapter.create(hostConfig) : authFactory.createAnonymous();
    const apiClient = apiFactory.create({ transport, auth });
    const moduleRegistry = moduleRegistryFactory.create({
      onIssue(issue) {
        interactionRuntime.issues.push({
          type: 'module-registry',
          detail: `${issue.moduleId}: ${issue.type}: ${issue.detail}`,
          at: issue.at
        });
      }
    });

    moduleRegistry.registerReady({
      id: 'core.host-adapter',
      version: WORKSPACE_RELEASE,
      optional: false,
      capabilities: ['workspace.host']
    }, hostAdapter);
    moduleRegistry.registerReady({
      id: 'core.transport',
      version: WORKSPACE_RELEASE,
      optional: false,
      capabilities: ['workspace.transport']
    }, transport);
    moduleRegistry.registerReady({
      id: 'core.auth',
      version: WORKSPACE_RELEASE,
      optional: false,
      capabilities: ['workspace.auth']
    }, auth);
    moduleRegistry.registerReady({
      id: 'core.api',
      version: WORKSPACE_RELEASE,
      optional: false,
      dependsOn: ['core.transport', 'core.auth'],
      capabilities: ['workspace.api']
    }, apiClient);
    const kernel = kernelFactory.createKernel({ hostConfig });
    kernel.registerModuleRegistry(moduleRegistry);
    kernel.registerHostAdapter(hostAdapter); kernel.registerTransport(transport); kernel.registerAuth(auth); kernel.registerApiClient(apiClient); await kernel.boot();
    window.SCWorkspaceApplicationKernel = kernel; window.SCWorkspaceDecoupledApiClient = apiClient;
    interactionRuntime.applicationKernelReady = true; interactionRuntime.moduleRegistryReady = true; interactionRuntime.hostAdapterReady = true; interactionRuntime.transportReady = true; interactionRuntime.authReady = true; interactionRuntime.apiClientReady = true; interactionRuntime.applicationKernel = kernel.inspect();
    return kernel;
  }

  function resolveGlobalPath(path) {
    const parts = String(path || '').split('.').map((part) => part.trim()).filter(Boolean);
    let value = window;
    for (const part of parts) {
      if (value == null) return null;
      value = value[part];
    }
    return value || null;
  }

  function registerCoreModuleCapabilities() {
    const registry = window.SCWorkspaceModuleRegistry;
    return registry && typeof registry.inspect === 'function' ? registry.inspect() : null;
  }

  async function loadOptionalModules() {
    const moduleRegistry = window.SCWorkspaceModuleRegistry;
    if (!moduleRegistry || typeof moduleRegistry.register !== 'function') return null;

    const declarations = Array.isArray(hostConfig.optionalModules) ? hostConfig.optionalModules : [];
    declarations.forEach((descriptor) => {
      const source = descriptor && typeof descriptor === 'object' ? descriptor : {};
      const id = String(source.id || '').trim();
      if (!id || moduleRegistry.state(id)) return;

      moduleRegistry.register({
        id,
        version: String(source.version || WORKSPACE_RELEASE),
        title: String(source.title || id),
        optional: source.optional !== false,
        enabled: source.enabled !== false,
        dependsOn: Array.isArray(source.dependsOn) ? source.dependsOn : [],
        capabilities: Array.isArray(source.capabilities) ? source.capabilities : [],
        source: String(source.source || hostName)
      }, async () => {
        const assetId = String(source.assetId || '').trim();
        const url = assetId ? assetUrl('', assetId) : String(source.url || '').trim();
        if (url) await loadScriptAsset(url, 'optional-' + id.replace(/[^a-z0-9_-]+/gi, '-'));
        const provider = source.global ? resolveGlobalPath(source.global) : null;
        if (source.global && !provider) throw new Error('Optional module global unavailable: ' + source.global);
        return provider;
      });
    });

    try {
      const result = await moduleRegistry.loadAll({
        kernel: window.SCWorkspaceApplicationKernel,
        frontend: window.SCWorkspaceFrontendRuntime,
        host: hostName
      });
      interactionRuntime.optionalModulesLoaded = true;
      interactionRuntime.moduleRegistry = result;
      return result;
    } catch (error) {
      recordIssue('optional-module-load', String(error && error.message || error));
      interactionRuntime.optionalModulesLoaded = false;
      return moduleRegistry.inspect();
    }
  }

  function recordIssue(type, detail) {
    interactionRuntime.issues.push({
      type: String(type || 'runtime'),
      detail: String(detail || ''),
      at: new Date().toISOString()
    });
  }

  function loadCompat(reason) {
    if (compatPromise) return compatPromise;

    let existing = document.querySelector('script[data-scw-local-compatibility="1"]');
    const url = compatibilityUrl();
    if (!url) return Promise.reject(new Error('Workspace compatibility runtime URL unavailable'));

    let expectedUrl = url;
    try { expectedUrl = new URL(url, window.location.href).href; } catch (_) {}
    const existingMatches = Boolean(
      existing &&
      existing.dataset.scwCompatibilityRelease === WORKSPACE_RELEASE &&
      existing.src === expectedUrl
    );

    if (existing && !existingMatches) {
      recordIssue('compatibility-cache-replacement', existing.src || 'stale compatibility runtime');
      existing.remove();
      existing = null;
      interactionRuntime.compatibilityLoaded = false;
    }

    if (existing && interactionRuntime.compatibilityLoaded) {
      return Promise.resolve(true);
    }

    interactionRuntime.compatibilityReason = reason || 'core-interaction-continuity';
    compatPromise = new Promise((resolve, reject) => {
      const script = existing || document.createElement('script');

      if (!existing) {
        script.src = url;
        script.async = false;
        script.dataset.scwLocalCompatibility = '1';
        script.dataset.scwCompatibilityRelease = WORKSPACE_RELEASE;
      }

      const loaded = () => {
        interactionRuntime.compatibilityLoaded = true;
        interactionRuntime.compatibilityUrl = url;
        document.dispatchEvent(new CustomEvent('sc-workspace:interaction-runtime-ready', {
          detail: { version: WORKSPACE_RELEASE, host: hostName, compatibilityRuntime: true }
        }));
        resolve(true);
      };

      const failed = () => {
        compatPromise = null;
        recordIssue('compatibility-load', 'failed: ' + url);
        reject(new Error('Workspace interaction compatibility runtime failed to load'));
      };

      if (existing) {
        existing.addEventListener('load', loaded, { once: true });
        existing.addEventListener('error', failed, { once: true });
      } else {
        script.onload = loaded;
        script.onerror = failed;
        document.head.appendChild(script);
      }
    });

    return compatPromise;
  }

  async function hydrateBackend() {
    const api = window.SCWorkspaceApi;
    if (!api) {
      interactionRuntime.backendHydration = 'api-client-unavailable-at-bootstrap';
      return false;
    }

    try {
      if (typeof api.backendNativeBootstrap === 'function') {
        await api.backendNativeBootstrap();
      } else {
        if (typeof api.frontendRuntime === 'function') await api.frontendRuntime();
        if (window.SCWorkspaceState && typeof window.SCWorkspaceState.hydrate === 'function') {
          await window.SCWorkspaceState.hydrate();
        }
      }
      interactionRuntime.backendHydration = 'ready';
      document.dispatchEvent(new CustomEvent('sc-workspace:backend-hydrated', {
        detail: { version: WORKSPACE_RELEASE, host: hostName }
      }));
      return true;
    } catch (error) {
      interactionRuntime.backendHydration = 'failed';
      recordIssue('backend-hydration', String(error && error.message || error));
      return false;
    }
  }

  function markReady() {
    document.querySelectorAll(rootSelector).forEach(root => {
      root.dataset.scwRuntimeReady = '1';
      root.dataset.scwFrontendMode = 'standalone-core-with-host-adapters';
      root.dataset.scwHost = hostName;
      root.dataset.scwVersion = WORKSPACE_RELEASE;
    });
    interactionRuntime.ready = true;
    interactionRuntime.lastReadyAt = new Date().toISOString();
  }

  const frontendApi = {
    schema: 'sc-workspace-frontend-runtime/1.0',
    version: WORKSPACE_RELEASE,
    mode: 'standalone-core-with-host-adapters',
    host: hostName,
    transport: String(hostConfig.transport || identity.transport || 'host-configured'),
    backendAuthoritative: true,
    browserAuthoritativeState: false,
    wordpressRequired: false,
    primaryResponsibilities: [
      'application-bootstrap',
      'interaction-runtime',
      'presentation',
      'interaction-routing',
      'transient-ui-state',
      'explicit-local-draft-outbox'
    ],
    compatibilityStrategy: 'temporary-extracted-runtime-continuity',
    loadLocalCompatibility: loadCompat,
    boot: init,
    diagnostics() {
      return {
        schema: 'sc-workspace-frontend-runtime-diagnostics/1.0',
        version: WORKSPACE_RELEASE,
        host: hostName,
        ready: interactionRuntime.ready === true,
        standaloneBoot: interactionRuntime.standaloneBoot === true,
        wordpressRequired: false,
        compatibilityLoaded: interactionRuntime.compatibilityLoaded === true,
        applicationKernelReady: interactionRuntime.applicationKernelReady === true,
        moduleRegistryReady: interactionRuntime.moduleRegistryReady === true,
        optionalModulesLoaded: interactionRuntime.optionalModulesLoaded === true,
        moduleRegistry: window.SCWorkspaceModuleRegistry && window.SCWorkspaceModuleRegistry.inspect ? window.SCWorkspaceModuleRegistry.inspect() : null,
        hostAdapterReady: interactionRuntime.hostAdapterReady === true,
        transportReady: interactionRuntime.transportReady === true,
        authReady: interactionRuntime.authReady === true,
        apiClientReady: interactionRuntime.apiClientReady === true,
        projectRuntimeFactoryReady: interactionRuntime.projectRuntimeFactoryReady === true,
        applicationKernel: interactionRuntime.applicationKernel || null,
        projectCreationRuntimeAvailable: interactionRuntime.projectCreationRuntimeAvailable === true,
        backendHydration: interactionRuntime.backendHydration || 'not-requested',
        issues: [...interactionRuntime.issues]
      };
    }
  };

  window.SCWorkspaceFrontendRuntime = Object.freeze(frontendApi);

  async function init() {
    if (initPromise) return initPromise;

    initPromise = (async () => {
      await loadApplicationKernel();
      markReady();

      /*
       * making WordPress a runtime dependency. The compatibility bundle is
       * derived from the application asset location when no host provides a URL.
       *
       * Subsequent v3.46.x builds extract project/notebook/research capabilities
       * from this compatibility bundle into the standalone application kernel.
       */
      const tasks = [
        loadCompat('v3.65.0-core-interaction-continuity')
      ];

      if (identity.authenticated || hostConfig.authenticated || window.SCWorkspaceApi) {
        tasks.push(hydrateBackend());
      }

      const results = await Promise.allSettled(tasks);
      const compatOk = results[0] && results[0].status === 'fulfilled';
      await loadOptionalModules();

      interactionRuntime.projectCreationRuntimeAvailable = compatOk;
      interactionRuntime.standaloneBoot = true;
      interactionRuntime.wordpressRequired = false;

      document.dispatchEvent(new CustomEvent('sc-workspace:ready', {
        detail: {
          version: WORKSPACE_RELEASE,
          host: hostName,
          standaloneBoot: true,
          wordpressRequired: false,
          applicationKernelReady: interactionRuntime.applicationKernelReady === true,
          hostAdapterReady: interactionRuntime.hostAdapterReady === true,
          projectCreationRuntimeAvailable: compatOk
        }
      }));

      return compatOk;
    })();

    return initPromise;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => init().catch(error => {
      recordIssue('bootstrap', String(error && error.message || error));
    }), { once: true });
  } else {
    init().catch(error => {
      recordIssue('bootstrap', String(error && error.message || error));
    });
  }
})();


/* Workspace v3.65.0 — Reproducible Computational Linguistics feature loader */
(() => {
  if (window.SCWorkspaceReproducibleComputationalLinguistics) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-reproducible-computational-linguistics-v3530.js', current.src).href
      : 'assets/js/sc-workspace-reproducible-computational-linguistics-v3530.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-reproducible-computational-linguistics-v3530.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'reproducible-computational-linguistics';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Integrated Global Language Research feature loader */
(() => {
  if (window.SCWorkspaceIntegratedGlobalLanguageResearch) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-integrated-global-language-research-v3540.js', current.src).href
      : 'assets/js/sc-workspace-integrated-global-language-research-v3540.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-integrated-global-language-research-v3540.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'integrated-global-language-research';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Language Research Production Certification loader */
(() => {
  if (window.SCWorkspaceLanguageResearchProductionCertification) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-language-research-production-certification-v3550.js', current.src).href
      : 'assets/js/sc-workspace-language-research-production-certification-v3550.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-language-research-production-certification-v3550.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'language-research-production-certification';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Research Pipeline Composer loader */
(() => {
  if (window.SCWorkspaceResearchPipelineComposer) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-research-pipeline-composer-v3560.js', current.src).href
      : 'assets/js/sc-workspace-research-pipeline-composer-v3560.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-research-pipeline-composer-v3560.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'research-pipeline-composer';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Dataset & Feature Engineering loader */
(() => {
  if (window.SCWorkspaceDatasetFeatureEngineering) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-dataset-feature-engineering-v3570.js', current.src).href
      : 'assets/js/sc-workspace-dataset-feature-engineering-v3570.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-dataset-feature-engineering-v3570.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'dataset-feature-engineering';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Training & Evaluation Experiment loader */
(() => {
  if (window.SCWorkspaceTrainingEvaluationExperiment) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-training-evaluation-experiment-v3580.js', current.src).href
      : 'assets/js/sc-workspace-training-evaluation-experiment-v3580.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-training-evaluation-experiment-v3580.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'training-evaluation-experiment';
  document.head.appendChild(script);
})();


/* Workspace v3.65.0 — Model Registry & Research Model Lineage loader */
(() => {
  if (window.SCWorkspaceModelRegistryLineage) return;
  const current = document.currentScript;
  const script = document.createElement('script');
  try {
    script.src = current && current.src
      ? new URL('sc-workspace-model-registry-lineage-v3650.js', current.src).href
      : 'assets/js/sc-workspace-model-registry-lineage-v3650.js';
  } catch (_) {
    script.src = 'assets/js/sc-workspace-model-registry-lineage-v3650.js';
  }
  script.defer = true;
  script.dataset.scWorkspaceModule = 'model-registry-lineage';
  document.head.appendChild(script);
})();
