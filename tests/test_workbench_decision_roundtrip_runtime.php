<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','1.6.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-workbench-decision-roundtrip.php';
$c=SC_Workspace_Workbench_Decision_Roundtrip::contract();
if ($c['workspaceVersion']!=='1.6.0'||$c['canonicalWorkbenchRoute']!=='/lab/workbench/'||$c['canonicalDecisionStudioRoute']!=='/lab/decision-studio/'||count($c['workbenchWorkflows'])!==6||count($c['decisionStudioWorkflows'])!==6||!$c['destinationMatchRequired']||!$c['traceabilityEdgesFromSelectedContext']||$c['automaticContextUpload']||$c['automaticReturnCommit']||$c['automaticAI']||$c['schemaMigrationRequired']) { fwrite(STDERR,"FAIL\n"); exit(1); }
echo "PASS - v1.6.0 Workbench/Decision Studio round-trip PHP runtime\n";
