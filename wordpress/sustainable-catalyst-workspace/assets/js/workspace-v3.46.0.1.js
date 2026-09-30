/* Workspace v3.46.0.1 — Standalone Frontend Runtime & Project Creation Repair */
(() => {
  'use strict';

  const WORKSPACE_RELEASE = '3.46.0.1';
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

  function assetUrl(fileName) {
    const configuredBase = String(hostConfig.assetBase || identity.assetBase || '').trim();
    if (configuredBase) {
      try {
        return new URL(fileName, configuredBase.endsWith('/') ? configuredBase : configuredBase + '/').href;
      } catch (_) {}
    }
    if (runtimeScript && runtimeScript.src) {
      try {
        return new URL(fileName, runtimeScript.src).href;
      } catch (_) {}
    }
    return 'assets/js/' + fileName;
  }

  function compatibilityUrl() {
    return String(
      hostConfig.legacyCompatUrl ||
      identity.legacyCompatUrl ||
      assetUrl('sc-workspace-local-project-compat-v3000.js')
    );
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

    const existing = document.querySelector('script[data-scw-local-compatibility="1"]');
    if (existing && interactionRuntime.compatibilityLoaded) {
      return Promise.resolve(true);
    }

    const url = compatibilityUrl();
    if (!url) return Promise.reject(new Error('Workspace compatibility runtime URL unavailable'));

    interactionRuntime.compatibilityReason = reason || 'core-interaction-continuity';
    compatPromise = new Promise((resolve, reject) => {
      const script = existing || document.createElement('script');

      if (!existing) {
        script.src = url;
        script.async = false;
        script.dataset.scwLocalCompatibility = '1';
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
      markReady();

      /*
       * v3.46.0.1 restores complete Workspace interaction continuity without
       * making WordPress a runtime dependency. The compatibility bundle is
       * derived from the application asset location when no host provides a URL.
       *
       * Subsequent v3.46.x builds extract project/notebook/research capabilities
       * from this compatibility bundle into the standalone application kernel.
       */
      const tasks = [
        loadCompat('v3.46.0.1-core-interaction-continuity')
      ];

      if (identity.authenticated || hostConfig.authenticated || window.SCWorkspaceApi) {
        tasks.push(hydrateBackend());
      }

      const results = await Promise.allSettled(tasks);
      const compatOk = results[0] && results[0].status === 'fulfilled';

      interactionRuntime.projectCreationRuntimeAvailable = compatOk;
      interactionRuntime.standaloneBoot = true;
      interactionRuntime.wordpressRequired = false;

      document.dispatchEvent(new CustomEvent('sc-workspace:ready', {
        detail: {
          version: WORKSPACE_RELEASE,
          host: hostName,
          standaloneBoot: true,
          wordpressRequired: false,
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
