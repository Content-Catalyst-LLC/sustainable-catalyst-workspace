<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__ . '/');
define('SC_WORKSPACE_VERSION','1.3.0');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-library-continuity.php';
$c=SC_Workspace_Library_Continuity::contract();
if (($c['workspaceVersion']??'')!=='1.3.0') exit(1);
if (($c['canonicalLibraryRoute']??'')!=='/knowledge-libraries/') exit(2);
if (($c['secondAccountRequired']??true)!==false) exit(3);
if (($c['automaticBackgroundSync']??true)!==false) exit(4);
if (count($c['recordFamilies']??[])!==5) exit(5);
echo "PASS - v1.3.0 Library continuity PHP runtime\n";
