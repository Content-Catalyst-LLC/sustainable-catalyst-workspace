<?php
if (!defined('ABSPATH')) { exit; }

/** v2.0.3 live Workspace root-scope and cockpit CSS recovery contract. */
final class SC_Workspace_Root_Scope {
    const SCHEMA = 'sc-workspace-root-scope/2.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'release' => 'Workspace Root Scope & Cockpit CSS Recovery',
            'releaseStage' => 'root-scope-cockpit-recovery',
            'previousRelease' => '2.0.2',
            'rollbackRelease' => '2.0.2',
            'rootElementClass' => 'scw-shell scw-root',
            'requiredRootClasses' => array('scw-shell','scw-root'),
            'scopedSelectorModel' => 'root-descendant',
            'cockpitSelector' => '.scw-root .scw-project-cockpit',
            'workModeGridSelector' => '.scw-root .scw-project-cockpit-lanes',
            'workModeCardSelector' => '.scw-root .scw-project-cockpit-lanes .scw-work-mode-card',
            'selectorMatchVerified' => true,
            'computedLayoutVerified' => true,
            'cockpitGridRecovered' => true,
            'workModeCardGridRecovered' => true,
            'globalThemeButtonFallbackPrevented' => true,
            'routingSemanticsChanged' => false,
            'canonicalContentMutation' => false,
            'schemaMigrationRequired' => false,
            'automaticAi' => false,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchema' => 'sc-workspace-project-export/20.0',
        );
    }
}
