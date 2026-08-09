(() => {
  'use strict';

  const STORAGE_KEY = 'sc_workspace';
  const LEGACY_KEY = 'sc_workspace_v0_1';
  const RECOVERY_KEY = 'sc_workspace_recovery_v0_8_2';
  const LAST_GOOD_KEY = 'sc_workspace_last_good_v1';
  const DEVICE_KEY = 'sc_workspace_device_v1';
  const READINESS_DIAGNOSTIC_SCHEMA = 'sc-workspace-diagnostic-report/1.0';
  const EMERGENCY_BACKUP_SCHEMA = 'sc-workspace-emergency-backup/1.0';
  const HANDOFF_KEY = 'sc_workspace_handoff_v2';
  const HANDOFF_RETURN_KEY = 'sc_workspace_handoff_return_v1';
  const STORAGE_VERSION = 24;
  const PROJECT_SCHEMA = 'sc-workspace-project/11.0';
  const LEGACY_PROJECT_SCHEMA_V11 = 'sc-workspace-project/11.0';
  const LEGACY_PROJECT_SCHEMA_V10 = 'sc-workspace-project/10.0';
  const LEGACY_PROJECT_SCHEMA_V9 = 'sc-workspace-project/9.0';
  const LEGACY_PROJECT_SCHEMA_V8 = 'sc-workspace-project/8.0';
  const LEGACY_PROJECT_SCHEMA_V7 = 'sc-workspace-project/7.0';
  const LEGACY_PROJECT_SCHEMA_V6 = 'sc-workspace-project/6.0';
  const LEGACY_PROJECT_SCHEMA_V5 = 'sc-workspace-project/5.0';
  const LEGACY_PROJECT_SCHEMA_V4 = 'sc-workspace-project/4.0';
  const LEGACY_PROJECT_SCHEMA_V31 = 'sc-workspace-project/3.1';
  const LEGACY_PROJECT_SCHEMA_V3 = 'sc-workspace-project/3.0';
  const LEGACY_PROJECT_SCHEMA_V2 = 'sc-workspace-project/2.0';
  const LEGACY_PROJECT_SCHEMA_V1 = 'sc-workspace-project/1.0';
  const OBJECT_SCHEMA = 'sc-workspace-object/1.0';
  const EXPORT_SCHEMA = 'sc-workspace-project-export/11.0';
  const LEGACY_EXPORT_SCHEMA_V11 = 'sc-workspace-project-export/11.0';
  const LEGACY_EXPORT_SCHEMA_V10 = 'sc-workspace-project-export/10.0';
  const LEGACY_EXPORT_SCHEMA_V9 = 'sc-workspace-project-export/9.0';
  const LEGACY_EXPORT_SCHEMA_V8 = 'sc-workspace-project-export/8.0';
  const LEGACY_EXPORT_SCHEMA_V7 = 'sc-workspace-project-export/7.0';
  const LEGACY_EXPORT_SCHEMA_V6 = 'sc-workspace-project-export/6.0';
  const LEGACY_EXPORT_SCHEMA_V5 = 'sc-workspace-project-export/5.0';
  const LEGACY_EXPORT_SCHEMA_V4 = 'sc-workspace-project-export/4.0';
  const LEGACY_EXPORT_SCHEMA_V31 = 'sc-workspace-project-export/3.1';
  const LEGACY_EXPORT_SCHEMA_V3 = 'sc-workspace-project-export/3.0';
  const LEGACY_EXPORT_SCHEMA_V2 = 'sc-workspace-project-export/2.0';
  const LEGACY_EXPORT_SCHEMA_V1 = 'sc-workspace-project-export/1.0';
  const OBJECT_EXPORT_SCHEMA = 'sc-workspace-object-export/1.0';
  const HANDOFF_SCHEMA = 'sc-workspace-handoff/2.0';
  const HANDOFF_LEDGER_SCHEMA = 'sc-workspace-handoff-ledger/1.0';
  const HANDOFF_RETURN_SCHEMA = 'sc-workspace-handoff-return/1.0';
  const RETURN_ADAPTER_SCHEMA = 'sc-workspace-return-adapter/1.0';
  const PROCESSED_RETURN_KEY = 'sc_workspace_processed_returns_v1';
  const RESEARCH_SCHEMA = 'sc-workspace-research/1.0';
  const IDENTITY_SCHEMA = 'sc-workspace-identity/1.0';
  const ACCOUNT_PERSISTENCE_SCHEMA = 'sc-workspace-account-persistence/1.0';
  const CLOUD_BACKUP_SCHEMA = 'sc-workspace-cloud-backup/1.0';
  const CROSS_DEVICE_SYNC_SCHEMA = 'sc-workspace-cross-device-sync/1.0';
  const SYNC_PUSH_SCHEMA = 'sc-workspace-sync-push/1.0';
  const VERSION_HISTORY_SCHEMA = 'sc-workspace-version-history/1.0';
  const RESTORE_POINT_SCHEMA = 'sc-workspace-restore-point/1.0';
  const SAFE_ACTIONS_SCHEMA = 'sc-workspace-safe-actions/1.0';
  const ACTION_GATE_SCHEMA = 'sc-workspace-action-gate/1.0';
  const MAX_SAFE_ACTION_HISTORY = 120;
  const MAX_RESTORE_POINTS = 80;
  const MAX_RESTORE_POINTS_PER_PROJECT = 20;
  const MAX_RESTORE_POINT_BYTES = 1572864;
  const MAX_VERSION_HISTORY_EVENTS = 120;
  const MAX_ACCOUNT_HISTORY = 80;
  const MAX_SYNC_ENROLLMENTS = 25;
  const MAX_SYNC_HISTORY = 120;
  const SYNC_STATUS = new Set(['disabled','not-uploaded','up-to-date','local-ahead','remote-ahead','conflict','remote-missing','error']);
  const ANALYSIS_SCHEMA = 'sc-workspace-analysis/1.0';
  const DECISION_SCHEMA = 'sc-workspace-decision/1.0';
  const CANVAS_SCHEMA = 'sc-workspace-canvas/1.0';
  const TRACEABILITY_SCHEMA = 'sc-workspace-traceability/1.0';
  const REPRO_EXPORT_SCHEMA = 'sc-workspace-reproducibility-export/1.0';
  const BRIEFING_SCHEMA = 'sc-workspace-briefing/1.0';
  const PUBLICATION_EXPORT_SCHEMA = 'sc-workspace-publication-export/1.0';
  const GUIDED_WORKFLOWS_SCHEMA = 'sc-workspace-guided-workflows/1.0';
  const PERSONAL_KNOWLEDGE_SCHEMA = 'sc-workspace-personal-knowledge/1.0';
  const KNOWLEDGE_GRAPH_SCHEMA = 'sc-workspace-knowledge-graph/1.0';
  const ACTIVITY_INTELLIGENCE_SCHEMA = 'sc-workspace-activity-intelligence/1.0';
  const COLLABORATION_SCHEMA = 'sc-workspace-collaboration/1.0';
  const INSTITUTIONAL_SCHEMA = 'sc-workspace-institutional-handoff/1.0';
  const INSTITUTIONAL_PACKAGE_SCHEMA = 'sc-workspace-institutional-handoff-package/1.0';
  const INSTITUTIONAL_RECEIPT_SCHEMA = 'sc-workspace-institutional-handoff-receipt/1.0';
  const INSTITUTIONAL_RECEIPT_KEY = 'sc_workspace_institutional_receipt_v1';
  const REVIEW_PACKAGE_SCHEMA = 'sc-workspace-review-package/1.0';
  const MAX_COLLAB_SESSIONS = 60;
  const MAX_COLLAB_THREADS = 300;
  const MAX_COLLAB_PARTICIPANTS = 60;
  const MAX_COLLAB_HISTORY = 80;
  const MAX_INSTITUTIONAL_HANDOFFS = 60;
  const MAX_INSTITUTIONAL_HISTORY = 80;
  const INSTITUTIONAL_STATUS = new Set(['draft','prepared','exported','received','accepted','declined','closed']);
  const INSTITUTIONAL_RECEIPT_STATUS = new Set(['received','accepted','declined']);
  const COLLAB_ROLES = new Set(['owner','contributor','reviewer','observer']);
  const COLLAB_SESSION_STATUS = new Set(['draft','requested','in-review','changes-requested','approved','closed']);
  const COLLAB_THREAD_KIND = new Set(['comment','suggestion','question']);
  const COLLAB_THREAD_STATUS = new Set(['open','resolved']);
  const AI_ASSISTANCE_SCHEMA = 'sc-workspace-ai-assistance/1.0';
  const AI_REQUEST_EXPORT_SCHEMA = 'sc-workspace-ai-request-export/1.0';
  const AI_RESPONSE_EXPORT_SCHEMA = 'sc-workspace-ai-response-export/1.0';
  const AI_REQUEST_KEY = 'sc_workspace_ai_request_v1';
  const AI_RESPONSE_KEY = 'sc_workspace_ai_response_v1';
  const AI_RESPONSE_SCHEMA = 'sc-workspace-ai-response/1.0';
  const KNOWLEDGE_COLLECTION_EXPORT_SCHEMA = 'sc-workspace-knowledge-collection-export/1.0';
  const INTEROPERABILITY_SCHEMA = 'sc-workspace-interoperability/1.0';
  const INTERCHANGE_EXPORT_SCHEMA = 'sc-workspace-interchange/1.0';
  const SHARE_SCHEMA = 'sc-workspace-share/1.0';
  const PORTABLE_PROJECT_SCHEMA = 'sc-workspace-portable-project/1.0';
  const MAX_SHARE_HISTORY = 60;
  const MAX_NEXT_ACTIONS = 120;
  const MAX_DISMISSED_SIGNALS = 300;
  const NEXT_ACTION_STATUS = new Set(['open','done','deferred']);
  const NEXT_ACTION_PRIORITY = new Set(['low','normal','high']);
  const ACTIVITY_SIGNAL_KINDS = new Set(['workflow','research','analysis','decision','traceability','handoff','briefing','collaboration','institutional','stale']);
  const MAX_INTEROP_HISTORY = 60;
  const MAX_INTEROP_IMPORT_OBJECTS = 100;
  const INTEROP_FORMATS = new Set(['json','csv','tsv','markdown','html','text']);
  const AI_TASKS = new Set(['grounded-summary','evidence-gaps','compare-alternatives','briefing-draft','method-explanation','general-question']);
  const AI_SESSION_STATUS = new Set(['prepared','sent','response-received','accepted','rejected']);
  const AI_RESPONSE_SOURCES = new Set(['manual','research-librarian','adapter','external']);
  const WORKFLOW_RUN_STATUS = new Set(['active','paused','complete']);
  const WORKFLOW_STEP_STATUS = new Set(['todo','in-progress','complete','skipped']);
  const TRACE_RELATIONS = new Set(['derived-from','supports','contradicts','uses','produced-by','informs','supersedes','cites']);
  const REPRO_STATUS = new Set(['draft','ready','verified','stale']);
  const BRIEFING_FORMATS = new Set(['briefing','memo','report','article','publication-draft']);
  const BRIEFING_STATUS = new Set(['draft','review','ready','exported']);
  const MAX_ACTIVITY = 60;
  const MAX_RECENT_TOOLS = 8;
  const MAX_OBJECTS = 250;
  const MAX_RESEARCH_QUESTIONS = 100;
  const MAX_RESEARCH_CLAIMS = 100;
  const MAX_READING_QUEUE = 250;
  const MAX_EVIDENCE_LINKS = 500;
  const MAX_ANALYSIS_QUESTIONS = 100;
  const MAX_ANALYSIS_VARIABLES = 120;
  const MAX_ANALYSIS_ASSUMPTIONS = 120;
  const MAX_ANALYSIS_METHODS = 100;
  const MAX_ANALYSIS_COMPARISONS = 100;
  const MAX_ANALYSIS_FINDINGS = 150;
  const MAX_DECISIONS = 60;
  const MAX_DECISION_OPTIONS = 240;
  const MAX_DECISION_CRITERIA = 180;
  const MAX_DECISION_ASSESSMENTS = 1000;
  const MAX_DECISION_RISKS = 300;
  const MAX_CANVAS_BOARDS = 30;
  const MAX_CANVAS_NODES = 500;
  const MAX_CANVAS_EDGES = 1000;
  const MAX_CANVAS_FRAMES = 100;
  const MAX_HANDOFFS = 150;
  const MAX_EVIDENCE_ASSESSMENTS = 250;
  const MAX_LINEAGE_RELATIONS = 1000;
  const MAX_REPRO_RECORDS = 100;
  const MAX_BRIEFING_DRAFTS = 30;
  const MAX_BRIEFING_SECTIONS = 24;
  const MAX_BRIEFING_OBJECT_REFS = 80;
  const MAX_WORKFLOW_RUNS = 20;
  const MAX_WORKFLOW_STEPS = 16;
  const MAX_WORKFLOW_OBJECT_REFS = 80;
  const MAX_KNOWLEDGE_COLLECTIONS = 30;
  const MAX_KNOWLEDGE_COLLECTION_ITEMS = 200;
  const MAX_GRAPH_NODES = 1600;
  const MAX_GRAPH_EDGES = 5000;
  const MAX_AI_SESSIONS = 40;
  const MAX_AI_OBJECT_REFS = 24;
  const MAX_AI_PROMPT = 5000;
  const MAX_AI_RESPONSE = 30000;
  const MAX_HANDOFF_OBJECT_REFS = 12;
  const MAX_RETURN_ARTIFACTS = 20;
  const ALLOWED_STATUS = new Set(['active', 'paused', 'complete']);
  const OBJECT_TYPES = new Set(['source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export']);
  const OBJECT_STATUS = new Set(['draft', 'working', 'ready']);
  const GRAPH_RELATIONS = new Set(['contains','sourced-from','same-source','evidence-from','uses','informs','supports','contradicts','derived-from','produced-by','supersedes','cites']);
  const PROVENANCE_TYPES = new Set(['manual', 'web', 'library', 'dataset', 'tool', 'imported']);
  const QUESTION_STATUS = new Set(['open', 'answered', 'deferred']);
  const QUESTION_PRIORITY = new Set(['low', 'normal', 'high']);
  const CLAIM_STATUS = new Set(['exploratory', 'supported', 'contested', 'rejected']);
  const READING_STATUS = new Set(['unread', 'reading', 'read']);
  const ANALYSIS_QUESTION_STATUS = new Set(['open', 'resolved', 'deferred']);
  const ANALYSIS_VARIABLE_ROLE = new Set(['outcome', 'input', 'control', 'parameter', 'indicator']);
  const ANALYSIS_ASSUMPTION_STATUS = new Set(['untested', 'supported', 'challenged']);
  const ANALYSIS_METHOD_TYPE = new Set(['descriptive', 'comparative', 'statistical', 'modeling', 'scenario', 'sensitivity', 'other']);
  const ANALYSIS_FINDING_STATUS = new Set(['preliminary', 'supported', 'contested']);
  const DECISION_STATUS = new Set(['framing', 'evaluating', 'decided', 'revisit']);
  const DECISION_OPTION_STATUS = new Set(['candidate', 'shortlisted', 'selected', 'rejected']);
  const DECISION_CONFIDENCE = new Set(['low', 'medium', 'high']);
  const DECISION_RISK_LEVEL = new Set(['low', 'medium', 'high']);
  const CANVAS_BOARD_STATUS = new Set(['draft', 'working', 'ready']);
  const CANVAS_NODE_TYPE = new Set(['note', 'question', 'claim', 'evidence', 'data', 'analysis', 'decision', 'system', 'stakeholder', 'idea']);
  const CANVAS_RELATION_TYPE = new Set(['supports', 'contradicts', 'depends-on', 'influences', 'contains', 'causes', 'relates-to', 'sequence']);
  const HANDOFF_STATUS = new Set(['prepared', 'launched', 'returned', 'closed']);
  const HANDOFF_INTENT = new Set(['research', 'analysis', 'decision', 'canvas', 'data', 'compute', 'publish', 'general']);
  const HANDOFF_DESTINATIONS = new Set(['research-librarian', 'knowledge-library', 'site-intelligence', 'workbench', 'analytics-r', 'decision-studio', 'catalyst-canvas', 'catalyst-data', 'lab']);
  const HANDOFF_INTENT_BY_TOOL = { 'research-librarian':'research','knowledge-library':'research','site-intelligence':'data','workbench':'compute','analytics-r':'analysis','decision-studio':'decision','catalyst-canvas':'canvas','catalyst-data':'data','lab':'compute' };
  const RETURN_ADAPTERS = {
    'research-librarian': { label:'Research Librarian', preferredTypes:['source','evidence','document'], aliases:['research-librarian','research_librarian','researchlibrarian','sc-research-librarian'] },
    'knowledge-library': { label:'Knowledge Library', preferredTypes:['source','document'], aliases:['knowledge-library','knowledge_library','library','sc-knowledge-library'] },
    'site-intelligence': { label:'Site Intelligence', preferredTypes:['dataset','evidence','analysis','export'], aliases:['site-intelligence','site_intelligence','siteintelligence','sc-site-intelligence'] },
    'workbench': { label:'Workbench', preferredTypes:['dataset','analysis','export','document'], aliases:['workbench','sc-workbench'] },
    'analytics-r': { label:'Analytics R', preferredTypes:['dataset','analysis','export','document'], aliases:['analytics-r','analytics_r','analyticsr','catalyst-analytics-r'] },
    'decision-studio': { label:'Decision Studio', preferredTypes:['decision','document','export'], aliases:['decision-studio','decision_studio','decisionstudio','sc-decision-studio'] },
    'catalyst-canvas': { label:'Catalyst Canvas', preferredTypes:['document','decision','export'], aliases:['catalyst-canvas','catalyst_canvas','canvas','sc-catalyst-canvas'] },
    'catalyst-data': { label:'Catalyst Data', preferredTypes:['dataset','analysis','export','document'], aliases:['catalyst-data','catalyst_data','data','sc-catalyst-data'] },
    'lab': { label:'Lab', preferredTypes:['dataset','analysis','evidence','export','document'], aliases:['lab','sustainable-catalyst-lab','sc-lab'] }
  };
  const RETURN_ADAPTER_ALIASES = (() => { const out={}; Object.entries(RETURN_ADAPTERS).forEach(([key,cfg])=>cfg.aliases.forEach((alias)=>{out[String(alias).toLowerCase()]=key;})); return out; })();
  const OBJECT_LABELS = {
    source: 'Source', evidence: 'Evidence', dataset: 'Dataset', analysis: 'Analysis',
    decision: 'Decision', document: 'Document', export: 'Export'
  };

  let recoveryNotice = '';
  let memoryDeviceId = null;
  const IDENTITY_CONFIG = (window.SCWorkspaceIdentity && typeof window.SCWorkspaceIdentity === 'object') ? window.SCWorkspaceIdentity : {};

  function accountSession() { return IDENTITY_CONFIG.authenticated ? 'authenticated' : 'anonymous'; }

  function deviceId() {
    if (memoryDeviceId) return memoryDeviceId;
    try {
      const existing = window.localStorage.getItem(DEVICE_KEY);
      if (existing && /^scwd-[a-zA-Z0-9-]{8,160}$/.test(existing)) { memoryDeviceId = existing; return memoryDeviceId; }
      memoryDeviceId = id('scwd');
      window.localStorage.setItem(DEVICE_KEY, memoryDeviceId);
      return memoryDeviceId;
    } catch (_) {
      memoryDeviceId = memoryDeviceId || id('scwd');
      return memoryDeviceId;
    }
  }

  function identityTemplate() {
    return {
      schema: IDENTITY_SCHEMA,
      deviceId: deviceId(),
      session: accountSession(),
      persistenceMode: 'device-local',
      cloudSync: false,
      serverProjectStorage: false,
      updatedAt: nowIso()
    };
  }

  function normalizeIdentity() { return identityTemplate(); }

  function projectPersistenceTemplate() {
    return {
      scope: 'device',
      deviceId: deviceId(),
      syncState: 'local-only',
      accountEligible: true,
      serverStored: false
    };
  }

  function normalizeProjectPersistence() { return projectPersistenceTemplate(); }

  function nowIso() { return new Date().toISOString(); }

  function id(prefix) {
    if (window.crypto && typeof window.crypto.randomUUID === 'function') return `${prefix}-${window.crypto.randomUUID()}`;
    return `${prefix}-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`;
  }

  function validIso(value) {
    return Boolean(value && typeof value === 'string' && !Number.isNaN(Date.parse(value)));
  }

  function knowledgeTemplate() {
    const stamp = nowIso();
    return {
      schema: PERSONAL_KNOWLEDGE_SCHEMA,
      collections: [],
      activeCollectionId: null,
      preferences: { query: '', type: 'all', project: 'all', tag: '', scope: 'active' },
      createdAt: stamp,
      updatedAt: stamp
    };
  }

  function normalizeKnowledgeRef(raw, validObjectKeys) {
    if (!raw || typeof raw !== 'object') return null;
    const projectId = String(raw.projectId || '').slice(0, 160);
    const objectId = String(raw.objectId || '').slice(0, 160);
    if (!projectId || !objectId || !validObjectKeys.has(`${projectId}:${objectId}`)) return null;
    return { projectId, objectId };
  }

  function normalizeKnowledgeCollection(raw, validObjectKeys) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    const seen = new Set();
    const items = [];
    (Array.isArray(raw.items) ? raw.items : []).forEach((value) => {
      const ref = normalizeKnowledgeRef(value, validObjectKeys);
      if (!ref) return;
      const key = `${ref.projectId}:${ref.objectId}`;
      if (!seen.has(key) && items.length < MAX_KNOWLEDGE_COLLECTION_ITEMS) { seen.add(key); items.push(ref); }
    });
    return {
      id: String(raw.id || id('kc')).slice(0, 160),
      title: String(raw.title || 'Untitled collection').trim().slice(0, 160) || 'Untitled collection',
      description: String(raw.description || '').slice(0, 1000),
      items,
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeKnowledge(raw, projects=[]) {
    const base = knowledgeTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const projectIds = new Set(projects.map(p => p.id));
    const validObjectKeys = new Set(projects.flatMap(p => p.objects.map(o => `${p.id}:${o.id}`)));
    base.collections = (Array.isArray(value.collections) ? value.collections : []).map(v => normalizeKnowledgeCollection(v, validObjectKeys)).filter(Boolean).slice(0, MAX_KNOWLEDGE_COLLECTIONS);
    base.activeCollectionId = base.collections.some(c => c.id === value.activeCollectionId) ? value.activeCollectionId : null;
    const pref = value.preferences && typeof value.preferences === 'object' ? value.preferences : {};
    base.preferences = {
      query: String(pref.query || '').slice(0, 240),
      type: pref.type === 'all' || OBJECT_TYPES.has(pref.type) ? (pref.type || 'all') : 'all',
      project: pref.project === 'all' || projectIds.has(pref.project) ? (pref.project || 'all') : 'all',
      tag: String(pref.tag || '').slice(0, 80),
      scope: pref.scope === 'all' ? 'all' : 'active'
    };
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchKnowledge() {
    if (!state.knowledge) state.knowledge = knowledgeTemplate();
    state.knowledge.updatedAt = nowIso();
    state.updatedAt = state.knowledge.updatedAt;
  }

  function cleanKnowledgeObjectReferences(projectId, objectId) {
    if (!state || !state.knowledge) return;
    state.knowledge.collections.forEach(c => { c.items = c.items.filter(ref => !(ref.projectId === projectId && ref.objectId === objectId)); c.updatedAt = nowIso(); });
    touchKnowledge();
  }

  function cleanKnowledgeProjectReferences(projectId) {
    if (!state || !state.knowledge) return;
    state.knowledge.collections.forEach(c => { c.items = c.items.filter(ref => ref.projectId !== projectId); c.updatedAt = nowIso(); });
    touchKnowledge();
  }

  function knowledgeIndex() {
    const entries = [];
    state.projects.forEach(project => {
      project.objects.forEach(object => {
        if (object.archivedAt) return;
        entries.push({
          key: `${project.id}:${object.id}`,
          projectId: project.id,
          projectTitle: project.title,
          projectArchived: Boolean(project.archivedAt),
          objectId: object.id,
          object
        });
      });
    });
    return entries.sort((a,b) => String(b.object.updatedAt).localeCompare(String(a.object.updatedAt)));
  }

  function knowledgeReferenceCount(entry) {
    const project = state.projects.find(p => p.id === entry.projectId);
    if (!project) return 0;
    const oid = entry.objectId;
    let count = 0;
    if (project.traceability) count += project.traceability.lineage.filter(r => r.fromObjectId === oid || r.toObjectId === oid).length;
    if (project.research) count += project.research.claims.filter(c => c.evidenceObjectIds.includes(oid)).length + project.research.evidenceLinks.filter(l => l.sourceObjectId === oid || l.evidenceObjectId === oid).length;
    if (project.analysis) count += project.analysis.findings.filter(f => f.evidenceObjectIds.includes(oid) || f.analysisObjectId === oid).length;
    if (project.canvas) count += project.canvas.boards.reduce((n,b) => n + b.nodes.filter(node => node.objectId === oid).length, 0);
    if (project.briefing) count += project.briefing.drafts.reduce((n,d) => n + (d.objectIds.includes(oid) ? 1 : 0) + d.sections.filter(sec => sec.objectIds.includes(oid)).length, 0);
    return count;
  }

  function relatedKnowledgeEntries(entry, allEntries) {
    const source = entry.object;
    const sourceTags = new Set(source.tags.map(t => t.toLowerCase()));
    const sourceUrl = String(source.provenance?.sourceUrl || '').trim().toLowerCase();
    const sourceTitle = String(source.provenance?.sourceTitle || '').trim().toLowerCase();
    return allEntries.filter(other => other.key !== entry.key).map(other => {
      let score = 0; const reasons = [];
      const shared = other.object.tags.filter(t => sourceTags.has(t.toLowerCase()));
      if (shared.length) { score += Math.min(shared.length, 3) * 2; reasons.push(`shared tags: ${shared.slice(0,3).join(', ')}`); }
      const otherUrl = String(other.object.provenance?.sourceUrl || '').trim().toLowerCase();
      if (sourceUrl && otherUrl && sourceUrl === otherUrl) { score += 6; reasons.push('same source URL'); }
      const otherTitle = String(other.object.provenance?.sourceTitle || '').trim().toLowerCase();
      if (sourceTitle && otherTitle && sourceTitle === otherTitle) { score += 4; reasons.push('same provenance title'); }
      if (source.type === other.object.type) score += 1;
      return { entry: other, score, reasons };
    }).filter(x => x.score >= 3).sort((a,b) => b.score - a.score || String(b.entry.object.updatedAt).localeCompare(String(a.entry.object.updatedAt))).slice(0, 8);
  }



  function activityIntelligenceTemplate() {
    const stamp = nowIso();
    return {
      schema: ACTIVITY_INTELLIGENCE_SCHEMA,
      preferences: { project:'all', windowDays:30, staleDays:14, signal:'all' },
      nextActions: [],
      dismissedSignalIds: [],
      createdAt: stamp,
      updatedAt: stamp
    };
  }

  function normalizeNextAction(raw, projectIds) {
    if (!raw || typeof raw !== 'object') return null;
    const projectId = String(raw.projectId || '').slice(0,160);
    if (!projectIds.has(projectId)) return null;
    const stamp = nowIso();
    const dueAt = validIso(raw.dueAt) ? raw.dueAt : null;
    const status = NEXT_ACTION_STATUS.has(raw.status) ? raw.status : 'open';
    return {
      id: String(raw.id || id('na')).slice(0,160),
      title: String(raw.title || '').trim().slice(0,240),
      projectId,
      objectId: String(raw.objectId || '').slice(0,160),
      priority: NEXT_ACTION_PRIORITY.has(raw.priority) ? raw.priority : 'normal',
      status,
      dueAt,
      note: String(raw.note || '').slice(0,1000),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp,
      completedAt: status === 'done' && validIso(raw.completedAt) ? raw.completedAt : null
    };
  }

  function normalizeActivityIntelligence(raw, projects=[]) {
    const base = activityIntelligenceTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const projectIds = new Set(projects.map(p => p.id));
    const pref = value.preferences && typeof value.preferences === 'object' ? value.preferences : {};
    base.preferences = {
      project: pref.project === 'all' || projectIds.has(pref.project) ? (pref.project || 'all') : 'all',
      windowDays: [7,30,90].includes(Number(pref.windowDays)) ? Number(pref.windowDays) : 30,
      staleDays: [7,14,30].includes(Number(pref.staleDays)) ? Number(pref.staleDays) : 14,
      signal: pref.signal === 'all' || ACTIVITY_SIGNAL_KINDS.has(pref.signal) ? (pref.signal || 'all') : 'all'
    };
    base.nextActions = (Array.isArray(value.nextActions) ? value.nextActions : []).map(v => normalizeNextAction(v, projectIds)).filter(v => v && v.title).slice(0, MAX_NEXT_ACTIONS);
    base.dismissedSignalIds = [...new Set((Array.isArray(value.dismissedSignalIds) ? value.dismissedSignalIds : []).map(v => String(v).slice(0,260)))].slice(0, MAX_DISMISSED_SIGNALS);
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchActivityIntelligence() {
    if (!state.activityIntelligence) state.activityIntelligence = activityIntelligenceTemplate();
    state.activityIntelligence.updatedAt = nowIso();
    state.updatedAt = state.activityIntelligence.updatedAt;
  }

  function daysSince(iso) {
    if (!validIso(iso)) return Number.POSITIVE_INFINITY;
    return Math.max(0, (Date.now() - Date.parse(iso)) / 86400000);
  }

  function derivedAttentionSignals(currentState) {
    const ai = normalizeActivityIntelligence(currentState.activityIntelligence, currentState.projects);
    const dismissed = new Set(ai.dismissedSignalIds);
    const selectedProject = ai.preferences.project;
    const selectedKind = ai.preferences.signal;
    const signals = [];
    const add = (signal) => { if (!dismissed.has(signal.id) && (selectedProject === 'all' || signal.projectId === selectedProject) && (selectedKind === 'all' || signal.kind === selectedKind)) signals.push(signal); };
    currentState.projects.filter(p => !p.archivedAt).forEach(project => {
      if (project.status !== 'complete' && daysSince(project.updatedAt) >= ai.preferences.staleDays) add({id:`sig:stale:${project.id}`,projectId:project.id,kind:'stale',severity:'attention',title:'Project has gone quiet',detail:`No recorded project update for ${Math.floor(daysSince(project.updatedAt))} days.`,targetMode:'overview',at:project.updatedAt});
      (project.research?.questions || []).filter(q => q.status === 'open' && q.priority === 'high').forEach(q => add({id:`sig:rq:${project.id}:${q.id}`,projectId:project.id,kind:'research',severity:'high',title:'High-priority research question remains open',detail:q.text,targetMode:'research',at:q.updatedAt}));
      (project.analysis?.assumptions || []).filter(a => a.status === 'challenged').forEach(a => add({id:`sig:assumption:${project.id}:${a.id}`,projectId:project.id,kind:'analysis',severity:'high',title:'Analytical assumption is challenged',detail:a.text || a.title || 'A recorded assumption requires review.',targetMode:'analysis',at:a.updatedAt}));
      (project.analysis?.findings || []).filter(f => f.status === 'contested').forEach(f => add({id:`sig:finding:${project.id}:${f.id}`,projectId:project.id,kind:'analysis',severity:'high',title:'Finding is contested',detail:f.text || f.title || 'A finding remains contested.',targetMode:'analysis',at:f.updatedAt}));
      (project.decision?.decisions || []).filter(d => d.status === 'evaluating' || d.status === 'revisit').forEach(d => add({id:`sig:decision:${project.id}:${d.id}`,projectId:project.id,kind:'decision',severity:d.status === 'revisit'?'high':'attention',title:d.status === 'revisit'?'Decision marked for reconsideration':'Decision still being evaluated',detail:d.question || d.title || 'Decision record requires attention.',targetMode:'decision',at:d.updatedAt}));
      (project.traceability?.reproducibility || []).filter(r => r.status === 'stale').forEach(r => add({id:`sig:repro:${project.id}:${r.id}`,projectId:project.id,kind:'traceability',severity:'high',title:'Reproducibility record is stale',detail:r.title || 'Reproduction record requires verification.',targetMode:'traceability',at:r.updatedAt}));
      (project.handoffs?.entries || []).filter(h => h.status === 'launched' || h.status === 'prepared').forEach(h => add({id:`sig:handoff:${project.id}:${h.id}`,projectId:project.id,kind:'handoff',severity:'info',title:'Connected-tool handoff is awaiting return',detail:`${h.destinationLabel || h.destination || 'Connected tool'} · ${h.intent || 'general'}`,targetMode:'overview',at:h.updatedAt || h.launchedAt || h.createdAt}));
      (project.briefing?.drafts || []).filter(d => d.status === 'review').forEach(d => add({id:`sig:briefing:${project.id}:${d.id}`,projectId:project.id,kind:'briefing',severity:'attention',title:'Briefing draft is in review',detail:d.title || 'Publication draft requires review.',targetMode:'briefing',at:d.updatedAt}));
      (currentState.collaboration?.sessions || []).filter(s => s.localProjectId === project.id && ['requested','in-review','changes-requested'].includes(s.status)).forEach(s => { const open=(s.threads||[]).filter(t=>t.status==='open').length; add({id:`sig:collab:${project.id}:${s.id}`,projectId:project.id,kind:'collaboration',severity:s.status==='changes-requested'?'high':'attention',title:s.status==='changes-requested'?'Review changes requested':'Collaboration review remains open',detail:`${s.title} · ${open} open thread${open===1?'':'s'}`,targetMode:'overview',at:s.updatedAt}); });
      (currentState.institutional?.handoffs || []).filter(h => h.projectId === project.id && ['prepared','exported','received'].includes(h.status)).forEach(h => add({id:`sig:institutional:${project.id}:${h.id}`,projectId:project.id,kind:'institutional',severity:h.status==='received'?'info':'attention',title:h.status==='received'?'Institutional handoff receipt received':'Institutional handoff awaiting institutional receipt',detail:`${h.organizationLabel || 'Catalyst Intelligence'} · ${h.status}`,targetMode:'overview',at:h.updatedAt}));
      (project.guidedWorkflows?.runs || []).filter(run => run.status === 'active').forEach(run => {
        const next = (run.steps || []).find(step => step.status === 'in-progress') || (run.steps || []).find(step => step.status === 'todo');
        if (next) add({id:`sig:workflow:${project.id}:${run.id}:${next.id}`,projectId:project.id,kind:'workflow',severity:'info',title:'Guided workflow has a next step',detail:`${run.title || run.templateId}: ${next.title}`,targetMode:'guide',at:next.updatedAt || run.updatedAt});
      });
    });
    const order = {high:0,attention:1,info:2};
    return signals.sort((a,b)=>(order[a.severity]-order[b.severity]) || String(b.at||'').localeCompare(String(a.at||'')));
  }

  function workspaceActivityTimeline(currentState) {
    const ai = normalizeActivityIntelligence(currentState.activityIntelligence,currentState.projects);
    const since = Date.now() - ai.preferences.windowDays * 86400000;
    const rows = [];
    currentState.projects.forEach(project => {
      if (ai.preferences.project !== 'all' && project.id !== ai.preferences.project) return;
      (project.activity || []).forEach(entry => { if (validIso(entry.at) && Date.parse(entry.at) >= since) rows.push({id:`${project.id}:${entry.id}`,projectId:project.id,projectTitle:project.title,type:entry.type,summary:entry.summary,at:entry.at}); });
    });
    return rows.sort((a,b)=>String(b.at).localeCompare(String(a.at))).slice(0,160);
  }

  function workflowIntelligenceRows(currentState) {
    const ai = normalizeActivityIntelligence(currentState.activityIntelligence,currentState.projects);
    const rows=[];
    currentState.projects.filter(p=>!p.archivedAt).forEach(project=>{
      if(ai.preferences.project!=='all'&&project.id!==ai.preferences.project)return;
      (project.guidedWorkflows?.runs||[]).filter(run=>run.status!=='complete').forEach(run=>{
        const steps=run.steps||[],complete=steps.filter(s=>s.status==='complete'||s.status==='skipped').length,next=steps.find(s=>s.status==='in-progress')||steps.find(s=>s.status==='todo')||null;
        rows.push({projectId:project.id,projectTitle:project.title,runId:run.id,title:run.title||run.templateId,status:run.status,complete,total:steps.length,next});
      });
    });
    return rows.sort((a,b)=>a.projectTitle.localeCompare(b.projectTitle)||a.title.localeCompare(b.title));
  }

  function knowledgeGraphTemplate() {
    const stamp = nowIso();
    return {
      schema: KNOWLEDGE_GRAPH_SCHEMA,
      preferences: { query:'', nodeType:'all', relation:'all', project:'all', scope:'active', depth:1 },
      selectedNodeId: '',
      createdAt: stamp,
      updatedAt: stamp
    };
  }

  function normalizeKnowledgeGraph(raw, projects=[]) {
    const base=knowledgeGraphTemplate(), value=raw&&typeof raw==='object'?raw:{}, pref=value.preferences&&typeof value.preferences==='object'?value.preferences:{};
    const projectIds=new Set(projects.map(p=>p.id));
    const allowedTypes=new Set(['all','project','provenance',...OBJECT_TYPES]);
    base.preferences={
      query:String(pref.query||'').slice(0,240),
      nodeType:allowedTypes.has(pref.nodeType)?pref.nodeType:'all',
      relation:pref.relation==='all'||GRAPH_RELATIONS.has(pref.relation)?(pref.relation||'all'):'all',
      project:pref.project==='all'||projectIds.has(pref.project)?(pref.project||'all'):'all',
      scope:pref.scope==='all'?'all':'active',
      depth:Number(pref.depth)===2?2:1
    };
    base.selectedNodeId=String(value.selectedNodeId||'').slice(0,260);
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt;
    base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt;
    return base;
  }

  function touchKnowledgeGraph() {
    state.knowledgeGraph=normalizeKnowledgeGraph(state.knowledgeGraph,state.projects);
    state.knowledgeGraph.updatedAt=nowIso();
    state.updatedAt=state.knowledgeGraph.updatedAt;
  }

  function graphToken(value) {
    const text=String(value||''); let hash=2166136261;
    for(let i=0;i<text.length;i++){hash^=text.charCodeAt(i);hash=Math.imul(hash,16777619);}
    return (hash>>>0).toString(16).padStart(8,'0');
  }

  function buildKnowledgeGraph() {
    const nodes=new Map(), edges=[], edgeKeys=new Set();
    const addNode=(node)=>{if(node&&node.id&&!nodes.has(node.id)&&nodes.size<MAX_GRAPH_NODES)nodes.set(node.id,node);};
    const addEdge=(from,to,relation,meta={})=>{if(!from||!to||from===to||!GRAPH_RELATIONS.has(relation)||edges.length>=MAX_GRAPH_EDGES)return;const key=`${from}|${relation}|${to}`;if(edgeKeys.has(key))return;edgeKeys.add(key);edges.push({id:`ge-${graphToken(key)}`,from,to,relation,...meta});};
    const objectNodeId=(projectId,objectId)=>`object:${projectId}:${objectId}`;
    state.projects.forEach(project=>{
      const projectNode=`project:${project.id}`;
      addNode({id:projectNode,type:'project',label:project.title,summary:project.description||'',projectId:project.id,projectTitle:project.title,archived:Boolean(project.archivedAt),updatedAt:project.updatedAt||project.createdAt});
      project.objects.filter(o=>!o.archivedAt).forEach(object=>{
        const oid=objectNodeId(project.id,object.id);
        addNode({id:oid,type:object.type,label:object.title,summary:object.summary||'',projectId:project.id,projectTitle:project.title,objectId:object.id,archived:Boolean(project.archivedAt),tags:object.tags||[],updatedAt:object.updatedAt||object.createdAt});
        addEdge(projectNode,oid,'contains',{projectId:project.id});
        const provenanceKey=String(object.provenance?.sourceUrl||object.provenance?.sourceTitle||'').trim();
        if(provenanceKey){const pid=`provenance:${graphToken(provenanceKey.toLowerCase())}`;addNode({id:pid,type:'provenance',label:object.provenance?.sourceTitle||object.provenance?.sourceUrl||'Provenance source',summary:object.provenance?.sourceUrl||object.provenance?.sourceType||'',projectId:'',projectTitle:'',archived:false,updatedAt:object.provenance?.capturedAt||object.updatedAt});addEdge(oid,pid,'sourced-from',{projectId:project.id});}
      });
      const byId=new Map(project.objects.filter(o=>!o.archivedAt).map(o=>[o.id,objectNodeId(project.id,o.id)]));
      (project.traceability?.lineage||[]).forEach(rel=>{const from=byId.get(rel.fromObjectId),to=byId.get(rel.toObjectId);if(from&&to)addEdge(from,to,GRAPH_RELATIONS.has(rel.relation)?rel.relation:'derived-from',{projectId:project.id,note:rel.note||''});});
      (project.research?.evidenceLinks||[]).forEach(link=>{const source=byId.get(link.sourceObjectId),evidence=byId.get(link.evidenceObjectId);if(source&&evidence)addEdge(source,evidence,'evidence-from',{projectId:project.id});});
      (project.analysis?.methods||[]).forEach(method=>{const analysis=byId.get(method.analysisObjectId);if(!analysis)return;(method.datasetObjectIds||[]).forEach(idValue=>{const dataset=byId.get(idValue);if(dataset)addEdge(dataset,analysis,'uses',{projectId:project.id});});});
      (project.analysis?.findings||[]).forEach(finding=>{const analysis=byId.get(finding.analysisObjectId);if(!analysis)return;(finding.evidenceObjectIds||[]).forEach(idValue=>{const evidence=byId.get(idValue);if(evidence)addEdge(evidence,analysis,'informs',{projectId:project.id});});});
      (project.decision?.decisions||[]).forEach(decision=>{const decisionObject=byId.get(decision.decisionObjectId);if(!decisionObject)return;(project.decision.options||[]).filter(option=>option.decisionId===decision.id).forEach(option=>{(option.evidenceObjectIds||[]).forEach(idValue=>{const evidence=byId.get(idValue);if(evidence)addEdge(evidence,decisionObject,'informs',{projectId:project.id});});(option.analysisObjectIds||[]).forEach(idValue=>{const analysis=byId.get(idValue);if(analysis)addEdge(analysis,decisionObject,'informs',{projectId:project.id});});});});
    });
    const provenanceBuckets=new Map();
    nodes.forEach(node=>{if(node.type!=='source'&&node.type!=='evidence'&&node.type!=='document')return;const project=state.projects.find(p=>p.id===node.projectId),object=project?.objects.find(o=>o.id===node.objectId);const key=String(object?.provenance?.sourceUrl||object?.provenance?.sourceTitle||'').trim().toLowerCase();if(!key)return;if(!provenanceBuckets.has(key))provenanceBuckets.set(key,[]);provenanceBuckets.get(key).push(node.id);});
    provenanceBuckets.forEach(ids=>{if(ids.length<2)return;for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length&&j<i+8;j++){addEdge(ids[i],ids[j],'same-source');addEdge(ids[j],ids[i],'same-source');}});
    return {schema:KNOWLEDGE_GRAPH_SCHEMA,nodes:Array.from(nodes.values()),edges};
  }

  function graphNeighborhood(graph,nodeId,depth=1,relation='all') {
    if(!nodeId)return {nodes:[],edges:[]};
    const seen=new Set([nodeId]), frontier=[nodeId], selectedEdges=[];
    for(let d=0;d<depth;d++){
      const next=[];
      graph.edges.forEach(edge=>{if(relation!=='all'&&edge.relation!==relation)return;const hit=frontier.includes(edge.from)||frontier.includes(edge.to);if(!hit)return;selectedEdges.push(edge);const other=frontier.includes(edge.from)?edge.to:edge.from;if(!seen.has(other)){seen.add(other);next.push(other);}});
      frontier.splice(0,frontier.length,...next);
      if(!frontier.length)break;
    }
    const edgeIds=new Set(selectedEdges.map(e=>e.id));
    return {nodes:graph.nodes.filter(n=>seen.has(n.id)),edges:graph.edges.filter(e=>edgeIds.has(e.id)&&seen.has(e.from)&&seen.has(e.to))};
  }

  function interoperabilityTemplate() {
    const stamp=nowIso();
    return { schema:INTEROPERABILITY_SCHEMA, history:[], createdAt:stamp, updatedAt:stamp };
  }
  function normalizeInteroperability(raw) {
    const base=interoperabilityTemplate(), value=raw&&typeof raw==='object'?raw:{};
    base.history=(Array.isArray(value.history)?value.history:[]).map(item=>({
      id:String(item&&item.id||id('io')).slice(0,160), direction:item&&item.direction==='export'?'export':'import',
      format:INTEROP_FORMATS.has(item&&item.format)?item.format:'json', projectId:String(item&&item.projectId||'').slice(0,160),
      projectTitle:String(item&&item.projectTitle||'').slice(0,160), fileName:String(item&&item.fileName||'').slice(0,240),
      fingerprint:String(item&&item.fingerprint||'').slice(0,128), objectCount:Math.max(0,Math.min(1000,Number(item&&item.objectCount)||0)),
      at:validIso(item&&item.at)?item.at:nowIso()
    })).slice(0,MAX_INTEROP_HISTORY);
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt; base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt; return base;
  }
  function touchInteroperability(){state.interoperability=normalizeInteroperability(state.interoperability);state.interoperability.updatedAt=nowIso();}

  async function sha256Text(text){
    if(window.crypto&&window.crypto.subtle&&window.TextEncoder){const data=new TextEncoder().encode(String(text||''));const hash=await window.crypto.subtle.digest('SHA-256',data);return Array.from(new Uint8Array(hash)).map(b=>b.toString(16).padStart(2,'0')).join('');}
    return '';
  }
  function detectInteropFormat(file){
    const name=String(file&&file.name||'').toLowerCase();
    if(name.endsWith('.csv'))return 'csv'; if(name.endsWith('.tsv'))return 'tsv'; if(name.endsWith('.md')||name.endsWith('.markdown'))return 'markdown';
    if(name.endsWith('.html')||name.endsWith('.htm'))return 'html'; if(name.endsWith('.txt'))return 'text'; if(name.endsWith('.json'))return 'json';
    const type=String(file&&file.type||'').toLowerCase(); if(type.includes('csv'))return 'csv'; if(type.includes('tab-separated'))return 'tsv'; if(type.includes('markdown'))return 'markdown'; if(type.includes('html'))return 'html'; if(type.includes('json'))return 'json'; return 'text';
  }
  function csvRows(text, delimiter=','){
    const rows=[]; let row=[],field='',quoted=false; const src=String(text||'');
    for(let i=0;i<src.length;i++){const ch=src[i];if(ch==='"'){if(quoted&&src[i+1]==='"'){field+='"';i++;}else quoted=!quoted;}else if(ch===delimiter&&!quoted){row.push(field);field='';}else if((ch==='\n'||ch==='\r')&&!quoted){if(ch==='\r'&&src[i+1]==='\n')i++;row.push(field);field='';if(row.some(v=>String(v).trim()!==''))rows.push(row);row=[];}else field+=ch;}
    row.push(field);if(row.some(v=>String(v).trim()!==''))rows.push(row);return rows.slice(0,5000);
  }
  function htmlToText(html){const doc=new DOMParser().parseFromString(String(html||''),'text/html');return String(doc.body&&doc.body.textContent||'').replace(/\n{3,}/g,'\n\n').trim();}
  function importObjectDraft(type,title,content,summary,fileName,fingerprint,tags=[]){
    const obj=objectTemplate(OBJECT_TYPES.has(type)?type:'document',String(title||fileName||'Imported artifact').slice(0,160));
    obj.summary=String(summary||'Imported into Workspace for local review.').slice(0,1200); obj.content=String(content||'').slice(0,50000); obj.status='draft'; obj.tags=normalizeTags(['imported',...tags]);
    obj.provenance={sourceType:'imported',sourceTitle:String(fileName||'External import').slice(0,240),sourceUrl:'',capturedAt:nowIso()};
    obj._importFingerprint=fingerprint||''; return obj;
  }
  function stageInterchangePayload(payload,fileName,fingerprint){
    const objects=[]; const source=payload&&typeof payload==='object'?payload:{};
    const raws=Array.isArray(source.objects)?source.objects:(source.artifacts&&Array.isArray(source.artifacts)?source.artifacts:[]);
    raws.slice(0,MAX_INTEROP_IMPORT_OBJECTS).forEach(raw=>{const n=normalizeObject(raw);if(!n)return;const sourceObjectId=String(raw&&raw.id||'').slice(0,160);n.id=id('scwo');n.status='draft';n.tags=normalizeTags(['imported',...(n.tags||[])]);n.provenance={sourceType:'imported',sourceTitle:String(fileName||source.project&&source.project.title||'Interchange package').slice(0,240),sourceUrl:'',capturedAt:nowIso()};n.createdAt=nowIso();n.updatedAt=n.createdAt;n.archivedAt=null;n._importFingerprint=fingerprint||'';n._sourceObjectId=sourceObjectId;objects.push(n);});
    objects._relationships=(Array.isArray(source.relationships)?source.relationships:[]).map(r=>({relation:TRACE_RELATIONS.has(r&&r.relation)?r.relation:'derived-from',fromObjectId:String(r&&r.fromObjectId||'').slice(0,160),toObjectId:String(r&&r.toObjectId||'').slice(0,160),note:String(r&&r.note||'').slice(0,1000)})).filter(r=>r.fromObjectId&&r.toObjectId&&r.fromObjectId!==r.toObjectId).slice(0,MAX_LINEAGE_RELATIONS);
    return objects;
  }
  function stageExternalContent(format,text,fileName,fingerprint){
    const stem=String(fileName||'Imported file').replace(/\.[^.]+$/,'');
    if(format==='csv'||format==='tsv'){const rows=csvRows(text,format==='tsv'?'\t':',');const headers=rows[0]||[];const summary=`Imported ${format.toUpperCase()} dataset · ${Math.max(0,rows.length-1)} data row(s) · ${headers.length} column(s)${headers.length?` · ${headers.slice(0,8).join(', ')}`:''}`;return [importObjectDraft('dataset',stem,text,summary,fileName,fingerprint,[format])];}
    if(format==='markdown')return [importObjectDraft('document',stem,text,'Imported Markdown document.',fileName,fingerprint,['markdown'])];
    if(format==='html')return [importObjectDraft('document',stem,htmlToText(text),'Imported HTML document; text content preserved for local review.',fileName,fingerprint,['html'])];
    if(format==='text')return [importObjectDraft('document',stem,text,'Imported plain-text document.',fileName,fingerprint,['text'])];
    if(format==='json'){
      let payload; try{payload=JSON.parse(text);}catch(_){throw new Error('The selected JSON file is not valid JSON.');}
      if(payload&&['sc-workspace-interchange/1.0','sc-workspace-object-export/1.0'].includes(payload.schema)){
        const objs=payload.schema==='sc-workspace-object-export/1.0'?[payload.object]:stageInterchangePayload(payload,fileName,fingerprint);return payload.schema==='sc-workspace-object-export/1.0'?objs.map(raw=>{const n=normalizeObject(raw);n._sourceObjectId=String(raw&&raw.id||'').slice(0,160);n.id=id('scwo');n.status='draft';n.tags=normalizeTags(['imported',...(n.tags||[])]);n.provenance={sourceType:'imported',sourceTitle:fileName,sourceUrl:'',capturedAt:nowIso()};n._importFingerprint=fingerprint;return n;}):objs;
      }
      if(payload&&payload.project&&Array.isArray(payload.project.objects))return stageInterchangePayload({objects:payload.project.objects},fileName,fingerprint);
      const pretty=JSON.stringify(payload,null,2); const shape=Array.isArray(payload)?`${payload.length} top-level item(s)`:`${Object.keys(payload||{}).length} top-level field(s)`;return [importObjectDraft('dataset',stem,pretty,`Imported generic JSON dataset · ${shape}.`,fileName,fingerprint,['json'])];
    }
    throw new Error('Unsupported import format.');
  }
  function interchangePackage(project){
    const objectIds=new Set(project.objects.filter(o=>!o.archivedAt).map(o=>o.id));
    return {schema:INTERCHANGE_EXPORT_SCHEMA,workspaceVersion:rootVersion(),exportedAt:nowIso(),project:{id:project.id,title:project.title,description:project.description},objects:project.objects.filter(o=>!o.archivedAt).map(o=>JSON.parse(JSON.stringify(o))),relationships:(project.traceability&&Array.isArray(project.traceability.lineage)?project.traceability.lineage:[]).filter(r=>objectIds.has(r.fromObjectId)&&objectIds.has(r.toObjectId)).map(r=>({relation:r.relation,fromObjectId:r.fromObjectId,toObjectId:r.toObjectId,note:r.note||''})),boundary:{portableCopy:true,canonicalObjectOverwrite:false,serverUpload:false}};
  }

  function collaborationTemplate() {
    const stamp=nowIso();
    return {schema:COLLABORATION_SCHEMA,profile:{displayName:'',role:'owner'},sessions:[],activeSessionId:null,history:[],createdAt:stamp,updatedAt:stamp};
  }
  function normalizeCollabParticipant(raw){if(!raw||typeof raw!=='object')return null;return {id:String(raw.id||id('cp')).slice(0,160),displayName:String(raw.displayName||'Reviewer').trim().slice(0,120)||'Reviewer',role:COLLAB_ROLES.has(raw.role)?raw.role:'reviewer',origin:String(raw.origin||'local').slice(0,80),sourceThreadId:String(raw.sourceThreadId||'').slice(0,160),createdAt:validIso(raw.createdAt)?raw.createdAt:nowIso()};}
  function normalizeCollabThread(raw,objectIds){if(!raw||typeof raw!=='object')return null;const body=String(raw.body||'').trim().slice(0,5000);if(!body)return null;const oid=String(raw.objectId||'').slice(0,160);const status=COLLAB_THREAD_STATUS.has(raw.status)?raw.status:'open';return {id:String(raw.id||id('ct')).slice(0,160),kind:COLLAB_THREAD_KIND.has(raw.kind)?raw.kind:'comment',body,objectId:objectIds.has(oid)?oid:'',authorLabel:String(raw.authorLabel||'Reviewer').trim().slice(0,120)||'Reviewer',authorRole:COLLAB_ROLES.has(raw.authorRole)?raw.authorRole:'reviewer',status,origin:String(raw.origin||'local').slice(0,80),sourceThreadId:String(raw.sourceThreadId||'').slice(0,160),createdAt:validIso(raw.createdAt)?raw.createdAt:nowIso(),updatedAt:validIso(raw.updatedAt)?raw.updatedAt:nowIso(),resolvedAt:status==='resolved'&&validIso(raw.resolvedAt)?raw.resolvedAt:null};}
  function normalizeCollabSession(raw,projects){if(!raw||typeof raw!=='object')return null;const localProjectId=String(raw.localProjectId||raw.projectId||'').slice(0,160),sourceProjectId=String(raw.sourceProjectId||localProjectId).slice(0,160);const project=projects.find(p=>p.id===localProjectId);if(!project)return null;const objectIds=new Set(project.objects.map(o=>o.id));const participants=(Array.isArray(raw.participants)?raw.participants:[]).map(normalizeCollabParticipant).filter(Boolean).slice(0,MAX_COLLAB_PARTICIPANTS);const threads=(Array.isArray(raw.threads)?raw.threads:[]).map(v=>normalizeCollabThread(v,objectIds)).filter(Boolean).slice(0,MAX_COLLAB_THREADS);return {id:String(raw.id||id('cr')).slice(0,160),requestId:String(raw.requestId||raw.id||id('rrq')).slice(0,160),localProjectId,sourceProjectId,title:String(raw.title||'Workspace review').trim().slice(0,200)||'Workspace review',purpose:String(raw.purpose||'').slice(0,2400),status:COLLAB_SESSION_STATUS.has(raw.status)?raw.status:'draft',requestedRole:COLLAB_ROLES.has(raw.requestedRole)?raw.requestedRole:'reviewer',ownerLabel:String(raw.ownerLabel||'Workspace owner').trim().slice(0,120)||'Workspace owner',participants,threads,importedResponseCount:Math.max(0,Math.min(999,Number(raw.importedResponseCount)||0)),createdAt:validIso(raw.createdAt)?raw.createdAt:nowIso(),updatedAt:validIso(raw.updatedAt)?raw.updatedAt:nowIso(),closedAt:validIso(raw.closedAt)?raw.closedAt:null};}
  function normalizeCollaboration(raw,projects=[]){const base=collaborationTemplate(),v=raw&&typeof raw==='object'?raw:{};const prof=v.profile&&typeof v.profile==='object'?v.profile:{};base.profile={displayName:String(prof.displayName||'').trim().slice(0,120),role:COLLAB_ROLES.has(prof.role)?prof.role:'owner'};base.sessions=(Array.isArray(v.sessions)?v.sessions:[]).map(x=>normalizeCollabSession(x,projects)).filter(Boolean).slice(0,MAX_COLLAB_SESSIONS);base.activeSessionId=base.sessions.some(s=>s.id===v.activeSessionId)?String(v.activeSessionId):base.sessions[0]?.id||null;base.history=(Array.isArray(v.history)?v.history:[]).map(h=>({id:String(h&&h.id||id('ch')).slice(0,160),direction:h&&h.direction==='import'?'import':'export',kind:h&&h.kind==='response'?'response':'request',sessionId:String(h&&h.sessionId||'').slice(0,160),projectId:String(h&&h.projectId||'').slice(0,160),projectTitle:String(h&&h.projectTitle||'').slice(0,160),fileName:String(h&&h.fileName||'').slice(0,240),fingerprint:String(h&&h.fingerprint||'').slice(0,128),threadCount:Math.max(0,Math.min(MAX_COLLAB_THREADS,Number(h&&h.threadCount)||0)),at:validIso(h&&h.at)?h.at:nowIso()})).slice(0,MAX_COLLAB_HISTORY);base.createdAt=validIso(v.createdAt)?v.createdAt:base.createdAt;base.updatedAt=validIso(v.updatedAt)?v.updatedAt:base.updatedAt;return base;}
  function touchCollaboration(){state.collaboration=normalizeCollaboration(state.collaboration,state.projects);state.collaboration.updatedAt=nowIso();state.updatedAt=state.collaboration.updatedAt;}
  function activeCollaborationSession(){return state.collaboration?.sessions.find(s=>s.id===state.collaboration.activeSessionId)||null;}
  async function collaborationRequestPackage(session){const project=state.projects.find(p=>p.id===session.localProjectId&&!p.archivedAt);if(!project)throw new Error('Review project is unavailable.');const projectCopy=privacyMinimizedProject(project,{includeArchived:false,includeActivity:false,includeAi:false});const payload={schema:REVIEW_PACKAGE_SCHEMA,kind:'request',workspaceVersion:rootVersion(),createdAt:nowIso(),request:{id:session.requestId,sourceProjectId:session.sourceProjectId,title:session.title,purpose:session.purpose,requestedRole:session.requestedRole,ownerLabel:session.ownerLabel,participants:session.participants.map(p=>({displayName:p.displayName,role:p.role}))},project:projectCopy,threads:session.threads.map(t=>({...t}))};const canonical=JSON.stringify(payload);const fingerprint=await sha256Text(canonical);return {...payload,integrity:{algorithm:'SHA-256',payloadFingerprint:fingerprint||'',fingerprintAvailable:Boolean(fingerprint)}};}
  async function collaborationResponsePackage(session){const payload={schema:REVIEW_PACKAGE_SCHEMA,kind:'response',workspaceVersion:rootVersion(),createdAt:nowIso(),request:{id:session.requestId,sourceProjectId:session.sourceProjectId,title:session.title},responder:{displayName:state.collaboration.profile.displayName||'Reviewer',role:state.collaboration.profile.role},status:session.status,threads:session.threads.filter(t=>t.origin!=='request-package').map(t=>({...t,objectId:t.objectId||''}))};const canonical=JSON.stringify(payload);const fingerprint=await sha256Text(canonical);return {...payload,integrity:{algorithm:'SHA-256',payloadFingerprint:fingerprint||'',fingerprintAvailable:Boolean(fingerprint)}};}
  async function verifyReviewPackage(pkg){if(!pkg||pkg.schema!==REVIEW_PACKAGE_SCHEMA||!['request','response'].includes(pkg.kind)||!pkg.request)return {ok:false,verified:false,message:'Unsupported review package.'};const expected=String(pkg.integrity&&pkg.integrity.payloadFingerprint||'');if(!expected)return {ok:true,verified:false,message:'Review package has no fingerprint; inspect before committing.'};const clone=JSON.parse(JSON.stringify(pkg));delete clone.integrity;const actual=await sha256Text(JSON.stringify(clone));if(!actual)return {ok:true,verified:false,message:'This browser cannot verify the review fingerprint.'};return actual===expected?{ok:true,verified:true,message:'SHA-256 review package integrity verified.'}:{ok:false,verified:false,message:'Review package fingerprint does not match its contents.'};}

  function institutionalTemplate() {
    const stamp=nowIso();
    return {schema:INSTITUTIONAL_SCHEMA,handoffs:[],activeHandoffId:null,history:[],createdAt:stamp,updatedAt:stamp};
  }
  function normalizeInstitutionalHandoff(raw,projects=[]){
    if(!raw||typeof raw!=='object')return null;
    const projectId=String(raw.projectId||raw.sourceProjectId||'').slice(0,160),project=projects.find(p=>p.id===projectId);
    if(!project)return null;
    const validIds=new Set(project.objects.filter(o=>!o.archivedAt).map(o=>o.id));
    const objectIds=[...new Set((Array.isArray(raw.objectIds)?raw.objectIds:[]).map(v=>String(v).slice(0,160)).filter(v=>validIds.has(v)))].slice(0,MAX_OBJECTS);
    const stamp=nowIso(),status=INSTITUTIONAL_STATUS.has(raw.status)?raw.status:'draft';
    return {id:String(raw.id||id('ih')).slice(0,160),projectId,sourceProjectId:String(raw.sourceProjectId||projectId).slice(0,160),targetProduct:'catalyst-intelligence-platform',organizationLabel:String(raw.organizationLabel||'').trim().slice(0,200),purpose:String(raw.purpose||'').trim().slice(0,3000),status,objectIds,acknowledgements:{copyModel:Boolean(raw.acknowledgements?.copyModel),institutionalGovernance:Boolean(raw.acknowledgements?.institutionalGovernance),sharingReviewed:Boolean(raw.acknowledgements?.sharingReviewed)},packageFingerprint:String(raw.packageFingerprint||'').slice(0,128),externalRecordId:String(raw.externalRecordId||'').slice(0,240),receiptNote:String(raw.receiptNote||'').slice(0,3000),createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp,exportedAt:validIso(raw.exportedAt)?raw.exportedAt:null,receiptAt:validIso(raw.receiptAt)?raw.receiptAt:null,closedAt:validIso(raw.closedAt)?raw.closedAt:null};
  }
  function normalizeInstitutional(raw,projects=[]){
    const base=institutionalTemplate(),value=raw&&typeof raw==='object'?raw:{};
    base.handoffs=(Array.isArray(value.handoffs)?value.handoffs:[]).map(v=>normalizeInstitutionalHandoff(v,projects)).filter(Boolean).slice(0,MAX_INSTITUTIONAL_HANDOFFS);
    base.activeHandoffId=base.handoffs.some(h=>h.id===value.activeHandoffId)?String(value.activeHandoffId):base.handoffs[0]?.id||null;
    base.history=(Array.isArray(value.history)?value.history:[]).map(h=>({id:String(h&&h.id||id('ihh')).slice(0,160),direction:h&&h.direction==='import'?'import':'export',kind:h&&h.kind==='receipt'?'receipt':'promotion',handoffId:String(h&&h.handoffId||'').slice(0,160),projectId:String(h&&h.projectId||'').slice(0,160),projectTitle:String(h&&h.projectTitle||'').slice(0,160),organizationLabel:String(h&&h.organizationLabel||'').slice(0,200),fileName:String(h&&h.fileName||'').slice(0,240),fingerprint:String(h&&h.fingerprint||'').slice(0,128),status:INSTITUTIONAL_STATUS.has(h&&h.status)?h.status:'exported',objectCount:Math.max(0,Math.min(MAX_OBJECTS,Number(h&&h.objectCount)||0)),at:validIso(h&&h.at)?h.at:nowIso()})).slice(0,MAX_INSTITUTIONAL_HISTORY);
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt;base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt;return base;
  }
  function touchInstitutional(){state.institutional=normalizeInstitutional(state.institutional,state.projects);state.institutional.updatedAt=nowIso();state.updatedAt=state.institutional.updatedAt;}
  function activeInstitutionalHandoff(){return state.institutional?.handoffs.find(h=>h.id===state.institutional.activeHandoffId)||null;}
  function institutionalReadiness(project,objectIds){
    const selected=new Set(objectIds||[]),objects=project.objects.filter(o=>selected.has(o.id)&&!o.archivedAt);
    const provenanceTargets=objects.filter(o=>['source','evidence','dataset'].includes(o.type));
    const missingProvenance=provenanceTargets.filter(o=>!String(o.provenance?.sourceTitle||'').trim()&&!String(o.provenance?.sourceUrl||'').trim()&&o.provenance?.sourceType==='manual').length;
    const openQuestions=(project.research?.questions||[]).filter(q=>q.status==='open'&&q.priority==='high').length;
    const challenged=(project.analysis?.assumptions||[]).filter(a=>a.status==='challenged').length+(project.analysis?.findings||[]).filter(f=>f.status==='contested').length;
    const stale=(project.traceability?.reproducibility||[]).filter(r=>r.status==='stale').length;
    const openReview=(state.collaboration?.sessions||[]).filter(s=>s.localProjectId===project.id&&!['approved','closed'].includes(s.status)).reduce((n,s)=>n+(s.threads||[]).filter(t=>t.status==='open').length,0);
    const evaluating=(project.decision?.decisions||[]).filter(d=>['evaluating','revisit'].includes(d.status)).length;
    return [
      {key:'scope',label:'Promotion scope',status:objects.length?'ready':'attention',detail:objects.length?`${objects.length} canonical object${objects.length===1?'':'s'} selected.`:'No canonical objects selected.'},
      {key:'provenance',label:'Provenance coverage',status:missingProvenance?'attention':'ready',detail:missingProvenance?`${missingProvenance} selected source/evidence/dataset object${missingProvenance===1?'':'s'} lack recorded source provenance.`:'Selected source/evidence/dataset objects have recorded provenance.'},
      {key:'research',label:'Research closure',status:openQuestions?'attention':'ready',detail:openQuestions?`${openQuestions} high-priority research question${openQuestions===1?' remains':'s remain'} open.`:'No high-priority research questions remain open.'},
      {key:'analysis',label:'Analytical challenge',status:challenged?'attention':'ready',detail:challenged?`${challenged} challenged assumption or contested finding record${challenged===1?'':'s'} remain.`:'No challenged assumptions or contested findings are recorded.'},
      {key:'decision',label:'Decision state',status:evaluating?'attention':'ready',detail:evaluating?`${evaluating} decision record${evaluating===1?' is':'s are'} still evaluating or marked for revisit.`:'No decision record is currently evaluating or marked for revisit.'},
      {key:'repro',label:'Reproducibility',status:stale?'attention':'ready',detail:stale?`${stale} reproducibility record${stale===1?' is':'s are'} stale.`:'No stale reproducibility records are present.'},
      {key:'review',label:'Review closure',status:openReview?'attention':'ready',detail:openReview?`${openReview} open collaboration thread${openReview===1?' remains':'s remain'}.`:'No open collaboration review threads are attached to this project.'}
    ];
  }
  function institutionalProjectCopy(project,objectIds){
    const selected=new Set(objectIds||[]),clone=privacyMinimizedProject(project,{includeArchived:false,includeActivity:false,includeAi:false});
    clone.objects=clone.objects.filter(o=>selected.has(o.id));
    clone.activeObjectId=null;clone.recentTools=[];clone.activity=[];clone.handoffs=handoffLedgerTemplate();clone.aiAssistance=aiAssistanceTemplate();
    clone.research=normalizeResearch(clone.research,clone.objects);clone.analysis=normalizeAnalysis(clone.analysis,clone.objects);clone.decision=normalizeDecision(clone.decision,clone.objects);clone.canvas=normalizeCanvas(clone.canvas,clone.objects);clone.traceability=normalizeTraceability(clone.traceability,clone.objects);clone.briefing=normalizeBriefing(clone.briefing,clone.objects);clone.guidedWorkflows=normalizeGuidedWorkflows(clone.guidedWorkflows,clone.objects);
    return clone;
  }
  async function institutionalPromotionPackage(handoff){
    const project=state.projects.find(p=>p.id===handoff.projectId&&!p.archivedAt);if(!project)throw new Error('Institutional handoff project is unavailable.');
    const projectCopy=institutionalProjectCopy(project,handoff.objectIds),readiness=institutionalReadiness(project,handoff.objectIds);
    const manifest={schema:INSTITUTIONAL_PACKAGE_SCHEMA,workspaceVersion:rootVersion(),createdAt:nowIso(),handoffId:handoff.id,sourceProjectId:project.id,projectTitle:project.title,targetProduct:'catalyst-intelligence-platform',organizationLabel:handoff.organizationLabel,objectCount:projectCopy.objects.length,readiness,privacy:{deviceIdentityIncluded:false,accountIdentityIncluded:false,persistenceMetadataIncluded:false,connectedToolHandoffStateIncluded:false,recentToolsIncluded:false,activityHistoryIncluded:false,aiReviewHistoryIncluded:false,collaborationHistoryIncluded:false},governance:{sourceWorkspaceRetainsIndependentCopy:true,institutionalCopyCreated:true,institutionalGovernanceBeginsAfterAcceptance:true,automaticUpload:false,automaticSourceMutation:false}};
    const handoffMeta={id:handoff.id,sourceProjectId:project.id,targetProduct:'catalyst-intelligence-platform',organizationLabel:handoff.organizationLabel,purpose:handoff.purpose,requestedMode:'institutional-copy',createdAt:handoff.createdAt};
    const canonical=JSON.stringify({manifest,handoff:handoffMeta,project:projectCopy}),fingerprint=await sha256Text(canonical);
    return {schema:INSTITUTIONAL_PACKAGE_SCHEMA,kind:'promotion',manifest,handoff:handoffMeta,project:projectCopy,integrity:{algorithm:'SHA-256',payloadFingerprint:fingerprint||'',fingerprintAvailable:Boolean(fingerprint)}};
  }
  async function verifyInstitutionalReceipt(pkg){
    if(!pkg||pkg.schema!==INSTITUTIONAL_RECEIPT_SCHEMA||!pkg.handoffId||!pkg.sourceProjectId||pkg.targetProduct!=='catalyst-intelligence-platform'||!INSTITUTIONAL_RECEIPT_STATUS.has(pkg.status))return {ok:false,verified:false,message:'Unsupported institutional receipt.'};
    const expected=String(pkg.integrity?.payloadFingerprint||'');if(!expected)return {ok:true,verified:false,message:'Receipt has no fingerprint; inspect the institutional source before committing.'};
    const clone=JSON.parse(JSON.stringify(pkg));delete clone.integrity;const actual=await sha256Text(JSON.stringify(clone));if(!actual)return {ok:true,verified:false,message:'This browser cannot verify the receipt fingerprint.'};
    return actual===expected?{ok:true,verified:true,message:'SHA-256 institutional receipt integrity verified.'}:{ok:false,verified:false,message:'Institutional receipt fingerprint does not match its contents.'};
  }
  function ingestInstitutionalReceiptPacket(currentState,pkg,fileName='same-origin receipt'){
    if(!currentState||!pkg||pkg.schema!==INSTITUTIONAL_RECEIPT_SCHEMA)return {ok:false,message:'Unsupported institutional receipt.'};
    currentState.institutional=normalizeInstitutional(currentState.institutional,currentState.projects);
    const handoff=currentState.institutional.handoffs.find(h=>h.id===String(pkg.handoffId||'')&&h.sourceProjectId===String(pkg.sourceProjectId||'')&&pkg.targetProduct==='catalyst-intelligence-platform');
    if(!handoff)return {ok:false,message:'Receipt does not match a local institutional handoff.'};
    if(!INSTITUTIONAL_RECEIPT_STATUS.has(pkg.status))return {ok:false,message:'Receipt status is not supported.'};
    handoff.status=pkg.status;handoff.externalRecordId=String(pkg.externalRecordId||'').slice(0,240);handoff.receiptNote=String(pkg.note||'').slice(0,3000);handoff.receiptAt=validIso(pkg.receivedAt)?pkg.receivedAt:nowIso();handoff.updatedAt=nowIso();
    currentState.institutional.history.unshift({id:id('ihh'),direction:'import',kind:'receipt',handoffId:handoff.id,projectId:handoff.projectId,projectTitle:currentState.projects.find(p=>p.id===handoff.projectId)?.title||'',organizationLabel:handoff.organizationLabel,fileName:String(fileName).slice(0,240),fingerprint:String(pkg.integrity?.payloadFingerprint||'').slice(0,128),status:handoff.status,objectCount:handoff.objectIds.length,at:handoff.receiptAt});
    currentState.institutional.history=currentState.institutional.history.slice(0,MAX_INSTITUTIONAL_HISTORY);currentState.institutional.updatedAt=nowIso();
    const project=currentState.projects.find(p=>p.id===handoff.projectId);if(project)addActivity(project,'institutional-receipt',`Institutional handoff ${handoff.status}: ${handoff.organizationLabel||'Catalyst Intelligence'}`);
    return {ok:true,message:`Institutional receipt recorded: ${handoff.status}.`,handoffId:handoff.id,projectId:handoff.projectId};
  }

  function shareTemplate() {
    const stamp=nowIso();
    return {schema:SHARE_SCHEMA,history:[],createdAt:stamp,updatedAt:stamp};
  }
  function normalizeShare(raw){
    const base=shareTemplate(),value=raw&&typeof raw==='object'?raw:{};
    base.history=(Array.isArray(value.history)?value.history:[]).map(item=>({
      id:String(item&&item.id||id('sh')).slice(0,160),direction:item&&item.direction==='import'?'import':'export',kind:item&&item.kind==='review-html'?'review-html':'portable-project',projectId:String(item&&item.projectId||'').slice(0,160),projectTitle:String(item&&item.projectTitle||'').slice(0,160),fileName:String(item&&item.fileName||'').slice(0,240),fingerprint:String(item&&item.fingerprint||'').slice(0,128),objectCount:Math.max(0,Math.min(1000,Number(item&&item.objectCount)||0)),at:validIso(item&&item.at)?item.at:nowIso()
    })).slice(0,MAX_SHARE_HISTORY);
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt;base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt;return base;
  }
  function touchShare(){state.share=normalizeShare(state.share);state.share.updatedAt=nowIso();}
  function privacyMinimizedProject(project,options={}){
    const includeArchived=Boolean(options.includeArchived),includeActivity=Boolean(options.includeActivity),includeAi=Boolean(options.includeAi);
    const clone=JSON.parse(JSON.stringify(project));
    delete clone.persistence;delete clone.recentTools;delete clone.handoffs;clone.pinned=false;clone.archivedAt=null;clone.activeObjectId=null;
    clone.activity=includeActivity?clone.activity:[];
    clone.objects=(Array.isArray(clone.objects)?clone.objects:[]).filter(o=>includeArchived||!o.archivedAt);
    const ids=new Set(clone.objects.map(o=>o.id));
    if(!includeAi)clone.aiAssistance=aiAssistanceTemplate();
    else clone.aiAssistance=normalizeAiAssistance(clone.aiAssistance,clone.objects);
    // Re-normalize the content-bearing structures against the objects actually included.
    clone.research=normalizeResearch(clone.research,clone.objects);clone.analysis=normalizeAnalysis(clone.analysis,clone.objects);clone.decision=normalizeDecision(clone.decision,clone.objects);clone.canvas=normalizeCanvas(clone.canvas,clone.objects);clone.traceability=normalizeTraceability(clone.traceability,clone.objects);clone.briefing=normalizeBriefing(clone.briefing,clone.objects);clone.guidedWorkflows=normalizeGuidedWorkflows(clone.guidedWorkflows,clone.objects);
    clone.schema=PROJECT_SCHEMA;clone.updatedAt=nowIso();
    return clone;
  }
  function portableManifest(project,options,payload){return {schema:PORTABLE_PROJECT_SCHEMA,workspaceVersion:rootVersion(),createdAt:nowIso(),sourceProjectId:project.id,projectTitle:project.title,objectCount:payload.objects.length,privacy:{deviceIdentityIncluded:false,accountIdentityIncluded:false,persistenceMetadataIncluded:false,handoffStateIncluded:false,recentToolsIncluded:false,activityIncluded:Boolean(options.includeActivity),aiReviewHistoryIncluded:Boolean(options.includeAi),archivedObjectsIncluded:Boolean(options.includeArchived)},transport:{cloudUpload:false,publicShareLink:false,liveCollaboration:false,importMode:'copy'}};}
  async function portableProjectPackage(project,options={}){
    const payload=privacyMinimizedProject(project,options),manifest=portableManifest(project,options,payload),canonical=JSON.stringify({manifest,project:payload});const fingerprint=await sha256Text(canonical);
    return {schema:PORTABLE_PROJECT_SCHEMA,manifest,project:payload,integrity:{algorithm:'SHA-256',payloadFingerprint:fingerprint||'',fingerprintAvailable:Boolean(fingerprint)}};
  }
  async function verifyPortablePackage(pkg){
    if(!pkg||pkg.schema!==PORTABLE_PROJECT_SCHEMA||!pkg.manifest||!pkg.project)return {ok:false,message:'Unsupported portable project package.'};
    const expected=String(pkg.integrity&&pkg.integrity.payloadFingerprint||'');if(!expected)return {ok:true,verified:false,message:'Package has no browser-generated fingerprint; review before import.'};
    const actual=await sha256Text(JSON.stringify({manifest:pkg.manifest,project:pkg.project}));if(!actual)return {ok:true,verified:false,message:'This browser cannot verify the package fingerprint.'};
    return actual===expected?{ok:true,verified:true,message:'SHA-256 package integrity verified.'}:{ok:false,verified:false,message:'Package fingerprint does not match its contents.'};
  }
  function reviewCopyHtml(project){
    const objects=project.objects.filter(o=>!o.archivedAt),counts={};objects.forEach(o=>counts[o.type]=(counts[o.type]||0)+1);const rows=objects.map(o=>`<tr><td>${escapeHtml(OBJECT_LABELS[o.type]||o.type)}</td><td>${escapeHtml(o.title)}</td><td>${escapeHtml(o.summary||'')}</td><td>${escapeHtml(o.provenance?.sourceTitle||o.provenance?.sourceType||'')}</td></tr>`).join('');
    return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${escapeHtml(project.title)} — Workspace review copy</title><style>body{font-family:Arial,sans-serif;margin:0;color:#111}main{max-width:1080px;margin:auto;padding:48px 28px}header{border-top:12px solid #000;border-bottom:1px solid #bbb;padding:28px 0}.k{font-size:12px;letter-spacing:.12em;color:#8b0000;font-weight:700}h1{font-size:42px;margin:10px 0}p{line-height:1.55}table{width:100%;border-collapse:collapse;margin-top:28px}th,td{text-align:left;vertical-align:top;border-bottom:1px solid #ddd;padding:10px 8px}th{font-size:12px;letter-spacing:.08em;text-transform:uppercase}.note{margin-top:32px;padding:16px;border-top:3px solid #000;background:#f4f1eb}</style></head><body><main><header><div class="k">SUSTAINABLE CATALYST / WORKSPACE REVIEW COPY</div><h1>${escapeHtml(project.title)}</h1><p>${escapeHtml(project.description||'')}</p><p><strong>Status:</strong> ${escapeHtml(project.status)} · <strong>Objects:</strong> ${objects.length}</p></header><section><h2>Project objects</h2><table><thead><tr><th>Type</th><th>Title</th><th>Summary</th><th>Provenance</th></tr></thead><tbody>${rows}</tbody></table></section><div class="note"><strong>Static review copy.</strong> This file is not a live Workspace Project and cannot synchronize changes back to Sustainable Catalyst.</div></main></body></html>`;
  }
  function downloadText(filename,text,type='text/plain'){const blob=new Blob([text],{type});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=filename;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}

  function accountPersistenceTemplate() {
    return { schema: ACCOUNT_PERSISTENCE_SCHEMA, selectedProjectId: '', cloudRecords: [], history: [], lastRefreshAt: null, updatedAt: nowIso() };
  }

  function normalizeAccountPersistence(raw, projects) {
    const next = accountPersistenceTemplate();
    if (!raw || typeof raw !== 'object') return next;
    const ids = new Set(projects.map(p => p.id));
    next.selectedProjectId = ids.has(String(raw.selectedProjectId || '')) ? String(raw.selectedProjectId) : '';
    next.cloudRecords = (Array.isArray(raw.cloudRecords) ? raw.cloudRecords : []).map(item => ({
      projectId: String(item?.projectId || '').slice(0,160),
      title: String(item?.title || 'Workspace project').slice(0,200),
      clientUpdatedAt: validIso(item?.clientUpdatedAt) ? item.clientUpdatedAt : '',
      backedUpAt: validIso(item?.backedUpAt) ? item.backedUpAt : '',
      fingerprint: String(item?.fingerprint || '').slice(0,128),
      projectFingerprint: String(item?.projectFingerprint || '').slice(0,128),
      revision: Math.max(0, Number(item?.revision) || 0),
      storageMode: ['manual-backup','sync-head'].includes(item?.storageMode) ? item.storageMode : 'manual-backup',
      bytes: Math.max(0, Number(item?.bytes) || 0),
      objectCount: Math.max(0, Number(item?.objectCount) || 0),
    })).filter(item => item.projectId).slice(0,25);
    next.history = (Array.isArray(raw.history) ? raw.history : []).map(item => ({
      id: String(item?.id || id('aph')).slice(0,160),
      action: ['backup','restore','delete','refresh'].includes(item?.action) ? item.action : 'refresh',
      projectId: String(item?.projectId || '').slice(0,160),
      projectTitle: String(item?.projectTitle || '').slice(0,200),
      at: validIso(item?.at) ? item.at : nowIso(),
    })).slice(0, MAX_ACCOUNT_HISTORY);
    next.lastRefreshAt = validIso(raw.lastRefreshAt) ? raw.lastRefreshAt : null;
    next.updatedAt = validIso(raw.updatedAt) ? raw.updatedAt : nowIso();
    return next;
  }

  function crossDeviceSyncTemplate() {
    return { schema: CROSS_DEVICE_SYNC_SCHEMA, enrollments: [], history: [], updatedAt: nowIso() };
  }

  function normalizeCrossDeviceSync(raw, projects) {
    const next = crossDeviceSyncTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const projectIds = new Set(projects.map(project => project.id));
    next.enrollments = (Array.isArray(value.enrollments) ? value.enrollments : []).map(item => ({
      projectId: String(item?.projectId || '').slice(0,160),
      enabled: Boolean(item?.enabled),
      serverRevision: Math.max(0, Number(item?.serverRevision) || 0),
      lastSyncedFingerprint: String(item?.lastSyncedFingerprint || '').slice(0,128),
      remoteFingerprint: String(item?.remoteFingerprint || '').slice(0,128),
      remoteRevision: Math.max(0, Number(item?.remoteRevision) || 0),
      status: SYNC_STATUS.has(item?.status) ? item.status : 'disabled',
      lastCheckedAt: validIso(item?.lastCheckedAt) ? item.lastCheckedAt : null,
      lastSyncedAt: validIso(item?.lastSyncedAt) ? item.lastSyncedAt : null,
      updatedAt: validIso(item?.updatedAt) ? item.updatedAt : nowIso(),
    })).filter(item => item.projectId && projectIds.has(item.projectId)).slice(0, MAX_SYNC_ENROLLMENTS);
    next.history = (Array.isArray(value.history) ? value.history : []).map(item => ({
      id: String(item?.id || id('syh')).slice(0,160),
      action: ['enable','disable','check','push','pull','conflict','remote-copy','resolve-local','resolve-cloud','remote-missing'].includes(item?.action) ? item.action : 'check',
      projectId: String(item?.projectId || '').slice(0,160),
      projectTitle: String(item?.projectTitle || '').slice(0,200),
      revision: Math.max(0, Number(item?.revision) || 0),
      at: validIso(item?.at) ? item.at : nowIso(),
    })).slice(0, MAX_SYNC_HISTORY);
    next.updatedAt = validIso(value.updatedAt) ? value.updatedAt : nowIso();
    return next;
  }

  function versionHistoryTemplate() { return { schema: VERSION_HISTORY_SCHEMA, selectedProjectId: '', restorePoints: [], history: [], updatedAt: nowIso() }; }

  function normalizeVersionHistory(raw, projects) {
    const next=versionHistoryTemplate(), value=raw&&typeof raw==='object'?raw:{}, ids=new Set(projects.map(project=>project.id));
    next.selectedProjectId=ids.has(String(value.selectedProjectId||''))?String(value.selectedProjectId):'';
    next.restorePoints=(Array.isArray(value.restorePoints)?value.restorePoints:[]).map(item=>{if(!item||typeof item!=='object'||!item.snapshot||typeof item.snapshot!=='object')return null;const projectId=String(item.projectId||item.snapshot.id||'').slice(0,160);if(!projectId)return null;const snapshot=normalizeProject(item.snapshot);if(!snapshot)return null;snapshot.id=projectId;return {schema:RESTORE_POINT_SCHEMA,id:String(item.id||id('rpt')).slice(0,160),projectId,projectTitle:String(item.projectTitle||snapshot.title||'Workspace project').slice(0,200),label:String(item.label||'Restore point').slice(0,120),note:String(item.note||'').slice(0,1200),source:['manual','imported','sync-safety'].includes(item.source)?item.source:'manual',createdAt:validIso(item.createdAt)?item.createdAt:nowIso(),projectUpdatedAt:validIso(item.projectUpdatedAt)?item.projectUpdatedAt:snapshot.updatedAt,fingerprint:String(item.fingerprint||'').slice(0,128),bytes:Math.max(0,Number(item.bytes)||approximateBytes(snapshot)),snapshot};}).filter(Boolean).slice(0,MAX_RESTORE_POINTS);
    next.history=(Array.isArray(value.history)?value.history:[]).map(item=>({id:String(item?.id||id('vhh')).slice(0,160),action:['create','verify','restore-copy','export','delete'].includes(item?.action)?item.action:'create',restorePointId:String(item?.restorePointId||'').slice(0,160),projectId:String(item?.projectId||'').slice(0,160),projectTitle:String(item?.projectTitle||'').slice(0,200),label:String(item?.label||'').slice(0,120),at:validIso(item?.at)?item.at:nowIso()})).slice(0,MAX_VERSION_HISTORY_EVENTS);next.updatedAt=validIso(value.updatedAt)?value.updatedAt:nowIso();return next;
  }

  function safeActionsTemplate() { return { schema: SAFE_ACTIONS_SCHEMA, history: [], updatedAt: nowIso() }; }

  function normalizeSafeActions(raw, projects=[]) {
    const next=safeActionsTemplate(), value=raw&&typeof raw==='object'?raw:{}, projectIds=new Set(projects.map(project=>project.id));
    next.history=(Array.isArray(value.history)?value.history:[]).map(item=>{
      if(!item||typeof item!=='object')return null;
      const projectId=String(item.projectId||'').slice(0,160);
      return {schema:SAFE_ACTIONS_SCHEMA,id:String(item.id||id('sah')).slice(0,160),action:String(item.action||'').slice(0,80),actionLabel:String(item.actionLabel||'Safe action').slice(0,160),projectId,projectTitle:String(item.projectTitle||'Workspace project').slice(0,200),outcome:['proceeded','cancelled','blocked'].includes(item.outcome)?item.outcome:'blocked',reviewAvailable:Boolean(item.reviewAvailable),reviewSummary:{added:Math.max(0,Number(item.reviewSummary?.added)||0),removed:Math.max(0,Number(item.reviewSummary?.removed)||0),modified:Math.max(0,Number(item.reviewSummary?.modified)||0),total:Math.max(0,Number(item.reviewSummary?.total)||0),relationshipsChanged:Math.max(0,Number(item.reviewSummary?.relationshipsChanged)||0),categoriesChanged:Math.max(0,Number(item.reviewSummary?.categoriesChanged)||0)},baseline:item.baseline&&typeof item.baseline==='object'?{kind:String(item.baseline.kind||'none').slice(0,80),label:String(item.baseline.label||'No comparison baseline').slice(0,200),id:String(item.baseline.id||'').slice(0,160)}:{kind:'none',label:'No comparison baseline',id:''},target:item.target&&typeof item.target==='object'?{kind:String(item.target.kind||'current-project').slice(0,80),label:String(item.target.label||'Current project').slice(0,200),id:String(item.target.id||'').slice(0,160)}:{kind:'current-project',label:'Current project',id:''},checkpointRestorePointId:String(item.checkpointRestorePointId||'').slice(0,160),acknowledged:Boolean(item.acknowledged),at:validIso(item.at)?item.at:nowIso()};
    }).filter(Boolean).slice(0,MAX_SAFE_ACTION_HISTORY);
    next.updatedAt=validIso(value.updatedAt)?value.updatedAt:nowIso();
    return next;
  }

  function defaultState() {
    const stamp = nowIso();
    return { schemaVersion: STORAGE_VERSION, identity: identityTemplate(), accountPersistence: accountPersistenceTemplate(), crossDeviceSync: crossDeviceSyncTemplate(), versionHistory: versionHistoryTemplate(), safeActions: safeActionsTemplate(), activeProjectId: null, projects: [], recentTools: [], knowledge: knowledgeTemplate(), knowledgeGraph: knowledgeGraphTemplate(), activityIntelligence: activityIntelligenceTemplate(), interoperability: interoperabilityTemplate(), share: shareTemplate(), collaboration: collaborationTemplate(), institutional: institutionalTemplate(), createdAt: stamp, updatedAt: stamp };
  }

  function provenanceTemplate() {
    return { sourceType: 'manual', sourceTitle: '', sourceUrl: '', capturedAt: null };
  }

  function researchTemplate() {
    const stamp = nowIso();
    return {
      schema: RESEARCH_SCHEMA,
      questions: [],
      claims: [],
      readingQueue: [],
      evidenceLinks: [],
      activeQuestionId: null,
      activeClaimId: null,
      createdAt: stamp,
      updatedAt: stamp
    };
  }

  function normalizeResearchQuestion(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('rq')).slice(0, 160),
      text: String(raw.text || '').trim().slice(0, 1000),
      status: QUESTION_STATUS.has(raw.status) ? raw.status : 'open',
      priority: QUESTION_PRIORITY.has(raw.priority) ? raw.priority : 'normal',
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeResearchClaim(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('rc')).slice(0, 160),
      text: String(raw.text || '').trim().slice(0, 2000),
      status: CLAIM_STATUS.has(raw.status) ? raw.status : 'exploratory',
      evidenceObjectIds: Array.isArray(raw.evidenceObjectIds) ? [...new Set(raw.evidenceObjectIds.map((value) => String(value).slice(0, 160)))].slice(0, 50) : [],
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeReadingItem(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('rr')).slice(0, 160),
      objectId: String(raw.objectId || '').slice(0, 160),
      status: READING_STATUS.has(raw.status) ? raw.status : 'unread',
      note: String(raw.note || '').slice(0, 1000),
      addedAt: validIso(raw.addedAt) ? raw.addedAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeEvidenceLink(raw) {
    if (!raw || typeof raw !== 'object') return null;
    return {
      id: String(raw.id || id('rel')).slice(0, 160),
      evidenceObjectId: String(raw.evidenceObjectId || '').slice(0, 160),
      sourceObjectId: String(raw.sourceObjectId || '').slice(0, 160),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : nowIso()
    };
  }

  function normalizeResearch(raw, objects = []) {
    const base = researchTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const objectIds = new Set(objects.map((object) => object.id));
    base.questions = Array.isArray(value.questions) ? value.questions.map(normalizeResearchQuestion).filter((item) => item && item.text).slice(0, MAX_RESEARCH_QUESTIONS) : [];
    base.claims = Array.isArray(value.claims) ? value.claims.map(normalizeResearchClaim).filter((item) => item && item.text).slice(0, MAX_RESEARCH_CLAIMS) : [];
    base.claims.forEach((claim) => { claim.evidenceObjectIds = claim.evidenceObjectIds.filter((objectId) => objectIds.has(objectId)); });
    base.readingQueue = Array.isArray(value.readingQueue) ? value.readingQueue.map(normalizeReadingItem).filter((item) => item && objectIds.has(item.objectId)).slice(0, MAX_READING_QUEUE) : [];
    base.evidenceLinks = Array.isArray(value.evidenceLinks) ? value.evidenceLinks.map(normalizeEvidenceLink).filter((link) => link && objectIds.has(link.evidenceObjectId) && objectIds.has(link.sourceObjectId)).slice(0, MAX_EVIDENCE_LINKS) : [];
    base.activeQuestionId = base.questions.some((item) => item.id === value.activeQuestionId) ? value.activeQuestionId : null;
    base.activeClaimId = base.claims.some((item) => item.id === value.activeClaimId) ? value.activeClaimId : null;
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchResearch(project) {
    if (!project.research) project.research = researchTemplate();
    project.research.updatedAt = nowIso();
    project.updatedAt = project.research.updatedAt;
  }

  function cleanResearchReferences(project, objectId) {
    if (!project || !project.research) return;
    project.research.readingQueue = project.research.readingQueue.filter((item) => item.objectId !== objectId);
    project.research.evidenceLinks = project.research.evidenceLinks.filter((link) => link.evidenceObjectId !== objectId && link.sourceObjectId !== objectId);
    project.research.claims.forEach((claim) => { claim.evidenceObjectIds = claim.evidenceObjectIds.filter((idValue) => idValue !== objectId); });
    touchResearch(project);
  }




  function analysisTemplate() {
    const stamp = nowIso();
    return {
      schema: ANALYSIS_SCHEMA,
      questions: [], variables: [], assumptions: [], methods: [], comparisons: [], findings: [],
      activeQuestionId: null, activeMethodId: null,
      createdAt: stamp, updatedAt: stamp
    };
  }

  function normalizeAnalysisQuestion(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('aq')).slice(0,160), text: String(raw.text || '').trim().slice(0,1200), status: ANALYSIS_QUESTION_STATUS.has(raw.status) ? raw.status : 'open', priority: QUESTION_PRIORITY.has(raw.priority) ? raw.priority : 'normal', createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysisVariable(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('av')).slice(0,160), name: String(raw.name || '').trim().slice(0,160), role: ANALYSIS_VARIABLE_ROLE.has(raw.role) ? raw.role : 'indicator', unit: String(raw.unit || '').slice(0,80), definition: String(raw.definition || '').slice(0,1200), createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysisAssumption(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('aa')).slice(0,160), text: String(raw.text || '').trim().slice(0,2000), status: ANALYSIS_ASSUMPTION_STATUS.has(raw.status) ? raw.status : 'untested', evidenceObjectIds: Array.isArray(raw.evidenceObjectIds) ? [...new Set(raw.evidenceObjectIds.map((v)=>String(v).slice(0,160)))].slice(0,50) : [], createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysisMethod(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('am')).slice(0,160), name: String(raw.name || '').trim().slice(0,200), type: ANALYSIS_METHOD_TYPE.has(raw.type) ? raw.type : 'descriptive', description: String(raw.description || '').slice(0,3000), datasetObjectIds: Array.isArray(raw.datasetObjectIds) ? [...new Set(raw.datasetObjectIds.map((v)=>String(v).slice(0,160)))].slice(0,25) : [], analysisObjectId: String(raw.analysisObjectId || '').slice(0,160), createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysisComparison(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('ac')).slice(0,160), label: String(raw.label || '').trim().slice(0,200), baseline: String(raw.baseline || '').slice(0,800), alternative: String(raw.alternative || '').slice(0,800), metric: String(raw.metric || '').slice(0,240), result: String(raw.result || '').slice(0,1200), interpretation: String(raw.interpretation || '').slice(0,2000), createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysisFinding(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return { id: String(raw.id || id('af')).slice(0,160), text: String(raw.text || '').trim().slice(0,3000), status: ANALYSIS_FINDING_STATUS.has(raw.status) ? raw.status : 'preliminary', evidenceObjectIds: Array.isArray(raw.evidenceObjectIds) ? [...new Set(raw.evidenceObjectIds.map((v)=>String(v).slice(0,160)))].slice(0,50) : [], analysisObjectId: String(raw.analysisObjectId || '').slice(0,160), createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp, updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp };
  }

  function normalizeAnalysis(raw, objects = []) {
    const base = analysisTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const objectIds = new Set(objects.map((object)=>object.id));
    const datasetIds = new Set(objects.filter((object)=>object.type === 'dataset').map((object)=>object.id));
    const evidenceIds = new Set(objects.filter((object)=>object.type === 'evidence').map((object)=>object.id));
    const analysisIds = new Set(objects.filter((object)=>object.type === 'analysis').map((object)=>object.id));
    base.questions = Array.isArray(value.questions) ? value.questions.map(normalizeAnalysisQuestion).filter((x)=>x && x.text).slice(0,MAX_ANALYSIS_QUESTIONS) : [];
    base.variables = Array.isArray(value.variables) ? value.variables.map(normalizeAnalysisVariable).filter((x)=>x && x.name).slice(0,MAX_ANALYSIS_VARIABLES) : [];
    base.assumptions = Array.isArray(value.assumptions) ? value.assumptions.map(normalizeAnalysisAssumption).filter((x)=>x && x.text).slice(0,MAX_ANALYSIS_ASSUMPTIONS) : [];
    base.assumptions.forEach((x)=>{ x.evidenceObjectIds = x.evidenceObjectIds.filter((v)=>evidenceIds.has(v)); });
    base.methods = Array.isArray(value.methods) ? value.methods.map(normalizeAnalysisMethod).filter((x)=>x && x.name).slice(0,MAX_ANALYSIS_METHODS) : [];
    base.methods.forEach((x)=>{ x.datasetObjectIds = x.datasetObjectIds.filter((v)=>datasetIds.has(v)); x.analysisObjectId = analysisIds.has(x.analysisObjectId) ? x.analysisObjectId : ''; });
    base.comparisons = Array.isArray(value.comparisons) ? value.comparisons.map(normalizeAnalysisComparison).filter((x)=>x && x.label).slice(0,MAX_ANALYSIS_COMPARISONS) : [];
    base.findings = Array.isArray(value.findings) ? value.findings.map(normalizeAnalysisFinding).filter((x)=>x && x.text).slice(0,MAX_ANALYSIS_FINDINGS) : [];
    base.findings.forEach((x)=>{ x.evidenceObjectIds = x.evidenceObjectIds.filter((v)=>evidenceIds.has(v)); x.analysisObjectId = analysisIds.has(x.analysisObjectId) ? x.analysisObjectId : ''; });
    base.activeQuestionId = base.questions.some((x)=>x.id===value.activeQuestionId) ? value.activeQuestionId : null;
    base.activeMethodId = base.methods.some((x)=>x.id===value.activeMethodId) ? value.activeMethodId : null;
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchAnalysis(project) {
    if (!project.analysis) project.analysis = analysisTemplate();
    project.analysis.updatedAt = nowIso();
    project.updatedAt = project.analysis.updatedAt;
  }

  function cleanAnalysisReferences(project, objectId) {
    if (!project || !project.analysis) return;
    project.analysis.assumptions.forEach((x)=>{ x.evidenceObjectIds = x.evidenceObjectIds.filter((v)=>v!==objectId); });
    project.analysis.methods.forEach((x)=>{ x.datasetObjectIds = x.datasetObjectIds.filter((v)=>v!==objectId); if (x.analysisObjectId===objectId) x.analysisObjectId=''; });
    project.analysis.findings.forEach((x)=>{ x.evidenceObjectIds = x.evidenceObjectIds.filter((v)=>v!==objectId); if (x.analysisObjectId===objectId) x.analysisObjectId=''; });
    touchAnalysis(project);
  }


  function decisionTemplate() {
    const stamp = nowIso();
    return { schema: DECISION_SCHEMA, decisions: [], options: [], criteria: [], assessments: [], risks: [], activeDecisionId: null, createdAt: stamp, updatedAt: stamp };
  }

  function normalizeDecisionRecord(raw) {
    if (!raw || typeof raw !== 'object') return null; const stamp=nowIso();
    return { id:String(raw.id||id('dr')).slice(0,160), title:String(raw.title||'').trim().slice(0,200), question:String(raw.question||'').trim().slice(0,2000), status:DECISION_STATUS.has(raw.status)?raw.status:'framing', decisionObjectId:String(raw.decisionObjectId||'').slice(0,160), selectedOptionId:String(raw.selectedOptionId||'').slice(0,160), rationale:String(raw.rationale||'').slice(0,6000), confidence:DECISION_CONFIDENCE.has(raw.confidence)?raw.confidence:'medium', createdAt:validIso(raw.createdAt)?raw.createdAt:stamp, updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp, decidedAt:validIso(raw.decidedAt)?raw.decidedAt:null };
  }
  function normalizeDecisionOption(raw) { if(!raw||typeof raw!=='object')return null; const stamp=nowIso(); return {id:String(raw.id||id('do')).slice(0,160),decisionId:String(raw.decisionId||'').slice(0,160),label:String(raw.label||'').trim().slice(0,200),description:String(raw.description||'').slice(0,2400),status:DECISION_OPTION_STATUS.has(raw.status)?raw.status:'candidate',evidenceObjectIds:Array.isArray(raw.evidenceObjectIds)?[...new Set(raw.evidenceObjectIds.map(v=>String(v).slice(0,160)))].slice(0,50):[],analysisObjectIds:Array.isArray(raw.analysisObjectIds)?[...new Set(raw.analysisObjectIds.map(v=>String(v).slice(0,160)))].slice(0,50):[],createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp}; }
  function normalizeDecisionCriterion(raw) { if(!raw||typeof raw!=='object')return null; const stamp=nowIso(); return {id:String(raw.id||id('dc')).slice(0,160),decisionId:String(raw.decisionId||'').slice(0,160),label:String(raw.label||'').trim().slice(0,200),weight:Math.max(0,Math.min(100,Number(raw.weight)||0)),description:String(raw.description||'').slice(0,1200),createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp}; }
  function normalizeDecisionAssessment(raw) { if(!raw||typeof raw!=='object')return null; const stamp=nowIso(); return {id:String(raw.id||id('da')).slice(0,160),decisionId:String(raw.decisionId||'').slice(0,160),optionId:String(raw.optionId||'').slice(0,160),criterionId:String(raw.criterionId||'').slice(0,160),score:Math.max(-5,Math.min(5,Number(raw.score)||0)),note:String(raw.note||'').slice(0,1200),createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp}; }
  function normalizeDecisionRisk(raw) { if(!raw||typeof raw!=='object')return null; const stamp=nowIso(); return {id:String(raw.id||id('dk')).slice(0,160),decisionId:String(raw.decisionId||'').slice(0,160),optionId:String(raw.optionId||'').slice(0,160),risk:String(raw.risk||'').trim().slice(0,2400),likelihood:DECISION_RISK_LEVEL.has(raw.likelihood)?raw.likelihood:'medium',impact:DECISION_RISK_LEVEL.has(raw.impact)?raw.impact:'medium',mitigation:String(raw.mitigation||'').slice(0,2000),createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp}; }
  function normalizeDecision(raw, objects=[]) {
    const base=decisionTemplate(), value=raw&&typeof raw==='object'?raw:{}; const objectIds=new Set(objects.map(o=>o.id)); const evidenceIds=new Set(objects.filter(o=>o.type==='evidence').map(o=>o.id)); const analysisIds=new Set(objects.filter(o=>o.type==='analysis').map(o=>o.id)); const decisionObjectIds=new Set(objects.filter(o=>o.type==='decision').map(o=>o.id));
    base.decisions=Array.isArray(value.decisions)?value.decisions.map(normalizeDecisionRecord).filter(x=>x&&x.title&&x.question).slice(0,MAX_DECISIONS):[]; const decisionIds=new Set(base.decisions.map(x=>x.id));
    base.options=Array.isArray(value.options)?value.options.map(normalizeDecisionOption).filter(x=>x&&decisionIds.has(x.decisionId)&&x.label).slice(0,MAX_DECISION_OPTIONS):[]; const optionIds=new Set(base.options.map(x=>x.id)); base.options.forEach(x=>{x.evidenceObjectIds=x.evidenceObjectIds.filter(v=>evidenceIds.has(v));x.analysisObjectIds=x.analysisObjectIds.filter(v=>analysisIds.has(v));});
    base.criteria=Array.isArray(value.criteria)?value.criteria.map(normalizeDecisionCriterion).filter(x=>x&&decisionIds.has(x.decisionId)&&x.label).slice(0,MAX_DECISION_CRITERIA):[]; const criterionIds=new Set(base.criteria.map(x=>x.id));
    base.assessments=Array.isArray(value.assessments)?value.assessments.map(normalizeDecisionAssessment).filter(x=>x&&decisionIds.has(x.decisionId)&&optionIds.has(x.optionId)&&criterionIds.has(x.criterionId)).slice(0,MAX_DECISION_ASSESSMENTS):[];
    base.risks=Array.isArray(value.risks)?value.risks.map(normalizeDecisionRisk).filter(x=>x&&decisionIds.has(x.decisionId)&&x.risk&&(!x.optionId||optionIds.has(x.optionId))).slice(0,MAX_DECISION_RISKS):[];
    base.decisions.forEach(x=>{x.decisionObjectId=decisionObjectIds.has(x.decisionObjectId)?x.decisionObjectId:'';x.selectedOptionId=optionIds.has(x.selectedOptionId)?x.selectedOptionId:'';});
    base.activeDecisionId=decisionIds.has(value.activeDecisionId)?value.activeDecisionId:null; base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt; base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt; return base;
  }
  function touchDecision(project){ if(!project.decision)project.decision=decisionTemplate(); project.decision.updatedAt=nowIso(); project.updatedAt=project.decision.updatedAt; }
  function cleanDecisionReferences(project, objectId){ if(!project||!project.decision)return; project.decision.options.forEach(x=>{x.evidenceObjectIds=x.evidenceObjectIds.filter(v=>v!==objectId);x.analysisObjectIds=x.analysisObjectIds.filter(v=>v!==objectId);}); project.decision.decisions.forEach(x=>{if(x.decisionObjectId===objectId)x.decisionObjectId='';}); touchDecision(project); }

  function canvasTemplate() {
    const stamp = nowIso();
    return { schema: CANVAS_SCHEMA, boards: [], nodes: [], edges: [], frames: [], activeBoardId: null, createdAt: stamp, updatedAt: stamp };
  }

  function normalizeCanvasBoard(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('cb')).slice(0, 160),
      title: String(raw.title || '').trim().slice(0, 200),
      description: String(raw.description || '').slice(0, 2400),
      status: CANVAS_BOARD_STATUS.has(raw.status) ? raw.status : 'draft',
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeCanvasNode(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('cn')).slice(0, 160),
      boardId: String(raw.boardId || '').slice(0, 160),
      type: CANVAS_NODE_TYPE.has(raw.type) ? raw.type : 'note',
      title: String(raw.title || '').trim().slice(0, 240),
      body: String(raw.body || '').slice(0, 4000),
      objectId: String(raw.objectId || '').slice(0, 160),
      x: Math.max(0, Math.min(820, Number(raw.x) || 24)),
      y: Math.max(0, Math.min(420, Number(raw.y) || 24)),
      tags: normalizeTags(raw.tags),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeCanvasEdge(raw) {
    if (!raw || typeof raw !== 'object') return null;
    return {
      id: String(raw.id || id('ce')).slice(0, 160),
      boardId: String(raw.boardId || '').slice(0, 160),
      fromNodeId: String(raw.fromNodeId || '').slice(0, 160),
      toNodeId: String(raw.toNodeId || '').slice(0, 160),
      relation: CANVAS_RELATION_TYPE.has(raw.relation) ? raw.relation : 'relates-to',
      label: String(raw.label || '').slice(0, 240),
      createdAt: validIso(raw.createdAt) ? raw.createdAt : nowIso()
    };
  }

  function normalizeCanvasFrame(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    return {
      id: String(raw.id || id('cf')).slice(0, 160),
      boardId: String(raw.boardId || '').slice(0, 160),
      title: String(raw.title || '').trim().slice(0, 200),
      description: String(raw.description || '').slice(0, 1600),
      nodeIds: Array.isArray(raw.nodeIds) ? [...new Set(raw.nodeIds.map((value) => String(value).slice(0, 160)))].slice(0, 100) : [],
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      updatedAt: validIso(raw.updatedAt) ? raw.updatedAt : stamp
    };
  }

  function normalizeCanvas(raw, objects = []) {
    const base = canvasTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const objectIds = new Set(objects.map((object) => object.id));
    base.boards = Array.isArray(value.boards) ? value.boards.map(normalizeCanvasBoard).filter((board) => board && board.title).slice(0, MAX_CANVAS_BOARDS) : [];
    const boardIds = new Set(base.boards.map((board) => board.id));
    base.nodes = Array.isArray(value.nodes) ? value.nodes.map(normalizeCanvasNode).filter((node) => node && node.title && boardIds.has(node.boardId)).slice(0, MAX_CANVAS_NODES) : [];
    base.nodes.forEach((node) => { if (node.objectId && !objectIds.has(node.objectId)) node.objectId = ''; });
    const nodeIds = new Set(base.nodes.map((node) => node.id));
    base.edges = Array.isArray(value.edges) ? value.edges.map(normalizeCanvasEdge).filter((edge) => edge && boardIds.has(edge.boardId) && nodeIds.has(edge.fromNodeId) && nodeIds.has(edge.toNodeId) && edge.fromNodeId !== edge.toNodeId).slice(0, MAX_CANVAS_EDGES) : [];
    base.frames = Array.isArray(value.frames) ? value.frames.map(normalizeCanvasFrame).filter((frame) => frame && frame.title && boardIds.has(frame.boardId)).slice(0, MAX_CANVAS_FRAMES) : [];
    base.frames.forEach((frame) => { frame.nodeIds = frame.nodeIds.filter((nodeId) => nodeIds.has(nodeId)); });
    base.activeBoardId = boardIds.has(value.activeBoardId) ? value.activeBoardId : (base.boards[0] ? base.boards[0].id : null);
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchCanvas(project) {
    if (!project.canvas) project.canvas = canvasTemplate();
    project.canvas.updatedAt = nowIso();
    project.updatedAt = project.canvas.updatedAt;
  }

  function cleanCanvasReferences(project, objectId) {
    if (!project || !project.canvas) return;
    project.canvas.nodes.forEach((node) => { if (node.objectId === objectId) node.objectId = ''; });
    touchCanvas(project);
  }

  function removeCanvasNode(project, nodeId) {
    if (!project || !project.canvas) return;
    project.canvas.nodes = project.canvas.nodes.filter((node) => node.id !== nodeId);
    project.canvas.edges = project.canvas.edges.filter((edge) => edge.fromNodeId !== nodeId && edge.toNodeId !== nodeId);
    project.canvas.frames.forEach((frame) => { frame.nodeIds = frame.nodeIds.filter((idValue) => idValue !== nodeId); });
    touchCanvas(project);
  }

  function normalizeDestinationKey(value) {
    const key=String(value || '').trim().toLowerCase();
    return RETURN_ADAPTER_ALIASES[key] || (HANDOFF_DESTINATIONS.has(key) ? key : '');
  }

  function processedReturnIds() {
    try { const raw=JSON.parse(window.sessionStorage.getItem(PROCESSED_RETURN_KEY) || '[]'); return Array.isArray(raw) ? raw.map(String).slice(0,100) : []; } catch (_) { return []; }
  }

  function returnAlreadyProcessed(returnId) { return Boolean(returnId && processedReturnIds().includes(String(returnId))); }

  function markReturnProcessed(returnId) {
    if (!returnId) return;
    try { const ids=[String(returnId), ...processedReturnIds().filter((item)=>item!==String(returnId))].slice(0,100); window.sessionStorage.setItem(PROCESSED_RETURN_KEY, JSON.stringify(ids)); } catch (_) {}
  }

  function adaptReturnPacket(payload) {
    if (!payload || typeof payload !== 'object') return { ok:false, message:'Return payload is not an object.' };
    let source=payload;
    if (payload.type === 'sc-workspace-return' && payload.payload && typeof payload.payload === 'object') source=payload.payload;
    const isCanonical=source.schema === HANDOFF_RETURN_SCHEMA;
    const isAdapter=source.schema === RETURN_ADAPTER_SCHEMA;
    if (!isCanonical && !isAdapter) return { ok:false, message:'Unsupported handoff return or adapter schema.' };
    const destination=normalizeDestinationKey(source.destination || source.source || source.tool || '');
    const artifactsRaw=Array.isArray(source.artifacts) ? source.artifacts : (Array.isArray(source.outputs) ? source.outputs : (Array.isArray(source.results) ? source.results : (source.artifact ? [source.artifact] : [])));
    const packet={
      schema: HANDOFF_RETURN_SCHEMA,
      returnId: String(source.returnId || source.receiptId || '').slice(0,160),
      handoffId: String(source.handoffId || source.handoff_id || '').slice(0,160),
      projectId: String(source.projectId || source.project_id || '').slice(0,160),
      destination,
      destinationLabel: String(source.destinationLabel || (destination && RETURN_ADAPTERS[destination] ? RETURN_ADAPTERS[destination].label : source.source || source.tool || '')).slice(0,120),
      intent: HANDOFF_INTENT.has(source.intent) ? source.intent : (destination ? handoffIntent(destination) : 'general'),
      createdAt: validIso(source.createdAt) ? source.createdAt : null,
      returnedAt: validIso(source.returnedAt) ? source.returnedAt : nowIso(),
      artifacts: artifactsRaw.map(normalizeReturnArtifact).filter(Boolean).slice(0,MAX_RETURN_ARTIFACTS)
    };
    return { ok:true, packet, adapter:isAdapter, sourceSchema:source.schema };
  }

  function handoffLedgerTemplate() {
    const stamp = nowIso();
    return { schema: HANDOFF_LEDGER_SCHEMA, entries: [], activeHandoffId: null, createdAt: stamp, updatedAt: stamp };
  }

  function normalizeHandoffEntry(raw, projectObjectIds = new Set(), canvasBoardIds = new Set()) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    const status = HANDOFF_STATUS.has(raw.status) ? raw.status : 'launched';
    const objectIds = Array.isArray(raw.objectIds) ? [...new Set(raw.objectIds.map((value) => String(value).slice(0,160)).filter((value) => projectObjectIds.has(value)))].slice(0,MAX_HANDOFF_OBJECT_REFS) : [];
    const returned = Array.isArray(raw.returnObjectIds) ? [...new Set(raw.returnObjectIds.map((value) => String(value).slice(0,160)).filter((value) => projectObjectIds.has(value)))].slice(0,MAX_RETURN_ARTIFACTS) : [];
    return {
      id: String(raw.id || id('sch')).slice(0,160),
      destination: normalizeDestinationKey(raw.destination) || 'lab',
      destinationLabel: String(raw.destinationLabel || raw.destination || 'Tool').slice(0,120),
      intent: HANDOFF_INTENT.has(raw.intent) ? raw.intent : 'general',
      objectIds,
      canvasBoardId: canvasBoardIds.has(String(raw.canvasBoardId || '')) ? String(raw.canvasBoardId) : '',
      status,
      createdAt: validIso(raw.createdAt) ? raw.createdAt : stamp,
      launchedAt: validIso(raw.launchedAt) ? raw.launchedAt : (status === 'prepared' ? null : stamp),
      returnedAt: validIso(raw.returnedAt) ? raw.returnedAt : null,
      closedAt: validIso(raw.closedAt) ? raw.closedAt : null,
      returnObjectIds: returned,
      note: String(raw.note || '').slice(0,1000)
    };
  }

  function normalizeHandoffs(raw, objects = [], canvas = null) {
    const base = handoffLedgerTemplate();
    const value = raw && typeof raw === 'object' ? raw : {};
    const objectIds = new Set(objects.map((object) => object.id));
    const boardIds = new Set(canvas && Array.isArray(canvas.boards) ? canvas.boards.map((board) => board.id) : []);
    base.entries = Array.isArray(value.entries) ? value.entries.map((entry) => normalizeHandoffEntry(entry, objectIds, boardIds)).filter(Boolean).slice(0,MAX_HANDOFFS) : [];
    base.activeHandoffId = base.entries.some((entry) => entry.id === value.activeHandoffId) ? value.activeHandoffId : null;
    base.createdAt = validIso(value.createdAt) ? value.createdAt : base.createdAt;
    base.updatedAt = validIso(value.updatedAt) ? value.updatedAt : base.updatedAt;
    return base;
  }

  function touchHandoffs(project) {
    if (!project.handoffs) project.handoffs = handoffLedgerTemplate();
    project.handoffs.updatedAt = nowIso();
    project.updatedAt = project.handoffs.updatedAt;
  }

  function cleanHandoffReferences(project, objectId) {
    if (!project || !project.handoffs) return;
    project.handoffs.entries.forEach((entry) => {
      entry.objectIds = entry.objectIds.filter((idValue) => idValue !== objectId);
      entry.returnObjectIds = entry.returnObjectIds.filter((idValue) => idValue !== objectId);
    });
    touchHandoffs(project);
  }

  function handoffIntent(toolKey) { return HANDOFF_INTENT_BY_TOOL[toolKey] || 'general'; }

  function createHandoff(project, destination, destinationLabel, object, canvasBoardId = '') {
    destination = normalizeDestinationKey(destination) || 'lab';
    if (!project.handoffs) project.handoffs = handoffLedgerTemplate();
    const stamp = nowIso();
    const entry = {
      id: id('sch'), destination, destinationLabel: String(destinationLabel || destination).slice(0,120), intent: handoffIntent(destination),
      objectIds: object ? [object.id] : [], canvasBoardId: String(canvasBoardId || '').slice(0,160), status: 'launched',
      createdAt: stamp, launchedAt: stamp, returnedAt: null, closedAt: null, returnObjectIds: [], note: ''
    };
    project.handoffs.entries.unshift(entry);
    project.handoffs.entries = project.handoffs.entries.slice(0,MAX_HANDOFFS);
    project.handoffs.activeHandoffId = entry.id;
    touchHandoffs(project);
    return entry;
  }

  function normalizeReturnArtifact(raw) {
    if (!raw || typeof raw !== 'object') return null;
    const type = OBJECT_TYPES.has(raw.type) ? raw.type : 'document';
    const title = String(raw.title || 'Returned artifact').trim().slice(0,160) || 'Returned artifact';
    return { type, title, summary: String(raw.summary || '').slice(0,1200), content: String(raw.content || '').slice(0,50000), tags: normalizeTags(raw.tags), status: OBJECT_STATUS.has(raw.status) ? raw.status : 'ready', sourceTitle: String(raw.sourceTitle || '').slice(0,240), sourceUrl: String(raw.sourceUrl || '').slice(0,2000) };
  }

  function ingestReturnPacket(state, payload, options = {}) {
    const adapted=adaptReturnPacket(payload);
    if (!adapted.ok) return adapted;
    const packet=adapted.packet;
    const automatic=options.mode === 'automatic';
    const allowUnmatched=Boolean(options.allowUnmatched) && !automatic;
    if (packet.returnId && returnAlreadyProcessed(packet.returnId)) return { ok:false, duplicate:true, message:'This handoff return was already processed in this browser session.' };
    const project = state.projects.find((item) => item.id === packet.projectId && !item.archivedAt);
    if (!project) return { ok:false, message:'The return package does not match an available Workspace Project on this device.' };
    if (!project.handoffs) project.handoffs = handoffLedgerTemplate();
    let entry = project.handoffs.entries.find((item) => item.id === packet.handoffId);
    if (automatic && !entry) return { ok:false, message:'Automatic return rejected because the handoff ID is not recorded in this local project.' };
    if (entry && packet.destination && entry.destination !== packet.destination) return { ok:false, message:'Return destination does not match the originating Workspace handoff.' };
    if (!entry && !allowUnmatched) return { ok:false, message:'The return package does not match a recorded Workspace handoff.' };
    if (!entry) {
      const destination=packet.destination || 'lab';
      entry = { id:packet.handoffId || id('sch'), destination, destinationLabel:packet.destinationLabel || (RETURN_ADAPTERS[destination] ? RETURN_ADAPTERS[destination].label : 'Returned tool'), intent:HANDOFF_INTENT.has(packet.intent)?packet.intent:handoffIntent(destination), objectIds:[], canvasBoardId:'', status:'returned', createdAt:packet.createdAt || nowIso(), launchedAt:packet.createdAt || null, returnedAt:packet.returnedAt || nowIso(), closedAt:null, returnObjectIds:[], note:'Manual return package received without a matching local launch record.' };
      project.handoffs.entries.unshift(entry);
    }
    const createdIds = [];
    packet.artifacts.forEach((artifact) => {
      if (project.objects.length >= MAX_OBJECTS) return;
      const obj = objectTemplate(artifact.type, artifact.title);
      obj.summary = artifact.summary; obj.content = artifact.content; obj.tags = artifact.tags; obj.status = artifact.status;
      obj.provenance.sourceType = 'tool'; obj.provenance.sourceTitle = artifact.sourceTitle || entry.destinationLabel; obj.provenance.sourceUrl = artifact.sourceUrl; obj.provenance.capturedAt = packet.returnedAt || nowIso();
      project.objects.push(obj); createdIds.push(obj.id);
    });
    entry.status = 'returned'; entry.returnedAt = packet.returnedAt || nowIso(); entry.returnObjectIds = [...new Set([...(entry.returnObjectIds || []), ...createdIds])].slice(0,MAX_RETURN_ARTIFACTS);
    project.handoffs.activeHandoffId = entry.id;
    if (createdIds[0]) project.activeObjectId = createdIds[0];
    touchHandoffs(project); addActivity(project,'handoff-return',`${entry.destinationLabel} returned ${createdIds.length} artifact${createdIds.length===1?'':'s'}`);
    state.activeProjectId = project.id;
    markReturnProcessed(packet.returnId);
    return { ok:true, project, entry, createdIds, adapted:adapted.adapter, message: createdIds.length ? `${createdIds.length} returned artifact${createdIds.length===1?'':'s'} added to ${project.title}.` : `Return received from ${entry.destinationLabel}.` };
  }

  function traceabilityTemplate() {
    const stamp = nowIso();
    return { schema: TRACEABILITY_SCHEMA, evidenceAssessments: [], lineage: [], reproducibility: [], createdAt: stamp, updatedAt: stamp };
  }

  function clampScore(value) { const n=Number(value); return Number.isFinite(n) ? Math.max(0,Math.min(4,Math.round(n))) : 0; }
  function normalizeEvidenceAssessment(raw, objectIds) {
    if (!raw || typeof raw !== 'object') return null; const stamp=nowIso(); const objectId=String(raw.objectId||'').slice(0,160); if(!objectIds.has(objectId)) return null;
    return { id:String(raw.id||id('tea')).slice(0,160), objectId, relevance:clampScore(raw.relevance), sourceQuality:clampScore(raw.sourceQuality), independence:clampScore(raw.independence), recency:clampScore(raw.recency), note:String(raw.note||'').slice(0,2000), fingerprint:String(raw.fingerprint||'').toLowerCase().replace(/[^a-f0-9]/g,'').slice(0,64), fingerprintAlgorithm:'SHA-256', fingerprintState:['unverified','match','changed'].includes(raw.fingerprintState)?raw.fingerprintState:'unverified', createdAt:validIso(raw.createdAt)?raw.createdAt:stamp, updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp };
  }
  function normalizeLineage(raw, objectIds) {
    if(!raw||typeof raw!=='object')return null; const fromObjectId=String(raw.fromObjectId||'').slice(0,160),toObjectId=String(raw.toObjectId||'').slice(0,160); if(!objectIds.has(fromObjectId)||!objectIds.has(toObjectId)||fromObjectId===toObjectId)return null;
    return { id:String(raw.id||id('tl')).slice(0,160),fromObjectId,toObjectId,relation:TRACE_RELATIONS.has(raw.relation)?raw.relation:'derived-from',note:String(raw.note||'').slice(0,500),createdAt:validIso(raw.createdAt)?raw.createdAt:nowIso() };
  }
  function normalizeRepro(raw, objectIds) {
    if(!raw||typeof raw!=='object')return null; const stamp=nowIso(); const keep=(v)=>Array.isArray(v)?[...new Set(v.map(x=>String(x).slice(0,160)).filter(x=>objectIds.has(x)))].slice(0,60):[]; const analysisObjectId=String(raw.analysisObjectId||'').slice(0,160);
    return { id:String(raw.id||id('trr')).slice(0,160),title:String(raw.title||'Reproduction record').trim().slice(0,200)||'Reproduction record',analysisObjectId:objectIds.has(analysisObjectId)?analysisObjectId:'',datasetObjectIds:keep(raw.datasetObjectIds),evidenceObjectIds:keep(raw.evidenceObjectIds),resultObjectIds:keep(raw.resultObjectIds),method:String(raw.method||'').slice(0,4000),parameters:String(raw.parameters||'').slice(0,5000),environment:String(raw.environment||'').slice(0,3000),steps:String(raw.steps||'').slice(0,8000),status:REPRO_STATUS.has(raw.status)?raw.status:'draft',createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp,lastVerifiedAt:validIso(raw.lastVerifiedAt)?raw.lastVerifiedAt:null };
  }
  function normalizeTraceability(raw, objects=[]) {
    const base=traceabilityTemplate(), value=raw&&typeof raw==='object'?raw:{}, objectIds=new Set(objects.map(o=>o.id));
    base.evidenceAssessments=Array.isArray(value.evidenceAssessments)?value.evidenceAssessments.map(x=>normalizeEvidenceAssessment(x,objectIds)).filter(Boolean).slice(0,MAX_EVIDENCE_ASSESSMENTS):[];
    base.lineage=Array.isArray(value.lineage)?value.lineage.map(x=>normalizeLineage(x,objectIds)).filter(Boolean).slice(0,MAX_LINEAGE_RELATIONS):[];
    base.reproducibility=Array.isArray(value.reproducibility)?value.reproducibility.map(x=>normalizeRepro(x,objectIds)).filter(Boolean).slice(0,MAX_REPRO_RECORDS):[];
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt; base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt; return base;
  }
  function touchTraceability(project){ if(!project.traceability)project.traceability=traceabilityTemplate(); project.traceability.updatedAt=nowIso(); project.updatedAt=project.traceability.updatedAt; }
  function cleanTraceabilityReferences(project, objectId){ if(!project||!project.traceability)return; const t=project.traceability; t.evidenceAssessments=t.evidenceAssessments.filter(x=>x.objectId!==objectId); t.lineage=t.lineage.filter(x=>x.fromObjectId!==objectId&&x.toObjectId!==objectId); t.reproducibility.forEach(x=>{if(x.analysisObjectId===objectId)x.analysisObjectId='';x.datasetObjectIds=x.datasetObjectIds.filter(v=>v!==objectId);x.evidenceObjectIds=x.evidenceObjectIds.filter(v=>v!==objectId);x.resultObjectIds=x.resultObjectIds.filter(v=>v!==objectId);}); touchTraceability(project); }
  function canonicalObjectFingerprintText(object){ return JSON.stringify({schema:object.schema,id:object.id,type:object.type,title:object.title,summary:object.summary,content:object.content,status:object.status,tags:object.tags,provenance:object.provenance}); }
  async function sha256Object(object){
    try { if(!window.crypto||!window.crypto.subtle||typeof TextEncoder==='undefined') return ''; const bytes=new TextEncoder().encode(canonicalObjectFingerprintText(object)); const digest=await window.crypto.subtle.digest('SHA-256',bytes); return Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join(''); } catch(_){ return ''; }
  }



  function briefingTemplate() {
    const stamp = nowIso();
    return { schema: BRIEFING_SCHEMA, drafts: [], activeDraftId: null, createdAt: stamp, updatedAt: stamp };
  }
  function normalizeBriefingSection(raw, objectIds) {
    if (!raw || typeof raw !== 'object') return null; const stamp=nowIso();
    return { id:String(raw.id||id('bs')).slice(0,160), heading:String(raw.heading||'').trim().slice(0,180), body:String(raw.body||'').slice(0,8000), objectIds:Array.isArray(raw.objectIds)?[...new Set(raw.objectIds.map(v=>String(v).slice(0,160)).filter(v=>objectIds.has(v)))].slice(0,MAX_BRIEFING_OBJECT_REFS):[], createdAt:validIso(raw.createdAt)?raw.createdAt:stamp, updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp };
  }
  function normalizeBriefingDraft(raw, objectIds) {
    if (!raw || typeof raw !== 'object') return null; const stamp=nowIso(); const documentObjectId=String(raw.documentObjectId||'').slice(0,160);
    const draft={ id:String(raw.id||id('bd')).slice(0,160), title:String(raw.title||'Untitled draft').trim().slice(0,200)||'Untitled draft', format:BRIEFING_FORMATS.has(raw.format)?raw.format:'briefing', audience:String(raw.audience||'').slice(0,300), purpose:String(raw.purpose||'').slice(0,600), status:BRIEFING_STATUS.has(raw.status)?raw.status:'draft', objectIds:Array.isArray(raw.objectIds)?[...new Set(raw.objectIds.map(v=>String(v).slice(0,160)).filter(v=>objectIds.has(v)))].slice(0,MAX_BRIEFING_OBJECT_REFS):[], sections:[], documentObjectId:objectIds.has(documentObjectId)?documentObjectId:'', createdAt:validIso(raw.createdAt)?raw.createdAt:stamp, updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp, lastExportedAt:validIso(raw.lastExportedAt)?raw.lastExportedAt:null };
    draft.sections=Array.isArray(raw.sections)?raw.sections.map(x=>normalizeBriefingSection(x,objectIds)).filter(x=>x&&x.heading).slice(0,MAX_BRIEFING_SECTIONS):[]; return draft;
  }
  function normalizeBriefing(raw, objects=[]) {
    const base=briefingTemplate(), value=raw&&typeof raw==='object'?raw:{}, objectIds=new Set(objects.map(o=>o.id));
    base.drafts=Array.isArray(value.drafts)?value.drafts.map(x=>normalizeBriefingDraft(x,objectIds)).filter(Boolean).slice(0,MAX_BRIEFING_DRAFTS):[];
    base.activeDraftId=base.drafts.some(x=>x.id===value.activeDraftId)?value.activeDraftId:null; base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt; base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt; return base;
  }
  function touchBriefing(project){ if(!project.briefing)project.briefing=briefingTemplate(); project.briefing.updatedAt=nowIso(); project.updatedAt=project.briefing.updatedAt; }
  function cleanBriefingReferences(project, objectId){ if(!project||!project.briefing)return; project.briefing.drafts.forEach(d=>{d.objectIds=d.objectIds.filter(v=>v!==objectId);d.sections.forEach(sec=>{sec.objectIds=sec.objectIds.filter(v=>v!==objectId);});if(d.documentObjectId===objectId)d.documentObjectId='';});touchBriefing(project); }
  function briefingOutline(format){
    const outlines={
      'briefing':['Executive summary','Question and context','Evidence base','Analysis','Decision implications','Next steps'],
      'memo':['Purpose','Background','Findings','Recommendation','Risks and limitations','Next steps'],
      'report':['Executive summary','Scope','Evidence and methods','Findings','Analysis','Conclusions','Limitations'],
      'article':['Introduction','Context','Evidence','Analysis','Implications','Conclusion'],
      'publication-draft':['Abstract','Introduction','Evidence base','Analysis','Discussion','Conclusion','Sources']
    }; return outlines[format]||outlines.briefing;
  }

  function guidedWorkflowDefinitions() {
    return {
      'research-investigation': { title:'Research Investigation', description:'Move from a bounded question through source collection, evidence assessment, analysis, and a reusable briefing.', steps:[
        ['frame-question','Frame the question','Define the scope, constraints, and what would count as a useful answer.','research'],
        ['collect-sources','Collect sources','Capture and organize relevant sources in the Research Workspace.','research'],
        ['extract-evidence','Extract evidence','Create evidence objects and preserve links back to their sources.','research'],
        ['assess-evidence','Assess evidence','Record relevance, source quality, independence, recency, and provenance.','traceability'],
        ['analyze','Analyze the evidence','Make methods, assumptions, comparisons, and findings explicit.','analysis'],
        ['brief','Prepare a briefing','Turn the connected work into a traceable briefing or report.','briefing']
      ]},
      'evidence-review': { title:'Evidence Review', description:'Appraise a body of evidence without collapsing uncertainty into a single score.', steps:[
        ['scope-review','Define the review scope','State the question, inclusion boundary, and review purpose.','research'],
        ['capture-sources','Capture the source set','Register the sources that belong in the review.','research'],
        ['extract-evidence','Extract evidence','Create evidence objects and source relationships.','research'],
        ['assess-provenance','Assess provenance','Record evidence quality dimensions and fingerprints.','traceability'],
        ['map-claims','Map claims and tensions','Connect evidence to claims, contradictions, and gaps.','research'],
        ['synthesize','Synthesize the review','Prepare a reusable evidence package or briefing.','briefing']
      ]},
      'analytical-assessment': { title:'Analytical Assessment', description:'Structure an analysis so questions, datasets, assumptions, methods, findings, and reproducibility remain connected.', steps:[
        ['analysis-question','Frame the analysis question','Define the analytical question and intended decision/use.','analysis'],
        ['register-data','Register datasets and variables','Make data inputs, variables, units, and definitions visible.','analysis'],
        ['state-assumptions','State assumptions','Record assumptions and link supporting evidence where available.','analysis'],
        ['select-method','Select methods','Record the method and create the canonical Analysis object.','analysis'],
        ['record-findings','Record findings','Capture comparisons, findings, uncertainty, and evidence links.','analysis'],
        ['reproduce','Document reproducibility','Record environment, parameters, steps, and result objects.','traceability'],
        ['communicate','Communicate the analysis','Build a report or briefing from the connected analytical record.','briefing']
      ]},
      'decision-case': { title:'Decision Case', description:'Move from a decision question to explicit alternatives, criteria, evidence, risk, rationale, and a durable decision record.', steps:[
        ['frame-decision','Frame the decision','State the decision question and the boundary of the choice.','decision'],
        ['develop-options','Develop options','Create candidate alternatives without prematurely selecting one.','decision'],
        ['define-criteria','Define criteria','Record evaluation criteria and weights explicitly.','decision'],
        ['connect-evidence','Connect evidence and analysis','Bring relevant evidence and analytical objects into the decision case.','decision'],
        ['assess-tradeoffs','Assess trade-offs and risks','Score option/criterion pairs and record risks and mitigations.','decision'],
        ['record-decision','Record the decision','Select an option and preserve rationale and confidence.','decision'],
        ['brief-decision','Prepare the decision briefing','Materialize a briefing or memo with a traceable basis.','briefing']
      ]},
      'systems-mapping': { title:'Systems Mapping', description:'Use evidence, data, stakeholders, relationships, and structured visual reasoning to develop a system-level synthesis.', steps:[
        ['define-system','Define the system','State the focal system, boundary, purpose, and key question.','overview'],
        ['collect-basis','Collect the evidence basis','Capture sources, evidence, and relevant data objects.','research'],
        ['identify-elements','Identify actors and elements','Create stakeholders, systems, claims, data, and idea nodes.','canvas'],
        ['map-relations','Map relationships','Use typed relationships and frames to make structure visible.','canvas'],
        ['analyze-system','Analyze the system','Record assumptions, patterns, comparisons, and implications.','analysis'],
        ['capture-synthesis','Capture synthesis','Materialize the Canvas synthesis and prepare a briefing.','briefing']
      ]},
      'publication-preparation': { title:'Publication Preparation', description:'Move a mature project into a traceable publication draft without bypassing the public publishing systems.', steps:[
        ['review-basis','Review the basis','Confirm the sources, evidence, analyses, decisions, and documents the publication will rely on.','traceability'],
        ['check-lineage','Check lineage and provenance','Confirm that important claims and outputs retain their basis.','traceability'],
        ['create-draft','Create the draft','Choose a publication format, audience, purpose, and object basis.','briefing'],
        ['structure-draft','Structure the narrative','Build and edit the outline and sections.','briefing'],
        ['materialize','Materialize the Document','Create the canonical Document object and derived-from lineage.','briefing'],
        ['export','Export for publication','Export Markdown, HTML, or a portable publication package for the publishing workflow.','briefing']
      ]}
    };
  }
  function guidedWorkflowsTemplate(){ const stamp=nowIso(); return {schema:GUIDED_WORKFLOWS_SCHEMA,runs:[],activeRunId:null,createdAt:stamp,updatedAt:stamp}; }
  function normalizeWorkflowStep(raw, objectIds){ if(!raw||typeof raw!=='object')return null;const stamp=nowIso();return{id:String(raw.id||id('ws')).slice(0,160),key:String(raw.key||'step').slice(0,80),title:String(raw.title||'Workflow step').trim().slice(0,180)||'Workflow step',description:String(raw.description||'').slice(0,1200),mode:String(raw.mode||'overview').slice(0,40),status:WORKFLOW_STEP_STATUS.has(raw.status)?raw.status:'todo',note:String(raw.note||'').slice(0,2000),objectIds:Array.isArray(raw.objectIds)?[...new Set(raw.objectIds.map(v=>String(v).slice(0,160)).filter(v=>objectIds.has(v)))].slice(0,MAX_WORKFLOW_OBJECT_REFS):[],createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp,completedAt:validIso(raw.completedAt)?raw.completedAt:null}; }
  function normalizeWorkflowRun(raw, objectIds){ if(!raw||typeof raw!=='object')return null;const stamp=nowIso(),defs=guidedWorkflowDefinitions(),templateId=String(raw.templateId||'').slice(0,80);if(!defs[templateId])return null;const steps=Array.isArray(raw.steps)?raw.steps.map(x=>normalizeWorkflowStep(x,objectIds)).filter(Boolean).slice(0,MAX_WORKFLOW_STEPS):[];const currentStepId=steps.some(x=>x.id===raw.currentStepId)?raw.currentStepId:null;return{id:String(raw.id||id('wr')).slice(0,160),templateId,title:String(raw.title||defs[templateId].title).trim().slice(0,200)||defs[templateId].title,status:WORKFLOW_RUN_STATUS.has(raw.status)?raw.status:'active',currentStepId,steps,createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp,completedAt:validIso(raw.completedAt)?raw.completedAt:null}; }
  function normalizeGuidedWorkflows(raw,objects=[]){const base=guidedWorkflowsTemplate(),value=raw&&typeof raw==='object'?raw:{},objectIds=new Set(objects.map(o=>o.id));base.runs=Array.isArray(value.runs)?value.runs.map(x=>normalizeWorkflowRun(x,objectIds)).filter(Boolean).slice(0,MAX_WORKFLOW_RUNS):[];base.activeRunId=base.runs.some(x=>x.id===value.activeRunId)?value.activeRunId:null;base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt;base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt;return base;}
  function touchGuidedWorkflows(project){if(!project.guidedWorkflows)project.guidedWorkflows=guidedWorkflowsTemplate();project.guidedWorkflows.updatedAt=nowIso();project.updatedAt=project.guidedWorkflows.updatedAt;}
  function cleanGuidedWorkflowReferences(project,objectId){if(!project||!project.guidedWorkflows)return;project.guidedWorkflows.runs.forEach(run=>run.steps.forEach(step=>{step.objectIds=step.objectIds.filter(v=>v!==objectId);}));touchGuidedWorkflows(project);}
  function startGuidedWorkflow(project,templateId){const defs=guidedWorkflowDefinitions(),def=defs[templateId];if(!project||!def||project.guidedWorkflows.runs.length>=MAX_WORKFLOW_RUNS)return null;const stamp=nowIso();const steps=def.steps.slice(0,MAX_WORKFLOW_STEPS).map(([key,title,description,mode],index)=>({id:id('ws'),key,title,description,mode,status:index===0?'in-progress':'todo',note:'',objectIds:[],createdAt:stamp,updatedAt:stamp,completedAt:null}));const run={id:id('wr'),templateId,title:def.title,status:'active',currentStepId:steps[0]?.id||null,steps,createdAt:stamp,updatedAt:stamp,completedAt:null};project.guidedWorkflows.runs.unshift(run);project.guidedWorkflows.activeRunId=run.id;touchGuidedWorkflows(project);addActivity(project,'workflow-started',`Guided workflow started: ${def.title}`);return run;}

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

  function aiAssistanceTemplate() {
    const stamp = nowIso();
    return { schema: AI_ASSISTANCE_SCHEMA, sessions: [], activeSessionId: null, createdAt: stamp, updatedAt: stamp };
  }

  function normalizeAiSession(raw, objectIds) {
    if (!raw || typeof raw !== 'object') return null;
    const stamp = nowIso();
    const ids = Array.isArray(raw.objectIds) ? [...new Set(raw.objectIds.map(v=>String(v).slice(0,160)))].filter(v=>objectIds.has(v)).slice(0,MAX_AI_OBJECT_REFS) : [];
    const citations = Array.isArray(raw.citationObjectIds) ? [...new Set(raw.citationObjectIds.map(v=>String(v).slice(0,160)))].filter(v=>objectIds.has(v)&&ids.includes(v)).slice(0,MAX_AI_OBJECT_REFS) : [];
    return {
      id:String(raw.id||id('ai')).slice(0,160),
      title:String(raw.title||'AI assistance request').trim().slice(0,200)||'AI assistance request',
      task:AI_TASKS.has(raw.task)?raw.task:'general-question',
      status:AI_SESSION_STATUS.has(raw.status)?raw.status:'prepared',
      prompt:String(raw.prompt||'').slice(0,MAX_AI_PROMPT),
      objectIds:ids,
      response:String(raw.response||'').slice(0,MAX_AI_RESPONSE),
      responseSource:AI_RESPONSE_SOURCES.has(raw.responseSource)?raw.responseSource:'manual',
      citationObjectIds:citations,
      acceptedDocumentObjectId:objectIds.has(String(raw.acceptedDocumentObjectId||''))?String(raw.acceptedDocumentObjectId):'',
      createdAt:validIso(raw.createdAt)?raw.createdAt:stamp,
      updatedAt:validIso(raw.updatedAt)?raw.updatedAt:stamp,
      sentAt:validIso(raw.sentAt)?raw.sentAt:null,
      respondedAt:validIso(raw.respondedAt)?raw.respondedAt:null,
      acceptedAt:validIso(raw.acceptedAt)?raw.acceptedAt:null
    };
  }

  function normalizeAiAssistance(raw, objects=[]) {
    const base=aiAssistanceTemplate(), value=raw&&typeof raw==='object'?raw:{}, objectIds=new Set(objects.map(o=>o.id));
    base.sessions=Array.isArray(value.sessions)?value.sessions.map(x=>normalizeAiSession(x,objectIds)).filter(Boolean).slice(0,MAX_AI_SESSIONS):[];
    base.activeSessionId=base.sessions.some(x=>x.id===value.activeSessionId)?value.activeSessionId:null;
    base.createdAt=validIso(value.createdAt)?value.createdAt:base.createdAt; base.updatedAt=validIso(value.updatedAt)?value.updatedAt:base.updatedAt;
    return base;
  }

  function touchAiAssistance(project){ if(!project.aiAssistance)project.aiAssistance=aiAssistanceTemplate(); project.aiAssistance.updatedAt=nowIso(); project.updatedAt=project.aiAssistance.updatedAt; }
  function activeAiSession(project){ return project&&project.aiAssistance?project.aiAssistance.sessions.find(x=>x.id===project.aiAssistance.activeSessionId)||null:null; }
  function cleanAiAssistanceReferences(project,objectId){ if(!project||!project.aiAssistance)return; project.aiAssistance.sessions.forEach(s=>{s.objectIds=s.objectIds.filter(v=>v!==objectId);s.citationObjectIds=s.citationObjectIds.filter(v=>v!==objectId);if(s.acceptedDocumentObjectId===objectId)s.acceptedDocumentObjectId='';});touchAiAssistance(project); }
  function aiTaskLabel(task){ return ({'grounded-summary':'Grounded summary','evidence-gaps':'Evidence gaps & contradictions','compare-alternatives':'Compare alternatives','briefing-draft':'Draft briefing section','method-explanation':'Explain method & assumptions','general-question':'Grounded question'})[task]||'Grounded question'; }
  function aiGroundingPolicy(){ return {selectedWorkspaceContextOnly:true,discloseInsufficientEvidence:true,distinguishEvidenceFromInference:true,preserveUncertainty:true,noDecisionAuthority:true,noAutomaticPublication:true,humanAcceptanceRequired:true}; }
  function aiSelectedObjects(project,session){ const ids=new Set(session.objectIds); return project.objects.filter(o=>ids.has(o.id)&&!o.archivedAt); }
  function aiRequestPackage(project,session){
    return {schema:AI_REQUEST_EXPORT_SCHEMA,workspaceVersion:rootVersion(),exportedAt:nowIso(),request:{id:session.id,title:session.title,task:session.task,prompt:session.prompt,status:session.status},project:{id:project.id,title:project.title},returnUrl:(document.querySelector('[data-sc-workspace]')?.dataset.returnUrl||window.location.href),responseStorageKey:AI_RESPONSE_KEY,responseSchema:AI_RESPONSE_SCHEMA,groundingPolicy:aiGroundingPolicy(),selectedObjects:aiSelectedObjects(project,session).map(o=>({id:o.id,type:o.type,title:o.title,summary:o.summary,content:o.content,status:o.status,tags:o.tags,provenance:o.provenance}))};
  }
  function rootVersion(){ const el=document.querySelector('[data-sc-workspace]'); return el&&el.dataset.version?el.dataset.version:'0.23.0'; }
  function aiPromptMarkdown(project,session){
    const objects=aiSelectedObjects(project,session), lines=[`# ${session.title}`,`Task: ${aiTaskLabel(session.task)}`,'','## User request',session.prompt||'(No additional prompt supplied.)','','## Grounding rules','- Use only the selected Workspace context below unless explicitly stating that more information is needed.','- Distinguish source-backed statements from inference.','- Preserve uncertainty, limitations, and conflicting evidence.','- Do not make or approve a final decision for the user.','- Do not invent citations or claim access to sources not included here.',''];
    objects.forEach((o,i)=>{lines.push(`## Context ${i+1}: ${o.title}`,`Workspace Object ID: ${o.id}`,`Type: ${o.type}`,`Status: ${o.status}`,`Provenance: ${o.provenance?.sourceTitle||o.provenance?.sourceType||'manual'}${o.provenance?.sourceUrl?` — ${o.provenance.sourceUrl}`:''}`,'',o.summary?`Summary: ${o.summary}`:'',o.content?`Content:\n${o.content}`:'','');});
    return lines.filter((v,i,a)=>!(v===''&&a[i-1]==='')).join('\n');
  }
  function aiResponsePackage(project,session){return {schema:AI_RESPONSE_EXPORT_SCHEMA,workspaceVersion:rootVersion(),exportedAt:nowIso(),project:{id:project.id,title:project.title},requestId:session.id,task:session.task,status:session.status,responseSource:session.responseSource,response:session.response,citationObjectIds:session.citationObjectIds.slice(),acceptedDocumentObjectId:session.acceptedDocumentObjectId||null,groundingPolicy:aiGroundingPolicy()};}
  function writeAiRequestToSession(project,session){try{window.sessionStorage.setItem(AI_REQUEST_KEY,JSON.stringify(aiRequestPackage(project,session)));return true;}catch(_){return false;}}

  function ingestAiResponsePacket(stateValue, raw){
    if(!raw||typeof raw!=='object'||raw.schema!==AI_RESPONSE_SCHEMA)return {ok:false,message:'Unsupported AI response package.'};
    const project=stateValue.projects.find(p=>p.id===String(raw.projectId||'')&&!p.archivedAt); if(!project)return {ok:false,message:'AI response does not match a local Workspace Project.'};
    const session=project.aiAssistance&&project.aiAssistance.sessions.find(x=>x.id===String(raw.requestId||'')); if(!session)return {ok:false,message:'AI response does not match a local assistance request.'};
    const response=String(raw.response||'').slice(0,MAX_AI_RESPONSE); if(!response)return {ok:false,message:'AI response is empty.'};
    const allowed=new Set(session.objectIds); session.response=response; session.responseSource='adapter'; session.citationObjectIds=Array.isArray(raw.citationObjectIds)?[...new Set(raw.citationObjectIds.map(v=>String(v).slice(0,160)).filter(v=>allowed.has(v)))].slice(0,MAX_AI_OBJECT_REFS):[]; session.status='response-received'; session.respondedAt=validIso(raw.returnedAt)?raw.returnedAt:nowIso(); session.updatedAt=nowIso(); project.aiAssistance.activeSessionId=session.id; touchAiAssistance(project); addActivity(project,'ai-response-returned',`AI response returned for review: ${session.title}`); return {ok:true,message:'AI response returned for human review.',projectId:project.id,requestId:session.id};
  }
  function checkAiResponseInbox(showMessage=false){try{const raw=window.sessionStorage.getItem(AI_RESPONSE_KEY);if(!raw)return false;const result=ingestAiResponsePacket(state,JSON.parse(raw));if(!result.ok){if(showMessage)window.alert(result.message);return false;}window.sessionStorage.removeItem(AI_RESPONSE_KEY);state.activeProjectId=result.projectId;activeProjectMode='assist';persist(result.message);render();return true;}catch(_){if(showMessage)window.alert('Workspace could not read the AI response inbox.');return false;}}

  function projectTemplate(title, description = '') {
    const stamp = nowIso();
    const project = {
      schema: PROJECT_SCHEMA,
      id: id('scwp'),
      persistence: projectPersistenceTemplate(),
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
      activeObjectId: null,
      research: researchTemplate(),
      analysis: analysisTemplate(),
      decision: decisionTemplate(),
      canvas: canvasTemplate(),
      handoffs: handoffLedgerTemplate(),
      traceability: traceabilityTemplate(),
      briefing: briefingTemplate(),
      guidedWorkflows: guidedWorkflowsTemplate(),
      aiAssistance: aiAssistanceTemplate()
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
    const canvas = normalizeCanvas(raw.canvas, objects);
    return {
      schema: PROJECT_SCHEMA,
      id: String(raw.id || id('scwp')).slice(0, 160),
      persistence: normalizeProjectPersistence(raw.persistence),
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
      activeObjectId,
      research: normalizeResearch(raw.research, objects),
      analysis: normalizeAnalysis(raw.analysis, objects),
      decision: normalizeDecision(raw.decision, objects),
      canvas,
      handoffs: normalizeHandoffs(raw.handoffs, objects, canvas),
      traceability: normalizeTraceability(raw.traceability, objects),
      briefing: normalizeBriefing(raw.briefing, objects),
      guidedWorkflows: normalizeGuidedWorkflows(raw.guidedWorkflows, objects),
      aiAssistance: normalizeAiAssistance(raw.aiAssistance, objects)
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
      activeProjectMode = 'overview';
    }
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV2(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized && project.schema === LEGACY_PROJECT_SCHEMA_V1) addActivity(normalized, 'migrated', 'Project upgraded from v0.2.0 to Workspace object model');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.accountPersistence = normalizeAccountPersistence(raw.accountPersistence, state.projects);
    state.crossDeviceSync = normalizeCrossDeviceSync(raw.crossDeviceSync, state.projects);
    state.knowledge = normalizeKnowledge(raw.knowledge, state.projects);
    state.knowledgeGraph = normalizeKnowledgeGraph(raw.knowledgeGraph, state.projects);
    state.activityIntelligence = normalizeActivityIntelligence(raw.activityIntelligence, state.projects);
    state.interoperability = normalizeInteroperability(raw.interoperability);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV3(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Project upgraded to Research Workspace');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV4(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Identity and persistence boundary added; project remains saved on this device');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }



  function migrateV5(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Project upgraded to Analysis Workspace');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }



  function migrateV6(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Project upgraded to Decision Workspace');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV7(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Project upgraded to Canvas & Structured Thinking');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV8(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map((project) => {
      const normalized = normalizeProject(project);
      if (normalized) addActivity(normalized, 'migrated', 'Project upgraded to Cross-Product Handoffs');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV9(raw) {
    const state=defaultState();
    state.projects=Array.isArray(raw.projects)?raw.projects.map((project)=>{const normalized=normalizeProject(project);if(normalized)addActivity(normalized,'migrated','Project upgraded to Evidence, Provenance & Reproducibility');return normalized;}).filter(Boolean):[];
    state.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    state.activeProjectId=state.projects.some((project)=>project.id===raw.activeProjectId&&!project.archivedAt)?raw.activeProjectId:null; state.identity=normalizeIdentity(raw.identity); state.createdAt=validIso(raw.createdAt)?raw.createdAt:state.createdAt; state.updatedAt=nowIso(); return state;
  }


  function migrateV10(raw) {
    const state=defaultState();
    state.projects=Array.isArray(raw.projects)?raw.projects.map((project)=>{const normalized=normalizeProject(project);if(normalized)addActivity(normalized,'migrated','Project upgraded to Briefing & Publication Studio');return normalized;}).filter(Boolean):[];
    state.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    state.activeProjectId=state.projects.some((project)=>project.id===raw.activeProjectId&&!project.archivedAt)?raw.activeProjectId:null; state.identity=normalizeIdentity(raw.identity); state.createdAt=validIso(raw.createdAt)?raw.createdAt:state.createdAt; state.updatedAt=nowIso(); return state;
  }

  function migrateV11(raw) {
    const state=defaultState();
    state.projects=Array.isArray(raw.projects)?raw.projects.map((project)=>{const normalized=normalizeProject(project);if(normalized)addActivity(normalized,'migrated','Project upgraded to Templates & Guided Workflows');return normalized;}).filter(Boolean):[];
    state.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    state.activeProjectId=state.projects.some((project)=>project.id===raw.activeProjectId&&!project.archivedAt)?raw.activeProjectId:null;state.identity=normalizeIdentity(raw.identity);state.createdAt=validIso(raw.createdAt)?raw.createdAt:state.createdAt;state.updatedAt=nowIso();return state;
  }

  function migrateV12(raw) {
    const state = defaultState();
    state.projects = Array.isArray(raw.projects) ? raw.projects.map(normalizeProject).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some(project => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.identity = normalizeIdentity(raw.identity);
    state.knowledge = normalizeKnowledge(raw.knowledge, state.projects);
    state.knowledgeGraph = normalizeKnowledgeGraph(raw.knowledgeGraph, state.projects);
    state.activityIntelligence = normalizeActivityIntelligence(raw.activityIntelligence, state.projects);
    state.interoperability = normalizeInteroperability(raw.interoperability);
    state.share = normalizeShare(raw.share);
    state.collaboration = normalizeCollaboration(raw.collaboration, state.projects);
    state.institutional = normalizeInstitutional(raw.institutional, state.projects);
    state.accountPersistence = normalizeAccountPersistence(raw.accountPersistence, state.projects);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = nowIso();
    return state;
  }

  function migrateV13(raw) {
    const state=defaultState();
    state.projects=Array.isArray(raw.projects)?raw.projects.map((project)=>{const normalized=normalizeProject(project);if(normalized)addActivity(normalized,'migrated','Project upgraded to Responsible AI Assistance');return normalized;}).filter(Boolean):[];
    state.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    state.activeProjectId=state.projects.some((project)=>project.id===raw.activeProjectId&&!project.archivedAt)?raw.activeProjectId:null;
    state.identity=normalizeIdentity(raw.identity); state.knowledge=normalizeKnowledge(raw.knowledge,state.projects); state.createdAt=validIso(raw.createdAt)?raw.createdAt:state.createdAt; state.updatedAt=nowIso(); return state;
  }

  function migrateV14(raw) {
    const state=defaultState(); state.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[]; state.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[]; state.activeProjectId=state.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null; state.identity=normalizeIdentity(raw.identity); state.knowledge=normalizeKnowledge(raw.knowledge,state.projects); state.interoperability=interoperabilityTemplate(); state.createdAt=validIso(raw.createdAt)?raw.createdAt:state.createdAt; state.updatedAt=nowIso(); return state;
  }

  function migrateV15(raw) {
    const next=defaultState();next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;next.identity=normalizeIdentity(raw.identity);next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);next.interoperability=normalizeInteroperability(raw.interoperability);next.share=shareTemplate();next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;next.updatedAt=nowIso();return next;
  }


  function migrateV16(raw) {
    const next=defaultState();
    next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];
    next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;
    next.identity=normalizeIdentity(raw.identity);
    next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);
    next.knowledgeGraph=knowledgeGraphTemplate();
    next.interoperability=normalizeInteroperability(raw.interoperability);
    next.share=normalizeShare(raw.share);
    next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;
    next.updatedAt=nowIso();
    return next;
  }

  function migrateV17(raw) {
    const next=defaultState();
    next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];
    next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;
    next.identity=normalizeIdentity(raw.identity);
    next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);
    next.knowledgeGraph=normalizeKnowledgeGraph(raw.knowledgeGraph,next.projects);
    next.activityIntelligence=activityIntelligenceTemplate();
    next.interoperability=normalizeInteroperability(raw.interoperability);
    next.share=normalizeShare(raw.share);
    next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;
    next.updatedAt=nowIso();
    return next;
  }

  function migrateV18(raw) {
    const next=defaultState();
    next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];
    next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;
    next.identity=normalizeIdentity(raw.identity);next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);next.knowledgeGraph=normalizeKnowledgeGraph(raw.knowledgeGraph,next.projects);next.activityIntelligence=normalizeActivityIntelligence(raw.activityIntelligence,next.projects);next.interoperability=normalizeInteroperability(raw.interoperability);next.share=normalizeShare(raw.share);next.collaboration=collaborationTemplate();next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;next.updatedAt=nowIso();return next;
  }

  function migrateV19(raw) {
    const next=defaultState();
    next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];
    next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;
    next.identity=normalizeIdentity(raw.identity);
    next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);
    next.knowledgeGraph=normalizeKnowledgeGraph(raw.knowledgeGraph,next.projects);
    next.activityIntelligence=normalizeActivityIntelligence(raw.activityIntelligence,next.projects);
    next.interoperability=normalizeInteroperability(raw.interoperability);
    next.share=normalizeShare(raw.share);
    next.collaboration=normalizeCollaboration(raw.collaboration,next.projects);
    next.institutional=institutionalTemplate();
    next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;
    next.updatedAt=nowIso();
    return next;
  }

  function migrateV20(raw) {
    const next = defaultState();
    next.projects = Array.isArray(raw.projects) ? raw.projects.map(normalizeProject).filter(Boolean) : [];
    next.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    next.activeProjectId = next.projects.some(p => p.id === raw.activeProjectId && !p.archivedAt) ? raw.activeProjectId : null;
    next.identity = normalizeIdentity(raw.identity);
    next.accountPersistence = accountPersistenceTemplate();
    next.knowledge = normalizeKnowledge(raw.knowledge, next.projects);
    next.knowledgeGraph = normalizeKnowledgeGraph(raw.knowledgeGraph, next.projects);
    next.activityIntelligence = normalizeActivityIntelligence(raw.activityIntelligence, next.projects);
    next.interoperability = normalizeInteroperability(raw.interoperability);
    next.share = normalizeShare(raw.share);
    next.collaboration = normalizeCollaboration(raw.collaboration, next.projects);
    next.institutional = normalizeInstitutional(raw.institutional, next.projects);
    next.createdAt = validIso(raw.createdAt) ? raw.createdAt : next.createdAt;
    next.updatedAt = nowIso();
    return next;
  }

  function migrateV21(raw) {
    const next = defaultState();
    next.projects = Array.isArray(raw.projects) ? raw.projects.map(normalizeProject).filter(Boolean) : [];
    next.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    next.activeProjectId = next.projects.some(p => p.id === raw.activeProjectId && !p.archivedAt) ? raw.activeProjectId : null;
    next.identity = normalizeIdentity(raw.identity);
    next.accountPersistence = normalizeAccountPersistence(raw.accountPersistence, next.projects);
    next.crossDeviceSync = crossDeviceSyncTemplate();
    next.knowledge = normalizeKnowledge(raw.knowledge, next.projects);
    next.knowledgeGraph = normalizeKnowledgeGraph(raw.knowledgeGraph, next.projects);
    next.activityIntelligence = normalizeActivityIntelligence(raw.activityIntelligence, next.projects);
    next.interoperability = normalizeInteroperability(raw.interoperability);
    next.share = normalizeShare(raw.share);
    next.collaboration = normalizeCollaboration(raw.collaboration, next.projects);
    next.institutional = normalizeInstitutional(raw.institutional, next.projects);
    next.createdAt = validIso(raw.createdAt) ? raw.createdAt : next.createdAt;
    next.updatedAt = nowIso();
    return next;
  }

  function migrateV22(raw) {
    const next=defaultState();next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;next.identity=normalizeIdentity(raw.identity);next.accountPersistence=normalizeAccountPersistence(raw.accountPersistence,next.projects);next.crossDeviceSync=normalizeCrossDeviceSync(raw.crossDeviceSync,next.projects);next.versionHistory=versionHistoryTemplate();next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);next.knowledgeGraph=normalizeKnowledgeGraph(raw.knowledgeGraph,next.projects);next.activityIntelligence=normalizeActivityIntelligence(raw.activityIntelligence,next.projects);next.interoperability=normalizeInteroperability(raw.interoperability);next.share=normalizeShare(raw.share);next.collaboration=normalizeCollaboration(raw.collaboration,next.projects);next.institutional=normalizeInstitutional(raw.institutional,next.projects);next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;next.updatedAt=nowIso();return next;
  }

  function migrateV23(raw) {
    const next=defaultState();
    next.projects=Array.isArray(raw.projects)?raw.projects.map(normalizeProject).filter(Boolean):[];
    next.recentTools=Array.isArray(raw.recentTools)?raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0,MAX_RECENT_TOOLS):[];
    next.activeProjectId=next.projects.some(p=>p.id===raw.activeProjectId&&!p.archivedAt)?raw.activeProjectId:null;
    next.identity=normalizeIdentity(raw.identity);
    next.accountPersistence=normalizeAccountPersistence(raw.accountPersistence,next.projects);
    next.crossDeviceSync=normalizeCrossDeviceSync(raw.crossDeviceSync,next.projects);
    next.versionHistory=normalizeVersionHistory(raw.versionHistory,next.projects);
    next.safeActions=safeActionsTemplate();
    next.knowledge=normalizeKnowledge(raw.knowledge,next.projects);
    next.knowledgeGraph=normalizeKnowledgeGraph(raw.knowledgeGraph,next.projects);
    next.activityIntelligence=normalizeActivityIntelligence(raw.activityIntelligence,next.projects);
    next.interoperability=normalizeInteroperability(raw.interoperability);
    next.share=normalizeShare(raw.share);
    next.collaboration=normalizeCollaboration(raw.collaboration,next.projects);
    next.institutional=normalizeInstitutional(raw.institutional,next.projects);
    next.createdAt=validIso(raw.createdAt)?raw.createdAt:next.createdAt;
    next.updatedAt=nowIso();
    return next;
  }

  function normalizeState(raw) {
    if (!raw || typeof raw !== 'object') return defaultState();
    if (raw.schemaVersion === 1 || raw.schema === 1) return migrateLegacyV1(raw);
    if (raw.schemaVersion === 2) return migrateV2(raw);
    if (raw.schemaVersion === 3) return migrateV3(raw);
    if (raw.schemaVersion === 4) return migrateV4(raw);
    if (raw.schemaVersion === 5) return migrateV5(raw);
    if (raw.schemaVersion === 6) return migrateV6(raw);
    if (raw.schemaVersion === 7) return migrateV7(raw);
    if (raw.schemaVersion === 8) return migrateV8(raw);
    if (raw.schemaVersion === 9) return migrateV9(raw);
    if (raw.schemaVersion === 10) return migrateV10(raw);
    if (raw.schemaVersion === 11) return migrateV11(raw);
    if (raw.schemaVersion === 12) return migrateV12(raw);
    if (raw.schemaVersion === 13) return migrateV13(raw);
    if (raw.schemaVersion === 14) return migrateV14(raw);
    if (raw.schemaVersion === 15) return migrateV15(raw);
    if (raw.schemaVersion === 16) return migrateV16(raw);
    if (raw.schemaVersion === 17) return migrateV17(raw);
    if (raw.schemaVersion === 18) return migrateV18(raw);
    if (raw.schemaVersion === 19) return migrateV19(raw);
    if (raw.schemaVersion === 20) return migrateV20(raw);
    if (raw.schemaVersion === 21) return migrateV21(raw);
    if (raw.schemaVersion === 22) return migrateV22(raw);
    if (raw.schemaVersion === 23) return migrateV23(raw);
    const state = defaultState();
    state.identity = normalizeIdentity(raw.identity);
    state.projects = Array.isArray(raw.projects) ? raw.projects.map(normalizeProject).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
    state.accountPersistence = normalizeAccountPersistence(raw.accountPersistence, state.projects);
    state.crossDeviceSync = normalizeCrossDeviceSync(raw.crossDeviceSync, state.projects);
    state.versionHistory = normalizeVersionHistory(raw.versionHistory, state.projects);
    state.safeActions = normalizeSafeActions(raw.safeActions, state.projects);
    state.knowledge = normalizeKnowledge(raw.knowledge, state.projects);
    state.knowledgeGraph = normalizeKnowledgeGraph(raw.knowledgeGraph, state.projects);
    state.activityIntelligence = normalizeActivityIntelligence(raw.activityIntelligence, state.projects);
    state.interoperability = normalizeInteroperability(raw.interoperability);
    state.share = normalizeShare(raw.share);
    state.collaboration = normalizeCollaboration(raw.collaboration, state.projects);
    state.institutional = normalizeInstitutional(raw.institutional, state.projects);
    state.createdAt = validIso(raw.createdAt) ? raw.createdAt : state.createdAt;
    state.updatedAt = validIso(raw.updatedAt) ? raw.updatedAt : state.updatedAt;
    return state;
  }

  function localStateLooksValid(raw) {
    if (!raw || typeof raw !== 'string') return false;
    try {
      const parsed = JSON.parse(raw);
      return Boolean(parsed && typeof parsed === 'object' && Array.isArray(parsed.projects));
    } catch (_) { return false; }
  }

  function captureLastGoodSnapshot() {
    try {
      const current = window.localStorage.getItem(STORAGE_KEY);
      if (!localStateLooksValid(current)) return false;
      window.localStorage.setItem(LAST_GOOD_KEY, JSON.stringify({
        schema: 'sc-workspace-last-known-good/1.0',
        capturedAt: nowIso(),
        storageSchemaVersion: STORAGE_VERSION,
        raw: current
      }));
      return true;
    } catch (_) { return false; }
  }

  function readLastGoodState() {
    try {
      const envelope = JSON.parse(window.localStorage.getItem(LAST_GOOD_KEY) || 'null');
      if (!envelope || envelope.schema !== 'sc-workspace-last-known-good/1.0' || !localStateLooksValid(envelope.raw)) return null;
      return normalizeState(JSON.parse(envelope.raw));
    } catch (_) { return null; }
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
          const recovered = readLastGoodState();
          if (recovered) {
            recoveryNotice = 'Workspace isolated a damaged local state and restored the last-known-good local snapshot. Review the project list before continuing.';
            return recovered;
          }
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
    state.identity = normalizeIdentity(state.identity);
    state.projects.forEach((project) => { project.persistence = normalizeProjectPersistence(project.persistence); });
    state.activityIntelligence = normalizeActivityIntelligence(state.activityIntelligence, state.projects);
    state.interoperability = normalizeInteroperability(state.interoperability);
    state.share = normalizeShare(state.share);
    state.collaboration = normalizeCollaboration(state.collaboration, state.projects);
    state.institutional = normalizeInstitutional(state.institutional, state.projects);
    state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
    state.crossDeviceSync = normalizeCrossDeviceSync(state.crossDeviceSync, state.projects);
    state.versionHistory = normalizeVersionHistory(state.versionHistory, state.projects);
    state.updatedAt = nowIso();
    try {
      const serialized = JSON.stringify(state);
      captureLastGoodSnapshot();
      window.localStorage.setItem(STORAGE_KEY, serialized);
      const verified = window.localStorage.getItem(STORAGE_KEY);
      if (verified !== serialized) throw new Error('read-after-write verification failed');
      return true;
    } catch (_) {
      recoveryNotice = 'Workspace could not save and verify browser storage. Your current changes may only last for this page; the previous last-known-good snapshot was preserved when possible.';
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


  function downloadText(filename, text, type='text/plain;charset=utf-8') {
    const blob = new Blob([String(text || '')], { type }); const url=URL.createObjectURL(blob); const anchor=document.createElement('a'); anchor.href=url; anchor.download=filename; document.body.appendChild(anchor); anchor.click(); anchor.remove(); window.setTimeout(()=>URL.revokeObjectURL(url),500);
  }
  function prefersReducedMotion() {
    try { return Boolean(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches); }
    catch (_) { return false; }
  }

  function approximateBytes(value) {
    try {
      const text = typeof value === 'string' ? value : JSON.stringify(value);
      return window.TextEncoder ? new TextEncoder().encode(text).length : text.length * 2;
    } catch (_) { return 0; }
  }

  function privacyMinimizedDiagnostic(state) {
    let storageAvailable = false, stateSerializable = false, lastKnownGood = false, currentRaw = '';
    try {
      const probe = '__scw_readiness_probe__';
      window.localStorage.setItem(probe, '1');
      storageAvailable = window.localStorage.getItem(probe) === '1';
      window.localStorage.removeItem(probe);
      currentRaw = window.localStorage.getItem(STORAGE_KEY) || '';
      stateSerializable = Boolean(JSON.stringify(state));
      const envelope = JSON.parse(window.localStorage.getItem(LAST_GOOD_KEY) || 'null');
      lastKnownGood = Boolean(envelope && envelope.schema === 'sc-workspace-last-known-good/1.0' && localStateLooksValid(envelope.raw));
    } catch (_) {}
    const projects = Array.isArray(state.projects) ? state.projects : [];
    const objectCount = projects.reduce((sum, project) => sum + (Array.isArray(project.objects) ? project.objects.length : 0), 0);
    return {
      schema: READINESS_DIAGNOSTIC_SCHEMA,
      workspaceVersion: rootVersion(),
      generatedAt: nowIso(),
      storageSchemaVersion: STORAGE_VERSION,
      projectSchema: PROJECT_SCHEMA,
      privacy: { localOnly: true, projectContentIncluded: false, objectContentIncluded: false, sourceUrlsIncluded: false, deviceIdentifierIncluded: false, automaticTelemetry: false },
      checks: {
        browserStorageAvailable: storageAvailable,
        currentStateSerializable: stateSerializable,
        lastKnownGoodSnapshotAvailable: lastKnownGood,
        webCryptoSha256Available: Boolean(window.crypto && window.crypto.subtle && typeof window.crypto.subtle.digest === 'function'),
        reducedMotionPreferred: prefersReducedMotion(),
        browserOnline: typeof navigator.onLine === 'boolean' ? navigator.onLine : null
      },
      counts: { projects: projects.length, objects: objectCount },
      approximateWorkspaceBytes: approximateBytes(currentRaw || state),
      schemaMigrationRequired: false
    };
  }

  function emergencyBackupPayload(state) {
    const snapshot = JSON.parse(JSON.stringify(state));
    snapshot.identity = { schema: IDENTITY_SCHEMA, session: 'portable-backup', persistenceMode: 'device-local', cloudSync: false, serverProjectStorage: false, updatedAt: nowIso() };
    (snapshot.projects || []).forEach(project => {
      project.persistence = { scope: 'device', syncState: 'local-only', accountEligible: true, serverStored: false };
    });
    return {
      schema: EMERGENCY_BACKUP_SCHEMA,
      workspaceVersion: rootVersion(),
      exportedAt: nowIso(),
      storageSchemaVersion: STORAGE_VERSION,
      projectSchema: PROJECT_SCHEMA,
      includesProjectContent: true,
      deviceIdentifierIncluded: false,
      automaticUpload: false,
      workspaceState: snapshot
    };
  }

  function escapeHtml(value){ return String(value||'').replace(/[&<>\"']/g,(c)=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c])); }

  function toolLabel(link) {
    const strong = link.querySelector('strong');
    return strong ? strong.textContent.trim() : link.dataset.scwTool;
  }

  function cloneProject(project) {
    const copy = normalizeProject(JSON.parse(JSON.stringify(project)));
    copy.id = id('scwp');
    copy.persistence = projectPersistenceTemplate();
    copy.title = `${project.title} (Copy)`.slice(0, 120);
    copy.pinned = false;
    copy.createdAt = nowIso();
    copy.updatedAt = copy.createdAt;
    copy.archivedAt = null;
    copy.activity = [];
    copy.activeObjectId = null;
    const objectMap = new Map();
    copy.objects = copy.objects.map((object) => {
      const oldId = object.id;
      const newId = id('scwo');
      objectMap.set(oldId, newId);
      return { ...object, id: newId, createdAt: copy.createdAt, updatedAt: copy.createdAt, archivedAt: null };
    });
    copy.research.questions = copy.research.questions.map((question) => ({ ...question, id: id('rq'), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.research.claims = copy.research.claims.map((claim) => ({ ...claim, id: id('rc'), evidenceObjectIds: claim.evidenceObjectIds.map((objectId) => objectMap.get(objectId)).filter(Boolean), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.research.readingQueue = copy.research.readingQueue.map((item) => ({ ...item, id: id('rr'), objectId: objectMap.get(item.objectId) || '', addedAt: copy.createdAt, updatedAt: copy.createdAt })).filter((item) => item.objectId);
    copy.research.evidenceLinks = copy.research.evidenceLinks.map((link) => ({ ...link, id: id('rel'), evidenceObjectId: objectMap.get(link.evidenceObjectId) || '', sourceObjectId: objectMap.get(link.sourceObjectId) || '', createdAt: copy.createdAt })).filter((link) => link.evidenceObjectId && link.sourceObjectId);
    copy.research.activeQuestionId = null;
    copy.research.activeClaimId = null;
    copy.research.createdAt = copy.createdAt;
    copy.research.updatedAt = copy.createdAt;

    copy.analysis.questions = copy.analysis.questions.map((question) => ({ ...question, id: id('aq'), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.variables = copy.analysis.variables.map((variable) => ({ ...variable, id: id('av'), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.assumptions = copy.analysis.assumptions.map((assumption) => ({ ...assumption, id: id('aa'), evidenceObjectIds: assumption.evidenceObjectIds.map((objectId)=>objectMap.get(objectId)).filter(Boolean), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.methods = copy.analysis.methods.map((method) => ({ ...method, id: id('am'), datasetObjectIds: method.datasetObjectIds.map((objectId)=>objectMap.get(objectId)).filter(Boolean), analysisObjectId: objectMap.get(method.analysisObjectId) || '', createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.comparisons = copy.analysis.comparisons.map((comparison) => ({ ...comparison, id: id('ac'), createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.findings = copy.analysis.findings.map((finding) => ({ ...finding, id: id('af'), evidenceObjectIds: finding.evidenceObjectIds.map((objectId)=>objectMap.get(objectId)).filter(Boolean), analysisObjectId: objectMap.get(finding.analysisObjectId) || '', createdAt: copy.createdAt, updatedAt: copy.createdAt }));
    copy.analysis.activeQuestionId = null; copy.analysis.activeMethodId = null; copy.analysis.createdAt = copy.createdAt; copy.analysis.updatedAt = copy.createdAt;
    const decisionMap = new Map(); copy.decision.decisions = copy.decision.decisions.map((record) => { const old=record.id, next=id('dr'); decisionMap.set(old,next); return {...record,id:next,decisionObjectId:objectMap.get(record.decisionObjectId)||'',selectedOptionId:'',status:record.status==='decided'?'revisit':record.status,decidedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt}; });
    const optionMap = new Map(); copy.decision.options = copy.decision.options.map((option)=>{const old=option.id,next=id('do');optionMap.set(old,next);return {...option,id:next,decisionId:decisionMap.get(option.decisionId)||'',evidenceObjectIds:option.evidenceObjectIds.map(v=>objectMap.get(v)).filter(Boolean),analysisObjectIds:option.analysisObjectIds.map(v=>objectMap.get(v)).filter(Boolean),createdAt:copy.createdAt,updatedAt:copy.createdAt};}).filter(x=>x.decisionId);
    const criterionMap = new Map(); copy.decision.criteria = copy.decision.criteria.map((criterion)=>{const old=criterion.id,next=id('dc');criterionMap.set(old,next);return {...criterion,id:next,decisionId:decisionMap.get(criterion.decisionId)||'',createdAt:copy.createdAt,updatedAt:copy.createdAt};}).filter(x=>x.decisionId);
    copy.decision.assessments = copy.decision.assessments.map((assessment)=>({...assessment,id:id('da'),decisionId:decisionMap.get(assessment.decisionId)||'',optionId:optionMap.get(assessment.optionId)||'',criterionId:criterionMap.get(assessment.criterionId)||'',createdAt:copy.createdAt,updatedAt:copy.createdAt})).filter(x=>x.decisionId&&x.optionId&&x.criterionId);
    copy.decision.risks = copy.decision.risks.map((risk)=>({...risk,id:id('dk'),decisionId:decisionMap.get(risk.decisionId)||'',optionId:optionMap.get(risk.optionId)||'',createdAt:copy.createdAt,updatedAt:copy.createdAt})).filter(x=>x.decisionId);
    copy.decision.activeDecisionId = null; copy.decision.createdAt=copy.createdAt; copy.decision.updatedAt=copy.createdAt;
    const boardMap = new Map();
    copy.canvas.boards = copy.canvas.boards.map((board) => { const oldId = board.id, next = id('cb'); boardMap.set(oldId, next); return { ...board, id: next, createdAt: copy.createdAt, updatedAt: copy.createdAt }; });
    const nodeMap = new Map();
    copy.canvas.nodes = copy.canvas.nodes.map((node) => { const oldId = node.id, next = id('cn'); nodeMap.set(oldId, next); return { ...node, id: next, boardId: boardMap.get(node.boardId) || '', objectId: objectMap.get(node.objectId) || '', createdAt: copy.createdAt, updatedAt: copy.createdAt }; }).filter((node) => node.boardId);
    copy.canvas.edges = copy.canvas.edges.map((edge) => ({ ...edge, id: id('ce'), boardId: boardMap.get(edge.boardId) || '', fromNodeId: nodeMap.get(edge.fromNodeId) || '', toNodeId: nodeMap.get(edge.toNodeId) || '', createdAt: copy.createdAt })).filter((edge) => edge.boardId && edge.fromNodeId && edge.toNodeId);
    copy.canvas.frames = copy.canvas.frames.map((frame) => ({ ...frame, id: id('cf'), boardId: boardMap.get(frame.boardId) || '', nodeIds: frame.nodeIds.map((nodeId) => nodeMap.get(nodeId)).filter(Boolean), createdAt: copy.createdAt, updatedAt: copy.createdAt })).filter((frame) => frame.boardId);
    copy.canvas.activeBoardId = null; copy.canvas.createdAt = copy.createdAt; copy.canvas.updatedAt = copy.createdAt;
    copy.traceability.evidenceAssessments = copy.traceability.evidenceAssessments.map((item)=>({...item,id:id('tea'),objectId:objectMap.get(item.objectId)||'',fingerprintState:'unverified',createdAt:copy.createdAt,updatedAt:copy.createdAt})).filter(item=>item.objectId);
    copy.traceability.lineage = copy.traceability.lineage.map((item)=>({...item,id:id('tl'),fromObjectId:objectMap.get(item.fromObjectId)||'',toObjectId:objectMap.get(item.toObjectId)||'',createdAt:copy.createdAt})).filter(item=>item.fromObjectId&&item.toObjectId&&item.fromObjectId!==item.toObjectId);
    copy.traceability.reproducibility = copy.traceability.reproducibility.map((item)=>({...item,id:id('trr'),analysisObjectId:objectMap.get(item.analysisObjectId)||'',datasetObjectIds:item.datasetObjectIds.map(v=>objectMap.get(v)).filter(Boolean),evidenceObjectIds:item.evidenceObjectIds.map(v=>objectMap.get(v)).filter(Boolean),resultObjectIds:item.resultObjectIds.map(v=>objectMap.get(v)).filter(Boolean),status:item.status==='verified'?'ready':item.status,lastVerifiedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt}));
    copy.traceability.createdAt=copy.createdAt; copy.traceability.updatedAt=copy.createdAt;

    const draftMap=new Map(); copy.briefing.drafts=copy.briefing.drafts.map((draft)=>{const old=draft.id,next=id('bd');draftMap.set(old,next);return {...draft,id:next,objectIds:draft.objectIds.map(v=>objectMap.get(v)).filter(Boolean),documentObjectId:objectMap.get(draft.documentObjectId)||'',sections:draft.sections.map(sec=>({...sec,id:id('bs'),objectIds:sec.objectIds.map(v=>objectMap.get(v)).filter(Boolean),createdAt:copy.createdAt,updatedAt:copy.createdAt})),status:draft.status==='exported'?'ready':draft.status,lastExportedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt};}); copy.briefing.activeDraftId=null; copy.briefing.createdAt=copy.createdAt; copy.briefing.updatedAt=copy.createdAt;
    copy.guidedWorkflows.runs = copy.guidedWorkflows.runs.map((run)=>({...run,id:id('wr'),currentStepId:null,status:run.status==='complete'?'paused':run.status,completedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt,steps:run.steps.map((step,index)=>({...step,id:id('ws'),status:index===0?'in-progress':step.status==='complete'?'todo':step.status,objectIds:step.objectIds.map(v=>objectMap.get(v)).filter(Boolean),completedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt}))}));
    copy.guidedWorkflows.runs.forEach(run=>{run.currentStepId=run.steps.find(x=>x.status==='in-progress')?.id||run.steps[0]?.id||null;});copy.guidedWorkflows.activeRunId=null;copy.guidedWorkflows.createdAt=copy.createdAt;copy.guidedWorkflows.updatedAt=copy.createdAt;
    copy.aiAssistance.sessions=copy.aiAssistance.sessions.map(session=>({...session,id:id('ai'),status:'prepared',objectIds:session.objectIds.map(v=>objectMap.get(v)).filter(Boolean),citationObjectIds:session.citationObjectIds.map(v=>objectMap.get(v)).filter(Boolean),acceptedDocumentObjectId:objectMap.get(session.acceptedDocumentObjectId)||'',sentAt:null,respondedAt:null,acceptedAt:null,createdAt:copy.createdAt,updatedAt:copy.createdAt}));copy.aiAssistance.activeSessionId=null;copy.aiAssistance.createdAt=copy.createdAt;copy.aiAssistance.updatedAt=copy.createdAt;
    copy.handoffs = handoffLedgerTemplate();
    addActivity(copy, 'duplicated', `Duplicated from ${project.title}`);
    return copy;
  }

  function versionHistorySnapshot(project){const snapshot=normalizeProject(JSON.parse(JSON.stringify(project)));snapshot.persistence=projectPersistenceTemplate();return snapshot;}
  function restorePointExport(point){return {schema:RESTORE_POINT_SCHEMA,workspaceVersion:rootVersion(),exportedAt:nowIso(),integrity:{algorithm:'SHA-256',projectFingerprint:point.fingerprint},metadata:{id:point.id,projectId:point.projectId,projectTitle:point.projectTitle,label:point.label,note:point.note,createdAt:point.createdAt,projectUpdatedAt:point.projectUpdatedAt,source:point.source},project:JSON.parse(JSON.stringify(point.snapshot)),transport:{automaticUpload:false,restoreMode:'new-local-copy'}};}

  function init(root) {
    if (root.dataset.scwReady === '1') return;
    root.dataset.scwReady = '1';

    let state = readState();
    let activeProjectMode = 'overview';
    let workspaceView = 'projects';
    let stagedInteroperability = null;
    let selectedKnowledgeKey = null;
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
    const identityBadge = root.querySelector('[data-scw-identity-badge]');
    const identityHeading = root.querySelector('[data-scw-identity-heading]');
    const identityDetail = root.querySelector('[data-scw-identity-detail]');
    const identityAccess = root.querySelector('[data-scw-identity-access]');
    const identityNote = root.querySelector('[data-scw-identity-note]');
    const cloudBadge = root.querySelector('[data-scw-cloud-badge]');
    const cloudProject = root.querySelector('[data-scw-cloud-project]');
    const cloudBackupButton = root.querySelector('[data-scw-cloud-backup]');
    const cloudRefreshButton = root.querySelector('[data-scw-cloud-refresh]');
    const cloudStatus = root.querySelector('[data-scw-cloud-status]');
    const cloudList = root.querySelector('[data-scw-cloud-list]');
    const syncBadge = root.querySelector('[data-scw-sync-badge]');
    const syncProject = root.querySelector('[data-scw-sync-project]');
    const syncToggleButton = root.querySelector('[data-scw-sync-toggle]');
    const syncCheckButton = root.querySelector('[data-scw-sync-check]');
    const syncNowButton = root.querySelector('[data-scw-sync-now]');
    const syncStatus = root.querySelector('[data-scw-sync-status]');
    const syncLocal = root.querySelector('[data-scw-sync-local]');
    const syncRemote = root.querySelector('[data-scw-sync-remote]');
    const syncBaseline = root.querySelector('[data-scw-sync-baseline]');
    const syncStateEl = root.querySelector('[data-scw-sync-state]');
    const syncRemoteCopyButton = root.querySelector('[data-scw-sync-remote-copy]');
    const syncResolveLocalButton = root.querySelector('[data-scw-sync-resolve-local]');
    const syncResolveCloudButton = root.querySelector('[data-scw-sync-resolve-cloud]');
    const deviceIdEl = root.querySelector('[data-scw-device-id]');
    const loginLink = root.querySelector('[data-scw-login]');
    const registerLink = root.querySelector('[data-scw-register]');
    const logoutLink = root.querySelector('[data-scw-logout]');
    const readinessBadge = root.querySelector('[data-scw-readiness-badge]');
    const readinessStorage = root.querySelector('[data-scw-readiness-storage]');
    const readinessRecovery = root.querySelector('[data-scw-readiness-recovery]');
    const readinessCrypto = root.querySelector('[data-scw-readiness-crypto]');
    const readinessSize = root.querySelector('[data-scw-readiness-size]');
    const readinessStatus = root.querySelector('[data-scw-readiness-status]');
    const runDiagnostics = root.querySelector('[data-scw-run-diagnostics]');
    const exportDiagnostics = root.querySelector('[data-scw-export-diagnostics]');
    const emergencyBackup = root.querySelector('[data-scw-emergency-backup]');
    let latestDiagnosticReport = null;

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

    const researchQuestionForm = root.querySelector('[data-scw-research-question-form]');
    const researchQuestionList = root.querySelector('[data-scw-research-question-list]');
    const researchActiveQuestion = root.querySelector('[data-scw-research-active-question]');
    const researchSourceForm = root.querySelector('[data-scw-research-source-form]');
    const researchReadingList = root.querySelector('[data-scw-research-reading-list]');
    const researchEvidenceForm = root.querySelector('[data-scw-research-evidence-form]');
    const researchEvidenceSource = root.querySelector('[data-scw-research-evidence-source]');
    const researchClaimForm = root.querySelector('[data-scw-research-claim-form]');
    const researchClaimList = root.querySelector('[data-scw-research-claim-list]');
    const researchClaimEvidence = root.querySelector('[data-scw-research-claim-evidence]');
    const researchMetricQuestions = root.querySelector('[data-scw-research-metric-questions]');
    const researchMetricSources = root.querySelector('[data-scw-research-metric-sources]');
    const researchMetricEvidence = root.querySelector('[data-scw-research-metric-evidence]');
    const researchMetricClaims = root.querySelector('[data-scw-research-metric-claims]');


    const analysisQuestionForm = root.querySelector('[data-scw-analysis-question-form]');
    const analysisQuestionList = root.querySelector('[data-scw-analysis-question-list]');
    const analysisActiveQuestion = root.querySelector('[data-scw-analysis-active-question]');
    const analysisDatasetForm = root.querySelector('[data-scw-analysis-dataset-form]');
    const analysisDatasetList = root.querySelector('[data-scw-analysis-dataset-list]');
    const analysisVariableForm = root.querySelector('[data-scw-analysis-variable-form]');
    const analysisVariableList = root.querySelector('[data-scw-analysis-variable-list]');
    const analysisAssumptionForm = root.querySelector('[data-scw-analysis-assumption-form]');
    const analysisAssumptionList = root.querySelector('[data-scw-analysis-assumption-list]');
    const analysisMethodForm = root.querySelector('[data-scw-analysis-method-form]');
    const analysisMethodDataset = root.querySelector('[data-scw-analysis-method-dataset]');
    const analysisMethodList = root.querySelector('[data-scw-analysis-method-list]');
    const analysisComparisonForm = root.querySelector('[data-scw-analysis-comparison-form]');
    const analysisComparisonList = root.querySelector('[data-scw-analysis-comparison-list]');
    const analysisFindingForm = root.querySelector('[data-scw-analysis-finding-form]');
    const analysisFindingEvidence = root.querySelector('[data-scw-analysis-finding-evidence]');
    const analysisFindingList = root.querySelector('[data-scw-analysis-finding-list]');
    const analysisMetricQuestions = root.querySelector('[data-scw-analysis-metric-questions]');
    const analysisMetricDatasets = root.querySelector('[data-scw-analysis-metric-datasets]');
    const analysisMetricAnalyses = root.querySelector('[data-scw-analysis-metric-analyses]');
    const analysisMetricFindings = root.querySelector('[data-scw-analysis-metric-findings]');

    const decisionForm = root.querySelector('[data-scw-decision-form]');
    const decisionList = root.querySelector('[data-scw-decision-list]');
    const decisionActive = root.querySelector('[data-scw-decision-active]');
    const decisionOptionForm = root.querySelector('[data-scw-decision-option-form]');
    const decisionOptionList = root.querySelector('[data-scw-decision-option-list]');
    const decisionCriterionForm = root.querySelector('[data-scw-decision-criterion-form]');
    const decisionCriterionList = root.querySelector('[data-scw-decision-criterion-list]');
    const decisionAssessmentForm = root.querySelector('[data-scw-decision-assessment-form]');
    const decisionAssessmentOption = root.querySelector('[data-scw-decision-assessment-option]');
    const decisionAssessmentCriterion = root.querySelector('[data-scw-decision-assessment-criterion]');
    const decisionAssessmentList = root.querySelector('[data-scw-decision-assessment-list]');
    const decisionRiskForm = root.querySelector('[data-scw-decision-risk-form]');
    const decisionRiskList = root.querySelector('[data-scw-decision-risk-list]');
    const decisionFinalForm = root.querySelector('[data-scw-decision-final-form]');
    const decisionFinalOption = root.querySelector('[data-scw-decision-final-option]');
    const decisionSummary = root.querySelector('[data-scw-decision-summary]');
    const decisionMetricOpen = root.querySelector('[data-scw-decision-metric-open]');
    const decisionMetricOptions = root.querySelector('[data-scw-decision-metric-options]');
    const decisionMetricCriteria = root.querySelector('[data-scw-decision-metric-criteria]');
    const decisionMetricDecided = root.querySelector('[data-scw-decision-metric-decided]');

    const canvasBoardForm = root.querySelector('[data-scw-canvas-board-form]');
    const canvasBoardList = root.querySelector('[data-scw-canvas-board-list]');
    const canvasActive = root.querySelector('[data-scw-canvas-active]');
    const canvasSurface = root.querySelector('[data-scw-canvas-surface]');
    const canvasLines = root.querySelector('[data-scw-canvas-lines]');
    const canvasSurfaceEmpty = root.querySelector('[data-scw-canvas-surface-empty]');
    const canvasNodeForm = root.querySelector('[data-scw-canvas-node-form]');
    const canvasNodeObject = root.querySelector('[data-scw-canvas-node-object]');
    const canvasEdgeForm = root.querySelector('[data-scw-canvas-edge-form]');
    const canvasEdgeFrom = root.querySelector('[data-scw-canvas-edge-from]');
    const canvasEdgeTo = root.querySelector('[data-scw-canvas-edge-to]');
    const canvasEdgeList = root.querySelector('[data-scw-canvas-edge-list]');
    const canvasFrameForm = root.querySelector('[data-scw-canvas-frame-form]');
    const canvasFrameNodes = root.querySelector('[data-scw-canvas-frame-nodes]');
    const canvasFrameList = root.querySelector('[data-scw-canvas-frame-list]');
    const canvasSynthesis = root.querySelector('[data-scw-canvas-synthesis]');
    const canvasMetricBoards = root.querySelector('[data-scw-canvas-metric-boards]');
    const canvasMetricNodes = root.querySelector('[data-scw-canvas-metric-nodes]');
    const canvasMetricEdges = root.querySelector('[data-scw-canvas-metric-edges]');
    const canvasMetricFrames = root.querySelector('[data-scw-canvas-metric-frames]');
    const traceEvidenceForm = root.querySelector('[data-scw-evidence-assessment-form]');
    const traceEvidenceObject = root.querySelector('[data-scw-trace-evidence-object]');
    const traceEvidenceList = root.querySelector('[data-scw-evidence-assessment-list]');
    const traceLineageForm = root.querySelector('[data-scw-lineage-form]');
    const traceLineageFrom = root.querySelector('[data-scw-lineage-from]');
    const traceLineageTo = root.querySelector('[data-scw-lineage-to]');
    const traceLineageList = root.querySelector('[data-scw-lineage-list]');
    const traceReproForm = root.querySelector('[data-scw-repro-form]');
    const traceReproAnalysis = root.querySelector('[data-scw-repro-analysis]');
    const traceReproDatasets = root.querySelector('[data-scw-repro-datasets]');
    const traceReproEvidence = root.querySelector('[data-scw-repro-evidence]');
    const traceReproList = root.querySelector('[data-scw-repro-list]');
    const traceMetricAssessments = root.querySelector('[data-scw-trace-metric-assessments]');
    const traceMetricLineage = root.querySelector('[data-scw-trace-metric-lineage]');
    const traceMetricRepro = root.querySelector('[data-scw-trace-metric-repro]');
    const traceMetricVerified = root.querySelector('[data-scw-trace-metric-verified]');
    const traceExportButton = root.querySelector('[data-scw-traceability-export]');

    const aiRequestForm = root.querySelector('[data-scw-ai-request-form]');
    const aiSessionList = root.querySelector('[data-scw-ai-session-list]');
    const aiActive = root.querySelector('[data-scw-ai-active]');
    const aiObjectSelect = root.querySelector('[data-scw-ai-object-select]');
    const aiResponse = root.querySelector('[data-scw-ai-response]');
    const aiCitationSelect = root.querySelector('[data-scw-ai-citation-select]');
    const aiResponseSource = root.querySelector('[data-scw-ai-response-source]');
    const aiSaveResponse = root.querySelector('[data-scw-ai-save-response]');
    const aiCopyPrompt = root.querySelector('[data-scw-ai-copy-prompt]');
    const aiExportRequest = root.querySelector('[data-scw-ai-export-request]');
    const aiOpenLibrarian = root.querySelector('[data-scw-ai-open-librarian]');
    const aiAcceptDocument = root.querySelector('[data-scw-ai-accept-document]');
    const aiReject = root.querySelector('[data-scw-ai-reject]');
    const aiExportResponse = root.querySelector('[data-scw-ai-export-response]');
    const aiGrounding = root.querySelector('[data-scw-ai-grounding]');
    const aiMetricSessions = root.querySelector('[data-scw-ai-metric-sessions]');
    const aiMetricGrounding = root.querySelector('[data-scw-ai-metric-grounding]');
    const aiMetricResponses = root.querySelector('[data-scw-ai-metric-responses]');
    const aiMetricAccepted = root.querySelector('[data-scw-ai-metric-accepted]');
    const briefingDraftForm = root.querySelector('[data-scw-briefing-draft-form]');
    const briefingDraftList = root.querySelector('[data-scw-briefing-draft-list]');
    const briefingActive = root.querySelector('[data-scw-briefing-active]');
    const briefingObjectSelect = root.querySelector('[data-scw-briefing-object-select]');
    const briefingSaveBasis = root.querySelector('[data-scw-briefing-save-basis]');
    const briefingBasisList = root.querySelector('[data-scw-briefing-basis-list]');
    const briefingOutlineButton = root.querySelector('[data-scw-briefing-outline]');
    const briefingStatus = root.querySelector('[data-scw-briefing-status]');
    const briefingSectionForm = root.querySelector('[data-scw-briefing-section-form]');
    const briefingSectionList = root.querySelector('[data-scw-briefing-section-list]');
    const briefingMaterialize = root.querySelector('[data-scw-briefing-materialize]');
    const briefingExportMarkdown = root.querySelector('[data-scw-briefing-export-markdown]');
    const briefingExportHtml = root.querySelector('[data-scw-briefing-export-html]');
    const briefingExportPackage = root.querySelector('[data-scw-briefing-export-package]');
    const briefingMetricDrafts = root.querySelector('[data-scw-briefing-metric-drafts]');
    const briefingMetricReady = root.querySelector('[data-scw-briefing-metric-ready]');
    const briefingMetricRefs = root.querySelector('[data-scw-briefing-metric-refs]');
    const briefingMetricDocs = root.querySelector('[data-scw-briefing-metric-docs]');
    const workflowTemplateList = root.querySelector('[data-scw-workflow-template-list]');
    const workflowRunList = root.querySelector('[data-scw-workflow-run-list]');
    const workflowActive = root.querySelector('[data-scw-workflow-active]');
    const workflowStepList = root.querySelector('[data-scw-workflow-step-list]');
    const workflowMetricRuns = root.querySelector('[data-scw-workflow-metric-runs]');
    const workflowMetricSteps = root.querySelector('[data-scw-workflow-metric-steps]');
    const workflowMetricComplete = root.querySelector('[data-scw-workflow-metric-complete]');
    const workspaceViewNav = root.querySelector('[data-scw-workspace-view-nav]');
    const projectsSection = root.querySelector('[data-scw-workspace-section="projects"]');
    const knowledgeSection = root.querySelector('[data-scw-workspace-section="knowledge"]');
    const graphSection = root.querySelector('[data-scw-workspace-section="graph"]');
    const activityIntelligenceSection = root.querySelector('[data-scw-workspace-section="activity"]');
    const interoperabilitySection = root.querySelector('[data-scw-workspace-section="interoperability"]');
    const shareSection = root.querySelector('[data-scw-workspace-section="share"]');
    const versionHistorySection = root.querySelector('[data-scw-workspace-section="history"]');
    const historyForm = root.querySelector('[data-scw-history-form]');
    const historyProject = root.querySelector('[data-scw-history-project]');
    const historyFilter = root.querySelector('[data-scw-history-filter]');
    const historyList = root.querySelector('[data-scw-history-list]');
    const historyEvents = root.querySelector('[data-scw-history-events]');
    const historyStatus = root.querySelector('[data-scw-history-status]');
    const historyMetricPoints = root.querySelector('[data-scw-history-metric-points]');
    const historyMetricProjects = root.querySelector('[data-scw-history-metric-projects]');
    const historyMetricBytes = root.querySelector('[data-scw-history-metric-bytes]');
    const historyMetricNewest = root.querySelector('[data-scw-history-metric-newest]');
    const changeReviewSection = root.querySelector('[data-scw-workspace-section="changes"]');
    const changeProject = root.querySelector('[data-scw-change-project]');
    const changeBase = root.querySelector('[data-scw-change-base]');
    const changeTarget = root.querySelector('[data-scw-change-target]');
    const changeRun = root.querySelector('[data-scw-change-run]');
    const changeExport = root.querySelector('[data-scw-change-export]');
    const changeStatus = root.querySelector('[data-scw-change-status]');
    const changeAdded = root.querySelector('[data-scw-change-added]');
    const changeRemoved = root.querySelector('[data-scw-change-removed]');
    const changeModified = root.querySelector('[data-scw-change-modified]');
    const changeRelationships = root.querySelector('[data-scw-change-relationships]');
    const changeAttention = root.querySelector('[data-scw-change-attention]');
    const changeResults = root.querySelector('[data-scw-change-results]');
    let activeChangeReview = null;
    const safeActionsSection = root.querySelector('[data-scw-workspace-section="safety"]');
    const safeHistory = root.querySelector('[data-scw-safe-history]');
    const safeMetricTotal = root.querySelector('[data-scw-safe-metric-total]');
    const safeMetricProceeded = root.querySelector('[data-scw-safe-metric-proceeded]');
    const safeMetricCancelled = root.querySelector('[data-scw-safe-metric-cancelled]');
    const safeMetricChanges = root.querySelector('[data-scw-safe-metric-changes]');
    const actionGate = root.querySelector('[data-scw-action-gate]');
    const actionGateTitle = root.querySelector('[data-scw-action-gate-title]');
    const actionGateIntro = root.querySelector('[data-scw-action-gate-intro]');
    const actionGateReview = root.querySelector('[data-scw-action-gate-review]');
    const actionGateAck = root.querySelector('[data-scw-action-gate-ack]');
    const actionGateAckText = root.querySelector('[data-scw-action-gate-ack-text]');
    const actionGateProceed = root.querySelector('[data-scw-action-gate-proceed]');
    const actionGateStatus = root.querySelector('[data-scw-action-gate-status]');
    let activeSafeGate = null;
    let activeSafeAction = null;
    const collaborationSection = root.querySelector('[data-scw-workspace-section="collaboration"]');
    const collabProfileForm = root.querySelector('[data-scw-collab-profile-form]');
    const collabRequestForm = root.querySelector('[data-scw-collab-request-form]');
    const collabProject = root.querySelector('[data-scw-collab-project]');
    const collabSessionList = root.querySelector('[data-scw-collab-session-list]');
    const collabActive = root.querySelector('[data-scw-collab-active]');
    const collabThreadForm = root.querySelector('[data-scw-collab-thread-form]');
    const collabObject = root.querySelector('[data-scw-collab-object]');
    const collabThreadList = root.querySelector('[data-scw-collab-thread-list]');
    const collabExportRequest = root.querySelector('[data-scw-collab-export-request]');
    const collabExportResponse = root.querySelector('[data-scw-collab-export-response]');
    const collabImport = root.querySelector('[data-scw-collab-import]');
    const collabFile = root.querySelector('[data-scw-collab-file]');
    const collabStage = root.querySelector('[data-scw-collab-stage]');
    const collabCommit = root.querySelector('[data-scw-collab-commit]');
    const collabClear = root.querySelector('[data-scw-collab-clear]');
    const collabHistory = root.querySelector('[data-scw-collab-history]');
    const collabMetricSessions = root.querySelector('[data-scw-collab-metric-sessions]');
    const collabMetricOpen = root.querySelector('[data-scw-collab-metric-open]');
    const collabMetricPeople = root.querySelector('[data-scw-collab-metric-people]');
    const collabMetricResponses = root.querySelector('[data-scw-collab-metric-responses]');
    let stagedReviewPackage = null;
    const institutionalSection = root.querySelector('[data-scw-workspace-section="institutional"]');
    const institutionalForm = root.querySelector('[data-scw-institutional-form]');
    const institutionalProject = root.querySelector('[data-scw-institutional-project]');
    const institutionalObjectScope = root.querySelector('[data-scw-institutional-object-scope]');
    const institutionalList = root.querySelector('[data-scw-institutional-list]');
    const institutionalActive = root.querySelector('[data-scw-institutional-active]');
    const institutionalReadinessEl = root.querySelector('[data-scw-institutional-readiness]');
    const institutionalExport = root.querySelector('[data-scw-institutional-export]');
    const institutionalClose = root.querySelector('[data-scw-institutional-close]');
    const institutionalImport = root.querySelector('[data-scw-institutional-import]');
    const institutionalFile = root.querySelector('[data-scw-institutional-file]');
    const institutionalStage = root.querySelector('[data-scw-institutional-stage]');
    const institutionalCommit = root.querySelector('[data-scw-institutional-commit]');
    const institutionalClear = root.querySelector('[data-scw-institutional-clear]');
    const institutionalHistory = root.querySelector('[data-scw-institutional-history]');
    const institutionalMetricTotal = root.querySelector('[data-scw-institutional-metric-total]');
    const institutionalMetricExported = root.querySelector('[data-scw-institutional-metric-exported]');
    const institutionalMetricReceived = root.querySelector('[data-scw-institutional-metric-received]');
    const institutionalMetricAccepted = root.querySelector('[data-scw-institutional-metric-accepted]');
    let stagedInstitutionalReceipt = null;
    const activityProject = root.querySelector('[data-scw-activity-project]');
    const activityWindow = root.querySelector('[data-scw-activity-window]');
    const activityStale = root.querySelector('[data-scw-activity-stale]');
    const activitySignal = root.querySelector('[data-scw-activity-signal]');
    const activityMetricProjects = root.querySelector('[data-scw-activity-metric-projects]');
    const activityMetricActions = root.querySelector('[data-scw-activity-metric-actions]');
    const activityMetricSignals = root.querySelector('[data-scw-activity-metric-signals]');
    const activityMetricChanges = root.querySelector('[data-scw-activity-metric-changes]');
    const nextActionForm = root.querySelector('[data-scw-next-action-form]');
    const nextActionProject = root.querySelector('[data-scw-next-action-project]');
    const nextActionList = root.querySelector('[data-scw-next-action-list]');
    const attentionList = root.querySelector('[data-scw-attention-list]');
    const workflowIntelligenceList = root.querySelector('[data-scw-workflow-intelligence-list]');
    const workspaceActivityTimelineEl = root.querySelector('[data-scw-workspace-activity-timeline]');
    const restoreDismissedSignals = root.querySelector('[data-scw-activity-restore-dismissed]');
    const interoperabilityForm = root.querySelector('[data-scw-interoperability-form]');
    const interoperabilityProject = root.querySelector('[data-scw-interoperability-project]');
    const interoperabilityFile = root.querySelector('[data-scw-interoperability-file]');
    const interoperabilityStage = root.querySelector('[data-scw-interoperability-stage]');
    const interoperabilityCommit = root.querySelector('[data-scw-interoperability-commit]');
    const interoperabilityClear = root.querySelector('[data-scw-interoperability-clear]');
    const interoperabilityExportProject = root.querySelector('[data-scw-interoperability-export-project]');
    const interoperabilityExport = root.querySelector('[data-scw-interoperability-export]');
    const interoperabilityHistory = root.querySelector('[data-scw-interoperability-history]');
    const shareProject = root.querySelector('[data-scw-share-project]');
    const shareIncludeArchived = root.querySelector('[data-scw-share-include-archived]');
    const shareIncludeActivity = root.querySelector('[data-scw-share-include-activity]');
    const shareIncludeAi = root.querySelector('[data-scw-share-include-ai]');
    const shareExport = root.querySelector('[data-scw-share-export]');
    const shareReview = root.querySelector('[data-scw-share-review]');
    const shareFile = root.querySelector('[data-scw-share-file]');
    const shareStage = root.querySelector('[data-scw-share-stage]');
    const shareImport = root.querySelector('[data-scw-share-import]');
    const shareClear = root.querySelector('[data-scw-share-clear]');
    const shareHistory = root.querySelector('[data-scw-share-history]');
    let stagedPortableProject = null;
    const knowledgeSearch = root.querySelector('[data-scw-knowledge-search]');
    const knowledgeType = root.querySelector('[data-scw-knowledge-type]');
    const knowledgeProject = root.querySelector('[data-scw-knowledge-project]');
    const knowledgeTag = root.querySelector('[data-scw-knowledge-tag]');
    const knowledgeScope = root.querySelector('[data-scw-knowledge-scope]');
    const knowledgeResults = root.querySelector('[data-scw-knowledge-results]');
    const knowledgeEmpty = root.querySelector('[data-scw-knowledge-empty]');
    const knowledgeDetail = root.querySelector('[data-scw-knowledge-detail]');
    const knowledgeCollectionForm = root.querySelector('[data-scw-knowledge-collection-form]');
    const knowledgeCollectionList = root.querySelector('[data-scw-knowledge-collection-list]');
    const knowledgeCollectionDetail = root.querySelector('[data-scw-knowledge-collection-detail]');
    const knowledgeCollectionSelect = root.querySelector('[data-scw-knowledge-collection-select]');
    const knowledgeMetricObjects = root.querySelector('[data-scw-knowledge-metric-objects]');
    const knowledgeMetricProjects = root.querySelector('[data-scw-knowledge-metric-projects]');
    const knowledgeMetricCollections = root.querySelector('[data-scw-knowledge-metric-collections]');
    const knowledgeMetricTags = root.querySelector('[data-scw-knowledge-metric-tags]');
    const graphSearch = root.querySelector('[data-scw-graph-search]');
    const graphNodeType = root.querySelector('[data-scw-graph-node-type]');
    const graphRelation = root.querySelector('[data-scw-graph-relation]');
    const graphProject = root.querySelector('[data-scw-graph-project]');
    const graphScope = root.querySelector('[data-scw-graph-scope]');
    const graphDepth = root.querySelector('[data-scw-graph-depth]');
    const graphResults = root.querySelector('[data-scw-graph-results]');
    const graphDetail = root.querySelector('[data-scw-graph-detail]');
    const graphRelations = root.querySelector('[data-scw-graph-relations]');
    const graphSvg = root.querySelector('[data-scw-graph-svg]');
    const graphMetricNodes = root.querySelector('[data-scw-graph-metric-nodes]');
    const graphMetricEdges = root.querySelector('[data-scw-graph-metric-edges]');
    const graphMetricProjects = root.querySelector('[data-scw-graph-metric-projects]');
    const graphMetricProvenance = root.querySelector('[data-scw-graph-metric-provenance]');
    const connectionsDrawer = root.querySelector('.scw-connections-drawer');
    const handoffList = root.querySelector('[data-scw-handoff-list]');
    const handoffEmpty = root.querySelector('[data-scw-handoff-empty]');
    const handoffImportFile = root.querySelector('[data-scw-handoff-import-file]');
    const handoffMetricLaunched = root.querySelector('[data-scw-handoff-metric-launched]');
    const handoffMetricReturned = root.querySelector('[data-scw-handoff-metric-returned]');
    const handoffMetricObjects = root.querySelector('[data-scw-handoff-metric-objects]');
    const handoffMetricClosed = root.querySelector('[data-scw-handoff-metric-closed]');


    function renderIdentity() {
      const authenticated = Boolean(IDENTITY_CONFIG.authenticated);
      state.identity = normalizeIdentity(state.identity);
      if (identityBadge) identityBadge.textContent = authenticated ? 'SIGNED IN' : 'GUEST';
      if (identityHeading) identityHeading.textContent = authenticated ? (String(IDENTITY_CONFIG.displayName || 'Workspace account')) : 'Guest Workspace';
      if (identityDetail) identityDetail.textContent = authenticated ? 'Account recognized. Local storage remains primary; manual recovery and explicit project sync are available.' : 'Your work is associated only with this browser device.';
      if (identityAccess) identityAccess.textContent = authenticated ? 'Account recognized · backup + explicit sync' : 'No account required';
      if (identityNote) identityNote.textContent = authenticated ? 'You are signed in. Workspace stays local first; use Back up now for recovery or explicitly enroll a project for conflict-safe cross-device sync. Nothing synchronizes in the background.' : 'Sign in only if you want account recovery or explicit cross-device sync. Local Workspace remains fully available without an account.';
      if (deviceIdEl) deviceIdEl.textContent = state.identity.deviceId;
      if (loginLink) { loginLink.hidden = authenticated; loginLink.href = String(IDENTITY_CONFIG.loginUrl || '#'); }
      if (logoutLink) { logoutLink.hidden = !authenticated; logoutLink.href = String(IDENTITY_CONFIG.logoutUrl || '#'); }
      if (registerLink) {
        registerLink.hidden = authenticated || !IDENTITY_CONFIG.registrationEnabled;
        registerLink.href = String(IDENTITY_CONFIG.registrationUrl || '#');
      }
    }

    function cloudRestUrl(path = '') {
      const base = String(IDENTITY_CONFIG.restRoot || '').replace(/\/+$/, '');
      return `${base}/${String(path || '').replace(/^\/+/, '')}`;
    }

    async function cloudRequest(path, options = {}) {
      if (!IDENTITY_CONFIG.authenticated || !IDENTITY_CONFIG.restNonce) throw new Error('Sign in to use cloud recovery.');
      const headers = { 'X-WP-Nonce': String(IDENTITY_CONFIG.restNonce), ...(options.headers || {}) };
      if (options.body && !headers['Content-Type']) headers['Content-Type'] = 'application/json';
      const response = await fetch(cloudRestUrl(path), { credentials: 'same-origin', ...options, headers });
      let data = null;
      try { data = await response.json(); } catch (_) {}
      if (!response.ok) throw new Error(String(data?.message || `Cloud recovery request failed (${response.status}).`));
      return data;
    }

    function touchAccountPersistence(action, project = null) {
      state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
      if (action) state.accountPersistence.history.unshift({ id: id('aph'), action, projectId: project?.id || '', projectTitle: project?.title || '', at: nowIso() });
      state.accountPersistence.history = state.accountPersistence.history.slice(0, MAX_ACCOUNT_HISTORY);
      state.accountPersistence.updatedAt = nowIso();
    }

    function cloudBackupPayload(project) {
      const copy = JSON.parse(JSON.stringify(project));
      copy.persistence = { scope: 'account-backup-copy', syncState: 'manual-backup', accountEligible: true, serverStored: true };
      return {
        schema: CLOUD_BACKUP_SCHEMA,
        workspaceVersion: rootVersion(),
        createdAt: nowIso(),
        sourceProjectId: project.id,
        projectTitle: project.title,
        clientUpdatedAt: project.updatedAt,
        privacy: { deviceIdentityIncluded: false, accountProfileIncluded: false, recentToolsIncluded: false },
        transport: { automaticUpload: false, backgroundSync: false, restoreMode: 'new-local-copy' },
        project: copy,
      };
    }

    function syncProjectSnapshot(project) {
      const copy = JSON.parse(JSON.stringify(project));
      copy.persistence = { scope: 'account-sync-copy', syncState: 'sync-head', accountEligible: true, serverStored: true };
      copy.recentTools = [];
      return copy;
    }

    async function syncProjectFingerprint(project) {
      return sha256Text(JSON.stringify(syncProjectSnapshot(project)));
    }

    function syncEnrollment(projectId, create = false) {
      state.crossDeviceSync = normalizeCrossDeviceSync(state.crossDeviceSync, state.projects);
      let enrollment = state.crossDeviceSync.enrollments.find(item => item.projectId === projectId) || null;
      if (!enrollment && create && state.crossDeviceSync.enrollments.length < MAX_SYNC_ENROLLMENTS) {
        enrollment = { projectId, enabled: false, serverRevision: 0, lastSyncedFingerprint: '', remoteFingerprint: '', remoteRevision: 0, status: 'disabled', lastCheckedAt: null, lastSyncedAt: null, updatedAt: nowIso() };
        state.crossDeviceSync.enrollments.push(enrollment);
      }
      return enrollment;
    }

    function recordSync(action, project, revision = 0) {
      state.crossDeviceSync = normalizeCrossDeviceSync(state.crossDeviceSync, state.projects);
      state.crossDeviceSync.history.unshift({ id: id('syh'), action, projectId: project?.id || '', projectTitle: project?.title || '', revision: Math.max(0, Number(revision) || 0), at: nowIso() });
      state.crossDeviceSync.history = state.crossDeviceSync.history.slice(0, MAX_SYNC_HISTORY);
      state.crossDeviceSync.updatedAt = nowIso();
    }

    function syncPushPayload(project, enrollment, expectedRevision) {
      return { schema: SYNC_PUSH_SCHEMA, workspaceVersion: rootVersion(), createdAt: nowIso(), sourceProjectId: project.id, projectTitle: project.title, clientUpdatedAt: project.updatedAt, expectedRevision: Math.max(0, Number(expectedRevision) || 0), privacy: { deviceIdentityIncluded: false, accountProfileIncluded: false, recentToolsIncluded: false }, transport: { automaticUpload: false, backgroundSync: false, explicitEnrollment: true, conflictStrategy: 'revision-precondition' }, project: syncProjectSnapshot(project) };
    }

    function remoteCloudRecord(projectId) {
      state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
      return state.accountPersistence.cloudRecords.find(record => record.projectId === projectId) || null;
    }

    async function refreshCloudIndexForSync() {
      const data = await cloudRequest('cloud-projects');
      state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
      state.accountPersistence.cloudRecords = Array.isArray(data?.items) ? data.items : [];
      state.accountPersistence.lastRefreshAt = nowIso();
      return state.accountPersistence.cloudRecords;
    }

    function syncStatusMessage(status, remote = null) {
      const revision = remote?.revision ? ` Cloud revision ${remote.revision}.` : '';
      return ({ disabled:'Sync is off for this project.', 'not-uploaded':'Sync is enabled locally. No cloud sync head exists yet; Sync now will create the first revision.', 'up-to-date':`Local and cloud fingerprints match.${revision}`, 'local-ahead':`Local work has changed since the last synchronized revision.${revision}`, 'remote-ahead':`A newer cloud revision exists and this local project has no competing local changes.${revision}`, conflict:`Both local and cloud state have changed since the last common revision. Workspace will not overwrite either copy automatically.${revision}`, 'remote-missing':'The previously synchronized cloud head is missing. Workspace will not recreate it without confirmation.', error:'Sync status could not be determined.' })[status] || 'Sync status is unknown.';
    }

    async function evaluateSync(project, refreshRemote = true) {
      if (!project) return { status:'error', message:'Choose a local project.' };
      const enrollment = syncEnrollment(project.id, true);
      if (!enrollment?.enabled) return { status:'disabled', enrollment, message:'Cross-device sync is not enabled for this project.' };
      if (refreshRemote) await refreshCloudIndexForSync();
      const localFingerprint = await syncProjectFingerprint(project);
      if (!localFingerprint) return { status:'error', enrollment, message:'This browser cannot calculate the SHA-256 project fingerprint required for safe synchronization.' };
      const remote = remoteCloudRecord(project.id);
      enrollment.lastCheckedAt = nowIso(); enrollment.remoteRevision = remote ? remote.revision : 0; enrollment.remoteFingerprint = remote ? remote.projectFingerprint : '';
      let status='up-to-date';
      if (!remote) status=enrollment.serverRevision>0?'remote-missing':'not-uploaded';
      else if (enrollment.serverRevision===0) { if(remote.projectFingerprint&&remote.projectFingerprint===localFingerprint){enrollment.serverRevision=remote.revision;enrollment.lastSyncedFingerprint=localFingerprint;enrollment.lastSyncedAt=nowIso();status='up-to-date';} else status='conflict'; }
      else if (remote.revision===enrollment.serverRevision) status=localFingerprint===enrollment.lastSyncedFingerprint?'up-to-date':'local-ahead';
      else if (remote.revision>enrollment.serverRevision) status=localFingerprint===enrollment.lastSyncedFingerprint?'remote-ahead':'conflict';
      else status='conflict';
      enrollment.status=status; enrollment.updatedAt=nowIso(); state.crossDeviceSync.updatedAt=enrollment.updatedAt;
      return {status,enrollment,remote,localFingerprint,message:syncStatusMessage(status,remote)};
    }

    async function fetchRemoteSyncProject(projectId) {
      const data=await cloudRequest(`cloud-projects/${encodeURIComponent(projectId)}`); const source=normalizeProject(data?.package?.project); if(!source)throw new Error('The cloud project is not compatible with this Workspace version.'); return {source,item:data.item||null};
    }

    async function pushSyncHead(project,enrollment,expectedRevision) {
      const data=await cloudRequest('cloud-projects',{method:'POST',body:JSON.stringify(syncPushPayload(project,enrollment,expectedRevision))}); if(!data?.item)throw new Error('The server did not return synchronized project metadata.');
      const localFingerprint=await syncProjectFingerprint(project); enrollment.serverRevision=Math.max(0,Number(data.item.revision)||0); enrollment.remoteRevision=enrollment.serverRevision; enrollment.lastSyncedFingerprint=localFingerprint||String(data.item.projectFingerprint||''); enrollment.remoteFingerprint=String(data.item.projectFingerprint||enrollment.lastSyncedFingerprint||''); enrollment.lastSyncedAt=nowIso(); enrollment.lastCheckedAt=enrollment.lastSyncedAt; enrollment.status='up-to-date'; enrollment.updatedAt=enrollment.lastSyncedAt; state.accountPersistence.cloudRecords=[data.item,...state.accountPersistence.cloudRecords.filter(record=>record.projectId!==data.item.projectId)]; state.crossDeviceSync.updatedAt=enrollment.updatedAt; return data.item;
    }

    async function applyRemoteInPlace(project,enrollment,remote,preserveLocalConflictCopy=false) {
      const {source,item}=await fetchRemoteSyncProject(project.id); if(preserveLocalConflictCopy){const safety=cloneProject(project);safety.title=`${project.title} (Local conflict copy)`.slice(0,120);safety.activity.unshift({id:id('act'),type:'sync-conflict-copy',summary:`Preserved local changes before accepting cloud revision ${remote?.revision||item?.revision||''}`.trim(),at:nowIso()});state.projects.unshift(safety);} source.id=project.id; source.persistence=projectPersistenceTemplate(); source.activity=Array.isArray(source.activity)?source.activity:[]; source.activity.unshift({id:id('act'),type:'sync-pull',summary:`Applied cloud revision ${remote?.revision||item?.revision||''}`.trim(),at:nowIso()}); const index=state.projects.findIndex(candidate=>candidate.id===project.id);if(index<0)throw new Error('Local project is no longer available.');state.projects[index]=source; const fingerprint=await syncProjectFingerprint(source); enrollment.serverRevision=Math.max(0,Number(remote?.revision||item?.revision)||0);enrollment.remoteRevision=enrollment.serverRevision;enrollment.lastSyncedFingerprint=fingerprint||String(remote?.projectFingerprint||item?.projectFingerprint||'');enrollment.remoteFingerprint=String(remote?.projectFingerprint||item?.projectFingerprint||enrollment.lastSyncedFingerprint||'');enrollment.lastSyncedAt=nowIso();enrollment.lastCheckedAt=enrollment.lastSyncedAt;enrollment.status='up-to-date';enrollment.updatedAt=enrollment.lastSyncedAt;state.crossDeviceSync.updatedAt=enrollment.updatedAt;return source;
    }

    async function refreshCloudProjects(recordHistory = true) {
      if (!cloudStatus || !cloudList) return;
      if (!IDENTITY_CONFIG.authenticated) {
        cloudStatus.textContent = 'Sign in to use account recovery and explicit cross-device sync. Local Workspace remains fully available without an account.';
        cloudList.innerHTML = '';
        if (cloudBadge) cloudBadge.textContent = 'LOCAL ONLY';
        if (cloudBackupButton) cloudBackupButton.disabled = true;
        if (cloudRefreshButton) cloudRefreshButton.disabled = true;
        return;
      }
      try {
        cloudStatus.textContent = 'Checking account project copies…';
        const data = await cloudRequest('cloud-projects');
        state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
        state.accountPersistence.cloudRecords = Array.isArray(data?.items) ? data.items : [];
        state.accountPersistence.lastRefreshAt = nowIso();
        if (recordHistory) touchAccountPersistence('refresh');
        writeState(state);
        renderCloudRecovery();
        cloudStatus.textContent = `${state.accountPersistence.cloudRecords.length} account project cop${state.accountPersistence.cloudRecords.length === 1 ? 'y' : 'ies'} available.`;
      } catch (error) {
        cloudStatus.textContent = error.message || 'Cloud recovery could not be checked.';
      }
    }

    function renderCloudRecovery() {
      if (!cloudList || !cloudProject) return;
      state.accountPersistence = normalizeAccountPersistence(state.accountPersistence, state.projects);
      cloudProject.innerHTML = '<option value="">Choose a project</option>';
      state.projects.filter(p => !p.archivedAt).forEach(project => {
        const option = document.createElement('option'); option.value = project.id; option.textContent = project.title; cloudProject.appendChild(option);
      });
      if (state.projects.some(p => p.id === state.accountPersistence.selectedProjectId && !p.archivedAt)) cloudProject.value = state.accountPersistence.selectedProjectId;
      else if (activeProject()) cloudProject.value = activeProject().id;
      const authenticated = Boolean(IDENTITY_CONFIG.authenticated);
      if (cloudBadge) cloudBadge.textContent = authenticated ? 'ACCOUNT COPIES' : 'LOCAL ONLY';
      if (cloudBackupButton) cloudBackupButton.disabled = !authenticated || !cloudProject.value;
      if (cloudRefreshButton) cloudRefreshButton.disabled = !authenticated;
      cloudList.innerHTML = '';
      if (!authenticated) return;
      if (!state.accountPersistence.cloudRecords.length) {
        cloudList.innerHTML = '<div class="scw-cloud-empty">No account project copies yet. Choose a local project and use Back up now, or explicitly enable sync below.</div>';
        return;
      }
      state.accountPersistence.cloudRecords.forEach(record => {
        const row = document.createElement('article'); row.className = 'scw-cloud-item';
        const meta = document.createElement('div');
        meta.innerHTML = `<span>${escapeHtml(record.objectCount)} objects · ${escapeHtml(formatTime(record.backedUpAt))}</span><strong>${escapeHtml(record.title)}</strong><small>r${escapeHtml(record.revision || 0)} · ${escapeHtml(record.storageMode === 'sync-head' ? 'SYNC HEAD' : 'MANUAL BACKUP')} · ${escapeHtml((record.bytes/1024).toFixed(1))} KB · SHA-256 ${escapeHtml(String(record.projectFingerprint||record.fingerprint||'').slice(0,12))}…</small>`;
        const actions = document.createElement('div'); actions.className='scw-cloud-item-actions';
        const restore = document.createElement('button'); restore.type='button'; restore.className='scw-card-action'; restore.textContent='Restore as copy';
        restore.addEventListener('click', async()=>{
          try {
            cloudStatus.textContent='Loading backup…';
            const data=await cloudRequest(`cloud-projects/${encodeURIComponent(record.projectId)}`);
            const source=normalizeProject(data?.package?.project);
            if(!source) throw new Error('Cloud backup project is not compatible with this Workspace version.');
            const copy=cloneProject(source); copy.title=`${source.title} (Recovered)`.slice(0,120); copy.activity.unshift({id:id('act'),type:'cloud-restore',summary:`Restored as a local copy from account backup ${record.backedUpAt||''}`.trim(),at:nowIso()});
            state.projects.unshift(copy); state.activeProjectId=copy.id; touchAccountPersistence('restore',copy); persist('Account backup restored as a new local copy'); render(); setWorkspaceView('projects',true); cloudStatus.textContent=`Restored ${source.title} as a new local copy.`;
          } catch(error){ cloudStatus.textContent=error.message||'Restore failed.'; }
        });
        const del = document.createElement('button'); del.type='button'; del.className='scw-card-action scw-card-danger'; del.textContent='Delete backup';
        del.addEventListener('click', async()=>{
          if(!window.confirm(`Delete the account backup for “${record.title}”? Your local project will not be changed.`)) return;
          try { await cloudRequest(`cloud-projects/${encodeURIComponent(record.projectId)}`,{method:'DELETE'}); touchAccountPersistence('delete',{id:record.projectId,title:record.title}); await refreshCloudProjects(false); persist('Account backup deleted'); }
          catch(error){ cloudStatus.textContent=error.message||'Delete failed.'; }
        });
        actions.append(restore,del); row.append(meta,actions); cloudList.appendChild(row);
      });
    }

    function renderAccountSync() {
      if (!syncProject || !syncStatus) return;
      state.crossDeviceSync=normalizeCrossDeviceSync(state.crossDeviceSync,state.projects); const authenticated=Boolean(IDENTITY_CONFIG.authenticated); const current=syncProject.value; syncProject.innerHTML='<option value="">Choose a project</option>'; state.projects.filter(project=>!project.archivedAt).forEach(project=>{const option=document.createElement('option');option.value=project.id;option.textContent=project.title;syncProject.appendChild(option);}); if(state.projects.some(project=>project.id===current&&!project.archivedAt))syncProject.value=current;else if(activeProject())syncProject.value=activeProject().id; const project=state.projects.find(item=>item.id===syncProject.value&&!item.archivedAt)||null; const enrollment=project?syncEnrollment(project.id,false):null; const enabled=Boolean(enrollment?.enabled); if(syncBadge)syncBadge.textContent=!authenticated?'LOCAL ONLY':enabled?String(enrollment.status||'enabled').replaceAll('-',' ').toUpperCase():'SYNC OFF'; if(syncToggleButton){syncToggleButton.disabled=!authenticated||!project;syncToggleButton.textContent=enabled?'Disable sync':'Enable sync';} if(syncCheckButton)syncCheckButton.disabled=!authenticated||!project||!enabled;if(syncNowButton)syncNowButton.disabled=!authenticated||!project||!enabled;if(syncLocal)syncLocal.textContent=project?`Local · ${formatTime(project.updatedAt)}`:'Choose project'; const remote=project?remoteCloudRecord(project.id):null;if(syncRemote)syncRemote.textContent=remote?`Cloud r${remote.revision} · ${formatTime(remote.backedUpAt)}`:'No cloud head';if(syncBaseline)syncBaseline.textContent=enrollment?.serverRevision?`r${enrollment.serverRevision} · ${String(enrollment.lastSyncedFingerprint||'').slice(0,12)}…`:'No common revision';if(syncStateEl)syncStateEl.textContent=enabled?String(enrollment.status||'not-uploaded').replaceAll('-',' ').toUpperCase():'DISABLED';if(!authenticated)syncStatus.textContent='Sign in to enable explicit cross-device sync. Guest/local Workspace remains fully available.';else if(!project)syncStatus.textContent='Choose a local project.';else if(!enabled)syncStatus.textContent='Sync is off. Enabling it changes local sync metadata only; no project content uploads until you choose Sync now.';else syncStatus.textContent=syncStatusMessage(enrollment.status||'not-uploaded',remote);const conflicted=enabled&&enrollment?.status==='conflict',remoteAvailable=Boolean(remote);if(syncRemoteCopyButton){syncRemoteCopyButton.hidden=!authenticated||!project||!enabled||!remoteAvailable;syncRemoteCopyButton.disabled=!remoteAvailable;}if(syncResolveLocalButton){syncResolveLocalButton.hidden=!conflicted;syncResolveLocalButton.disabled=!conflicted;}if(syncResolveCloudButton){syncResolveCloudButton.hidden=!conflicted;syncResolveCloudButton.disabled=!conflicted;}
    }

    function activeProject() {
      return state.projects.find((project) => project.id === state.activeProjectId && !project.archivedAt) || null;
    }

    function setProjectMode(mode) {
      const allowed = new Set(['overview','guide','research','analysis','decision','canvas','traceability','assist','briefing','objects']);
      activeProjectMode = allowed.has(mode) ? mode : 'overview';
      root.classList.add('scw-mode-enabled');
      root.querySelectorAll('[data-scw-project-mode]').forEach((button) => {
        const selected = button.dataset.scwProjectMode === activeProjectMode;
        button.classList.toggle('is-active', selected);
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
      root.querySelectorAll('[data-scw-project-panel]').forEach((panel) => {
        panel.hidden = panel.dataset.scwProjectPanel !== activeProjectMode;
      });
    }

    function activeObject() {
      const project = activeProject();
      if (!project || !project.activeObjectId) return null;
      return project.objects.find((object) => object.id === project.activeObjectId && !object.archivedAt) || null;
    }

    function persist(message = 'Saved on this device') {
      const saved = writeState(state);
      if (saveState) saveState.textContent = saved ? message : 'Save unavailable';
      if (storageState) storageState.textContent = saved ? 'Local project storage ready · verified' : 'Local project storage unavailable';
      if (recoveryNotice) showRecovery();
      return saved;
    }

    function schedulePersist() {
      if (saveState) saveState.textContent = 'Saving…';
      window.clearTimeout(saveTimer);
      saveTimer = window.setTimeout(() => persist(), 320);
    }

    function showRecovery() {
      if (!recoveryNotice) return;
      if (recoveryMessage) recoveryMessage.textContent = recoveryNotice;
      if (recovery) recovery.hidden = false;
    }

    function renderDiagnosticReport(report) {
      if (!report) return;
      const checks = report.checks || {};
      const storageOk = Boolean(checks.browserStorageAvailable && checks.currentStateSerializable);
      if (readinessStorage) readinessStorage.textContent = storageOk ? 'READY' : 'ATTENTION';
      if (readinessRecovery) readinessRecovery.textContent = checks.lastKnownGoodSnapshotAvailable ? 'SNAPSHOT READY' : 'CREATED AFTER NEXT VERIFIED SAVE';
      if (readinessCrypto) readinessCrypto.textContent = checks.webCryptoSha256Available ? 'SHA-256 READY' : 'LIMITED';
      if (readinessSize) readinessSize.textContent = `${Math.max(0, Number(report.approximateWorkspaceBytes || 0) / 1024).toFixed(1)} KB`;
      const ready = storageOk && Boolean(checks.webCryptoSha256Available);
      if (readinessBadge) readinessBadge.textContent = ready ? 'READY' : 'ATTENTION';
      if (readinessStatus) readinessStatus.textContent = ready
        ? `Local diagnostics passed. ${report.counts.projects} project(s), ${report.counts.objects} object(s); no project content left this browser.`
        : 'Diagnostics found a browser capability that needs attention. Export a diagnostic report before troubleshooting; it excludes project content.';
      if (exportDiagnostics) exportDiagnostics.disabled = false;
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
        activeProjectMode = 'overview';
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



    function objectById(project, objectId) {
      return project.objects.find((object) => object.id === objectId && !object.archivedAt) || null;
    }

    function renderResearch(project) {
      const research = project.research || researchTemplate();
      const sources = project.objects.filter((object) => object.type === 'source' && !object.archivedAt).sort(objectSort);
      const evidence = project.objects.filter((object) => object.type === 'evidence' && !object.archivedAt).sort(objectSort);
      const openQuestions = research.questions.filter((question) => question.status === 'open').length;
      const supportedClaims = research.claims.filter((claim) => claim.status === 'supported').length;
      researchMetricQuestions.textContent = String(openQuestions);
      researchMetricSources.textContent = String(sources.length);
      researchMetricEvidence.textContent = String(evidence.length);
      researchMetricClaims.textContent = String(supportedClaims);

      const activeQuestion = research.questions.find((question) => question.id === research.activeQuestionId) || null;
      researchActiveQuestion.textContent = activeQuestion ? activeQuestion.text : 'No active research question selected.';

      researchQuestionList.innerHTML = '';
      if (!research.questions.length) {
        const emptyItem = document.createElement('div'); emptyItem.className = 'scw-research-empty'; emptyItem.textContent = 'No research questions yet.'; researchQuestionList.appendChild(emptyItem);
      } else {
        [...research.questions].sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt))).forEach((question) => {
          const row = document.createElement('article'); row.className = `scw-research-row${question.id === research.activeQuestionId ? ' is-active' : ''}`;
          const text = document.createElement('strong'); text.textContent = question.text;
          const meta = document.createElement('span'); meta.textContent = `${question.priority.toUpperCase()} · ${question.status.toUpperCase()}`;
          const controls = document.createElement('div'); controls.className = 'scw-research-row-controls';
          const status = document.createElement('select');
          ['open','answered','deferred'].forEach((value) => { const option = document.createElement('option'); option.value = value; option.textContent = value[0].toUpperCase() + value.slice(1); status.appendChild(option); });
          status.value = question.status;
          status.addEventListener('change', () => { question.status = QUESTION_STATUS.has(status.value) ? status.value : 'open'; question.updatedAt = nowIso(); touchResearch(project); addActivity(project, 'research-question', `Research question marked ${question.status}`); persist('Research question saved'); renderResearch(project); });
          const activate = document.createElement('button'); activate.type = 'button'; activate.className = 'scw-card-action'; activate.textContent = question.id === research.activeQuestionId ? 'Active question' : 'Set active';
          activate.addEventListener('click', () => { research.activeQuestionId = question.id; question.updatedAt = nowIso(); touchResearch(project); persist('Active research question saved'); renderResearch(project); });
          const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'scw-card-action scw-card-action-muted'; remove.textContent = 'Remove';
          remove.addEventListener('click', () => { research.questions = research.questions.filter((item) => item.id !== question.id); if (research.activeQuestionId === question.id) research.activeQuestionId = null; touchResearch(project); addActivity(project, 'research-question', 'Research question removed'); persist('Research question removed'); renderResearch(project); });
          controls.append(status, activate, remove); row.append(text, meta, controls); researchQuestionList.appendChild(row);
        });
      }

      researchEvidenceSource.innerHTML = '<option value="">No linked source</option>';
      sources.forEach((source) => { const option = document.createElement('option'); option.value = source.id; option.textContent = source.title; researchEvidenceSource.appendChild(option); });
      researchClaimEvidence.innerHTML = '<option value="">Choose evidence</option>';
      evidence.forEach((item) => { const option = document.createElement('option'); option.value = item.id; option.textContent = item.title; researchClaimEvidence.appendChild(option); });

      researchReadingList.innerHTML = '';
      const queue = research.readingQueue.map((item) => ({ item, object: objectById(project, item.objectId) })).filter((entry) => entry.object);
      if (!queue.length) {
        const emptyItem = document.createElement('div'); emptyItem.className = 'scw-research-empty'; emptyItem.textContent = 'No sources in the reading queue.'; researchReadingList.appendChild(emptyItem);
      } else {
        queue.forEach(({ item, object }) => {
          const row = document.createElement('article'); row.className = 'scw-research-row';
          const text = document.createElement('strong'); text.textContent = object.title;
          const meta = document.createElement('span'); meta.textContent = object.provenance.sourceType.toUpperCase();
          const controls = document.createElement('div'); controls.className = 'scw-research-row-controls';
          const status = document.createElement('select');
          ['unread','reading','read'].forEach((value) => { const option = document.createElement('option'); option.value = value; option.textContent = value[0].toUpperCase() + value.slice(1); status.appendChild(option); });
          status.value = item.status;
          status.addEventListener('change', () => { item.status = READING_STATUS.has(status.value) ? status.value : 'unread'; item.updatedAt = nowIso(); touchResearch(project); addActivity(project, 'reading-queue', `${object.title} marked ${item.status}`); persist('Reading queue saved'); renderResearch(project); });
          const open = document.createElement('button'); open.type = 'button'; open.className = 'scw-card-action'; open.textContent = 'Open source';
          open.addEventListener('click', () => { project.activeObjectId = object.id; project.updatedAt = nowIso(); persist(); render(); objectEditor.scrollIntoView({ behavior: 'auto', block: 'start' }); });
          const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'scw-card-action scw-card-action-muted'; remove.textContent = 'Remove';
          remove.addEventListener('click', () => { research.readingQueue = research.readingQueue.filter((queueItem) => queueItem.id !== item.id); touchResearch(project); persist('Reading queue updated'); renderResearch(project); });
          controls.append(status, open, remove); row.append(text, meta, controls); researchReadingList.appendChild(row);
        });
      }

      researchClaimList.innerHTML = '';
      if (!research.claims.length) {
        const emptyItem = document.createElement('div'); emptyItem.className = 'scw-research-empty'; emptyItem.textContent = 'No research claims yet.'; researchClaimList.appendChild(emptyItem);
      } else {
        [...research.claims].sort((a, b) => String(b.updatedAt).localeCompare(String(a.updatedAt))).forEach((claim) => {
          const row = document.createElement('article'); row.className = `scw-research-claim${claim.id === research.activeClaimId ? ' is-active' : ''}`;
          const top = document.createElement('div'); top.className = 'scw-research-claim-top';
          const text = document.createElement('strong'); text.textContent = claim.text;
          const status = document.createElement('select');
          ['exploratory','supported','contested','rejected'].forEach((value) => { const option = document.createElement('option'); option.value = value; option.textContent = value[0].toUpperCase() + value.slice(1); status.appendChild(option); });
          status.value = claim.status;
          status.addEventListener('change', () => { claim.status = CLAIM_STATUS.has(status.value) ? status.value : 'exploratory'; claim.updatedAt = nowIso(); touchResearch(project); addActivity(project, 'research-claim', `Claim marked ${claim.status}`); persist('Research claim saved'); renderResearch(project); });
          top.append(text, status);
          const linked = document.createElement('div'); linked.className = 'scw-research-evidence-links';
          const linkedObjects = claim.evidenceObjectIds.map((objectId) => objectById(project, objectId)).filter(Boolean);
          linked.textContent = linkedObjects.length ? `EVIDENCE · ${linkedObjects.map((item) => item.title).join(' · ')}` : 'NO EVIDENCE LINKED';
          const controls = document.createElement('div'); controls.className = 'scw-research-row-controls';
          const activate = document.createElement('button'); activate.type = 'button'; activate.className = 'scw-card-action'; activate.textContent = claim.id === research.activeClaimId ? 'Active claim' : 'Set active';
          activate.addEventListener('click', () => { research.activeClaimId = claim.id; claim.updatedAt = nowIso(); touchResearch(project); persist('Active claim saved'); renderResearch(project); });
          const remove = document.createElement('button'); remove.type = 'button'; remove.className = 'scw-card-action scw-card-action-muted'; remove.textContent = 'Remove';
          remove.addEventListener('click', () => { research.claims = research.claims.filter((item) => item.id !== claim.id); if (research.activeClaimId === claim.id) research.activeClaimId = null; touchResearch(project); addActivity(project, 'research-claim', 'Research claim removed'); persist('Research claim removed'); renderResearch(project); });
          controls.append(activate, remove); row.append(top, linked, controls); researchClaimList.appendChild(row);
        });
      }
    }



    function renderAnalysis(project) {
      const analysis = project.analysis || analysisTemplate();
      const datasets = project.objects.filter((object)=>object.type==='dataset' && !object.archivedAt).sort(objectSort);
      const analyses = project.objects.filter((object)=>object.type==='analysis' && !object.archivedAt).sort(objectSort);
      const evidence = project.objects.filter((object)=>object.type==='evidence' && !object.archivedAt).sort(objectSort);
      if (analysisMetricQuestions) analysisMetricQuestions.textContent = String(analysis.questions.filter((x)=>x.status==='open').length);
      if (analysisMetricDatasets) analysisMetricDatasets.textContent = String(datasets.length);
      if (analysisMetricAnalyses) analysisMetricAnalyses.textContent = String(analyses.length);
      if (analysisMetricFindings) analysisMetricFindings.textContent = String(analysis.findings.filter((x)=>x.status==='supported').length);
      const activeQuestion = analysis.questions.find((x)=>x.id===analysis.activeQuestionId) || null;
      if (analysisActiveQuestion) analysisActiveQuestion.textContent = activeQuestion ? activeQuestion.text : 'No active analysis question selected.';

      analysisQuestionList.innerHTML='';
      if (!analysis.questions.length) analysisQuestionList.innerHTML='<div class="scw-analysis-empty">No analysis questions yet.</div>';
      [...analysis.questions].sort((a,b)=>String(b.updatedAt).localeCompare(String(a.updatedAt))).forEach((question)=>{
        const row=document.createElement('article'); row.className=`scw-analysis-row${question.id===analysis.activeQuestionId?' is-active':''}`;
        const strong=document.createElement('strong'); strong.textContent=question.text;
        const meta=document.createElement('span'); meta.textContent=`${question.priority.toUpperCase()} · ${question.status.toUpperCase()}`;
        const controls=document.createElement('div'); controls.className='scw-analysis-row-controls';
        const status=document.createElement('select'); ['open','resolved','deferred'].forEach((v)=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)}); status.value=question.status;
        status.addEventListener('change',()=>{question.status=ANALYSIS_QUESTION_STATUS.has(status.value)?status.value:'open';question.updatedAt=nowIso();touchAnalysis(project);persist('Analysis question saved');renderAnalysis(project)});
        const active=document.createElement('button');active.type='button';active.className='scw-card-action';active.textContent=question.id===analysis.activeQuestionId?'Active question':'Set active';active.addEventListener('click',()=>{analysis.activeQuestionId=question.id;question.updatedAt=nowIso();touchAnalysis(project);persist('Active analysis question saved');renderAnalysis(project)});
        const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{analysis.questions=analysis.questions.filter((x)=>x.id!==question.id);if(analysis.activeQuestionId===question.id)analysis.activeQuestionId=null;touchAnalysis(project);persist('Analysis question removed');renderAnalysis(project)});
        controls.append(status,active,remove); row.append(strong,meta,controls); analysisQuestionList.appendChild(row);
      });

      analysisDatasetList.innerHTML='';
      if (!datasets.length) analysisDatasetList.innerHTML='<div class="scw-analysis-empty">No Dataset objects yet.</div>';
      datasets.forEach((dataset)=>{const row=document.createElement('article');row.className='scw-analysis-row';const strong=document.createElement('strong');strong.textContent=dataset.title;const meta=document.createElement('span');meta.textContent=dataset.status.toUpperCase();const controls=document.createElement('div');controls.className='scw-analysis-row-controls';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open dataset';open.addEventListener('click',()=>{project.activeObjectId=dataset.id;persist();render();objectEditor.scrollIntoView({behavior:'auto',block:'start'})});controls.append(open);row.append(strong,meta,controls);analysisDatasetList.appendChild(row)});
      analysisMethodDataset.innerHTML='<option value="">No linked dataset</option>'; datasets.forEach((dataset)=>{const o=document.createElement('option');o.value=dataset.id;o.textContent=dataset.title;analysisMethodDataset.appendChild(o)});
      analysisFindingEvidence.innerHTML='<option value="">No linked evidence</option>'; evidence.forEach((item)=>{const o=document.createElement('option');o.value=item.id;o.textContent=item.title;analysisFindingEvidence.appendChild(o)});

      function simpleList(el, items, render) { el.innerHTML=''; if (!items.length) { const e=document.createElement('div');e.className='scw-analysis-empty';e.textContent='Nothing recorded yet.';el.appendChild(e);return; } items.forEach(render); }
      simpleList(analysisVariableList, analysis.variables, (variable)=>{const row=document.createElement('article');row.className='scw-analysis-row';const strong=document.createElement('strong');strong.textContent=variable.name;const meta=document.createElement('span');meta.textContent=`${variable.role.toUpperCase()}${variable.unit?` · ${variable.unit}`:''}`;const controls=document.createElement('div');controls.className='scw-analysis-row-controls';const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{analysis.variables=analysis.variables.filter((x)=>x.id!==variable.id);touchAnalysis(project);persist('Variable removed');renderAnalysis(project)});controls.append(remove);row.append(strong,meta,controls);analysisVariableList.appendChild(row)});
      simpleList(analysisAssumptionList, analysis.assumptions, (assumption)=>{const row=document.createElement('article');row.className='scw-analysis-row';const strong=document.createElement('strong');strong.textContent=assumption.text;const controls=document.createElement('div');controls.className='scw-analysis-row-controls';const status=document.createElement('select');['untested','supported','challenged'].forEach((v)=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)});status.value=assumption.status;status.addEventListener('change',()=>{assumption.status=ANALYSIS_ASSUMPTION_STATUS.has(status.value)?status.value:'untested';assumption.updatedAt=nowIso();touchAnalysis(project);persist('Assumption saved');renderAnalysis(project)});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{analysis.assumptions=analysis.assumptions.filter((x)=>x.id!==assumption.id);touchAnalysis(project);persist('Assumption removed');renderAnalysis(project)});controls.append(status,remove);row.append(strong,controls);analysisAssumptionList.appendChild(row)});
      simpleList(analysisMethodList, analysis.methods, (method)=>{const row=document.createElement('article');row.className=`scw-analysis-row${method.id===analysis.activeMethodId?' is-active':''}`;const strong=document.createElement('strong');strong.textContent=method.name;const meta=document.createElement('span');meta.textContent=method.type.toUpperCase();const controls=document.createElement('div');controls.className='scw-analysis-row-controls';const active=document.createElement('button');active.type='button';active.className='scw-card-action';active.textContent=method.id===analysis.activeMethodId?'Active method':'Set active';active.addEventListener('click',()=>{analysis.activeMethodId=method.id;touchAnalysis(project);persist('Active method saved');renderAnalysis(project)});const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open analysis';open.disabled=!method.analysisObjectId;open.addEventListener('click',()=>{if(!method.analysisObjectId)return;project.activeObjectId=method.analysisObjectId;persist();render();objectEditor.scrollIntoView({behavior:'auto',block:'start'})});controls.append(active,open);row.append(strong,meta,controls);analysisMethodList.appendChild(row)});
      simpleList(analysisComparisonList, analysis.comparisons, (comparison)=>{const row=document.createElement('article');row.className='scw-analysis-record';const strong=document.createElement('strong');strong.textContent=comparison.label;const body=document.createElement('p');body.textContent=`${comparison.baseline || 'Baseline'} → ${comparison.alternative || 'Alternative'}${comparison.metric?` · ${comparison.metric}`:''}${comparison.result?` · ${comparison.result}`:''}`;const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{analysis.comparisons=analysis.comparisons.filter((x)=>x.id!==comparison.id);touchAnalysis(project);persist('Comparison removed');renderAnalysis(project)});row.append(strong,body,remove);analysisComparisonList.appendChild(row)});
      simpleList(analysisFindingList, analysis.findings, (finding)=>{const row=document.createElement('article');row.className='scw-analysis-row';const strong=document.createElement('strong');strong.textContent=finding.text;const meta=document.createElement('span');meta.textContent=`${finding.status.toUpperCase()}${finding.evidenceObjectIds.length?` · ${finding.evidenceObjectIds.length} evidence link(s)`:''}`;const controls=document.createElement('div');controls.className='scw-analysis-row-controls';const status=document.createElement('select');['preliminary','supported','contested'].forEach((v)=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)});status.value=finding.status;status.addEventListener('change',()=>{finding.status=ANALYSIS_FINDING_STATUS.has(status.value)?status.value:'preliminary';finding.updatedAt=nowIso();touchAnalysis(project);persist('Finding saved');renderAnalysis(project)});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{analysis.findings=analysis.findings.filter((x)=>x.id!==finding.id);touchAnalysis(project);persist('Finding removed');renderAnalysis(project)});controls.append(status,remove);row.append(strong,meta,controls);analysisFindingList.appendChild(row)});
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


    function renderDecision(project) {
      if (!decisionList) return;
      const d=project.decision||decisionTemplate(); const active=d.decisions.find(x=>x.id===d.activeDecisionId)||null;
      const options=active?d.options.filter(x=>x.decisionId===active.id):[]; const criteria=active?d.criteria.filter(x=>x.decisionId===active.id):[]; const assessments=active?d.assessments.filter(x=>x.decisionId===active.id):[]; const risks=active?d.risks.filter(x=>x.decisionId===active.id):[];
      decisionMetricOpen.textContent=String(d.decisions.filter(x=>x.status!=='decided').length); decisionMetricOptions.textContent=String(d.options.length); decisionMetricCriteria.textContent=String(d.criteria.length); decisionMetricDecided.textContent=String(d.decisions.filter(x=>x.status==='decided').length);
      decisionActive.textContent=active?`${active.title} — ${active.question}`:'No active decision selected.';
      decisionList.innerHTML=''; if(!d.decisions.length)decisionList.innerHTML='<div class="scw-decision-empty">No decision records yet.</div>';
      d.decisions.forEach(record=>{const row=document.createElement('article');row.className=`scw-decision-row${record.id===d.activeDecisionId?' is-active':''}`;const strong=document.createElement('strong');strong.textContent=record.title;const meta=document.createElement('span');meta.textContent=record.status.toUpperCase();const controls=document.createElement('div');controls.className='scw-decision-row-controls';const status=document.createElement('select');['framing','evaluating','decided','revisit'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)});status.value=record.status;status.addEventListener('change',()=>{record.status=DECISION_STATUS.has(status.value)?status.value:'framing';record.updatedAt=nowIso();touchDecision(project);persist('Decision status saved');renderDecision(project)});const activate=document.createElement('button');activate.type='button';activate.className='scw-card-action';activate.textContent=record.id===d.activeDecisionId?'Active decision':'Set active';activate.addEventListener('click',()=>{d.activeDecisionId=record.id;touchDecision(project);persist('Active decision saved');renderDecision(project)});const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open object';open.disabled=!record.decisionObjectId;open.addEventListener('click',()=>{if(!record.decisionObjectId)return;project.activeObjectId=record.decisionObjectId;persist();render();objectEditor.scrollIntoView({behavior:'auto',block:'start'})});controls.append(status,activate,open);row.append(strong,meta,controls);decisionList.appendChild(row)});
      const list=(el,items,empty,fn)=>{el.innerHTML='';if(!items.length){el.innerHTML=`<div class="scw-decision-empty">${empty}</div>`;return;}items.forEach(fn)};
      list(decisionOptionList,options,'No options for the active decision.',option=>{const row=document.createElement('article');row.className='scw-decision-row';const strong=document.createElement('strong');strong.textContent=option.label;const meta=document.createElement('span');meta.textContent=option.status.toUpperCase();const controls=document.createElement('div');controls.className='scw-decision-row-controls';const status=document.createElement('select');['candidate','shortlisted','selected','rejected'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)});status.value=option.status;status.addEventListener('change',()=>{option.status=DECISION_OPTION_STATUS.has(status.value)?status.value:'candidate';option.updatedAt=nowIso();touchDecision(project);persist('Option status saved');renderDecision(project)});controls.append(status);row.append(strong,meta,controls);decisionOptionList.appendChild(row)});
      list(decisionCriterionList,criteria,'No criteria for the active decision.',criterion=>{const row=document.createElement('article');row.className='scw-decision-record';const strong=document.createElement('strong');strong.textContent=criterion.label;const body=document.createElement('p');body.textContent=`Weight ${criterion.weight}/100${criterion.description?` · ${criterion.description}`:''}`;row.append(strong,body);decisionCriterionList.appendChild(row)});
      decisionAssessmentOption.innerHTML='<option value="">Choose option</option>'; decisionFinalOption.innerHTML='<option value="">Choose option</option>'; options.forEach(x=>{[decisionAssessmentOption,decisionFinalOption].forEach(el=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.label;el.appendChild(o)})}); decisionAssessmentCriterion.innerHTML='<option value="">Choose criterion</option>';criteria.forEach(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.label;decisionAssessmentCriterion.appendChild(o)});
      list(decisionAssessmentList,assessments,'No assessments recorded.',assessment=>{const row=document.createElement('article');row.className='scw-decision-record';const option=options.find(x=>x.id===assessment.optionId),criterion=criteria.find(x=>x.id===assessment.criterionId);const strong=document.createElement('strong');strong.textContent=`${option?option.label:'Option'} × ${criterion?criterion.label:'Criterion'}: ${assessment.score>0?'+':''}${assessment.score}`;const body=document.createElement('p');body.textContent=assessment.note||'No assessment note.';row.append(strong,body);decisionAssessmentList.appendChild(row)});
      list(decisionRiskList,risks,'No risks recorded.',risk=>{const row=document.createElement('article');row.className='scw-decision-record';const strong=document.createElement('strong');strong.textContent=risk.risk;const body=document.createElement('p');body.textContent=`${risk.likelihood.toUpperCase()} likelihood · ${risk.impact.toUpperCase()} impact${risk.mitigation?` · Mitigation: ${risk.mitigation}`:''}`;row.append(strong,body);decisionRiskList.appendChild(row)});
      if(!active||active.status!=='decided'){decisionSummary.innerHTML='<span>No finalized decision yet.</span>';}else{const selected=options.find(x=>x.id===active.selectedOptionId);decisionSummary.innerHTML='';const strong=document.createElement('strong');strong.textContent=selected?selected.label:'Decision finalized';const p=document.createElement('p');p.textContent=active.rationale;const meta=document.createElement('span');meta.textContent=`${active.confidence.toUpperCase()} CONFIDENCE · ${formatTime(active.decidedAt||active.updatedAt)}`;decisionSummary.append(strong,p,meta);}
    }

    function renderCanvas(project) {
      if (!canvasBoardList) return;
      const c = project.canvas || canvasTemplate();
      const active = c.boards.find((board) => board.id === c.activeBoardId) || null;
      const nodes = active ? c.nodes.filter((node) => node.boardId === active.id) : [];
      const nodeIds = new Set(nodes.map((node) => node.id));
      const edges = active ? c.edges.filter((edge) => edge.boardId === active.id && nodeIds.has(edge.fromNodeId) && nodeIds.has(edge.toNodeId)) : [];
      const frames = active ? c.frames.filter((frame) => frame.boardId === active.id) : [];
      if (canvasMetricBoards) canvasMetricBoards.textContent = String(c.boards.length);
      if (canvasMetricNodes) canvasMetricNodes.textContent = String(c.nodes.length);
      if (canvasMetricEdges) canvasMetricEdges.textContent = String(c.edges.length);
      if (canvasMetricFrames) canvasMetricFrames.textContent = String(c.frames.length);
      if (canvasActive) canvasActive.textContent = active ? `${active.title} · ${active.status.toUpperCase()}` : 'No active board selected.';

      canvasBoardList.innerHTML = '';
      if (!c.boards.length) canvasBoardList.innerHTML = '<div class="scw-canvas-empty">No Canvas boards yet.</div>';
      c.boards.forEach((board) => {
        const row = document.createElement('article'); row.className = `scw-canvas-row${board.id === c.activeBoardId ? ' is-active' : ''}`;
        const copy = document.createElement('div'); const strong = document.createElement('strong'); strong.textContent = board.title; const small = document.createElement('span'); small.textContent = board.description || 'No board purpose recorded.'; copy.append(strong, small);
        const controls = document.createElement('div'); controls.className = 'scw-canvas-row-controls';
        const status = document.createElement('select'); ['draft','working','ready'].forEach((value) => { const option=document.createElement('option'); option.value=value; option.textContent=value[0].toUpperCase()+value.slice(1); status.appendChild(option); }); status.value=board.status;
        status.addEventListener('change', () => { board.status = CANVAS_BOARD_STATUS.has(status.value) ? status.value : 'draft'; board.updatedAt = nowIso(); touchCanvas(project); persist('Canvas board status saved'); renderCanvas(project); });
        const activate = document.createElement('button'); activate.type='button'; activate.className='scw-card-action'; activate.textContent=board.id===c.activeBoardId?'Active':'Open'; activate.addEventListener('click',()=>{c.activeBoardId=board.id;touchCanvas(project);persist('Active Canvas board saved');renderCanvas(project);});
        const remove = document.createElement('button'); remove.type='button'; remove.className='scw-card-action'; remove.textContent='Delete'; remove.addEventListener('click',()=>{if(!window.confirm(`Delete Canvas board “${board.title}” and its nodes, relationships, and frames?`))return;const ids=new Set(c.nodes.filter(node=>node.boardId===board.id).map(node=>node.id));c.nodes=c.nodes.filter(node=>node.boardId!==board.id);c.edges=c.edges.filter(edge=>edge.boardId!==board.id&&!ids.has(edge.fromNodeId)&&!ids.has(edge.toNodeId));c.frames=c.frames.filter(frame=>frame.boardId!==board.id);c.boards=c.boards.filter(item=>item.id!==board.id);c.activeBoardId=c.boards[0]?c.boards[0].id:null;touchCanvas(project);addActivity(project,'canvas-board-deleted',`Canvas board deleted: ${board.title}`);persist('Canvas board deleted');renderCanvas(project);});
        controls.append(status, activate, remove); row.append(copy, controls); canvasBoardList.appendChild(row);
      });

      if (canvasNodeObject) {
        canvasNodeObject.innerHTML = '<option value="">No linked object</option>';
        project.objects.filter((object)=>!object.archivedAt).sort(objectSort).forEach((object)=>{const option=document.createElement('option');option.value=object.id;option.textContent=`${OBJECT_LABELS[object.type]} · ${object.title}`;canvasNodeObject.appendChild(option);});
      }
      const fillNodeSelect = (select, emptyLabel) => { if(!select)return; select.innerHTML=`<option value="">${emptyLabel}</option>`; nodes.forEach((node)=>{const option=document.createElement('option');option.value=node.id;option.textContent=`${node.type.toUpperCase()} · ${node.title}`;select.appendChild(option);}); };
      fillNodeSelect(canvasEdgeFrom,'Choose node'); fillNodeSelect(canvasEdgeTo,'Choose node');
      if (canvasFrameNodes) { canvasFrameNodes.innerHTML=''; nodes.forEach((node)=>{const option=document.createElement('option');option.value=node.id;option.textContent=`${node.type.toUpperCase()} · ${node.title}`;canvasFrameNodes.appendChild(option);}); }

      if (canvasSurface) {
        canvasSurface.querySelectorAll('.scw-canvas-node').forEach((node)=>node.remove());
        if (canvasLines) canvasLines.innerHTML='';
        if (canvasSurfaceEmpty) { canvasSurfaceEmpty.hidden = Boolean(active && nodes.length); canvasSurfaceEmpty.textContent = active ? 'This board is empty. Add a node below.' : 'Select or create a board to begin mapping.'; }
        if (active) {
          edges.forEach((edge)=>{const from=nodes.find((node)=>node.id===edge.fromNodeId),to=nodes.find((node)=>node.id===edge.toNodeId);if(!from||!to||!canvasLines)return;const line=document.createElementNS('http://www.w3.org/2000/svg','line');line.setAttribute('x1',String(from.x+90));line.setAttribute('y1',String(from.y+40));line.setAttribute('x2',String(to.x+90));line.setAttribute('y2',String(to.y+40));line.setAttribute('data-relation',edge.relation);canvasLines.appendChild(line);});
          nodes.forEach((node)=>{
            const card=document.createElement('article');card.className=`scw-canvas-node scw-canvas-node-${node.type}`;card.style.left=`${node.x}px`;card.style.top=`${node.y}px`;card.dataset.nodeId=node.id;
            const type=document.createElement('span');type.textContent=node.type.toUpperCase();const strong=document.createElement('strong');strong.textContent=node.title;const body=document.createElement('p');body.textContent=node.body||'No detail.';const actions=document.createElement('div');actions.className='scw-canvas-node-actions';
            if(node.objectId){const open=document.createElement('button');open.type='button';open.textContent='Object';open.addEventListener('click',(event)=>{event.stopPropagation();project.activeObjectId=node.objectId;persist();render();objectEditor.scrollIntoView({behavior:'auto',block:'start'});});actions.appendChild(open);}
            const remove=document.createElement('button');remove.type='button';remove.textContent='×';remove.setAttribute('aria-label',`Delete ${node.title}`);remove.addEventListener('click',(event)=>{event.stopPropagation();removeCanvasNode(project,node.id);addActivity(project,'canvas-node-deleted',`Canvas node deleted: ${node.title}`);persist('Canvas node deleted');renderCanvas(project);});actions.appendChild(remove);card.append(type,strong,body,actions);
            card.addEventListener('pointerdown',(event)=>{if(event.target.closest('button'))return;const startX=event.clientX,startY=event.clientY,originX=node.x,originY=node.y;card.setPointerCapture(event.pointerId);card.classList.add('is-dragging');const move=(ev)=>{node.x=Math.max(0,Math.min(820,originX+(ev.clientX-startX)));node.y=Math.max(0,Math.min(420,originY+(ev.clientY-startY)));card.style.left=`${node.x}px`;card.style.top=`${node.y}px`;};const up=()=>{card.classList.remove('is-dragging');card.removeEventListener('pointermove',move);card.removeEventListener('pointerup',up);node.updatedAt=nowIso();touchCanvas(project);persist('Canvas layout saved');renderCanvas(project);};card.addEventListener('pointermove',move);card.addEventListener('pointerup',up);});
            canvasSurface.appendChild(card);
          });
        }
      }

      canvasEdgeList.innerHTML=''; if(!edges.length)canvasEdgeList.innerHTML='<div class="scw-canvas-empty">No relationships on the active board.</div>';
      edges.forEach((edge)=>{const from=nodes.find(node=>node.id===edge.fromNodeId),to=nodes.find(node=>node.id===edge.toNodeId);const row=document.createElement('article');row.className='scw-canvas-record';const strong=document.createElement('strong');strong.textContent=`${from?from.title:'Node'} → ${to?to.title:'Node'}`;const meta=document.createElement('span');meta.textContent=`${edge.relation}${edge.label?` · ${edge.label}`:''}`;const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action';remove.textContent='Remove';remove.addEventListener('click',()=>{c.edges=c.edges.filter(item=>item.id!==edge.id);touchCanvas(project);persist('Canvas relationship removed');renderCanvas(project);});row.append(strong,meta,remove);canvasEdgeList.appendChild(row);});
      canvasFrameList.innerHTML=''; if(!frames.length)canvasFrameList.innerHTML='<div class="scw-canvas-empty">No frames on the active board.</div>';
      frames.forEach((frame)=>{const row=document.createElement('article');row.className='scw-canvas-record';const strong=document.createElement('strong');strong.textContent=frame.title;const meta=document.createElement('span');meta.textContent=`${frame.nodeIds.length} nodes${frame.description?` · ${frame.description}`:''}`;const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action';remove.textContent='Remove';remove.addEventListener('click',()=>{c.frames=c.frames.filter(item=>item.id!==frame.id);touchCanvas(project);persist('Canvas frame removed');renderCanvas(project);});row.append(strong,meta,remove);canvasFrameList.appendChild(row);});
    }

    function renderHandoffs(project) {
      if (!handoffList || !handoffEmpty) return;
      const ledger = project.handoffs || handoffLedgerTemplate();
      const entries = ledger.entries || [];
      const awaiting = entries.filter((entry) => entry.status === 'launched' || entry.status === 'prepared').length;
      const returned = entries.filter((entry) => entry.status === 'returned').length;
      const closed = entries.filter((entry) => entry.status === 'closed').length;
      const returnedObjects = entries.reduce((total, entry) => total + (Array.isArray(entry.returnObjectIds) ? entry.returnObjectIds.length : 0), 0);
      if (handoffMetricLaunched) handoffMetricLaunched.textContent = String(awaiting);
      if (handoffMetricReturned) handoffMetricReturned.textContent = String(returned);
      if (handoffMetricObjects) handoffMetricObjects.textContent = String(returnedObjects);
      if (handoffMetricClosed) handoffMetricClosed.textContent = String(closed);
      handoffList.innerHTML = '';
      handoffEmpty.hidden = entries.length > 0;
      entries.slice(0,40).forEach((entry) => {
        const row = document.createElement('article'); row.className = `scw-handoff-row is-${entry.status}`;
        const main = document.createElement('div');
        const meta = document.createElement('span'); meta.className='scw-handoff-meta'; meta.textContent = `${entry.intent.toUpperCase()} · ${entry.status.toUpperCase()} · ${formatTime(entry.launchedAt || entry.createdAt)}`;
        const title = document.createElement('strong'); title.textContent = entry.destinationLabel;
        const detail = document.createElement('p'); detail.textContent = `${entry.id} · ${entry.objectIds.length} outbound object ref${entry.objectIds.length===1?'':'s'} · ${entry.returnObjectIds.length} returned artifact${entry.returnObjectIds.length===1?'':'s'}`;
        main.append(meta,title,detail);
        const actions=document.createElement('div'); actions.className='scw-handoff-row-actions';
        if (entry.returnObjectIds && entry.returnObjectIds.length) { const open=document.createElement('button'); open.type='button'; open.className='scw-card-action'; open.textContent='Open return'; open.addEventListener('click',()=>{const objectId=entry.returnObjectIds.find((oid)=>project.objects.some((object)=>object.id===oid&&!object.archivedAt));if(objectId){project.activeObjectId=objectId;persist();renderObjectEditor(project);objectEditor.scrollIntoView({behavior:'auto',block:'start'});}});actions.appendChild(open); }
        if (entry.status !== 'closed') { const close=document.createElement('button'); close.type='button'; close.className='scw-card-action'; close.textContent='Close'; close.addEventListener('click',()=>{entry.status='closed';entry.closedAt=nowIso();touchHandoffs(project);addActivity(project,'handoff-closed',`Handoff closed: ${entry.destinationLabel}`);persist('Handoff closed');renderHandoffs(project);});actions.appendChild(close); }
        const template=document.createElement('button'); template.type='button'; template.className='scw-card-action'; template.textContent='Return template'; template.addEventListener('click',()=>downloadReturnTemplate(project,entry)); actions.appendChild(template);
        row.append(main,actions); handoffList.appendChild(row);
      });
    }

    function downloadReturnTemplate(project, entry) {
      if (!project || !entry) return;
      downloadJson(`${safeFileName(project.title)}-${entry.id}.sc-handoff-return.json`, { schema: HANDOFF_RETURN_SCHEMA, handoffId: entry.id, projectId: project.id, destination: entry.destination, destinationLabel: entry.destinationLabel, intent: entry.intent, returnedAt: nowIso(), artifacts: [{ type:'document', title:'Returned artifact', summary:'Replace this example with the artifact summary.', content:'', tags:[], status:'ready', sourceTitle:entry.destinationLabel, sourceUrl:'' }] });
    }

    function checkReturnInbox(showEmptyNotice = true) {
      let raw = null;
      try { raw = window.sessionStorage.getItem(HANDOFF_RETURN_KEY); } catch (_) {}
      if (!raw) { if (showEmptyNotice) window.alert('No structured handoff return is waiting in this browser session.'); return false; }
      try {
        const result = ingestReturnPacket(state, JSON.parse(raw), {mode:'automatic'});
        if (!result.ok) { window.alert(result.message); return false; }
        try { window.sessionStorage.removeItem(HANDOFF_RETURN_KEY); } catch (_) {}
        persist(result.message); render(); return true;
      } catch (_) { window.alert('Workspace could not read the structured return packet.'); return false; }
    }

    function receiveAdapterReturn(payload, source = 'adapter') {
      const result=ingestReturnPacket(state,payload,{mode:'automatic'});
      if (!result.ok) { if (!result.duplicate) console.warn(`Workspace ${source} return rejected: ${result.message}`); return result; }
      try { window.sessionStorage.removeItem(HANDOFF_RETURN_KEY); } catch (_) {}
      persist(result.message); render(); return result;
    }

    window.SCWorkspaceReturnAdapter = {
      schema: RETURN_ADAPTER_SCHEMA,
      receive(payload) { return receiveAdapterReturn(payload,'direct'); },
      destinations: Object.keys(RETURN_ADAPTERS),
      returnStorageKey: HANDOFF_RETURN_KEY
    };
    window.SCWorkspaceAIReceiver = {
      schema: AI_RESPONSE_SCHEMA,
      receive(packet) {
        const result=ingestAiResponsePacket(state,packet);
        if(result.ok){state.activeProjectId=result.projectId;activeProjectMode='assist';persist(result.message);render();}
        return result;
      },
      responseStorageKey: AI_RESPONSE_KEY
    };
    window.addEventListener('message',(event)=>{
      if (event.origin !== window.location.origin) return;
      const envelope=event.data;
      if (!envelope || typeof envelope !== 'object') return;
      if (envelope.type === 'sc-workspace-ai-response') {
        const result=window.SCWorkspaceAIReceiver.receive(envelope.packet);
        if (!result.ok) console.warn(`Workspace AI response rejected: ${result.message}`);
        return;
      }
      const candidate=envelope.type === 'sc-workspace-return' ? envelope.payload : envelope;
      if (!candidate || (candidate.schema !== RETURN_ADAPTER_SCHEMA && candidate.schema !== HANDOFF_RETURN_SCHEMA)) return;
      receiveAdapterReturn(candidate,'postMessage');
    });

    function objectOptionLabel(object){ return `${OBJECT_LABELS[object.type]||object.type} · ${object.title}`; }
    function fillObjectSelect(select, objects, placeholder='Choose an object') { if(!select)return; const current=Array.from(select.selectedOptions||[]).map(o=>o.value); select.innerHTML=''; if(!select.multiple){const p=document.createElement('option');p.value='';p.textContent=placeholder;select.appendChild(p);} objects.forEach((object)=>{const opt=document.createElement('option');opt.value=object.id;opt.textContent=objectOptionLabel(object);if(current.includes(object.id))opt.selected=true;select.appendChild(opt);}); }
    function selectedValues(select){ return select?Array.from(select.selectedOptions||[]).map(o=>o.value).filter(Boolean):[]; }
    function renderTraceability(project){
      if(!traceEvidenceList)return; const t=project.traceability||traceabilityTemplate(); const objects=project.objects.filter(o=>!o.archivedAt); const evidenceObjects=objects.filter(o=>o.type==='source'||o.type==='evidence'), analyses=objects.filter(o=>o.type==='analysis'), datasets=objects.filter(o=>o.type==='dataset'), evidenceOnly=objects.filter(o=>o.type==='evidence');
      if(traceMetricAssessments)traceMetricAssessments.textContent=String(t.evidenceAssessments.length); if(traceMetricLineage)traceMetricLineage.textContent=String(t.lineage.length); if(traceMetricRepro)traceMetricRepro.textContent=String(t.reproducibility.length); if(traceMetricVerified)traceMetricVerified.textContent=String(t.reproducibility.filter(x=>x.status==='verified').length);
      fillObjectSelect(traceEvidenceObject,evidenceObjects,'Choose a source or evidence object'); fillObjectSelect(traceLineageFrom,objects,'Choose an object'); fillObjectSelect(traceLineageTo,objects,'Choose an object'); fillObjectSelect(traceReproAnalysis,analyses,'No linked analysis object'); fillObjectSelect(traceReproDatasets,datasets); fillObjectSelect(traceReproEvidence,evidenceOnly);
      traceEvidenceList.innerHTML=''; if(!t.evidenceAssessments.length)traceEvidenceList.innerHTML='<div class="scw-trace-empty">No evidence assessments yet.</div>';
      t.evidenceAssessments.forEach((item)=>{const object=objectById(project,item.objectId);if(!object)return;const row=document.createElement('article');row.className='scw-trace-record';const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=object.title;const p=document.createElement('p');p.textContent=`Relevance ${item.relevance}/4 · Source quality ${item.sourceQuality}/4 · Independence ${item.independence}/4 · Recency ${item.recency}/4${item.note?` · ${item.note}`:''}`;const fp=document.createElement('small');fp.className=`scw-fingerprint ${item.fingerprintState==='changed'?'is-changed':item.fingerprintState==='match'?'is-match':''}`;fp.textContent=item.fingerprint?`SHA-256 ${item.fingerprint.slice(0,16)}… · ${item.fingerprintState}`:'Fingerprint unavailable';body.append(strong,p,fp);const acts=document.createElement('div');acts.className='scw-trace-actions';const review=document.createElement('button');review.type='button';review.className='scw-card-action';review.textContent='Review changes';review.addEventListener('click',()=>{setWorkspaceView('changes');populateChangeReviewSelectors(point.projectId,point.id,'current');activeChangeReview=null;renderChangeReview();if(changeStatus)changeStatus.textContent='Restore point selected as the base. Choose Review changes to compare it with the current project.';});const verify=document.createElement('button');verify.type='button';verify.className='scw-card-action';verify.textContent='Verify';verify.addEventListener('click',async()=>{const next=await sha256Object(object);item.fingerprintState=next&&item.fingerprint&&next===item.fingerprint?'match':'changed';item.updatedAt=nowIso();touchTraceability(project);persist('Evidence fingerprint checked');renderTraceability(project);});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{t.evidenceAssessments=t.evidenceAssessments.filter(x=>x.id!==item.id);touchTraceability(project);persist('Evidence assessment removed');renderTraceability(project);});acts.append(verify,remove);row.append(body,acts);traceEvidenceList.appendChild(row);});
      traceLineageList.innerHTML=''; if(!t.lineage.length)traceLineageList.innerHTML='<div class="scw-trace-empty">No lineage links yet.</div>'; t.lineage.forEach((item)=>{const from=objectById(project,item.fromObjectId),to=objectById(project,item.toObjectId);if(!from||!to)return;const row=document.createElement('article');row.className='scw-trace-record';const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=`${from.title} → ${to.title}`;const p=document.createElement('p');p.textContent=`${item.relation.replaceAll('-',' ')}${item.note?` · ${item.note}`:''}`;body.append(strong,p);const acts=document.createElement('div');acts.className='scw-trace-actions';const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{t.lineage=t.lineage.filter(x=>x.id!==item.id);touchTraceability(project);persist('Lineage link removed');renderTraceability(project);});acts.append(remove);row.append(body,acts);traceLineageList.appendChild(row);});
      traceReproList.innerHTML=''; if(!t.reproducibility.length)traceReproList.innerHTML='<div class="scw-trace-empty">No reproduction records yet.</div>'; t.reproducibility.forEach((item)=>{const row=document.createElement('article');row.className='scw-trace-record';const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=item.title;const p=document.createElement('p');p.textContent=`${item.status.toUpperCase()} · ${item.datasetObjectIds.length} dataset(s) · ${item.evidenceObjectIds.length} evidence input(s)${item.lastVerifiedAt?` · verified ${formatTime(item.lastVerifiedAt)}`:''}`;body.append(strong,p);const acts=document.createElement('div');acts.className='scw-trace-actions';const status=document.createElement('select');['draft','ready','verified','stale'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o)});status.value=item.status;status.addEventListener('change',()=>{item.status=REPRO_STATUS.has(status.value)?status.value:'draft';if(item.status==='verified')item.lastVerifiedAt=nowIso();item.updatedAt=nowIso();touchTraceability(project);persist('Reproduction status saved');renderTraceability(project);});const exp=document.createElement('button');exp.type='button';exp.className='scw-card-action';exp.textContent='Export package';exp.addEventListener('click',()=>{const ids=new Set([item.analysisObjectId,...item.datasetObjectIds,...item.evidenceObjectIds,...item.resultObjectIds].filter(Boolean));const payload={schema:REPRO_EXPORT_SCHEMA,workspaceVersion:root.dataset.version||'0.23.0',exportedAt:nowIso(),project:{id:project.id,title:project.title},record:JSON.parse(JSON.stringify(item)),referencedObjects:project.objects.filter(o=>ids.has(o.id)).map(o=>JSON.parse(JSON.stringify(o)))};downloadJson(`${safeFileName(item.title)}.sc-workspace-repro.json`,payload);addActivity(project,'repro-export',`Reproduction package exported: ${item.title}`);persist('Reproduction export recorded');});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{t.reproducibility=t.reproducibility.filter(x=>x.id!==item.id);touchTraceability(project);persist('Reproduction record removed');renderTraceability(project);});acts.append(status,exp,remove);row.append(body,acts);traceReproList.appendChild(row);});
    }


    function activeBriefingDraft(project){ return project&&project.briefing?project.briefing.drafts.find(d=>d.id===project.briefing.activeDraftId)||null:null; }
    function briefingCitationLines(project,draft){ return draft.objectIds.map(idv=>objectById(project,idv)).filter(Boolean).map((o,i)=>{const src=o.provenance||{};const origin=src.sourceTitle||src.sourceUrl||src.sourceType||'Workspace';return `${i+1}. ${o.title} — ${origin}`;}); }
    function briefingMarkdown(project,draft){ const lines=[`# ${draft.title}`,'',draft.audience?`**Audience:** ${draft.audience}`:'',draft.purpose?`**Purpose:** ${draft.purpose}`:'',`**Format:** ${draft.format.replaceAll('-',' ')}`,'']; draft.sections.forEach(sec=>{lines.push(`## ${sec.heading}`,'',sec.body||'','');}); const cites=briefingCitationLines(project,draft); if(cites.length)lines.push('## Basis','',...cites,''); return lines.filter((v,i,a)=>!(v===''&&a[i-1]==='')).join('\n')+'\n'; }
    function briefingHtml(project,draft){ const sections=draft.sections.map(sec=>`<section><h2>${escapeHtml(sec.heading)}</h2><p>${escapeHtml(sec.body).replaceAll('\n','<br>')}</p></section>`).join(''); const cites=briefingCitationLines(project,draft); const basis=cites.length?`<section><h2>Basis</h2><ol>${cites.map(x=>`<li>${escapeHtml(x.replace(/^\\d+\\.\\s*/,''))}</li>`).join('')}</ol></section>`:''; return `<!doctype html><html><head><meta charset="utf-8"><title>${escapeHtml(draft.title)}</title></head><body><main><h1>${escapeHtml(draft.title)}</h1>${draft.audience?`<p><strong>Audience:</strong> ${escapeHtml(draft.audience)}</p>`:''}${draft.purpose?`<p><strong>Purpose:</strong> ${escapeHtml(draft.purpose)}</p>`:''}${sections}${basis}</main></body></html>`; }
    function publicationPackage(project,draft){ const refs=new Set(draft.objectIds); draft.sections.forEach(sec=>sec.objectIds.forEach(v=>refs.add(v))); return {schema:PUBLICATION_EXPORT_SCHEMA,workspaceVersion:root.dataset.version||'0.23.0',exportedAt:nowIso(),automaticPublication:false,project:{id:project.id,title:project.title},draft:JSON.parse(JSON.stringify(draft)),referencedObjects:project.objects.filter(o=>refs.has(o.id)).map(o=>({id:o.id,type:o.type,title:o.title,summary:o.summary,status:o.status,tags:o.tags,provenance:o.provenance}))}; }
    function activeWorkflowRun(project){return project&&project.guidedWorkflows?project.guidedWorkflows.runs.find(r=>r.id===project.guidedWorkflows.activeRunId)||null:null;}
    function renderGuidedWorkflows(project){
      if(!workflowTemplateList)return;const defs=guidedWorkflowDefinitions(),g=project.guidedWorkflows||guidedWorkflowsTemplate(),run=activeWorkflowRun(project);const allSteps=g.runs.flatMap(r=>r.steps);
      if(workflowMetricRuns)workflowMetricRuns.textContent=String(g.runs.length);if(workflowMetricSteps)workflowMetricSteps.textContent=String(allSteps.filter(x=>x.status==='in-progress').length);if(workflowMetricComplete)workflowMetricComplete.textContent=String(allSteps.filter(x=>x.status==='complete').length);
      workflowTemplateList.innerHTML='';Object.entries(defs).forEach(([templateId,def])=>{const card=document.createElement('article');card.className='scw-workflow-template';const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=def.title;const p=document.createElement('p');p.textContent=def.description;const meta=document.createElement('small');meta.textContent=`${def.steps.length} visible steps · editable progress`;body.append(strong,p,meta);const start=document.createElement('button');start.type='button';start.className='scw-card-action';start.textContent='Start workflow';start.addEventListener('click',()=>{const next=startGuidedWorkflow(project,templateId);if(!next){window.alert('This project has reached the guided workflow limit.');return;}persist('Guided workflow started');renderGuidedWorkflows(project);});card.append(body,start);workflowTemplateList.appendChild(card);});
      if(workflowActive)workflowActive.textContent=run?`${run.title} · ${run.status}`:'No active guided workflow selected.';
      if(workflowRunList){workflowRunList.innerHTML='';if(!g.runs.length)workflowRunList.innerHTML='<div class="scw-workflow-empty">No guided workflows yet. Start from a template when structure would help; blank projects remain fully supported.</div>';g.runs.forEach(item=>{const row=document.createElement('article');row.className=`scw-workflow-run${item.id===g.activeRunId?' is-active':''}`;const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=item.title;const complete=item.steps.filter(x=>x.status==='complete').length;const p=document.createElement('p');p.textContent=`${item.status} · ${complete}/${item.steps.length} steps complete`;body.append(strong,p);const acts=document.createElement('div');acts.className='scw-workflow-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent=item.id===g.activeRunId?'Active':'Open';open.addEventListener('click',()=>{g.activeRunId=item.id;touchGuidedWorkflows(project);persist('Guided workflow opened');renderGuidedWorkflows(project);});const pause=document.createElement('button');pause.type='button';pause.className='scw-card-action';pause.textContent=item.status==='paused'?'Resume':'Pause';pause.disabled=item.status==='complete';pause.addEventListener('click',()=>{item.status=item.status==='paused'?'active':'paused';item.updatedAt=nowIso();touchGuidedWorkflows(project);persist('Workflow status saved');renderGuidedWorkflows(project);});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{if(!window.confirm(`Remove guided workflow “${item.title}”? Project content and objects will remain.`))return;g.runs=g.runs.filter(x=>x.id!==item.id);if(g.activeRunId===item.id)g.activeRunId=g.runs[0]?.id||null;touchGuidedWorkflows(project);persist('Guided workflow removed');renderGuidedWorkflows(project);});acts.append(open,pause,remove);row.append(body,acts);workflowRunList.appendChild(row);});}
      if(workflowStepList){workflowStepList.innerHTML='';if(!run)workflowStepList.innerHTML='<div class="scw-workflow-empty">Open a guided workflow to see its steps.</div>';else run.steps.forEach((step,index)=>{const row=document.createElement('article');row.className=`scw-workflow-step is-${step.status}`;const number=document.createElement('span');number.className='scw-workflow-step-number';number.textContent=String(index+1).padStart(2,'0');const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=step.title;const p=document.createElement('p');p.textContent=step.description;const note=document.createElement('textarea');note.rows=2;note.maxLength=2000;note.placeholder='Optional step note';note.value=step.note;note.addEventListener('input',()=>{step.note=note.value.slice(0,2000);step.updatedAt=nowIso();touchGuidedWorkflows(project);schedulePersist();});body.append(strong,p,note);const acts=document.createElement('div');acts.className='scw-workflow-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open workspace';open.addEventListener('click',()=>{run.currentStepId=step.id;if(step.status==='todo')step.status='in-progress';step.updatedAt=nowIso();run.updatedAt=step.updatedAt;touchGuidedWorkflows(project);persist('Workflow step opened');setProjectMode(step.mode);});const status=document.createElement('select');['todo','in-progress','complete','skipped'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v==='in-progress'?'In progress':v[0].toUpperCase()+v.slice(1);status.appendChild(o);});status.value=step.status;status.addEventListener('change',()=>{step.status=WORKFLOW_STEP_STATUS.has(status.value)?status.value:'todo';step.completedAt=step.status==='complete'?nowIso():null;step.updatedAt=nowIso();run.currentStepId=step.id;const unfinished=run.steps.some(x=>!['complete','skipped'].includes(x.status));run.status=unfinished?'active':'complete';run.completedAt=unfinished?null:nowIso();run.updatedAt=step.updatedAt;touchGuidedWorkflows(project);persist('Workflow step status saved');renderGuidedWorkflows(project);});acts.append(open,status);row.append(number,body,acts);workflowStepList.appendChild(row);});}
    }

    function renderAiAssistance(project){
      if(!aiSessionList)return; const a=project.aiAssistance||aiAssistanceTemplate(), session=activeAiSession(project), objects=project.objects.filter(o=>!o.archivedAt);
      if(aiMetricSessions)aiMetricSessions.textContent=a.sessions.length; if(aiMetricGrounding)aiMetricGrounding.textContent=a.sessions.reduce((n,x)=>n+x.objectIds.length,0); if(aiMetricResponses)aiMetricResponses.textContent=a.sessions.filter(x=>x.response).length; if(aiMetricAccepted)aiMetricAccepted.textContent=a.sessions.filter(x=>x.status==='accepted').length;
      if(aiSessionList){aiSessionList.innerHTML='';if(!a.sessions.length)aiSessionList.innerHTML='<div class="scw-ai-empty">No AI assistance requests yet. Prepare one from selected Workspace Objects when AI would help; nothing is sent automatically.</div>';a.sessions.forEach(item=>{const row=document.createElement('article');row.className=`scw-ai-session${item.id===a.activeSessionId?' is-active':''}`;const body=document.createElement('div');const meta=document.createElement('span');meta.textContent=`${aiTaskLabel(item.task)} · ${item.status.replaceAll('-',' ')}`;const strong=document.createElement('strong');strong.textContent=item.title;const p=document.createElement('p');p.textContent=`${item.objectIds.length} grounding object(s)${item.response?` · response ${item.response.length.toLocaleString()} chars`:''}`;body.append(meta,strong,p);const actions=document.createElement('div');actions.className='scw-ai-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent=item.id===a.activeSessionId?'Active':'Open';open.addEventListener('click',()=>{a.activeSessionId=item.id;touchAiAssistance(project);persist('AI request opened');renderAiAssistance(project);});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{if(!window.confirm(`Remove AI assistance request “${item.title}”? Accepted Workspace Objects will remain.`))return;a.sessions=a.sessions.filter(x=>x.id!==item.id);if(a.activeSessionId===item.id)a.activeSessionId=a.sessions[0]?.id||null;touchAiAssistance(project);persist('AI request removed');renderAiAssistance(project);});actions.append(open,remove);row.append(body,actions);aiSessionList.appendChild(row);});}
      if(aiActive)aiActive.textContent=session?`${session.title} · ${aiTaskLabel(session.task)} · ${session.status.replaceAll('-',' ')}`:'No active AI assistance request.';
      if(aiObjectSelect){aiObjectSelect.innerHTML='';objects.forEach(o=>{const opt=document.createElement('option');opt.value=o.id;opt.textContent=`${OBJECT_LABELS[o.type]||o.type} · ${o.title}`;opt.selected=Boolean(session&&session.objectIds.includes(o.id));aiObjectSelect.appendChild(opt);});}
      if(aiCitationSelect){aiCitationSelect.innerHTML='';const allowed=session?new Set(session.objectIds):new Set();objects.filter(o=>allowed.has(o.id)).forEach(o=>{const opt=document.createElement('option');opt.value=o.id;opt.textContent=`${OBJECT_LABELS[o.type]||o.type} · ${o.title}`;opt.selected=Boolean(session&&session.citationObjectIds.includes(o.id));aiCitationSelect.appendChild(opt);});}
      if(aiResponse)aiResponse.value=session?session.response:''; if(aiResponseSource)aiResponseSource.value=session?session.responseSource:'manual';
      const disabled=!session;[aiResponse,aiCitationSelect,aiResponseSource,aiSaveResponse,aiCopyPrompt,aiExportRequest,aiOpenLibrarian,aiAcceptDocument,aiReject,aiExportResponse].forEach(el=>{if(el)el.disabled=disabled;});
      if(aiGrounding){aiGrounding.innerHTML='';if(!session)aiGrounding.innerHTML='<div class="scw-ai-empty">Open a request to inspect its grounding basis.</div>';else{const selected=aiSelectedObjects(project,session);const sourceCount=selected.filter(o=>['source','evidence'].includes(o.type)).length, provenanceCount=selected.filter(o=>o.provenance&&(o.provenance.sourceTitle||o.provenance.sourceUrl||o.provenance.capturedAt)).length;const summary=document.createElement('div');summary.className='scw-ai-grounding-summary';summary.innerHTML=`<strong>${selected.length} selected object(s)</strong><span>${sourceCount} source/evidence · ${provenanceCount} with provenance</span><small>Only these selected Workspace Objects are included in the prepared request package.</small>`;aiGrounding.appendChild(summary);selected.forEach(o=>{const row=document.createElement('article');row.innerHTML=`<span>${escapeHtml(OBJECT_LABELS[o.type]||o.type)}</span><strong>${escapeHtml(o.title)}</strong><small>${escapeHtml(o.provenance?.sourceTitle||o.provenance?.sourceUrl||'Manual Workspace object')}</small>`;aiGrounding.appendChild(row);});}}
    }

    function renderBriefing(project){
      if(!briefingDraftList)return; const b=project.briefing||briefingTemplate(), draft=activeBriefingDraft(project), objects=project.objects.filter(o=>!o.archivedAt);
      if(briefingMetricDrafts)briefingMetricDrafts.textContent=String(b.drafts.length); if(briefingMetricReady)briefingMetricReady.textContent=String(b.drafts.filter(d=>d.status==='ready'||d.status==='exported').length); if(briefingMetricRefs)briefingMetricRefs.textContent=String(b.drafts.reduce((n,d)=>n+d.objectIds.length,0)); if(briefingMetricDocs)briefingMetricDocs.textContent=String(b.drafts.filter(d=>d.documentObjectId&&objectById(project,d.documentObjectId)).length);
      if(briefingActive)briefingActive.textContent=draft?`${draft.title} · ${draft.format.replaceAll('-',' ')}`:'No active draft selected.';
      briefingDraftList.innerHTML=''; if(!b.drafts.length)briefingDraftList.innerHTML='<div class="scw-briefing-empty">No briefing or publication drafts yet.</div>';
      b.drafts.forEach(item=>{const row=document.createElement('article');row.className=`scw-briefing-record${item.id===b.activeDraftId?' is-active':''}`;const body=document.createElement('div');const strong=document.createElement('strong');strong.textContent=item.title;const p=document.createElement('p');p.textContent=`${item.format.replaceAll('-',' ')} · ${item.status} · ${item.sections.length} section(s) · ${item.objectIds.length} reference(s)`;body.append(strong,p);const acts=document.createElement('div');acts.className='scw-briefing-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent=item.id===b.activeDraftId?'Active':'Open';open.addEventListener('click',()=>{b.activeDraftId=item.id;touchBriefing(project);persist('Draft opened');renderBriefing(project);});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{if(!window.confirm(`Remove draft “${item.title}”? The materialized Document, if any, will remain in Objects.`))return;b.drafts=b.drafts.filter(d=>d.id!==item.id);if(b.activeDraftId===item.id)b.activeDraftId=b.drafts[0]?.id||null;touchBriefing(project);persist('Draft removed');renderBriefing(project);});acts.append(open,remove);row.append(body,acts);briefingDraftList.appendChild(row);});
      fillObjectSelect(briefingObjectSelect,objects); if(briefingObjectSelect){Array.from(briefingObjectSelect.options).forEach(o=>{o.selected=Boolean(draft&&draft.objectIds.includes(o.value));});}
      [briefingSaveBasis,briefingOutlineButton,briefingStatus,briefingMaterialize,briefingExportMarkdown,briefingExportHtml,briefingExportPackage].forEach(el=>{if(el)el.disabled=!draft;}); if(briefingSectionForm)Array.from(briefingSectionForm.elements).forEach(el=>{if(el.matches('input,textarea,button'))el.disabled=!draft;}); if(briefingStatus&&draft)briefingStatus.value=draft.status;
      if(briefingBasisList){briefingBasisList.innerHTML=''; if(!draft||!draft.objectIds.length)briefingBasisList.innerHTML='<div class="scw-briefing-empty">No Workspace Objects selected as the basis yet.</div>'; else draft.objectIds.map(v=>objectById(project,v)).filter(Boolean).forEach(o=>{const row=document.createElement('div');row.className='scw-briefing-basis-item';row.innerHTML=`<strong>${escapeHtml(o.title)}</strong><span>${escapeHtml(OBJECT_LABELS[o.type]||o.type)}</span>`;briefingBasisList.appendChild(row);});}
      if(briefingSectionList){briefingSectionList.innerHTML=''; if(!draft||!draft.sections.length)briefingSectionList.innerHTML='<div class="scw-briefing-empty">No sections yet. Add one or build a standard outline.</div>'; else draft.sections.forEach((sec,index)=>{const row=document.createElement('article');row.className='scw-briefing-section-record';const fields=document.createElement('div');const heading=document.createElement('input');heading.type='text';heading.maxLength=180;heading.value=sec.heading;heading.setAttribute('aria-label','Section heading');const body=document.createElement('textarea');body.rows=5;body.maxLength=8000;body.value=sec.body;body.setAttribute('aria-label','Section text');heading.addEventListener('input',()=>{sec.heading=heading.value.slice(0,180);sec.updatedAt=nowIso();touchBriefing(project);schedulePersist();});body.addEventListener('input',()=>{sec.body=body.value.slice(0,8000);sec.updatedAt=nowIso();touchBriefing(project);schedulePersist();});fields.append(heading,body);const acts=document.createElement('div');acts.className='scw-briefing-actions';const up=document.createElement('button');up.type='button';up.className='scw-card-action';up.textContent='↑';up.disabled=index===0;up.addEventListener('click',()=>{[draft.sections[index-1],draft.sections[index]]=[draft.sections[index],draft.sections[index-1]];touchBriefing(project);persist('Section moved');renderBriefing(project);});const down=document.createElement('button');down.type='button';down.className='scw-card-action';down.textContent='↓';down.disabled=index===draft.sections.length-1;down.addEventListener('click',()=>{[draft.sections[index+1],draft.sections[index]]=[draft.sections[index],draft.sections[index+1]];touchBriefing(project);persist('Section moved');renderBriefing(project);});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{draft.sections=draft.sections.filter(x=>x.id!==sec.id);touchBriefing(project);persist('Section removed');renderBriefing(project);});acts.append(up,down,remove);row.append(fields,acts);briefingSectionList.appendChild(row);});}
    }

    function openActivityProject(projectId, mode='overview') {
      const project=state.projects.find(p=>p.id===projectId&&!p.archivedAt); if(!project)return;
      state.activeProjectId=project.id; activeProjectMode=mode || 'overview'; persist('Project opened from Activity'); render(); setWorkspaceView('projects'); setProjectMode(activeProjectMode);
      activePanel.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
    }

    function renderActivityIntelligence() {
      if (!activityIntelligenceSection) return;
      state.activityIntelligence=normalizeActivityIntelligence(state.activityIntelligence,state.projects);
      const ai=state.activityIntelligence, prefs=ai.preferences;
      const projects=state.projects.filter(p=>!p.archivedAt).sort(projectSort);
      const fillProjects=(select,allowAll)=>{if(!select)return;const current=select.value;select.innerHTML=allowAll?'<option value="all">All projects</option>':'<option value="">Choose project</option>';projects.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.title;select.appendChild(o);});if([...select.options].some(o=>o.value===current))select.value=current;};
      fillProjects(activityProject,true); fillProjects(nextActionProject,false);
      if(activityProject)activityProject.value=prefs.project;
      if(activityWindow)activityWindow.value=String(prefs.windowDays);
      if(activityStale)activityStale.value=String(prefs.staleDays);
      if(activitySignal)activitySignal.value=prefs.signal;
      const signals=derivedAttentionSignals(state), timeline=workspaceActivityTimeline(state), workflows=workflowIntelligenceRows(state), openActions=ai.nextActions.filter(a=>a.status==='open' && (prefs.project==='all'||a.projectId===prefs.project));
      if(activityMetricProjects)activityMetricProjects.textContent=String(projects.length);
      if(activityMetricActions)activityMetricActions.textContent=String(openActions.length);
      if(activityMetricSignals)activityMetricSignals.textContent=String(signals.length);
      if(activityMetricChanges)activityMetricChanges.textContent=String(timeline.length);
      if(nextActionList){nextActionList.innerHTML='';const actions=ai.nextActions.filter(a=>prefs.project==='all'||a.projectId===prefs.project).sort((a,b)=>{const status=(a.status==='open'?0:1)-(b.status==='open'?0:1);if(status)return status;return String(a.dueAt||'9999').localeCompare(String(b.dueAt||'9999'))||String(b.updatedAt).localeCompare(String(a.updatedAt));});if(!actions.length)nextActionList.innerHTML='<div class="scw-activity-intelligence-empty">No next actions yet.</div>';actions.forEach(action=>{const project=state.projects.find(p=>p.id===action.projectId);if(!project)return;const row=document.createElement('article');row.className=`scw-next-action-row${action.status!=='open'?' is-resolved':''}`;const body=document.createElement('div');body.innerHTML=`<span>${escapeHtml(action.priority.toUpperCase())}${action.dueAt?` · DUE ${escapeHtml(new Date(action.dueAt).toLocaleDateString())}`:''}</span><strong>${escapeHtml(action.title)}</strong><small>${escapeHtml(project.title)} · ${escapeHtml(action.status.toUpperCase())}</small>`;const acts=document.createElement('div');acts.className='scw-activity-row-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open project';open.addEventListener('click',()=>openActivityProject(project.id));const status=document.createElement('select');['open','done','deferred'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v[0].toUpperCase()+v.slice(1);status.appendChild(o);});status.value=action.status;status.addEventListener('change',()=>{action.status=NEXT_ACTION_STATUS.has(status.value)?status.value:'open';action.updatedAt=nowIso();action.completedAt=action.status==='done'?nowIso():null;touchActivityIntelligence();persist('Next action status saved');renderActivityIntelligence();});const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove';remove.addEventListener('click',()=>{ai.nextActions=ai.nextActions.filter(x=>x.id!==action.id);touchActivityIntelligence();persist('Next action removed');renderActivityIntelligence();});acts.append(open,status,remove);row.append(body,acts);nextActionList.appendChild(row);});}
      if(attentionList){attentionList.innerHTML='';if(!signals.length)attentionList.innerHTML='<div class="scw-activity-intelligence-empty">No visible attention signals for these filters.</div>';signals.slice(0,100).forEach(signal=>{const project=state.projects.find(p=>p.id===signal.projectId);if(!project)return;const row=document.createElement('article');row.className=`scw-attention-row is-${signal.severity}`;const body=document.createElement('div');body.innerHTML=`<span>${escapeHtml(signal.kind.toUpperCase())} · ${escapeHtml(signal.severity.toUpperCase())}</span><strong>${escapeHtml(signal.title)}</strong><p>${escapeHtml(signal.detail)}</p><small>${escapeHtml(project.title)}</small>`;const acts=document.createElement('div');acts.className='scw-activity-row-actions';const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open';open.addEventListener('click',()=>openActivityProject(project.id,signal.targetMode));const dismiss=document.createElement('button');dismiss.type='button';dismiss.className='scw-card-action scw-card-action-muted';dismiss.textContent='Dismiss';dismiss.addEventListener('click',()=>{ai.dismissedSignalIds=[signal.id,...ai.dismissedSignalIds.filter(v=>v!==signal.id)].slice(0,MAX_DISMISSED_SIGNALS);touchActivityIntelligence();persist('Attention signal dismissed');renderActivityIntelligence();});acts.append(open,dismiss);row.append(body,acts);attentionList.appendChild(row);});}
      if(workflowIntelligenceList){workflowIntelligenceList.innerHTML='';if(!workflows.length)workflowIntelligenceList.innerHTML='<div class="scw-activity-intelligence-empty">No active or paused guided workflows.</div>';workflows.slice(0,80).forEach(item=>{const row=document.createElement('button');row.type='button';row.className='scw-workflow-intelligence-row';row.innerHTML=`<span>${escapeHtml(item.status.toUpperCase())} · ${item.complete}/${item.total} steps</span><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.projectTitle)}${item.next?` · Next: ${escapeHtml(item.next.title)}`:''}</small>`;row.addEventListener('click',()=>openActivityProject(item.projectId,'guide'));workflowIntelligenceList.appendChild(row);});}
      if(workspaceActivityTimelineEl){workspaceActivityTimelineEl.innerHTML='';if(!timeline.length)workspaceActivityTimelineEl.innerHTML='<div class="scw-activity-intelligence-empty">No recorded project activity in this window.</div>';timeline.forEach(item=>{const row=document.createElement('button');row.type='button';row.className='scw-workspace-activity-row';row.innerHTML=`<span>${escapeHtml(String(item.type||'updated').replaceAll('-',' ').toUpperCase())}</span><strong>${escapeHtml(item.summary)}</strong><small>${escapeHtml(item.projectTitle)} · ${escapeHtml(formatTime(item.at))}</small>`;row.addEventListener('click',()=>openActivityProject(item.projectId));workspaceActivityTimelineEl.appendChild(row);});}
    }

    function recordVersionHistory(action,point){state.versionHistory=normalizeVersionHistory(state.versionHistory,state.projects);state.versionHistory.history.unshift({id:id('vhh'),action,restorePointId:point?.id||'',projectId:point?.projectId||'',projectTitle:point?.projectTitle||'',label:point?.label||'',at:nowIso()});state.versionHistory.history=state.versionHistory.history.slice(0,MAX_VERSION_HISTORY_EVENTS);state.versionHistory.updatedAt=nowIso();}
    async function createRestorePoint(project,label,note='',source='manual'){state.versionHistory=normalizeVersionHistory(state.versionHistory,state.projects);const existing=state.versionHistory.restorePoints.filter(item=>item.projectId===project.id);if(existing.length>=MAX_RESTORE_POINTS_PER_PROJECT)throw new Error(`This project already has ${MAX_RESTORE_POINTS_PER_PROJECT} restore points. Delete an older point before creating another.`);if(state.versionHistory.restorePoints.length>=MAX_RESTORE_POINTS)throw new Error(`Workspace has reached the ${MAX_RESTORE_POINTS} restore-point limit. Delete an older point before creating another.`);const snapshot=versionHistorySnapshot(project),bytes=approximateBytes(snapshot);if(bytes>MAX_RESTORE_POINT_BYTES)throw new Error(`This project snapshot is ${(bytes/1024/1024).toFixed(2)} MB. Restore points are limited to ${(MAX_RESTORE_POINT_BYTES/1024/1024).toFixed(1)} MB each.`);const fingerprint=await sha256Text(JSON.stringify(snapshot));if(!fingerprint)throw new Error('This browser cannot calculate the SHA-256 fingerprint required for a restore point.');const point={schema:RESTORE_POINT_SCHEMA,id:id('rpt'),projectId:project.id,projectTitle:project.title,label:String(label||'Restore point').trim().slice(0,120),note:String(note||'').trim().slice(0,1200),source,createdAt:nowIso(),projectUpdatedAt:project.updatedAt,fingerprint,bytes,snapshot};state.versionHistory.restorePoints.unshift(point);recordVersionHistory('create',point);return point;}
    async function compareRestorePoint(point){const current=state.projects.find(project=>project.id===point.projectId)||null;if(!current)return 'The source project is no longer present locally. The restore point can still be restored as a copy.';const fingerprint=await sha256Text(JSON.stringify(versionHistorySnapshot(current)));if(!fingerprint)return 'This browser cannot calculate a current SHA-256 fingerprint.';return fingerprint===point.fingerprint?'Current project matches this restore point exactly.':`Current project differs from this restore point. Current SHA-256 ${fingerprint.slice(0,12)}… · point ${point.fingerprint.slice(0,12)}…`;}
    function renderVersionHistory(){if(!versionHistorySection)return;state.versionHistory=normalizeVersionHistory(state.versionHistory,state.projects);const projects=state.projects.filter(project=>!project.archivedAt),selected=historyProject?.value||state.versionHistory.selectedProjectId||activeProject()?.id||'';if(historyProject){const current=selected;historyProject.innerHTML='<option value="">Choose project</option>';projects.forEach(project=>{const o=document.createElement('option');o.value=project.id;o.textContent=project.title;historyProject.appendChild(o);});if(projects.some(p=>p.id===current))historyProject.value=current;}if(historyFilter){const current=historyFilter.value||'all';historyFilter.innerHTML='<option value="all">All projects</option>';state.projects.forEach(project=>{const o=document.createElement('option');o.value=project.id;o.textContent=project.title;historyFilter.appendChild(o);});if(current==='all'||state.projects.some(p=>p.id===current))historyFilter.value=current;}const points=state.versionHistory.restorePoints;if(historyMetricPoints)historyMetricPoints.textContent=String(points.length);if(historyMetricProjects)historyMetricProjects.textContent=String(new Set(points.map(point=>point.projectId)).size);if(historyMetricBytes)historyMetricBytes.textContent=`${(points.reduce((sum,point)=>sum+(point.bytes||0),0)/1024).toFixed(1)} KB`;if(historyMetricNewest)historyMetricNewest.textContent=points[0]?formatTime(points[0].createdAt):'None';if(historyList){historyList.innerHTML='';const filterId=historyFilter?.value||'all',visible=points.filter(point=>filterId==='all'||point.projectId===filterId);if(!visible.length)historyList.innerHTML='<div class="scw-version-history-empty">No restore points in this view yet.</div>';visible.forEach(point=>{const card=document.createElement('article');card.className='scw-version-history-card';const meta=document.createElement('div');meta.innerHTML=`<span>${escapeHtml(point.projectTitle)}</span><strong>${escapeHtml(point.label)}</strong><p>${escapeHtml(point.note||'No note.')}</p><small>Captured ${escapeHtml(formatTime(point.createdAt))} · project state ${escapeHtml(formatTime(point.projectUpdatedAt))} · ${(point.bytes/1024).toFixed(1)} KB · SHA-256 ${escapeHtml(point.fingerprint.slice(0,16))}…</small>`;const acts=document.createElement('div');acts.className='scw-version-history-actions';const compare=document.createElement('button');compare.type='button';compare.className='scw-card-action';compare.textContent='Compare current';compare.addEventListener('click',async()=>{if(historyStatus)historyStatus.textContent='Comparing fingerprints…';if(historyStatus)historyStatus.textContent=await compareRestorePoint(point);});const verify=document.createElement('button');verify.type='button';verify.className='scw-card-action';verify.textContent='Verify';verify.addEventListener('click',async()=>{const fp=await sha256Text(JSON.stringify(point.snapshot)),ok=Boolean(fp&&fp===point.fingerprint);recordVersionHistory('verify',point);persist('Restore point integrity checked');if(historyStatus)historyStatus.textContent=ok?'Restore point SHA-256 integrity verified.':'Restore point fingerprint does not match its stored snapshot. Do not rely on this point until you export and inspect it.';renderVersionHistory();});const restore=document.createElement('button');restore.type='button';restore.className='scw-card-action';restore.textContent='Restore as copy';restore.addEventListener('click',async()=>{const current=state.projects.find(project=>project.id===point.projectId)||point.snapshot;await openSafeActionGate({action:'restore-copy',project:current,baseProject:point.snapshot,baseMeta:{kind:'restore-point',restorePointId:point.id,id:point.id,label:point.label},targetProject:current,targetMeta:{kind:'current-project',id:current.id,label:'Current project'},perform:async()=>{const copy=cloneProject(point.snapshot);copy.title=`${point.projectTitle} (Restored: ${point.label})`.slice(0,120);addActivity(copy,'restore-point',`Restored from local point: ${point.label}`);state.projects.unshift(copy);state.activeProjectId=copy.id;recordVersionHistory('restore-copy',point);persist('Restore point opened as new project copy');render();setWorkspaceView('projects');}});});const exp=document.createElement('button');exp.type='button';exp.className='scw-card-action';exp.textContent='Export';exp.addEventListener('click',()=>{downloadJson(`${safeFileName(point.projectTitle)}-${safeFileName(point.label)}.sc-workspace-restore-point.json`,restorePointExport(point));recordVersionHistory('export',point);persist('Restore point exported');renderVersionHistory();});const del=document.createElement('button');del.type='button';del.className='scw-card-action scw-card-action-muted';del.textContent='Delete';del.addEventListener('click',()=>{if(!window.confirm(`Delete restore point “${point.label}”? The source project will not be changed.`))return;recordVersionHistory('delete',point);state.versionHistory.restorePoints=state.versionHistory.restorePoints.filter(item=>item.id!==point.id);persist('Restore point deleted');renderVersionHistory();});acts.append(compare,review,verify,restore,exp,del);card.append(meta,acts);historyList.appendChild(card);});}if(historyEvents){historyEvents.innerHTML='';const events=state.versionHistory.history.slice(0,16);if(!events.length)historyEvents.innerHTML='<div class="scw-version-history-empty">No version-history activity yet.</div>';events.forEach(item=>{const row=document.createElement('div');row.className='scw-version-history-event';row.innerHTML=`<strong>${escapeHtml(item.action.replaceAll('-',' ').toUpperCase())}</strong><span>${escapeHtml(item.projectTitle||'Project')} · ${escapeHtml(item.label||'Restore point')}</span><small>${escapeHtml(formatTime(item.at))}</small>`;historyEvents.appendChild(row);});}}

    function changeReviewProject(){return state.projects.find(project=>project.id===changeProject?.value)||null;}
    function changeReviewPoint(idValue){return state.versionHistory?.restorePoints?.find(point=>point.id===idValue)||null;}
    function populateChangeReviewSelectors(preferredProject='',preferredBase=null,preferredTarget=null){
      if(!changeProject||!changeBase||!changeTarget)return;
      state.versionHistory=normalizeVersionHistory(state.versionHistory,state.projects);
      const selectedBase=preferredBase!==null?preferredBase:(changeBase.value||'');
      const selectedTarget=preferredTarget!==null?preferredTarget:(changeTarget.value||'current');
      const currentProject=preferredProject||changeProject.value||activeProject()?.id||'';
      changeProject.innerHTML='<option value="">Choose project</option>';
      state.projects.filter(p=>!p.archivedAt).forEach(project=>{const o=document.createElement('option');o.value=project.id;o.textContent=project.title;changeProject.appendChild(o);});
      if(state.projects.some(p=>p.id===currentProject&&!p.archivedAt))changeProject.value=currentProject;
      const projectId=changeProject.value, points=state.versionHistory.restorePoints.filter(point=>point.projectId===projectId);
      changeBase.innerHTML='<option value="">Choose a restore point</option>';points.forEach(point=>{const o=document.createElement('option');o.value=point.id;o.textContent=`${point.label} · ${formatTime(point.createdAt)}`;changeBase.appendChild(o);});
      if(points.some(p=>p.id===selectedBase))changeBase.value=selectedBase;
      changeTarget.innerHTML='<option value="current">Current project</option>';points.forEach(point=>{const o=document.createElement('option');o.value=point.id;o.textContent=`Restore point: ${point.label}`;changeTarget.appendChild(o);});
      if(selectedTarget==='current'||points.some(p=>p.id===selectedTarget))changeTarget.value=selectedTarget;
      changeBase.disabled=!projectId||!points.length;changeTarget.disabled=!projectId||!points.length;changeRun.disabled=!projectId||!changeBase.value;
      if(!points.length&&projectId&&changeStatus)changeStatus.textContent='This project has no restore points yet. Create one in History before comparing changes.';
    }
    function renderChangeReview(review=null){
      if(!changeReviewSection)return;populateChangeReviewSelectors();const r=review||activeChangeReview;
      if(changeAdded)changeAdded.textContent=String(r?.summary?.added||0);if(changeRemoved)changeRemoved.textContent=String(r?.summary?.removed||0);if(changeModified)changeModified.textContent=String(r?.summary?.modified||0);if(changeRelationships)changeRelationships.textContent=String(r?.summary?.relationshipsChanged||0);
      if(changeAttention){changeAttention.innerHTML='';(r?.attention||[]).forEach(text=>{const span=document.createElement('span');span.textContent=text;changeAttention.appendChild(span);});}
      if(changeResults){changeResults.innerHTML='';if(!r){changeResults.innerHTML='<div class="scw-change-review-empty">No comparison generated yet.</div>';}else if(!r.summary.total){changeResults.innerHTML='<div class="scw-change-review-empty">No meaningful project changes were detected between these states.</div>';}else{r.categories.forEach(category=>{const group=document.createElement('section');group.className='scw-change-review-category';const h=document.createElement('div');h.className='scw-change-review-category-head';h.innerHTML=`<strong>${escapeHtml(category.category)}</strong><span>${category.changes.length} change${category.changes.length===1?'':'s'}${category.kind==='relationship'?' · relationship':''}</span>`;const list=document.createElement('div');category.changes.forEach(change=>{const row=document.createElement('article');row.className=`scw-change-review-row is-${change.change}`;row.innerHTML=`<span>${escapeHtml(change.change.toUpperCase())}</span><strong>${escapeHtml(change.label)}</strong><small>${change.fields?.length?`Fields: ${escapeHtml(change.fields.join(', '))}`:'Record '+escapeHtml(change.change)}</small>`;list.appendChild(row);});group.append(h,list);changeResults.appendChild(group);});}}
      if(changeExport)changeExport.disabled=!r;
    }
    function generateChangeReview(){
      const project=changeReviewProject(),base=changeReviewPoint(changeBase?.value||'');if(!project||!base)return null;let targetProject=project,targetMeta={kind:'current-project',label:'Current project',updatedAt:project.updatedAt};if(changeTarget?.value&&changeTarget.value!=='current'){const point=changeReviewPoint(changeTarget.value);if(!point)return null;targetProject=point.snapshot;targetMeta={kind:'restore-point',restorePointId:point.id,label:point.label,capturedAt:point.createdAt,fingerprint:point.fingerprint};}
      const engine=window.SCWorkspaceProjectDiff;if(!engine||typeof engine.compareProjects!=='function'){if(changeStatus)changeStatus.textContent='Change Review engine is unavailable. Reload the page and try again.';return null;}
      const review=engine.compareProjects(base.snapshot,targetProject,{base:{kind:'restore-point',restorePointId:base.id,label:base.label,capturedAt:base.createdAt,fingerprint:base.fingerprint},target:targetMeta});activeChangeReview=review;if(changeStatus)changeStatus.textContent=review.summary.total?`${review.summary.total} explicit changes across ${review.summary.categoriesChanged} categories. Review before taking any action.`:'These states match on the meaningful fields reviewed by Workspace.';renderChangeReview(review);return review;
    }

    function latestRestorePoint(projectId){return (state.versionHistory?.restorePoints||[]).filter(point=>point.projectId===projectId).sort((a,b)=>Date.parse(b.createdAt)-Date.parse(a.createdAt))[0]||null;}
    function recordSafeAction(gate,outcome){const helper=window.SCWorkspaceSafeActions;if(!helper||!gate)return;state.safeActions=normalizeSafeActions(state.safeActions,state.projects);state.safeActions.history.unshift(helper.historyRecord(gate,outcome,nowIso()));state.safeActions.history=state.safeActions.history.slice(0,MAX_SAFE_ACTION_HISTORY);state.safeActions.updatedAt=nowIso();}
    function renderSafeActions(){if(!safeActionsSection)return;state.safeActions=normalizeSafeActions(state.safeActions,state.projects);const rows=state.safeActions.history;if(safeMetricTotal)safeMetricTotal.textContent=String(rows.length);if(safeMetricProceeded)safeMetricProceeded.textContent=String(rows.filter(row=>row.outcome==='proceeded').length);if(safeMetricCancelled)safeMetricCancelled.textContent=String(rows.filter(row=>row.outcome==='cancelled').length);if(safeMetricChanges)safeMetricChanges.textContent=String(rows.reduce((sum,row)=>sum+(row.reviewSummary?.total||0),0));if(safeHistory){safeHistory.innerHTML='';if(!rows.length){safeHistory.innerHTML='<div class="scw-safe-actions-empty">No gated actions have been recorded yet.</div>';return;}rows.slice(0,30).forEach(row=>{const el=document.createElement('article');el.className='scw-safe-actions-record';el.innerHTML=`<div><span>${escapeHtml(row.outcome.toUpperCase())}</span><strong>${escapeHtml(row.actionLabel)}</strong><p>${escapeHtml(row.projectTitle)}</p><small>${row.reviewAvailable?`${escapeHtml(row.reviewSummary.total)} explicit changes reviewed`:'No comparison baseline available'} · ${escapeHtml(row.baseline?.label||'No baseline')} · ${escapeHtml(formatTime(row.at))}</small></div>`;safeHistory.appendChild(el);});}}
    function closeSafeActionGate(outcome='cancelled'){if(activeSafeGate&&outcome)recordSafeAction(activeSafeGate,outcome);if(outcome)persist(`Safe action ${outcome}`);activeSafeGate=null;activeSafeAction=null;if(actionGate){actionGate.hidden=true;actionGate.setAttribute('aria-hidden','true');}if(actionGateAck)actionGateAck.checked=false;if(actionGateProceed)actionGateProceed.disabled=true;renderSafeActions();}
    async function openSafeActionGate({action,project,baseProject=null,baseMeta=null,targetProject=null,targetMeta=null,perform}){
      const helper=window.SCWorkspaceSafeActions,engine=window.SCWorkspaceProjectDiff;if(!helper||!project||typeof perform!=='function')throw new Error('Safe Action gate is unavailable.');let review=null;
      if(baseProject&&targetProject&&engine&&typeof engine.compareProjects==='function'){review=engine.compareProjects(baseProject,targetProject,{base:baseMeta||{kind:'restore-point',label:'Baseline'},target:targetMeta||{kind:'current-project',label:'Current project'}});}
      const gate=helper.buildGate({id:id('sag'),action,projectId:project.id,projectTitle:project.title,review,baseline:baseMeta||{kind:'none',label:'No named comparison baseline'},target:targetMeta||{kind:'current-project',label:'Current project'},checkpointRestorePointId:baseMeta?.restorePointId||''});
      activeSafeGate=gate;activeSafeAction=perform;if(actionGateTitle)actionGateTitle.textContent=`${gate.actionLabel} — preflight`;if(actionGateIntro)actionGateIntro.textContent=`${project.title}. Review the meaningful differences and the action boundary before proceeding.`;if(actionGateAckText)actionGateAckText.textContent=gate.requiredAcknowledgement;if(actionGateStatus)actionGateStatus.textContent=gate.reviewAvailable?'Change Review generated. Nothing has been applied.':'No earlier comparison baseline is available. Review the action boundary carefully before proceeding.';
      if(actionGateReview){if(review){const flags=(review.attention||[]).map(flag=>`<li>${escapeHtml(flag)}</li>`).join('');actionGateReview.innerHTML=`<div class="scw-action-gate-summary"><strong>${escapeHtml(review.summary.total)} explicit changes</strong><span>${escapeHtml(review.summary.added)} added · ${escapeHtml(review.summary.removed)} removed · ${escapeHtml(review.summary.modified)} modified · ${escapeHtml(review.summary.relationshipsChanged)} relationship changes</span></div>${flags?`<ul>${flags}</ul>`:'<p>No attention labels were triggered.</p>'}<small>${escapeHtml(gate.baseline.label)} → ${escapeHtml(gate.target.label)}</small>`;}else actionGateReview.innerHTML=`<div class="scw-action-gate-summary"><strong>No prior comparison state</strong><span>This action can still proceed only after explicit acknowledgement. Create named restore points to make future preflights more informative.</span></div>`;}
      if(actionGateAck)actionGateAck.checked=false;if(actionGateProceed)actionGateProceed.disabled=true;if(actionGate){actionGate.hidden=false;actionGate.setAttribute('aria-hidden','false');}setTimeout(()=>actionGateAck?.focus(),0);return gate;
    }
    async function gateFromLatestRestore(action,project,perform){const point=latestRestorePoint(project.id);return openSafeActionGate({action,project,baseProject:point?.snapshot||null,baseMeta:point?{kind:'restore-point',restorePointId:point.id,id:point.id,label:point.label}:{kind:'none',label:'No named restore point'},targetProject:project,targetMeta:{kind:'current-project',id:project.id,label:'Current project'},perform});}

    function setWorkspaceView(view, moveFocus = false) {
      workspaceView = ['projects','knowledge','graph','activity','history','changes','safety','interoperability','collaboration','institutional','share'].includes(view) ? view : 'projects';
      root.querySelectorAll('[data-scw-workspace-view]').forEach(button => {
        const selected = button.dataset.scwWorkspaceView === workspaceView;
        button.classList.toggle('is-active', selected);
        button.setAttribute('aria-pressed', selected ? 'true' : 'false');
      });
      if (projectsSection) projectsSection.hidden = workspaceView !== 'projects';
      if (activePanel) activePanel.hidden = workspaceView !== 'projects' || !activeProject();
      if (knowledgeSection) knowledgeSection.hidden = workspaceView !== 'knowledge';
      if (graphSection) graphSection.hidden = workspaceView !== 'graph';
      if (activityIntelligenceSection) activityIntelligenceSection.hidden = workspaceView !== 'activity';
      if (versionHistorySection) versionHistorySection.hidden = workspaceView !== 'history';
      if (changeReviewSection) changeReviewSection.hidden = workspaceView !== 'changes';
      if (safeActionsSection) safeActionsSection.hidden = workspaceView !== 'safety';
      if (interoperabilitySection) interoperabilitySection.hidden = workspaceView !== 'interoperability';
      if (collaborationSection) collaborationSection.hidden = workspaceView !== 'collaboration';
      if (institutionalSection) institutionalSection.hidden = workspaceView !== 'institutional';
      if (shareSection) shareSection.hidden = workspaceView !== 'share';
      if (connectionsDrawer) connectionsDrawer.hidden = workspaceView !== 'projects';
      if (workspaceView === 'knowledge') renderKnowledge();
      if (workspaceView === 'graph') renderKnowledgeGraph();
      if (workspaceView === 'activity') renderActivityIntelligence();
      if (workspaceView === 'history') renderVersionHistory();
      if (workspaceView === 'changes') renderChangeReview();
      if (workspaceView === 'interoperability') renderInteroperability();
      if (workspaceView === 'collaboration') renderCollaboration();
      if (workspaceView === 'institutional') renderInstitutional();
      if (workspaceView === 'share') renderShare();
      if (workspaceView === 'safety') renderSafeActions();
      if (moveFocus) {
        const section = root.querySelector(`[data-scw-workspace-section="${workspaceView}"]`);
        const heading = section && section.querySelector('h2, h3');
        if (heading) {
          if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
          heading.focus({ preventScroll: true });
          heading.scrollIntoView({ behavior: prefersReducedMotion() ? 'auto' : 'smooth', block: 'start' });
        }
      }
    }

    function openKnowledgeEntry(entry) {
      const project = state.projects.find(p => p.id === entry.projectId && !p.archivedAt);
      if (!project) { window.alert('This object belongs to an archived project. Restore that project before opening it.'); return; }
      state.activeProjectId = project.id;
      project.activeObjectId = entry.objectId;
      state.updatedAt = nowIso();
      persist('Knowledge item opened');
      workspaceView = 'projects';
      setProjectMode('objects');
      render();
      activePanel.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' });
    }

    function activeKnowledgeCollection() {
      return state.knowledge?.collections.find(c => c.id === state.knowledge.activeCollectionId) || null;
    }

    function renderKnowledgeCollectionDetail(index) {
      if (!knowledgeCollectionDetail) return;
      const collection = activeKnowledgeCollection();
      knowledgeCollectionDetail.innerHTML = '';
      if (!collection) { knowledgeCollectionDetail.innerHTML = '<div class="scw-knowledge-empty-note">Select or create a collection to organize reusable objects across projects.</div>'; return; }
      const head = document.createElement('div'); head.className='scw-knowledge-collection-head';
      const body=document.createElement('div'); const strong=document.createElement('strong');strong.textContent=collection.title;const p=document.createElement('p');p.textContent=collection.description||'No collection description.';body.append(strong,p);
      const acts=document.createElement('div');acts.className='scw-knowledge-actions';
      const exp=document.createElement('button');exp.type='button';exp.className='scw-card-action';exp.textContent='Export JSON';exp.addEventListener('click',()=>{const payload={schema:KNOWLEDGE_COLLECTION_EXPORT_SCHEMA,workspaceVersion:root.dataset.version||'0.23.0',exportedAt:nowIso(),collection:JSON.parse(JSON.stringify(collection)),objects:collection.items.map(ref=>{const e=index.find(x=>x.projectId===ref.projectId&&x.objectId===ref.objectId);return e?{project:{id:e.projectId,title:e.projectTitle},object:JSON.parse(JSON.stringify(e.object))}:null;}).filter(Boolean)};downloadJson(`${safeFileName(collection.title)}.sc-workspace-knowledge.json`,payload);});
      const remove=document.createElement('button');remove.type='button';remove.className='scw-card-action scw-card-action-muted';remove.textContent='Remove collection';remove.addEventListener('click',()=>{if(!window.confirm(`Remove collection “${collection.title}”? Workspace Objects will not be deleted.`))return;state.knowledge.collections=state.knowledge.collections.filter(c=>c.id!==collection.id);state.knowledge.activeCollectionId=state.knowledge.collections[0]?.id||null;touchKnowledge();persist('Knowledge collection removed');renderKnowledge();});acts.append(exp,remove);head.append(body,acts);knowledgeCollectionDetail.appendChild(head);
      const list=document.createElement('div');list.className='scw-knowledge-collection-items';
      if(!collection.items.length)list.innerHTML='<div class="scw-knowledge-empty-note">No objects in this collection yet.</div>';
      collection.items.forEach(ref=>{const e=index.find(x=>x.projectId===ref.projectId&&x.objectId===ref.objectId);if(!e)return;const row=document.createElement('article');const meta=document.createElement('span');meta.textContent=`${OBJECT_LABELS[e.object.type]||e.object.type} · ${e.projectTitle}`;const title=document.createElement('strong');title.textContent=e.object.title;const removeItem=document.createElement('button');removeItem.type='button';removeItem.className='scw-card-action scw-card-action-muted';removeItem.textContent='Remove';removeItem.addEventListener('click',()=>{collection.items=collection.items.filter(x=>!(x.projectId===ref.projectId&&x.objectId===ref.objectId));collection.updatedAt=nowIso();touchKnowledge();persist('Collection updated');renderKnowledge();});row.append(meta,title,removeItem);list.appendChild(row);});knowledgeCollectionDetail.appendChild(list);
    }

    function renderInteroperability(){
      const projects=state.projects.filter(p=>!p.archivedAt);
      [interoperabilityProject,interoperabilityExportProject].forEach(sel=>{if(!sel)return;const current=sel.value;sel.innerHTML='<option value="">Choose project</option>';projects.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.title;sel.appendChild(o);});if(projects.some(p=>p.id===current))sel.value=current;else if(state.activeProjectId&&projects.some(p=>p.id===state.activeProjectId))sel.value=state.activeProjectId;});
      if(interoperabilityStage){interoperabilityStage.innerHTML='';if(!stagedInteroperability){interoperabilityStage.innerHTML='<span>No file staged.</span>';}else{const head=document.createElement('div');head.className='scw-interoperability-stage-head';head.innerHTML=`<strong>${escapeHtml(stagedInteroperability.fileName)}</strong><span>${escapeHtml(stagedInteroperability.format.toUpperCase())} · ${stagedInteroperability.objects.length} object(s) · SHA-256 ${escapeHtml(stagedInteroperability.fingerprint?stagedInteroperability.fingerprint.slice(0,16)+'…':'unavailable')}</span>`;const list=document.createElement('div');list.className='scw-interoperability-preview-list';stagedInteroperability.objects.slice(0,20).forEach(o=>{const row=document.createElement('article');row.innerHTML=`<span>${escapeHtml(OBJECT_LABELS[o.type]||o.type)}</span><strong>${escapeHtml(o.title)}</strong><small>${escapeHtml(o.summary||'Imported artifact')}</small>`;list.appendChild(row);});if(stagedInteroperability.objects.length>20){const more=document.createElement('small');more.textContent=`+ ${stagedInteroperability.objects.length-20} additional object(s)`;list.appendChild(more);}interoperabilityStage.append(head,list);}}
      if(interoperabilityCommit)interoperabilityCommit.disabled=!stagedInteroperability||!stagedInteroperability.objects.length;if(interoperabilityClear)interoperabilityClear.disabled=!stagedInteroperability;
      if(interoperabilityHistory){interoperabilityHistory.innerHTML='';const hist=state.interoperability&&state.interoperability.history||[];if(!hist.length){interoperabilityHistory.innerHTML='<div class="scw-analysis-empty">No import or interchange export activity yet.</div>';}hist.forEach(item=>{const row=document.createElement('article');row.className='scw-interoperability-history-row';row.innerHTML=`<span>${escapeHtml(item.direction.toUpperCase())} · ${escapeHtml(item.format.toUpperCase())}</span><strong>${escapeHtml(item.fileName||item.projectTitle||'Workspace package')}</strong><small>${escapeHtml(item.projectTitle)} · ${item.objectCount} object(s) · ${escapeHtml(formatTime(item.at))}</small>`;interoperabilityHistory.appendChild(row);});}
    }

    function openCollaborationProject(projectId,objectId=''){const project=state.projects.find(p=>p.id===projectId&&!p.archivedAt);if(!project)return;state.activeProjectId=project.id;if(objectId&&project.objects.some(o=>o.id===objectId&&!o.archivedAt)){project.activeObjectId=objectId;activeProjectMode='objects';}else activeProjectMode='overview';persist('Project opened from collaboration review');render();setWorkspaceView('projects');setProjectMode(activeProjectMode);activePanel.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});}
    function renderCollaboration(){if(!collaborationSection)return;state.collaboration=normalizeCollaboration(state.collaboration,state.projects);const c=state.collaboration,session=activeCollaborationSession(),projects=state.projects.filter(p=>!p.archivedAt).sort(projectSort);if(collabProfileForm){const name=collabProfileForm.querySelector('[name="displayName"]'),role=collabProfileForm.querySelector('[name="role"]');if(name&&document.activeElement!==name)name.value=c.profile.displayName;if(role)role.value=c.profile.role;}
      if(collabProject){const cur=collabProject.value;collabProject.innerHTML='<option value="">Choose project</option>';projects.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.title;collabProject.appendChild(o);});if(projects.some(p=>p.id===cur))collabProject.value=cur;else if(state.activeProjectId&&projects.some(p=>p.id===state.activeProjectId))collabProject.value=state.activeProjectId;}
      const openThreads=c.sessions.reduce((n,s)=>n+s.threads.filter(t=>t.status==='open').length,0),people=new Set();c.sessions.forEach(s=>s.participants.forEach(p=>people.add(`${p.displayName}|${p.role}`)));if(c.profile.displayName)people.add(`${c.profile.displayName}|${c.profile.role}`);if(collabMetricSessions)collabMetricSessions.textContent=String(c.sessions.length);if(collabMetricOpen)collabMetricOpen.textContent=String(openThreads);if(collabMetricPeople)collabMetricPeople.textContent=String(people.size);if(collabMetricResponses)collabMetricResponses.textContent=String(c.sessions.reduce((n,s)=>n+s.importedResponseCount,0));
      if(collabSessionList){collabSessionList.innerHTML='';if(!c.sessions.length)collabSessionList.innerHTML='<div class="scw-collaboration-empty">No collaboration review sessions yet. Create one when a project needs structured external review.</div>';c.sessions.forEach(s=>{const project=state.projects.find(p=>p.id===s.localProjectId);const row=document.createElement('button');row.type='button';row.className=`scw-collaboration-session${s.id===c.activeSessionId?' is-active':''}`;const open=s.threads.filter(t=>t.status==='open').length;row.innerHTML=`<span>${escapeHtml(s.status.toUpperCase().replaceAll('-',' '))} · ${open} OPEN</span><strong>${escapeHtml(s.title)}</strong><small>${escapeHtml(project?.title||'Unavailable project')} · ${escapeHtml(s.requestedRole)}</small>`;row.addEventListener('click',()=>{c.activeSessionId=s.id;touchCollaboration();persist('Review session opened');renderCollaboration();});collabSessionList.appendChild(row);});}
      if(collabActive){collabActive.innerHTML='';if(!session){collabActive.innerHTML='<div class="scw-collaboration-empty">Open a review session to inspect its responsibility, status, and threads.</div>';if(collabThreadForm)collabThreadForm.hidden=true;}else{const project=state.projects.find(p=>p.id===session.localProjectId);const head=document.createElement('div');head.className='scw-collaboration-active-head';head.innerHTML=`<span>${escapeHtml(session.status.toUpperCase().replaceAll('-',' '))} · ${escapeHtml(session.requestedRole.toUpperCase())}</span><strong>${escapeHtml(session.title)}</strong><p>${escapeHtml(session.purpose||'No review purpose recorded.')}</p><small>${escapeHtml(project?.title||'Unavailable project')} · source ${escapeHtml(session.sourceProjectId)}</small>`;const controls=document.createElement('div');controls.className='scw-collaboration-actions';const status=document.createElement('select');['draft','requested','in-review','changes-requested','approved','closed'].forEach(v=>{const o=document.createElement('option');o.value=v;o.textContent=v.replaceAll('-',' ').replace(/\b\w/g,m=>m.toUpperCase());status.appendChild(o);});status.value=session.status;status.addEventListener('change',()=>{session.status=COLLAB_SESSION_STATUS.has(status.value)?status.value:session.status;session.updatedAt=nowIso();session.closedAt=session.status==='closed'?nowIso():null;touchCollaboration();persist('Review status saved');renderCollaboration();});const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open project';open.addEventListener('click',()=>openCollaborationProject(session.localProjectId));controls.append(status,open);collabActive.append(head,controls);if(collabThreadForm)collabThreadForm.hidden=false;if(collabObject){collabObject.innerHTML='<option value="">Project-level review</option>';if(project)project.objects.filter(o=>!o.archivedAt).forEach(o=>{const opt=document.createElement('option');opt.value=o.id;opt.textContent=`${OBJECT_LABELS[o.type]||o.type}: ${o.title}`;collabObject.appendChild(opt);});}}}
      if(collabThreadList){collabThreadList.innerHTML='';if(!session||!session.threads.length)collabThreadList.innerHTML='<div class="scw-collaboration-empty">No review threads yet.</div>';if(session)session.threads.slice().sort((a,b)=>String(b.updatedAt).localeCompare(String(a.updatedAt))).forEach(t=>{const project=state.projects.find(p=>p.id===session.localProjectId),obj=project?.objects.find(o=>o.id===t.objectId);const row=document.createElement('article');row.className=`scw-collaboration-thread${t.status==='resolved'?' is-resolved':''}`;const body=document.createElement('div');body.innerHTML=`<span>${escapeHtml(t.kind.toUpperCase())} · ${escapeHtml(t.authorRole.toUpperCase())} · ${escapeHtml(t.status.toUpperCase())}</span><strong>${escapeHtml(t.authorLabel)}</strong><p>${escapeHtml(t.body)}</p><small>${obj?`Object: ${escapeHtml(obj.title)}`:'Project-level review'} · ${escapeHtml(formatTime(t.updatedAt))}</small>`;const acts=document.createElement('div');acts.className='scw-collaboration-actions';if(obj){const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open object';open.addEventListener('click',()=>openCollaborationProject(session.localProjectId,obj.id));acts.appendChild(open);}const resolve=document.createElement('button');resolve.type='button';resolve.className='scw-card-action';resolve.textContent=t.status==='resolved'?'Reopen':'Resolve';resolve.addEventListener('click',()=>{t.status=t.status==='resolved'?'open':'resolved';t.resolvedAt=t.status==='resolved'?nowIso():null;t.updatedAt=nowIso();session.updatedAt=t.updatedAt;touchCollaboration();persist('Review thread status saved');renderCollaboration();});acts.appendChild(resolve);row.append(body,acts);collabThreadList.appendChild(row);});}
      if(collabStage){collabStage.innerHTML='';if(!stagedReviewPackage)collabStage.innerHTML='<span>No review package staged.</span>';else{const pkg=stagedReviewPackage.package,request=pkg.request||{};collabStage.innerHTML=`<strong>${escapeHtml(stagedReviewPackage.fileName)}</strong><span>${escapeHtml(pkg.kind.toUpperCase())} · ${escapeHtml(request.title||'Workspace review')} · ${Array.isArray(pkg.threads)?pkg.threads.length:0} thread(s)</span><small>${escapeHtml(stagedReviewPackage.verification.message)}</small>`;}}if(collabCommit)collabCommit.disabled=!stagedReviewPackage||!stagedReviewPackage.verification.ok;if(collabClear)collabClear.disabled=!stagedReviewPackage;
      if(collabHistory){collabHistory.innerHTML='';if(!c.history.length)collabHistory.innerHTML='<div class="scw-collaboration-empty">No portable review exchange yet.</div>';c.history.forEach(h=>{const row=document.createElement('article');row.className='scw-collaboration-history-row';row.innerHTML=`<span>${escapeHtml(h.direction.toUpperCase())} · ${escapeHtml(h.kind.toUpperCase())}</span><strong>${escapeHtml(h.fileName||h.projectTitle)}</strong><small>${escapeHtml(h.projectTitle)} · ${h.threadCount} thread(s) · ${escapeHtml(formatTime(h.at))}</small>`;collabHistory.appendChild(row);});}
    }

    function renderInstitutionalObjectScope(projectId,selectedIds=null){
      if(!institutionalObjectScope)return;const project=state.projects.find(p=>p.id===projectId&&!p.archivedAt);institutionalObjectScope.innerHTML='';
      if(!project){institutionalObjectScope.innerHTML='<span>Choose a project to review its canonical objects.</span>';return;}
      const objects=project.objects.filter(o=>!o.archivedAt),selected=selectedIds?new Set(selectedIds):new Set(objects.map(o=>o.id));
      if(!objects.length){institutionalObjectScope.innerHTML='<span>This project has no active canonical Workspace Objects to promote.</span>';return;}
      const toolbar=document.createElement('div');toolbar.className='scw-institutional-scope-actions';const all=document.createElement('button');all.type='button';all.className='scw-card-action';all.textContent='Select all';all.addEventListener('click',()=>institutionalObjectScope.querySelectorAll('input[type="checkbox"]').forEach(x=>x.checked=true));const none=document.createElement('button');none.type='button';none.className='scw-card-action scw-card-action-muted';none.textContent='Clear';none.addEventListener('click',()=>institutionalObjectScope.querySelectorAll('input[type="checkbox"]').forEach(x=>x.checked=false));toolbar.append(all,none);institutionalObjectScope.appendChild(toolbar);
      objects.forEach(o=>{const label=document.createElement('label');label.className='scw-institutional-object-choice';const input=document.createElement('input');input.type='checkbox';input.name='objectIds[]';input.value=o.id;input.checked=selected.has(o.id);const text=document.createElement('span');text.innerHTML=`<strong>${escapeHtml(OBJECT_LABELS[o.type]||o.type)} · ${escapeHtml(o.title)}</strong><small>${escapeHtml(o.provenance?.sourceTitle||o.provenance?.sourceType||'Manual provenance')}</small>`;label.append(input,text);institutionalObjectScope.appendChild(label);});
    }
    function renderInstitutional(){
      if(!institutionalSection)return;state.institutional=normalizeInstitutional(state.institutional,state.projects);const ih=state.institutional,projects=state.projects.filter(p=>!p.archivedAt).sort(projectSort),active=activeInstitutionalHandoff();
      if(institutionalProject){const current=institutionalProject.value;institutionalProject.innerHTML='<option value="">Choose project</option>';projects.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.title;institutionalProject.appendChild(o);});if(projects.some(p=>p.id===current))institutionalProject.value=current;else if(state.activeProjectId&&projects.some(p=>p.id===state.activeProjectId))institutionalProject.value=state.activeProjectId;if(!institutionalObjectScope.querySelector('input[type="checkbox"]')||institutionalObjectScope.dataset.projectId!==institutionalProject.value){institutionalObjectScope.dataset.projectId=institutionalProject.value;renderInstitutionalObjectScope(institutionalProject.value);}}
      if(institutionalMetricTotal)institutionalMetricTotal.textContent=String(ih.handoffs.length);if(institutionalMetricExported)institutionalMetricExported.textContent=String(ih.handoffs.filter(h=>['exported','received','accepted','declined','closed'].includes(h.status)).length);if(institutionalMetricReceived)institutionalMetricReceived.textContent=String(ih.handoffs.filter(h=>['received','accepted','declined','closed'].includes(h.status)&&h.receiptAt).length);if(institutionalMetricAccepted)institutionalMetricAccepted.textContent=String(ih.handoffs.filter(h=>h.status==='accepted').length);
      if(institutionalList){institutionalList.innerHTML='';if(!ih.handoffs.length)institutionalList.innerHTML='<div class="scw-institutional-empty">No institutional handoffs yet. Prepare one only when personal Workspace material is ready to enter a governed institutional environment.</div>';ih.handoffs.forEach(h=>{const project=state.projects.find(p=>p.id===h.projectId);const b=document.createElement('button');b.type='button';b.className=`scw-institutional-row${h.id===ih.activeHandoffId?' is-active':''}`;b.innerHTML=`<span>${escapeHtml(h.status.toUpperCase())} · ${h.objectIds.length} OBJECT${h.objectIds.length===1?'':'S'}</span><strong>${escapeHtml(h.organizationLabel||'Catalyst Intelligence')}</strong><small>${escapeHtml(project?.title||'Unavailable project')} · ${escapeHtml(formatTime(h.updatedAt))}</small>`;b.addEventListener('click',()=>{ih.activeHandoffId=h.id;touchInstitutional();persist('Institutional handoff opened');renderInstitutional();});institutionalList.appendChild(b);});}
      if(institutionalActive){institutionalActive.innerHTML='';if(!active){institutionalActive.innerHTML='<div class="scw-institutional-empty">Prepare or open an institutional handoff to inspect scope and readiness.</div>';}else{const project=state.projects.find(p=>p.id===active.projectId),head=document.createElement('div');head.className='scw-institutional-active-head';head.innerHTML=`<span>${escapeHtml(active.status.toUpperCase())} · CATALYST INTELLIGENCE</span><strong>${escapeHtml(active.organizationLabel||'Institutional destination')}</strong><p>${escapeHtml(active.purpose||'No promotion purpose recorded.')}</p><small>${escapeHtml(project?.title||'Unavailable project')} · Handoff ${escapeHtml(active.id)}</small>`;const scope=document.createElement('div');scope.className='scw-institutional-active-scope';active.objectIds.forEach(oid=>{const o=project?.objects.find(x=>x.id===oid);if(!o)return;const row=document.createElement('div');row.innerHTML=`<span>${escapeHtml(OBJECT_LABELS[o.type]||o.type)}</span><strong>${escapeHtml(o.title)}</strong>`;scope.appendChild(row);});institutionalActive.append(head,scope);}}
      if(institutionalReadinessEl){institutionalReadinessEl.innerHTML='';if(active){const project=state.projects.find(p=>p.id===active.projectId);institutionalReadiness(project,active.objectIds).forEach(check=>{const row=document.createElement('article');row.className=`scw-institutional-check is-${check.status}`;row.innerHTML=`<span>${check.status==='ready'?'READY':'ATTENTION'}</span><strong>${escapeHtml(check.label)}</strong><p>${escapeHtml(check.detail)}</p>`;institutionalReadinessEl.appendChild(row);});}else institutionalReadinessEl.innerHTML='<div class="scw-institutional-empty">Readiness checks are shown as explicit conditions, never as a composite score.</div>';}
      const exportable=Boolean(active&&active.objectIds.length&&active.acknowledgements.copyModel&&active.acknowledgements.institutionalGovernance&&active.acknowledgements.sharingReviewed&&active.status!=='closed');if(institutionalExport)institutionalExport.disabled=!exportable;if(institutionalClose)institutionalClose.disabled=!active||active.status==='closed';
      if(institutionalStage){if(!stagedInstitutionalReceipt)institutionalStage.innerHTML='<span>No institutional receipt staged.</span>';else institutionalStage.innerHTML=`<strong>${escapeHtml(stagedInstitutionalReceipt.fileName)}</strong><span>${escapeHtml(stagedInstitutionalReceipt.verification.message)} · ${escapeHtml(String(stagedInstitutionalReceipt.package.status||'').toUpperCase())}</span><small>Handoff ${escapeHtml(String(stagedInstitutionalReceipt.package.handoffId||''))}</small>`;}if(institutionalCommit)institutionalCommit.disabled=!stagedInstitutionalReceipt||!stagedInstitutionalReceipt.verification.ok;if(institutionalClear)institutionalClear.disabled=!stagedInstitutionalReceipt;
      if(institutionalHistory){institutionalHistory.innerHTML='';if(!ih.history.length)institutionalHistory.innerHTML='<div class="scw-institutional-empty">No institutional package or receipt activity yet.</div>';ih.history.forEach(h=>{const row=document.createElement('article');row.className='scw-institutional-history-row';row.innerHTML=`<span>${escapeHtml(h.direction.toUpperCase())} · ${h.kind==='receipt'?'RECEIPT':'PROMOTION'} · ${escapeHtml(h.status.toUpperCase())}</span><strong>${escapeHtml(h.organizationLabel||h.projectTitle||'Institutional handoff')}</strong><small>${escapeHtml(h.fileName||'')} · ${h.objectCount} object(s) · ${escapeHtml(formatTime(h.at))}</small>`;institutionalHistory.appendChild(row);});}
    }

    function renderShare(){
      const projects=state.projects.filter(p=>!p.archivedAt);if(shareProject){const current=shareProject.value;shareProject.innerHTML='<option value="">Choose project</option>';projects.forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=p.title;shareProject.appendChild(o);});if(projects.some(p=>p.id===current))shareProject.value=current;else if(state.activeProjectId&&projects.some(p=>p.id===state.activeProjectId))shareProject.value=state.activeProjectId;}
      if(shareStage){shareStage.innerHTML='';if(!stagedPortableProject)shareStage.innerHTML='<span>No portable project staged.</span>';else{const p=stagedPortableProject.package,verification=stagedPortableProject.verification;shareStage.innerHTML=`<strong>${escapeHtml(p.manifest?.projectTitle||p.project?.title||'Portable project')}</strong><span>${escapeHtml(verification.message)} · ${Number(p.manifest?.objectCount||p.project?.objects?.length||0)} object(s)</span><small>${escapeHtml(stagedPortableProject.fileName)}</small>`;}}
      if(shareImport)shareImport.disabled=!stagedPortableProject||!stagedPortableProject.verification.ok;if(shareClear)shareClear.disabled=!stagedPortableProject;
      if(shareHistory){shareHistory.innerHTML='';const hist=state.share&&state.share.history||[];if(!hist.length)shareHistory.innerHTML='<div class="scw-analysis-empty">No portable project sharing activity yet.</div>';hist.forEach(item=>{const row=document.createElement('article');row.className='scw-share-history-row';row.innerHTML=`<span>${escapeHtml(item.direction.toUpperCase())} · ${item.kind==='review-html'?'REVIEW COPY':'PORTABLE PROJECT'}</span><strong>${escapeHtml(item.fileName||item.projectTitle)}</strong><small>${escapeHtml(item.projectTitle)} · ${item.objectCount} object(s) · ${escapeHtml(formatTime(item.at))}</small>`;shareHistory.appendChild(row);});}
    }

    function renderKnowledge() {
      if (!knowledgeSection) return;
      state.knowledge = normalizeKnowledge(state.knowledge, state.projects);
      const index = knowledgeIndex();
      const prefs = state.knowledge.preferences;
      if (knowledgeSearch && document.activeElement !== knowledgeSearch) knowledgeSearch.value = prefs.query;
      if (knowledgeType) knowledgeType.value = prefs.type;
      if (knowledgeTag && document.activeElement !== knowledgeTag) knowledgeTag.value = prefs.tag;
      if (knowledgeScope) knowledgeScope.value = prefs.scope;
      if (knowledgeProject) {
        const current = prefs.project;
        knowledgeProject.innerHTML='<option value="all">All projects</option>';
        state.projects.slice().sort(projectSort).forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=`${p.title}${p.archivedAt?' (archived)':''}`;knowledgeProject.appendChild(o);});
        knowledgeProject.value = Array.from(knowledgeProject.options).some(o=>o.value===current)?current:'all';
      }
      const tagSet=new Set();index.forEach(e=>e.object.tags.forEach(t=>tagSet.add(t.toLowerCase())));
      const projectSet=new Set(index.map(e=>e.projectId));
      if(knowledgeMetricObjects)knowledgeMetricObjects.textContent=String(index.length);
      if(knowledgeMetricProjects)knowledgeMetricProjects.textContent=String(projectSet.size);
      if(knowledgeMetricCollections)knowledgeMetricCollections.textContent=String(state.knowledge.collections.length);
      if(knowledgeMetricTags)knowledgeMetricTags.textContent=String(tagSet.size);
      const q=prefs.query.trim().toLowerCase(), tag=prefs.tag.trim().toLowerCase();
      const filtered=index.filter(e=>{
        if(prefs.scope==='active'&&e.projectArchived)return false;
        if(prefs.type!=='all'&&e.object.type!==prefs.type)return false;
        if(prefs.project!=='all'&&e.projectId!==prefs.project)return false;
        if(tag&&!e.object.tags.some(t=>t.toLowerCase().includes(tag)))return false;
        if(q){const hay=[e.projectTitle,e.object.title,e.object.summary,e.object.content,e.object.tags.join(' '),e.object.provenance?.sourceTitle||'',e.object.provenance?.sourceUrl||''].join(' ').toLowerCase();if(!hay.includes(q))return false;}
        return true;
      });
      if(knowledgeResults){knowledgeResults.innerHTML='';filtered.forEach(e=>{const card=document.createElement('article');card.className=`scw-knowledge-result${selectedKnowledgeKey===e.key?' is-selected':''}`;const meta=document.createElement('span');meta.className='scw-knowledge-result-meta';meta.textContent=`${OBJECT_LABELS[e.object.type]||e.object.type} · ${e.projectTitle}`;const title=document.createElement('strong');title.textContent=e.object.title;const summary=document.createElement('p');summary.textContent=e.object.summary||'No summary yet.';const tags=document.createElement('small');tags.textContent=e.object.tags.length?e.object.tags.join(' · '):'No tags';const actions=document.createElement('div');actions.className='scw-knowledge-actions';const inspect=document.createElement('button');inspect.type='button';inspect.className='scw-card-action';inspect.textContent='Inspect';inspect.addEventListener('click',()=>{selectedKnowledgeKey=e.key;renderKnowledge();});const open=document.createElement('button');open.type='button';open.className='scw-card-action';open.textContent='Open in project';open.addEventListener('click',()=>openKnowledgeEntry(e));const add=document.createElement('button');add.type='button';add.className='scw-card-action';add.textContent='Add to collection';add.disabled=!state.knowledge.collections.length;add.addEventListener('click',()=>{const c=activeKnowledgeCollection()||state.knowledge.collections[0];if(!c)return;const key=e.key;if(!c.items.some(ref=>`${ref.projectId}:${ref.objectId}`===key)&&c.items.length<MAX_KNOWLEDGE_COLLECTION_ITEMS)c.items.push({projectId:e.projectId,objectId:e.objectId});c.updatedAt=nowIso();state.knowledge.activeCollectionId=c.id;touchKnowledge();persist('Added to knowledge collection');renderKnowledge();});actions.append(inspect,open,add);card.append(meta,title,summary,tags,actions);knowledgeResults.appendChild(card);});}
      if(knowledgeEmpty)knowledgeEmpty.hidden=filtered.length>0;
      if(knowledgeDetail){knowledgeDetail.innerHTML='';const selected=index.find(x=>x.key===selectedKnowledgeKey);if(!selected){knowledgeDetail.innerHTML='<div class="scw-knowledge-empty-note">Inspect an object to see provenance, backlinks, and transparent related-work signals.</div>';}else{const h=document.createElement('div');h.className='scw-knowledge-detail-head';h.innerHTML=`<span>${escapeHtml(OBJECT_LABELS[selected.object.type]||selected.object.type)} · ${escapeHtml(selected.projectTitle)}</span><strong>${escapeHtml(selected.object.title)}</strong><p>${escapeHtml(selected.object.summary||'No summary yet.')}</p>`;const prov=document.createElement('div');prov.className='scw-knowledge-provenance';prov.innerHTML=`<span>PROVENANCE</span><strong>${escapeHtml(selected.object.provenance?.sourceTitle||selected.object.provenance?.sourceType||'Manual')}</strong><small>${escapeHtml(selected.object.provenance?.sourceUrl||'No source URL')}</small><em>${knowledgeReferenceCount(selected)} internal reference(s)</em>`;const related=relatedKnowledgeEntries(selected,index);const rel=document.createElement('div');rel.className='scw-knowledge-related';const label=document.createElement('span');label.textContent='RELATED WORK';rel.appendChild(label);if(!related.length){const none=document.createElement('small');none.textContent='No deterministic related-work signals yet. Add shared tags or provenance to improve discovery.';rel.appendChild(none);}related.forEach(r=>{const row=document.createElement('button');row.type='button';row.className='scw-knowledge-related-item';row.innerHTML=`<strong>${escapeHtml(r.entry.object.title)}</strong><small>${escapeHtml(r.entry.projectTitle)} · ${escapeHtml(r.reasons.join(' · ')||'same object type')}</small>`;row.addEventListener('click',()=>{selectedKnowledgeKey=r.entry.key;renderKnowledge();});rel.appendChild(row);});knowledgeDetail.append(h,prov,rel);}}
      if(knowledgeCollectionSelect){knowledgeCollectionSelect.innerHTML='<option value="">Select collection</option>';state.knowledge.collections.forEach(c=>{const o=document.createElement('option');o.value=c.id;o.textContent=`${c.title} (${c.items.length})`;knowledgeCollectionSelect.appendChild(o);});knowledgeCollectionSelect.value=state.knowledge.activeCollectionId||'';}
      if(knowledgeCollectionList){knowledgeCollectionList.innerHTML='';state.knowledge.collections.forEach(c=>{const b=document.createElement('button');b.type='button';b.className=`scw-knowledge-collection-chip${c.id===state.knowledge.activeCollectionId?' is-active':''}`;b.textContent=`${c.title} · ${c.items.length}`;b.addEventListener('click',()=>{state.knowledge.activeCollectionId=c.id;touchKnowledge();persist('Knowledge collection opened');renderKnowledge();});knowledgeCollectionList.appendChild(b);});}
      renderKnowledgeCollectionDetail(index);
    }



    function graphNodeLabel(node){return node.type==='project'?'Project':node.type==='provenance'?'Provenance':(OBJECT_LABELS[node.type]||node.type);}
    function openGraphNode(node){if(!node)return;if(node.type==='project'){const project=state.projects.find(p=>p.id===node.projectId&&!p.archivedAt);if(!project)return;state.activeProjectId=project.id;persist('Project opened from Knowledge Graph');render();setWorkspaceView('projects');activePanel.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});return;}if(node.objectId){openKnowledgeEntry({projectId:node.projectId,objectId:node.objectId,key:`${node.projectId}:${node.objectId}`,object:state.projects.find(p=>p.id===node.projectId)?.objects.find(o=>o.id===node.objectId)});}}
    function renderGraphSvg(focus,neighborhood){if(!graphSvg)return;while(graphSvg.firstChild)graphSvg.removeChild(graphSvg.firstChild);graphSvg.setAttribute('viewBox','0 0 760 430');const NS='http://www.w3.org/2000/svg';if(!focus){const t=document.createElementNS(NS,'text');t.setAttribute('x','380');t.setAttribute('y','215');t.setAttribute('text-anchor','middle');t.setAttribute('class','scw-graph-svg-empty');t.textContent='Select a graph node to inspect its neighborhood.';graphSvg.appendChild(t);return;}const others=neighborhood.nodes.filter(n=>n.id!==focus.id).slice(0,14),cx=380,cy=215,radius=155;const positions=new Map([[focus.id,{x:cx,y:cy}]]);others.forEach((n,i)=>{const angle=(Math.PI*2*i/Math.max(others.length,1))-Math.PI/2;positions.set(n.id,{x:cx+Math.cos(angle)*radius,y:cy+Math.sin(angle)*radius});});neighborhood.edges.forEach(edge=>{const a=positions.get(edge.from),b=positions.get(edge.to);if(!a||!b)return;const line=document.createElementNS(NS,'line');line.setAttribute('x1',a.x);line.setAttribute('y1',a.y);line.setAttribute('x2',b.x);line.setAttribute('y2',b.y);line.setAttribute('class','scw-graph-edge');graphSvg.appendChild(line);});[focus,...others].forEach(node=>{const p=positions.get(node.id),g=document.createElementNS(NS,'g');g.setAttribute('class',`scw-graph-node scw-graph-node-${node.type}${node.id===focus.id?' is-focus':''}`);g.setAttribute('tabindex','0');g.setAttribute('role','button');g.setAttribute('aria-label',`${graphNodeLabel(node)}: ${node.label}`);const circle=document.createElementNS(NS,'circle');circle.setAttribute('cx',p.x);circle.setAttribute('cy',p.y);circle.setAttribute('r',node.id===focus.id?'31':'23');const text=document.createElementNS(NS,'text');text.setAttribute('x',p.x);text.setAttribute('y',p.y+(node.id===focus.id?48:39));text.setAttribute('text-anchor','middle');text.textContent=String(node.label||'').slice(0,28);g.append(circle,text);const select=()=>{state.knowledgeGraph.selectedNodeId=node.id;touchKnowledgeGraph();persist('Knowledge Graph focus saved');renderKnowledgeGraph();};g.addEventListener('click',select);g.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select();}});graphSvg.appendChild(g);});}
    function renderKnowledgeGraph(){if(!graphSection)return;state.knowledgeGraph=normalizeKnowledgeGraph(state.knowledgeGraph,state.projects);const graph=buildKnowledgeGraph(),prefs=state.knowledgeGraph.preferences;const projectIds=new Set(graph.nodes.filter(n=>n.type==='project').map(n=>n.projectId));if(graphSearch&&document.activeElement!==graphSearch)graphSearch.value=prefs.query;if(graphNodeType)graphNodeType.value=prefs.nodeType;if(graphRelation)graphRelation.value=prefs.relation;if(graphScope)graphScope.value=prefs.scope;if(graphDepth)graphDepth.value=String(prefs.depth);if(graphProject){const current=prefs.project;graphProject.innerHTML='<option value="all">All projects</option>';state.projects.slice().sort(projectSort).forEach(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=`${p.title}${p.archivedAt?' (archived)':''}`;graphProject.appendChild(o);});graphProject.value=projectIds.has(current)?current:'all';}
      if(graphMetricNodes)graphMetricNodes.textContent=String(graph.nodes.length);if(graphMetricEdges)graphMetricEdges.textContent=String(graph.edges.length);if(graphMetricProjects)graphMetricProjects.textContent=String(projectIds.size);if(graphMetricProvenance)graphMetricProvenance.textContent=String(graph.nodes.filter(n=>n.type==='provenance').length);
      const q=prefs.query.trim().toLowerCase();let candidates=graph.nodes.filter(node=>{if(prefs.scope==='active'&&node.archived)return false;if(prefs.nodeType!=='all'&&node.type!==prefs.nodeType)return false;if(prefs.project!=='all'&&node.type!=='provenance'&&node.projectId!==prefs.project)return false;if(q&&!`${node.label} ${node.summary||''} ${(node.tags||[]).join(' ')} ${node.projectTitle||''}`.toLowerCase().includes(q))return false;if(prefs.relation!=='all'&&!graph.edges.some(edge=>edge.relation===prefs.relation&&(edge.from===node.id||edge.to===node.id)))return false;return true;});candidates=candidates.sort((a,b)=>String(b.updatedAt||'').localeCompare(String(a.updatedAt||''))).slice(0,120);
      if(graphResults){graphResults.innerHTML='';if(!candidates.length)graphResults.innerHTML='<div class="scw-knowledge-empty-note">No graph nodes match these filters.</div>';candidates.forEach(node=>{const b=document.createElement('button');b.type='button';b.className=`scw-graph-result${state.knowledgeGraph.selectedNodeId===node.id?' is-selected':''}`;const degree=graph.edges.filter(e=>e.from===node.id||e.to===node.id).length;b.innerHTML=`<span>${escapeHtml(graphNodeLabel(node))}${node.projectTitle?` · ${escapeHtml(node.projectTitle)}`:''}</span><strong>${escapeHtml(node.label)}</strong><small>${degree} relationship${degree===1?'':'s'}</small>`;b.addEventListener('click',()=>{state.knowledgeGraph.selectedNodeId=node.id;touchKnowledgeGraph();persist('Knowledge Graph focus saved');renderKnowledgeGraph();});graphResults.appendChild(b);});}
      let focus=graph.nodes.find(n=>n.id===state.knowledgeGraph.selectedNodeId);if(!focus&&candidates.length){focus=candidates[0];state.knowledgeGraph.selectedNodeId=focus.id;}const neighborhood=focus?graphNeighborhood(graph,focus.id,prefs.depth,prefs.relation):{nodes:[],edges:[]};renderGraphSvg(focus,neighborhood);
      if(graphDetail){graphDetail.innerHTML='';if(!focus)graphDetail.innerHTML='<div class="scw-knowledge-empty-note">Select a project, object, or provenance source to inspect its graph context.</div>';else{const head=document.createElement('div');head.className='scw-graph-detail-head';head.innerHTML=`<span>${escapeHtml(graphNodeLabel(focus))}${focus.projectTitle?` · ${escapeHtml(focus.projectTitle)}`:''}</span><strong>${escapeHtml(focus.label)}</strong><p>${escapeHtml(focus.summary||'No additional summary.')}</p>`;const action=document.createElement('button');action.type='button';action.className='scw-card-action';action.textContent=focus.type==='provenance'?'Provenance node':'Open source context';action.disabled=focus.type==='provenance';action.addEventListener('click',()=>openGraphNode(focus));head.appendChild(action);graphDetail.appendChild(head);}}
      if(graphRelations){graphRelations.innerHTML='';if(!focus||!neighborhood.edges.length)graphRelations.innerHTML='<div class="scw-knowledge-empty-note">No relationships are visible for this focus and filter.</div>';else neighborhood.edges.slice(0,80).forEach(edge=>{const otherId=edge.from===focus.id?edge.to:edge.from,other=graph.nodes.find(n=>n.id===otherId);if(!other)return;const row=document.createElement('button');row.type='button';row.className='scw-graph-relation-row';row.innerHTML=`<span>${escapeHtml(edge.relation.replaceAll('-',' '))}</span><strong>${escapeHtml(other.label)}</strong><small>${escapeHtml(graphNodeLabel(other))}${other.projectTitle?` · ${escapeHtml(other.projectTitle)}`:''}</small>`;row.addEventListener('click',()=>{state.knowledgeGraph.selectedNodeId=other.id;touchKnowledgeGraph();persist('Knowledge Graph focus saved');renderKnowledgeGraph();});graphRelations.appendChild(row);});}
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
      renderResearch(project);
      renderAnalysis(project);
      renderDecision(project);
      renderCanvas(project);
      renderHandoffs(project);
      renderTraceability(project);
      renderGuidedWorkflows(project);
      renderAiAssistance(project);
      renderBriefing(project);
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
      renderIdentity();
      renderCloudRecovery();
      renderAccountSync();
      renderFilters();
      renderList();
      renderActive();
      if (recoveryNotice) showRecovery();
      setProjectMode(activeProjectMode);
      setWorkspaceView(workspaceView);
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
      state.projects.push(copy); state.activeProjectId = copy.id; activeProjectMode = 'overview';
      persist('Duplicate saved on this device'); render();
    });

    root.querySelector('[data-scw-export]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      const portable = JSON.parse(JSON.stringify(project)); portable.persistence = { scope: 'device', deviceId: 'scwd-portable', syncState: 'local-only', accountEligible: true, serverStored: false };
      const payload = { schema: EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.23.0', exportedAt: nowIso(), project: portable };
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
      cleanKnowledgeProjectReferences(project.id); state.projects = state.projects.filter((item) => item.id !== project.id); state.activeProjectId = null; persist('Project deleted from this device'); render();
    });

    root.querySelector('[data-scw-import-project]').addEventListener('click', () => importFile.click());
    importFile.addEventListener('change', () => {
      const file = importFile.files && importFile.files[0]; if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {
        try {
          const payload = JSON.parse(String(reader.result || ''));
          const supportedExport = payload && (payload.schema === EXPORT_SCHEMA || payload.schema === LEGACY_EXPORT_SCHEMA_V10 || payload.schema === LEGACY_EXPORT_SCHEMA_V9 || payload.schema === LEGACY_EXPORT_SCHEMA_V8 || payload.schema === LEGACY_EXPORT_SCHEMA_V7 || payload.schema === LEGACY_EXPORT_SCHEMA_V6 || payload.schema === LEGACY_EXPORT_SCHEMA_V5 || payload.schema === LEGACY_EXPORT_SCHEMA_V4 || payload.schema === LEGACY_EXPORT_SCHEMA_V31 || payload.schema === LEGACY_EXPORT_SCHEMA_V3 || payload.schema === LEGACY_EXPORT_SCHEMA_V2 || payload.schema === LEGACY_EXPORT_SCHEMA_V1);
          const rawProject = supportedExport ? payload.project : payload;
          if (!rawProject || (rawProject.schema !== PROJECT_SCHEMA && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V10 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V9 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V8 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V7 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V6 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V5 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V4 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V31 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V3 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V2 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V1)) throw new Error('Unsupported project schema');
          const project = normalizeProject(rawProject);
          if (!project) throw new Error('Invalid project');
          if (state.projects.some((item) => item.id === project.id)) { project.id = id('scwp'); project.title = `${project.title} (Imported)`.slice(0, 120); }
          project.archivedAt = null; project.activeObjectId = null; project.updatedAt = nowIso(); addActivity(project, 'imported', 'Project imported on this device');
          state.projects.push(project); state.activeProjectId = project.id; activeProjectMode = 'overview'; persist('Imported project saved'); render();
        } catch (_) {
          window.alert('Workspace could not import this file. Use a Workspace project JSON export from v0.2.0 through v0.23.0, or a compatible future release.');
        } finally { importFile.value = ''; }
      };
      reader.readAsText(file);
    });



    researchQuestionForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const project = activeProject(); if (!project) return;
      if (project.research.questions.length >= MAX_RESEARCH_QUESTIONS) { window.alert(`This project has reached the ${MAX_RESEARCH_QUESTIONS}-question research limit.`); return; }
      const data = new FormData(researchQuestionForm);
      const text = String(data.get('question') || '').trim().slice(0, 1000); if (!text) return;
      const stamp = nowIso();
      const question = { id: id('rq'), text, status: 'open', priority: QUESTION_PRIORITY.has(String(data.get('priority'))) ? String(data.get('priority')) : 'normal', createdAt: stamp, updatedAt: stamp };
      project.research.questions.push(question); project.research.activeQuestionId = question.id; touchResearch(project);
      addActivity(project, 'research-question', 'Research question added'); researchQuestionForm.reset(); persist('Research question saved'); renderResearch(project); renderList();
    });

    researchSourceForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
      const data = new FormData(researchSourceForm);
      const title = String(data.get('title') || '').trim().slice(0, 160); if (!title) return;
      const source = objectTemplate('source', title);
      source.summary = String(data.get('summary') || '').slice(0, 1200);
      source.status = 'working';
      source.tags = normalizeTags(data.get('tags'));
      source.provenance.sourceType = PROVENANCE_TYPES.has(String(data.get('sourceType'))) ? String(data.get('sourceType')) : 'web';
      source.provenance.sourceTitle = title.slice(0, 240);
      source.provenance.sourceUrl = String(data.get('url') || '').slice(0, 2000);
      source.provenance.capturedAt = nowIso();
      project.objects.push(source); project.activeObjectId = source.id;
      if (project.research.readingQueue.length < MAX_READING_QUEUE) project.research.readingQueue.push({ id: id('rr'), objectId: source.id, status: 'unread', note: '', addedAt: nowIso(), updatedAt: nowIso() });
      touchResearch(project); addActivity(project, 'source-captured', `Source captured: ${source.title}`); researchSourceForm.reset(); persist('Source captured and queued'); render();
    });

    researchEvidenceForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
      const data = new FormData(researchEvidenceForm);
      const title = String(data.get('title') || '').trim().slice(0, 160); const content = String(data.get('content') || '').slice(0, 50000); if (!title || !content.trim()) return;
      const evidence = objectTemplate('evidence', title); evidence.content = content; evidence.summary = String(data.get('summary') || '').slice(0, 1200); evidence.status = 'working';
      const sourceId = String(data.get('sourceObjectId') || ''); const source = objectById(project, sourceId);
      if (source) { evidence.provenance = { ...source.provenance, sourceTitle: source.title, capturedAt: nowIso() }; }
      project.objects.push(evidence); project.activeObjectId = evidence.id;
      if (source && project.research.evidenceLinks.length < MAX_EVIDENCE_LINKS) project.research.evidenceLinks.push({ id: id('rel'), evidenceObjectId: evidence.id, sourceObjectId: source.id, createdAt: nowIso() });
      touchResearch(project); addActivity(project, 'evidence-captured', `Evidence captured: ${evidence.title}`); researchEvidenceForm.reset(); persist('Evidence captured'); render();
    });

    researchClaimForm.addEventListener('submit', (event) => {
      event.preventDefault();
      const project = activeProject(); if (!project) return;
      if (project.research.claims.length >= MAX_RESEARCH_CLAIMS) { window.alert(`This project has reached the ${MAX_RESEARCH_CLAIMS}-claim research limit.`); return; }
      const data = new FormData(researchClaimForm); const text = String(data.get('claim') || '').trim().slice(0, 2000); if (!text) return;
      const stamp = nowIso(); const claim = { id: id('rc'), text, status: 'exploratory', evidenceObjectIds: [], createdAt: stamp, updatedAt: stamp };
      project.research.claims.push(claim); project.research.activeClaimId = claim.id; touchResearch(project); addActivity(project, 'research-claim', 'Research claim added'); researchClaimForm.reset(); persist('Research claim saved'); renderResearch(project);
    });

    root.querySelector('[data-scw-research-link-evidence]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      const claim = project.research.claims.find((item) => item.id === project.research.activeClaimId); const evidenceId = researchClaimEvidence.value;
      if (!claim) { window.alert('Set an active claim first.'); return; }
      const evidence = objectById(project, evidenceId); if (!evidence || evidence.type !== 'evidence') return;
      if (!claim.evidenceObjectIds.includes(evidence.id)) claim.evidenceObjectIds.push(evidence.id);
      claim.updatedAt = nowIso(); touchResearch(project); addActivity(project, 'evidence-linked', `Evidence linked to active claim: ${evidence.title}`); persist('Evidence link saved'); renderResearch(project);
    });



    analysisQuestionForm.addEventListener('submit', (event) => {
      event.preventDefault(); const project=activeProject(); if(!project) return; if(project.analysis.questions.length>=MAX_ANALYSIS_QUESTIONS)return;
      const data=new FormData(analysisQuestionForm); const text=String(data.get('question')||'').trim().slice(0,1200); if(!text)return; const stamp=nowIso();
      const question={id:id('aq'),text,status:'open',priority:QUESTION_PRIORITY.has(String(data.get('priority')))?String(data.get('priority')):'normal',createdAt:stamp,updatedAt:stamp};
      project.analysis.questions.push(question);project.analysis.activeQuestionId=question.id;touchAnalysis(project);addActivity(project,'analysis-question','Analysis question added');analysisQuestionForm.reset();persist('Analysis question saved');renderAnalysis(project);renderList();
    });

    analysisDatasetForm.addEventListener('submit', (event)=>{
      event.preventDefault();const project=activeProject();if(!project||project.objects.length>=MAX_OBJECTS)return;const data=new FormData(analysisDatasetForm);const title=String(data.get('title')||'').trim().slice(0,160);if(!title)return;
      const dataset=objectTemplate('dataset',title);dataset.summary=String(data.get('summary')||'').slice(0,1200);dataset.status='working';dataset.tags=normalizeTags(data.get('tags'));dataset.provenance.sourceType='dataset';dataset.provenance.sourceTitle=title;dataset.provenance.sourceUrl=String(data.get('url')||'').slice(0,2000);dataset.provenance.capturedAt=nowIso();project.objects.push(dataset);project.activeObjectId=dataset.id;touchAnalysis(project);addActivity(project,'dataset-registered',`Dataset registered: ${dataset.title}`);analysisDatasetForm.reset();persist('Dataset registered');render();
    });

    analysisVariableForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.analysis.variables.length>=MAX_ANALYSIS_VARIABLES)return;const data=new FormData(analysisVariableForm);const name=String(data.get('name')||'').trim().slice(0,160);if(!name)return;const stamp=nowIso();project.analysis.variables.push({id:id('av'),name,role:ANALYSIS_VARIABLE_ROLE.has(String(data.get('role')))?String(data.get('role')):'indicator',unit:String(data.get('unit')||'').slice(0,80),definition:String(data.get('definition')||'').slice(0,1200),createdAt:stamp,updatedAt:stamp});touchAnalysis(project);addActivity(project,'analysis-variable',`Variable registered: ${name}`);analysisVariableForm.reset();persist('Variable saved');renderAnalysis(project)});

    analysisAssumptionForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.analysis.assumptions.length>=MAX_ANALYSIS_ASSUMPTIONS)return;const data=new FormData(analysisAssumptionForm);const text=String(data.get('assumption')||'').trim().slice(0,2000);if(!text)return;const stamp=nowIso();project.analysis.assumptions.push({id:id('aa'),text,status:'untested',evidenceObjectIds:[],createdAt:stamp,updatedAt:stamp});touchAnalysis(project);addActivity(project,'analysis-assumption','Assumption added');analysisAssumptionForm.reset();persist('Assumption saved');renderAnalysis(project)});

    analysisMethodForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.analysis.methods.length>=MAX_ANALYSIS_METHODS||project.objects.length>=MAX_OBJECTS)return;const data=new FormData(analysisMethodForm);const name=String(data.get('name')||'').trim().slice(0,200);if(!name)return;const stamp=nowIso();const analysisObject=objectTemplate('analysis',name);analysisObject.status='working';analysisObject.summary=String(data.get('description')||'').slice(0,1200);analysisObject.provenance.sourceType='tool';analysisObject.provenance.sourceTitle='Workspace Analysis';analysisObject.provenance.capturedAt=stamp;project.objects.push(analysisObject);const datasetId=String(data.get('datasetObjectId')||'');const method={id:id('am'),name,type:ANALYSIS_METHOD_TYPE.has(String(data.get('type')))?String(data.get('type')):'descriptive',description:String(data.get('description')||'').slice(0,3000),datasetObjectIds:objectById(project,datasetId)&&objectById(project,datasetId).type==='dataset'?[datasetId]:[],analysisObjectId:analysisObject.id,createdAt:stamp,updatedAt:stamp};project.analysis.methods.push(method);project.analysis.activeMethodId=method.id;project.activeObjectId=analysisObject.id;touchAnalysis(project);addActivity(project,'analysis-method',`Analysis method registered: ${name}`);analysisMethodForm.reset();persist('Analysis method saved');render();});

    analysisComparisonForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.analysis.comparisons.length>=MAX_ANALYSIS_COMPARISONS)return;const data=new FormData(analysisComparisonForm);const label=String(data.get('label')||'').trim().slice(0,200);if(!label)return;const stamp=nowIso();project.analysis.comparisons.push({id:id('ac'),label,baseline:String(data.get('baseline')||'').slice(0,800),alternative:String(data.get('alternative')||'').slice(0,800),metric:String(data.get('metric')||'').slice(0,240),result:String(data.get('result')||'').slice(0,1200),interpretation:String(data.get('interpretation')||'').slice(0,2000),createdAt:stamp,updatedAt:stamp});touchAnalysis(project);addActivity(project,'analysis-comparison',`Comparison added: ${label}`);analysisComparisonForm.reset();persist('Comparison saved');renderAnalysis(project)});

    analysisFindingForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.analysis.findings.length>=MAX_ANALYSIS_FINDINGS)return;const data=new FormData(analysisFindingForm);const text=String(data.get('finding')||'').trim().slice(0,3000);if(!text)return;const stamp=nowIso();const evidenceId=String(data.get('evidenceObjectId')||'');const evidence=objectById(project,evidenceId);const activeMethod=project.analysis.methods.find((x)=>x.id===project.analysis.activeMethodId);project.analysis.findings.push({id:id('af'),text,status:ANALYSIS_FINDING_STATUS.has(String(data.get('status')))?String(data.get('status')):'preliminary',evidenceObjectIds:evidence&&evidence.type==='evidence'?[evidence.id]:[],analysisObjectId:activeMethod?activeMethod.analysisObjectId:'',createdAt:stamp,updatedAt:stamp});touchAnalysis(project);addActivity(project,'analysis-finding','Finding recorded');analysisFindingForm.reset();persist('Finding saved');renderAnalysis(project)});


    decisionForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.decision.decisions.length>=MAX_DECISIONS||project.objects.length>=MAX_OBJECTS)return;const data=new FormData(decisionForm);const title=String(data.get('title')||'').trim().slice(0,200),question=String(data.get('question')||'').trim().slice(0,2000);if(!title||!question)return;const stamp=nowIso();const obj=objectTemplate('decision',title);obj.status='working';obj.summary=question.slice(0,1200);obj.provenance.sourceType='tool';obj.provenance.sourceTitle='Workspace Decision';obj.provenance.capturedAt=stamp;project.objects.push(obj);const record={id:id('dr'),title,question,status:'framing',decisionObjectId:obj.id,selectedOptionId:'',rationale:'',confidence:'medium',createdAt:stamp,updatedAt:stamp,decidedAt:null};project.decision.decisions.push(record);project.decision.activeDecisionId=record.id;project.activeObjectId=obj.id;touchDecision(project);addActivity(project,'decision-created',`Decision framed: ${title}`);decisionForm.reset();persist('Decision created');render();});
    decisionOptionForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.decision.options.length>=MAX_DECISION_OPTIONS)return;const active=project.decision.decisions.find(x=>x.id===project.decision.activeDecisionId);if(!active)return;const data=new FormData(decisionOptionForm),label=String(data.get('label')||'').trim().slice(0,200);if(!label)return;const stamp=nowIso();project.decision.options.push({id:id('do'),decisionId:active.id,label,description:String(data.get('description')||'').slice(0,2400),status:'candidate',evidenceObjectIds:[],analysisObjectIds:[],createdAt:stamp,updatedAt:stamp});if(active.status==='framing')active.status='evaluating';touchDecision(project);addActivity(project,'decision-option',`Option added: ${label}`);decisionOptionForm.reset();persist('Decision option saved');renderDecision(project)});
    decisionCriterionForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.decision.criteria.length>=MAX_DECISION_CRITERIA)return;const active=project.decision.decisions.find(x=>x.id===project.decision.activeDecisionId);if(!active)return;const data=new FormData(decisionCriterionForm),label=String(data.get('label')||'').trim().slice(0,200);if(!label)return;const stamp=nowIso();project.decision.criteria.push({id:id('dc'),decisionId:active.id,label,weight:Math.max(0,Math.min(100,Number(data.get('weight'))||0)),description:String(data.get('description')||'').slice(0,1200),createdAt:stamp,updatedAt:stamp});touchDecision(project);addActivity(project,'decision-criterion',`Criterion added: ${label}`);decisionCriterionForm.reset();persist('Decision criterion saved');renderDecision(project)});
    decisionAssessmentForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.decision.assessments.length>=MAX_DECISION_ASSESSMENTS)return;const active=project.decision.decisions.find(x=>x.id===project.decision.activeDecisionId);if(!active)return;const data=new FormData(decisionAssessmentForm),optionId=String(data.get('optionId')||''),criterionId=String(data.get('criterionId')||'');if(!project.decision.options.some(x=>x.id===optionId&&x.decisionId===active.id)||!project.decision.criteria.some(x=>x.id===criterionId&&x.decisionId===active.id))return;const stamp=nowIso();project.decision.assessments.push({id:id('da'),decisionId:active.id,optionId,criterionId,score:Math.max(-5,Math.min(5,Number(data.get('score'))||0)),note:String(data.get('note')||'').slice(0,1200),createdAt:stamp,updatedAt:stamp});touchDecision(project);addActivity(project,'decision-assessment','Decision assessment recorded');decisionAssessmentForm.reset();persist('Assessment saved');renderDecision(project)});
    decisionRiskForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.decision.risks.length>=MAX_DECISION_RISKS)return;const active=project.decision.decisions.find(x=>x.id===project.decision.activeDecisionId);if(!active)return;const data=new FormData(decisionRiskForm),risk=String(data.get('risk')||'').trim().slice(0,2400);if(!risk)return;const stamp=nowIso();project.decision.risks.push({id:id('dk'),decisionId:active.id,optionId:'',risk,likelihood:DECISION_RISK_LEVEL.has(String(data.get('likelihood')))?String(data.get('likelihood')):'medium',impact:DECISION_RISK_LEVEL.has(String(data.get('impact')))?String(data.get('impact')):'medium',mitigation:String(data.get('mitigation')||'').slice(0,2000),createdAt:stamp,updatedAt:stamp});touchDecision(project);addActivity(project,'decision-risk','Decision risk recorded');decisionRiskForm.reset();persist('Risk saved');renderDecision(project)});
    decisionFinalForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project)return;const active=project.decision.decisions.find(x=>x.id===project.decision.activeDecisionId);if(!active)return;const data=new FormData(decisionFinalForm),selectedOptionId=String(data.get('selectedOptionId')||''),rationale=String(data.get('rationale')||'').trim().slice(0,6000);const selected=project.decision.options.find(x=>x.id===selectedOptionId&&x.decisionId===active.id);if(!selected||!rationale)return;const stamp=nowIso();active.selectedOptionId=selected.id;active.rationale=rationale;active.confidence=DECISION_CONFIDENCE.has(String(data.get('confidence')))?String(data.get('confidence')):'medium';active.status='decided';active.decidedAt=stamp;active.updatedAt=stamp;project.decision.options.filter(x=>x.decisionId===active.id).forEach(x=>{x.status=x.id===selected.id?'selected':(x.status==='rejected'?'rejected':'shortlisted');x.updatedAt=stamp;});const obj=objectById(project,active.decisionObjectId);if(obj){obj.status='ready';obj.summary=`Selected: ${selected.label}`.slice(0,1200);obj.content=`Decision: ${active.question}\n\nSelected option: ${selected.label}\n\nRationale:\n${rationale}\n\nConfidence: ${active.confidence}`.slice(0,50000);obj.updatedAt=stamp;}touchDecision(project);addActivity(project,'decision-finalized',`Decision finalized: ${active.title}`);persist('Decision finalized');render();});

    if (canvasBoardForm) canvasBoardForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.canvas.boards.length>=MAX_CANVAS_BOARDS)return;const data=new FormData(canvasBoardForm),title=String(data.get('title')||'').trim().slice(0,200);if(!title)return;const stamp=nowIso();const board={id:id('cb'),title,description:String(data.get('description')||'').slice(0,2400),status:'working',createdAt:stamp,updatedAt:stamp};project.canvas.boards.push(board);project.canvas.activeBoardId=board.id;touchCanvas(project);addActivity(project,'canvas-board-created',`Canvas board created: ${title}`);canvasBoardForm.reset();persist('Canvas board created');renderCanvas(project);});

    if (canvasNodeForm) canvasNodeForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.canvas.nodes.length>=MAX_CANVAS_NODES)return;const board=project.canvas.boards.find(item=>item.id===project.canvas.activeBoardId);if(!board)return;const data=new FormData(canvasNodeForm),objectId=String(data.get('objectId')||''),linked=objectId?objectById(project,objectId):null;let title=String(data.get('title')||'').trim().slice(0,240);if(!title&&linked)title=linked.title;if(!title)return;const existing=project.canvas.nodes.filter(node=>node.boardId===board.id).length;const stamp=nowIso();const node={id:id('cn'),boardId:board.id,type:CANVAS_NODE_TYPE.has(String(data.get('type')))?String(data.get('type')):'note',title,body:String(data.get('body')||'').slice(0,4000),objectId:linked?linked.id:'',x:24+(existing%4)*205,y:24+(Math.floor(existing/4)%5)*95,tags:[],createdAt:stamp,updatedAt:stamp};project.canvas.nodes.push(node);board.updatedAt=stamp;touchCanvas(project);addActivity(project,'canvas-node-created',`Canvas node added: ${title}`);canvasNodeForm.reset();persist('Canvas node added');renderCanvas(project);});

    if (canvasEdgeForm) canvasEdgeForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.canvas.edges.length>=MAX_CANVAS_EDGES)return;const board=project.canvas.boards.find(item=>item.id===project.canvas.activeBoardId);if(!board)return;const data=new FormData(canvasEdgeForm),fromNodeId=String(data.get('fromNodeId')||''),toNodeId=String(data.get('toNodeId')||'');if(!fromNodeId||!toNodeId||fromNodeId===toNodeId)return;const valid=project.canvas.nodes.filter(node=>node.boardId===board.id).map(node=>node.id);if(!valid.includes(fromNodeId)||!valid.includes(toNodeId))return;project.canvas.edges.push({id:id('ce'),boardId:board.id,fromNodeId,toNodeId,relation:CANVAS_RELATION_TYPE.has(String(data.get('relation')))?String(data.get('relation')):'relates-to',label:String(data.get('label')||'').slice(0,240),createdAt:nowIso()});touchCanvas(project);addActivity(project,'canvas-edge-created','Canvas relationship recorded');canvasEdgeForm.reset();persist('Canvas relationship saved');renderCanvas(project);});

    if (canvasFrameForm) canvasFrameForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.canvas.frames.length>=MAX_CANVAS_FRAMES)return;const board=project.canvas.boards.find(item=>item.id===project.canvas.activeBoardId);if(!board)return;const data=new FormData(canvasFrameForm),title=String(data.get('title')||'').trim().slice(0,200);if(!title)return;const valid=new Set(project.canvas.nodes.filter(node=>node.boardId===board.id).map(node=>node.id));const selected=canvasFrameNodes?Array.from(canvasFrameNodes.selectedOptions).map(option=>option.value).filter(value=>valid.has(value)):[];const stamp=nowIso();project.canvas.frames.push({id:id('cf'),boardId:board.id,title,description:String(data.get('description')||'').slice(0,1600),nodeIds:selected.slice(0,100),createdAt:stamp,updatedAt:stamp});touchCanvas(project);addActivity(project,'canvas-frame-created',`Canvas frame created: ${title}`);canvasFrameForm.reset();persist('Canvas frame saved');renderCanvas(project);});

    if (canvasSynthesis) canvasSynthesis.addEventListener('click',()=>{const project=activeProject();if(!project||project.objects.length>=MAX_OBJECTS)return;const board=project.canvas.boards.find(item=>item.id===project.canvas.activeBoardId);if(!board)return;const nodes=project.canvas.nodes.filter(node=>node.boardId===board.id),edges=project.canvas.edges.filter(edge=>edge.boardId===board.id),frames=project.canvas.frames.filter(frame=>frame.boardId===board.id);const byId=new Map(nodes.map(node=>[node.id,node]));const lines=[`# ${board.title}`,board.description?`\n${board.description}`:'','\n## Nodes',...nodes.map(node=>`- [${node.type}] ${node.title}${node.body?`: ${node.body}`:''}`),'\n## Relationships',...edges.map(edge=>`- ${byId.get(edge.fromNodeId)?.title||'Node'} —${edge.relation}${edge.label?` (${edge.label})`:''}→ ${byId.get(edge.toNodeId)?.title||'Node'}`),'\n## Frames',...frames.map(frame=>`- ${frame.title}: ${frame.nodeIds.map(nodeId=>byId.get(nodeId)?.title).filter(Boolean).join(', ')}${frame.description?` — ${frame.description}`:''}`)];const obj=objectTemplate('document',`${board.title} — Canvas synthesis`);obj.status='ready';obj.summary=`Structured synthesis of ${nodes.length} nodes, ${edges.length} relationships, and ${frames.length} frames.`;obj.content=lines.filter(Boolean).join('\n').slice(0,50000);obj.provenance.sourceType='tool';obj.provenance.sourceTitle='Workspace Canvas';obj.provenance.capturedAt=nowIso();project.objects.push(obj);project.activeObjectId=obj.id;touchCanvas(project);addActivity(project,'canvas-synthesis',`Canvas synthesis captured: ${board.title}`);persist('Canvas synthesis captured');render();objectEditor.scrollIntoView({behavior:'auto',block:'start'});});

    root.querySelector('[data-scw-new-object]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This v0.8.2 project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
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
      const payload = { schema: OBJECT_EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.23.0', exportedAt: nowIso(), projectId: project.id, object: JSON.parse(JSON.stringify(object)) };
      downloadJson(`${safeFileName(object.title)}.sc-workspace-object.json`, payload);
      addActivity(project, 'object-exported', `${OBJECT_LABELS[object.type]} exported: ${object.title}`); project.updatedAt = nowIso(); persist('Object export recorded'); renderActive();
    });

    root.querySelector('[data-scw-object-archive]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      if (!window.confirm(`Archive “${object.title}”? It will remain inside this project on this device.`)) return;
      object.archivedAt = nowIso(); object.updatedAt = object.archivedAt; project.updatedAt = object.updatedAt; project.activeObjectId = null;
      addActivity(project, 'object-archived', `${OBJECT_LABELS[object.type]} archived: ${object.title}`); persist('Object archived'); render();
    });

    if(traceEvidenceForm) traceEvidenceForm.addEventListener('submit',async(event)=>{event.preventDefault();const project=activeProject();if(!project||project.traceability.evidenceAssessments.length>=MAX_EVIDENCE_ASSESSMENTS)return;const data=new FormData(traceEvidenceForm),objectId=String(data.get('objectId')||''),object=objectById(project,objectId);if(!object||!['source','evidence'].includes(object.type))return;const existing=project.traceability.evidenceAssessments.find(x=>x.objectId===objectId);const stamp=nowIso(),fingerprint=await sha256Object(object);const item=existing||{id:id('tea'),objectId,createdAt:stamp};Object.assign(item,{relevance:clampScore(data.get('relevance')),sourceQuality:clampScore(data.get('sourceQuality')),independence:clampScore(data.get('independence')),recency:clampScore(data.get('recency')),note:String(data.get('note')||'').slice(0,2000),fingerprint,fingerprintAlgorithm:'SHA-256',fingerprintState:fingerprint?'match':'unverified',updatedAt:stamp});if(!existing)project.traceability.evidenceAssessments.push(item);touchTraceability(project);addActivity(project,'evidence-assessed',`Evidence assessed: ${object.title}`);traceEvidenceForm.reset();persist('Evidence assessment saved');renderTraceability(project);});
    if(traceLineageForm) traceLineageForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.traceability.lineage.length>=MAX_LINEAGE_RELATIONS)return;const data=new FormData(traceLineageForm),fromObjectId=String(data.get('fromObjectId')||''),toObjectId=String(data.get('toObjectId')||'');if(!objectById(project,fromObjectId)||!objectById(project,toObjectId)||fromObjectId===toObjectId)return;project.traceability.lineage.push({id:id('tl'),fromObjectId,toObjectId,relation:TRACE_RELATIONS.has(String(data.get('relation')))?String(data.get('relation')):'derived-from',note:String(data.get('note')||'').slice(0,500),createdAt:nowIso()});touchTraceability(project);addActivity(project,'lineage-added','Object lineage link added');traceLineageForm.reset();persist('Lineage link saved');renderTraceability(project);});
    if(traceReproForm) traceReproForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.traceability.reproducibility.length>=MAX_REPRO_RECORDS)return;const data=new FormData(traceReproForm),title=String(data.get('title')||'').trim().slice(0,200);if(!title)return;const stamp=nowIso(),analysisObjectId=String(data.get('analysisObjectId')||'');project.traceability.reproducibility.push({id:id('trr'),title,analysisObjectId:objectById(project,analysisObjectId)?.type==='analysis'?analysisObjectId:'',datasetObjectIds:selectedValues(traceReproDatasets).filter(v=>objectById(project,v)?.type==='dataset'),evidenceObjectIds:selectedValues(traceReproEvidence).filter(v=>objectById(project,v)?.type==='evidence'),resultObjectIds:[],method:String(data.get('method')||'').slice(0,4000),parameters:String(data.get('parameters')||'').slice(0,5000),environment:String(data.get('environment')||'').slice(0,3000),steps:String(data.get('steps')||'').slice(0,8000),status:'draft',createdAt:stamp,updatedAt:stamp,lastVerifiedAt:null});touchTraceability(project);addActivity(project,'repro-created',`Reproduction record created: ${title}`);traceReproForm.reset();persist('Reproduction record saved');renderTraceability(project);});
    if(traceExportButton) traceExportButton.addEventListener('click',()=>{const project=activeProject();if(!project)return;const payload={schema:'sc-workspace-traceability-export/1.0',workspaceVersion:root.dataset.version||'0.23.0',exportedAt:nowIso(),project:{id:project.id,title:project.title},traceability:JSON.parse(JSON.stringify(project.traceability))};downloadJson(`${safeFileName(project.title)}.traceability.json`,payload);addActivity(project,'traceability-export','Traceability package exported');persist('Traceability export recorded');});


    if(aiRequestForm) aiRequestForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.aiAssistance.sessions.length>=MAX_AI_SESSIONS)return;const data=new FormData(aiRequestForm),title=String(data.get('title')||'').trim().slice(0,200),prompt=String(data.get('prompt')||'').trim().slice(0,MAX_AI_PROMPT),task=AI_TASKS.has(String(data.get('task')))?String(data.get('task')):'general-question',objectIds=selectedValues(aiObjectSelect).filter(v=>objectById(project,v)).slice(0,MAX_AI_OBJECT_REFS);if(!title||!prompt)return;const stamp=nowIso(),session={id:id('ai'),title,task,status:'prepared',prompt,objectIds,response:'',responseSource:'manual',citationObjectIds:[],acceptedDocumentObjectId:'',createdAt:stamp,updatedAt:stamp,sentAt:null,respondedAt:null,acceptedAt:null};project.aiAssistance.sessions.unshift(session);project.aiAssistance.activeSessionId=session.id;touchAiAssistance(project);addActivity(project,'ai-request-prepared',`AI assistance request prepared: ${title}`);aiRequestForm.reset();persist('AI assistance request prepared locally');renderAiAssistance(project);});
    if(aiCopyPrompt) aiCopyPrompt.addEventListener('click',async()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session)return;const text=aiPromptMarkdown(project,session);try{await navigator.clipboard.writeText(text);persist('Grounded prompt copied');}catch(_){downloadText(`${safeFileName(session.title)}.ai-prompt.md`,text,'text/markdown;charset=utf-8');persist('Grounded prompt exported');}});
    if(aiExportRequest) aiExportRequest.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session)return;downloadJson(`${safeFileName(session.title)}.sc-workspace-ai-request.json`,aiRequestPackage(project,session));addActivity(project,'ai-request-export',`AI request package exported: ${session.title}`);persist('AI request package exported');});
    if(aiOpenLibrarian) aiOpenLibrarian.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session)return;writeAiRequestToSession(project,session);session.status='sent';session.sentAt=nowIso();session.updatedAt=session.sentAt;touchAiAssistance(project);persist('AI request prepared for Research Librarian');const link=root.querySelector('[data-scw-tool="research-librarian"]');if(link){link.click();window.location.href=link.href;}});
    if(aiSaveResponse) aiSaveResponse.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session)return;session.response=String(aiResponse.value||'').slice(0,MAX_AI_RESPONSE);session.responseSource=AI_RESPONSE_SOURCES.has(aiResponseSource.value)?aiResponseSource.value:'manual';session.citationObjectIds=selectedValues(aiCitationSelect).filter(v=>session.objectIds.includes(v)).slice(0,MAX_AI_OBJECT_REFS);session.status=session.response?'response-received':'prepared';session.respondedAt=session.response?nowIso():null;session.updatedAt=nowIso();touchAiAssistance(project);addActivity(project,'ai-response-saved',`AI response saved for review: ${session.title}`);persist('AI response saved locally');renderAiAssistance(project);});
    if(aiAcceptDocument) aiAcceptDocument.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session||!session.response)return;if(project.objects.length>=MAX_OBJECTS){window.alert('This project has reached the Workspace Object limit.');return;}let doc=session.acceptedDocumentObjectId?objectById(project,session.acceptedDocumentObjectId):null;if(!doc){doc=objectTemplate('document',`${session.title} — AI-assisted draft`);project.objects.push(doc);session.acceptedDocumentObjectId=doc.id;}doc.summary=`Human-accepted AI-assisted draft for ${aiTaskLabel(session.task)}.`;doc.content=session.response;doc.status='working';doc.tags=normalizeTags([...doc.tags,'ai-assisted','human-accepted']);doc.provenance={sourceType:'tool',sourceTitle:'Workspace Responsible AI Assistance',sourceUrl:'',capturedAt:nowIso()};doc.updatedAt=nowIso();session.status='accepted';session.acceptedAt=nowIso();session.updatedAt=session.acceptedAt;session.citationObjectIds.forEach(refId=>{if(project.traceability.lineage.length>=MAX_LINEAGE_RELATIONS)return;if(!project.traceability.lineage.some(x=>x.fromObjectId===doc.id&&x.toObjectId===refId&&x.relation==='derived-from'))project.traceability.lineage.push({id:id('tl'),fromObjectId:doc.id,toObjectId:refId,relation:'derived-from',note:'AI-assisted draft grounding reference accepted by user',createdAt:nowIso()});});touchTraceability(project);touchAiAssistance(project);addActivity(project,'ai-response-accepted',`AI-assisted draft accepted as Document: ${doc.title}`);persist('AI-assisted draft materialized as Document');renderAiAssistance(project);renderObjects(project);});
    if(aiReject) aiReject.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session)return;session.status='rejected';session.updatedAt=nowIso();touchAiAssistance(project);addActivity(project,'ai-response-rejected',`AI response rejected: ${session.title}`);persist('AI response rejected');renderAiAssistance(project);});
    if(aiExportResponse) aiExportResponse.addEventListener('click',()=>{const project=activeProject(),session=activeAiSession(project);if(!project||!session||!session.response)return;downloadJson(`${safeFileName(session.title)}.sc-workspace-ai-response.json`,aiResponsePackage(project,session));persist('AI response package exported');});

    if(briefingDraftForm) briefingDraftForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject();if(!project||project.briefing.drafts.length>=MAX_BRIEFING_DRAFTS)return;const data=new FormData(briefingDraftForm),title=String(data.get('title')||'').trim().slice(0,200);if(!title)return;const stamp=nowIso(),draft={id:id('bd'),title,format:BRIEFING_FORMATS.has(String(data.get('format')))?String(data.get('format')):'briefing',audience:String(data.get('audience')||'').slice(0,300),purpose:String(data.get('purpose')||'').slice(0,600),status:'draft',objectIds:[],sections:[],documentObjectId:'',createdAt:stamp,updatedAt:stamp,lastExportedAt:null};project.briefing.drafts.unshift(draft);project.briefing.activeDraftId=draft.id;touchBriefing(project);addActivity(project,'briefing-created',`Draft created: ${title}`);briefingDraftForm.reset();persist('Briefing draft created');renderBriefing(project);});
    if(briefingSaveBasis) briefingSaveBasis.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!project||!draft)return;draft.objectIds=selectedValues(briefingObjectSelect).filter(v=>objectById(project,v)).slice(0,MAX_BRIEFING_OBJECT_REFS);draft.updatedAt=nowIso();touchBriefing(project);persist('Draft basis saved');renderBriefing(project);});
    if(briefingOutlineButton) briefingOutlineButton.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!project||!draft)return;if(draft.sections.length&&!window.confirm('Add a standard outline after the existing sections?'))return;const stamp=nowIso();briefingOutline(draft.format).forEach(heading=>{if(draft.sections.length>=MAX_BRIEFING_SECTIONS)return;if(!draft.sections.some(s=>s.heading.toLowerCase()===heading.toLowerCase()))draft.sections.push({id:id('bs'),heading,body:'',objectIds:[],createdAt:stamp,updatedAt:stamp});});draft.updatedAt=stamp;touchBriefing(project);persist('Standard outline added');renderBriefing(project);});
    if(briefingStatus) briefingStatus.addEventListener('change',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!draft)return;draft.status=BRIEFING_STATUS.has(briefingStatus.value)?briefingStatus.value:'draft';draft.updatedAt=nowIso();touchBriefing(project);persist('Draft status saved');renderBriefing(project);});
    if(briefingSectionForm) briefingSectionForm.addEventListener('submit',(event)=>{event.preventDefault();const project=activeProject(),draft=activeBriefingDraft(project);if(!project||!draft||draft.sections.length>=MAX_BRIEFING_SECTIONS)return;const data=new FormData(briefingSectionForm),heading=String(data.get('heading')||'').trim().slice(0,180);if(!heading)return;const stamp=nowIso();draft.sections.push({id:id('bs'),heading,body:String(data.get('body')||'').slice(0,8000),objectIds:[],createdAt:stamp,updatedAt:stamp});draft.updatedAt=stamp;touchBriefing(project);briefingSectionForm.reset();persist('Section added');renderBriefing(project);});
    if(briefingMaterialize) briefingMaterialize.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!project||!draft)return;let doc=draft.documentObjectId?objectById(project,draft.documentObjectId):null;if(!doc){if(project.objects.length>=MAX_OBJECTS){window.alert('This project has reached the Workspace Object limit.');return;}doc=objectTemplate('document',draft.title);project.objects.push(doc);draft.documentObjectId=doc.id;}doc.title=draft.title;doc.summary=draft.purpose||`Workspace ${draft.format.replaceAll('-',' ')}.`;doc.content=briefingMarkdown(project,draft);doc.status=draft.status==='draft'?'working':'ready';doc.tags=normalizeTags([...doc.tags,'workspace-briefing',draft.format]);doc.provenance={sourceType:'manual',sourceTitle:'Workspace Briefing & Publication Studio',sourceUrl:'',capturedAt:nowIso()};doc.updatedAt=nowIso();draft.updatedAt=doc.updatedAt;draft.objectIds.forEach((refId)=>{if(project.traceability.lineage.length>=MAX_LINEAGE_RELATIONS)return;if(!project.traceability.lineage.some(x=>x.fromObjectId===doc.id&&x.toObjectId===refId&&x.relation==='derived-from'))project.traceability.lineage.push({id:id('tl'),fromObjectId:doc.id,toObjectId:refId,relation:'derived-from',note:'Briefing basis',createdAt:nowIso()});});touchTraceability(project);touchBriefing(project);addActivity(project,'briefing-materialized',`Document materialized: ${draft.title}`);persist('Document materialized');renderBriefing(project);renderObjects(project);});
    if(briefingExportMarkdown) briefingExportMarkdown.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!draft)return;downloadText(`${safeFileName(draft.title)}.md`,briefingMarkdown(project,draft),'text/markdown;charset=utf-8');draft.status='exported';draft.lastExportedAt=nowIso();touchBriefing(project);persist('Markdown exported');renderBriefing(project);});
    if(briefingExportHtml) briefingExportHtml.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!draft)return;downloadText(`${safeFileName(draft.title)}.html`,briefingHtml(project,draft),'text/html;charset=utf-8');draft.status='exported';draft.lastExportedAt=nowIso();touchBriefing(project);persist('HTML exported');renderBriefing(project);});
    if(briefingExportPackage) briefingExportPackage.addEventListener('click',()=>{const project=activeProject(),draft=activeBriefingDraft(project);if(!draft)return;downloadJson(`${safeFileName(draft.title)}.sc-workspace-publication.json`,publicationPackage(project,draft));draft.status='exported';draft.lastExportedAt=nowIso();touchBriefing(project);addActivity(project,'publication-export',`Publication package exported: ${draft.title}`);persist('Publication package exported');renderBriefing(project);});

    root.querySelector('[data-scw-object-delete]').addEventListener('click', () => {
      const project = activeProject(); const object = activeObject(); if (!project || !object) return;
      if (!window.confirm(`Delete “${object.title}” from this project? This cannot be undone unless you exported a copy.`)) return;
      project.objects = project.objects.filter((item) => item.id !== object.id); cleanResearchReferences(project, object.id); cleanAnalysisReferences(project, object.id); cleanDecisionReferences(project, object.id); cleanCanvasReferences(project, object.id); cleanHandoffReferences(project, object.id); cleanTraceabilityReferences(project, object.id); cleanBriefingReferences(project, object.id); cleanGuidedWorkflowReferences(project, object.id); cleanAiAssistanceReferences(project, object.id); cleanKnowledgeObjectReferences(project.id, object.id); project.activeObjectId = null; project.updatedAt = nowIso();
      addActivity(project, 'object-deleted', `${OBJECT_LABELS[object.type]} deleted from project`); persist('Object deleted'); render();
    });

    const dismissRecovery = root.querySelector('[data-scw-dismiss-recovery]');
    if (dismissRecovery) dismissRecovery.addEventListener('click', () => { if (recovery) recovery.hidden = true; recoveryNotice = ''; });

    const handoffImportButton = root.querySelector('[data-scw-handoff-import]');
    const handoffCheckButton = root.querySelector('[data-scw-handoff-check]');
    const handoffTemplateButton = root.querySelector('[data-scw-handoff-template]');
    if (handoffImportButton && handoffImportFile) handoffImportButton.addEventListener('click',()=>handoffImportFile.click());
    if (handoffImportFile) handoffImportFile.addEventListener('change',()=>{const file=handoffImportFile.files&&handoffImportFile.files[0];if(!file)return;const reader=new FileReader();reader.onload=()=>{try{const result=ingestReturnPacket(state,JSON.parse(String(reader.result||'')),{mode:'manual',allowUnmatched:true});if(!result.ok)throw new Error(result.message);persist(result.message);render();}catch(err){window.alert(err&&err.message?err.message:'Workspace could not import this handoff return package.');}finally{handoffImportFile.value='';}};reader.readAsText(file);});
    if (handoffCheckButton) handoffCheckButton.addEventListener('click',()=>checkReturnInbox(true));
    if (handoffTemplateButton) handoffTemplateButton.addEventListener('click',()=>{const project=activeProject();if(!project||!project.handoffs)return;const entry=project.handoffs.entries.find((item)=>item.id===project.handoffs.activeHandoffId)||project.handoffs.entries[0];if(!entry){window.alert('Open a connected tool first so Workspace has a handoff to receive back.');return;}downloadReturnTemplate(project,entry);});

    root.querySelectorAll('[data-scw-project-mode]').forEach((button) => {
      button.addEventListener('click', () => setProjectMode(button.dataset.scwProjectMode || 'overview'));
    });

    if(interoperabilityForm)interoperabilityForm.addEventListener('submit',async(event)=>{event.preventDefault();const projectId=interoperabilityProject&&interoperabilityProject.value;const file=interoperabilityFile&&interoperabilityFile.files&&interoperabilityFile.files[0];if(!projectId){window.alert('Choose a target project first.');return;}if(!file){window.alert('Choose a file to stage.');return;}if(file.size>5*1024*1024){window.alert('For this local release, imports are limited to 5 MB per file.');return;}try{const text=await file.text();const format=detectInteropFormat(file);const fingerprint=await sha256Text(text);const objects=stageExternalContent(format,text,file.name,fingerprint).slice(0,MAX_INTEROP_IMPORT_OBJECTS);if(!objects.length)throw new Error('The file did not contain importable artifacts.');stagedInteroperability={projectId,fileName:file.name,format,fingerprint,objects,relationships:Array.isArray(objects._relationships)?objects._relationships:[]};renderInteroperability();}catch(err){stagedInteroperability=null;renderInteroperability();window.alert(err&&err.message?err.message:'Workspace could not stage this file.');}});
    if(interoperabilityClear)interoperabilityClear.addEventListener('click',()=>{stagedInteroperability=null;if(interoperabilityFile)interoperabilityFile.value='';renderInteroperability();});
    if(interoperabilityCommit)interoperabilityCommit.addEventListener('click',()=>{if(!stagedInteroperability)return;const project=state.projects.find(p=>p.id===stagedInteroperability.projectId&&!p.archivedAt);if(!project){window.alert('The target project is no longer available.');return;}const capacity=Math.max(0,MAX_OBJECTS-project.objects.length);const incoming=stagedInteroperability.objects.slice(0,capacity);if(!incoming.length){window.alert('The target project has reached its local object limit.');return;}const sourceMap=new Map();incoming.forEach(obj=>{const stagedId=obj.id,sourceId=String(obj._sourceObjectId||'');const finalId=id('scwo');obj.id=finalId;delete obj._importFingerprint;delete obj._sourceObjectId;const normalized=normalizeObject(obj);project.objects.unshift(normalized);sourceMap.set(stagedId,finalId);if(sourceId)sourceMap.set(sourceId,finalId);});let importedRelations=0;(Array.isArray(stagedInteroperability.relationships)?stagedInteroperability.relationships:[]).forEach(rel=>{if(project.traceability.lineage.length>=MAX_LINEAGE_RELATIONS)return;const from=sourceMap.get(rel.fromObjectId),to=sourceMap.get(rel.toObjectId);if(!from||!to||from===to)return;project.traceability.lineage.push({id:id('tl'),relation:TRACE_RELATIONS.has(rel.relation)?rel.relation:'derived-from',fromObjectId:from,toObjectId:to,note:String(rel.note||'Imported interoperability relationship').slice(0,1000),createdAt:nowIso()});importedRelations++;});if(importedRelations)touchTraceability(project);project.updatedAt=nowIso();addActivity(project,'interop-import',`Imported ${incoming.length} artifact(s)${importedRelations?` and ${importedRelations} relationship(s)`:''} from ${stagedInteroperability.fileName}`);state.interoperability.history.unshift({id:id('io'),direction:'import',format:stagedInteroperability.format,projectId:project.id,projectTitle:project.title,fileName:stagedInteroperability.fileName,fingerprint:stagedInteroperability.fingerprint,objectCount:incoming.length,at:nowIso()});state.interoperability.history=state.interoperability.history.slice(0,MAX_INTEROP_HISTORY);touchInteroperability();const message=`Imported ${incoming.length} artifact(s) as draft Workspace Objects. Review provenance before using them as evidence.`;stagedInteroperability=null;if(interoperabilityFile)interoperabilityFile.value='';persist(message);render();setWorkspaceView('interoperability');});
    if(interoperabilityExport)interoperabilityExport.addEventListener('click',()=>{const project=state.projects.find(p=>p.id===(interoperabilityExportProject&&interoperabilityExportProject.value)&&!p.archivedAt);if(!project){window.alert('Choose a project to export.');return;}const pkg=interchangePackage(project);const name=`${safeFileName(project.title)}.sc-workspace-interchange.json`;downloadJson(name,pkg);state.interoperability.history.unshift({id:id('io'),direction:'export',format:'json',projectId:project.id,projectTitle:project.title,fileName:name,fingerprint:'',objectCount:pkg.objects.length,at:nowIso()});state.interoperability.history=state.interoperability.history.slice(0,MAX_INTEROP_HISTORY);touchInteroperability();persist('Interchange package exported');renderInteroperability();});
    if (cloudProject) cloudProject.addEventListener('change',()=>{ state.accountPersistence=normalizeAccountPersistence(state.accountPersistence,state.projects); state.accountPersistence.selectedProjectId=String(cloudProject.value||''); touchAccountPersistence(); persist('Cloud backup project selection saved'); renderCloudRecovery(); });
    if (cloudRefreshButton) cloudRefreshButton.addEventListener('click',()=>refreshCloudProjects(true));
    if (cloudBackupButton) cloudBackupButton.addEventListener('click',async()=>{
      const project=state.projects.find(p=>p.id===String(cloudProject?.value||'')&&!p.archivedAt);
      if(!project||!IDENTITY_CONFIG.authenticated)return;
      cloudBackupButton.disabled=true;
      try {
        cloudStatus.textContent=`Backing up ${project.title}…`;
        const data=await cloudRequest('cloud-projects',{method:'POST',body:JSON.stringify(cloudBackupPayload(project))});
        touchAccountPersistence('backup',project);
        if(data?.item){state.accountPersistence.cloudRecords=[data.item,...state.accountPersistence.cloudRecords.filter(r=>r.projectId!==data.item.projectId)];}
        persist('Manual account cloud backup saved'); renderCloudRecovery(); cloudStatus.textContent=`Manual account backup saved for ${project.title}.`;
      } catch(error){ cloudStatus.textContent=error.message||'Backup failed.'; }
      finally { renderCloudRecovery(); }
    });

    if (syncProject) syncProject.addEventListener('change', () => { renderAccountSync(); });
    if (syncToggleButton) syncToggleButton.addEventListener('click', () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt);
      if (!project || !IDENTITY_CONFIG.authenticated) return;
      const enrollment = syncEnrollment(project.id, true);
      enrollment.enabled = !enrollment.enabled;
      enrollment.status = enrollment.enabled ? (enrollment.serverRevision ? 'up-to-date' : 'not-uploaded') : 'disabled';
      enrollment.updatedAt = nowIso();
      recordSync(enrollment.enabled ? 'enable' : 'disable', project, enrollment.serverRevision);
      persist(enrollment.enabled ? 'Cross-device sync enabled locally' : 'Cross-device sync disabled locally');
      renderAccountSync();
    });
    if (syncCheckButton) syncCheckButton.addEventListener('click', async () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt);
      if (!project) return;
      syncCheckButton.disabled = true;
      syncStatus.textContent = 'Comparing local and cloud revisions…';
      try {
        const result = await evaluateSync(project, true);
        recordSync(result.status === 'conflict' ? 'conflict' : result.status === 'remote-missing' ? 'remote-missing' : 'check', project, result.remote?.revision || result.enrollment?.serverRevision || 0);
        persist('Cross-device sync status checked');
        renderCloudRecovery(); renderAccountSync(); syncStatus.textContent = result.message;
      } catch (error) {
        const enrollment = syncEnrollment(project.id, true); enrollment.status = 'error';
        syncStatus.textContent = error.message || 'Sync status check failed.'; renderAccountSync();
      } finally { syncCheckButton.disabled = false; }
    });
    if (syncNowButton) syncNowButton.addEventListener('click', async () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt);
      if (!project) return;
      syncNowButton.disabled = true;
      syncStatus.textContent = 'Comparing revisions before synchronization…';
      try {
        const result = await evaluateSync(project, true);
        const enrollment = result.enrollment;
        if (result.status === 'not-uploaded') {
          const item = await pushSyncHead(project, enrollment, 0); recordSync('push', project, item.revision); syncStatus.textContent = `Created cloud sync revision ${item.revision}.`;
        } else if (result.status === 'local-ahead') {
          const item = await pushSyncHead(project, enrollment, enrollment.serverRevision); recordSync('push', project, item.revision); syncStatus.textContent = `Pushed local changes as cloud revision ${item.revision}.`;
        } else if (result.status === 'remote-ahead') {
          const source = await applyRemoteInPlace(project, enrollment, result.remote, false); recordSync('pull', source, enrollment.serverRevision); syncStatus.textContent = `Applied cloud revision ${enrollment.serverRevision}; no competing local edits were detected.`;
        } else if (result.status === 'remote-missing') {
          if (window.confirm('The previous cloud sync head is missing. Recreate it from this local project?')) {
            const item = await pushSyncHead(project, enrollment, 0); recordSync('push', project, item.revision); syncStatus.textContent = `Recreated cloud sync head at revision ${item.revision}.`;
          } else syncStatus.textContent = result.message;
        } else if (result.status === 'conflict') {
          recordSync('conflict', project, result.remote?.revision || 0); syncStatus.textContent = result.message;
        } else syncStatus.textContent = result.message;
        persist('Cross-device synchronization completed'); render();
      } catch (error) {
        const enrollment = syncEnrollment(project.id, true);
        enrollment.status = /revision conflict/i.test(String(error.message || '')) ? 'conflict' : 'error';
        recordSync(enrollment.status === 'conflict' ? 'conflict' : 'check', project, enrollment.remoteRevision || enrollment.serverRevision);
        persist('Cross-device sync state updated'); renderAccountSync(); syncStatus.textContent = error.message || 'Synchronization failed.';
      } finally { syncNowButton.disabled = false; }
    });
    if (syncRemoteCopyButton) syncRemoteCopyButton.addEventListener('click', async () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt); if (!project) return;
      try {
        const remote = remoteCloudRecord(project.id); if (!remote) throw new Error('No cloud revision is available.');
        const { source } = await fetchRemoteSyncProject(project.id); const copy = cloneProject(source);
        copy.title = `${source.title} (Cloud copy r${remote.revision})`.slice(0,120);
        copy.activity.unshift({ id:id('act'), type:'sync-remote-copy', summary:`Opened cloud revision ${remote.revision} as a separate local copy`, at:nowIso() });
        state.projects.unshift(copy); state.activeProjectId = copy.id; recordSync('remote-copy', project, remote.revision);
        persist('Cloud revision opened as a local copy'); render(); setWorkspaceView('projects', true);
      } catch (error) { syncStatus.textContent = error.message || 'Cloud revision could not be opened as a copy.'; }
    });
    if (syncResolveLocalButton) syncResolveLocalButton.addEventListener('click', async () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt); if (!project) return;
      try { await refreshCloudIndexForSync(); const remote=remoteCloudRecord(project.id); if(!remote)throw new Error('The cloud head disappeared; check status again.'); const fetched=await fetchRemoteSyncProject(project.id); await openSafeActionGate({action:'sync-resolve-local',project,baseProject:fetched.source,baseMeta:{kind:'cloud-revision',id:String(remote.revision),label:`Cloud revision ${remote.revision}`},targetProject:project,targetMeta:{kind:'current-project',id:project.id,label:'Local project'},perform:async()=>{await refreshCloudIndexForSync();const latest=remoteCloudRecord(project.id);if(!latest)throw new Error('The cloud head disappeared; check status again.');const enrollment=syncEnrollment(project.id,true);const item=await pushSyncHead(project,enrollment,latest.revision);recordSync('resolve-local',project,item.revision);persist('Sync conflict resolved with local project');render();syncStatus.textContent=`Conflict resolved with local project at cloud revision ${item.revision}.`;}}); } catch(error){syncStatus.textContent=error.message||'Conflict resolution preflight failed.';}
    });
    if (syncResolveCloudButton) syncResolveCloudButton.addEventListener('click', async () => {
      const project = state.projects.find(item => item.id === String(syncProject?.value || '') && !item.archivedAt); if (!project) return;
      try { await refreshCloudIndexForSync(); const remote=remoteCloudRecord(project.id); if(!remote)throw new Error('The cloud head disappeared; check status again.'); const fetched=await fetchRemoteSyncProject(project.id); await openSafeActionGate({action:'sync-resolve-cloud',project,baseProject:project,baseMeta:{kind:'current-project',id:project.id,label:'Local project'},targetProject:fetched.source,targetMeta:{kind:'cloud-revision',id:String(remote.revision),label:`Cloud revision ${remote.revision}`},perform:async()=>{await refreshCloudIndexForSync();const latest=remoteCloudRecord(project.id);if(!latest)throw new Error('The cloud head disappeared; check status again.');const enrollment=syncEnrollment(project.id,true);const source=await applyRemoteInPlace(project,enrollment,latest,true);recordSync('resolve-cloud',source,enrollment.serverRevision);persist('Sync conflict resolved with cloud revision; local conflict copy preserved');render();syncStatus.textContent=`Conflict resolved with cloud revision ${enrollment.serverRevision}; local changes were preserved as a separate copy.`;}}); } catch(error){syncStatus.textContent=error.message||'Conflict resolution preflight failed.';}
    });

    if(collabProfileForm)collabProfileForm.addEventListener('submit',event=>{event.preventDefault();const data=new FormData(collabProfileForm);state.collaboration.profile={displayName:String(data.get('displayName')||'').trim().slice(0,120),role:COLLAB_ROLES.has(String(data.get('role')))?String(data.get('role')):'owner'};touchCollaboration();persist('Local review identity saved');renderCollaboration();});
    if(collabRequestForm)collabRequestForm.addEventListener('submit',event=>{event.preventDefault();if(state.collaboration.sessions.length>=MAX_COLLAB_SESSIONS){window.alert('This local Workspace has reached its review-session limit.');return;}const data=new FormData(collabRequestForm),projectId=String(data.get('projectId')||''),project=state.projects.find(p=>p.id===projectId&&!p.archivedAt),title=String(data.get('title')||'').trim().slice(0,200);if(!project||!title)return;const stamp=nowIso(),requestId=id('rrq'),ownerLabel=state.collaboration.profile.displayName||'Workspace owner';const session={id:id('cr'),requestId,localProjectId:project.id,sourceProjectId:project.id,title,purpose:String(data.get('purpose')||'').slice(0,2400),status:'draft',requestedRole:COLLAB_ROLES.has(String(data.get('requestedRole')))?String(data.get('requestedRole')):'reviewer',ownerLabel,participants:[{id:id('cp'),displayName:ownerLabel,role:'owner',origin:'local',createdAt:stamp}],threads:[],importedResponseCount:0,createdAt:stamp,updatedAt:stamp,closedAt:null};state.collaboration.sessions.unshift(session);state.collaboration.activeSessionId=session.id;touchCollaboration();addActivity(project,'collaboration-review',`Collaboration review created: ${title}`);collabRequestForm.reset();persist('Review request created');renderCollaboration();});
    if(collabThreadForm)collabThreadForm.addEventListener('submit',event=>{event.preventDefault();const session=activeCollaborationSession();if(!session||session.threads.length>=MAX_COLLAB_THREADS)return;const data=new FormData(collabThreadForm),body=String(data.get('body')||'').trim().slice(0,5000);if(!body)return;const project=state.projects.find(p=>p.id===session.localProjectId),objectId=String(data.get('objectId')||''),obj=project?.objects.find(o=>o.id===objectId&&!o.archivedAt);const stamp=nowIso();session.threads.unshift({id:id('ct'),kind:COLLAB_THREAD_KIND.has(String(data.get('kind')))?String(data.get('kind')):'comment',body,objectId:obj?obj.id:'',authorLabel:state.collaboration.profile.displayName||'Reviewer',authorRole:state.collaboration.profile.role, status:'open',origin:'local',createdAt:stamp,updatedAt:stamp,resolvedAt:null});session.status=session.status==='draft'?'in-review':session.status;session.updatedAt=stamp;touchCollaboration();if(project)addActivity(project,'collaboration-thread',`Review ${String(data.get('kind')||'comment')} added`);collabThreadForm.reset();persist('Review thread added');renderCollaboration();});
    if(collabExportRequest)collabExportRequest.addEventListener('click',async()=>{const session=activeCollaborationSession();if(!session){window.alert('Open a review session first.');return;}try{const pkg=await collaborationRequestPackage(session),project=state.projects.find(p=>p.id===session.localProjectId),name=`${safeFileName(session.title)}.sc-workspace-review-request.json`;downloadJson(name,pkg);session.status=session.status==='draft'?'requested':session.status;session.updatedAt=nowIso();state.collaboration.history.unshift({id:id('ch'),direction:'export',kind:'request',sessionId:session.id,projectId:session.localProjectId,projectTitle:project?.title||session.title,fileName:name,fingerprint:String(pkg.integrity?.payloadFingerprint||''),threadCount:session.threads.length,at:nowIso()});state.collaboration.history=state.collaboration.history.slice(0,MAX_COLLAB_HISTORY);touchCollaboration();persist('Review request exported');renderCollaboration();}catch(err){window.alert(err?.message||'Review request could not be exported.');}});
    if(collabExportResponse)collabExportResponse.addEventListener('click',async()=>{const session=activeCollaborationSession();if(!session){window.alert('Open a review session first.');return;}const pkg=await collaborationResponsePackage(session),project=state.projects.find(p=>p.id===session.localProjectId),name=`${safeFileName(session.title)}.sc-workspace-review-response.json`;downloadJson(name,pkg);state.collaboration.history.unshift({id:id('ch'),direction:'export',kind:'response',sessionId:session.id,projectId:session.localProjectId,projectTitle:project?.title||session.title,fileName:name,fingerprint:String(pkg.integrity?.payloadFingerprint||''),threadCount:session.threads.length,at:nowIso()});state.collaboration.history=state.collaboration.history.slice(0,MAX_COLLAB_HISTORY);touchCollaboration();persist('Review response exported');renderCollaboration();});
    if(collabImport)collabImport.addEventListener('click',()=>collabFile&&collabFile.click());
    if(collabFile)collabFile.addEventListener('change',async()=>{const file=collabFile.files&&collabFile.files[0];if(!file)return;if(file.size>8*1024*1024){window.alert('Review packages are limited to 8 MB in this local release.');collabFile.value='';return;}try{const pkg=JSON.parse(await file.text()),verification=await verifyReviewPackage(pkg);stagedReviewPackage={fileName:file.name,package:pkg,verification};renderCollaboration();}catch(_){stagedReviewPackage=null;renderCollaboration();window.alert('Workspace could not stage this review package.');}finally{collabFile.value='';}});
    if(collabClear)collabClear.addEventListener('click',()=>{stagedReviewPackage=null;renderCollaboration();});
    if(collabCommit)collabCommit.addEventListener('click',()=>{if(!stagedReviewPackage||!stagedReviewPackage.verification.ok)return;const pkg=stagedReviewPackage.package,request=pkg.request||{};if(pkg.kind==='request'){const copy=normalizeProject(pkg.project);if(!copy){window.alert('Review request project content is invalid.');return;}const sourceProjectId=String(request.sourceProjectId||copy.id);copy.id=id('scwp');copy.persistence=projectPersistenceTemplate();copy.pinned=false;copy.archivedAt=null;copy.handoffs=handoffLedgerTemplate();copy.activity=[{id:id('act'),type:'collaboration-review-import',summary:`Imported collaboration review request: ${request.title||copy.title}`,at:nowIso()}];copy.title=(state.projects.some(p=>p.title===copy.title)?`${copy.title} (review copy)`:copy.title).slice(0,120);copy.updatedAt=nowIso();state.projects.unshift(copy);const stamp=nowIso(),ownerLabel=String(request.ownerLabel||'Workspace owner').slice(0,120),session={id:id('cr'),requestId:String(request.id||id('rrq')).slice(0,160),localProjectId:copy.id,sourceProjectId,title:String(request.title||'Workspace review').slice(0,200),purpose:String(request.purpose||'').slice(0,2400),status:'in-review',requestedRole:COLLAB_ROLES.has(request.requestedRole)?request.requestedRole:'reviewer',ownerLabel,participants:[{id:id('cp'),displayName:ownerLabel,role:'owner',origin:'package',createdAt:stamp},{id:id('cp'),displayName:state.collaboration.profile.displayName||'Reviewer',role:state.collaboration.profile.role,origin:'local',createdAt:stamp}],threads:(Array.isArray(pkg.threads)?pkg.threads:[]).map(t=>({...t,id:id('ct'),sourceThreadId:String(t.id||''),origin:'request-package'})),importedResponseCount:0,createdAt:stamp,updatedAt:stamp,closedAt:null};state.collaboration.sessions.unshift(normalizeCollabSession(session,state.projects));state.collaboration.activeSessionId=session.id;state.activeProjectId=copy.id;state.collaboration.history.unshift({id:id('ch'),direction:'import',kind:'request',sessionId:session.id,projectId:copy.id,projectTitle:copy.title,fileName:stagedReviewPackage.fileName,fingerprint:String(pkg.integrity?.payloadFingerprint||''),threadCount:session.threads.length,at:stamp});}else{const session=state.collaboration.sessions.find(s=>s.requestId===String(request.id||'')&&s.sourceProjectId===String(request.sourceProjectId||''));if(!session){window.alert('No matching local review request was found. Import the response into the Workspace that created the request.');return;}const project=state.projects.find(p=>p.id===session.localProjectId);const objectIds=new Set(project?project.objects.map(o=>o.id):[]),known=new Set(session.threads.filter(t=>t.origin==='response'&&t.sourceThreadId).map(t=>`response:${t.sourceThreadId}`));(Array.isArray(pkg.threads)?pkg.threads:[]).forEach(raw=>{if(session.threads.length>=MAX_COLLAB_THREADS)return;const key=`response:${String(raw.id||'')}`;if(known.has(key))return;const t=normalizeCollabThread({...raw,id:id('ct'),sourceThreadId:String(raw.id||''),origin:'response'},objectIds);if(t){session.threads.push(t);known.add(key);}});const responder=normalizeCollabParticipant({displayName:pkg.responder?.displayName||'Reviewer',role:pkg.responder?.role||'reviewer',origin:'response'});if(responder&&!session.participants.some(p=>p.displayName===responder.displayName&&p.role===responder.role))session.participants.push(responder);session.importedResponseCount+=1;session.status=COLLAB_SESSION_STATUS.has(pkg.status)?pkg.status:(session.status==='requested'?'in-review':session.status);session.updatedAt=nowIso();state.collaboration.history.unshift({id:id('ch'),direction:'import',kind:'response',sessionId:session.id,projectId:session.localProjectId,projectTitle:project?.title||session.title,fileName:stagedReviewPackage.fileName,fingerprint:String(pkg.integrity?.payloadFingerprint||''),threadCount:Array.isArray(pkg.threads)?pkg.threads.length:0,at:nowIso()});if(project)addActivity(project,'collaboration-response',`Review response imported: ${session.title}`);}state.collaboration.history=state.collaboration.history.slice(0,MAX_COLLAB_HISTORY);touchCollaboration();stagedReviewPackage=null;persist('Review package committed locally');render();setWorkspaceView('collaboration');});

    if(institutionalProject)institutionalProject.addEventListener('change',()=>{institutionalObjectScope.dataset.projectId=institutionalProject.value;renderInstitutionalObjectScope(institutionalProject.value);});
    if(institutionalForm)institutionalForm.addEventListener('submit',event=>{event.preventDefault();state.institutional=normalizeInstitutional(state.institutional,state.projects);if(state.institutional.handoffs.length>=MAX_INSTITUTIONAL_HANDOFFS){window.alert('This local Workspace has reached the institutional handoff limit.');return;}const data=new FormData(institutionalForm),projectId=String(data.get('projectId')||''),project=state.projects.find(p=>p.id===projectId&&!p.archivedAt),organizationLabel=String(data.get('organizationLabel')||'').trim().slice(0,200),purpose=String(data.get('purpose')||'').trim().slice(0,3000),objectIds=[...new Set(data.getAll('objectIds[]').map(v=>String(v).slice(0,160)))].filter(v=>project?.objects.some(o=>o.id===v&&!o.archivedAt));const acknowledgements={copyModel:data.get('copyModel')==='on',institutionalGovernance:data.get('institutionalGovernance')==='on',sharingReviewed:data.get('sharingReviewed')==='on'};if(!project||!organizationLabel||!purpose){window.alert('Project, receiving organization, and purpose are required.');return;}if(!objectIds.length){window.alert('Select at least one canonical Workspace Object for institutional promotion.');return;}if(!Object.values(acknowledgements).every(Boolean)){window.alert('Review and accept all institutional handoff acknowledgements before preparing the package.');return;}const stamp=nowIso(),handoff={id:id('ih'),projectId:project.id,sourceProjectId:project.id,targetProduct:'catalyst-intelligence-platform',organizationLabel,purpose,status:'prepared',objectIds,acknowledgements,packageFingerprint:'',externalRecordId:'',receiptNote:'',createdAt:stamp,updatedAt:stamp,exportedAt:null,receiptAt:null,closedAt:null};state.institutional.handoffs.unshift(handoff);state.institutional.activeHandoffId=handoff.id;touchInstitutional();addActivity(project,'institutional-handoff',`Institutional handoff prepared for ${organizationLabel}`);institutionalForm.reset();institutionalObjectScope.dataset.projectId='';persist('Institutional handoff prepared');renderInstitutional();});
    if(institutionalExport)institutionalExport.addEventListener('click',async()=>{const handoff=activeInstitutionalHandoff();if(!handoff)return;const project=state.projects.find(p=>p.id===handoff.projectId);if(!project)return;try{await gateFromLatestRestore('institutional-promotion',project,async()=>{const pkg=await institutionalPromotionPackage(handoff),name=`${safeFileName(project.title||'workspace-project')}.sc-workspace-institutional-handoff.json`;downloadJson(name,pkg);handoff.status='exported';handoff.packageFingerprint=String(pkg.integrity?.payloadFingerprint||'');handoff.exportedAt=nowIso();handoff.updatedAt=handoff.exportedAt;state.institutional.history.unshift({id:id('ihh'),direction:'export',kind:'promotion',handoffId:handoff.id,projectId:handoff.projectId,projectTitle:project.title||'',organizationLabel:handoff.organizationLabel,fileName:name,fingerprint:handoff.packageFingerprint,status:handoff.status,objectCount:handoff.objectIds.length,at:handoff.exportedAt});state.institutional.history=state.institutional.history.slice(0,MAX_INSTITUTIONAL_HISTORY);touchInstitutional();addActivity(project,'institutional-export',`Institutional promotion package exported for ${handoff.organizationLabel}`);persist('Institutional promotion package exported');renderInstitutional();});}catch(err){window.alert(err?.message||'Institutional handoff preflight could not be opened.');}});
    if(institutionalClose)institutionalClose.addEventListener('click',()=>{const handoff=activeInstitutionalHandoff();if(!handoff)return;handoff.status='closed';handoff.closedAt=nowIso();handoff.updatedAt=handoff.closedAt;touchInstitutional();persist('Institutional handoff closed');renderInstitutional();});
    if(institutionalImport)institutionalImport.addEventListener('click',()=>institutionalFile&&institutionalFile.click());
    if(institutionalFile)institutionalFile.addEventListener('change',async()=>{const file=institutionalFile.files&&institutionalFile.files[0];if(!file)return;if(file.size>2*1024*1024){window.alert('Institutional receipt files are limited to 2 MB.');institutionalFile.value='';return;}try{const pkg=JSON.parse(await file.text()),verification=await verifyInstitutionalReceipt(pkg);stagedInstitutionalReceipt={fileName:file.name,package:pkg,verification};renderInstitutional();}catch(_){stagedInstitutionalReceipt=null;renderInstitutional();window.alert('Workspace could not stage this institutional receipt.');}finally{institutionalFile.value='';}});
    if(institutionalClear)institutionalClear.addEventListener('click',()=>{stagedInstitutionalReceipt=null;renderInstitutional();});
    if(institutionalCommit)institutionalCommit.addEventListener('click',()=>{if(!stagedInstitutionalReceipt||!stagedInstitutionalReceipt.verification.ok)return;const result=ingestInstitutionalReceiptPacket(state,stagedInstitutionalReceipt.package,stagedInstitutionalReceipt.fileName);if(!result.ok){window.alert(result.message);return;}state.institutional.activeHandoffId=result.handoffId;stagedInstitutionalReceipt=null;persist(result.message);render();setWorkspaceView('institutional');});

    if(shareExport)shareExport.addEventListener('click',async()=>{const project=state.projects.find(p=>p.id===(shareProject&&shareProject.value)&&!p.archivedAt);if(!project){window.alert('Choose a project to share.');return;}const options={includeArchived:Boolean(shareIncludeArchived&&shareIncludeArchived.checked),includeActivity:Boolean(shareIncludeActivity&&shareIncludeActivity.checked),includeAi:Boolean(shareIncludeAi&&shareIncludeAi.checked)};await gateFromLatestRestore('share-portable',project,async()=>{const pkg=await portableProjectPackage(project,options),name=`${safeFileName(project.title)}.sc-workspace-project.json`;downloadJson(name,pkg);state.share.history.unshift({id:id('sh'),direction:'export',kind:'portable-project',projectId:project.id,projectTitle:project.title,fileName:name,fingerprint:pkg.integrity.payloadFingerprint,objectCount:pkg.manifest.objectCount,at:nowIso()});state.share.history=state.share.history.slice(0,MAX_SHARE_HISTORY);touchShare();persist('Portable project exported');renderShare();});});
    if(shareReview)shareReview.addEventListener('click',async()=>{const project=state.projects.find(p=>p.id===(shareProject&&shareProject.value)&&!p.archivedAt);if(!project){window.alert('Choose a project to review.');return;}await gateFromLatestRestore('share-review-copy',project,async()=>{const name=`${safeFileName(project.title)}.workspace-review.html`;downloadText(name,reviewCopyHtml(project),'text/html');state.share.history.unshift({id:id('sh'),direction:'export',kind:'review-html',projectId:project.id,projectTitle:project.title,fileName:name,fingerprint:'',objectCount:project.objects.filter(o=>!o.archivedAt).length,at:nowIso()});state.share.history=state.share.history.slice(0,MAX_SHARE_HISTORY);touchShare();persist('Static review copy exported');renderShare();});});
    if(shareFile)shareFile.addEventListener('change',async()=>{stagedPortableProject=null;const file=shareFile.files&&shareFile.files[0];if(!file){renderShare();return;}if(file.size>8*1024*1024){window.alert('Portable project packages are limited to 8 MB in this local release.');shareFile.value='';renderShare();return;}try{const pkg=JSON.parse(await file.text()),verification=await verifyPortablePackage(pkg);stagedPortableProject={fileName:file.name,package:pkg,verification};renderShare();if(!verification.ok)window.alert(verification.message);}catch(err){stagedPortableProject=null;renderShare();window.alert(err&&err.message?err.message:'Workspace could not read this portable project.');}});
    if(shareClear)shareClear.addEventListener('click',()=>{stagedPortableProject=null;if(shareFile)shareFile.value='';renderShare();});
    if(shareImport)shareImport.addEventListener('click',()=>{if(!stagedPortableProject||!stagedPortableProject.verification.ok)return;const pkg=stagedPortableProject.package,copy=normalizeProject(pkg.project);if(!copy){window.alert('Portable project content is not valid.');return;}const originalId=copy.id;copy.id=id('scwp');copy.persistence=projectPersistenceTemplate();copy.pinned=false;copy.archivedAt=null;copy.recentTools=[];copy.handoffs=handoffLedgerTemplate();copy.activity=[{id:id('act'),type:'portable-import',summary:`Imported as a portable copy from ${pkg.manifest?.projectTitle||copy.title}`,at:nowIso()}];copy.title=(state.projects.some(p=>p.title===copy.title)?`${copy.title} (shared copy)`:copy.title).slice(0,120);copy.updatedAt=nowIso();state.projects.unshift(copy);state.activeProjectId=copy.id;state.share.history.unshift({id:id('sh'),direction:'import',kind:'portable-project',projectId:copy.id,projectTitle:copy.title,fileName:stagedPortableProject.fileName,fingerprint:String(pkg.integrity&&pkg.integrity.payloadFingerprint||''),objectCount:copy.objects.length,at:nowIso()});state.share.history=state.share.history.slice(0,MAX_SHARE_HISTORY);touchShare();stagedPortableProject=null;if(shareFile)shareFile.value='';persist(`Portable project imported as a new local copy. Source project ID: ${originalId}`);render();setWorkspaceView('projects');});

    if(historyProject)historyProject.addEventListener('change',()=>{state.versionHistory.selectedProjectId=historyProject.value||'';state.versionHistory.updatedAt=nowIso();persist('Version-history project selection saved');});
    if(historyFilter)historyFilter.addEventListener('change',renderVersionHistory);
    if(historyForm)historyForm.addEventListener('submit',async(event)=>{event.preventDefault();const data=new FormData(historyForm),project=state.projects.find(item=>item.id===String(data.get('projectId')||'')&&!item.archivedAt);if(!project){if(historyStatus)historyStatus.textContent='Choose an active project first.';return;}const label=String(data.get('label')||'').trim();if(!label){if(historyStatus)historyStatus.textContent='Add a restore-point label.';return;}if(historyStatus)historyStatus.textContent='Creating SHA-256 restore point…';try{const point=await createRestorePoint(project,label,String(data.get('note')||''));state.versionHistory.selectedProjectId=project.id;persist('Named restore point created');historyForm.reset();if(historyProject)historyProject.value=project.id;if(historyStatus)historyStatus.textContent=`Restore point “${point.label}” created without changing the project.`;renderVersionHistory();}catch(err){if(historyStatus)historyStatus.textContent=err&&err.message?err.message:'Workspace could not create the restore point.';}});

    if(actionGateAck)actionGateAck.addEventListener('change',()=>{if(actionGateProceed)actionGateProceed.disabled=!Boolean(actionGateAck.checked);});
    if(actionGateProceed)actionGateProceed.addEventListener('click',async()=>{if(!activeSafeGate||!activeSafeAction||!window.SCWorkspaceSafeActions?.canProceed(activeSafeGate,Boolean(actionGateAck?.checked)))return;actionGateProceed.disabled=true;if(actionGateStatus)actionGateStatus.textContent='Proceeding with the acknowledged action…';const gate=activeSafeGate,action=activeSafeAction;try{await action();recordSafeAction(gate,'proceeded');persist('Safe action proceeded after explicit preflight');activeSafeGate=null;activeSafeAction=null;if(actionGate)actionGate.hidden=true;renderSafeActions();}catch(err){recordSafeAction(gate,'blocked');persist('Safe action blocked after preflight');if(actionGateStatus)actionGateStatus.textContent=err?.message||'The action was blocked.';renderSafeActions();}});
    root.querySelectorAll('[data-scw-action-gate-cancel]').forEach(el=>el.addEventListener('click',()=>closeSafeActionGate('cancelled')));

    root.querySelectorAll('[data-scw-workspace-view]').forEach((button) => {
      button.addEventListener('click', () => setWorkspaceView(button.dataset.scwWorkspaceView, true));
    });

    if (runDiagnostics) runDiagnostics.addEventListener('click', () => {
      latestDiagnosticReport = privacyMinimizedDiagnostic(state);
      renderDiagnosticReport(latestDiagnosticReport);
    });
    if (exportDiagnostics) exportDiagnostics.addEventListener('click', () => {
      latestDiagnosticReport = latestDiagnosticReport || privacyMinimizedDiagnostic(state);
      downloadJson(`workspace-diagnostics-v${rootVersion()}.json`, latestDiagnosticReport);
      if (readinessStatus) readinessStatus.textContent = 'Privacy-minimized diagnostic report exported. No project content, source URLs, or device identifier are included.';
    });
    if (emergencyBackup) emergencyBackup.addEventListener('click', () => {
      const payload = emergencyBackupPayload(state);
      downloadJson(`sustainable-catalyst-workspace-emergency-backup-${new Date().toISOString().slice(0,10)}.json`, payload);
      if (readinessStatus) readinessStatus.textContent = 'Emergency backup exported explicitly. This file contains Workspace project content; store it accordingly.';
    });

    if(changeProject)changeProject.addEventListener('change',()=>{activeChangeReview=null;populateChangeReviewSelectors(changeProject.value);renderChangeReview();});
    if(changeBase)changeBase.addEventListener('change',()=>{activeChangeReview=null;changeRun.disabled=!changeBase.value;renderChangeReview();});
    if(changeTarget)changeTarget.addEventListener('change',()=>{activeChangeReview=null;renderChangeReview();});
    if(changeRun)changeRun.addEventListener('click',()=>generateChangeReview());
    if(changeExport)changeExport.addEventListener('click',()=>{if(!activeChangeReview)return;downloadJson(`${safeFileName(activeChangeReview.projectTitle)}-change-review-${new Date().toISOString().slice(0,10)}.json`,activeChangeReview);if(changeStatus)changeStatus.textContent='Change review exported as portable JSON. No project state was modified.';});

    [activityProject,activityWindow,activityStale,activitySignal].forEach(el=>{if(el)el.addEventListener('change',()=>{if(el===activityProject)state.activityIntelligence.preferences.project=el.value;else if(el===activityWindow)state.activityIntelligence.preferences.windowDays=Number(el.value);else if(el===activityStale)state.activityIntelligence.preferences.staleDays=Number(el.value);else if(el===activitySignal)state.activityIntelligence.preferences.signal=el.value;touchActivityIntelligence();persist('Activity Intelligence view saved');renderActivityIntelligence();});});
    if(nextActionForm)nextActionForm.addEventListener('submit',(event)=>{event.preventDefault();state.activityIntelligence=normalizeActivityIntelligence(state.activityIntelligence,state.projects);if(state.activityIntelligence.nextActions.length>=MAX_NEXT_ACTIONS){window.alert('This local Workspace has reached the next-action limit.');return;}const fd=new FormData(nextActionForm),title=String(fd.get('title')||'').trim(),projectId=String(fd.get('projectId')||'');if(!title||!state.projects.some(p=>p.id===projectId&&!p.archivedAt))return;const date=String(fd.get('dueDate')||'').trim();const stamp=nowIso();state.activityIntelligence.nextActions.unshift({id:id('na'),title:title.slice(0,240),projectId,objectId:'',priority:NEXT_ACTION_PRIORITY.has(fd.get('priority'))?fd.get('priority'):'normal',status:'open',dueAt:date?`${date}T12:00:00.000Z`:null,note:'',createdAt:stamp,updatedAt:stamp,completedAt:null});touchActivityIntelligence();nextActionForm.reset();persist('Next action created');renderActivityIntelligence();});
    if(restoreDismissedSignals)restoreDismissedSignals.addEventListener('click',()=>{state.activityIntelligence.dismissedSignalIds=[];touchActivityIntelligence();persist('Dismissed attention signals restored');renderActivityIntelligence();});

    [graphSearch].forEach(el=>{if(el)el.addEventListener('input',()=>{state.knowledgeGraph.preferences.query=el.value.slice(0,240);touchKnowledgeGraph();schedulePersist();renderKnowledgeGraph();});});
    [graphNodeType,graphRelation,graphProject,graphScope,graphDepth].forEach(el=>{if(el)el.addEventListener('change',()=>{if(el===graphNodeType)state.knowledgeGraph.preferences.nodeType=el.value;else if(el===graphRelation)state.knowledgeGraph.preferences.relation=el.value;else if(el===graphProject)state.knowledgeGraph.preferences.project=el.value;else if(el===graphScope)state.knowledgeGraph.preferences.scope=el.value;else if(el===graphDepth)state.knowledgeGraph.preferences.depth=Number(el.value)===2?2:1;touchKnowledgeGraph();persist('Knowledge Graph view saved');renderKnowledgeGraph();});});

    [knowledgeSearch, knowledgeTag].forEach(el => { if(el) el.addEventListener('input',()=>{state.knowledge.preferences[el===knowledgeSearch?'query':'tag']=el.value.slice(0,el===knowledgeSearch?240:80);touchKnowledge();schedulePersist();renderKnowledge();}); });
    [knowledgeType, knowledgeProject, knowledgeScope].forEach(el => { if(el) el.addEventListener('change',()=>{const key=el===knowledgeType?'type':el===knowledgeProject?'project':'scope';state.knowledge.preferences[key]=el.value;touchKnowledge();persist('Knowledge view saved');renderKnowledge();}); });
    if(knowledgeCollectionSelect)knowledgeCollectionSelect.addEventListener('change',()=>{state.knowledge.activeCollectionId=knowledgeCollectionSelect.value||null;touchKnowledge();persist('Knowledge collection selected');renderKnowledge();});
    if(knowledgeCollectionForm)knowledgeCollectionForm.addEventListener('submit',(event)=>{event.preventDefault();if(state.knowledge.collections.length>=MAX_KNOWLEDGE_COLLECTIONS){window.alert('This Workspace has reached the local knowledge collection limit.');return;}const fd=new FormData(knowledgeCollectionForm),title=String(fd.get('title')||'').trim();if(!title)return;const stamp=nowIso(),collection={id:id('kc'),title:title.slice(0,160),description:String(fd.get('description')||'').slice(0,1000),items:[],createdAt:stamp,updatedAt:stamp};state.knowledge.collections.unshift(collection);state.knowledge.activeCollectionId=collection.id;touchKnowledge();knowledgeCollectionForm.reset();persist('Knowledge collection created');renderKnowledge();});

    setProjectMode('overview');

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
            const activeBoard = project.canvas && project.canvas.boards ? project.canvas.boards.find((board) => board.id === project.canvas.activeBoardId) : null;
            const handoff = createHandoff(project, key, label, object, (activeBoard && key === 'catalyst-canvas') ? activeBoard.id : '');
            addActivity(project, 'handoff', `Opened ${label}${object ? ` with ${OBJECT_LABELS[object.type]}` : ''} · ${handoff.id}`);
            target.searchParams.set('sc_workspace_project', project.id);
            target.searchParams.set('sc_workspace_handoff', handoff.id);
            target.searchParams.set('sc_workspace_intent', handoff.intent);
            if (object) target.searchParams.set('sc_workspace_object', object.id);
            if (activeBoard && key === 'catalyst-canvas') target.searchParams.set('sc_workspace_canvas', activeBoard.id);
            target.searchParams.set('sc_workspace_origin', 'workspace');
            target.searchParams.set('sc_workspace_return', '1');
            window.sessionStorage.setItem(HANDOFF_KEY, JSON.stringify({
              schema: HANDOFF_SCHEMA, handoffId: handoff.id, projectId: project.id, objectIds: handoff.objectIds,
              canvasBoardId: handoff.canvasBoardId || null, destination: key, intent: handoff.intent, createdAt: stamp,
              returnUrl: root.dataset.returnUrl || window.location.href, returnSchema: HANDOFF_RETURN_SCHEMA, returnStorageKey: HANDOFF_RETURN_KEY
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
      const returnCanvas = params.get('sc_workspace_canvas');
      const returnHandoff = params.get('sc_workspace_handoff');
      const project = state.projects.find((item) => item.id === returnProject && !item.archivedAt);
      if (project) {
        state.activeProjectId = project.id;
        activeProjectMode = 'overview';
        if (returnObject && project.objects.some((object) => object.id === returnObject && !object.archivedAt)) project.activeObjectId = returnObject;
        if (returnCanvas && project.canvas && project.canvas.boards.some((board) => board.id === returnCanvas)) project.canvas.activeBoardId = returnCanvas;
        if (returnHandoff && project.handoffs) project.handoffs.activeHandoffId = project.handoffs.entries.some((entry)=>entry.id===returnHandoff) ? returnHandoff : project.handoffs.activeHandoffId;
        persist('Workspace context restored');
      }
    } catch (_) {}

    try {
      const receiptRaw=window.sessionStorage.getItem(INSTITUTIONAL_RECEIPT_KEY);
      if(receiptRaw){const result=ingestInstitutionalReceiptPacket(state,JSON.parse(receiptRaw),'same-origin institutional receipt');if(result.ok){window.sessionStorage.removeItem(INSTITUTIONAL_RECEIPT_KEY);state.institutional.activeHandoffId=result.handoffId;}}
    } catch (_) {}
    window.addEventListener('message',(event)=>{if(event.origin!==window.location.origin||!event.data||event.data.type!=='sc-workspace-institutional-receipt')return;const result=ingestInstitutionalReceiptPacket(state,event.data.packet,'same-origin institutional receipt');if(!result.ok)return;state.institutional.activeHandoffId=result.handoffId;persist(result.message);render();setWorkspaceView('institutional');});
    checkAiResponseInbox(false);
    checkReturnInbox(false);
    persist();
    render();
  }

  function bindPlatformNewProjectActions() {
    document.querySelectorAll('[data-scw-platform-new-project]').forEach((button) => {
      if (button.dataset.scwBound === '1') return;
      button.dataset.scwBound = '1';
      button.addEventListener('click', () => {
        const platform = button.closest('[data-sc-workspace-platform]');
        const workspace = platform ? platform.querySelector('[data-sc-workspace]') : null;
        const trigger = workspace ? workspace.querySelector('[data-scw-new-project]') : null;
        const form = workspace ? workspace.querySelector('[data-scw-create-form]') : null;
        if (!trigger || !form) return;
        trigger.click();
        form.scrollIntoView({
          behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
          block: 'center'
        });
      });
    });
  }

  function boot() {
    document.querySelectorAll('[data-sc-workspace]').forEach(init);
    bindPlatformNewProjectActions();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
