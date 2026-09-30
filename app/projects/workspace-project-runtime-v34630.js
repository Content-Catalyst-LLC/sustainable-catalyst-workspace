(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  root.SCWorkspaceProjectRuntimeFactory = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  const SCHEMA = 'sc-workspace-project-runtime/1.0';
  const PORT_SCHEMA = 'sc-workspace-project-state-port/1.0';
  const VERSION = '3.46.3.0';

  function nowIso() {
    return new Date().toISOString();
  }

  function makeId() {
    try {
      if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
        return 'scwp-' + crypto.randomUUID();
      }
    } catch (_) {}
    return 'scwp-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 12);
  }

  function clone(value) {
    return value == null ? value : JSON.parse(JSON.stringify(value));
  }

  function defaultProjectRecord(input) {
    const source = input && typeof input === 'object' ? input : {};
    const stamp = nowIso();
    return {
      schema: 'sc-workspace-project/core-extraction-1.0',
      id: makeId(),
      title: String(source.title || 'Untitled project').trim().slice(0, 120) || 'Untitled project',
      description: String(source.description || '').trim().slice(0, 600),
      status: 'active',
      pinned: false,
      createdAt: stamp,
      updatedAt: stamp,
      archivedAt: null,
      notes: '',
      objects: [],
      activeObjectId: null
    };
  }

  function validatePort(port) {
    const required = [
      'snapshot',
      'replaceProjects',
      'setActiveProjectId',
      'persist',
      'render'
    ];
    const missing = required.filter((key) => !port || typeof port[key] !== 'function');
    return Object.freeze({
      schema: PORT_SCHEMA,
      version: VERSION,
      ok: missing.length === 0,
      missing
    });
  }

  function create(options) {
    const source = options && typeof options === 'object' ? options : {};
    const port = source.port;
    const validation = validatePort(port);
    if (!validation.ok) {
      throw new Error('Workspace project state port missing: ' + validation.missing.join(', '));
    }

    function snapshot() {
      const value = port.snapshot() || {};
      return {
        projects: Array.isArray(value.projects) ? value.projects : [],
        activeProjectId: value.activeProjectId == null ? null : String(value.activeProjectId)
      };
    }

    function reportIssue(type, error) {
      if (typeof port.reportIssue === 'function') {
        try { port.reportIssue(type, String(error && error.message || error || '')); } catch (_) {}
      }
    }

    function notifyFailure(message) {
      if (typeof port.notifyFailure === 'function') {
        try { port.notifyFailure(String(message || 'Workspace project operation failed.')); } catch (_) {}
      }
    }

    function persist(message) {
      return port.persist(String(message || 'Workspace project state saved')) !== false;
    }

    function listProjects() {
      return snapshot().projects.map(clone);
    }

    function findProject(projectId, includeArchived) {
      const id = String(projectId || '');
      return snapshot().projects.find((project) => (
        project && String(project.id || '') === id && (includeArchived || !project.archivedAt)
      )) || null;
    }

    function createProject(input) {
      const before = snapshot();
      const project = typeof port.createRecord === 'function'
        ? port.createRecord(input || {})
        : defaultProjectRecord(input || {});
      if (!project || !String(project.id || '')) {
        throw new Error('Workspace project factory returned an invalid record');
      }

      const next = before.projects.concat([project]);
      port.replaceProjects(next);
      port.setActiveProjectId(project.id);
      if (typeof port.afterCreate === 'function') port.afterCreate(project);

      if (!persist('Project created and saved')) {
        port.replaceProjects(before.projects);
        port.setActiveProjectId(before.activeProjectId);
        port.render();
        notifyFailure('Workspace could not verify the local project creation, so the in-memory change was rolled back.');
        return null;
      }

      port.render();
      return clone(project);
    }

    function openProject(projectId, options) {
      const settings = options && typeof options === 'object' ? options : {};
      const before = snapshot();
      const project = findProject(projectId, true);
      if (!project) return null;

      const wasArchivedAt = project.archivedAt || null;
      if (project.archivedAt && settings.restoreArchived !== false) {
        project.archivedAt = null;
        project.updatedAt = nowIso();
        if (typeof port.markRestored === 'function') port.markRestored(project);
      } else if (project.archivedAt) {
        return null;
      }

      port.setActiveProjectId(project.id);
      if (typeof port.afterOpen === 'function') port.afterOpen(project, settings);

      if (!persist(project.archivedAt ? 'Project opened' : (wasArchivedAt ? 'Project restored' : 'Project opened'))) {
        project.archivedAt = wasArchivedAt;
        port.setActiveProjectId(before.activeProjectId);
        port.render();
        notifyFailure('Workspace could not verify the project-open state change.');
        return null;
      }

      port.render();
      return clone(project);
    }

    function deleteProject(projectId, options) {
      const settings = options && typeof options === 'object' ? options : {};
      const before = snapshot();
      const project = before.projects.find((item) => (
        item && String(item.id || '') === String(projectId || '') && !item.archivedAt
      )) || null;
      if (!project) return false;

      if (settings.confirm !== false && typeof port.confirmDelete === 'function') {
        if (!port.confirmDelete(project)) return false;
      }

      // Canonical removal happens first. Secondary-index cleanup is best-effort
      // and can never block the local project deletion.
      port.replaceProjects(before.projects.filter((item) => item !== project && String(item.id || '') !== String(project.id)));
      port.setActiveProjectId(null);

      if (typeof port.cleanupReferences === 'function') {
        try {
          port.cleanupReferences(project.id);
        } catch (error) {
          reportIssue('project-delete-reference-cleanup', error);
        }
      }

      if (!persist('Project deleted from this device')) {
        port.replaceProjects(before.projects);
        port.setActiveProjectId(before.activeProjectId);
        port.render();
        notifyFailure('Workspace could not verify the local deletion, so the project was restored in memory. Review browser storage availability and try again.');
        return false;
      }

      if (typeof port.afterDelete === 'function') port.afterDelete(project);
      port.render();
      return true;
    }

    function inspect() {
      const current = snapshot();
      return Object.freeze({
        schema: 'sc-workspace-project-runtime-state/1.0',
        version: VERSION,
        portSchema: PORT_SCHEMA,
        projectCount: current.projects.length,
        activeProjectId: current.activeProjectId,
        hostRequired: false,
        wordpressRequired: false,
        compatibilityBundleOwnsLifecycle: false,
        persistenceAuthority: 'state-port',
        backendAuthorityWhenSignedIn: true
      });
    }

    return Object.freeze({
      schema: SCHEMA,
      version: VERSION,
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
    portSchema: PORT_SCHEMA,
    validatePort,
    defaultProjectRecord,
    create
  });
});
