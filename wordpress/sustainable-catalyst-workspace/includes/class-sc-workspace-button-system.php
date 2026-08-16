<?php
if (!defined('ABSPATH')) { exit; }

/**
 * v2.0.1 visual-control contract.
 *
 * This is intentionally descriptive. It does not mutate projects or infer
 * interaction state; it documents the UI control system shipped in the
 * cumulative v2.0.1 stylesheet.
 */
final class SC_Workspace_Button_System {
    const SCHEMA = 'sc-workspace-button-system/2.0';

    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'release' => 'Button System, Control Alignment & Interaction-State Repair',
            'releaseStage' => 'button-system-repair',
            'previousRelease' => '2.0.0',
            'rollbackRelease' => '2.0.0',
            'canonicalButtonClass' => 'scw-button',
            'primaryButtonClass' => 'scw-button-primary',
            'desktopMinimumControlHeightPx' => 40,
            'touchMinimumControlHeightPx' => 44,
            'secondaryTreatment' => 'white-black-border',
            'primaryTreatment' => 'red-white-text',
            'disabledTreatment' => 'neutral-non-cta',
            'focusVisible' => true,
            'forcedColorsSupported' => true,
            'connectedProductActionsUseIntentionalGrid' => true,
            'connectedKnowledgeOddFinalActionSpansRow' => true,
            'connectedIntelligenceExportSpansRow' => true,
            'statusOutputsAreInformationSurfaces' => true,
            'drawerStateUsesCompactUtilityTreatment' => true,
            'canonicalContentMutation' => false,
            'javascriptBehaviorChange' => false,
            'schemaMigrationRequired' => false,
            'automaticAi' => false,
            'behavioralTelemetry' => false,
            'queryTelemetry' => false,
            'storageSchemaVersion' => 35,
            'projectSchema' => 'sc-workspace-project/20.0',
            'exportSchema' => 'sc-workspace-project-export/20.0',
            'targetSurfaces' => array(
                'home', 'projects', 'research', 'review', 'exchange',
                'connected-knowledge', 'connected-intelligence',
                'lab-handoff', 'workbench-decision-handoff',
                'review-rooms', 'research-operations', 'footer-actions'
            ),
        );
    }
}
