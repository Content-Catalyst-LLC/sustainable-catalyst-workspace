<?php
if (!defined('ABSPATH')) { exit; }

/** v2.0.4 visual regression, theme isolation, and cross-viewport hardening contract. */
final class SC_Workspace_Visual_Regression {
    const SCHEMA = 'sc-workspace-visual-regression/2.0';
    public static function contract() {
        return array(
            'schema' => self::SCHEMA,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
            'release' => 'Visual Regression, Theme Isolation & Cross-Viewport Hardening',
            'releaseStage' => 'visual-regression-theme-isolation',
            'previousRelease' => '2.0.3',
            'rollbackRelease' => '2.0.3',
            'viewportMatrix' => array(1440, 1024, 768, 390),
            'hostileThemeFixture' => true,
            'rootScopeRequired' => true,
            'noHorizontalOverflowRequired' => true,
            'buttonThemeIsolationRequired' => true,
            'workModeCardIsolationRequired' => true,
            'connectedSurfaceGridRequired' => true,
            'touchMinimumControlHeight' => 44,
            'desktopMinimumControlHeight' => 40,
            'renderedComputedStyleChecksRequired' => true,
            'visualSnapshotReceiptRequired' => true,
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
