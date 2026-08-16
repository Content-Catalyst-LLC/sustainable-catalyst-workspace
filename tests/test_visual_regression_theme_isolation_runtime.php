<?php
define('ABSPATH', __DIR__);
define('SC_WORKSPACE_VERSION','2.0.4');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-visual-regression.php';
$c=SC_Workspace_Visual_Regression::contract();
if (($c['workspaceVersion'] ?? '') !== '2.0.4') { fwrite(STDERR,"version\n"); exit(1); }
if (($c['previousRelease'] ?? '') !== '2.0.3') { fwrite(STDERR,"previous\n"); exit(1); }
if (($c['viewportMatrix'] ?? []) !== array(1440,1024,768,390)) { fwrite(STDERR,"viewport\n"); exit(1); }
if (empty($c['hostileThemeFixture']) || empty($c['renderedComputedStyleChecksRequired'])) { fwrite(STDERR,"render\n"); exit(1); }
echo "PASS - v2.0.4 visual regression PHP runtime\n";
