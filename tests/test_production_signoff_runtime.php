<?php
define('ABSPATH', __DIR__ . '/');
define('SC_WORKSPACE_VERSION', '0.83.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-production-signoff.php';
$c=SC_Workspace_Production_Signoff::contract();
if ($c['workspace_version'] !== '0.83.0') { exit(1); }
if (count($c['required_checks']) !== 14) { exit(2); }
if ($c['automatic_signoff'] !== false || $c['project_data_inspected'] !== false) { exit(3); }
echo "PASS - v0.83.0 production sign-off PHP runtime\n";
