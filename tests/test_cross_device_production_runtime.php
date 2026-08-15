<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','1.7.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-cross-device-production.php';
$c=SC_Workspace_Cross_Device_Production::contract();
if ($c['workspaceVersion']!=='1.7.0'||$c['schema']!=='sc-workspace-cross-device-production/1.0'||count($c['planActions'])!==8||!$c['guestWorkspaceFirstClass']||!$c['deterministicContinuityPlan']||!$c['conflictPreservesBothSides']||$c['backgroundSync']||$c['automaticUpload']||$c['deviceFingerprinting']||$c['schemaMigrationRequired']) { fwrite(STDERR,"FAIL\n"); exit(1); }
echo "PASS - v1.7.0 cross-device production PHP runtime\n";
