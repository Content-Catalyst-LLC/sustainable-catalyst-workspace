<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Home {
    const CONTRACT_SCHEMA = 'sc-workspace-home-project-cockpit-contract/1.0';
    public static function contract() { return array(
        'schema'=>self::CONTRACT_SCHEMA,
        'workspace_version'=>SC_WORKSPACE_VERSION,
        'release'=>'Workspace Home, Project Cockpit & Navigation Refinement',
        'surface'=>'home',
        'primary_area_label'=>'Home',
        'project_cockpit'=>true,
        'active_project_summary'=>true,
        'recent_project_resume'=>true,
        'deterministic_next_actions'=>true,
        'research_shortcuts'=>true,
        'project_mode_shortcuts'=>true,
        'review_navigation_progressive_disclosure'=>true,
        'command_palette_preserved'=>true,
        'specialized_surfaces_preserved'=>true,
        'canonical_schema_freeze'=>true,
        'storage_schema_version'=>35,
        'project_schema'=>'sc-workspace-project/20.0',
        'project_export_schema'=>'sc-workspace-project-export/20.0',
        'schema_migration_required'=>false,
        'automatic_project_mutation'=>false,
        'automatic_ai'=>false,
        'behavioral_telemetry'=>false,
        'hidden_productivity_score'=>false,
    ); }
}
