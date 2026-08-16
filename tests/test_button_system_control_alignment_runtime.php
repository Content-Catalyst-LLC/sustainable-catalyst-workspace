<?php
if (!defined('ABSPATH')) define('ABSPATH', __DIR__);
if (!defined('SC_WORKSPACE_VERSION')) define('SC_WORKSPACE_VERSION','2.0.2');
require_once __DIR__ . '/../wordpress/sustainable-catalyst-workspace/includes/class-sc-workspace-button-system.php';
$c=SC_Workspace_Button_System::contract();
if ($c['workspaceVersion']!=='2.0.2'||$c['releaseStage']!=='button-system-repair'||$c['previousRelease']!=='2.0.0'||$c['desktopMinimumControlHeightPx']!==40||$c['touchMinimumControlHeightPx']!==44||!$c['focusVisible']||!$c['forcedColorsSupported']||!$c['connectedProductActionsUseIntentionalGrid']||!$c['statusOutputsAreInformationSurfaces']||$c['javascriptBehaviorChange']||$c['schemaMigrationRequired']||$c['canonicalContentMutation']) { fwrite(STDERR,'FAIL'.PHP_EOL); exit(1); }
echo 'PASS - v2.0.1 Button System PHP runtime'.PHP_EOL;
