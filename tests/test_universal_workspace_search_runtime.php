<?php
define('ABSPATH', __DIR__ . '/');
define('SC_WORKSPACE_VERSION','1.2.0');
$root=dirname(__DIR__);
require_once $root.'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-universal-search.php';
$c=SC_Workspace_Universal_Search::contract();
$expected=array('project','object','notebook','notebook-block','research-question','research-claim','analysis-question','decision','briefing-draft','citation-reference','research-task');
if($c['workspace_version']!=='1.2.0'||$c['search_schema']!=='sc-workspace-universal-search/1.0'||$c['corpus']!==$expected||empty($c['derived_from_local_records'])||empty($c['browser_local_index'])||!empty($c['server_index'])||!empty($c['semantic_embeddings'])||!empty($c['automatic_ai'])||!empty($c['query_telemetry'])||!empty($c['automatic_canonical_mutation'])){fwrite(STDERR,"FAIL - universal Workspace search PHP contract\n");exit(1);}echo "PASS - universal Workspace search PHP runtime\n";
