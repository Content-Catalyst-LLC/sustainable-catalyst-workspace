<?php
$root=dirname(__DIR__);$main=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/sustainable-catalyst-workspace.php');$class=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace.php');$cards=file_get_contents($root.'/wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-work-mode-cards.php');
if(strpos($main,'Version: 2.0.2')===false||strpos($cards,'sc-workspace-work-mode-cards/2.0')===false||substr_count($class,'class="scw-work-mode-card"')!==4||strpos($class,"/work-mode-cards-contract")===false){fwrite(STDERR,"FAIL - v2.0.2 work-mode card runtime contract
");exit(1);}echo "PASS - v2.0.2 work-mode card runtime contract
";
