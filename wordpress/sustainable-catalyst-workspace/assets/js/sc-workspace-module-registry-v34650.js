(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceModuleRegistryFactory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-module-registry/1.0';
  const MANIFEST_SCHEMA = 'sc-workspace-module-manifest/1.0';
  const VERSION = '3.46.5.0';
  const VALID_STATES = new Set(['registered', 'loading', 'ready', 'degraded', 'failed', 'disabled', 'blocked']);

  function nowIso() {
    return new Date().toISOString();
  }

  function normalizeStringList(value) {
    return [...new Set((Array.isArray(value) ? value : [])
      .map((item) => String(item || '').trim())
      .filter(Boolean))];
  }

  function normalizeManifest(input) {
    const source = input && typeof input === 'object' ? input : {};
    const id = String(source.id || '').trim();
    if (!id) throw new Error('Workspace module manifest requires an id');

    return Object.freeze({
      schema: MANIFEST_SCHEMA,
      id,
      version: String(source.version || '0.0.0'),
      title: String(source.title || id),
      optional: source.optional !== false,
      enabled: source.enabled !== false,
      dependsOn: normalizeStringList(source.dependsOn),
      capabilities: normalizeStringList(source.capabilities),
      tags: normalizeStringList(source.tags),
      source: String(source.source || 'application'),
      failurePolicy: source.optional === false ? 'block-required-module' : 'isolate-optional-module'
    });
  }

  function create(options) {
    const settings = options && typeof options === 'object' ? options : {};
    const records = new Map();
    const capabilityProviders = new Map();
    const issues = [];
    const listeners = new Map();

    function emit(type, detail) {
      const event = Object.freeze({
        schema: 'sc-workspace-module-registry-event/1.0',
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
      const key = String(type || '').trim();
      if (!key || typeof handler !== 'function') throw new Error('Workspace module-registry subscription requires a type and handler');
      const list = listeners.get(key) || [];
      list.push(handler);
      listeners.set(key, list);
      return () => listeners.set(key, (listeners.get(key) || []).filter((item) => item !== handler));
    }

    function recordIssue(moduleId, type, detail) {
      const issue = Object.freeze({
        moduleId: String(moduleId || ''),
        type: String(type || 'module-error'),
        detail: String(detail || ''),
        at: nowIso()
      });
      issues.push(issue);
      if (issues.length > 100) issues.splice(0, issues.length - 100);
      emit('issue', issue);
      if (typeof settings.onIssue === 'function') {
        try { settings.onIssue(issue); } catch (_) {}
      }
      return issue;
    }

    function publicRecord(record) {
      return Object.freeze({
        schema: 'sc-workspace-module-record/1.0',
        manifest: record.manifest,
        state: record.state,
        error: record.error,
        registeredAt: record.registeredAt,
        loadedAt: record.loadedAt,
        providerAvailable: Boolean(record.provider)
      });
    }

    function register(manifestInput, loader) {
      const manifest = normalizeManifest(manifestInput);
      if (records.has(manifest.id)) {
        throw new Error('Workspace module already registered: ' + manifest.id);
      }
      if (loader != null && typeof loader !== 'function') {
        throw new Error('Workspace module loader must be a function: ' + manifest.id);
      }
      const record = {
        manifest,
        loader: loader || null,
        provider: null,
        state: manifest.enabled ? 'registered' : 'disabled',
        error: '',
        registeredAt: nowIso(),
        loadedAt: null
      };
      records.set(manifest.id, record);
      emit('registered', { id: manifest.id, optional: manifest.optional, enabled: manifest.enabled });
      return publicRecord(record);
    }

    function registerReady(manifestInput, provider) {
      const manifest = normalizeManifest(manifestInput);
      if (records.has(manifest.id)) {
        const existing = records.get(manifest.id);
        existing.provider = provider || existing.provider || null;
        existing.state = 'ready';
        existing.error = '';
        existing.loadedAt = nowIso();
        existing.manifest.capabilities.forEach((capability) => capabilityProviders.set(capability, manifest.id));
        emit('ready', { id: manifest.id, preloaded: true });
        return publicRecord(existing);
      }
      const record = {
        manifest,
        loader: null,
        provider: provider || null,
        state: manifest.enabled ? 'ready' : 'disabled',
        error: '',
        registeredAt: nowIso(),
        loadedAt: manifest.enabled ? nowIso() : null
      };
      records.set(manifest.id, record);
      if (record.state === 'ready') {
        manifest.capabilities.forEach((capability) => capabilityProviders.set(capability, manifest.id));
      }
      emit(record.state === 'ready' ? 'ready' : 'disabled', { id: manifest.id, preloaded: true });
      return publicRecord(record);
    }

    function state(id) {
      const record = records.get(String(id || ''));
      return record ? publicRecord(record) : null;
    }

    function setState(record, nextState, error) {
      if (!VALID_STATES.has(nextState)) throw new Error('Invalid Workspace module state: ' + nextState);
      record.state = nextState;
      record.error = String(error || '');
      if (nextState === 'ready' || nextState === 'degraded') record.loadedAt = nowIso();
      emit(nextState, { id: record.manifest.id, error: record.error });
    }

    function enable(id) {
      const record = records.get(String(id || ''));
      if (!record) return false;
      if (record.state === 'disabled') setState(record, 'registered', '');
      return true;
    }

    function disable(id) {
      const record = records.get(String(id || ''));
      if (!record) return false;
      record.manifest.capabilities.forEach((capability) => {
        if (capabilityProviders.get(capability) === record.manifest.id) capabilityProviders.delete(capability);
      });
      setState(record, 'disabled', '');
      return true;
    }

    async function load(id, context, stack) {
      const key = String(id || '').trim();
      const record = records.get(key);
      if (!record) throw new Error('Workspace module is not registered: ' + key);
      if (record.state === 'ready' || record.state === 'degraded') return record.provider;
      if (record.state === 'disabled') return null;
      if (record.state === 'loading') return record.provider;

      const chain = Array.isArray(stack) ? stack.slice() : [];
      if (chain.includes(key)) {
        const error = 'Workspace module dependency cycle: ' + chain.concat([key]).join(' -> ');
        setState(record, record.manifest.optional ? 'blocked' : 'failed', error);
        recordIssue(key, 'dependency-cycle', error);
        if (!record.manifest.optional) throw new Error(error);
        return null;
      }
      chain.push(key);

      for (const dependencyId of record.manifest.dependsOn) {
        const dependency = records.get(dependencyId);
        if (!dependency) {
          const error = 'Missing Workspace module dependency: ' + dependencyId;
          setState(record, record.manifest.optional ? 'blocked' : 'failed', error);
          recordIssue(key, 'missing-dependency', error);
          if (!record.manifest.optional) throw new Error(error);
          return null;
        }
        try {
          await load(dependencyId, context, chain);
        } catch (error) {
          const detail = String(error && error.message || error);
          setState(record, record.manifest.optional ? 'blocked' : 'failed', detail);
          recordIssue(key, 'dependency-failed', detail);
          if (!record.manifest.optional) throw error;
          return null;
        }
        if (!['ready', 'degraded'].includes(dependency.state)) {
          const error = 'Workspace module dependency is unavailable: ' + dependencyId;
          setState(record, record.manifest.optional ? 'blocked' : 'failed', error);
          recordIssue(key, 'dependency-unavailable', error);
          if (!record.manifest.optional) throw new Error(error);
          return null;
        }
      }

      if (!record.loader) {
        const error = 'Workspace module has no loader: ' + key;
        setState(record, record.manifest.optional ? 'failed' : 'failed', error);
        recordIssue(key, 'loader-missing', error);
        if (!record.manifest.optional) throw new Error(error);
        return null;
      }

      setState(record, 'loading', '');
      try {
        const provider = await Promise.resolve(record.loader(context || {}));
        record.provider = provider || null;
        record.manifest.capabilities.forEach((capability) => capabilityProviders.set(capability, key));
        setState(record, 'ready', '');
        return record.provider;
      } catch (error) {
        const detail = String(error && error.message || error);
        setState(record, 'failed', detail);
        recordIssue(key, 'load-failed', detail);
        if (!record.manifest.optional) throw error;
        return null;
      }
    }

    async function loadAll(context) {
      const required = [...records.values()].filter((record) => !record.manifest.optional && record.state === 'registered');
      const optional = [...records.values()].filter((record) => record.manifest.optional && record.state === 'registered');

      for (const record of required) {
        await load(record.manifest.id, context || {});
      }

      for (const record of optional) {
        try {
          await load(record.manifest.id, context || {});
        } catch (error) {
          recordIssue(record.manifest.id, 'unexpected-optional-load-propagation', String(error && error.message || error));
        }
      }

      return inspect();
    }

    function capability(name) {
      const key = String(name || '').trim();
      const moduleId = capabilityProviders.get(key);
      if (!moduleId) return null;
      const record = records.get(moduleId);
      if (!record || !['ready', 'degraded'].includes(record.state)) return null;
      return Object.freeze({
        schema: 'sc-workspace-capability-resolution/1.0',
        capability: key,
        moduleId,
        provider: record.provider
      });
    }

    function provider(id) {
      const record = records.get(String(id || ''));
      return record && ['ready', 'degraded'].includes(record.state) ? record.provider : null;
    }

    function inspect() {
      const modules = [...records.values()].map(publicRecord);
      const counts = modules.reduce((acc, record) => {
        acc[record.state] = (acc[record.state] || 0) + 1;
        return acc;
      }, {});
      return Object.freeze({
        schema: 'sc-workspace-module-registry-state/1.0',
        version: VERSION,
        moduleCount: modules.length,
        capabilityCount: capabilityProviders.size,
        counts: Object.freeze(counts),
        modules: Object.freeze(modules),
        issues: Object.freeze(issues.slice()),
        optionalFailureIsolation: true,
        requiredFailureBlocksBoot: true,
        hostRequired: false,
        wordpressRequired: false
      });
    }

    return Object.freeze({
      schema: SCHEMA,
      manifestSchema: MANIFEST_SCHEMA,
      version: VERSION,
      register,
      registerReady,
      load,
      loadAll,
      enable,
      disable,
      state,
      provider,
      capability,
      on,
      inspect
    });
  }

  return Object.freeze({
    schema: SCHEMA,
    manifestSchema: MANIFEST_SCHEMA,
    version: VERSION,
    normalizeManifest,
    create
  });
});
