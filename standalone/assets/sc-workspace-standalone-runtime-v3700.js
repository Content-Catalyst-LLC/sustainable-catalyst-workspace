(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceStandaloneRuntimeFactory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-standalone-runtime/1.0';
  const VERSION = '3.70.0';
  const STORAGE_SCHEMA_VERSION = 38;

  function nowIso() {
    return new Date().toISOString();
  }

  function createDefaultState() {
    return {
      schemaVersion: STORAGE_SCHEMA_VERSION,
      projects: [],
      activeProjectId: null,
      createdAt: nowIso(),
      updatedAt: nowIso()
    };
  }

  function normalizeState(value) {
    const state = value && typeof value === 'object' ? value : {};
    if (!Array.isArray(state.projects)) state.projects = [];
    if (state.activeProjectId == null) state.activeProjectId = null;
    state.schemaVersion = Math.max(Number(state.schemaVersion || 0), STORAGE_SCHEMA_VERSION);
    state.updatedAt = String(state.updatedAt || nowIso());
    return state;
  }

  function prepareForSave(state) {
    const next = normalizeState(state);
    next.schemaVersion = Math.max(Number(next.schemaVersion || 0), STORAGE_SCHEMA_VERSION);
    next.updatedAt = nowIso();
    return next;
  }

  async function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const config = source.config && typeof source.config === 'object' ? source.config : {};

    const required = {
      hostContract: source.hostContract,
      hostAdapterFactory: source.hostAdapterFactory,
      transportFactory: source.transportFactory,
      authFactory: source.authFactory,
      apiFactory: source.apiFactory,
      persistenceFactory: source.persistenceFactory,
      stateStoreFactory: source.stateStoreFactory,
      projectFactory: source.projectFactory,
      moduleRegistryFactory: source.moduleRegistryFactory,
      kernelFactory: source.kernelFactory
    };

    Object.entries(required).forEach(([key, value]) => {
      if (!value) throw new Error('Standalone Workspace dependency unavailable: ' + key);
    });

    const storage = source.storage;
    if (!storage || typeof storage.getItem !== 'function' || typeof storage.setItem !== 'function') {
      throw new Error('Standalone Workspace requires a Storage-compatible state adapter');
    }

    const hostAdapter = source.hostAdapterFactory.create(config, source.hostContract);
    const transport = source.transportFactory.createDirect({
      name: 'standalone-direct-backend',
      baseUrl: String(config.apiBase || ''),
      fetchImpl: source.fetchImpl || undefined
    });
    const auth = source.authContext || source.authFactory.createAnonymous();
    const apiClient = source.apiFactory.create({ transport, auth });

    const persistence = source.persistenceFactory.create({
      storage,
      workspaceVersion: VERSION,
      storageSchemaVersion: STORAGE_SCHEMA_VERSION,
      keys: {
        current: String(config.storageKey || 'sc_workspace'),
        legacy: String(config.legacyStorageKey || 'sc_workspace_v0_1'),
        recovery: String(config.recoveryStorageKey || 'sc_workspace_recovery_v0_8_2'),
        lastGood: String(config.lastGoodStorageKey || 'sc_workspace_last_good_v1')
      },
      defaultState: createDefaultState,
      normalize: normalizeState,
      prepareForSave
    });

    const loaded = persistence.load();
    const stateStore = source.stateStoreFactory.create({
      initialState: loaded && loaded.state ? loaded.state : createDefaultState(),
      persistence
    });

    const projectRuntime = source.projectFactory.create({
      port: {
        schema: 'sc-workspace-standalone-project-state-port/1.0',
        snapshot() {
          const state = stateStore.current();
          return { projects: state.projects, activeProjectId: state.activeProjectId };
        },
        replaceProjects(projects) {
          stateStore.current().projects = Array.isArray(projects) ? projects : [];
        },
        setActiveProjectId(projectId) {
          stateStore.current().activeProjectId = projectId || null;
        },
        createRecord(input) {
          return source.projectFactory.defaultProjectRecord(input || {});
        },
        persist(message) {
          const result = stateStore.persist(message);
          return Boolean(result && result.ok);
        },
        render() {},
        cleanupReferences() {},
        confirmDelete(project) {
          if (typeof source.confirmDelete === 'function') {
            return source.confirmDelete(project);
          }
          return true;
        },
        notifyFailure(message) {
          if (typeof source.notifyFailure === 'function') source.notifyFailure(message);
        },
        reportIssue(type, detail) {
          if (typeof source.onIssue === 'function') source.onIssue({ type, detail });
        }
      }
    });

    const moduleRegistry = source.moduleRegistryFactory.create({
      onIssue(issue) {
        if (typeof source.onIssue === 'function') source.onIssue(issue);
      }
    });

    moduleRegistry.registerReady({
      id: 'core.host-adapter',
      version: VERSION,
      optional: false,
      capabilities: ['workspace.host']
    }, hostAdapter);
    moduleRegistry.registerReady({
      id: 'core.transport',
      version: VERSION,
      optional: false,
      capabilities: ['workspace.transport']
    }, transport);
    moduleRegistry.registerReady({
      id: 'core.auth',
      version: VERSION,
      optional: false,
      capabilities: ['workspace.auth']
    }, auth);
    moduleRegistry.registerReady({
      id: 'core.api',
      version: VERSION,
      optional: false,
      dependsOn: ['core.transport', 'core.auth'],
      capabilities: ['workspace.api']
    }, apiClient);
    moduleRegistry.registerReady({
      id: 'core.persistence',
      version: VERSION,
      optional: false,
      capabilities: ['workspace.persistence']
    }, persistence);
    moduleRegistry.registerReady({
      id: 'core.state-store',
      version: VERSION,
      optional: false,
      dependsOn: ['core.persistence'],
      capabilities: ['workspace.state']
    }, stateStore);
    moduleRegistry.registerReady({
      id: 'core.project-runtime',
      version: VERSION,
      optional: false,
      dependsOn: ['core.state-store'],
      capabilities: ['workspace.projects']
    }, projectRuntime);

    const kernel = source.kernelFactory.createKernel({ hostConfig: config });
    kernel.registerHostAdapter(hostAdapter);
    kernel.registerTransport(transport);
    kernel.registerAuth(auth);
    kernel.registerApiClient(apiClient);
    kernel.registerPersistence(persistence);
    kernel.registerStateStore(stateStore);
    kernel.registerModuleRegistry(moduleRegistry);
    kernel.registerProjectLifecycle(projectRuntime);
    await kernel.boot();

    async function health() {
      return apiClient.get('/health');
    }

    function inspect() {
      return Object.freeze({
        schema: 'sc-workspace-standalone-runtime-state/1.0',
        version: VERSION,
        host: 'standalone',
        apiBase: String(config.apiBase || ''),
        wordpressRequired: false,
        directBackendTransport: true,
        originalLanguageCorpusWorkspace: true,
        linguisticAnnotationCorpusStructureWorkspace: true,
        translationTransliterationParallelAlignmentWorkspace: true,
        historicalLanguageScriptVariantIdentityWorkspace: true,
        decoupledProductionBaseline: '3.46.10.0',
        productionCertificationContract: 'sc-workspace-standalone-production-certification/1.0',
        storageSchemaVersion: STORAGE_SCHEMA_VERSION,
        persistence: persistence.inspect ? persistence.inspect() : null,
        stateStore: stateStore.inspect ? stateStore.inspect() : null,
        projectRuntime: projectRuntime.inspect ? projectRuntime.inspect() : null,
        moduleRegistry: moduleRegistry.inspect ? moduleRegistry.inspect() : null,
        kernel: kernel.inspect ? kernel.inspect() : null
      });
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      host: 'standalone',
      kernel,
      apiClient,
      persistence,
      stateStore,
      projectRuntime,
      moduleRegistry,
      health,
      inspect
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    storageSchemaVersion: STORAGE_SCHEMA_VERSION,
    createDefaultState,
    normalizeState,
    prepareForSave,
    create
  });
});
