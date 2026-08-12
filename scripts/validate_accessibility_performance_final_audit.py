from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
MAN=json.loads((R/'release-manifest-v0.78.0.json').read_text())
PHP=(R/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text(); CORE=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-v1.js').read_text(); UI=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-accessibility-performance-final-audit-ui-v1.js').read_text(); CSS=(R/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.78.0.css').read_text(); APP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.78.0.js').read_text(); EXP=(R/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-experience-v1.js').read_text()
def check(cond,msg):
 if not cond: raise SystemExit('FAIL - v0.78 final audit gate: '+msg)
a=MAN['accessibility_performance_final_audit']
check(MAN['version']=='0.78.0' and MAN['previous_version']=='0.77.0','lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['schema_migration_required'] is False,'schema stability')
check("'/accessibility-performance-final-audit-contract'" in PHP and "'methods' => 'GET'" in PHP,'public GET contract')
check('data-scw-final-audit' in PHP and 'data-scw-workspace-view="final-audit"' in PHP,'final audit route/surface')
check('sc-workspace-accessibility-performance-final-audit-v1' in PHP and 'sc-workspace-accessibility-performance-final-audit-ui-v1' in PHP,'final audit assets')
check("array('sc-workspace-accessibility-v1', 'sc-workspace-long-session-performance-v1')" in PHP,'existing engines dependency')
for k in ['critical_automated_release_gate','manual_field_audit_required','existing_accessibility_engine_reused','existing_long_session_monitor_reused','privacy_minimized_report']: check(a[k] is True,k)
for k in ['automated_accessibility_certification','automated_performance_certification','hidden_score','automatic_repair','automatic_optimization','automatic_deletion','automatic_upload','telemetry','canonical_mutation','schema_migration_required']: check(a[k] is False,k)
for k,v in [('dom_attention',7000),('dom_critical',10000),('render_p95_attention_ms',32),('render_p95_critical_ms',100),('index_p95_attention_ms',250),('index_p95_critical_ms',1000),('long_task_critical_count',5)]: check(a[k]==v,k)
for tok in ['duplicateIds','unnamedInteractive','renderP95CriticalMs:100','indexP95CriticalMs:1000','longTaskCriticalCount:5','projectContentIncluded:false','deviceIdentifierIncluded:false','automatedCertification:false','automaticOptimization:false']: check(tok in CORE,'core '+tok)
for tok in ['SCWorkspaceAccessibility','SCWorkspacePerformanceSession','Export final field-QA checklist']: check(tok in (UI+PHP),'integration '+tok)
for tok in ['VoiceOver + Safari','400% / 320 CSS px reflow','Representative four-hour session','Production WordPress smoke test']: check(tok in CORE,'manual checklist '+tok)
check("'final-audit'" in APP and "id:'final-audit'" in EXP,'route recognition')
check('/* v0.78.0 — Accessibility & Performance Final Audit */' in CSS,'css layer')
for f in ['schemas/sc-workspace-accessibility-performance-final-audit-v1.schema.json','schemas/sc-workspace-accessibility-performance-final-audit-report-v1.schema.json','schemas/sc-workspace-accessibility-performance-final-checklist-v1.schema.json','docs/ACCESSIBILITY_PERFORMANCE_FINAL_AUDIT_V0780.md','RELEASE_NOTES_0.78.0.md','history/release-manifest-v0.77.0.json','history/workspace-product-record-v0.77.0.json']: check((R/f).exists(),f)
print('PASS - v0.78.0 Accessibility & Performance Final Audit source gate')
