(() => {
  'use strict';

  const STORAGE_KEY = 'sc_workspace';
  const LEGACY_KEY = 'sc_workspace_v0_1';
  const RECOVERY_KEY = 'sc_workspace_recovery_v0_3';
  const HANDOFF_KEY = 'sc_workspace_handoff_v1';
  const STORAGE_VERSION = 3;
  const PROJECT_SCHEMA = 'sc-workspace-project/2.0';
  const LEGACY_PROJECT_SCHEMA = 'sc-workspace-project/1.0';
  const OBJECT_SCHEMA = 'sc-workspace-object/1.0';
  const EXPORT_SCHEMA = 'sc-workspace-project-export/2.0';
  const LEGACY_EXPORT_SCHEMA = 'sc-workspace-project-export/1.0';
  const OBJECT_EXPORT_SCHEMA = 'sc-workspace-object-export/1.0';
  const HANDOFF_SCHEMA = 'sc-workspace-handoff/1.1';
  const MAX_ACTIVITY = 60;
  const MAX_RECENT_TOOLS = 8;
  const MAX_OBJECTS = 250;
  const ALLOWED_STATUS = new Set(['active', 'paused', 'complete']);
  const OBJECT_TYPES = new Set(['source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export']);
  const OBJECT_STATUS = new Set(['draft', 'working', 'ready']);
  const PROVENANCE_TYPES = new Set(['manual', 'web', 'library', 'dataset', 'tool', 'imported']);
  const OBJECT_LABELS = {
    source: 'Source', evidence: 'Evidence', dataset: 'Dataset', analysis: 'Analysis',
    decision: 'Decision', document: 'Document', export: 'Export'
  };

  let recoveryNotice = '';

  function nowIso() { return new Date().toISOString(); }

  function id(prefix) {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return `${prefix}-${window.crypto.randomUUID()}`;
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function validIso(value) {
    return Boolean(value && typeof value === 'string' && !Number.isNaN(Date.parse(value)));
  }

  function defaultState() {
    const stamp = nowIso();
    return { schemaVersion: STORAGE_VERSION, activeProjectId: null, projects: [], recentTools: [], createdAt: stamp, updatedAt: stamp };
  }

  function provenanceTemplate() {
    return { sourceType: 'manual', sourceTitle: '', sourceUrl: '', capturedAt: null };
  }

  function objectTemplate(type, title) {
    const stamp = nowIso();
    return {
      schema: OBJECT_SCHEMA,
      id: id('scwo'),
      type: OBJECT_TYPES.has(type) ? type : 'document',
      title: String(title || 'Untitled object').trim().slice(0, 160) || 'Untitled object',
      summary: '',
      content: '',
      status: 'draft',
      tags: [],
      provenance: provenanceTemplate(),
      createdAt: stamp,
      updatedAt: stamp,
      archivedAt: null
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
      activity: [],
      objects: [],
      activeObjectId: null
    };
    addActivity(project, 'created', 'Project created');
    return project;
  }

  function addActivity(project, type, summary) {
    if (!project || !Array.isArray(project.activity)) return;
    project.activity.unshift({ id: id('act'), type: String(type || 'updated').slice(0, 40), summary: String(summary || 'Project updated').slice(0, 240), at: nowIso() });
    project.activity = project.activity.slice(0, MAX_ACTIVITY);
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

  function normalizeTags(raw) {
    const input = Array.isArray(raw) ? raw : String(raw || '').split(',');
    const seen = new Set();
    const tags = [];
    input.forEach((value) => {
      const tag = String(value || '').trim().slice(0, 48);
      const key = tag.toLowerCase();
      if (tag && !seen.has(key) && tags.length < 20) {
        seen.add(key);
        tags.push(tag);
      }
    });
    return tags;
  }

  function normalizeProvenance(raw) {
    const value = raw && typeof raw === 'object' ? raw : {};
    return {
      sourceType: PROVENANCE_TYPES.has(value.sourceType) ? value.sourceType : 'manual',
      sourceTitle: String(value.sourceTitle || '').slice(0, 240),
      sourceUrl: String(value.sourceUrl || '').slice(0, 2000),
      capturedAt: validIso(value.capturedAt) ? value.capturedAt : null
    };
  }

  function normalizeObject(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      schema: OBJECT_SCHEMA,
      id: String(raw.id || id('scwo')).slice(0, 160),
      type: OBJECT_TYPES.has(raw.type) ? raw.type : 'document',
      title: String(raw.title || 'Untitled object').trim().slice(0, 160) || 'Untitled object',
      summary: String(raw.summary || '').slice(0, 1200),
      content: String(raw.content || '').slice(0, 50000),
      status: OBJECT_STATUS.has(raw.status) ? raw.status : 'draft',
      tags: normalizeTags(raw.tags),
      provenance: normalizeProvenance(raw.provenance),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp,
      archivedAt: validIso(raw.archivedAt) ? raw.archivedAt : null
    };
  }

  function normalizeProject(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    const objects = Array.isArray(raw.objects) ? raw.objects.map(normalizeObject).filter(Boolean).slice(0, MAX_OBJECTS) : [];
    const activeObjectId = objects.some((object) => object.id === raw.activeObjectId && !object.archivedAt) ? raw.activeObjectId : null;
    return {
      schema: PROJECT_SCHEMA,
      id: String(raw.id || id('scwp')).slice(0, 160),
      title: String(raw.title || 'Untitled project').trim().slice(0, 120) || 'Untitled project',
      description: String(raw.description || '').slice(0, 600),
      status: ALLOWED_STATUS.has(raw.status) ? raw.status : 'active',
      pinned: Boolean(raw.pinned),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp,
      archivedAt: validIso(raw.archivedAt) ? raw.archivedAt : null,
      notes: String(raw.notes || '').slice(0, 20000),
      recentTools: Array.isArray(raw.recentTools) ? raw.recentTools.slice(0, MAX_RECENT_TOOLS).map(normalizeRecentTool).filter(Boolean) : [],
      activity: Array.isArray(raw.activity) ? raw.activity.slice(0, MAX_ACTIVITY).map(normalizeActivity).filter(Boolean) : [],
      objects,
      activeObjectId
    };
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

  function migrateV2(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized && project.schema === LEGACY_PROJECT_SCHEMA) addActivity(normalized, 'migrated', 'Project upgraded to Workspace object model');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function normalizeState(raw) {
    if (!raw || typeof raw !== 'object') return defaultState();
    if (raw.schemaVersion === 1 || raw.schema === 1) return migrateLegacyV1(raw);
    if (raw.schemaVersion === 2) return migrateV2(raw);
    const state = defaultState();
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
        } catch (_) {
          quarantine(current, 'Workspace could not read its saved project/object state. The damaged copy was isolated for recovery.');
          return defaultState();
        }
      }
      const legacy = window.localStorage.getItem(LEGACY_KEY);
      if (legacy) {
        try {
          const migrated = migrateLegacyV1(JSON.parse(legacy));
          writeState(migrated);
          return migrated;
        } catch (_) {
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
    try { return new Intl.DateTimeFormat(undefined, { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(iso)); }
    catch (_) { return String(iso); }
  }

  function safeFileName(value) {
    return String(value || 'workspace-object').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 70) || 'workspace-object';
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

  function cloneProject(project) {
    const copy = normalizeProject(JSON.parse(JSON.stringify(project)));
    copy.id = id('scwp');
    copy.title = `${project.title} (Copy)`.slice(0, 120);
    copy.pinned = false;
    copy.createdAt = nowIso();
    copy.updatedAt = copy.createdAt;
    copy.archivedAt = null;
    copy.activity = [];
    copy.activeObjectId = null;
    copy.objects = copy.objects.map((object) => ({ ...object, id: id('scwo'), createdAt: copy.createdAt, updatedAt: copy.createdAt, archivedAt: null }));
    addActivity(copy, 'duplicated', `Duplicated from ${project.title}`);
    return copy;
  }

  function init(root) {
    if (root.dataset.scwReady === '1') return;
    root.dataset.scwReady = '1';

    let state = readState();
    let filter = 'active';
    let objectArchiveFilter = 'current';
    let objectTypeFilter = 'all';
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
    const objectTotal = root.querySelector('[data-scw-object-total]');
    const saveState = root.querySelector('[data-scw-save-state]');
    const activity = root.querySelector('[data-scw-activity]');
    const storageState = root.querySelector('[data-scw-storage-state]');
    const createForm = root.querySelector('[data-scw-create-form]');
    const importFile = root.querySelector('[data-scw-import-file]');
    const recovery = root.querySelector('[data-scw-recovery]');
    const recoveryMessage = root.querySelector('[data-scw-recovery-message]');

    const objectCreateForm = root.querySelector('[data-scw-object-create-form]');
    const objectList = root.querySelector('[data-scw-object-list]');
    const objectEmpty = root.querySelector('[data-scw-object-empty]');
    const objectEditor = root.querySelector('[data-scw-object-editor]');
    const objectTypeFilterInput = root.querySelector('[data-scw-object-type-filter]');
    const objectArchiveFilterInput = root.querySelector('[data-scw-object-archive-filter]');
    const objectLimit = root.querySelector('[data-scw-object-limit]');
    const objectHeading = root.querySelector('[data-scw-object-heading]');
    const objectTypeLabel = root.querySelector('[data-scw-object-type-label]');
    const objectIdEl = root.querySelector('[data-scw-object-id]');
    const objectTitle = root.querySelector('[data-scw-object-title]');
    const objectStatus = root.querySelector('[data-scw-object-status]');
    const objectSummary = root.querySelector('[data-scw-object-summary]');
    const objectContent = root.querySelector('[data-scw-object-content]');
    const objectTags = root.querySelector('[data-scw-object-tags]');
    const objectSourceType = root.querySelector('[data-scw-object-source-type]');
    const objectSourceTitle = root.querySelector('[data-scw-object-source-title]');
    const objectSourceUrl = root.querySelector('[data-scw-object-source-url]');
    const objectCreated = root.querySelector('[data-scw-object-created]');
    const objectUpdated = root.querySelector('[data-scw-object-updated]');

    function activeProject() {
      return state.projects.find((project) => project.id === state.activeProjectId && !project.archivedAt) || null;
    }

    function activeObject() {
      const project = activeProject();
      if (!project || !project.activeObjectId) return null;
      return project.objects.find((object) => object.id === project.activeObjectId && !object.archivedAt) || null;
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

    function objectSort(a, b) { return String(b.updatedAt).localeCompare(String(a.updatedAt)); }

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
      const objectCount = document.createElement('span');
      objectCount.className = 'scw-project-card-objects';
      const currentCount = project.objects.filter((object) => !object.archivedAt).length;
      objectCount.textContent = `${currentCount} ${currentCount === 1 ? 'object' : 'objects'}`;
      const updated = document.createElement('span');
      updated.className = 'scw-project-card-updated';
      updated.textContent = `${project.archivedAt ? 'Archived' : 'Updated'} ${formatTime(project.archivedAt || project.updatedAt)}`;
      const actions = document.createElement('div');
      actions.className = 'scw-project-card-actions';
      const open = document.createElement('button');
      open.type = 'button';
      open.className = 'scw-card-action';
      open.textContent = project.archivedAt ? 'Restore' : 'Open project';
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
      card.append(top, name, description, objectCount, updated, actions);
      return card;
    }

    function renderList() {
      list.innerHTML = '';
      const projects = state.projects.filter((project) => filter === 'archived' ? Boolean(project.archivedAt) : !project.archivedAt).sort(projectSort);
      empty.hidden = projects.length > 0;
      if (!projects.length) {
        empty.querySelector('strong').textContent = filter === 'archived' ? 'No archived projects.' : 'No Workspace Projects yet.';
        empty.querySelector('span').textContent = filter === 'archived' ? 'Archived projects remain available here until you delete them from this device.' : 'Create one to keep notes, objects, activity, and cross-product context together on this device.';
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
      project.activity.slice(0, 10).forEach((entry) => {
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

    function objectCard(object, project) {
      const card = document.createElement('article');
      card.className = `scw-object-card${object.id === project.activeObjectId ? ' is-active' : ''}`;
      const header = document.createElement('div');
      header.className = 'scw-object-card-head';
      const type = document.createElement('span');
      type.className = 'scw-object-type';
      type.textContent = OBJECT_LABELS[object.type] || object.type;
      const status = document.createElement('span');
      status.className = 'scw-object-card-status';
      status.textContent = object.archivedAt ? 'ARCHIVED' : object.status.toUpperCase();
      header.append(type, status);
      const name = document.createElement('strong');
      name.textContent = object.title;
      const summary = document.createElement('p');
      summary.textContent = object.summary || 'No summary yet.';
      const tags = document.createElement('span');
      tags.className = 'scw-object-card-tags';
      tags.textContent = object.tags.length ? object.tags.slice(0, 4).join(' · ') : 'UNTAGGED';
      const updated = document.createElement('span');
      updated.className = 'scw-object-card-updated';
      updated.textContent = `${object.archivedAt ? 'Archived' : 'Updated'} ${formatTime(object.archivedAt || object.updatedAt)}`;
      const open = document.createElement('button');
      open.type = 'button';
      open.className = 'scw-card-action';
      open.textContent = object.archivedAt ? 'Restore object' : 'Open object';
      open.addEventListener('click', () => {
        if (object.archivedAt) {
          object.archivedAt = null;
          object.updatedAt = nowIso();
          addActivity(project, 'object-restored', `${OBJECT_LABELS[object.type]} restored: ${object.title}`);
        }
        project.activeObjectId = object.id;
        project.updatedAt = nowIso();
        persist();
        render();
        objectEditor.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
      });
      card.append(header, name, summary, tags, updated, open);
      return card;
    }

    function renderObjects(project) {
      objectList.innerHTML = '';
      objectLimit.textContent = `${project.objects.length} / ${MAX_OBJECTS} objects`;
      const objects = project.objects.filter((object) => {
        const archiveMatch = objectArchiveFilter === 'archived' ? Boolean(object.archivedAt) : !object.archivedAt;
        const typeMatch = objectTypeFilter === 'all' || object.type === objectTypeFilter;
        return archiveMatch && typeMatch;
      }).sort(objectSort);
      objectEmpty.hidden = objects.length > 0;
      if (!objects.length) {
        objectEmpty.querySelector('strong').textContent = objectArchiveFilter === 'archived' ? 'No archived objects.' : 'No matching Workspace Objects.';
        objectEmpty.querySelector('span').textContent = objectArchiveFilter === 'archived' ? 'Archived project objects will appear here.' : 'Create a typed object or change the type filter.';
      }
      objects.forEach((object) => objectList.appendChild(objectCard(object, project)));
    }

    function renderObjectEditor(project) {
      const object = activeObject();
      objectEditor.hidden = !object;
      if (!object) return;
      objectHeading.textContent = object.title;
      objectTypeLabel.textContent = (OBJECT_LABELS[object.type] || object.type).toUpperCase();
      objectIdEl.textContent = object.id;
      objectTitle.value = object.title;
      objectStatus.value = object.status;
      objectSummary.value = object.summary;
      objectContent.value = object.content;
      objectTags.value = object.tags.join(', ');
      objectSourceType.value = object.provenance.sourceType;
      objectSourceTitle.value = object.provenance.sourceTitle;
      objectSourceUrl.value = object.provenance.sourceUrl;
      objectCreated.textContent = formatTime(object.createdAt);
      objectUpdated.textContent = formatTime(object.updatedAt);
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
      objectTotal.textContent = project.objects.filter((object) => !object.archivedAt).length;
      root.querySelector('[data-scw-pin]').textContent = project.pinned ? 'Unpin project' : 'Pin project';
      renderActivity(project);
      renderObjects(project);
      renderObjectEditor(project);
    }

    function renderFilters() {
      root.querySelectorAll('[data-scw-filter]').forEach((button) => {
        const selected = button.dataset.scwFilter === filter;
        button.classList.toggle('is-active', selected);
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
      objectTypeFilterInput.value = objectTypeFilter;
      objectArchiveFilterInput.value = objectArchiveFilter;
    }

    function render() {
      renderFilters();
      renderList();
      renderActive();
      if (recoveryNotice) showRecovery();
    }

    function updateProject(mutator) {
      const project = activeProject();
      if (!project) return;
      mutator(project);
      project.updatedAt = nowIso();
      activeHeading.textContent = project.title;
      schedulePersist();
      renderList();
    }

    function updateObject(mutator, activitySummary = '') {
      const project = activeProject();
      const object = activeObject();
      if (!project || !object) return;
      mutator(object);
      object.updatedAt = nowIso();
      project.updatedAt = object.updatedAt;
      if (activitySummary) addActivity(project, 'object-updated', activitySummary);
      objectHeading.textContent = object.title;
      objectUpdated.textContent = formatTime(object.updatedAt);
      schedulePersist();
      renderList();
      renderObjects(project);
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
      button.addEventListener('click', () => { filter = button.dataset.scwFilter; render(); });
    });

    titleInput.addEventListener('input', () => updateProject((project) => { project.title = titleInput.value.trim().slice(0, 120) || 'Untitled project'; }));
    titleInput.addEventListener('change', () => { const project = activeProject(); if (project) addActivity(project, 'renamed', 'Project name updated'); persist(); render(); });
    descriptionInput.addEventListener('input', () => updateProject((project) => { project.description = descriptionInput.value.slice(0, 600); }));
    statusInput.addEventListener('change', () => updateProject((project) => { project.status = ALLOWED_STATUS.has(statusInput.value) ? statusInput.value : 'active'; addActivity(project, 'status', `Status changed to ${project.status}`); }));
    notesInput.addEventListener('input', () => updateProject((project) => { project.notes = notesInput.value.slice(0, 20000); }));

    root.querySelector('[data-scw-pin]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      project.pinned = !project.pinned; project.updatedAt = nowIso();
      addActivity(project, project.pinned ? 'pinned' : 'unpinned', project.pinned ? 'Project pinned' : 'Project unpinned');
      persist(); render();
    });

    root.querySelector('[data-scw-duplicate]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      const copy = cloneProject(project);
      state.projects.push(copy); state.activeProjectId = copy.id;
      persist('Duplicate saved on this device'); render();
    });

    root.querySelector('[data-scw-export]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      const payload = { schema: EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.3.0', exportedAt: nowIso(), project: JSON.parse(JSON.stringify(project)) };
      downloadJson(`${safeFileName(project.title)}.sc-workspace.json`, payload);
      addActivity(project, 'exported', 'Project exported as JSON'); project.updatedAt = nowIso(); persist('Export recorded'); renderActive();
    });

    root.querySelector('[data-scw-archive]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      if (!window.confirm(`Archive “${project.title}”? It will remain saved on this device.`)) return;
      project.archivedAt = nowIso(); project.updatedAt = project.archivedAt; addActivity(project, 'archived', 'Project archived');
      state.activeProjectId = null; persist('Project archived'); render();
    });

    root.querySelector('[data-scw-delete]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      if (!window.confirm(`Delete “${project.title}” and its ${project.objects.length} object(s) from this device? This cannot be undone unless you exported a copy.`)) return;
      state.projects = state.projects.filter((item) => item.id !== project.id); state.activeProjectId = null; persist('Project deleted from this device'); render();
    });

    root.querySelector('[data-scw-import-project]').addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', () => {
      const file = importFile.files && importFile.files[0]; if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const payload = JSON.parse(String(reader.result || ''));
          const supportedExport = payload && (payload.schema === EXPORT_SCHEMA || payload.schema === LEGACY_EXPORT_SCHEMA);
          const rawProject = supportedExport ? payload.project : payload;
          if (!rawProject || (rawProject.schema !== PROJECT_SCHEMA && rawProject.schema !== LEGACY_PROJECT_SCHEMA)) throw new Error('Unsupported project schema');
          const project = normalizeProject(rawProject);
          if (!project) throw new Error('Invalid project');
          if (state.projects.some((item) => item.id === project.id)) { project.id = id('scwp'); project.title = `${project.title} (Imported)`.slice(0, 120); }
          project.archivedAt = null; project.activeObjectId = null; project.updatedAt = nowIso(); addActivity(project, 'imported', 'Project imported on this device');
          state.projects.push(project); state.activeProjectId = project.id; persist('Imported project saved'); render();
        } catch (_) {
          window.alert('Workspace could not import this file. Use a Workspace project JSON export from v0.2.0, v0.3.0, or a compatible future release.');
        } finally { importFile.value = ''; }
      };
      reader.readAsText(file);
    });

    root.querySelector('[data-scw-new-object]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This v0.3.0 project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
      objectCreateForm.hidden = false;
      objectCreateForm.querySelector('input[name="title"]').focus();
    });

    root.querySelector('[data-scw-cancel-object]').addEventListener('click', () => { objectCreateForm.reset(); objectCreateForm.hidden = true; });

    objectCreateForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) return;
      const data = new FormData(objectCreateForm);
      const object = objectTemplate(String(data.get('type') || 'document'), data.get('title'));
      project.objects.push(object); project.activeObjectId = object.id; project.updatedAt = nowIso();
      addActivity(project, 'object-created', `${OBJECT_LABELS[object.type]} created: ${object.title}`);
      objectCreateForm.reset(); objectCreateForm.hidden = true; objectArchiveFilter = 'current'; objectTypeFilter = 'all';
      persist('Object created and saved'); render();
      objectEditor.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    });

    objectTypeFilterInput.addEventListener('change', () => { objectTypeFilter = objectTypeFilterInput.value; const project = activeProject(); if (project) renderObjects(project); });
    objectArchiveFilterInput.addEventListener('change', () => { objectArchiveFilter = objectArchiveFilterInput.value; const project = activeProject(); if (project) renderObjects(project); });

    objectTitle.addEventListener('input', () => updateObject((object) => { object.title = objectTitle.value.trim().slice(0, 160) || 'Untitled object'; }));
    objectTitle.addEventListener('change', () => { const project = activeProject(); const object = activeObject(); if (project && object) addActivity(project, 'object-renamed', `${OBJECT_LABELS[object.type]} renamed`); persist(); render(); });
    objectStatus.addEventListener('change', () => updateObject((object) => { object.status = OBJECT_STATUS.has(objectStatus.value) ? objectStatus.value : 'draft'; }, `Object status changed to ${objectStatus.value}`));
    objectSummary.addEventListener('input', () => updateObject((object) => { object.summary = objectSummary.value.slice(0, 1200); }));
    objectContent.addEventListener('input', () => updateObject((object) => { object.content = objectContent.value.slice(0, 50000); }));
    objectTags.addEventListener('change', () => updateObject((object) => { object.tags = normalizeTags(objectTags.value); objectTags.value = object.tags.join(', '); }, 'Object tags updated'));
    objectSourceType.addEventListener('change', () => updateObject((object) => { object.provenance.sourceType = PROVENANCE_TYPES.has(objectSourceType.value) ? objectSourceType.value : 'manual'; if (!object.provenance.capturedAt) object.provenance.capturedAt = nowIso(); }, 'Object provenance updated'));
    objectSourceTitle.addEventListener('input', () => updateObject((object) => { object.provenance.sourceTitle = objectSourceTitle.value.slice(0, 240); if (!object.provenance.capturedAt && object.provenance.sourceTitle) object.provenance.capturedAt = nowIso(); }));
    objectSourceUrl.addEventListener('input', () => updateObject((object) => { object.provenance.sourceUrl = objectSourceUrl.value.slice(0, 2000); if (!object.provenance.capturedAt && object.provenance.sourceUrl) object.provenance.capturedAt = nowIso(); }));

    root.querySelector('[data-scw-object-duplicate]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
      const copy = normalizeObject(JSON.parse(JSON.stringify(object)));
      copy.id = id('scwo'); copy.title = `${object.title} (Copy)`.slice(0, 160); copy.createdAt = nowIso(); copy.updatedAt = copy.createdAt; copy.archivedAt = null;
      project.objects.push(copy); project.activeObjectId = copy.id; project.updatedAt = copy.updatedAt;
      addActivity(project, 'object-duplicated', `${OBJECT_LABELS[copy.type]} duplicated: ${object.title}`);
      persist('Object duplicate saved'); render();
    });

    root.querySelector('[data-scw-object-export]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      const payload = { schema: OBJECT_EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.3.0', exportedAt: nowIso(), projectId: project.id, object: JSON.parse(JSON.stringify(object)) };
      downloadJson(`${safeFileName(object.title)}.sc-workspace-object.json`, payload);
      addActivity(project, 'object-exported', `${OBJECT_LABELS[object.type]} exported: ${object.title}`); project.updatedAt = nowIso(); persist('Object export recorded'); renderActive();
    });

    root.querySelector('[data-scw-object-archive]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      if (!window.confirm(`Archive “${object.title}”? It will remain inside this project on this device.`)) return;
      object.archivedAt = nowIso(); object.updatedAt = object.archivedAt; project.updatedAt = object.updatedAt; project.activeObjectId = null;
      addActivity(project, 'object-archived', `${OBJECT_LABELS[object.type]} archived: ${object.title}`); persist('Object archived'); render();
    });

    root.querySelector('[data-scw-object-delete]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      if (!window.confirm(`Delete “${object.title}” from this project? This cannot be undone unless you exported a copy.`)) return;
      project.objects = project.objects.filter((item) => item.id !== object.id); project.activeObjectId = null; project.updatedAt = nowIso();
      addActivity(project, 'object-deleted', `${OBJECT_LABELS[object.type]} deleted from project`); persist('Object deleted'); render();
    });

    root.querySelector('[data-scw-dismiss-recovery]').addEventListener('click', () => { recovery.hidden = true; recoveryNotice = ''; });

    root.querySelectorAll('[data-scw-tool]').forEach((link) => {
      link.dataset.scwBaseHref = link.href;
      link.addEventListener('click', () => {
        const key = link.dataset.scwTool;
        const label = toolLabel(link);
        const stamp = nowIso();
        const project = activeProject();
        const object = activeObject();
        state.recentTools = [{ key, label, openedAt: stamp }, ...state.recentTools.filter((item) => item.key !== key)].slice(0, MAX_RECENT_TOOLS);
        try {
          const target = new URL(link.dataset.scwBaseHref || link.href, window.location.href);
          if (project) {
            project.recentTools = [{ key, label, openedAt: stamp }, ...project.recentTools.filter((item) => item.key !== key)].slice(0, MAX_RECENT_TOOLS);
            project.updatedAt = stamp;
            addActivity(project, 'handoff', `Opened ${label}${object ? ` with ${OBJECT_LABELS[object.type]}` : ''}`);
            target.searchParams.set('sc_workspace_project', project.id);
            if (object) target.searchParams.set('sc_workspace_object', object.id);
            target.searchParams.set('sc_workspace_origin', 'workspace');
            target.searchParams.set('sc_workspace_return', '1');
            window.sessionStorage.setItem(HANDOFF_KEY, JSON.stringify({
              schema: HANDOFF_SCHEMA,
              projectId: project.id,
              objectId: object ? object.id : null,
              destination: key,
              createdAt: stamp,
              returnUrl: root.dataset.returnUrl || window.location.href
            }));
          }
          link.href = target.toString();
        } catch (_) {}
        persist();
      });
    });

    try {
      const params = new URLSearchParams(window.location.search);
      const returnProject = params.get('sc_workspace_project');
      const returnObject = params.get('sc_workspace_object');
      const project = state.projects.find((item) => item.id === returnProject && !item.archivedAt);
      if (project) {
        state.activeProjectId = project.id;
        if (returnObject && project.objects.some((object) => object.id === returnObject && !object.archivedAt)) project.activeObjectId = returnObject;
        persist('Workspace context restored');
      }
    } catch (_) {}

    persist();
    render();
  }

  function boot() { document.querySelectorAll('[data-sc-workspace]').forEach(init); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
