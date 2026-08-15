<?php
if (!defined('ABSPATH')) { exit; }
final class SC_Workspace_Universal_Search {
    const CONTRACT_SCHEMA = 'sc-workspace-universal-search-contract/1.0';
    const SEARCH_SCHEMA = 'sc-workspace-universal-search/1.0';
    public static function contract() {
        return array(
            'schema' => self::CONTRACT_SCHEMA,
            'workspace_version' => SC_WORKSPACE_VERSION,
            'search_schema' => self::SEARCH_SCHEMA,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'corpus' => array('project','object','notebook','notebook-block','research-question','research-claim','analysis-question','decision','briefing-draft','citation-reference','research-task'),
            'derived_from_local_records' => true,
            'browser_local_index' => true,
            'cross_project' => true,
            'canonical_origin_navigation' => true,
            'ranking' => 'deterministic-explainable-field-match-plus-recorded-provenance',
            'ranking_reasons_visible' => true,
            'saved_searches' => 'browser-local-preferences',
            'citation_library_included' => true,
            'research_tasks_included' => true,
            'server_index' => false,
            'semantic_embeddings' => false,
            'automatic_ai' => false,
            'automatic_semantic_inference' => false,
            'automatic_canonical_mutation' => false,
            'query_telemetry' => false,
            'behavioral_telemetry' => false,
            'schema_migration_required' => false,
        );
    }
}
