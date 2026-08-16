<?php
if (!defined('ABSPATH')) { exit; }

/** v2.0.2 Workspace Home work-mode navigation-card contract. */
final class SC_Workspace_Work_Mode_Cards {
    const SCHEMA = 'sc-workspace-work-mode-cards/2.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'release' => 'Work Mode Cards, Cockpit Hierarchy & Navigation-State Repair',
            'releaseStage' => 'work-mode-cards-repair',
            'previousRelease' => '2.0.1',
            'rollbackRelease' => '2.0.1',
            'cardClass' => 'scw-work-mode-card',
            'modes' => array('objects','analysis','decision','briefing'),
            'desktopColumns' => 2,
            'mobileColumns' => 1,
            'equalHeightCards' => true,
            'directionalAffordance' => 'Open →',
            'disabledWithoutActiveProject' => true,
            'explicitActiveState' => true,
            'ariaPressedState' => true,
            'ariaCurrentState' => true,
            'focusVisible' => true,
            'forcedColorsSupported' => true,
            'genericButtonTreatment' => false,
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
