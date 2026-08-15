<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','1.5.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-lab-integration.php';
$c=SC_Workspace_Lab_Integration::contract();
if ($c['workspaceVersion']!=='1.5.0'||$c['canonicalLabRoute']!=='/lab/'||count($c['supportedWorkflows'])!==8||!$c['explicitContextSelection']||!$c['traceabilityEdgesFromSelectedContext']||$c['automaticContextUpload']||$c['automaticReturnCommit']||$c['automaticAI']||$c['schemaMigrationRequired']) { fwrite(STDERR,"FAIL\n"); exit(1); }
echo "PASS - v1.5.0 Lab integration PHP runtime\n";
