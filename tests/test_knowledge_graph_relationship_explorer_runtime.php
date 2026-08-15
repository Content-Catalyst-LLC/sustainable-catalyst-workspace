<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','1.4.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-knowledge-graph-explorer.php';
$c=SC_Workspace_Knowledge_Graph_Explorer::contract();
if ($c['workspaceVersion']!=='1.4.0'||$c['maxPathDepth']!==5||!$c['explicitPathTracing']||!$c['portableGraphSnapshotExport']||$c['serverGraphDatabase']||$c['automaticRelationshipInference']) { fwrite(STDERR,"FAIL
"); exit(1); }
echo "PASS - v1.4.0 Knowledge Graph PHP runtime
";
