(() => {
  'use strict';

  const STORAGE_KEY = 'sc_workspace';
  const LEGACY_KEY = 'sc_workspace_v0_1';
  const RECOVERY_KEY = 'sc_workspace_recovery_v0_2';
  const HANDOFF_KEY = 'sc_workspace_handoff_v1';
  const STORAGE_VERSION = 2;
  const PROJECT_SCHEMA = 'sc-workspace-project/1.0';
  const EXPORT_SCHEMA = 'sc-workspace-project-export/1.0';
  const MAX_ACTIVITY = 40;
  const MAX_RECENT_TOOLS = 8;
  const ALLOWED_STATUS = new Set(['active', 'paused', 'complete']);

  let recoveryNotice = '';

  function nowIso() {
    return new Date().toISOString();
  }

  function id(prefix) {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') {
      return `${prefix}-${window.crypto.randomUUID()}`;
    }
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function defaultState() {
    const stamp = nowIso();
    return {
      schemaVersion: STORAGE_VERSION,
      activeProjectId: null,
      projects: [],
      recentTools: [],
      createdAt: stamp,
      updatedAt: stamp
    };
  }

  function projectTemplate(title, description = '') {
    const stamp = nowIso();
    const project = {
      schema: PROJECT_SCHEMA,
      id: id('scwp'),
      title: String(title || 'Untitled project').trim().slice(0, 120) || 'Untitled project',
      description: String(description || '').trim().slice(0, 600),
      status: 'active',
      pinned: false,
      createdAt: stamp,
      updatedAt: stamp,
      archivedAt: null,
      notes: '',
      recentTools: [],
      activity: []
    };
    addActivity(project, 'created', 'Project created');
    return project;
  }

  function addActivity(project, type, summary) {
    if (!project || !Array.isArray(project.activity)) return;
    project.activity.unshift({ id: id('act'), type, summary, at: nowIso() });
    project.activity = project.activity.slice(0, MAX_ACTIVITY);
  }

  function normalizeProject(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    const title = String(raw.title || 'Untitled project').trim().slice(0, 120) || 'Untitled project';
    const project = {
      schema: PROJECT_SCHEMA,
      id: String(raw.id || id('scwp')).slice(0, 160),
      title,
      description: String(raw.description || '').slice(0, 600),
      status: ALLOWED_STATUS.has(raw.status) ? raw.status : 'active',
      pinned: Boolean(raw.pinned),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp,
      archivedAt: validIso(raw.archivedAt) ? raw.archivedAt : null,
      notes: String(raw.notes || '').slice(0, 20000),
      recentTools: Array.isArray(raw.recentTools) ? raw.recentTools.slice(0, MAX_RECENT_TOOLS).map(normalizeRecentTool).filter(Boolean) : [],
      activity: Array.isArray(raw.activity) ? raw.activity.slice(0, MAX_ACTIVITY).map(normalizeActivity).filter(Boolean) : []
    };
    return project;
  }

  function normalizeActivity(raw) {
    if (!raw || typeof raw !== 'object') return null;
    return {
      id: String(raw.id || id('act')).slice(0, 160),
      type: String(raw.type || 'updated').slice(0, 40),
      summary: String(raw.summary || 'Project updated').slice(0, 240),
      at: validIso(raw.at) ? raw.at : nowIso()
    };
  }

  function normalizeRecentTool(raw) {
    if (!raw || typeof raw !== 'object') return null;
    return {
      key: String(raw.key || '').slice(0, 80),
      label: String(raw.label || raw.key || 'Tool').slice(0, 120),
      openedAt: validIso(raw.openedAt) ? raw.openedAt : nowIso()
    };
  }

  function validIso(value) {
    if (!value || typeof value !== 'string') return false;
    return !Number.isNaN(Date.parse(value));
  }

  function migrateLegacyV1(raw) {
    const state = defaultState();
    const recent = Array.isArray(raw && raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean) : [];
    state.recentTools = recent.slice(0, MAX_RECENT_TOOLS);
    if (raw && raw.activeSession) {
      const legacy = raw.activeSession;
      const project = projectTemplate(legacy.title === 'Workspace session' ? 'Migrated Workspace project' : legacy.title, 'Migrated from Workspace v0.1.0 browser-local session state.');
      project.createdAt = validIso(legacy.createdAt) ? legacy.createdAt : project.createdAt;
      project.updatedAt = validIso(legacy.updatedAt) ? legacy.updatedAt : project.updatedAt;
      project.recentTools = recent.slice(0, MAX_RECENT_TOOLS);
      addActivity(project, 'migrated', 'Migrated from Workspace v0.1.0');
      state.projects.push(project);
      state.activeProjectId = project.id;
    }
    state.updatedAt = nowIso();
    return state;
  }

  function normalizeState(raw) {
    if (!raw || typeof raw !== 'object') return defaultState();
    if (raw.schemaVersion === 1 || raw.schema === 1) return migrateLegacyV1(raw);
    const state = defaultState();
    state.schemaVersion = STORAGE_VERSION;
    state.projects = Array.isArray(raw.projects) ? raw.projects.map(normalizeProject).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = validIso(raw.updatedAt) ? raw.updatedAt : state.updatedAt;
    return state;
  }

  function quarantine(raw, reason) {
    recoveryNotice = reason || 'A damaged local Workspace state was isolated.';
    try {
      window.localStorage.setItem(RECOVERY_KEY, JSON.stringify({ capturedAt: nowIso(), reason: recoveryNotice, raw: String(raw || '').slice(0, 250000) }));
    } catch (_) {}
  }

  function readState() {
    try {
      const current = window.localStorage.getItem(STORAGE_KEY);
      if (current) {
        try {
          return normalizeState(JSON.parse(current));
        } catch (error) {
          quarantine(current, 'Workspace could not read its saved project state. The damaged copy was isolated for recovery.');
          return defaultState();
        }
      }
      const legacy = window.localStorage.getItem(LEGACY_KEY);
      if (legacy) {
        try {
          const migrated = migrateLegacyV1(JSON.parse(legacy));
          writeState(migrated);
          return migrated;
        } catch (error) {
          quarantine(legacy, 'Workspace v0.1.0 session data could not be migrated and was isolated for recovery.');
        }
      }
    } catch (_) {
      recoveryNotice = 'Browser storage is unavailable. Workspace is running in temporary memory for this page.';
    }
    return defaultState();
  }

  function writeState(state) {
    state.schemaVersion = STORAGE_VERSION;
    state.updatedAt = nowIso();
    try {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      return true;
    } catch (_) {
      recoveryNotice = 'Workspace could not save to browser storage. Your current changes may only last for this page.';
      return false;
    }
  }

  function formatTime(iso) {
    if (!iso) return 'Not yet';
    try {
      return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso));
    } catch (_) {
      return String(iso);
    }
  }

  function safeFileName(value) {
    return String(value || 'workspace-project').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'workspace-project';
  }

  function downloadJson(filename, payload) {
    const blob = new Blob([JSON.stringify(payload, null, 2) + '\n'], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 500);
  }

  function toolLabel(link) {
    const strong = link.querySelector('strong');
    return strong ? strong.textContent.trim() : link.dataset.scwTool;
  }

  function init(root) {
    if (root.dataset.scwReady === '1') return;
    root.dataset.scwReady = '1';

    let state = readState();
    let filter = 'active';
    let saveTimer = null;

    const list = root.querySelector('[data-scw-project-list]');
    const empty = root.querySelector('[data-scw-empty]');
    const activePanel = root.querySelector('[data-scw-active-project]');
    const activeHeading = root.querySelector('[data-scw-active-heading]');
    const titleInput = root.querySelector('[data-scw-project-title]');
    const descriptionInput = root.querySelector('[data-scw-project-description]');
    const statusInput = root.querySelector('[data-scw-project-status]');
    const notesInput = root.querySelector('[data-scw-project-notes]');
    const projectId = root.querySelector('[data-scw-project-id]');
    const saveState = root.querySelector('[data-scw-save-state]');
    const activity = root.querySelector('[data-scw-activity]');
    const storageState = root.querySelector('[data-scw-storage-state]');
    const createForm = root.querySelector('[data-scw-create-form]');
    const importFile = root.querySelector('[data-scw-import-file]');
    const recovery = root.querySelector('[data-scw-recovery]');
    const recoveryMessage = root.querySelector('[data-scw-recovery-message]');

    function activeProject() {
      return state.projects.find((project) => project.id === state.activeProjectId && !project.archivedAt) || null;
    }

    function persist(message = 'Saved on this device') {
      const saved = writeState(state);
      saveState.textContent = saved ? message : 'Save unavailable';
      storageState.textContent = saved ? 'Local project storage ready' : 'Local project storage unavailable';
      if (recoveryNotice) showRecovery();
      return saved;
    }

    function schedulePersist() {
      saveState.textContent = 'Saving…';
      window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => persist(), 320);
    }

    function showRecovery() {
      if (!recoveryNotice) return;
      recoveryMessage.textContent = recoveryNotice;
      recovery.hidden = false;
    }

    function projectSort(a, b) {
      if (a.pinned !== b.pinned) return a.pinned ? -1 : 1;
      return String(b.updatedAt).localeCompare(String(a.updatedAt));
    }

    function projectCard(project) {
      const card = document.createElement('article');
      card.className = `scw-project-card${project.id === state.activeProjectId ? ' is-active' : ''}`;
      card.dataset.projectId = project.id;

      const top = document.createElement('div');
      top.className = 'scw-project-card-top';
      const meta = document.createElement('span');
      meta.className = 'scw-project-card-meta';
      meta.textContent = project.archivedAt ? 'ARCHIVED' : project.status.toUpperCase();
      const pin = document.createElement('span');
      pin.className = 'scw-project-card-pin';
      pin.textContent = project.pinned ? 'PINNED' : '';
      top.append(meta, pin);

      const name = document.createElement('strong');
      name.textContent = project.title;
      const description = document.createElement('p');
      description.textContent = project.description || 'No project description yet.';
      const updated = document.createElement('span');
      updated.className = 'scw-project-card-updated';
      updated.textContent = `${project.archivedAt ? 'Archived' : 'Updated'} ${formatTime(project.archivedAt || project.updatedAt)}`;

      const actions = document.createElement('div');
      actions.className = 'scw-project-card-actions';
      const open = document.createElement('button');
      open.type = 'button';
      open.className = 'scw-card-action';
      open.textContent = project.archivedAt ? 'Restore' : (project.id === state.activeProjectId ? 'Open' : 'Open project');
      open.addEventListener('click', () => {
        if (project.archivedAt) {
          project.archivedAt = null;
          project.updatedAt = nowIso();
          addActivity(project, 'restored', 'Project restored');
        }
        state.activeProjectId = project.id;
        persist();
        render();
        activePanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
      });
      actions.appendChild(open);
      card.append(top, name, description, updated, actions);
      return card;
    }

    function renderList() {
      list.innerHTML = '';
      const projects = state.projects.filter((project) => filter === 'archived' ? Boolean(project.archivedAt) : !project.archivedAt).sort(projectSort);
      empty.hidden = projects.length > 0;
      if (!projects.length) {
        empty.querySelector('strong').textContent = filter === 'archived' ? 'No archived projects.' : 'No Workspace Projects yet.';
        empty.querySelector('span').textContent = filter === 'archived' ? 'Archived projects will remain available here until you delete them from this device.' : 'Create one to keep notes, activity, and cross-product context together on this device.';
      }
      projects.forEach((project) => list.appendChild(projectCard(project)));
    }

    function renderActivity(project) {
      activity.innerHTML = '';
      if (!project.activity.length) {
        const item = document.createElement('span');
        item.className = 'scw-activity-empty';
        item.textContent = 'No recorded activity yet.';
        activity.appendChild(item);
        return;
      }
      project.activity.slice(0, 8).forEach((entry) => {
        const item = document.createElement('div');
        item.className = 'scw-activity-item';
        const summary = document.createElement('strong');
        summary.textContent = entry.summary;
        const when = document.createElement('span');
        when.textContent = formatTime(entry.at);
        item.append(summary, when);
        activity.appendChild(item);
      });
    }

    function renderActive() {
      const project = activeProject();
      activePanel.hidden = !project;
      if (!project) return;
      activeHeading.textContent = project.title;
      titleInput.value = project.title;
      descriptionInput.value = project.description;
      statusInput.value = project.status;
      notesInput.value = project.notes;
      projectId.textContent = project.id;
      root.querySelector('[data-scw-pin]').textContent = project.pinned ? 'Unpin project' : 'Pin project';
      renderActivity(project);
    }

    function renderFilters() {
      root.querySelectorAll('[data-scw-filter]').forEach((button) => {
        const selected = button.dataset.scwFilter === filter;
        button.classList.toggle('is-active', selected);
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
    }

    function render() {
      renderFilters();
      renderList();
      renderActive();
      if (recoveryNotice) showRecovery();
    }

    function updateProject(mutator, activitySummary) {
      const project = activeProject();
      if (!project) return;
      mutator(project);
      project.updatedAt = nowIso();
      if (activitySummary) addActivity(project, 'updated', activitySummary);
      activeHeading.textContent = project.title;
      schedulePersist();
      renderList();
    }

    root.querySelector('[data-scw-new-project]').addEventListener('click', () => {
      createForm.hidden = false;
      createForm.querySelector('input[name="title"]').focus();
    });

    root.querySelector('[data-scw-cancel-create]').addEventListener('click', () => {
      createForm.reset();
      createForm.hidden = true;
    });

    createForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const data = new FormData(createForm);
      const project = projectTemplate(data.get('title'), data.get('description'));
      state.projects.push(project);
      state.activeProjectId = project.id;
      createForm.reset();
      createForm.hidden = true;
      persist('Project created and saved');
      render();
      activePanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });

    root.querySelectorAll('[data-scw-filter]').forEach((button) => {
      button.addEventListener('click', () => {
        filter = button.dataset.scwFilter;
        render();
      });
    });

    titleInput.addEventListener('input', () => updateProject((project) => {
      project.title = titleInput.value.trim().slice(0, 120) || 'Untitled project';
    }));
    titleInput.addEventListener('change', () => {
      const project = activeProject();
      if (project) addActivity(project, 'renamed', 'Project name updated');
      persist();
      render();
    });

    descriptionInput.addEventListener('input', () => updateProject((project) => {
      project.description = descriptionInput.value.slice(0, 600);
    }));

    statusInput.addEventListener('change', () => updateProject((project) => {
      project.status = ALLOWED_STATUS.has(statusInput.value) ? statusInput.value : 'active';
      addActivity(project, 'status', `Status changed to ${project.status}`);
    }));

    notesInput.addEventListener('input', () => updateProject((project) => {
      project.notes = notesInput.value.slice(0, 20000);
    }));

    root.querySelector('[data-scw-pin]').addEventListener('click', () => {
      const project = activeProject();
      if (!project) return;
      project.pinned = !project.pinned;
      project.updatedAt = nowIso();
      addActivity(project, project.pinned ? 'pinned' : 'unpinned', project.pinned ? 'Project pinned' : 'Project unpinned');
      persist();
      render();
    });

    root.querySelector('[data-scw-duplicate]').addEventListener('click', () => {
      const project = activeProject();
      if (!project) return;
      const copy = normalizeProject(JSON.parse(JSON.stringify(project)));
      copy.id = id('scwp');
      copy.title = `${project.title} (Copy)`.slice(0, 120);
      copy.pinned = false;
      copy.createdAt = nowIso();
      copy.updatedAt = copy.createdAt;
      copy.archivedAt = null;
      copy.activity = [];
      addActivity(copy, 'duplicated', `Duplicated from ${project.title}`);
      state.projects.push(copy);
      state.activeProjectId = copy.id;
      persist('Duplicate saved on this device');
      render();
    });

    root.querySelector('[data-scw-export]').addEventListener('click', () => {
      const project = activeProject();
      if (!project) return;
      const payload = {
        schema: EXPORT_SCHEMA,
        workspaceVersion: root.dataset.version || '0.2.0',
        exportedAt: nowIso(),
        project: JSON.parse(JSON.stringify(project))
      };
      downloadJson(`${safeFileName(project.title)}.sc-workspace.json`, payload);
      addActivity(project, 'exported', 'Project exported as JSON');
      project.updatedAt = nowIso();
      persist('Export recorded');
      renderActive();
    });

    root.querySelector('[data-scw-archive]').addEventListener('click', () => {
      const project = activeProject();
      if (!project) return;
      if (!window.confirm(`Archive “${project.title}”? It will remain saved on this device.`)) return;
      project.archivedAt = nowIso();
      project.updatedAt = project.archivedAt;
      addActivity(project, 'archived', 'Project archived');
      state.activeProjectId = null;
      persist('Project archived');
      render();
    });

    root.querySelector('[data-scw-delete]').addEventListener('click', () => {
      const project = activeProject();
      if (!project) return;
      if (!window.confirm(`Delete “${project.title}” from this device? This cannot be undone unless you exported a copy.`)) return;
      state.projects = state.projects.filter((item) => item.id !== project.id);
      state.activeProjectId = null;
      persist('Project deleted from this device');
      render();
    });

    root.querySelector('[data-scw-import-project]').addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', () => {
      const file = importFile.files && importFile.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const payload = JSON.parse(String(reader.result || ''));
          const rawProject = payload && payload.schema === EXPORT_SCHEMA ? payload.project : payload;
          if (!rawProject || rawProject.schema !== PROJECT_SCHEMA) throw new Error('Unsupported project schema');
          const project = normalizeProject(rawProject);
          if (!project) throw new Error('Invalid project');
          if (state.projects.some((item) => item.id === project.id)) {
            project.id = id('scwp');
            project.title = `${project.title} (Imported)`.slice(0, 120);
          }
          project.archivedAt = null;
          project.updatedAt = nowIso();
          addActivity(project, 'imported', 'Project imported on this device');
          state.projects.push(project);
          state.activeProjectId = project.id;
          persist('Imported project saved');
          render();
        } catch (_) {
          window.alert('Workspace could not import this file. Use a Workspace project JSON export from v0.2.0 or a compatible future release.');
        } finally {
          importFile.value = '';
        }
      };
      reader.readAsText(file);
    });

    root.querySelector('[data-scw-dismiss-recovery]').addEventListener('click', () => {
      recovery.hidden = true;
      recoveryNotice = '';
    });

    root.querySelectorAll('[data-scw-tool]').forEach((link) => {
      link.addEventListener('click', () => {
        const key = link.dataset.scwTool;
        const label = toolLabel(link);
        const stamp = nowIso();
        const project = activeProject();
        state.recentTools = [{ key, label, openedAt: stamp }, ...state.recentTools.filter((item) => item.key !== key)].slice(0, MAX_RECENT_TOOLS);
        if (project) {
          project.recentTools = [{ key, label, openedAt: stamp }, ...project.recentTools.filter((item) => item.key !== key)].slice(0, MAX_RECENT_TOOLS);
          project.updatedAt = stamp;
          addActivity(project, 'handoff', `Opened ${label}`);
          try {
            const target = new URL(link.href, window.location.href);
            target.searchParams.set('sc_workspace_project', project.id);
            target.searchParams.set('sc_workspace_origin', 'workspace');
            target.searchParams.set('sc_workspace_return', '1');
            link.href = target.toString();
            window.sessionStorage.setItem(HANDOFF_KEY, JSON.stringify({
              schema: 'sc-workspace-handoff/1.0',
              projectId: project.id,
              destination: key,
              createdAt: stamp,
              returnUrl: root.dataset.returnUrl || window.location.href
            }));
          } catch (_) {}
        }
        persist();
      });
    });

    try {
      const params = new URLSearchParams(window.location.search);
      const returnProject = params.get('sc_workspace_project');
      if (returnProject && state.projects.some((project) => project.id === returnProject && !project.archivedAt)) {
        state.activeProjectId = returnProject;
        persist('Project context restored');
      }
    } catch (_) {}

    persist();
    render();
  }

  function boot() {
    document.querySelectorAll('[data-sc-workspace]').forEach(init);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
