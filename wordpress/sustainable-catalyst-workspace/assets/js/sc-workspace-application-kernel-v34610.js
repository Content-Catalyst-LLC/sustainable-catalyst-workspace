(function (root, factory) {
  'use strict';
  const api = factory(root);
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceApplicationKernelFactory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function (root) {
  'use strict';

  const SCHEMA = 'sc-workspace-application-kernel/1.0';
  const VERSION = '3.46.1.0';

  function nowIso() {
    return new Date().toISOString();
  }

  function createKernel(options) {
    const settings = options && typeof options === 'object' ? options : {};
    const listeners = new Map();
    const capabilities = new Map();
    let hostAdapter = null;
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
      const handlers = listeners.get(event.type) || [];
      handlers.slice().forEach((handler) => {
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
      return () => {
        const current = listeners.get(key) || [];
        listeners.set(key, current.filter((item) => item !== handler));
      };
    }

    function registerHostAdapter(adapter) {
      const contract = root.SCWorkspaceHostAdapterContract;
      if (contract && typeof contract.validate === 'function') {
        const result = contract.validate(adapter);
        if (!result.ok) throw new Error('Workspace host adapter contract failed: ' + result.missing.join(', '));
      }
      if (!adapter || typeof adapter !== 'object' || !String(adapter.name || '').trim()) {
        throw new Error('Workspace host adapter is required');
      }
      hostAdapter = adapter;
      emit('host-adapter-registered', { host: adapter.name });
      return adapter;
    }

    function registerProjectLifecycle(provider) {
      const required = ['listProjects', 'createProject', 'openProject', 'deleteProject'];
      const missing = required.filter((key) => !provider || typeof provider[key] !== 'function');
      if (missing.length) throw new Error('Project lifecycle provider missing: ' + missing.join(', '));
      lifecycle = provider;
      emit('project-lifecycle-registered', {
        provider: String(provider.name || provider.schema || 'project-lifecycle'),
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

    function capability(name) {
      return capabilities.get(String(name || '')) || null;
    }

    async function boot(input) {
      const value = input && typeof input === 'object' ? input : {};
      if (value.hostAdapter) registerHostAdapter(value.hostAdapter);
      if (value.projectLifecycle) registerProjectLifecycle(value.projectLifecycle);
      if (!hostAdapter) {
        const contract = root.SCWorkspaceHostAdapterContract;
        if (!contract || typeof contract.create !== 'function') {
          throw new Error('Workspace host-adapter contract unavailable');
        }
        hostAdapter = contract.create(settings.hostConfig || { host: 'standalone' });
      }
      booted = true;
      bootedAt = nowIso();
      emit('booted', { host: hostAdapter.name, lifecycleAvailable: Boolean(lifecycle) });
      return inspect();
    }

    function requireLifecycle() {
      if (!lifecycle) throw new Error('Workspace project lifecycle provider unavailable');
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

    async function openProject(projectId) {
      const result = await Promise.resolve(requireLifecycle().openProject(String(projectId || '')));
      emit('project-opened', { projectId: String(projectId || '') });
      return result;
    }

    async function deleteProject(projectId, options) {
      const result = await Promise.resolve(requireLifecycle().deleteProject(String(projectId || ''), options || {}));
      emit('project-deleted', { projectId: String(projectId || ''), result: Boolean(result) });
      return result;
    }

    function inspect() {
      return Object.freeze({
        schema: 'sc-workspace-application-kernel-state/1.0',
        version: VERSION,
        booted,
        bootedAt,
        host: hostAdapter ? String(hostAdapter.name || '') : '',
        hostAdapterRegistered: Boolean(hostAdapter),
        projectLifecycleRegistered: Boolean(lifecycle),
        capabilityCount: capabilities.size,
        capabilityNames: [...capabilities.keys()],
        wordpressRequired: false,
        backendAuthoritative: true
      });
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
      registerHostAdapter,
      registerProjectLifecycle,
      registerCapability,
      capability,
      on,
      boot,
      listProjects,
      createProject,
      openProject,
      deleteProject,
      inspect
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    version: VERSION,
    createKernel
  });
});
