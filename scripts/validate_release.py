from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
MAN=json.loads((ROOT/'release-manifest-v0.68.0.json').read_text())
REG=json.loads((ROOT/'registry/workspace-product-record-v0.68.0.json').read_text())
MAINP=ROOT/'wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php'
MAIN=MAINP.read_text(); RAW=MAINP.read_bytes(); HEAD=RAW[:8192].decode('utf-8',errors='replace')
PHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php').read_text()
REGPHP=(ROOT/'wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-registry.php').read_text()
APP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/workspace-v0.68.0.js').read_text()
HELP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-long-session-performance-v1.js').read_text()
UI=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-long-session-performance-ui-v1.js').read_text()
BETA=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-public-beta-ii-ui-v1.js').read_text()
COMP=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/js/sc-workspace-import-export-compatibility-v1.js').read_text()
CSS=(ROOT/'wordpress/sustainable-catalyst-workspace/assets/css/workspace-v0.68.0.css').read_text()
def check(ok,label):
 if not ok: raise SystemExit('FAIL - '+label)
check('Version: 0.68.0' in MAIN and "SC_WORKSPACE_VERSION', '0.68.0" in MAIN,'plugin version')
check((MAN['version'],MAN['previous_version'],MAN['release_name'])==('0.68.0','0.67.0','Performance II: Long Sessions & Very Large Workspaces'),'release lineage')
check(MAN['storage_schema_version']==35 and MAN['project_schema']=='sc-workspace-project/20.0' and MAN['export_schema']=='sc-workspace-project-export/20.0' and MAN['schema_migration_required'] is False,'canonical schemas stable')
mig=MAN['migration']
check(mig.get('performance_ii_only_release') is True and mig.get('performance_ii_project_schema_change') is False and mig.get('performance_ii_storage_schema_change') is False and mig.get('performance_ii_canonical_data_rewrite') is False,'performance-only non-destructive migration boundary')
for label,expected in [('Plugin Name','Sustainable Catalyst Workspace'),('Version','0.68.0'),('Author','Content Catalyst LLC'),('Requires at least','6.4'),('Requires PHP','8.0')]:
 m=re.search(r'^[ \t\/*#@]*'+re.escape(label)+r':(.*)$',HEAD,re.I|re.M); check(bool(m) and m.group(1).strip()==expected,'8KB header '+label)
check(RAW.find(b'Version:')<512 and RAW.find(b'Requires PHP:')<512 and RAW.find(b'Description:')<1024,'compact plugin header')
check("'sc-workspace-v0680'" in PHP and 'workspace-v0.68.0.js' in PHP and 'workspace-v0.68.0.css' in PHP,'v0.68 cumulative assets')
check("wp_localize_script('sc-workspace-v0680'" in PHP,'current asset localization handle')
check('sc-workspace-long-session-performance-v1.js' in PHP and 'sc-workspace-long-session-performance-ui-v1.js' in PHP and "'/long-session-performance-contract'" in PHP,'performance helper UI and REST contract')
check('/wp-json/sc-workspace/v1/long-session-performance-contract' in MAN['rest_routes'],'performance REST manifest')
perf=MAN['long_session_performance']
check(perf['bounded_in_memory_samples']==120 and perf['long_task_threshold_ms']==50 and perf['render_attention_ms']==32 and perf['render_critical_ms']==100,'bounded session/render budgets')
check(perf['index_attention_ms']==250 and perf['index_critical_ms']==1000 and perf['route_transition_attention']==300 and perf['session_attention_minutes']==240,'index/route/session budgets')
check(perf['revision_memoization'] is True and perf['cooperative_chunk_yield'] is True and perf['bounded_render_windows'] is True,'large-work performance controls')
for key in ['persistent_profiling','automatic_telemetry','automatic_submission','project_content_in_report','query_text_in_report','source_urls_in_report','device_identifier_in_report','automatic_deletion','automatic_archival','automatic_compaction','automatic_migration','canonical_mutation']:
 check(perf[key] is False,'performance governance '+key)
check("maxSamples:120" in HELP and 'createRevisionMemo' in HELP and 'boundedWindow' in HELP and 'chunkedMap' in HELP and 'PerformanceObserver' in HELP,'performance helper primitives')
check('projectContentIncluded:false' in HELP and 'automaticTelemetry:false' in HELP and 'persisted:false' in HELP,'performance report privacy boundary')
check('SCWorkspacePerformanceSession' in APP and 'longSessionMonitor?.markRoute' in APP and 'longSessionMonitor?.markRender' in APP and 'longSessionMonitor?.markIndex' in APP,'application performance instrumentation')
check('derivedIntegratedEntries(ik)' in APP and APP.count('ik.derive(state)')==0,'integrated-knowledge repeated derive consolidation')
check("if (!event.persisted) longSessionMonitor.dispose()" in APP,'bfcache-safe lifecycle cleanup')
check('data-scw-performance-session' in PHP and 'data-scw-perf-session-export' in PHP and 'data-scw-perf-session-reset' in PHP,'performance review surface')
check('timings/counters only, not project content' in UI and "root.dataset.version||'0.68.0'" in UI,'performance UI privacy/version')
check('/* v0.68.0 — Performance II: Long Sessions & Very Large Workspaces */' in CSS,'performance responsive CSS')
check("expectedVersion:'0.68.0'" in BETA and "root.dataset.version==='0.68.0'" in BETA,'beta current version gate')
check("workspaceVersion:'0.68.0'" in COMP,'compatibility report current version')
check("BACKUP_KEY = 'sc_workspace_registry_backup_v0680'" in REGPHP and "PENDING_KEY = 'sc_workspace_registry_pending_v0680'" in REGPHP and 'LEGACY_PENDING_KEY_V0670' in REGPHP,'registry lineage')
check((REG['public_version'],REG['previous_version'],REG['release_name'])==('0.68.0','0.67.0','Performance II: Long Sessions & Very Large Workspaces'),'registry record')
check((ROOT/'history/release-manifest-v0.67.0.json').exists() and (ROOT/'history/workspace-product-record-v0.67.0.json').exists(),'v0.67.0 history retained')
for f in ['schemas/sc-workspace-long-session-performance-v1.schema.json','schemas/sc-workspace-performance-session-v1.schema.json','schemas/sc-workspace-performance-session-report-v1.schema.json','docs/PERFORMANCE_LONG_SESSIONS_V0680.md']:
 check((ROOT/f).exists(),f)
print('PASS - v0.68.0 release validator')
