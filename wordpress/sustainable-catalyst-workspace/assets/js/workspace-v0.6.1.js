(() => {
  'use strict';

  const STORAGE_KEY = 'sc_workspace';
  const LEGACY_KEY = 'sc_workspace_v0_1';
  const RECOVERY_KEY = 'sc_workspace_recovery_v0_6_0';
  const DEVICE_KEY = 'sc_workspace_device_v1';
  const HANDOFF_KEY = 'sc_workspace_handoff_v1';
  const STORAGE_VERSION = 7;
  const PROJECT_SCHEMA = 'sc-workspace-project/5.0';
  const LEGACY_PROJECT_SCHEMA_V4 = 'sc-workspace-project/4.0';
  const LEGACY_PROJECT_SCHEMA_V31 = 'sc-workspace-project/3.1';
  const LEGACY_PROJECT_SCHEMA_V3 = 'sc-workspace-project/3.0';
  const LEGACY_PROJECT_SCHEMA_V2 = 'sc-workspace-project/2.0';
  const LEGACY_PROJECT_SCHEMA_V1 = 'sc-workspace-project/1.0';
  const OBJECT_SCHEMA = 'sc-workspace-object/1.0';
  const EXPORT_SCHEMA = 'sc-workspace-project-export/5.0';
  const LEGACY_EXPORT_SCHEMA_V4 = 'sc-workspace-project-export/4.0';
  const LEGACY_EXPORT_SCHEMA_V31 = 'sc-workspace-project-export/3.1';
  const LEGACY_EXPORT_SCHEMA_V3 = 'sc-workspace-project-export/3.0';
  const LEGACY_EXPORT_SCHEMA_V2 = 'sc-workspace-project-export/2.0';
  const LEGACY_EXPORT_SCHEMA_V1 = 'sc-workspace-project-export/1.0';
  const OBJECT_EXPORT_SCHEMA = 'sc-workspace-object-export/1.0';
  const HANDOFF_SCHEMA = 'sc-workspace-handoff/1.4';
  const RESEARCH_SCHEMA = 'sc-workspace-research/1.0';
  const IDENTITY_SCHEMA = 'sc-workspace-identity/1.0';
  const ANALYSIS_SCHEMA = 'sc-workspace-analysis/1.0';
  const DECISION_SCHEMA = 'sc-workspace-decision/1.0';
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
  const ALLOWED_STATUS = new Set(['active', 'paused', 'complete']);
  const OBJECT_TYPES = new Set(['source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export']);
  const OBJECT_STATUS = new Set(['draft', 'working', 'ready']);
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

  function defaultState() {
    const stamp = nowIso();
    return { schemaVersion: STORAGE_VERSION, identity: identityTemplate(), activeProjectId: null, projects: [], recentTools: [], createdAt: stamp, updatedAt: stamp };
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
      decision: decisionTemplate()
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
      decision: normalizeDecision(raw.decision, objects)
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
      if (normalized && project.schema === LEGACY_PROJECT_SCHEMA_V1) addActivity(normalized, 'migrated', 'Project upgraded from v0.2.0 to Workspace object model');
      return normalized;
    }).filter(Boolean) : [];
    state.recentTools = Array.isArray(raw.recentTools) ? raw.recentTools.map(normalizeRecentTool).filter(Boolean).slice(0, MAX_RECENT_TOOLS) : [];
    state.activeProjectId = state.projects.some((project) => project.id === raw.activeProjectId && !project.archivedAt) ? raw.activeProjectId : null;
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

  function normalizeState(raw) {
    if (!raw || typeof raw !== 'object') return defaultState();
    if (raw.schemaVersion === 1 || raw.schema === 1) return migrateLegacyV1(raw);
    if (raw.schemaVersion === 2) return migrateV2(raw);
    if (raw.schemaVersion === 3) return migrateV3(raw);
    if (raw.schemaVersion === 4) return migrateV4(raw);
    if (raw.schemaVersion === 5) return migrateV5(raw);
    if (raw.schemaVersion === 6) return migrateV6(raw);
    const state = defaultState();
    state.identity = normalizeIdentity(raw.identity);
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
    state.identity = normalizeIdentity(state.identity);
    state.projects.forEach((project) => { project.persistence = normalizeProjectPersistence(project.persistence); });
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
    const identityBadge = root.querySelector('[data-scw-identity-badge]');
    const identityHeading = root.querySelector('[data-scw-identity-heading]');
    const identityDetail = root.querySelector('[data-scw-identity-detail]');
    const identityAccess = root.querySelector('[data-scw-identity-access]');
    const identityNote = root.querySelector('[data-scw-identity-note]');
    const deviceIdEl = root.querySelector('[data-scw-device-id]');
    const loginLink = root.querySelector('[data-scw-login]');
    const registerLink = root.querySelector('[data-scw-register]');
    const logoutLink = root.querySelector('[data-scw-logout]');

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


    function renderIdentity() {
      const authenticated = Boolean(IDENTITY_CONFIG.authenticated);
      state.identity = normalizeIdentity(state.identity);
      if (identityBadge) identityBadge.textContent = authenticated ? 'SIGNED IN' : 'GUEST';
      if (identityHeading) identityHeading.textContent = authenticated ? (String(IDENTITY_CONFIG.displayName || 'Workspace account')) : 'Guest Workspace';
      if (identityDetail) identityDetail.textContent = authenticated ? 'Account recognized. Project storage remains local to this device.' : 'Your work is associated only with this browser device.';
      if (identityAccess) identityAccess.textContent = authenticated ? 'Account recognized · no sync' : 'No account required';
      if (identityNote) identityNote.textContent = authenticated ? 'You are signed in, but v0.6.1 does not upload or synchronize Workspace Projects. Export/import remains the cross-device portability path.' : 'Sign-in establishes the identity boundary only. Project sync and server-side project storage remain disabled.';
      if (deviceIdEl) deviceIdEl.textContent = state.identity.deviceId;
      if (loginLink) { loginLink.hidden = authenticated; loginLink.href = String(IDENTITY_CONFIG.loginUrl || '#'); }
      if (logoutLink) { logoutLink.hidden = !authenticated; logoutLink.href = String(IDENTITY_CONFIG.logoutUrl || '#'); }
      if (registerLink) {
        registerLink.hidden = authenticated || !IDENTITY_CONFIG.registrationEnabled;
        registerLink.href = String(IDENTITY_CONFIG.registrationUrl || '#');
      }
    }

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
      const portable = JSON.parse(JSON.stringify(project)); portable.persistence = { scope: 'device', deviceId: 'scwd-portable', syncState: 'local-only', accountEligible: true, serverStored: false };
      const payload = { schema: EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.6.1', exportedAt: nowIso(), project: portable };
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
          const supportedExport = payload && (payload.schema === EXPORT_SCHEMA || payload.schema === LEGACY_EXPORT_SCHEMA_V4 || payload.schema === LEGACY_EXPORT_SCHEMA_V31 || payload.schema === LEGACY_EXPORT_SCHEMA_V3 || payload.schema === LEGACY_EXPORT_SCHEMA_V2 || payload.schema === LEGACY_EXPORT_SCHEMA_V1);
          const rawProject = supportedExport ? payload.project : payload;
          if (!rawProject || (rawProject.schema !== PROJECT_SCHEMA && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V31 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V3 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V2 && rawProject.schema !== LEGACY_PROJECT_SCHEMA_V1)) throw new Error('Unsupported project schema');
          const project = normalizeProject(rawProject);
          if (!project) throw new Error('Invalid project');
          if (state.projects.some((item) => item.id === project.id)) { project.id = id('scwp'); project.title = `${project.title} (Imported)`.slice(0, 120); }
          project.archivedAt = null; project.activeObjectId = null; project.updatedAt = nowIso(); addActivity(project, 'imported', 'Project imported on this device');
          state.projects.push(project); state.activeProjectId = project.id; persist('Imported project saved'); render();
        } catch (_) {
          window.alert('Workspace could not import this file. Use a Workspace project JSON export from v0.2.0 through v0.6.1, or a compatible future release.');
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

    root.querySelector('[data-scw-new-object]').addEventListener('click', () => {
      const project = activeProject(); if (!project) return;
      if (project.objects.length >= MAX_OBJECTS) { window.alert(`This v0.6.1 project has reached the ${MAX_OBJECTS}-object local limit.`); return; }
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
      const payload = { schema: OBJECT_EXPORT_SCHEMA, workspaceVersion: root.dataset.version || '0.6.1', exportedAt: nowIso(), projectId: project.id, object: JSON.parse(JSON.stringify(object)) };
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
      project.objects = project.objects.filter((item) => item.id !== object.id); cleanResearchReferences(project, object.id); cleanAnalysisReferences(project, object.id); cleanDecisionReferences(project, object.id); project.activeObjectId = null; project.updatedAt = nowIso();
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
