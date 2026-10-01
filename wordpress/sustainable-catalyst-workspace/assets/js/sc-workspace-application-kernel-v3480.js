(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceApplicationKernelFactory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';

  const SCHEMA = 'sc-workspace-application-kernel/2.1';
  const VERSION = '3.48.0';

  function nowIso() { return new Date().toISOString(); }

  function createKernel(options) {
    const settings = options && typeof options === 'object' ? options : {};
    const listeners = new Map();
    const capabilities = new Map();
    let hostAdapter = null;
    let transport = null;
    let auth = null;
    let apiClient = null;
    let persistence = null;
    let stateStore = null;
    let moduleRegistry = null;
    let lifecycle = null;
    let booted = false;
    let bootedAt = null;

    function emit(type, detail) {
      const event = Object.freeze({
        schema: 'sc-workspace-kernel-event/1.0',
        version: VERSION,
        type: String(type || 'event'),
        at: nowIso(),
        detail: detail && typeof detail === 'object' ? detail : {}
      });
      (listeners.get(event.type) || []).slice().forEach((handler) => {
        try { handler(event); } catch (_) {}
      });
      return event;
    }

    function on(type, handler) {
      const key = String(type || '');
      if (!key || typeof handler !== 'function') throw new Error('Kernel event subscription requires a type and handler');
      const handlers = listeners.get(key) || [];
      handlers.push(handler);
      listeners.set(key, handlers);
      return () => listeners.set(key, (listeners.get(key) || []).filter((item) => item !== handler));
    }

    function registerHostAdapter(adapter) {
      const contract = root.SCWorkspaceHostAdapterContract;
      if (contract && typeof contract.validate === 'function') {
        const result = contract.validate(adapter);
        if (!result.ok) throw new Error('Workspace host adapter contract failed: ' + result.missing.join(', '));
      }
      if (!adapter || typeof adapter !== 'object' || !String(adapter.name || '').trim()) throw new Error('Workspace host adapter is required');
      hostAdapter = adapter;
      emit('host-adapter-registered', { host: adapter.name });
      return adapter;
    }

    function registerTransport(provider) {
      if (!provider || typeof provider.request !== 'function') throw new Error('Workspace transport provider is required');
      transport = provider;
      emit('transport-registered', { name: String(provider.name || ''), mode: String(provider.mode || '') });
      return provider;
    }

    function registerAuth(provider) {
      if (!provider || typeof provider.headers !== 'function' || typeof provider.identity !== 'function') throw new Error('Workspace auth provider is required');
      auth = provider;
      emit('auth-registered', { name: String(provider.name || ''), mode: String(provider.mode || '') });
      return provider;
    }

    function registerApiClient(client) {
      if (!client || typeof client.request !== 'function') throw new Error('Workspace API client is required');
      apiClient = client;
      emit('api-client-registered', { transport: String(client.transportName || ''), auth: String(client.authName || '') });
      return client;
    }

    function registerPersistence(provider) {
      if (!provider || typeof provider.load !== 'function' || typeof provider.save !== 'function') throw new Error('Workspace persistence runtime is required');
      persistence = provider;
      emit('persistence-registered', { schema: String(provider.schema || ''), version: String(provider.version || '') });
      return provider;
    }

    function registerStateStore(store) {
      if (!store || typeof store.current !== 'function' || typeof store.persist !== 'function') throw new Error('Workspace state store is required');
      stateStore = store;
      emit('state-store-registered', { schema: String(store.schema || ''), version: String(store.version || '') });
      return store;
    }

    function registerModuleRegistry(registry) {
      if (!registry || typeof registry.register !== 'function' || typeof registry.loadAll !== 'function' || typeof registry.capability !== 'function') {
        throw new Error('Workspace module registry is required');
      }
      moduleRegistry = registry;
      emit('module-registry-registered', { schema: String(registry.schema || ''), version: String(registry.version || '') });
      return registry;
    }

    function registerProjectLifecycle(provider) {
      const required = ['listProjects', 'createProject', 'openProject', 'deleteProject'];
      const missing = required.filter((key) => !provider || typeof provider[key] !== 'function');
      if (missing.length) throw new Error('Project lifecycle provider missing: ' + missing.join(', '));
      lifecycle = provider;
      emit('project-lifecycle-registered', {
        provider: String(provider.schema || provider.name || 'project-lifecycle'),
        version: String(provider.version || '')
      });
      return provider;
    }

    function registerCapability(name, capability) {
      const key = String(name || '').trim();
      if (!key) throw new Error('Capability name is required');
      capabilities.set(key, capability);
      emit('capability-registered', { name: key });
      return capability;
    }

    function capability(name) { return capabilities.get(String(name || '')) || null; }

    async function boot(input) {
      const value = input && typeof input === 'object' ? input : {};
      if (value.hostAdapter) registerHostAdapter(value.hostAdapter);
      if (value.transport) registerTransport(value.transport);
      if (value.auth) registerAuth(value.auth);
      if (value.apiClient) registerApiClient(value.apiClient);
      if (value.persistence) registerPersistence(value.persistence);
      if (value.stateStore) registerStateStore(value.stateStore);
      if (value.moduleRegistry) registerModuleRegistry(value.moduleRegistry);
      if (value.projectLifecycle) registerProjectLifecycle(value.projectLifecycle);

      if (!hostAdapter) {
        const contract = root.SCWorkspaceHostAdapterContract;
        if (!contract || typeof contract.create !== 'function') throw new Error('Workspace host-adapter contract unavailable');
        hostAdapter = contract.create(settings.hostConfig || { host: 'standalone' });
      }
      if (!transport || !auth || !apiClient) throw new Error('Workspace kernel requires transport, auth, and API client before boot');

      booted = true;
      bootedAt = nowIso();
      emit('booted', {
        host: hostAdapter.name,
        transport: String(transport.name || ''),
        auth: String(auth.name || ''),
        lifecycleAvailable: Boolean(lifecycle)
      });
      return inspect();
    }

    function requireLifecycle() {
      if (!lifecycle) throw new Error('Workspace project runtime unavailable');
      return lifecycle;
    }

    async function listProjects() {
      return Promise.resolve(requireLifecycle().listProjects());
    }

    async function createProject(input) {
      const result = await Promise.resolve(requireLifecycle().createProject(input || {}));
      emit('project-created', { projectId: result && result.id ? String(result.id) : '' });
      return result;
    }

    async function openProject(projectId, options) {
      const result = await Promise.resolve(requireLifecycle().openProject(String(projectId || ''), options || {}));
      emit('project-opened', { projectId: String(projectId || ''), restored: Boolean(options && options.restoreArchived) });
      return result;
    }

    async function deleteProject(projectId, options) {
      const result = await Promise.resolve(requireLifecycle().deleteProject(String(projectId || ''), options || {}));
      emit('project-deleted', { projectId: String(projectId || ''), result: Boolean(result) });
      return result;
    }

    function inspect() {
      return Object.freeze({
        schema: 'sc-workspace-application-kernel-state/1.4',
        version: VERSION,
        booted,
        bootedAt,
        host: hostAdapter ? String(hostAdapter.name || '') : '',
        hostAdapterRegistered: Boolean(hostAdapter),
        transportRegistered: Boolean(transport),
        authRegistered: Boolean(auth),
        apiClientRegistered: Boolean(apiClient),
        persistenceRegistered: Boolean(persistence),
        stateStoreRegistered: Boolean(stateStore),
        moduleRegistryRegistered: Boolean(moduleRegistry),
        optionalModuleFailureIsolation: Boolean(moduleRegistry && moduleRegistry.inspect && moduleRegistry.inspect().optionalFailureIsolation),
        canonicalStateBoundaryDecoupled: Boolean(persistence && stateStore),
        projectLifecycleRegistered: Boolean(lifecycle),
        projectRuntimeExtracted: Boolean(lifecycle && lifecycle.schema === 'sc-workspace-project-runtime/1.0'),
        capabilityCount: capabilities.size,
        capabilityNames: [...capabilities.keys()],
        standaloneShellCapable: true,
        wordpressThinAdapterCapable: true,
        hostAgnosticAssetPipelineCapable: true,
        standaloneProductionCertificationCapable: true,
        decoupledProductionBaseline: true,
        originalLanguageCorpusWorkspaceCapable: true,
        linguisticAnnotationCorpusStructureWorkspaceCapable: true,
        wordpressRequired: false,
        backendAuthoritative: true
      });
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      registerHostAdapter,
      registerTransport,
      registerAuth,
      registerApiClient,
      registerPersistence,
      registerStateStore,
      registerModuleRegistry,
      registerProjectLifecycle,
      registerCapability,
      capability,
      on,
      boot,
      api() { return apiClient; },
      authentication() { return auth; },
      transport() { return transport; },
      persistence() { return persistence; },
      stateStore() { return stateStore; },
      moduleRegistry() { return moduleRegistry; },
      projectRuntime() { return lifecycle; },
      listProjects,
      createProject,
      openProject,
      deleteProject,
      inspect
    });
  }

  return Object.freeze({ schema: SCHEMA, version: VERSION, createKernel });
});
