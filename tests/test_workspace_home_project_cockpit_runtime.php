<?php
$root=dirname(__DIR__);$main=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php');$class=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-home.php');$workspace=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php');
if(strpos($main,'Version: 1.4.0')===false||strpos($class,'sc-workspace-home-project-cockpit-contract/1.0')===false||strpos($workspace,'/workspace-home-contract')===false||strpos($workspace,'data-scw-project-cockpit')===false){fwrite(STDERR,"FAIL - v1.1.0 home contract/runtime markers missing
");exit(1);}echo "PASS - workspace home project cockpit PHP runtime
";
