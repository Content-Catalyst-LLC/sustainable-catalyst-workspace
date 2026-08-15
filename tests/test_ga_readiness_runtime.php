<?php
define('ABSPATH', __DIR__ . '/');
define('SC_WORKSPACE_VERSION', '1.0.1');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-ga-readiness.php';
$c=SC_Workspace_GA_Readiness::contract();
if ($c['workspace_version'] !== '1.0.1') { exit(1); }
if ($c['previous_release'] !== '0.83.0' || $c['rollback_release'] !== '0.83.0') { exit(2); }
if ($c['production_signoff_release'] !== '0.83.0') { exit(3); }
if (count($c['required_checks']) !== 9) { exit(4); }
if ($c['automatic_promotion_to_1_0'] !== false || $c['project_data_inspected'] !== false) { exit(5); }
echo "PASS - v0.84.0 GA readiness PHP runtime\n";
