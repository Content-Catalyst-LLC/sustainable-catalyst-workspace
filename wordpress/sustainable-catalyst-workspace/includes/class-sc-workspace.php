<?php
if (!defined('ABSPATH')) {
    exit;
}

final class SC_Workspace {
    private static $instance = null;

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('init', array($this, 'register_shortcodes'));
        add_action('rest_api_init', array($this, 'register_rest_routes'));
        add_action('admin_init', array($this, 'retry_registry_registration'));
        add_action('admin_notices', array($this, 'registry_notice'));
    }

    public function register_shortcodes() {
        add_shortcode('sc_workspace', array($this, 'render_workspace'));
        add_shortcode('sc_workspace_entry', array($this, 'render_entry'));
        add_shortcode('sc_workspace_platform', array($this, 'render_platform'));
    }

    public function retry_registry_registration() {
        if (
            get_option(SC_Workspace_Registry::PENDING_KEY, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0220, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0210, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0200, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0190, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0180, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0170, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0160, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0150, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0140, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0130, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0120, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0110, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0100, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0901, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0831, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V082, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V081, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V080, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V070, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V061, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V060, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V041, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V040, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V030, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V020, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V010, '') === '1'
        ) {
            SC_Workspace_Registry::register_product();
        }
    }

    public function registry_notice() {
        if (!current_user_can('manage_options')) {
            return;
        }
        if (get_option(SC_Workspace_Registry::PENDING_KEY, '') !== '1') {
            return;
        }
        echo '<div class="notice notice-warning"><p><strong>Sustainable Catalyst Workspace:</strong> the canonical Product Registry was not available during activation. Workspace is active, but its v0.23.0 Commercial Release record is pending until Product Support and Feedback is active.</p></div>';
    }

    public function register_rest_routes() {
        register_rest_route('sc-workspace/v1', '/health', array(
            'methods' => 'GET',
            'callback' => array($this, 'health'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/project-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'project_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/object-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'object_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/research-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'research_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/identity-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'identity_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/analysis-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'analysis_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/decision-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'decision_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/canvas-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'canvas_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/handoff-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'handoff_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/adapter-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'adapter_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/traceability-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'traceability_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/briefing-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'briefing_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/guided-workflows-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'guided_workflows_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/personal-knowledge-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'personal_knowledge_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/knowledge-graph-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'knowledge_graph_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/ai-assistance-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'ai_assistance_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/interoperability-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'interoperability_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/share-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'share_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/activity-intelligence-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'activity_intelligence_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/collaboration-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'collaboration_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/institutional-handoff-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'institutional_handoff_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/account-persistence-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'account_persistence_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/sync-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'sync_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/version-history-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'version_history_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/cloud-projects', array(
            array(
                'methods' => 'GET',
                'callback' => array($this, 'cloud_projects_list'),
                'permission_callback' => array($this, 'cloud_permission'),
            ),
            array(
                'methods' => 'POST',
                'callback' => array($this, 'cloud_project_store'),
                'permission_callback' => array($this, 'cloud_permission'),
            ),
        ));
        register_rest_route('sc-workspace/v1', '/cloud-projects/(?P<project_id>[A-Za-z0-9._-]{1,160})', array(
            array(
                'methods' => 'GET',
                'callback' => array($this, 'cloud_project_get'),
                'permission_callback' => array($this, 'cloud_permission'),
            ),
            array(
                'methods' => 'DELETE',
                'callback' => array($this, 'cloud_project_delete'),
                'permission_callback' => array($this, 'cloud_permission'),
            ),
        ));
        register_rest_route('sc-workspace/v1', '/readiness-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'readiness_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/platform-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'platform_contract'),
            'permission_callback' => '__return_true',
        ));
    }

    public function health() {
        return rest_ensure_response(array(
            'ok' => true,
            'product' => 'Sustainable Catalyst Workspace',
            'canonical_id' => 'sustainable-catalyst-workspace',
            'version' => SC_WORKSPACE_VERSION,
            'access' => 'free-public',
            'account_required' => false,
            'persistence' => 'browser-local-projects-v23-plus-version-history-account-backup-and-explicit-conflict-safe-sync',
            'project_schema' => 'sc-workspace-project/11.0',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'identity_schema' => 'sc-workspace-identity/1.0',
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'decision_schema' => 'sc-workspace-decision/1.0',
            'canvas_schema' => 'sc-workspace-canvas/1.0',
            'handoff_schema' => 'sc-workspace-handoff/2.0',
            'handoff_ledger_schema' => 'sc-workspace-handoff-ledger/1.0',
            'handoff_return_schema' => 'sc-workspace-handoff-return/1.0',
            'return_adapter_schema' => 'sc-workspace-return-adapter/1.0',
            'traceability_schema' => 'sc-workspace-traceability/1.0',
            'briefing_schema' => 'sc-workspace-briefing/1.0',
            'guided_workflows_schema' => 'sc-workspace-guided-workflows/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'knowledge_graph_schema' => 'sc-workspace-knowledge-graph/1.0',
            'activity_intelligence_schema' => 'sc-workspace-activity-intelligence/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'institutional_handoff_schema' => 'sc-workspace-institutional-handoff/1.0',
            'institutional_handoff_package_schema' => 'sc-workspace-institutional-handoff-package/1.0',
            'institutional_handoff_receipt_schema' => 'sc-workspace-institutional-handoff-receipt/1.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'publication_export_schema' => 'sc-workspace-publication-export/1.0',
            'reproducibility_export_schema' => 'sc-workspace-reproducibility-export/1.0',
            'return_adapter_transport' => array('session-storage', 'same-origin-postmessage', 'portable-json'),
            'authentication_provider' => 'wordpress',
            'anonymous_workspace_supported' => true,
            'storage_schema_version' => 23,
            'server_project_storage' => 'manual-backup-plus-explicit-sync-head',
            'cloud_sync' => 'explicit-project-enrollment',
            'cross_device_sync_schema' => 'sc-workspace-cross-device-sync/1.0',
            'version_history_schema' => 'sc-workspace-version-history/1.0',
            'restore_point_schema' => 'sc-workspace-restore-point/1.0',
            'restore_strategy' => 'new-local-copy',
            'background_sync' => false,
            'release_readiness' => 'stability-accessibility-validated',
            'accessibility_target' => 'WCAG 2.2 AA',
            'diagnostics' => 'local-privacy-minimized',
            'last_known_good_recovery' => true,
            'collaboration' => 'asynchronous-portable-review',
            'live_collaboration' => false,
            'server_collaboration' => false,
            'institutional_handoff' => 'explicit-portable-promotion',
            'institutional_handoff_automatic_upload' => false,
            'institutional_handoff_source_mutation' => false,
            'registry_family' => 'commercial',
            'lifecycle' => 'experimental',
        ));
    }

    public function project_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-project-contract/11.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/11.0',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'decision_schema' => 'sc-workspace-decision/1.0',
            'canvas_schema' => 'sc-workspace-canvas/1.0',
            'export_schema' => 'sc-workspace-project-export/11.0',
            'storage_schema_version' => 23,
            'persistence' => 'device-local',
            'server_storage' => false,
            'project_persistence_metadata' => true,
            'device_identity' => 'anonymous-pseudonymous-local-id',
            'account_sign_in_changes_storage' => false,
            'max_objects_per_project' => 250,
            'handoff_schema' => 'sc-workspace-handoff/2.0',
            'handoff_query_fields' => array('sc_workspace_project', 'sc_workspace_object', 'sc_workspace_canvas', 'sc_workspace_handoff', 'sc_workspace_intent', 'sc_workspace_origin', 'sc_workspace_return'),
            'handoff_ledger_schema' => 'sc-workspace-handoff-ledger/1.0',
            'handoff_return_schema' => 'sc-workspace-handoff-return/1.0',
            'handoff_content_in_url' => false,
            'structured_return_supported' => true,
            'return_adapter_schema' => 'sc-workspace-return-adapter/1.0',
            'automatic_return_requires_local_handoff_match' => true,
            'traceability_schema' => 'sc-workspace-traceability/1.0',
            'content_fingerprint_algorithm' => 'SHA-256',
            'reproducibility_export_schema' => 'sc-workspace-reproducibility-export/1.0',
            'guided_workflows_schema' => 'sc-workspace-guided-workflows/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'institutional_handoff_schema' => 'sc-workspace-institutional-handoff/1.0',
            'institutional_handoff_package_schema' => 'sc-workspace-institutional-handoff-package/1.0',
        ));
    }

    public function object_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-object-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'object_schema' => 'sc-workspace-object/1.0',
            'object_export_schema' => 'sc-workspace-object-export/1.0',
            'types' => array('source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'export'),
            'statuses' => array('draft', 'working', 'ready'),
            'provenance_source_types' => array('manual', 'web', 'library', 'dataset', 'tool', 'imported'),
            'content_in_handoff_url' => false,
            'stable_object_id_handoff' => true,
        ));
    }

    public function research_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-research-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'research_schema' => 'sc-workspace-research/1.0',
            'question_statuses' => array('open', 'answered', 'deferred'),
            'question_priorities' => array('low', 'normal', 'high'),
            'claim_statuses' => array('exploratory', 'supported', 'contested', 'rejected'),
            'reading_statuses' => array('unread', 'reading', 'read'),
            'max_questions_per_project' => 100,
            'max_claims_per_project' => 100,
            'max_reading_queue_items' => 250,
            'max_evidence_links' => 500,
            'references_workspace_object_ids' => true,
            'research_content_in_handoff_url' => false,
        ));
    }


    public function analysis_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-analysis-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'project_schema' => 'sc-workspace-project/11.0',
            'dataset_object_type' => 'dataset',
            'analysis_object_type' => 'analysis',
            'question_statuses' => array('open', 'resolved', 'deferred'),
            'variable_roles' => array('outcome', 'input', 'control', 'parameter', 'indicator'),
            'assumption_statuses' => array('untested', 'supported', 'challenged'),
            'method_types' => array('descriptive', 'comparative', 'statistical', 'modeling', 'scenario', 'sensitivity', 'other'),
            'finding_statuses' => array('preliminary', 'supported', 'contested'),
            'max_questions_per_project' => 100,
            'max_variables_per_project' => 120,
            'max_assumptions_per_project' => 120,
            'max_methods_per_project' => 100,
            'max_comparisons_per_project' => 100,
            'max_findings_per_project' => 150,
            'references_workspace_object_ids' => true,
            'analysis_content_in_handoff_url' => false,
            'server_compute' => false,
            'local_first' => true,
        ));
    }


    public function decision_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-decision-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'decision_schema' => 'sc-workspace-decision/1.0',
            'project_schema' => 'sc-workspace-project/11.0',
            'decision_object_type' => 'decision',
            'decision_statuses' => array('framing', 'evaluating', 'decided', 'revisit'),
            'option_statuses' => array('candidate', 'shortlisted', 'selected', 'rejected'),
            'confidence_levels' => array('low', 'medium', 'high'),
            'risk_levels' => array('low', 'medium', 'high'),
            'score_range' => array('minimum' => -5, 'maximum' => 5),
            'max_decisions_per_project' => 60,
            'max_options_per_project' => 240,
            'max_criteria_per_project' => 180,
            'max_assessments_per_project' => 1000,
            'max_risks_per_project' => 300,
            'references_workspace_object_ids' => true,
            'decision_content_in_handoff_url' => false,
            'local_first' => true,
        ));
    }

    public function canvas_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-canvas-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'canvas_schema' => 'sc-workspace-canvas/1.0',
            'project_schema' => 'sc-workspace-project/11.0',
            'board_statuses' => array('draft', 'working', 'ready'),
            'node_types' => array('note', 'question', 'claim', 'evidence', 'data', 'analysis', 'decision', 'system', 'stakeholder', 'idea'),
            'relationship_types' => array('supports', 'contradicts', 'depends-on', 'influences', 'contains', 'causes', 'relates-to', 'sequence'),
            'max_boards_per_project' => 30,
            'max_nodes_per_project' => 500,
            'max_edges_per_project' => 1000,
            'max_frames_per_project' => 100,
            'references_workspace_object_ids' => true,
            'synthesis_creates_document_object' => true,
            'canvas_content_in_handoff_url' => false,
            'local_first' => true,
        ));
    }

    public function handoff_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-handoff-contract/2.1',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/11.0',
            'handoff_schema' => 'sc-workspace-handoff/2.0',
            'ledger_schema' => 'sc-workspace-handoff-ledger/1.0',
            'return_schema' => 'sc-workspace-handoff-return/1.0',
            'return_adapter_schema' => 'sc-workspace-return-adapter/1.0',
            'statuses' => array('prepared', 'launched', 'returned', 'closed'),
            'intents' => array('research', 'analysis', 'decision', 'canvas', 'data', 'compute', 'publish', 'general'),
            'destinations' => array('research-librarian', 'knowledge-library', 'site-intelligence', 'workbench', 'analytics-r', 'decision-studio', 'catalyst-canvas', 'catalyst-data', 'lab'),
            'max_handoffs_per_project' => 150,
            'max_object_refs_per_handoff' => 12,
            'max_return_artifacts' => 20,
            'query_fields' => array('sc_workspace_project', 'sc_workspace_object', 'sc_workspace_canvas', 'sc_workspace_handoff', 'sc_workspace_intent', 'sc_workspace_origin', 'sc_workspace_return'),
            'content_in_query_string' => false,
            'same_origin_session_return' => true,
            'same_origin_postmessage_return' => true,
            'automatic_return_requires_local_handoff_match' => true,
            'outbound_session_storage_key' => 'sc_workspace_handoff_v2',
            'return_session_storage_key' => 'sc_workspace_handoff_return_v1',
            'portable_json_return' => true,
            'return_materializes_workspace_objects' => true,
            'producer_helper' => sc_workspace_return_adapter_script_url(),
            'server_broker' => false,
            'local_first' => true,
        ));
    }

    public function adapter_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-return-adapter-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'adapter_schema' => 'sc-workspace-return-adapter/1.0',
            'canonical_return_schema' => 'sc-workspace-handoff-return/1.0',
            'producer_helper' => sc_workspace_return_adapter_script_url(),
            'transports' => array('session-storage', 'same-origin-postmessage', 'portable-json'),
            'outbound_session_storage_key' => 'sc_workspace_handoff_v2',
            'return_session_storage_key' => 'sc_workspace_handoff_return_v1',
            'automatic_return_requires_local_project' => true,
            'automatic_return_requires_local_handoff' => true,
            'automatic_return_requires_destination_match' => true,
            'manual_unmatched_import_supported' => true,
            'content_in_query_string' => false,
            'server_broker' => false,
            'destinations' => array(
                'research-librarian' => array('preferred_types' => array('source','evidence','document')),
                'knowledge-library' => array('preferred_types' => array('source','document')),
                'site-intelligence' => array('preferred_types' => array('dataset','evidence','analysis','export')),
                'workbench' => array('preferred_types' => array('dataset','analysis','export','document')),
                'analytics-r' => array('preferred_types' => array('dataset','analysis','export','document')),
                'decision-studio' => array('preferred_types' => array('decision','document','export')),
                'catalyst-canvas' => array('preferred_types' => array('document','decision','export')),
                'catalyst-data' => array('preferred_types' => array('dataset','analysis','export','document')),
                'lab' => array('preferred_types' => array('dataset','analysis','evidence','export','document')),
            ),
        ));
    }

    public function traceability_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-traceability-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/11.0',
            'traceability_schema' => 'sc-workspace-traceability/1.0',
            'briefing_schema' => 'sc-workspace-briefing/1.0',
            'publication_export_schema' => 'sc-workspace-publication-export/1.0',
            'reproducibility_export_schema' => 'sc-workspace-reproducibility-export/1.0',
            'evidence_assessment_dimensions' => array('relevance', 'source-quality', 'independence', 'recency'),
            'assessment_scale' => array('minimum' => 0, 'maximum' => 4, 'zero_means' => 'unrated'),
            'lineage_relations' => array('derived-from', 'supports', 'contradicts', 'uses', 'produced-by', 'informs', 'supersedes', 'cites'),
            'reproducibility_statuses' => array('draft', 'ready', 'verified', 'stale'),
            'content_fingerprint_algorithm' => 'SHA-256',
            'max_evidence_assessments' => 250,
            'max_lineage_relations' => 1000,
            'max_reproducibility_records' => 100,
            'references_workspace_object_ids' => true,
            'portable_reproduction_packages' => true,
            'server_execution' => false,
            'local_first' => true,
        ));
    }


    public function guided_workflows_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-guided-workflows-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'guided_workflows_schema' => 'sc-workspace-guided-workflows/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'project_schema' => 'sc-workspace-project/11.0',
            'storage_schema_version' => 23,
            'templates' => array('research-investigation', 'evidence-review', 'analytical-assessment', 'decision-case', 'systems-mapping', 'publication-preparation'),
            'run_statuses' => array('active', 'paused', 'complete'),
            'step_statuses' => array('todo', 'in-progress', 'complete', 'skipped'),
            'blank_projects_supported' => true,
            'templates_create_hidden_content' => false,
            'user_controls_step_completion' => true,
            'max_workflows_per_project' => 20,
            'local_first' => true,
        ));
    }

    public function briefing_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-briefing-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/11.0',
            'briefing_schema' => 'sc-workspace-briefing/1.0',
            'publication_export_schema' => 'sc-workspace-publication-export/1.0',
            'draft_formats' => array('briefing', 'memo', 'report', 'article', 'publication-draft'),
            'draft_statuses' => array('draft', 'review', 'ready', 'exported'),
            'max_drafts_per_project' => 30,
            'max_sections_per_draft' => 24,
            'max_object_references_per_draft' => 80,
            'materializes_document_objects' => true,
            'portable_markdown_export' => true,
            'portable_html_export' => true,
            'portable_json_package' => true,
            'automatic_publication' => false,
            'cms_write' => false,
            'references_workspace_object_ids' => true,
            'local_first' => true,
        ));
    }

    public function personal_knowledge_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-personal-knowledge-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'scope' => 'device-local-workspace',
            'index' => array(
                'derived_from_projects' => true,
                'duplicates_object_content' => false,
                'server_index' => false,
                'semantic_embedding_index' => false,
                'search_fields' => array('project-title', 'object-title', 'summary', 'content', 'tags', 'provenance-title', 'provenance-url'),
            ),
            'collections' => array(
                'max_collections' => 30,
                'max_items_per_collection' => 200,
                'stable_refs' => array('projectId', 'objectId'),
                'deleting_collection_deletes_objects' => false,
            ),
            'related_work' => array(
                'automatic_semantic_claims' => false,
                'signals' => array('shared-tags', 'same-source-url', 'same-provenance-title', 'object-type-secondary-signal'),
                'transparent_reasons' => true,
            ),
            'privacy' => array(
                'local_only' => true,
                'cloud_sync' => false,
                'server_project_storage' => false,
                'external_search_index' => false,
            ),
        ));
    }


    public function knowledge_graph_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-knowledge-graph-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'knowledge_graph_schema' => 'sc-workspace-knowledge-graph/1.0',
            'activity_intelligence_schema' => 'sc-workspace-activity-intelligence/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'node_types' => array('project','provenance','source','evidence','dataset','analysis','decision','document','export'),
            'relationship_types' => array('contains','sourced-from','same-source','evidence-from','uses','informs','supports','contradicts','derived-from','produced-by','supersedes','cites'),
            'derived_from_canonical_objects' => true,
            'duplicates_object_content' => false,
            'focus_neighborhood_depths' => array(1,2),
            'transparent_relationship_labels' => true,
            'semantic_embeddings' => false,
            'server_graph_database' => false,
            'server_search_index' => false,
            'automatic_relationship_inference' => false,
            'local_first' => true,
        ));
    }

    public function ai_assistance_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-ai-assistance-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/11.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'ai_request_export_schema' => 'sc-workspace-ai-request-export/1.0',
            'ai_response_export_schema' => 'sc-workspace-ai-response-export/1.0',
            'task_types' => array('grounded-summary','evidence-gaps','compare-alternatives','briefing-draft','method-explanation','general-question'),
            'statuses' => array('prepared','sent','response-received','accepted','rejected'),
            'max_sessions_per_project' => 40,
            'max_grounding_objects_per_session' => 24,
            'request_session_storage_key' => 'sc_workspace_ai_request_v1',
            'response_session_storage_key' => 'sc_workspace_ai_response_v1',
            'response_schema' => 'sc-workspace-ai-response/1.0',
            'producer_helper' => sc_workspace_ai_adapter_script_url(),
            'automatic_remote_send' => false,
            'automatic_object_mutation' => false,
            'automatic_decision_authority' => false,
            'automatic_publication' => false,
            'human_acceptance_required' => true,
            'grounding_requires_selected_workspace_objects' => true,
            'response_materializes_document_only_after_acceptance' => true,
            'same_origin_research_librarian_handoff_supported' => true,
            'server_ai_provider_configured_by_workspace' => false,
            'local_first' => true,
        ));
    }

    public function interoperability_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-interoperability-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/1.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'accepted_formats' => array('json','csv','tsv','markdown','html','text'),
            'staged_review_required' => true,
            'automatic_overwrite' => false,
            'id_collision_strategy' => 'remap-new-stable-id',
            'imported_provenance_required' => true,
            'file_fingerprint_algorithm' => 'SHA-256',
            'generic_json_default_type' => 'dataset',
            'markdown_html_text_default_type' => 'document',
            'csv_tsv_default_type' => 'dataset',
            'project_package_import_supported' => true,
            'object_package_import_supported' => true,
            'portable_interchange_export_supported' => true,
            'server_import_pipeline' => false,
            'automatic_trust_elevation' => false,
            'local_first' => true,
        ));
    }

    public function share_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-share-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'transport' => array('local-download', 'manual-file-transfer', 'local-import-as-copy'),
            'review_copy_html' => true,
            'integrity_algorithm' => 'SHA-256',
            'device_identity_exported' => false,
            'account_identity_exported' => false,
            'handoff_session_state_exported' => false,
            'recent_tool_history_exported' => false,
            'automatic_cloud_upload' => false,
            'public_share_links' => false,
            'collaboration' => false,
            'import_overwrites_existing_project' => false,
            'human_export_required' => true,
            'human_import_required' => true,
        ));
    }

    public function activity_intelligence_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-activity-intelligence-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'activity_intelligence_schema' => 'sc-workspace-activity-intelligence/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'derived_from_local_project_state' => true,
            'next_actions_user_created' => true,
            'signal_kinds' => array('workflow', 'research', 'analysis', 'decision', 'traceability', 'handoff', 'briefing', 'collaboration', 'institutional', 'stale'),
            'signal_severities' => array('info', 'attention', 'high'),
            'productivity_score' => false,
            'automatic_task_completion' => false,
            'time_on_page_tracking' => false,
            'behavioral_telemetry' => false,
            'server_activity_analytics' => false,
            'local_first' => true,
        ));
    }

    public function collaboration_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-collaboration-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'roles' => array('owner', 'contributor', 'reviewer', 'observer'),
            'review_statuses' => array('draft', 'requested', 'in-review', 'changes-requested', 'approved', 'closed'),
            'thread_kinds' => array('comment', 'suggestion', 'question'),
            'thread_statuses' => array('open', 'resolved'),
            'transport' => array('local-download', 'manual-file-transfer', 'local-import'),
            'roles_are_server_permissions' => false,
            'source_project_owner_controlled' => true,
            'imported_feedback_mutates_project_automatically' => false,
            'review_request_contains_privacy_minimized_project_copy' => true,
            'review_response_contains_project_content' => false,
            'live_collaboration' => false,
            'server_collaboration' => false,
            'cloud_team_directory' => false,
            'automatic_cloud_upload' => false,
            'local_first' => true,
        ));
    }

    public function institutional_handoff_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-institutional-handoff-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'institutional_handoff_schema' => 'sc-workspace-institutional-handoff/1.0',
            'institutional_handoff_package_schema' => 'sc-workspace-institutional-handoff-package/1.0',
            'institutional_handoff_receipt_schema' => 'sc-workspace-institutional-handoff-receipt/1.0',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'target_product' => 'catalyst-intelligence-platform',
            'promotion_mode' => 'copy-into-institution',
            'source_workspace_retains_independent_copy' => true,
            'institutional_governance_begins_after_acceptance' => true,
            'explicit_object_scope_required' => true,
            'human_acknowledgement_required' => true,
            'readiness_is_explainable_not_scored' => true,
            'package_integrity_algorithm' => 'SHA-256',
            'receipt_match_requires_handoff_and_source_project' => true,
            'receipt_mutates_source_project_content' => false,
            'automatic_cloud_upload' => false,
            'automatic_institutional_ingestion' => false,
            'server_project_conversion_in_place' => false,
            'organization_permissions_in_workspace' => false,
            'local_first' => true,
        ));
    }

    public function account_persistence_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-account-persistence-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'anonymous_access' => true,
            'account_required' => false,
            'authentication_provider' => 'wordpress',
            'manual_cloud_backup' => true,
            'cross_device_sync' => true,
            'sync_requires_explicit_project_enrollment' => true,
            'automatic_cloud_upload' => false,
            'background_sync' => false,
            'restore_mode' => 'new-local-copy',
            'overwrite_local_project_on_restore' => false,
            'server_store' => 'wordpress-user-meta',
            'max_projects_per_account' => 25,
            'max_project_bytes' => 2621440,
            'max_account_bytes' => 26214400,
            'backup_schema' => 'sc-workspace-cloud-backup/1.0',
            'sync_schema' => 'sc-workspace-cross-device-sync/1.0',
            'sync_push_schema' => 'sc-workspace-sync-push/1.0',
            'sync_conflict_strategy' => 'server-revision-precondition',
            'silent_last_write_wins' => false,
            'integrity_algorithm' => 'SHA-256',
            'team_storage' => false,
            'institutional_permissions' => false,
        ));
    }

    public function sync_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-cross-device-sync-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'sync_schema' => 'sc-workspace-cross-device-sync/1.0',
            'push_schema' => 'sc-workspace-sync-push/1.0',
            'account_required_for_sync' => true,
            'guest_workspace_supported' => true,
            'explicit_project_enrollment' => true,
            'automatic_enrollment_on_sign_in' => false,
            'background_sync' => false,
            'automatic_upload' => false,
            'revision_precondition_required' => true,
            'conflict_http_status' => 409,
            'silent_last_write_wins' => false,
            'safe_remote_pull_requires_no_competing_local_change' => true,
            'conflict_remote_can_open_as_copy' => true,
            'accepting_cloud_preserves_local_conflict_copy' => true,
            'accepting_local_requires_explicit_confirmation' => true,
            'integrity_algorithm' => 'SHA-256',
            'server_store' => 'wordpress-user-meta',
            'team_sync' => false,
            'institutional_sync' => false,
        ));
    }

    public function version_history_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-version-history-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'version_history_schema' => 'sc-workspace-version-history/1.0',
            'restore_point_schema' => 'sc-workspace-restore-point/1.0',
            'storage_scope' => 'browser-local-workspace-level',
            'named_restore_points' => true,
            'integrity_algorithm' => 'SHA-256',
            'restore_mode' => 'new-local-copy',
            'overwrite_current_project' => false,
            'project_schema_changes' => false,
            'max_restore_points_per_project' => 20,
            'max_restore_points_workspace' => 80,
            'max_restore_point_bytes' => 1572864,
            'automatic_cloud_upload' => false,
            'server_version_history' => false,
            'sync_conflict_protections_preserved' => true,
        ));
    }

    public function cloud_permission() {
        return is_user_logged_in() && current_user_can('read');
    }

    private function cloud_store_key() {
        return 'sc_workspace_cloud_projects_v1';
    }

    private function cloud_store_read() {
        $store = get_user_meta(get_current_user_id(), $this->cloud_store_key(), true);
        return is_array($store) ? $store : array();
    }

    private function cloud_project_fingerprint($project) {
        $copy = is_array($project) ? $project : array();
        $copy['persistence'] = array(
            'scope' => 'account-sync-copy',
            'syncState' => 'sync-head',
            'accountEligible' => true,
            'serverStored' => true,
        );
        $copy['recentTools'] = array();
        return hash('sha256', wp_json_encode($copy, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    }

    private function cloud_metadata($record) {
        return array(
            'projectId' => isset($record['projectId']) ? (string) $record['projectId'] : '',
            'title' => isset($record['title']) ? (string) $record['title'] : 'Workspace project',
            'clientUpdatedAt' => isset($record['clientUpdatedAt']) ? (string) $record['clientUpdatedAt'] : '',
            'backedUpAt' => isset($record['backedUpAt']) ? (string) $record['backedUpAt'] : '',
            'fingerprint' => isset($record['fingerprint']) ? (string) $record['fingerprint'] : '',
            'projectFingerprint' => isset($record['projectFingerprint']) ? (string) $record['projectFingerprint'] : '',
            'revision' => isset($record['revision']) ? (int) $record['revision'] : 0,
            'storageMode' => isset($record['storageMode']) ? (string) $record['storageMode'] : 'manual-backup',
            'bytes' => isset($record['bytes']) ? (int) $record['bytes'] : 0,
            'objectCount' => isset($record['objectCount']) ? (int) $record['objectCount'] : 0,
        );
    }

    public function cloud_projects_list() {
        $items = array();
        foreach ($this->cloud_store_read() as $record) {
            if (is_array($record)) {
                $items[] = $this->cloud_metadata($record);
            }
        }
        usort($items, function($a, $b) {
            return strcmp($b['backedUpAt'], $a['backedUpAt']);
        });
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-account-cloud-index/1.1',
            'items' => $items,
            'automaticSync' => false,
            'explicitSync' => true,
        ));
    }

    public function cloud_project_store($request) {
        $payload = $request->get_json_params();
        $schema = is_array($payload) ? (string) ($payload['schema'] ?? '') : '';
        $is_manual = $schema === 'sc-workspace-cloud-backup/1.0';
        $is_sync = $schema === 'sc-workspace-sync-push/1.0';
        if (!is_array($payload) || (!$is_manual && !$is_sync)) {
            return new WP_Error('scw_invalid_cloud_backup', 'Unsupported Workspace account-persistence package.', array('status' => 400));
        }
        $project = isset($payload['project']) && is_array($payload['project']) ? $payload['project'] : null;
        $project_id = isset($payload['sourceProjectId']) ? sanitize_key((string) $payload['sourceProjectId']) : '';
        if (!$project || $project_id === '' || (($project['schema'] ?? '') !== 'sc-workspace-project/11.0')) {
            return new WP_Error('scw_invalid_cloud_project', 'A valid Workspace project is required.', array('status' => 400));
        }
        $canonical = wp_json_encode($payload, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        $bytes = strlen($canonical);
        if ($bytes > 2621440) {
            return new WP_Error('scw_cloud_project_too_large', 'This project exceeds the 2.5 MB account-persistence limit.', array('status' => 413));
        }
        $store = $this->cloud_store_read();
        $existing = isset($store[$project_id]) && is_array($store[$project_id]) ? $store[$project_id] : null;
        $current_revision = $existing ? max(0, (int) ($existing['revision'] ?? 1)) : 0;
        if ($is_sync) {
            $expected_revision = isset($payload['expectedRevision']) ? max(0, (int) $payload['expectedRevision']) : -1;
            if ($expected_revision !== $current_revision) {
                return new WP_Error('scw_sync_conflict', 'Workspace sync revision conflict. Check status before choosing a resolution.', array(
                    'status' => 409,
                    'currentRevision' => $current_revision,
                    'current' => $existing ? $this->cloud_metadata($existing) : null,
                ));
            }
        }
        if (!$existing && count($store) >= 25) {
            return new WP_Error('scw_cloud_project_limit', 'This account has reached the 25-project account-persistence limit.', array('status' => 409));
        }
        $replacement = array(
            'projectId' => $project_id,
            'title' => sanitize_text_field((string) ($payload['projectTitle'] ?? $project['title'] ?? 'Workspace project')),
            'clientUpdatedAt' => sanitize_text_field((string) ($payload['clientUpdatedAt'] ?? $project['updatedAt'] ?? '')),
            'backedUpAt' => gmdate('c'),
            'fingerprint' => hash('sha256', $canonical),
            'projectFingerprint' => $this->cloud_project_fingerprint($project),
            'revision' => $current_revision + 1,
            'storageMode' => $is_sync ? 'sync-head' : 'manual-backup',
            'bytes' => $bytes,
            'objectCount' => isset($project['objects']) && is_array($project['objects']) ? count($project['objects']) : 0,
            'package' => $payload,
        );
        $candidate = $store;
        $candidate[$project_id] = $replacement;
        $account_bytes = 0;
        foreach ($candidate as $record) {
            $account_bytes += is_array($record) ? (int) ($record['bytes'] ?? 0) : 0;
        }
        if ($account_bytes > 26214400) {
            return new WP_Error('scw_cloud_account_limit', 'This account has reached the 25 MB Workspace account-persistence limit.', array('status' => 409));
        }
        update_user_meta(get_current_user_id(), $this->cloud_store_key(), $candidate);
        return rest_ensure_response(array('ok' => true, 'item' => $this->cloud_metadata($replacement)));
    }

    public function cloud_project_get($request) {
        $project_id = sanitize_key((string) $request['project_id']);
        $store = $this->cloud_store_read();
        if (!isset($store[$project_id]) || !is_array($store[$project_id])) {
            return new WP_Error('scw_cloud_project_missing', 'Workspace account project copy not found.', array('status' => 404));
        }
        $record = $store[$project_id];
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-cloud-backup-response/1.1',
            'item' => $this->cloud_metadata($record),
            'package' => $record['package'],
        ));
    }

    public function cloud_project_delete($request) {
        $project_id = sanitize_key((string) $request['project_id']);
        $store = $this->cloud_store_read();
        if (!isset($store[$project_id])) {
            return rest_ensure_response(array('ok' => true, 'deleted' => false));
        }
        unset($store[$project_id]);
        update_user_meta(get_current_user_id(), $this->cloud_store_key(), $store);
        return rest_ensure_response(array('ok' => true, 'deleted' => true));
    }

    public function readiness_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-release-readiness-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Stability, Accessibility & Release Readiness',
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'schema_migration_required' => false,
            'local_recovery' => array(
                'last_known_good_snapshot' => true,
                'damaged_state_quarantine' => true,
                'read_after_write_verification' => true,
                'explicit_emergency_backup_export' => true,
            ),
            'accessibility' => array(
                'target' => 'WCAG 2.2 AA',
                'skip_link' => true,
                'visible_focus' => true,
                'reduced_motion' => true,
                'forced_colors' => true,
                'keyboard_graph_nodes' => true,
                'live_save_status' => true,
            ),
            'diagnostics' => array(
                'local_only' => true,
                'automatic_telemetry' => false,
                'project_content_in_diagnostic_export' => false,
                'device_identifier_in_diagnostic_export' => false,
                'checks' => array('storage-availability','state-serializable','last-known-good','web-crypto','reduced-motion','online-state','workspace-size'),
            ),
            'governance' => array(
                'cloud_sync' => false,
                'server_project_storage' => false,
                'behavioral_telemetry' => false,
                'productivity_score' => false,
                'automatic_repair_without_user_visibility' => false,
            ),
        ));
    }

    public function platform_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-platform-contract/1.2',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'dedicated_shortcode' => 'sc_workspace_platform',
            'canonical_path_after_conversion' => '/platform/',
            'legacy_workspace_path' => '/platform/workspace/',
            'automatic_activation_conversion' => false,
            'conversion_requires_administrator_action' => true,
            'conversion_reversible' => true,
            'page_id_preserved' => true,
            'slug_preserved' => true,
            'page_template_preserved' => true,
            'data_schema_change' => false,
            'storage_schema_version' => 23,
            'project_schema' => 'sc-workspace-project/11.0',
            'public_product_name' => 'Workspace',
            'recommended_navigation_label' => 'Workspace',
            'public_experience' => 'advisory-aligned-editorial',
            'traceability_workspace_mode' => true,
            'briefing_publication_workspace_mode' => true,
            'guided_workflows_workspace_mode' => true,
            'interoperability_workspace_view' => true,
            'collaboration_foundation_view' => true,
            'editorial_header_bar' => true,
            'editorial_shell' => true,
            'illustrative_software_preview' => true,
            'alternating_surface_rhythm' => true,
            'technical_controls_progressively_disclosed' => true,
            'project_mode_navigation' => true,
            'navigation_relabel_available' => true,
            'navigation_relabel_requires_administrator_action' => true,
            'state' => SC_Workspace_Platform::contract_status(),
        ));
    }

    public function identity_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-identity-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'identity_schema' => 'sc-workspace-identity/1.0',
            'authentication_provider' => 'wordpress',
            'anonymous_access' => true,
            'account_required' => false,
            'registration_respects_site_setting' => true,
            'device_identity' => true,
            'device_identity_contains_personal_data' => false,
            'project_persistence_scope' => 'device-by-default',
            'server_project_storage' => 'manual-backup-plus-explicit-sync-head',
            'cloud_sync' => 'explicit-project-enrollment',
            'automatic_account_upload' => false,
            'manual_cloud_backup' => true,
            'cross_device_sync' => true,
            'sync_requires_explicit_project_enrollment' => true,
            'background_sync' => false,
            'silent_last_write_wins' => false,
            'restore_mode' => 'new-local-copy',
            'manual_portability' => 'project-json-export-import',
            'future_sync_boundary_prepared' => false,
        ));
    }

    private function enqueue_assets() {
        wp_enqueue_style(
            'sc-workspace-v0230',
            SC_WORKSPACE_URL . 'assets/css/workspace-v0.23.0.css',
            array(),
            SC_WORKSPACE_VERSION
        );
        wp_enqueue_script(
            'sc-workspace-v0230',
            SC_WORKSPACE_URL . 'assets/js/workspace-v0.23.0.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );

        $return_url = SC_Workspace_Platform::canonical_url();
        $authenticated = is_user_logged_in();
        $user = $authenticated ? wp_get_current_user() : null;
        wp_localize_script('sc-workspace-v0230', 'SCWorkspaceIdentity', array(
            'authenticated' => $authenticated,
            'displayName' => $authenticated && $user ? $user->display_name : '',
            'loginUrl' => wp_login_url($return_url),
            'logoutUrl' => wp_logout_url($return_url),
            'registrationEnabled' => (bool) get_option('users_can_register'),
            'registrationUrl' => get_option('users_can_register') ? wp_registration_url() : '',
            'storageMode' => 'device-local-default',
            'cloudSync' => 'explicit-project-enrollment',
            'manualCloudBackup' => true,
            'crossDeviceSync' => true,
            'backgroundSync' => false,
            'serverProjectStorage' => 'manual-backup-plus-explicit-sync-head',
            'restRoot' => esc_url_raw(rest_url('sc-workspace/v1/')),
            'restNonce' => $authenticated ? wp_create_nonce('wp_rest') : '',
        ));
    }

    private function tools() {
        return array(
            array('key' => 'research-librarian', 'eyebrow' => 'DISCOVER', 'name' => 'Research Librarian', 'description' => 'Frame questions, route inquiry, and move into evidence-backed research.', 'url' => home_url('/research-librarian/')),
            array('key' => 'knowledge-library', 'eyebrow' => 'LEARN', 'name' => 'Knowledge Library', 'description' => 'Explore structured articles, fields, pathways, and open knowledge resources.', 'url' => home_url('/knowledge-libraries/')),
            array('key' => 'site-intelligence', 'eyebrow' => 'OBSERVE', 'name' => 'Site Intelligence', 'description' => 'Investigate public signals, countries, systems, evidence, and live intelligence.', 'url' => home_url('/platform/site-intelligence/')),
            array('key' => 'workbench', 'eyebrow' => 'COMPUTE', 'name' => 'Workbench', 'description' => 'Run calculations, models, engineering analysis, and scientific workflows.', 'url' => home_url('/platform/workbench/')),
            array('key' => 'analytics-r', 'eyebrow' => 'ANALYZE', 'name' => 'Analytics R', 'description' => 'Explore statistical, comparative, uncertainty, and analytical workflows.', 'url' => home_url('/platform/catalyst-analytics-r/')),
            array('key' => 'decision-studio', 'eyebrow' => 'DECIDE', 'name' => 'Decision Studio', 'description' => 'Structure alternatives, assumptions, scenarios, evidence, and trade-offs.', 'url' => home_url('/platform/decision-studio/')),
            array('key' => 'catalyst-canvas', 'eyebrow' => 'MAP', 'name' => 'Catalyst Canvas', 'description' => 'Frame systems, stakeholders, evidence, journeys, and structured thinking.', 'url' => home_url('/platform/catalyst-canvas/')),
            array('key' => 'catalyst-data', 'eyebrow' => 'DATA', 'name' => 'Catalyst Data', 'description' => 'Prepare, structure, trace, and move data into analysis workflows.', 'url' => home_url('/platform/catalyst-data/')),
            array('key' => 'lab', 'eyebrow' => 'EXPERIMENT', 'name' => 'Lab', 'description' => 'Use experimental scientific, computational, and observational tools.', 'url' => home_url('/lab/')),
        );
    }

    public function render_workspace($atts = array()) {
        $this->enqueue_assets();
        $tools = $this->tools();
        $return_url = SC_Workspace_Platform::canonical_url();
        ob_start();
        ?>
        <section class="scw-shell" data-sc-workspace data-version="<?php echo esc_attr(SC_WORKSPACE_VERSION); ?>" data-storage-version="23" data-return-url="<?php echo esc_url($return_url); ?>">
            <a class="scw-skip-link" href="#scw-workspace-main">Skip to Workspace application</a>
            <div class="scw-hero">
                <div class="scw-kicker">SUSTAINABLE CATALYST / WORKSPACE</div>
                <div class="scw-hero-grid">
                    <div>
                        <h1>Workspace</h1>
                        <p class="scw-deck">A free project environment for carrying questions, evidence, data, analysis, decisions, and authored work across Sustainable Catalyst.</p>
                    </div>
                    <div class="scw-state" aria-label="Workspace release state">
                        <span>FREE ACCESS</span>
                        <span>v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></span>
                        <span>ACCOUNT-AWARE</span>
                        <span>EXPERIMENTAL</span>
                    </div>
                </div>
            </div>

            <div class="scw-boundary" role="note">
                <strong>Local-first by default</strong>
                <span>Workspace remains fully usable without signing in. Projects are stored on this device. Sign-in is optional. Account recovery and cross-device sync are optional. Backups require an explicit action, sync requires explicit per-project enrollment, and nothing synchronizes in the background. Connected tools can return structured work to the originating project through the established local-first handoff contract.</span>
            </div>

            <details class="scw-settings-drawer" data-scw-settings-drawer>
                <summary><span><small>Storage &amp; identity</small><strong>Saved on this device</strong></span><em>Manage</em></summary>
                <section class="scw-identity" aria-labelledby="scw-identity-title">
                <div class="scw-identity-main">
                    <div>
                        <div class="scw-kicker">IDENTITY &amp; PERSISTENCE</div>
                        <h2 id="scw-identity-title">Identity is optional. Your project storage boundary stays explicit.</h2>
                    </div>
                    <div class="scw-identity-session">
                        <span class="scw-identity-badge" data-scw-identity-badge>GUEST</span>
                        <strong data-scw-identity-heading>Guest Workspace</strong>
                        <span data-scw-identity-detail>Your work is associated only with this browser device.</span>
                    </div>
                </div>
                <div class="scw-identity-grid">
                    <div><span>ACCESS</span><strong data-scw-identity-access>No account required</strong><small>Anonymous use remains a first-class path.</small></div>
                    <div><span>PERSISTENCE</span><strong>Local first · optional backup/sync</strong><small>Backups are explicit. Sync is opt-in per project and never runs in the background.</small></div>
                    <div><span>DEVICE ID</span><strong data-scw-device-id>Initializing…</strong><small>Pseudonymous local identifier; no personal data is encoded.</small></div>
                    <div class="scw-identity-actions">
                        <a class="scw-button scw-button-primary" data-scw-login href="#">Sign in</a>
                        <a class="scw-button" data-scw-register href="#" hidden>Create free account</a>
                        <a class="scw-button" data-scw-logout href="#" hidden>Sign out</a>
                    </div>
                </div>
                <p class="scw-identity-note" data-scw-identity-note>Sign-in keeps local work available and unlocks explicit account recovery plus opt-in per-project sync. Sign-in alone uploads nothing.</p>
                </section>
                <section class="scw-cloud-recovery" aria-labelledby="scw-cloud-recovery-title">
                    <div class="scw-cloud-recovery-head"><div><div class="scw-kicker">ACCOUNT CLOUD RECOVERY</div><h3 id="scw-cloud-recovery-title">Back up deliberately. Restore without overwriting local work.</h3></div><span class="scw-cloud-badge" data-scw-cloud-badge>LOCAL ONLY</span></div>
                    <p>Account recovery is optional and account-bound. Manual backups remain restore-as-copy. Sync below is separately enrolled per project and uses revision checks rather than silent overwrite.</p>
                    <div class="scw-cloud-controls">
                        <label><span>LOCAL PROJECT</span><select data-scw-cloud-project><option value="">Choose a project</option></select></label>
                        <button class="scw-button scw-button-primary" type="button" data-scw-cloud-backup>Back up now</button>
                        <button class="scw-button" type="button" data-scw-cloud-refresh>Refresh backups</button>
                    </div>
                    <div class="scw-cloud-status" data-scw-cloud-status role="status" aria-live="polite">Sign in to use account recovery and explicit sync. Local Workspace remains fully available without an account.</div>
                    <div class="scw-cloud-list" data-scw-cloud-list></div>
                </section>
                <section class="scw-account-sync" aria-labelledby="scw-account-sync-title">
                    <div class="scw-account-sync-head"><div><div class="scw-kicker">CROSS-DEVICE SYNC</div><h3 id="scw-account-sync-title">Synchronize deliberately. Never hide a conflict.</h3></div><span class="scw-sync-badge" data-scw-sync-badge>LOCAL ONLY</span></div>
                    <p>Sync is opt-in for each project and runs only when you choose an action. Workspace compares SHA-256 project fingerprints and server revisions before pushing or pulling. If both sides changed, neither copy is overwritten automatically.</p>
                    <div class="scw-sync-controls">
                        <label><span>LOCAL PROJECT</span><select data-scw-sync-project><option value="">Choose a project</option></select></label>
                        <button class="scw-button" type="button" data-scw-sync-toggle>Enable sync</button>
                        <button class="scw-button" type="button" data-scw-sync-check disabled>Check status</button>
                        <button class="scw-button scw-button-primary" type="button" data-scw-sync-now disabled>Sync now</button>
                    </div>
                    <div class="scw-sync-grid" aria-live="polite">
                        <div><span>LOCAL</span><strong data-scw-sync-local>Choose project</strong></div>
                        <div><span>CLOUD</span><strong data-scw-sync-remote>No cloud head</strong></div>
                        <div><span>COMMON BASE</span><strong data-scw-sync-baseline>No common revision</strong></div>
                        <div><span>STATE</span><strong data-scw-sync-state>DISABLED</strong></div>
                    </div>
                    <div class="scw-sync-status" data-scw-sync-status role="status" aria-live="polite">Sign in to enable explicit cross-device sync. Guest/local Workspace remains fully available.</div>
                    <div class="scw-sync-resolution" aria-label="Conflict-safe synchronization actions">
                        <button class="scw-button" type="button" data-scw-sync-remote-copy hidden>Open cloud as copy</button>
                        <button class="scw-button" type="button" data-scw-sync-resolve-local hidden>Keep local as sync head</button>
                        <button class="scw-button" type="button" data-scw-sync-resolve-cloud hidden>Use cloud here · preserve local copy</button>
                    </div>
                    <div class="scw-sync-boundary" role="note"><strong>No background synchronization</strong><span>Enabling sync stores local enrollment metadata only. Project content moves only after an explicit Sync now or conflict-resolution action. Shared team sync and institutional storage remain outside Workspace.</span></div>
                </section>
                <section class="scw-readiness" aria-labelledby="scw-readiness-title">
                    <div class="scw-readiness-head"><div><div class="scw-kicker">LOCAL HEALTH &amp; RECOVERY</div><h3 id="scw-readiness-title">Inspect the browser boundary before it becomes a problem.</h3></div><span class="scw-readiness-badge" data-scw-readiness-badge>NOT CHECKED</span></div>
                    <p>Diagnostics run only in this browser. The exported diagnostic report contains capability/status metadata, not project content, object text, URLs, or the local device identifier.</p>
                    <div class="scw-readiness-grid" aria-live="polite">
                        <div><span>STORAGE</span><strong data-scw-readiness-storage>Not checked</strong><small>Browser-local persistence availability and current-state serialization.</small></div>
                        <div><span>RECOVERY</span><strong data-scw-readiness-recovery>Not checked</strong><small>Last-known-good local snapshot availability.</small></div>
                        <div><span>INTEGRITY</span><strong data-scw-readiness-crypto>Not checked</strong><small>SHA-256/Web Crypto support for portable package verification.</small></div>
                        <div><span>WORKSPACE SIZE</span><strong data-scw-readiness-size>Not checked</strong><small>Approximate local serialized state size; no content leaves the browser.</small></div>
                    </div>
                    <div class="scw-readiness-actions">
                        <button class="scw-button scw-button-primary" type="button" data-scw-run-diagnostics>Run diagnostics</button>
                        <button class="scw-button" type="button" data-scw-export-diagnostics disabled>Export diagnostic report</button>
                        <button class="scw-button" type="button" data-scw-emergency-backup>Export emergency backup</button>
                    </div>
                    <div class="scw-readiness-status" data-scw-readiness-status role="status" aria-live="polite">No diagnostic run has been performed.</div>
                </section>
            </details>

            <div class="scw-recovery" data-scw-recovery hidden role="status" aria-live="polite">
                <div><strong>Workspace recovery mode</strong><span data-scw-recovery-message>A damaged local state was isolated and a clean workspace was opened.</span></div>
                <button type="button" class="scw-button" data-scw-dismiss-recovery>Dismiss</button>
            </div>

            <nav id="scw-workspace-main" class="scw-workspace-view-nav" aria-label="Workspace views" data-scw-workspace-view-nav tabindex="-1">
                <button type="button" class="is-active" data-scw-workspace-view="projects" aria-pressed="true">Projects</button>
                <button type="button" data-scw-workspace-view="knowledge" aria-pressed="false">Knowledge</button>
                <button type="button" data-scw-workspace-view="graph" aria-pressed="false">Graph</button>
                <button type="button" data-scw-workspace-view="activity" aria-pressed="false">Activity</button>
                <button type="button" data-scw-workspace-view="history" aria-pressed="false">History</button>
                <button type="button" data-scw-workspace-view="interoperability" aria-pressed="false">Import &amp; Interoperability</button>
                <button type="button" data-scw-workspace-view="collaboration" aria-pressed="false">Collaborate</button>
                <button type="button" data-scw-workspace-view="institutional" aria-pressed="false">Institutional</button>
                <button type="button" data-scw-workspace-view="share" aria-pressed="false">Share</button>
            </nav>

            <section class="scw-projects" data-scw-workspace-section="projects" aria-labelledby="scw-projects-title">
                <div class="scw-section-head scw-section-head-projects">
                    <div>
                        <div class="scw-kicker">PROJECTS</div>
                        <h2 id="scw-projects-title">Persistent work, without an account.</h2>
                    </div>
                    <div class="scw-project-actions">
                        <button class="scw-button scw-button-primary" type="button" data-scw-new-project>New project</button>
                        <button class="scw-button" type="button" data-scw-import-project>Import project</button>
                        <input type="file" accept="application/json,.json" data-scw-import-file hidden>
                    </div>
                </div>

                <form class="scw-create" data-scw-create-form hidden>
                    <label><span>Project name</span><input type="text" name="title" maxlength="120" required placeholder="Untitled project"></label>
                    <label><span>Description <em>optional</em></span><textarea name="description" rows="2" maxlength="600" placeholder="What are you trying to understand, analyze, or decide?"></textarea></label>
                    <div class="scw-create-actions">
                        <button class="scw-button scw-button-primary" type="submit">Create project</button>
                        <button class="scw-button" type="button" data-scw-cancel-create>Cancel</button>
                    </div>
                </form>

                <div class="scw-project-toolbar">
                    <div class="scw-filter" aria-label="Project filter">
                        <button type="button" class="is-active" data-scw-filter="active" aria-pressed="true">Active</button>
                        <button type="button" data-scw-filter="archived" aria-pressed="false">Archived</button>
                    </div>
                    <div class="scw-storage-state"><span class="scw-storage-dot" aria-hidden="true"></span><span data-scw-storage-state role="status" aria-live="polite">Local project storage ready</span></div>
                </div>

                <div class="scw-empty" data-scw-empty>
                    <strong>No Workspace Projects yet.</strong>
                    <span>Create one to keep notes, objects, activity, and cross-product context together on this device.</span>
                </div>
                <div class="scw-project-list" data-scw-project-list aria-live="polite"></div>
            </section>

            <section class="scw-personal-knowledge" data-scw-workspace-section="knowledge" hidden aria-labelledby="scw-knowledge-title">
                <div class="scw-knowledge-head">
                    <div>
                        <div class="scw-kicker">PERSONAL KNOWLEDGE ENVIRONMENT</div>
                        <h2 id="scw-knowledge-title">Find and reuse what you already know.</h2>
                        <p>Search canonical Workspace Objects across projects, inspect provenance and internal references, discover transparent related-work signals, and organize reusable objects into local collections. The index is built in this browser from existing project data; Workspace does not upload it to a server.</p>
                    </div>
                </div>
                <div class="scw-knowledge-metrics" aria-label="Personal knowledge metrics">
                    <div><strong data-scw-knowledge-metric-objects>0</strong><span>indexed objects</span></div>
                    <div><strong data-scw-knowledge-metric-projects>0</strong><span>projects represented</span></div>
                    <div><strong data-scw-knowledge-metric-collections>0</strong><span>collections</span></div>
                    <div><strong data-scw-knowledge-metric-tags>0</strong><span>distinct tags</span></div>
                </div>
                <div class="scw-knowledge-searchbar">
                    <label class="scw-knowledge-search"><span>Search local knowledge</span><input type="search" maxlength="240" data-scw-knowledge-search placeholder="Search titles, summaries, content, tags, and provenance"></label>
                    <label><span>Type</span><select data-scw-knowledge-type><option value="all">All types</option><option value="source">Sources</option><option value="evidence">Evidence</option><option value="dataset">Datasets</option><option value="analysis">Analyses</option><option value="decision">Decisions</option><option value="document">Documents</option><option value="export">Exports</option></select></label>
                    <label><span>Project</span><select data-scw-knowledge-project><option value="all">All projects</option></select></label>
                    <label><span>Tag</span><input type="text" maxlength="80" data-scw-knowledge-tag placeholder="Filter by tag"></label>
                    <label><span>Scope</span><select data-scw-knowledge-scope><option value="active">Active projects</option><option value="all">Active + archived</option></select></label>
                </div>
                <div class="scw-knowledge-layout">
                    <section class="scw-knowledge-results-panel" aria-labelledby="scw-knowledge-results-heading">
                        <div class="scw-knowledge-panel-head"><span>01 / INDEX</span><h3 id="scw-knowledge-results-heading">Cross-project knowledge</h3></div>
                        <div class="scw-knowledge-empty" data-scw-knowledge-empty>No matching Workspace Objects yet. Objects remain project-owned; this index only makes them discoverable across the local Workspace.</div>
                        <div class="scw-knowledge-results" data-scw-knowledge-results></div>
                    </section>
                    <aside class="scw-knowledge-detail-panel" aria-labelledby="scw-knowledge-detail-heading">
                        <div class="scw-knowledge-panel-head"><span>02 / CONTEXT</span><h3 id="scw-knowledge-detail-heading">Provenance &amp; related work</h3></div>
                        <div data-scw-knowledge-detail></div>
                    </aside>
                </div>
                <section class="scw-knowledge-collections" aria-labelledby="scw-knowledge-collections-heading">
                    <div class="scw-knowledge-panel-head"><span>03 / COLLECTIONS</span><h3 id="scw-knowledge-collections-heading">Organize reusable objects without moving them.</h3></div>
                    <form class="scw-knowledge-collection-form" data-scw-knowledge-collection-form>
                        <label><span>Collection name</span><input type="text" name="title" maxlength="160" required placeholder="e.g. Grid resilience evidence"></label>
                        <label><span>Description</span><input type="text" name="description" maxlength="1000" placeholder="Optional purpose or scope"></label>
                        <button class="scw-button" type="submit">Create collection</button>
                    </form>
                    <div class="scw-knowledge-collection-controls"><select data-scw-knowledge-collection-select aria-label="Active knowledge collection"><option value="">Select collection</option></select><div class="scw-knowledge-collection-list" data-scw-knowledge-collection-list></div></div>
                    <div class="scw-knowledge-collection-detail" data-scw-knowledge-collection-detail></div>
                </section>
                <div class="scw-knowledge-boundary" role="note"><strong>Local index, canonical objects</strong><span>Personal Knowledge does not copy object bodies into a separate database. Search is derived from device-local projects; collections store only stable project/object references. Related-work suggestions use visible deterministic signals rather than hidden semantic scoring.</span></div>
            </section>


            <section class="scw-knowledge-graph" data-scw-workspace-section="graph" hidden aria-labelledby="scw-graph-title">
                <div class="scw-graph-head">
                    <div><div class="scw-editorial-kicker">WORKSPACE SEARCH &amp; KNOWLEDGE GRAPH</div><h2 id="scw-graph-title">See how projects, evidence, analysis, decisions, and provenance connect.</h2><p>The graph is derived from canonical Workspace Objects and explicit relationships already present in your device-local work. Search the graph, focus a node, and inspect why two things are connected.</p></div>
                </div>
                <div class="scw-graph-metrics" aria-label="Knowledge graph metrics">
                    <div><strong data-scw-graph-metric-nodes>0</strong><span>Nodes</span></div><div><strong data-scw-graph-metric-edges>0</strong><span>Relationships</span></div><div><strong data-scw-graph-metric-projects>0</strong><span>Projects</span></div><div><strong data-scw-graph-metric-provenance>0</strong><span>Provenance sources</span></div>
                </div>
                <div class="scw-graph-controls">
                    <label class="scw-graph-search"><span>Search graph</span><input type="search" maxlength="240" data-scw-graph-search placeholder="Search projects, objects, provenance, tags"></label>
                    <label><span>Node type</span><select data-scw-graph-node-type><option value="all">All nodes</option><option value="project">Projects</option><option value="provenance">Provenance</option><option value="source">Sources</option><option value="evidence">Evidence</option><option value="dataset">Datasets</option><option value="analysis">Analyses</option><option value="decision">Decisions</option><option value="document">Documents</option><option value="export">Exports</option></select></label>
                    <label><span>Relationship</span><select data-scw-graph-relation><option value="all">All relationships</option><option value="contains">Contains</option><option value="sourced-from">Sourced from</option><option value="same-source">Same source</option><option value="evidence-from">Evidence from</option><option value="uses">Uses</option><option value="informs">Informs</option><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="derived-from">Derived from</option><option value="produced-by">Produced by</option><option value="supersedes">Supersedes</option><option value="cites">Cites</option></select></label>
                    <label><span>Project</span><select data-scw-graph-project><option value="all">All projects</option></select></label>
                    <label><span>Scope</span><select data-scw-graph-scope><option value="active">Active projects</option><option value="all">Active + archived</option></select></label>
                    <label><span>Depth</span><select data-scw-graph-depth><option value="1">1 hop</option><option value="2">2 hops</option></select></label>
                </div>
                <div class="scw-graph-layout">
                    <section class="scw-graph-results-panel" aria-labelledby="scw-graph-results-heading"><div class="scw-knowledge-panel-head"><span>01 / SEARCH</span><h3 id="scw-graph-results-heading">Graph nodes</h3></div><div class="scw-graph-results" data-scw-graph-results></div></section>
                    <section class="scw-graph-canvas-panel" aria-labelledby="scw-graph-canvas-heading"><div class="scw-knowledge-panel-head"><span>02 / FOCUS</span><h3 id="scw-graph-canvas-heading">Relationship neighborhood</h3></div><svg class="scw-graph-svg" data-scw-graph-svg role="img" aria-label="Focused Workspace knowledge graph neighborhood"></svg><div class="scw-graph-detail" data-scw-graph-detail></div></section>
                    <aside class="scw-graph-relations-panel" aria-labelledby="scw-graph-relations-heading"><div class="scw-knowledge-panel-head"><span>03 / RELATIONSHIPS</span><h3 id="scw-graph-relations-heading">Why this node is connected</h3></div><div class="scw-graph-relations" data-scw-graph-relations></div></aside>
                </div>
                <div class="scw-knowledge-boundary" role="note"><strong>Inspectable graph, not inferred truth</strong><span>Workspace builds this graph locally from explicit project containment, provenance, traceability, research evidence links, analysis inputs, decision inputs, and same-source matches. It does not use semantic embeddings, a server graph database, or hidden relationship inference.</span></div>
            </section>

            <section class="scw-activity-intelligence" data-scw-workspace-section="activity" hidden aria-labelledby="scw-activity-intelligence-title">
                <div class="scw-activity-intelligence-head">
                    <div><div class="scw-editorial-kicker">WORKFLOW &amp; ACTIVITY INTELLIGENCE</div><h2 id="scw-activity-intelligence-title">See what changed, what needs attention, and what comes next.</h2><p>This view derives transparent signals from the work already stored on this device. It does not calculate a productivity score, monitor behavior outside Workspace, or mark work complete automatically.</p></div>
                    <div class="scw-activity-intelligence-boundary"><strong>Inspectable, not surveillant</strong><span>Every signal states the project condition that produced it. Dismissal is user-controlled and stays on this device.</span></div>
                </div>
                <div class="scw-activity-intelligence-metrics" aria-label="Workflow and activity metrics">
                    <div><strong data-scw-activity-metric-projects>0</strong><span>active projects</span></div>
                    <div><strong data-scw-activity-metric-actions>0</strong><span>open next actions</span></div>
                    <div><strong data-scw-activity-metric-signals>0</strong><span>attention signals</span></div>
                    <div><strong data-scw-activity-metric-changes>0</strong><span>recent changes</span></div>
                </div>
                <div class="scw-activity-intelligence-toolbar">
                    <label><span>Project</span><select data-scw-activity-project><option value="all">All projects</option></select></label>
                    <label><span>Activity window</span><select data-scw-activity-window><option value="7">7 days</option><option value="30">30 days</option><option value="90">90 days</option></select></label>
                    <label><span>Stale after</span><select data-scw-activity-stale><option value="7">7 days</option><option value="14">14 days</option><option value="30">30 days</option></select></label>
                    <label><span>Signal</span><select data-scw-activity-signal><option value="all">All signals</option><option value="workflow">Workflow</option><option value="research">Research</option><option value="analysis">Analysis</option><option value="decision">Decision</option><option value="traceability">Traceability</option><option value="handoff">Handoffs</option><option value="briefing">Briefing</option><option value="collaboration">Collaboration</option><option value="institutional">Institutional handoff</option><option value="stale">Stale work</option></select></label>
                </div>
                <div class="scw-activity-intelligence-grid">
                    <section class="scw-activity-intelligence-panel" aria-labelledby="scw-next-actions-heading">
                        <div class="scw-knowledge-panel-head"><span>01 / NEXT</span><h3 id="scw-next-actions-heading">Next actions you control</h3></div>
                        <form class="scw-next-action-form" data-scw-next-action-form>
                            <label><span>Action</span><input type="text" name="title" maxlength="240" required placeholder="What needs to happen next?"></label>
                            <label><span>Project</span><select name="projectId" data-scw-next-action-project><option value="">Choose project</option></select></label>
                            <label><span>Priority</span><select name="priority"><option value="normal">Normal</option><option value="high">High</option><option value="low">Low</option></select></label>
                            <label><span>Due date <em>optional</em></span><input type="date" name="dueDate"></label>
                            <button class="scw-button" type="submit">Add next action</button>
                        </form>
                        <div class="scw-next-action-list" data-scw-next-action-list></div>
                    </section>
                    <section class="scw-activity-intelligence-panel" aria-labelledby="scw-attention-heading">
                        <div class="scw-knowledge-panel-head"><span>02 / ATTENTION</span><h3 id="scw-attention-heading">Explainable attention signals</h3></div>
                        <div class="scw-attention-list" data-scw-attention-list></div>
                        <button class="scw-text-button" type="button" data-scw-activity-restore-dismissed>Restore dismissed signals</button>
                    </section>
                    <section class="scw-activity-intelligence-panel" aria-labelledby="scw-workflow-status-heading">
                        <div class="scw-knowledge-panel-head"><span>03 / WORKFLOWS</span><h3 id="scw-workflow-status-heading">Active workflow status</h3></div>
                        <div class="scw-workflow-intelligence-list" data-scw-workflow-intelligence-list></div>
                    </section>
                    <section class="scw-activity-intelligence-panel" aria-labelledby="scw-activity-timeline-heading">
                        <div class="scw-knowledge-panel-head"><span>04 / TIMELINE</span><h3 id="scw-activity-timeline-heading">Recent local changes</h3></div>
                        <div class="scw-workspace-activity-timeline" data-scw-workspace-activity-timeline></div>
                    </section>
                </div>
                <div class="scw-activity-intelligence-note"><strong>No productivity score</strong><span>Workspace summarizes explicit project state, workflow progress, unresolved review conditions, handoff status, and user-created next actions. It does not rank people, infer effort, measure time-on-page, or send activity telemetry to a server.</span></div>
            </section>

            <section class="scw-version-history" data-scw-workspace-section="history" hidden aria-labelledby="scw-version-history-title">
                <div class="scw-version-history-head">
                    <div><div class="scw-editorial-kicker">PROJECT VERSION HISTORY</div><h2 id="scw-version-history-title">Create deliberate restore points before important changes.</h2><p>Restore points are named browser-local project snapshots with SHA-256 integrity fingerprints. They are separate from cloud sync and last-known-good Workspace recovery. Restoring never overwrites the current project; Workspace creates a new local copy instead.</p></div>
                    <div class="scw-version-history-boundary"><strong>Restore as copy</strong><span>The original project remains untouched. Restore-point snapshots are bounded local copies, not an automatic server version history.</span></div>
                </div>
                <div class="scw-version-history-metrics" aria-label="Project version history metrics">
                    <div><strong data-scw-history-metric-points>0</strong><span>restore points</span></div><div><strong data-scw-history-metric-projects>0</strong><span>projects represented</span></div><div><strong data-scw-history-metric-bytes>0 KB</strong><span>snapshot storage</span></div><div><strong data-scw-history-metric-newest>None</strong><span>newest point</span></div>
                </div>
                <div class="scw-version-history-grid">
                    <section class="scw-version-history-panel" aria-labelledby="scw-history-create-title"><div class="scw-knowledge-panel-head"><span>01 / CAPTURE</span><h3 id="scw-history-create-title">Create a named restore point</h3></div><form data-scw-history-form><label><span>Project</span><select name="projectId" data-scw-history-project required><option value="">Choose project</option></select></label><label><span>Label</span><input type="text" name="label" maxlength="120" required placeholder="Before major analysis revision"></label><label><span>Note <em>optional</em></span><textarea name="note" rows="3" maxlength="1200" placeholder="Why this state is worth preserving."></textarea></label><button class="scw-button scw-button-primary" type="submit">Create restore point</button></form><div class="scw-version-history-status" data-scw-history-status role="status" aria-live="polite">Restore points are stored only in this browser.</div></section>
                    <section class="scw-version-history-panel" aria-labelledby="scw-history-points-title"><div class="scw-knowledge-panel-head"><span>02 / RESTORE POINTS</span><h3 id="scw-history-points-title">Local snapshots</h3></div><label><span>Show</span><select data-scw-history-filter><option value="all">All projects</option></select></label><div class="scw-version-history-list" data-scw-history-list></div></section>
                </div>
                <section class="scw-version-history-events" aria-labelledby="scw-history-events-title"><div class="scw-knowledge-panel-head"><span>03 / HISTORY</span><h3 id="scw-history-events-title">Recent version-history activity</h3></div><div data-scw-history-events></div></section>
                <div class="scw-version-history-governance" role="note"><strong>Different recovery layers serve different purposes.</strong><span>Last-known-good recovery protects the entire browser Workspace from a damaged write. Account backup protects selected projects off-device. Sync compares local and cloud revisions. Restore points preserve named local project states for deliberate historical recovery.</span></div>
            </section>

            <section class="scw-interoperability" data-scw-workspace-section="interoperability" hidden aria-labelledby="scw-interoperability-title">
                <div class="scw-interoperability-head">
                    <div>
                        <div class="scw-kicker">IMPORT &amp; INTEROPERABILITY</div>
                        <h2 id="scw-interoperability-title">Bring outside work in without losing where it came from.</h2>
                        <p>Stage files locally, inspect what Workspace will create, then commit the import into a project. Imported artifacts receive explicit provenance and a file fingerprint; Workspace never silently replaces an existing canonical object.</p>
                    </div>
                </div>
                <div class="scw-interoperability-boundary" role="note"><strong>Review before commit</strong><span>Supported formats: JSON, CSV/TSV, Markdown, HTML, and plain text. Files are parsed in this browser. Nothing is uploaded by Workspace, and imported material is not treated as verified evidence merely because it was imported.</span></div>
                <div class="scw-interoperability-grid">
                    <section class="scw-interoperability-panel" aria-labelledby="scw-import-heading">
                        <div class="scw-knowledge-panel-head"><span>01 / STAGE</span><h3 id="scw-import-heading">Inspect an external file</h3></div>
                        <form data-scw-interoperability-form class="scw-interoperability-form">
                            <label><span>Target project</span><select data-scw-interoperability-project required><option value="">Choose project</option></select></label>
                            <label><span>External file</span><input data-scw-interoperability-file type="file" accept=".json,.csv,.tsv,.md,.markdown,.html,.htm,.txt,text/plain,text/csv,text/tab-separated-values,text/markdown,text/html,application/json"></label>
                            <button class="scw-button" type="submit">Stage file</button>
                        </form>
                        <div class="scw-interoperability-stage" data-scw-interoperability-stage><span>No file staged.</span></div>
                        <div class="scw-interoperability-actions">
                            <button class="scw-button scw-button-primary" type="button" data-scw-interoperability-commit disabled>Commit staged import</button>
                            <button class="scw-button" type="button" data-scw-interoperability-clear disabled>Clear</button>
                        </div>
                    </section>
                    <section class="scw-interoperability-panel" aria-labelledby="scw-interchange-heading">
                        <div class="scw-knowledge-panel-head"><span>02 / EXPORT</span><h3 id="scw-interchange-heading">Portable interchange package</h3></div>
                        <p>Export one project as a portable interoperability package containing canonical objects plus explicit object relationships that can be understood outside the live Workspace runtime.</p>
                        <label><span>Project</span><select data-scw-interoperability-export-project><option value="">Choose project</option></select></label>
                        <button class="scw-button" type="button" data-scw-interoperability-export>Export interchange JSON</button>
                        <div class="scw-interoperability-note"><strong>Canonical remains canonical</strong><span>An interchange export is a portable copy. Re-importing it creates new local object IDs when needed rather than overwriting existing project artifacts.</span></div>
                    </section>
                </div>
                <section class="scw-interoperability-history" aria-labelledby="scw-interoperability-history-heading">
                    <div class="scw-knowledge-panel-head"><span>03 / ACTIVITY</span><h3 id="scw-interoperability-history-heading">Recent interoperability activity</h3></div>
                    <div data-scw-interoperability-history></div>
                </section>
            </section>

            <section class="scw-collaboration" data-scw-workspace-section="collaboration" hidden aria-labelledby="scw-collaboration-title">
                <div class="scw-collaboration-head">
                    <div><div class="scw-editorial-kicker">COLLABORATION FOUNDATION</div><h2 id="scw-collaboration-title">Structured review without surrendering project ownership.</h2><p>Create a review request, send a privacy-minimized project copy, collect object-linked comments or suggestions, and bring feedback back to the source Workspace. v0.23.0 keeps collaboration asynchronous and file-based; it does not create a shared cloud project or server permission system.</p></div>
                </div>
                <div class="scw-collaboration-metrics" aria-label="Collaboration metrics">
                    <div><strong data-scw-collab-metric-sessions>0</strong><span>review sessions</span></div>
                    <div><strong data-scw-collab-metric-open>0</strong><span>open threads</span></div>
                    <div><strong data-scw-collab-metric-people>0</strong><span>contributors</span></div>
                    <div><strong data-scw-collab-metric-responses>0</strong><span>responses imported</span></div>
                </div>
                <div class="scw-collaboration-grid">
                    <section class="scw-collaboration-panel" aria-labelledby="scw-collab-profile-title">
                        <div class="scw-knowledge-panel-head"><span>01 / LOCAL IDENTITY</span><h3 id="scw-collab-profile-title">How you appear in review packages</h3></div>
                        <form class="scw-collaboration-form" data-scw-collab-profile-form>
                            <label><span>Display name or initials</span><input type="text" name="displayName" maxlength="120" placeholder="e.g. TA or Tariq Ahmad"></label>
                            <label><span>Default review role</span><select name="role"><option value="owner">Owner</option><option value="contributor">Contributor</option><option value="reviewer">Reviewer</option><option value="observer">Observer</option></select></label>
                            <button class="scw-button" type="submit">Save local review identity</button>
                        </form>
                        <p class="scw-collaboration-note">This label is stored on this device and included only when you explicitly export a review package. It is not an account directory or permission grant.</p>
                    </section>
                    <section class="scw-collaboration-panel" aria-labelledby="scw-collab-request-title">
                        <div class="scw-knowledge-panel-head"><span>02 / REQUEST</span><h3 id="scw-collab-request-title">Start structured review</h3></div>
                        <form class="scw-collaboration-form" data-scw-collab-request-form>
                            <label><span>Project</span><select name="projectId" data-scw-collab-project required><option value="">Choose project</option></select></label>
                            <label><span>Review title</span><input type="text" name="title" maxlength="200" required placeholder="e.g. Review evidence and decision rationale"></label>
                            <label><span>Review purpose</span><textarea name="purpose" rows="4" maxlength="2400" placeholder="What should the reviewer examine or challenge?"></textarea></label>
                            <label><span>Requested role</span><select name="requestedRole"><option value="reviewer">Reviewer</option><option value="contributor">Contributor</option><option value="observer">Observer</option></select></label>
                            <button class="scw-button scw-button-primary" type="submit">Create review request</button>
                        </form>
                    </section>
                </div>
                <div class="scw-collaboration-layout">
                    <section class="scw-collaboration-panel" aria-labelledby="scw-collab-sessions-title"><div class="scw-knowledge-panel-head"><span>03 / SESSIONS</span><h3 id="scw-collab-sessions-title">Review sessions</h3></div><div class="scw-collaboration-sessions" data-scw-collab-session-list></div></section>
                    <section class="scw-collaboration-panel" aria-labelledby="scw-collab-active-title"><div class="scw-knowledge-panel-head"><span>04 / REVIEW</span><h3 id="scw-collab-active-title">Comments, suggestions &amp; questions</h3></div><div class="scw-collaboration-active" data-scw-collab-active></div><form class="scw-collaboration-form" data-scw-collab-thread-form hidden><label><span>Kind</span><select name="kind"><option value="comment">Comment</option><option value="suggestion">Suggestion</option><option value="question">Question</option></select></label><label><span>Project object <em>optional</em></span><select name="objectId" data-scw-collab-object><option value="">Project-level review</option></select></label><label><span>Review note</span><textarea name="body" rows="5" maxlength="5000" required></textarea></label><button class="scw-button" type="submit">Add review thread</button></form><div class="scw-collaboration-threads" data-scw-collab-thread-list></div></section>
                </div>
                <section class="scw-collaboration-exchange" aria-labelledby="scw-collab-exchange-title">
                    <div class="scw-knowledge-panel-head"><span>05 / PORTABLE REVIEW</span><h3 id="scw-collab-exchange-title">Move a review request or response deliberately.</h3></div>
                    <div class="scw-collaboration-actions"><button class="scw-button" type="button" data-scw-collab-export-request>Export review request</button><button class="scw-button" type="button" data-scw-collab-export-response>Export review response</button><button class="scw-button" type="button" data-scw-collab-import>Import review package</button><input type="file" accept="application/json,.json" data-scw-collab-file hidden></div>
                    <div class="scw-collaboration-stage" data-scw-collab-stage><span>No review package staged.</span></div>
                    <div class="scw-collaboration-stage-actions"><button class="scw-button scw-button-primary" type="button" data-scw-collab-commit disabled>Commit staged review package</button><button class="scw-button" type="button" data-scw-collab-clear disabled>Clear</button></div>
                    <div class="scw-collaboration-history" data-scw-collab-history></div>
                </section>
                <div class="scw-collaboration-boundary" role="note"><strong>Collaboration foundation, not a shared tenant</strong><span>Roles in v0.23.0 continue to describe review responsibility inside portable packages; they are not server-enforced permissions. Imported comments never edit the source project automatically. Live co-editing, organization membership, shared cloud storage, audit-grade access control, and administrative governance remain outside this personal Workspace release.</span></div>
            </section>

            <section class="scw-institutional" data-scw-workspace-section="institutional" hidden aria-labelledby="scw-institutional-title">
                <div class="scw-institutional-head">
                    <div><div class="scw-editorial-kicker">INSTITUTIONAL HANDOFF</div><h2 id="scw-institutional-title">Promote mature work into governed institutional operations.</h2><p>Prepare an explicit copy of selected Workspace material for Catalyst Intelligence while preserving the personal Workspace as an independent source record. Promotion is deliberate, inspectable, and does not convert the local project in place.</p></div>
                    <div class="scw-institutional-boundary"><strong>Copy into institution</strong><span>The source Workspace remains device-local and independently owned. Institutional governance begins only after the receiving system accepts the handoff.</span></div>
                </div>
                <div class="scw-institutional-metrics" aria-label="Institutional handoff metrics">
                    <div><strong data-scw-institutional-metric-total>0</strong><span>handoffs</span></div>
                    <div><strong data-scw-institutional-metric-exported>0</strong><span>exported</span></div>
                    <div><strong data-scw-institutional-metric-received>0</strong><span>receipts</span></div>
                    <div><strong data-scw-institutional-metric-accepted>0</strong><span>accepted</span></div>
                </div>
                <div class="scw-institutional-grid">
                    <section class="scw-institutional-panel" aria-labelledby="scw-institutional-prepare-title">
                        <div class="scw-knowledge-panel-head"><span>01 / PREPARE</span><h3 id="scw-institutional-prepare-title">Define the institutional promotion</h3></div>
                        <form class="scw-institutional-form" data-scw-institutional-form>
                            <label><span>Project</span><select name="projectId" data-scw-institutional-project required><option value="">Choose project</option></select></label>
                            <label><span>Receiving organization / institutional workspace</span><input type="text" name="organizationLabel" maxlength="200" required placeholder="e.g. Client organization or internal program"></label>
                            <label><span>Purpose</span><textarea name="purpose" rows="4" maxlength="3000" required placeholder="Why should this work move into an institutional environment?"></textarea></label>
                            <fieldset class="scw-institutional-scope"><legend>Promotion scope</legend><div data-scw-institutional-object-scope><span>Choose a project to review its canonical objects.</span></div></fieldset>
                            <div class="scw-institutional-acknowledgements">
                                <label><input type="checkbox" name="copyModel" required> I understand this creates a separate institutional copy; the personal Workspace project remains independent.</label>
                                <label><input type="checkbox" name="institutionalGovernance" required> I understand institutional governance begins only after the receiving system accepts the handoff.</label>
                                <label><input type="checkbox" name="sharingReviewed" required> I have reviewed the selected material and intend to share it with the named organization.</label>
                            </div>
                            <button class="scw-button scw-button-primary" type="submit">Prepare institutional handoff</button>
                        </form>
                    </section>
                    <section class="scw-institutional-panel" aria-labelledby="scw-institutional-handoffs-title">
                        <div class="scw-knowledge-panel-head"><span>02 / HANDOFFS</span><h3 id="scw-institutional-handoffs-title">Promotion ledger</h3></div>
                        <div class="scw-institutional-list" data-scw-institutional-list></div>
                    </section>
                </div>
                <section class="scw-institutional-active" aria-labelledby="scw-institutional-active-title">
                    <div class="scw-knowledge-panel-head"><span>03 / READINESS &amp; EXPORT</span><h3 id="scw-institutional-active-title">Inspect before promotion</h3></div>
                    <div data-scw-institutional-active><div class="scw-institutional-empty">Prepare or open an institutional handoff to inspect scope and readiness.</div></div>
                    <div class="scw-institutional-readiness" data-scw-institutional-readiness></div>
                    <div class="scw-institutional-actions"><button class="scw-button scw-button-primary" type="button" data-scw-institutional-export disabled>Export promotion package</button><button class="scw-button" type="button" data-scw-institutional-close disabled>Close handoff</button></div>
                </section>
                <section class="scw-institutional-receipt" aria-labelledby="scw-institutional-receipt-title">
                    <div class="scw-knowledge-panel-head"><span>04 / RECEIPT</span><h3 id="scw-institutional-receipt-title">Record institutional acceptance without rewriting the source project.</h3></div>
                    <div class="scw-institutional-actions"><button class="scw-button" type="button" data-scw-institutional-import>Import institutional receipt</button><input type="file" accept="application/json,.json" data-scw-institutional-file hidden></div>
                    <div class="scw-institutional-stage" data-scw-institutional-stage><span>No institutional receipt staged.</span></div>
                    <div class="scw-institutional-actions"><button class="scw-button scw-button-primary" type="button" data-scw-institutional-commit disabled>Commit receipt</button><button class="scw-button" type="button" data-scw-institutional-clear disabled>Clear</button></div>
                    <div class="scw-institutional-history" data-scw-institutional-history></div>
                </section>
                <div class="scw-institutional-governance" role="note"><strong>Workspace does not become the institution.</strong><span>v0.23.0 preserves the governed handoff contract for Catalyst Intelligence while hardening the surrounding Workspace runtime. It does not create organization membership, server permissions, shared cloud storage, automatic ingestion, or an institutional tenant inside Workspace.</span></div>
            </section>

            <section class="scw-share" data-scw-workspace-section="share" hidden aria-labelledby="scw-share-title">
                <div class="scw-share-head">
                    <div><div class="scw-editorial-kicker">SHARE &amp; PORTABLE PROJECTS</div><h2 id="scw-share-title">Move a complete project without turning Workspace into a cloud service.</h2><p>Create a deliberate portable copy for another person or device, verify package integrity on import, or export a static review copy that can be read without Workspace.</p></div>
                    <div class="scw-share-boundary"><strong>Portable copy, not sync</strong><span>Workspace does not create public share links, upload projects, or establish live collaboration. Device identity, account/session metadata, handoff state, and recent-tool history are excluded.</span></div>
                </div>
                <div class="scw-share-grid">
                    <section class="scw-share-panel" aria-labelledby="scw-share-export-heading">
                        <div class="scw-knowledge-panel-head"><span>01 / PACKAGE</span><h3 id="scw-share-export-heading">Create a portable project</h3></div>
                        <label><span>Project</span><select data-scw-share-project><option value="">Choose project</option></select></label>
                        <div class="scw-share-options">
                            <label><input type="checkbox" data-scw-share-include-archived> Include archived objects</label>
                            <label><input type="checkbox" data-scw-share-include-activity> Include project activity history</label>
                            <label><input type="checkbox" data-scw-share-include-ai> Include Responsible AI review history</label>
                        </div>
                        <div class="scw-share-actions"><button class="scw-button scw-button-primary" type="button" data-scw-share-export>Export portable project</button><button class="scw-button" type="button" data-scw-share-review>Export review copy HTML</button></div>
                        <div class="scw-share-note"><strong>Privacy-minimized by default</strong><span>Portable JSON preserves the reasoning structures needed to continue the project. Operational browser metadata is stripped. Activity and AI review history are opt-in because they may contain context that is unnecessary for sharing.</span></div>
                    </section>
                    <section class="scw-share-panel" aria-labelledby="scw-share-import-heading">
                        <div class="scw-knowledge-panel-head"><span>02 / RECEIVE</span><h3 id="scw-share-import-heading">Import a portable project as a copy</h3></div>
                        <label><span>Portable project JSON</span><input data-scw-share-file type="file" accept=".json,application/json"></label>
                        <div class="scw-share-stage" data-scw-share-stage><span>No portable project staged.</span></div>
                        <div class="scw-share-actions"><button class="scw-button scw-button-primary" type="button" data-scw-share-import disabled>Import as copy</button><button class="scw-button" type="button" data-scw-share-clear disabled>Clear</button></div>
                        <div class="scw-share-note"><strong>No overwrite</strong><span>Imported packages receive a new local project ID and are rebound to this device. Their internal canonical object relationships are preserved, but they cannot replace an existing local project automatically.</span></div>
                    </section>
                </div>
                <section class="scw-share-history" aria-labelledby="scw-share-history-heading"><div class="scw-knowledge-panel-head"><span>03 / ACTIVITY</span><h3 id="scw-share-history-heading">Recent portable sharing activity</h3></div><div data-scw-share-history></div></section>
            </section>

            <section class="scw-active-project" data-scw-active-project hidden aria-labelledby="scw-active-title">
                <div class="scw-active-header">
                    <div>
                        <div class="scw-kicker">ACTIVE PROJECT</div>
                        <h2 id="scw-active-title" data-scw-active-heading>Project</h2>
                    </div>
                    <div class="scw-save-state" data-scw-save-state>Saved on this device</div>
                </div>

                <nav class="scw-project-mode-nav" aria-label="Project workspace modes" data-scw-project-mode-nav>
                    <button type="button" class="is-active" data-scw-project-mode="overview" aria-pressed="true">Overview</button>
                    <button type="button" data-scw-project-mode="guide" aria-pressed="false">Guide</button>
                    <button type="button" data-scw-project-mode="research" aria-pressed="false">Research</button>
                    <button type="button" data-scw-project-mode="analysis" aria-pressed="false">Analysis</button>
                    <button type="button" data-scw-project-mode="decision" aria-pressed="false">Decisions</button>
                    <button type="button" data-scw-project-mode="canvas" aria-pressed="false">Canvas</button>
                    <button type="button" data-scw-project-mode="traceability" aria-pressed="false">Traceability</button>
                    <button type="button" data-scw-project-mode="assist" aria-pressed="false">Assist</button>
                    <button type="button" data-scw-project-mode="briefing" aria-pressed="false">Briefing</button>
                    <button type="button" data-scw-project-mode="objects" aria-pressed="false">Objects</button>
                </nav>

                <div class="scw-project-editor" data-scw-project-panel="overview">
                    <div class="scw-project-fields">
                        <label><span>Project name</span><input type="text" maxlength="120" data-scw-project-title></label>
                        <label><span>Description</span><textarea rows="3" maxlength="600" data-scw-project-description></textarea></label>
                        <div class="scw-field-row">
                            <label><span>Status</span><select data-scw-project-status><option value="active">Active</option><option value="paused">Paused</option><option value="complete">Complete</option></select></label>
                            <div class="scw-project-id"><span>PROJECT ID</span><code data-scw-project-id></code></div>
                        </div>
                        <label><span>Project notes</span><textarea class="scw-notes" rows="8" maxlength="20000" data-scw-project-notes placeholder="Capture working notes, questions, constraints, decisions, or next steps."></textarea></label>
                    </div>

                    <aside class="scw-project-ops" aria-label="Project operations">
                        <div class="scw-op-group">
                            <span class="scw-op-label">PROJECT</span>
                            <div class="scw-project-stat"><strong data-scw-object-total>0</strong><span>objects</span></div>
                            <button class="scw-op" type="button" data-scw-pin>Pin project</button>
                            <button class="scw-op" type="button" data-scw-duplicate>Duplicate</button>
                            <button class="scw-op" type="button" data-scw-export>Export project JSON</button>
                            <button class="scw-op" type="button" data-scw-archive>Archive</button>
                            <button class="scw-op scw-op-danger" type="button" data-scw-delete>Delete from this device</button>
                        </div>
                        <div class="scw-op-group">
                            <span class="scw-op-label">ACTIVITY</span>
                            <div class="scw-activity" data-scw-activity></div>
                        </div>
                    </aside>
                </div>



                <section class="scw-workflows" data-scw-project-panel="guide" aria-labelledby="scw-workflows-title">
                    <div class="scw-workflows-head">
                        <div>
                            <div class="scw-kicker">TEMPLATES &amp; GUIDED WORKFLOWS</div>
                            <h3 id="scw-workflows-title">Add structure when the work benefits from it.</h3>
                            <p>Start from a visible method for research, evidence review, analysis, decisions, systems mapping, or publication preparation. Templates guide the sequence; they do not create hidden findings, complete steps automatically, or prevent blank-project work.</p>
                        </div>
                    </div>
                    <div class="scw-workflow-metrics" aria-label="Guided workflow metrics">
                        <div><strong data-scw-workflow-metric-runs>0</strong><span>workflow runs</span></div>
                        <div><strong data-scw-workflow-metric-steps>0</strong><span>in progress</span></div>
                        <div><strong data-scw-workflow-metric-complete>0</strong><span>steps complete</span></div>
                    </div>
                    <div class="scw-workflow-grid">
                        <section class="scw-workflow-panel scw-workflow-panel-wide" aria-labelledby="scw-workflow-templates-heading">
                            <div class="scw-workflow-panel-head"><span>01 / TEMPLATES</span><h4 id="scw-workflow-templates-heading">Choose a method, not a locked tier.</h4></div>
                            <div class="scw-workflow-template-list" data-scw-workflow-template-list></div>
                        </section>
                        <section class="scw-workflow-panel" aria-labelledby="scw-workflow-runs-heading">
                            <div class="scw-workflow-panel-head"><span>02 / RUNS</span><h4 id="scw-workflow-runs-heading">Keep more than one method in the same project.</h4></div>
                            <div class="scw-workflow-active"><span>ACTIVE WORKFLOW</span><strong data-scw-workflow-active>No active guided workflow selected.</strong></div>
                            <div class="scw-workflow-run-list" data-scw-workflow-run-list></div>
                        </section>
                        <section class="scw-workflow-panel scw-workflow-panel-wide" aria-labelledby="scw-workflow-steps-heading">
                            <div class="scw-workflow-panel-head"><span>03 / STEPS</span><h4 id="scw-workflow-steps-heading">Progress remains explicit and human-controlled.</h4></div>
                            <p class="scw-workflow-note">Open a step to move into the relevant Workspace mode. Mark completion yourself; Workspace never interprets activity as approval or completion.</p>
                            <div class="scw-workflow-step-list" data-scw-workflow-step-list></div>
                        </section>
                    </div>
                </section>

                <section class="scw-research" data-scw-project-panel="research" aria-labelledby="scw-research-title">
                    <div class="scw-research-head">
                        <div>
                            <div class="scw-kicker">RESEARCH WORKSPACE</div>
                            <h3 id="scw-research-title">From question to evidence-backed claim.</h3>
                            <p>Frame inquiry, capture sources, manage a reading queue, extract evidence, and test claims while retaining stable links to Workspace Objects.</p>
                        </div>
                        <div class="scw-research-launchers" aria-label="Research tools">
                            <a class="scw-button" data-scw-tool="research-librarian" href="<?php echo esc_url(home_url('/research-librarian/')); ?>"><strong>Research Librarian</strong></a>
                            <a class="scw-button" data-scw-tool="knowledge-library" href="<?php echo esc_url(home_url('/knowledge-libraries/')); ?>"><strong>Knowledge Library</strong></a>
                        </div>
                    </div>

                    <div class="scw-research-metrics" aria-label="Research project metrics">
                        <div><strong data-scw-research-metric-questions>0</strong><span>open questions</span></div>
                        <div><strong data-scw-research-metric-sources>0</strong><span>sources</span></div>
                        <div><strong data-scw-research-metric-evidence>0</strong><span>evidence objects</span></div>
                        <div><strong data-scw-research-metric-claims>0</strong><span>supported claims</span></div>
                    </div>

                    <div class="scw-research-grid">
                        <section class="scw-research-panel scw-research-panel-wide" aria-labelledby="scw-research-question-heading">
                            <div class="scw-research-panel-head"><span>01 / QUESTIONS</span><h4 id="scw-research-question-heading">Research questions</h4></div>
                            <div class="scw-research-active"><span>ACTIVE QUESTION</span><strong data-scw-research-active-question>No active research question selected.</strong></div>
                            <form class="scw-research-form scw-research-form-question" data-scw-research-question-form>
                                <label><span>Question</span><input type="text" name="question" maxlength="1000" required placeholder="What are we trying to establish?"></label>
                                <label><span>Priority</span><select name="priority"><option value="normal">Normal</option><option value="high">High</option><option value="low">Low</option></select></label>
                                <button class="scw-button" type="submit">Add question</button>
                            </form>
                            <div class="scw-research-list" data-scw-research-question-list></div>
                        </section>

                        <section class="scw-research-panel" aria-labelledby="scw-research-source-heading">
                            <div class="scw-research-panel-head"><span>02 / SOURCES</span><h4 id="scw-research-source-heading">Capture & reading queue</h4></div>
                            <form class="scw-research-form" data-scw-research-source-form>
                                <label><span>Source title</span><input type="text" name="title" maxlength="160" required></label>
                                <div class="scw-research-form-row"><label><span>Source type</span><select name="sourceType"><option value="web">Web</option><option value="library">Library</option><option value="manual">Manual</option><option value="dataset">Dataset</option><option value="tool">Tool</option></select></label><label><span>URL</span><input type="url" name="url" maxlength="2000" placeholder="https://"></label></div>
                                <label><span>Summary</span><textarea name="summary" rows="3" maxlength="1200" placeholder="Why is this source relevant?"></textarea></label>
                                <label><span>Tags</span><input type="text" name="tags" placeholder="policy, grid, evidence"></label>
                                <button class="scw-button" type="submit">Capture source</button>
                            </form>
                            <div class="scw-research-list" data-scw-research-reading-list></div>
                        </section>

                        <section class="scw-research-panel" aria-labelledby="scw-research-evidence-heading">
                            <div class="scw-research-panel-head"><span>03 / EVIDENCE</span><h4 id="scw-research-evidence-heading">Extract evidence</h4></div>
                            <form class="scw-research-form" data-scw-research-evidence-form>
                                <label><span>Evidence title</span><input type="text" name="title" maxlength="160" required></label>
                                <label><span>Linked source</span><select name="sourceObjectId" data-scw-research-evidence-source><option value="">No linked source</option></select></label>
                                <label><span>Summary</span><textarea name="summary" rows="2" maxlength="1200"></textarea></label>
                                <label><span>Evidence</span><textarea name="content" rows="6" maxlength="50000" required placeholder="Capture the observation, passage, finding, or result—not an unsupported conclusion."></textarea></label>
                                <button class="scw-button" type="submit">Create evidence object</button>
                            </form>
                        </section>

                        <section class="scw-research-panel scw-research-panel-wide" aria-labelledby="scw-research-claim-heading">
                            <div class="scw-research-panel-head"><span>04 / CLAIMS</span><h4 id="scw-research-claim-heading">Claims & evidence</h4></div>
                            <form class="scw-research-form scw-research-form-claim" data-scw-research-claim-form>
                                <label><span>Claim</span><input type="text" name="claim" maxlength="2000" required placeholder="What does the current evidence support or challenge?"></label>
                                <button class="scw-button" type="submit">Add claim</button>
                            </form>
                            <div class="scw-research-linker"><label><span>LINK EVIDENCE TO ACTIVE CLAIM</span><select data-scw-research-claim-evidence><option value="">Choose evidence</option></select></label><button class="scw-button" type="button" data-scw-research-link-evidence>Link evidence</button></div>
                            <div class="scw-research-list scw-research-claims" data-scw-research-claim-list></div>
                        </section>
                    </div>
                </section>


                <section class="scw-analysis" data-scw-project-panel="analysis" aria-labelledby="scw-analysis-title">
                    <div class="scw-analysis-head">
                        <div>
                            <div class="scw-kicker">ANALYSIS WORKSPACE</div>
                            <h3 id="scw-analysis-title">From evidence to structured analytical finding.</h3>
                            <p>Frame analytical questions, register datasets and variables, surface assumptions, record methods and comparisons, and connect findings back to Workspace evidence and analysis objects.</p>
                        </div>
                        <div class="scw-analysis-launchers" aria-label="Analysis tools">
                            <a class="scw-button" data-scw-tool="analytics-r" href="<?php echo esc_url(home_url('/platform/catalyst-analytics-r/')); ?>"><strong>Analytics R</strong></a>
                            <a class="scw-button" data-scw-tool="workbench" href="<?php echo esc_url(home_url('/platform/workbench/')); ?>"><strong>Workbench</strong></a>
                            <a class="scw-button" data-scw-tool="catalyst-data" href="<?php echo esc_url(home_url('/platform/catalyst-data/')); ?>"><strong>Catalyst Data</strong></a>
                            <a class="scw-button" data-scw-tool="site-intelligence" href="<?php echo esc_url(home_url('/platform/site-intelligence/')); ?>"><strong>Site Intelligence</strong></a>
                        </div>
                    </div>

                    <div class="scw-analysis-metrics" aria-label="Analysis project metrics">
                        <div><strong data-scw-analysis-metric-questions>0</strong><span>open questions</span></div>
                        <div><strong data-scw-analysis-metric-datasets>0</strong><span>datasets</span></div>
                        <div><strong data-scw-analysis-metric-analyses>0</strong><span>analysis objects</span></div>
                        <div><strong data-scw-analysis-metric-findings>0</strong><span>supported findings</span></div>
                    </div>

                    <div class="scw-analysis-grid">
                        <section class="scw-analysis-panel scw-analysis-panel-wide" aria-labelledby="scw-analysis-question-heading">
                            <div class="scw-analysis-panel-head"><span>01 / QUESTIONS</span><h4 id="scw-analysis-question-heading">Analysis questions</h4></div>
                            <div class="scw-analysis-active"><span>ACTIVE QUESTION</span><strong data-scw-analysis-active-question>No active analysis question selected.</strong></div>
                            <form class="scw-analysis-form scw-analysis-form-question" data-scw-analysis-question-form>
                                <label><span>Question</span><input type="text" name="question" maxlength="1200" required placeholder="What relationship, difference, pattern, or outcome are we testing?"></label>
                                <label><span>Priority</span><select name="priority"><option value="normal">Normal</option><option value="high">High</option><option value="low">Low</option></select></label>
                                <button class="scw-button" type="submit">Add question</button>
                            </form>
                            <div class="scw-analysis-list" data-scw-analysis-question-list></div>
                        </section>

                        <section class="scw-analysis-panel" aria-labelledby="scw-analysis-data-heading">
                            <div class="scw-analysis-panel-head"><span>02 / DATA</span><h4 id="scw-analysis-data-heading">Datasets &amp; variables</h4></div>
                            <form class="scw-analysis-form" data-scw-analysis-dataset-form>
                                <label><span>Dataset title</span><input type="text" name="title" maxlength="160" required></label>
                                <label><span>Source URL</span><input type="url" name="url" maxlength="2000" placeholder="https://"></label>
                                <label><span>Summary</span><textarea name="summary" rows="3" maxlength="1200" placeholder="Scope, coverage, grain, or analytical relevance."></textarea></label>
                                <label><span>Tags</span><input type="text" name="tags" placeholder="energy, country, panel"></label>
                                <button class="scw-button" type="submit">Register dataset</button>
                            </form>
                            <div class="scw-analysis-list" data-scw-analysis-dataset-list></div>
                            <form class="scw-analysis-form scw-analysis-subform" data-scw-analysis-variable-form>
                                <div class="scw-analysis-form-row"><label><span>Variable</span><input type="text" name="name" maxlength="160" required></label><label><span>Role</span><select name="role"><option value="outcome">Outcome</option><option value="input">Input</option><option value="control">Control</option><option value="parameter">Parameter</option><option value="indicator">Indicator</option></select></label></div>
                                <div class="scw-analysis-form-row"><label><span>Unit</span><input type="text" name="unit" maxlength="80"></label><label><span>Definition</span><input type="text" name="definition" maxlength="1200"></label></div>
                                <button class="scw-button" type="submit">Add variable</button>
                            </form>
                            <div class="scw-analysis-list" data-scw-analysis-variable-list></div>
                        </section>

                        <section class="scw-analysis-panel" aria-labelledby="scw-analysis-method-heading">
                            <div class="scw-analysis-panel-head"><span>03 / METHOD</span><h4 id="scw-analysis-method-heading">Assumptions &amp; methods</h4></div>
                            <form class="scw-analysis-form" data-scw-analysis-assumption-form>
                                <label><span>Assumption</span><textarea name="assumption" rows="3" maxlength="2000" required placeholder="What must be true, held constant, or accepted for this analysis?"></textarea></label>
                                <button class="scw-button" type="submit">Add assumption</button>
                            </form>
                            <div class="scw-analysis-list" data-scw-analysis-assumption-list></div>
                            <form class="scw-analysis-form scw-analysis-subform" data-scw-analysis-method-form>
                                <label><span>Method name</span><input type="text" name="name" maxlength="200" required placeholder="Comparative trend analysis"></label>
                                <div class="scw-analysis-form-row"><label><span>Method type</span><select name="type"><option value="descriptive">Descriptive</option><option value="comparative">Comparative</option><option value="statistical">Statistical</option><option value="modeling">Modeling</option><option value="scenario">Scenario</option><option value="sensitivity">Sensitivity</option><option value="other">Other</option></select></label><label><span>Dataset</span><select name="datasetObjectId" data-scw-analysis-method-dataset><option value="">No linked dataset</option></select></label></div>
                                <label><span>Description</span><textarea name="description" rows="4" maxlength="3000" placeholder="Method, transformations, tests, model form, or calculation logic."></textarea></label>
                                <button class="scw-button" type="submit">Register method &amp; analysis object</button>
                            </form>
                            <div class="scw-analysis-list" data-scw-analysis-method-list></div>
                        </section>

                        <section class="scw-analysis-panel scw-analysis-panel-wide" aria-labelledby="scw-analysis-findings-heading">
                            <div class="scw-analysis-panel-head"><span>04 / INTERPRETATION</span><h4 id="scw-analysis-findings-heading">Comparisons &amp; findings</h4></div>
                            <div class="scw-analysis-two-col">
                                <div>
                                    <form class="scw-analysis-form" data-scw-analysis-comparison-form>
                                        <label><span>Comparison label</span><input type="text" name="label" maxlength="200" required placeholder="Baseline vs intervention"></label>
                                        <div class="scw-analysis-form-row"><label><span>Baseline</span><input type="text" name="baseline" maxlength="800"></label><label><span>Alternative</span><input type="text" name="alternative" maxlength="800"></label></div>
                                        <div class="scw-analysis-form-row"><label><span>Metric</span><input type="text" name="metric" maxlength="240"></label><label><span>Result</span><input type="text" name="result" maxlength="1200"></label></div>
                                        <label><span>Interpretation</span><textarea name="interpretation" rows="3" maxlength="2000"></textarea></label>
                                        <button class="scw-button" type="submit">Add comparison</button>
                                    </form>
                                    <div class="scw-analysis-list" data-scw-analysis-comparison-list></div>
                                </div>
                                <div>
                                    <form class="scw-analysis-form" data-scw-analysis-finding-form>
                                        <label><span>Finding</span><textarea name="finding" rows="4" maxlength="3000" required placeholder="What does the analysis currently show?"></textarea></label>
                                        <div class="scw-analysis-form-row"><label><span>Status</span><select name="status"><option value="preliminary">Preliminary</option><option value="supported">Supported</option><option value="contested">Contested</option></select></label><label><span>Evidence</span><select name="evidenceObjectId" data-scw-analysis-finding-evidence><option value="">No linked evidence</option></select></label></div>
                                        <button class="scw-button" type="submit">Record finding</button>
                                    </form>
                                    <div class="scw-analysis-list" data-scw-analysis-finding-list></div>
                                </div>
                            </div>
                        </section>
                    </div>
                </section>


                <section class="scw-decision" data-scw-project-panel="decision" aria-labelledby="scw-decision-title">
                    <div class="scw-decision-head">
                        <div>
                            <div class="scw-kicker">DECISION WORKSPACE</div>
                            <h3 id="scw-decision-title">From analysis to accountable decision.</h3>
                            <p>Frame decisions, compare options against explicit criteria, record assessments and risks, and preserve the selected course, rationale, confidence, and supporting evidence as a durable Workspace Decision object.</p>
                        </div>
                        <div class="scw-decision-launchers" aria-label="Decision tools">
                            <a class="scw-button" data-scw-tool="decision-studio" href="<?php echo esc_url(home_url('/platform/decision-studio/')); ?>"><strong>Decision Studio</strong></a>
                            <a class="scw-button" data-scw-tool="catalyst-canvas" href="<?php echo esc_url(home_url('/platform/catalyst-canvas/')); ?>"><strong>Catalyst Canvas</strong></a>
                        </div>
                    </div>

                    <div class="scw-decision-metrics" aria-label="Decision project metrics">
                        <div><strong data-scw-decision-metric-open>0</strong><span>open decisions</span></div>
                        <div><strong data-scw-decision-metric-options>0</strong><span>options</span></div>
                        <div><strong data-scw-decision-metric-criteria>0</strong><span>criteria</span></div>
                        <div><strong data-scw-decision-metric-decided>0</strong><span>decided</span></div>
                    </div>

                    <div class="scw-decision-grid">
                        <section class="scw-decision-panel scw-decision-panel-wide" aria-labelledby="scw-decision-frame-heading">
                            <div class="scw-decision-panel-head"><span>01 / FRAME</span><h4 id="scw-decision-frame-heading">Decision records</h4></div>
                            <div class="scw-decision-active"><span>ACTIVE DECISION</span><strong data-scw-decision-active>No active decision selected.</strong></div>
                            <form class="scw-decision-form scw-decision-form-frame" data-scw-decision-form>
                                <label><span>Decision title</span><input type="text" name="title" maxlength="200" required placeholder="Choose an implementation pathway"></label>
                                <label><span>Decision question</span><input type="text" name="question" maxlength="2000" required placeholder="What exactly must be decided?"></label>
                                <button class="scw-button" type="submit">Create decision</button>
                            </form>
                            <div class="scw-decision-list" data-scw-decision-list></div>
                        </section>

                        <section class="scw-decision-panel" aria-labelledby="scw-decision-options-heading">
                            <div class="scw-decision-panel-head"><span>02 / OPTIONS</span><h4 id="scw-decision-options-heading">Options &amp; criteria</h4></div>
                            <form class="scw-decision-form" data-scw-decision-option-form>
                                <label><span>Option</span><input type="text" name="label" maxlength="200" required></label>
                                <label><span>Description</span><textarea name="description" rows="3" maxlength="2400"></textarea></label>
                                <button class="scw-button" type="submit">Add option</button>
                            </form>
                            <div class="scw-decision-list" data-scw-decision-option-list></div>
                            <form class="scw-decision-form scw-decision-subform" data-scw-decision-criterion-form>
                                <div class="scw-decision-form-row"><label><span>Criterion</span><input type="text" name="label" maxlength="200" required></label><label><span>Weight</span><input type="number" name="weight" min="0" max="100" value="50"></label></div>
                                <label><span>Description</span><input type="text" name="description" maxlength="1200"></label>
                                <button class="scw-button" type="submit">Add criterion</button>
                            </form>
                            <div class="scw-decision-list" data-scw-decision-criterion-list></div>
                        </section>

                        <section class="scw-decision-panel" aria-labelledby="scw-decision-assess-heading">
                            <div class="scw-decision-panel-head"><span>03 / ASSESS</span><h4 id="scw-decision-assess-heading">Option assessments</h4></div>
                            <form class="scw-decision-form" data-scw-decision-assessment-form>
                                <div class="scw-decision-form-row"><label><span>Option</span><select name="optionId" data-scw-decision-assessment-option><option value="">Choose option</option></select></label><label><span>Criterion</span><select name="criterionId" data-scw-decision-assessment-criterion><option value="">Choose criterion</option></select></label></div>
                                <div class="scw-decision-form-row"><label><span>Score (-5 to +5)</span><input type="number" name="score" min="-5" max="5" value="0"></label><label><span>Note</span><input type="text" name="note" maxlength="1200"></label></div>
                                <button class="scw-button" type="submit">Record assessment</button>
                            </form>
                            <div class="scw-decision-list" data-scw-decision-assessment-list></div>
                        </section>

                        <section class="scw-decision-panel scw-decision-panel-wide" aria-labelledby="scw-decision-record-heading">
                            <div class="scw-decision-panel-head"><span>04 / DECIDE</span><h4 id="scw-decision-record-heading">Risks &amp; decision record</h4></div>
                            <div class="scw-decision-two-col">
                                <div>
                                    <form class="scw-decision-form" data-scw-decision-risk-form>
                                        <label><span>Risk</span><textarea name="risk" rows="3" maxlength="2400" required></textarea></label>
                                        <div class="scw-decision-form-row"><label><span>Likelihood</span><select name="likelihood"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></label><label><span>Impact</span><select name="impact"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></label></div>
                                        <label><span>Mitigation</span><textarea name="mitigation" rows="2" maxlength="2000"></textarea></label>
                                        <button class="scw-button" type="submit">Add risk</button>
                                    </form>
                                    <div class="scw-decision-list" data-scw-decision-risk-list></div>
                                </div>
                                <div>
                                    <form class="scw-decision-form" data-scw-decision-final-form>
                                        <label><span>Selected option</span><select name="selectedOptionId" data-scw-decision-final-option><option value="">Choose option</option></select></label>
                                        <label><span>Rationale</span><textarea name="rationale" rows="5" maxlength="6000" required placeholder="Why is this the preferred course given the evidence, analysis, criteria, tradeoffs, and risks?"></textarea></label>
                                        <label><span>Confidence</span><select name="confidence"><option value="low">Low</option><option value="medium" selected>Medium</option><option value="high">High</option></select></label>
                                        <button class="scw-button scw-button-primary" type="submit">Finalize decision</button>
                                    </form>
                                    <div class="scw-decision-summary" data-scw-decision-summary><span>No finalized decision yet.</span></div>
                                </div>
                            </div>
                        </section>
                    </div>
                </section>

                <section class="scw-canvas" data-scw-project-panel="canvas" aria-labelledby="scw-canvas-title">
                    <div class="scw-canvas-head">
                        <div>
                            <div class="scw-kicker">CANVAS &amp; STRUCTURED THINKING</div>
                            <h3 id="scw-canvas-title">Make relationships visible without flattening the reasoning.</h3>
                            <p>Create project boards that connect questions, claims, evidence, data, analyses, decisions, systems, stakeholders, and ideas. Canvas nodes can reference existing Workspace Objects while relationships and frames preserve how the pieces fit together.</p>
                        </div>
                        <div class="scw-canvas-launchers" aria-label="Canvas tools">
                            <a class="scw-button" data-scw-tool="catalyst-canvas" data-scw-canvas-handoff href="<?php echo esc_url(home_url('/platform/catalyst-canvas/')); ?>"><strong>Open Catalyst Canvas</strong></a>
                            <button class="scw-button scw-button-primary" type="button" data-scw-canvas-synthesis>Capture synthesis</button>
                        </div>
                    </div>

                    <div class="scw-canvas-metrics" aria-label="Canvas project metrics">
                        <div><strong data-scw-canvas-metric-boards>0</strong><span>boards</span></div>
                        <div><strong data-scw-canvas-metric-nodes>0</strong><span>nodes</span></div>
                        <div><strong data-scw-canvas-metric-edges>0</strong><span>relationships</span></div>
                        <div><strong data-scw-canvas-metric-frames>0</strong><span>frames</span></div>
                    </div>

                    <div class="scw-canvas-layout">
                        <aside class="scw-canvas-sidebar" aria-labelledby="scw-canvas-board-heading">
                            <div class="scw-canvas-panel-head"><span>01 / BOARDS</span><h4 id="scw-canvas-board-heading">Thinking boards</h4></div>
                            <div class="scw-canvas-active"><span>ACTIVE BOARD</span><strong data-scw-canvas-active>No active board selected.</strong></div>
                            <form class="scw-canvas-form" data-scw-canvas-board-form>
                                <label><span>Board title</span><input type="text" name="title" maxlength="200" required placeholder="System map, argument map, stakeholder landscape…"></label>
                                <label><span>Purpose</span><textarea name="description" rows="3" maxlength="2400" placeholder="What are you trying to understand or structure?"></textarea></label>
                                <button class="scw-button" type="submit">Create board</button>
                            </form>
                            <div class="scw-canvas-list" data-scw-canvas-board-list></div>
                        </aside>

                        <section class="scw-canvas-main" aria-labelledby="scw-canvas-surface-heading">
                            <div class="scw-canvas-panel-head"><span>02 / MAP</span><h4 id="scw-canvas-surface-heading">Structured canvas</h4></div>
                            <div class="scw-canvas-surface" data-scw-canvas-surface>
                                <svg class="scw-canvas-lines" data-scw-canvas-lines aria-hidden="true"></svg>
                                <div class="scw-canvas-surface-empty" data-scw-canvas-surface-empty>Select or create a board to begin mapping.</div>
                            </div>

                            <form class="scw-canvas-form scw-canvas-node-form" data-scw-canvas-node-form>
                                <div class="scw-canvas-form-row">
                                    <label><span>Node type</span><select name="type"><option value="note">Note</option><option value="question">Question</option><option value="claim">Claim</option><option value="evidence">Evidence</option><option value="data">Data</option><option value="analysis">Analysis</option><option value="decision">Decision</option><option value="system">System</option><option value="stakeholder">Stakeholder</option><option value="idea">Idea</option></select></label>
                                    <label><span>Link Workspace Object</span><select name="objectId" data-scw-canvas-node-object><option value="">No linked object</option></select></label>
                                </div>
                                <label><span>Node title</span><input type="text" name="title" maxlength="240" placeholder="A concise proposition, actor, finding, or concept"></label>
                                <label><span>Detail</span><textarea name="body" rows="3" maxlength="4000" placeholder="Context, explanation, or working note."></textarea></label>
                                <button class="scw-button" type="submit">Add node</button>
                            </form>
                        </section>
                    </div>

                    <div class="scw-canvas-structure-grid">
                        <section class="scw-canvas-panel" aria-labelledby="scw-canvas-rel-heading">
                            <div class="scw-canvas-panel-head"><span>03 / RELATIONSHIPS</span><h4 id="scw-canvas-rel-heading">Typed relationships</h4></div>
                            <form class="scw-canvas-form" data-scw-canvas-edge-form>
                                <div class="scw-canvas-form-row"><label><span>From</span><select name="fromNodeId" data-scw-canvas-edge-from><option value="">Choose node</option></select></label><label><span>Relationship</span><select name="relation"><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="depends-on">Depends on</option><option value="influences">Influences</option><option value="contains">Contains</option><option value="causes">Causes</option><option value="relates-to">Relates to</option><option value="sequence">Sequence</option></select></label></div>
                                <div class="scw-canvas-form-row"><label><span>To</span><select name="toNodeId" data-scw-canvas-edge-to><option value="">Choose node</option></select></label><label><span>Label</span><input type="text" name="label" maxlength="240" placeholder="Optional nuance"></label></div>
                                <button class="scw-button" type="submit">Connect nodes</button>
                            </form>
                            <div class="scw-canvas-list" data-scw-canvas-edge-list></div>
                        </section>

                        <section class="scw-canvas-panel" aria-labelledby="scw-canvas-frame-heading">
                            <div class="scw-canvas-panel-head"><span>04 / FRAMES</span><h4 id="scw-canvas-frame-heading">Group meaning</h4></div>
                            <form class="scw-canvas-form" data-scw-canvas-frame-form>
                                <label><span>Frame title</span><input type="text" name="title" maxlength="200" required placeholder="Key uncertainty, stakeholder cluster, causal chain…"></label>
                                <label><span>Description</span><textarea name="description" rows="3" maxlength="1600"></textarea></label>
                                <label><span>Nodes</span><select name="nodeIds" multiple size="6" data-scw-canvas-frame-nodes></select></label>
                                <button class="scw-button" type="submit">Create frame</button>
                            </form>
                            <div class="scw-canvas-list" data-scw-canvas-frame-list></div>
                        </section>
                    </div>
                </section>

                <section class="scw-traceability" data-scw-project-panel="traceability" aria-labelledby="scw-traceability-title">
                    <div class="scw-traceability-head">
                        <div>
                            <div class="scw-kicker">EVIDENCE · PROVENANCE · REPRODUCIBILITY</div>
                            <h3 id="scw-traceability-title">Keep the basis of the work inspectable.</h3>
                            <p>Assess evidence, connect object lineage, fingerprint important artifacts, and record enough analytical context for another person—or your future self—to understand what produced a result.</p>
                        </div>
                        <button class="scw-button" type="button" data-scw-traceability-export>Export traceability package</button>
                    </div>
                    <div class="scw-traceability-metrics">
                        <div><strong data-scw-trace-metric-assessments>0</strong><span>assessed evidence</span></div>
                        <div><strong data-scw-trace-metric-lineage>0</strong><span>lineage links</span></div>
                        <div><strong data-scw-trace-metric-repro>0</strong><span>reproduction records</span></div>
                        <div><strong data-scw-trace-metric-verified>0</strong><span>verified records</span></div>
                    </div>
                    <div class="scw-traceability-grid">
                        <section class="scw-trace-panel" aria-labelledby="scw-trace-evidence-heading">
                            <div class="scw-trace-panel-head"><span>01 / EVIDENCE QUALITY</span><h4 id="scw-trace-evidence-heading">Assess the evidence explicitly.</h4></div>
                            <p class="scw-trace-note">The four ratings are a transparent working heuristic, not an automated truth score.</p>
                            <form class="scw-trace-form" data-scw-evidence-assessment-form>
                                <label><span>Source or evidence object</span><select name="objectId" data-scw-trace-evidence-object required><option value="">Choose an object</option></select></label>
                                <div class="scw-trace-score-grid">
                                    <label><span>Relevance</span><select name="relevance"><option value="0">Unrated</option><option value="1">Low</option><option value="2">Moderate</option><option value="3">Strong</option><option value="4">High</option></select></label>
                                    <label><span>Source quality</span><select name="sourceQuality"><option value="0">Unrated</option><option value="1">Low</option><option value="2">Moderate</option><option value="3">Strong</option><option value="4">High</option></select></label>
                                    <label><span>Independence</span><select name="independence"><option value="0">Unrated</option><option value="1">Low</option><option value="2">Moderate</option><option value="3">Strong</option><option value="4">High</option></select></label>
                                    <label><span>Recency</span><select name="recency"><option value="0">Unrated</option><option value="1">Low</option><option value="2">Moderate</option><option value="3">Strong</option><option value="4">High</option></select></label>
                                </div>
                                <label><span>Assessment note</span><textarea name="note" rows="3" maxlength="2000" placeholder="Why do these ratings make sense for this use? What limitations matter?"></textarea></label>
                                <button class="scw-button" type="submit">Save assessment & fingerprint</button>
                            </form>
                            <div class="scw-trace-list" data-scw-evidence-assessment-list></div>
                        </section>
                        <section class="scw-trace-panel" aria-labelledby="scw-trace-lineage-heading">
                            <div class="scw-trace-panel-head"><span>02 / LINEAGE</span><h4 id="scw-trace-lineage-heading">Connect how artifacts relate.</h4></div>
                            <form class="scw-trace-form" data-scw-lineage-form>
                                <label><span>From object</span><select name="fromObjectId" data-scw-lineage-from required><option value="">Choose an object</option></select></label>
                                <label><span>Relationship</span><select name="relation"><option value="derived-from">Derived from</option><option value="supports">Supports</option><option value="contradicts">Contradicts</option><option value="uses">Uses</option><option value="produced-by">Produced by</option><option value="informs">Informs</option><option value="supersedes">Supersedes</option><option value="cites">Cites</option></select></label>
                                <label><span>To object</span><select name="toObjectId" data-scw-lineage-to required><option value="">Choose an object</option></select></label>
                                <label><span>Note</span><input type="text" name="note" maxlength="500" placeholder="Optional relationship context"></label>
                                <button class="scw-button" type="submit">Add lineage link</button>
                            </form>
                            <div class="scw-trace-list" data-scw-lineage-list></div>
                        </section>
                        <section class="scw-trace-panel scw-trace-panel-wide" aria-labelledby="scw-trace-repro-heading">
                            <div class="scw-trace-panel-head"><span>03 / REPRODUCIBILITY</span><h4 id="scw-trace-repro-heading">Record what would be needed to reproduce an analysis.</h4></div>
                            <form class="scw-trace-form" data-scw-repro-form>
                                <div class="scw-trace-form-row"><label><span>Record title</span><input type="text" name="title" maxlength="200" required placeholder="Grid reliability sensitivity run"></label><label><span>Analysis object</span><select name="analysisObjectId" data-scw-repro-analysis><option value="">No linked analysis object</option></select></label></div>
                                <div class="scw-trace-form-row"><label><span>Dataset inputs</span><select name="datasetObjectIds" data-scw-repro-datasets multiple size="4"></select></label><label><span>Evidence inputs</span><select name="evidenceObjectIds" data-scw-repro-evidence multiple size="4"></select></label></div>
                                <label><span>Method / procedure</span><textarea name="method" rows="3" maxlength="4000" placeholder="Describe the analytical method or link it to the registered Analysis method."></textarea></label>
                                <div class="scw-trace-form-row"><label><span>Parameters / assumptions</span><textarea name="parameters" rows="4" maxlength="5000" placeholder="Parameter values, assumptions, thresholds, filters."></textarea></label><label><span>Environment</span><textarea name="environment" rows="4" maxlength="3000" placeholder="Tool/version, runtime, packages, data vintage, or other execution context."></textarea></label></div>
                                <label><span>Reproduction steps</span><textarea name="steps" rows="5" maxlength="8000" placeholder="Ordered steps another person could follow."></textarea></label>
                                <button class="scw-button" type="submit">Create reproduction record</button>
                            </form>
                            <div class="scw-trace-list" data-scw-repro-list></div>
                        </section>
                    </div>
                </section>


                <section class="scw-ai" data-scw-project-panel="assist" aria-labelledby="scw-ai-title">
                    <div class="scw-ai-head">
                        <div>
                            <div class="scw-kicker">RESPONSIBLE AI ASSISTANCE</div>
                            <h3 id="scw-ai-title">Ask for help without hiding the basis of the work.</h3>
                            <p>Prepare grounded AI requests from selected Workspace Objects, review responses locally, and explicitly accept useful material as a draft Document. Workspace does not automatically send project content to a model, approve decisions, publish outputs, or overwrite evidence.</p>
                        </div>
                        <div class="scw-ai-boundary"><strong>HUMAN CONTROLLED</strong><span>Prepare → review → accept or reject</span></div>
                    </div>
                    <div class="scw-ai-metrics" aria-label="Responsible AI assistance metrics">
                        <div><strong data-scw-ai-metric-sessions>0</strong><span>requests</span></div>
                        <div><strong data-scw-ai-metric-grounding>0</strong><span>grounding refs</span></div>
                        <div><strong data-scw-ai-metric-responses>0</strong><span>responses</span></div>
                        <div><strong data-scw-ai-metric-accepted>0</strong><span>accepted drafts</span></div>
                    </div>
                    <div class="scw-ai-grid">
                        <section class="scw-ai-panel" aria-labelledby="scw-ai-request-heading">
                            <div class="scw-ai-panel-head"><span>01 / PREPARE</span><h4 id="scw-ai-request-heading">Ground an assistance request.</h4></div>
                            <form class="scw-ai-form" data-scw-ai-request-form>
                                <label><span>Request title</span><input type="text" name="title" maxlength="200" required placeholder="e.g. Summarize the evidence on grid stability"></label>
                                <label><span>Task</span><select name="task"><option value="grounded-summary">Grounded summary</option><option value="evidence-gaps">Evidence gaps &amp; contradictions</option><option value="compare-alternatives">Compare alternatives</option><option value="briefing-draft">Draft briefing section</option><option value="method-explanation">Explain method &amp; assumptions</option><option value="general-question">Grounded question</option></select></label>
                                <label><span>User request</span><textarea name="prompt" rows="5" maxlength="5000" required placeholder="What would you like assistance with? State the scope, audience, or constraints explicitly."></textarea></label>
                                <label><span>Grounding objects</span><select multiple size="8" data-scw-ai-object-select aria-label="Workspace Objects used to ground the request"></select></label>
                                <button class="scw-button" type="submit">Prepare request</button>
                            </form>
                        </section>
                        <section class="scw-ai-panel" aria-labelledby="scw-ai-sessions-heading">
                            <div class="scw-ai-panel-head"><span>02 / REQUESTS</span><h4 id="scw-ai-sessions-heading">Keep assistance sessions reviewable.</h4></div>
                            <div class="scw-ai-active"><span>ACTIVE REQUEST</span><strong data-scw-ai-active>No active AI assistance request.</strong></div>
                            <div class="scw-ai-session-list" data-scw-ai-session-list></div>
                        </section>
                        <section class="scw-ai-panel" aria-labelledby="scw-ai-grounding-heading">
                            <div class="scw-ai-panel-head"><span>03 / GROUNDING</span><h4 id="scw-ai-grounding-heading">Make the source basis visible.</h4></div>
                            <div class="scw-ai-grounding" data-scw-ai-grounding></div>
                            <div class="scw-ai-actions scw-ai-request-actions">
                                <button class="scw-card-action" type="button" data-scw-ai-copy-prompt>Copy grounded prompt</button>
                                <button class="scw-card-action" type="button" data-scw-ai-export-request>Export request JSON</button>
                                <button class="scw-card-action" type="button" data-scw-ai-open-librarian>Open Research Librarian</button>
                            </div>
                            <p class="scw-ai-note">Preparing a request is local. No selected object content is sent automatically. A compatible same-origin Research Librarian adapter can read the prepared request only after this explicit user action. If no adapter is active, use Copy or Export instead.</p>
                        </section>
                        <section class="scw-ai-panel scw-ai-panel-wide" aria-labelledby="scw-ai-response-heading">
                            <div class="scw-ai-panel-head"><span>04 / REVIEW</span><h4 id="scw-ai-response-heading">Treat AI output as a draft, not evidence.</h4></div>
                            <div class="scw-ai-review-grid">
                                <label><span>Response source</span><select data-scw-ai-response-source><option value="manual">Manual paste / review</option><option value="research-librarian">Research Librarian</option><option value="adapter">Connected adapter</option><option value="external">External AI tool</option></select></label>
                                <label class="scw-ai-response-field"><span>Response</span><textarea rows="12" maxlength="30000" data-scw-ai-response placeholder="Paste or review an AI response here. Nothing is accepted into the project until you explicitly choose Accept as Document."></textarea></label>
                                <label><span>Grounding references cited by the response</span><select multiple size="7" data-scw-ai-citation-select></select></label>
                            </div>
                            <div class="scw-ai-actions scw-ai-review-actions">
                                <button class="scw-button" type="button" data-scw-ai-save-response>Save response for review</button>
                                <button class="scw-button" type="button" data-scw-ai-accept-document>Accept as Document</button>
                                <button class="scw-button" type="button" data-scw-ai-reject>Reject response</button>
                                <button class="scw-card-action" type="button" data-scw-ai-export-response>Export response JSON</button>
                            </div>
                            <div class="scw-ai-policy" role="note"><strong>AI does not become evidence by acceptance.</strong><span>Accepted output becomes a working Document object tagged <code>ai-assisted</code> and <code>human-accepted</code>. Any selected citation objects remain separate canonical Sources/Evidence and are linked through visible provenance lineage.</span></div>
                        </section>
                    </div>
                </section>

                <section class="scw-briefing" data-scw-project-panel="briefing" aria-labelledby="scw-briefing-title">
                    <div class="scw-briefing-head">
                        <div>
                            <div class="scw-kicker">BRIEFING &amp; PUBLICATION STUDIO</div>
                            <h3 id="scw-briefing-title">Turn connected project work into something another person can use.</h3>
                            <p>Compose briefings, memos, reports, articles, and publication drafts from existing Workspace Objects while preserving the basis of the work. Workspace exports portable drafts; it does not publish directly to a CMS.</p>
                        </div>
                        <button class="scw-button" type="button" data-scw-briefing-export-package disabled>Export publication package</button>
                    </div>
                    <div class="scw-briefing-metrics" aria-label="Briefing project metrics">
                        <div><strong data-scw-briefing-metric-drafts>0</strong><span>drafts</span></div>
                        <div><strong data-scw-briefing-metric-ready>0</strong><span>ready</span></div>
                        <div><strong data-scw-briefing-metric-refs>0</strong><span>object references</span></div>
                        <div><strong data-scw-briefing-metric-docs>0</strong><span>document outputs</span></div>
                    </div>
                    <div class="scw-briefing-grid">
                        <section class="scw-briefing-panel scw-briefing-panel-wide" aria-labelledby="scw-briefing-drafts-heading">
                            <div class="scw-briefing-panel-head"><span>01 / DRAFTS</span><h4 id="scw-briefing-drafts-heading">Create a communication artifact.</h4></div>
                            <form class="scw-briefing-form" data-scw-briefing-draft-form>
                                <div class="scw-briefing-form-row"><label><span>Title</span><input type="text" name="title" maxlength="200" required placeholder="Grid reliability briefing"></label><label><span>Format</span><select name="format"><option value="briefing">Briefing</option><option value="memo">Memo</option><option value="report">Report</option><option value="article">Article</option><option value="publication-draft">Publication draft</option></select></label></div>
                                <div class="scw-briefing-form-row"><label><span>Audience</span><input type="text" name="audience" maxlength="300" placeholder="Board, project team, general reader"></label><label><span>Purpose</span><input type="text" name="purpose" maxlength="600" placeholder="What should this artifact help the reader understand or decide?"></label></div>
                                <button class="scw-button" type="submit">Create draft</button>
                            </form>
                            <div class="scw-briefing-list" data-scw-briefing-draft-list></div>
                        </section>
                        <section class="scw-briefing-panel" aria-labelledby="scw-briefing-basis-heading">
                            <div class="scw-briefing-panel-head"><span>02 / BASIS</span><h4 id="scw-briefing-basis-heading">Choose the objects this draft is based on.</h4></div>
                            <div class="scw-briefing-active"><span>ACTIVE DRAFT</span><strong data-scw-briefing-active>No active draft selected.</strong></div>
                            <label><span>Workspace Objects</span><select data-scw-briefing-object-select multiple size="8"></select></label>
                            <button class="scw-button" type="button" data-scw-briefing-save-basis disabled>Save basis</button>
                            <div class="scw-briefing-basis-list" data-scw-briefing-basis-list></div>
                        </section>
                        <section class="scw-briefing-panel scw-briefing-panel-wide" aria-labelledby="scw-briefing-structure-heading">
                            <div class="scw-briefing-panel-head"><span>03 / STRUCTURE</span><h4 id="scw-briefing-structure-heading">Build the narrative without hiding the underlying work.</h4></div>
                            <div class="scw-briefing-structure-actions"><button class="scw-button" type="button" data-scw-briefing-outline disabled>Build standard outline</button><label><span>Status</span><select data-scw-briefing-status disabled><option value="draft">Draft</option><option value="review">Review</option><option value="ready">Ready</option><option value="exported">Exported</option></select></label></div>
                            <form class="scw-briefing-form" data-scw-briefing-section-form>
                                <label><span>Section heading</span><input type="text" name="heading" maxlength="180" required placeholder="Executive summary"></label>
                                <label><span>Section text</span><textarea name="body" rows="5" maxlength="8000" placeholder="Draft this section here. You can revise it after adding it."></textarea></label>
                                <button class="scw-button" type="submit">Add section</button>
                            </form>
                            <div class="scw-briefing-section-list" data-scw-briefing-section-list></div>
                        </section>
                        <section class="scw-briefing-panel scw-briefing-panel-wide" aria-labelledby="scw-briefing-output-heading">
                            <div class="scw-briefing-panel-head"><span>04 / OUTPUT</span><h4 id="scw-briefing-output-heading">Create a reusable document or export a portable draft.</h4></div>
                            <p class="scw-briefing-output-note">Exports include the authored draft and traceable object references. Workspace does not automatically publish or write to WordPress, Publications, or the Knowledge Library.</p>
                            <div class="scw-briefing-output-actions">
                                <button class="scw-button scw-button-primary" type="button" data-scw-briefing-materialize disabled>Materialize Document</button>
                                <button class="scw-button" type="button" data-scw-briefing-export-markdown disabled>Export Markdown</button>
                                <button class="scw-button" type="button" data-scw-briefing-export-html disabled>Export HTML</button>
                            </div>
                        </section>
                    </div>
                </section>

                <section class="scw-objects" data-scw-project-panel="objects" aria-labelledby="scw-objects-title">
                    <div class="scw-object-head">
                        <div>
                            <div class="scw-kicker">WORKSPACE OBJECTS</div>
                            <h3 id="scw-objects-title">Reusable work inside this project.</h3>
                            <p>Sources, evidence, datasets, analyses, decisions, documents, and exports share one stable local object contract.</p>
                        </div>
                        <button class="scw-button scw-button-primary" type="button" data-scw-new-object>New object</button>
                    </div>

                    <form class="scw-object-create" data-scw-object-create-form hidden>
                        <label><span>Object type</span><select name="type" required>
                            <option value="source">Source</option>
                            <option value="evidence">Evidence</option>
                            <option value="dataset">Dataset</option>
                            <option value="analysis">Analysis</option>
                            <option value="decision">Decision</option>
                            <option value="document">Document</option>
                            <option value="export">Export</option>
                        </select></label>
                        <label><span>Object title</span><input type="text" name="title" maxlength="160" required placeholder="Untitled object"></label>
                        <div class="scw-create-actions">
                            <button class="scw-button scw-button-primary" type="submit">Create object</button>
                            <button class="scw-button" type="button" data-scw-cancel-object>Create later</button>
                        </div>
                    </form>

                    <div class="scw-object-toolbar">
                        <label><span>SHOW</span><select data-scw-object-archive-filter><option value="current">Current objects</option><option value="archived">Archived objects</option></select></label>
                        <label><span>TYPE</span><select data-scw-object-type-filter>
                            <option value="all">All types</option>
                            <option value="source">Sources</option>
                            <option value="evidence">Evidence</option>
                            <option value="dataset">Datasets</option>
                            <option value="analysis">Analyses</option>
                            <option value="decision">Decisions</option>
                            <option value="document">Documents</option>
                            <option value="export">Exports</option>
                        </select></label>
                        <span class="scw-object-limit" data-scw-object-limit>0 / 250 objects</span>
                    </div>

                    <div class="scw-object-empty" data-scw-object-empty>
                        <strong>No Workspace Objects yet.</strong>
                        <span>Create a typed object to start turning project work into reusable artifacts.</span>
                    </div>
                    <div class="scw-object-list" data-scw-object-list aria-live="polite"></div>

                    <div class="scw-object-editor" data-scw-object-editor hidden>
                        <div class="scw-object-editor-head">
                            <div>
                                <span class="scw-object-type" data-scw-object-type-label>OBJECT</span>
                                <h4 data-scw-object-heading>Object</h4>
                            </div>
                            <code data-scw-object-id></code>
                        </div>
                        <div class="scw-object-editor-grid">
                            <div class="scw-object-fields">
                                <div class="scw-object-row">
                                    <label><span>Title</span><input type="text" maxlength="160" data-scw-object-title></label>
                                    <label><span>Status</span><select data-scw-object-status><option value="draft">Draft</option><option value="working">Working</option><option value="ready">Ready</option></select></label>
                                </div>
                                <label><span>Summary</span><textarea rows="3" maxlength="1200" data-scw-object-summary placeholder="What does this object contain or establish?"></textarea></label>
                                <label><span>Content</span><textarea class="scw-object-content" rows="12" maxlength="50000" data-scw-object-content placeholder="Capture the source, evidence, data description, analysis, decision record, document text, or export notes here."></textarea></label>
                                <label><span>Tags</span><input type="text" data-scw-object-tags placeholder="climate, grid, evidence (comma separated)"></label>
                                <div class="scw-object-provenance">
                                    <div class="scw-provenance-heading"><span>PROVENANCE</span><small>Optional but recommended</small></div>
                                    <div class="scw-object-row scw-object-row-provenance">
                                        <label><span>Source type</span><select data-scw-object-source-type>
                                            <option value="manual">Manual</option>
                                            <option value="web">Web</option>
                                            <option value="library">Library</option>
                                            <option value="dataset">Dataset</option>
                                            <option value="tool">Sustainable Catalyst tool</option>
                                            <option value="imported">Imported</option>
                                        </select></label>
                                        <label><span>Source title</span><input type="text" maxlength="240" data-scw-object-source-title></label>
                                    </div>
                                    <label><span>Source URL</span><input type="url" maxlength="2000" data-scw-object-source-url placeholder="https://"></label>
                                </div>
                            </div>
                            <aside class="scw-object-ops" aria-label="Object operations">
                                <span class="scw-op-label">OBJECT</span>
                                <button class="scw-op" type="button" data-scw-object-duplicate>Duplicate object</button>
                                <button class="scw-op" type="button" data-scw-object-export>Export object JSON</button>
                                <button class="scw-op" type="button" data-scw-object-archive>Archive object</button>
                                <button class="scw-op scw-op-danger" type="button" data-scw-object-delete>Delete object</button>
                                <div class="scw-object-meta">
                                    <span>CREATED</span><strong data-scw-object-created></strong>
                                    <span>UPDATED</span><strong data-scw-object-updated></strong>
                                </div>
                            </aside>
                        </div>
                    </div>
                </section>
            </section>

            <details class="scw-connections-drawer">
                <summary><span><small>Connected workflows</small><strong>Tools, returns &amp; handoff history</strong></span><em>Open</em></summary>
                <section class="scw-handoffs" aria-labelledby="scw-handoffs-title">
                <div class="scw-handoff-head">
                    <div>
                        <div class="scw-kicker">CROSS-PRODUCT HANDOFFS</div>
                        <h3 id="scw-handoffs-title">Connections & returns</h3>
                        <p>Review return activity or import a structured return package when you need it. The underlying handoff IDs and privacy checks remain intact.</p>
                    </div>
                    <div class="scw-handoff-actions">
                        <button class="scw-button" type="button" data-scw-handoff-check>Check return inbox</button>
                        <button class="scw-button" type="button" data-scw-handoff-import>Import return JSON</button>
                        <button class="scw-button" type="button" data-scw-handoff-template>Export return template</button>
                        <input type="file" accept="application/json,.json" data-scw-handoff-import-file hidden>
                    </div>
                </div>
                <div class="scw-handoff-metrics">
                    <div><strong data-scw-handoff-metric-launched>0</strong><span>Awaiting return</span></div>
                    <div><strong data-scw-handoff-metric-returned>0</strong><span>Returned</span></div>
                    <div><strong data-scw-handoff-metric-objects>0</strong><span>Returned artifacts</span></div>
                    <div><strong data-scw-handoff-metric-closed>0</strong><span>Closed</span></div>
                </div>
                <div class="scw-handoff-boundary" role="note">
                    <strong>Context, not content</strong>
                    <span>Outbound URLs carry only stable IDs, destination intent, and a return signal. Structured returned content is accepted locally through the return inbox and becomes ordinary Workspace Objects with tool provenance.</span>
                </div>
                <div class="scw-adapter-boundary" data-scw-return-adapters role="note">
                    <strong>ADAPTER DIAGNOSTICS</strong>
                    <span>Workspace now normalizes canonical returns from Research Librarian, Knowledge Library, Site Intelligence, Workbench, Analytics R, Decision Studio, Catalyst Canvas, Catalyst Data, and Lab. Automatic returns must match the locally recorded project, handoff ID, and destination.</span>
                </div>
                <div class="scw-handoff-list" data-scw-handoff-list></div>
                <div class="scw-handoff-empty" data-scw-handoff-empty>No handoffs recorded for this project yet. Open a connected tool below to create the first handoff.</div>
            </section>

            <section class="scw-tools" aria-labelledby="scw-tools-title">
                <div class="scw-section-head">
                    <div>
                        <div class="scw-kicker">CONNECTED TOOLS</div>
                        <h2 id="scw-tools-title">Open a specialized Sustainable Catalyst tool.</h2>
                        <p class="scw-section-note">The active project context stays available when supported tools open and return work.</p>
                    </div>
                    <a class="scw-text-link" href="<?php echo esc_url(home_url('/platform/')); ?>">Workspace home <span aria-hidden="true">→</span></a>
                </div>

                <div class="scw-tool-grid">
                    <?php foreach ($tools as $tool): ?>
                        <a class="scw-tool" data-scw-tool="<?php echo esc_attr($tool['key']); ?>" href="<?php echo esc_url($tool['url']); ?>">
                            <span class="scw-tool-eyebrow"><?php echo esc_html($tool['eyebrow']); ?></span>
                            <strong><?php echo esc_html($tool['name']); ?></strong>
                            <span class="scw-tool-description"><?php echo esc_html($tool['description']); ?></span>
                            <span class="scw-tool-open">Open <span aria-hidden="true">↗</span></span>
                        </a>
                    <?php endforeach; ?>
                </div>
                </section>
            </details>

            <footer class="scw-footer">
                <div><strong>Workspace v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></strong> · Free public access</div>
                <div>Projects remain local by default. Signed-in users can create manual recovery backups or explicitly enroll individual projects in conflict-safe sync. Nothing synchronizes in the background.</div>
            </footer>
        </section>
        <?php
        return ob_get_clean();
    }

    public function render_platform($atts = array()) {
        $this->enqueue_assets();
        $workspace = $this->render_workspace();
        ob_start();
        ?>
        <section class="scw-platform-page scw-public-experience scw-editorial-shell" data-sc-workspace-platform data-version="<?php echo esc_attr(SC_WORKSPACE_VERSION); ?>">
            <div class="scw-editorial-header-bar" aria-hidden="true"></div>
            <header class="scw-platform-hero scw-platform-hero-editorial">
                <div class="scw-platform-hero-grid">
                    <div class="scw-platform-hero-copy">
                        <div class="scw-kicker">SUSTAINABLE CATALYST / WORKSPACE</div>
                        <h1>Research. Analyze. Decide.</h1>
                        <p class="scw-platform-lede">A free personal workspace for keeping questions, evidence, analysis, decisions, and structured thinking connected from the beginning of an inquiry through its outcome.</p>
                        <div class="scw-platform-actions">
                            <a class="scw-button scw-button-primary" href="#workspace-application">Open Workspace</a>
                            <a class="scw-button" href="<?php echo esc_url(home_url('/knowledge-libraries/')); ?>">Explore the Library</a>
                        </div>
                        <div class="scw-platform-access-grid" aria-label="Workspace access summary">
                            <div><span>ACCESS</span><strong>Free public use</strong></div>
                            <div><span>ACCOUNT</span><strong>Optional</strong></div>
                            <div><span>PERSISTENCE</span><strong>Local first · optional backup</strong></div>
                        </div>
                    </div>
                    <aside class="scw-platform-preview" aria-label="Illustrative Workspace project preview">
                        <div class="scw-preview-topline"><span>ILLUSTRATIVE WORKSPACE</span><b>LOCAL</b></div>
                        <div class="scw-preview-title">Energy Systems Research</div>
                        <div class="scw-preview-status">Active project · Updated today</div>
                        <div class="scw-preview-grid">
                            <div><span>Research</span><strong>12 sources</strong><small>2 open questions</small></div>
                            <div><span>Evidence</span><strong>8 items</strong><small>Provenance retained</small></div>
                            <div><span>Analysis</span><strong>3 methods</strong><small>2 assumptions visible</small></div>
                            <div><span>Decision</span><strong>1 open</strong><small>Criteria in review</small></div>
                        </div>
                        <div class="scw-preview-track"><span class="is-complete">Research</span><span class="is-complete">Evidence</span><span>Analysis</span><span>Decision</span><span>Canvas</span></div>
                    </aside>
                </div>
            </header>

            <section class="scw-editorial-section scw-editorial-section-white scw-platform-story" aria-labelledby="scw-story-title">
                <div class="scw-editorial-kicker">ONE PERSONAL WORKSPACE</div>
                <h2 id="scw-story-title">From difficult question to a decision you can trace.</h2>
                <p class="scw-editorial-deck">Workspace keeps the basis of the work visible as it develops. Sources remain connected to evidence, evidence to analysis, analysis to choices, and choices to the reasoning that supports them.</p>
                <div class="scw-platform-flow scw-platform-flow-editorial" aria-label="Workspace workflow">
                    <article><span>01</span><strong>Research</strong><p>Frame questions, collect sources, and keep the inquiry organized.</p></article>
                    <article><span>02</span><strong>Evidence</strong><p>Preserve support, provenance, and links back to the source.</p></article>
                    <article><span>03</span><strong>Analysis</strong><p>Make datasets, methods, assumptions, comparisons, and findings visible.</p></article>
                    <article><span>04</span><strong>Decision</strong><p>Compare options, weigh criteria, assess risk, and record rationale.</p></article>
                    <article><span>05</span><strong>Canvas</strong><p>Map systems, relationships, stakeholders, claims, and ideas.</p></article>
                </div>
                <div class="scw-editorial-band"><strong>Connected reasoning across every stage</strong><span>Questions</span><span>Sources</span><span>Provenance</span><span>Assumptions</span><span>Methods</span><span>Trade-offs</span><span>Decisions</span></div>
            </section>

            <section class="scw-editorial-section scw-editorial-section-neutral scw-platform-pathways" aria-labelledby="scw-pathways-title">
                <div class="scw-editorial-kicker">WORKSPACE PATHWAYS</div>
                <h2 id="scw-pathways-title">Begin with the work in front of you.</h2>
                <p class="scw-editorial-deck">These are connected ways to use one personal environment, not separate products or locked tiers. A project can move between them as the work develops.</p>
                <div class="scw-pathway-list">
                    <article><b>01</b><div><strong>Research and evidence</strong><p>Investigate a question, organize sources, extract evidence, map claims, and preserve provenance.</p></div><span>Sources + evidence</span></article>
                    <article><b>02</b><div><strong>Analysis and modeling</strong><p>Register datasets, variables, assumptions, methods, comparisons, and findings.</p></div><span>Analytical record</span></article>
                    <article><b>03</b><div><strong>Decision and trade-offs</strong><p>Compare alternatives, criteria, uncertainty, risks, mitigations, and rationale.</p></div><span>Decision record</span></article>
                    <article><b>04</b><div><strong>Systems and structured thinking</strong><p>Use Canvas boards to arrange relationships among evidence, analysis, decisions, systems, and stakeholders.</p></div><span>Structured synthesis</span></article>
                    <article><b>05</b><div><strong>Connected tools and reusable artifacts</strong><p>Move stable project context into Sustainable Catalyst tools and return structured artifacts to the originating project.</p></div><span>Portable project context</span></article>
                    <article><b>06</b><div><strong>Personal knowledge</strong><p>Search canonical objects across projects, inspect provenance and references, discover related work, and organize reusable collections.</p></div><span>Cross-project local index</span></article>
                    <article><b>07</b><div><strong>Import and interoperability</strong><p>Stage outside files locally, review provenance, and move structured artifacts into or out of Workspace without silent overwrite.</p></div><span>Portable interchange</span></article>
                    <article><b>08</b><div><strong>Share and portable projects</strong><p>Create integrity-checked whole-project copies or static review snapshots without cloud sync, public links, or live collaboration.</p></div><span>Portable project</span></article>
                </div>
            </section>

            <section class="scw-editorial-section scw-editorial-section-white scw-platform-capability" aria-labelledby="scw-capability-title">
                <div class="scw-editorial-kicker">PERSONAL CAPABILITY</div>
                <h2 id="scw-capability-title">A serious working environment, free to use.</h2>
                <p class="scw-editorial-deck">Workspace is useful on its own. Institutional capabilities belong in Catalyst Intelligence because the operating context changes, not because the personal product is intentionally weakened.</p>
                <div class="scw-capability-grid">
                    <article><span>LOCAL FIRST</span><strong>Your work stays with you.</strong><p>Guest use remains device-local. Signed-in users may opt into explicit project backups for recovery without background sync.</p></article>
                    <article><span>VISIBLE REASONING</span><strong>Keep the basis of the work attached.</strong><p>Sources, evidence, assumptions, methods, findings, options, and rationale remain connected inside the project.</p></article>
                    <article><span>CONNECTED BY DESIGN</span><strong>Use specialized tools when they help.</strong><p>Workspace can pass privacy-minimized context to the wider Sustainable Catalyst system and accept structured returns.</p></article>
                </div>
                <div class="scw-capability-dark"><div><span>IDENTITY &amp; PERSISTENCE</span><strong>Use Workspace immediately. Add identity when it helps.</strong></div><p>No login wall. Signing in does not upload project content; each cloud backup requires an explicit action.</p></div>
            </section>

            <section class="scw-platform-app-intro" aria-labelledby="scw-app-title">
                <div><div class="scw-editorial-kicker">WORKSPACE APPLICATION</div><h2 id="scw-app-title">Open the working environment.</h2><p>Projects hold the work; Personal Knowledge and Graph connect it across projects; Activity and History make workflow state, next actions, and named restore points inspectable; Import, Share, and connected tools move work deliberately; optional account backup/sync add off-device recovery while local diagnostics keep the persistence boundary explicit.</p></div>
                <a class="scw-button scw-button-primary" href="#workspace-application">Go to projects</a>
            </section>

            <div class="scw-platform-application scw-platform-application-editorial" id="workspace-application">
                <?php echo $workspace; // phpcs:ignore WordPress.Security.EscapeOutput.OutputNotEscaped -- generated shortcode HTML ?>
            </div>

            <section class="scw-editorial-closing" aria-label="Workspace closing action">
                <div><span>FREE PERSONAL WORKSPACE</span><h2>Keep the evidence, analysis, and decisions connected.</h2><p>Start without an account, preserve the reasoning, and use the wider Sustainable Catalyst system when the work calls for it.</p></div>
                <div class="scw-editorial-closing-actions"><button class="scw-button scw-button-primary" type="button" data-scw-platform-new-project>New Project</button><a class="scw-button scw-button-dark-outline" href="<?php echo esc_url(home_url('/knowledge-libraries/')); ?>">Explore the Library</a></div>
            </section>
        </section>
        <?php
        return ob_get_clean();
    }

    public function render_entry($atts = array()) {
        $this->enqueue_assets();
        $url = SC_Workspace_Platform::canonical_url();
        return '<a class="scw-entry" href="' . esc_url($url) . '"><span><small>FREE PUBLIC WORKSPACE</small><strong>Workspace</strong><em>Create local-first projects, reusable research objects, and optional account-aware sessions without a login wall.</em></span><b aria-hidden="true">→</b></a>';
    }
}
