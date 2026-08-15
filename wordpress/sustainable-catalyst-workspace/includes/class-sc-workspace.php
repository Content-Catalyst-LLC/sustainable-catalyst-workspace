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
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0800, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0790, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0780, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0770, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0760, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0750, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0740, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0730, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0720, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0710, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0700, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0690, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0680, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0670, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0661, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0660, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0650, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0641, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0640, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0630, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0620, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0610, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0570, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0560, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0540, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0520, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0510, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0500, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0490, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0461, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0420, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0390, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0380, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0370, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0360, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0350, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0340, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0330, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0320, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0310, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0300, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0290, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0280, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0270, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0260, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0250, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0240, '') === '1' ||
            get_option(SC_Workspace_Registry::LEGACY_PENDING_KEY_V0230, '') === '1' ||
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
        echo '<div class="notice notice-warning"><p><strong>Sustainable Catalyst Workspace:</strong> the canonical Product Registry was not available during activation. Workspace is active, but its v' . esc_html(SC_WORKSPACE_VERSION) . ' release record is pending until Product Support and Feedback is active.</p></div>';
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
        register_rest_route('sc-workspace/v1', '/notebook-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'notebook_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/source-capture-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'source_capture_contract'),
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
        register_rest_route('sc-workspace/v1', '/integrated-knowledge-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'integrated_knowledge_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/knowledge-search-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'knowledge_search_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/research-collections-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'research_collections_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/citation-library-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'citation_library_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/composition-studio-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'composition_studio_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/navigation-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'navigation_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/cross-project-knowledge-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'cross_project_knowledge_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/research-templates-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'research_templates_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/experience-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'experience_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/grounded-research-assistant-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'grounded_research_assistant_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/research-tasks-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'research_tasks_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/collaboration-architecture-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'collaboration_architecture_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/shared-review-handoff-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'shared_review_handoff_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/api-embed-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'api_embed_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/api-embed-hardening-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'api_embed_hardening_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/research-automation-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'research_automation_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/institutional-research-packages-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'institutional_research_packages_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/institutional-validation-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'institutional_validation_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/product-help-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'product_help_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/scale-performance-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'scale_performance_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/long-session-performance-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'long_session_performance_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/recovery-disaster-simulation-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'recovery_disaster_simulation_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/security-privacy-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'security_privacy_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/security-privacy-audit-ii-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'security_privacy_audit_ii_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/public-product-beta-ii-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'public_product_beta_ii_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/public-product-beta-iii-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'public_product_beta_iii_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/first-run-onboarding-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'first_run_onboarding_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/workflow-guidance-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'workflow_guidance_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/collaboration-review-hardening-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'collaboration_review_hardening_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/field-resilience-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'field_resilience_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/persistence-integrity-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'persistence_integrity_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/compatibility-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'compatibility_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/accessibility-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'accessibility_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/accessibility-performance-final-audit-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'accessibility_performance_final_audit_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/public-beta-iii-defect-closure-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'public_beta_iii_defect_closure_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/release-candidate-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'release_candidate_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/deployment-hardening-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'deployment_hardening_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/production-certification-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'production_certification_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/production-signoff-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'production_signoff_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/ga-readiness-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'ga_readiness_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/general-availability-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'general_availability_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/ga-stabilization-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'ga_stabilization_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/workspace-home-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'workspace_home_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/universal-search-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'universal_search_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/library-continuity-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'library_continuity_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/knowledge-graph-explorer-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'knowledge_graph_explorer_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/lab-integration-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'lab_integration_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/workbench-decision-roundtrip-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'workbench_decision_roundtrip_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/cross-device-production-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'cross_device_production_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/field-use-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'field_use_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/import-export-compatibility-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'import_export_compatibility_contract'),
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
        register_rest_route('sc-workspace/v1', '/continuity-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'continuity_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/version-history-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'version_history_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/change-review-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'change_review_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/safe-actions-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'safe_actions_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/reconciliation-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'reconciliation_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/reconciliation-receipts-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'reconciliation_receipts_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/audit-trail-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'audit_trail_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/project-lifecycle-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'project_lifecycle_contract'),
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
        register_rest_route('sc-workspace/v1', '/cloud-notebooks', array(
            array('methods' => 'GET', 'callback' => array($this, 'cloud_notebooks_list'), 'permission_callback' => array($this, 'cloud_permission')),
            array('methods' => 'POST', 'callback' => array($this, 'cloud_notebook_store'), 'permission_callback' => array($this, 'cloud_permission')),
        ));
        register_rest_route('sc-workspace/v1', '/cloud-notebooks/(?P<notebook_id>[A-Za-z0-9._-]{1,160})', array(
            array('methods' => 'GET', 'callback' => array($this, 'cloud_notebook_get'), 'permission_callback' => array($this, 'cloud_permission')),
            array('methods' => 'DELETE', 'callback' => array($this, 'cloud_notebook_delete'), 'permission_callback' => array($this, 'cloud_permission')),
        ));
        register_rest_route('sc-workspace/v1', '/readiness-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'readiness_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/public-beta-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'public_beta_contract'),
            'permission_callback' => '__return_true',
        ));
        register_rest_route('sc-workspace/v1', '/field-diagnostics-contract', array(
            'methods' => 'GET',
            'callback' => array($this, 'field_diagnostics_contract'),
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
            'persistence' => 'browser-local-projects-v27-plus-human-declared-lifecycle-derived-governance-audit-guided-reconciliation-change-gates-version-history-account-backup-and-explicit-conflict-safe-sync',
            'project_schema' => 'sc-workspace-project/20.0',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'identity_schema' => 'sc-workspace-identity/1.0',
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'decision_schema' => 'sc-workspace-decision/1.0',
            'project_lifecycle_schema' => 'sc-workspace-project-lifecycle/1.0',
            'governance_milestone_schema' => 'sc-workspace-governance-milestone/1.0',
            'canvas_schema' => 'sc-workspace-canvas/1.0',
            'handoff_schema' => 'sc-workspace-handoff/2.0',
            'handoff_ledger_schema' => 'sc-workspace-handoff-ledger/1.0',
            'handoff_return_schema' => 'sc-workspace-handoff-return/1.0',
            'return_adapter_schema' => 'sc-workspace-return-adapter/1.0',
            'traceability_schema' => 'sc-workspace-traceability/1.0',
            'briefing_schema' => 'sc-workspace-briefing/1.0',
            'guided_workflows_schema' => 'sc-workspace-guided-workflows/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'integrated_knowledge_schema' => 'sc-workspace-integrated-knowledge/1.0',
            'knowledge_search_schema' => 'sc-workspace-knowledge-search/1.0',
            'saved_search_schema' => 'sc-workspace-saved-search/1.0',
            'knowledge_graph_schema' => 'sc-workspace-knowledge-graph/2.0',
            'relationship_explorer_schema' => 'sc-workspace-relationship-explorer/1.0',
            'cross_project_knowledge_schema' => 'sc-workspace-cross-project-knowledge/1.0',
            'grounded_research_assistant_schema' => 'sc-workspace-grounded-research-assistant/1.0',
            'grounded_research_request_schema' => 'sc-workspace-grounded-research-request/1.0',
            'grounded_research_response_schema' => 'sc-workspace-grounded-research-response/1.0',
            'activity_intelligence_schema' => 'sc-workspace-activity-intelligence/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'institutional_handoff_schema' => 'sc-workspace-institutional-handoff/1.0',
            'institutional_handoff_package_schema' => 'sc-workspace-institutional-handoff-package/1.0',
            'institutional_handoff_receipt_schema' => 'sc-workspace-institutional-handoff-receipt/1.0',
            'ai_assistance_schema' => 'sc-workspace-ai-assistance/1.0',
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/2.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'publication_export_schema' => 'sc-workspace-publication-export/1.0',
            'reproducibility_export_schema' => 'sc-workspace-reproducibility-export/1.0',
            'return_adapter_transport' => array('session-storage', 'same-origin-postmessage', 'portable-json'),
            'authentication_provider' => 'wordpress',
            'anonymous_workspace_supported' => true,
            'storage_schema_version' => 35,
            'server_project_storage' => 'manual-backup-plus-explicit-sync-head',
            'cloud_sync' => 'explicit-project-enrollment',
            'cross_device_sync_schema' => 'sc-workspace-cross-device-sync/1.0',
            'version_history_schema' => 'sc-workspace-version-history/1.0',
            'restore_point_schema' => 'sc-workspace-restore-point/1.0',
            'safe_actions_schema' => 'sc-workspace-safe-actions/1.0',
            'action_gate_schema' => 'sc-workspace-action-gate/1.0',
            'change_gates' => 'required-for-high-risk-actions',
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
            'schema' => 'sc-workspace-project-contract/20.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/20.0',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0',
            'notebook_schema' => 'sc-workspace-notebook/3.0',
            'notebook_block_schema' => 'sc-workspace-notebook-block/3.0',
            'notebook_link_schema' => 'sc-workspace-notebook-link/1.0',
            'notebook_collection_schema' => 'sc-workspace-notebook-collection/1.0',
            'notebook_ref_schema' => 'sc-workspace-notebook-ref/1.0',
            'notebook_promotion_schema' => 'sc-workspace-notebook-promotion/1.0',
            'notebook_synthesis_schema' => 'sc-workspace-notebook-synthesis/1.0',
            'notebook_synthesis_export_schema' => 'sc-workspace-notebook-synthesis-export/1.0',
            'notebook_assistance_schema' => 'sc-workspace-notebook-assistance/1.0',
            'notebook_assistance_request_export_schema' => 'sc-workspace-notebook-assistance-request-export/1.0',
            'notebook_assistance_response_export_schema' => 'sc-workspace-notebook-assistance-response-export/1.0',
            'notebook_change_review_schema' => 'sc-workspace-notebook-change-review/1.0',
            'notebook_reconciliation_schema' => 'sc-workspace-notebook-reconciliation/1.0',
            'notebook_audit_event_schema' => 'sc-workspace-notebook-audit-event/1.0',
            'notebook_lineage_schema' => 'sc-workspace-notebook-lineage/1.0',
            'notebook_governance_schema' => 'sc-workspace-notebook-governance/1.0',
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'decision_schema' => 'sc-workspace-decision/1.0',
            'project_lifecycle_schema' => 'sc-workspace-project-lifecycle/1.0',
            'governance_milestone_schema' => 'sc-workspace-governance-milestone/1.0',
            'canvas_schema' => 'sc-workspace-canvas/1.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'storage_schema_version' => 35,
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
            'integrated_knowledge_schema' => 'sc-workspace-integrated-knowledge/1.0',
            'knowledge_search_schema' => 'sc-workspace-knowledge-search/1.0',
            'saved_search_schema' => 'sc-workspace-saved-search/1.0',
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


    public function notebook_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-notebook-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/20.0',
            'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0',
            'notebook_schema' => 'sc-workspace-notebook/3.0',
            'notebook_block_schema' => 'sc-workspace-notebook-block/3.0',
            'notebook_export_schema' => 'sc-workspace-notebook-export/8.0',
            'notebook_link_schema' => 'sc-workspace-notebook-link/1.0',
            'notebook_collection_schema' => 'sc-workspace-notebook-collection/1.0',
            'notebook_ref_schema' => 'sc-workspace-notebook-ref/1.0',
            'notebook_promotion_schema' => 'sc-workspace-notebook-promotion/1.0',
            'notebook_synthesis_schema' => 'sc-workspace-notebook-synthesis/1.0',
            'notebook_synthesis_export_schema' => 'sc-workspace-notebook-synthesis-export/1.0',
            'notebook_assistance_schema' => 'sc-workspace-notebook-assistance/1.0',
            'notebook_assistance_request_export_schema' => 'sc-workspace-notebook-assistance-request-export/1.0',
            'notebook_assistance_response_export_schema' => 'sc-workspace-notebook-assistance-response-export/1.0',
            'notebook_change_review_schema' => 'sc-workspace-notebook-change-review/1.0',
            'notebook_reconciliation_schema' => 'sc-workspace-notebook-reconciliation/1.0',
            'notebook_audit_event_schema' => 'sc-workspace-notebook-audit-event/1.0',
            'notebook_lineage_schema' => 'sc-workspace-notebook-lineage/1.0',
            'notebook_governance_schema' => 'sc-workspace-notebook-governance/1.0',
            'block_types' => array('note', 'source', 'excerpt', 'question', 'claim', 'reference', 'checklist', 'divider', 'attachment'),
            'limits' => array(
                'notebooks_per_project' => 30,
                'sections_per_notebook' => 40,
                'blocks_per_notebook' => 300,
                'blocks_per_project' => 600,
                'collections_per_project' => 40,
                'items_per_collection' => 200,
                'links_per_project' => 400,
                'promotions_per_project' => 500,
                'syntheses_per_project' => 120,
                'items_per_synthesis' => 120,
                'assistances_per_project' => 120,
                'items_per_assistance' => 48,
            ),
            'promotion_targets' => array('source', 'evidence', 'dataset', 'analysis', 'decision', 'document', 'canvas'),
            'synthesis_kinds' => array('outline', 'citation-pack', 'source-matrix', 'evidence-summary', 'research-synthesis'),
            'synthesis_requires_explicit_selection' => true,
            'citation_guessing' => false,
            'missing_citation_facts_remain_missing' => true,
            'portable_synthesis_export' => true,
            'grounded_assistance_requires_explicit_selection' => true,
            'grounded_assistance_question_required' => true,
            'grounded_assistance_citations_required' => true,
            'grounded_assistance_citations_limited_to_selected_material' => true,
            'grounded_assistance_invalid_citation_markers_rejected' => true,
            'grounded_assistance_output_is_reviewable_draft' => true,
            'grounded_assistance_automatic_submission' => false,
            'grounded_assistance_automatic_acceptance' => false,
            'grounded_assistance_automatic_materialization' => false,
            'grounded_assistance_provider_neutral' => true,
            'grounded_assistance_portable_request_response' => true,
            'promotion' => array(
                'note' => 'document',
                'source' => 'source',
                'excerpt' => 'evidence',
                'question' => 'analysis',
                'claim' => 'analysis',
                'checklist' => 'document',
                'attachment' => 'source',
                'reference' => 'source',
                'divider' => 'none',
            ),
            'project_bound' => true,
            'multiple_notebooks_per_project' => true,
            'sections_reorderable' => true,
            'blocks_reorderable' => true,
            'portable_notebook_export' => true,
            'account_backup_inherits_project_boundary' => true,
            'cross_device_sync_inherits_project_boundary' => true,
            'portable_notebook_package_schema' => 'sc-workspace-notebook-portable-package/1.0',
            'notebook_restore_point_schema' => 'sc-workspace-notebook-restore-point/1.0',
            'notebook_cloud_backup_schema' => 'sc-workspace-notebook-cloud-backup/1.0',
            'notebook_sync_enrollment_schema' => 'sc-workspace-notebook-sync-enrollment/1.0',
            'notebook_sync_push_schema' => 'sc-workspace-notebook-sync-push/1.0',
            'notebook_import_mode' => 'new-notebook-copy',
            'notebook_sync_requires_explicit_enrollment' => true,
            'notebook_sync_revision_precondition' => true,
            'notebook_sync_conflicts_preserve_both' => true,
            'notebook_background_sync' => false,
            'notebook_silent_last_write_wins' => false,
            'notebook_change_review_explicit' => true,
            'notebook_change_review_hidden_score' => false,
            'notebook_reconciliation_explicit_selection' => true,
            'notebook_reconciliation_new_copy_only' => true,
            'notebook_audit_history_derived' => true,
            'notebook_audit_shadow_database' => false,
            'notebook_lineage_derived_from_authoritative_records' => true,
            'notebook_lineage_automatic_inference' => false,
            'restore_points_include_notebooks' => true,
            'automatic_promotion' => false,
            'promotion_requires_explicit_destination' => true,
            'promotion_preserves_original_notebook_material' => true,
            'multiple_derivatives_per_block' => true,
            'promotion_lineage_visible' => true,
            'automatic_ai' => false,
            'ai_required' => false,
            'source_project_mutation_on_export' => false,
            'bibliographic_context_schema' => 'sc-workspace-bibliographic-context/1.0',
            'source_capture_schema' => 'sc-workspace-source-capture/1.0',
            'capture_request_schema' => 'sc-workspace-notebook-capture-request/1.0',
            'capture_provenance_retained' => true,
            'automatic_metadata_fetch' => false,
            'explicit_cross_notebook_links' => true,
            'backlinks_derived_from_explicit_links' => true,
            'collections_support_notebooks_blocks_and_objects' => true,
            'automatic_link_inference' => false,
        ));
    }

    public function source_capture_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-source-capture-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/20.0',
            'capture_inbox_schema' => 'sc-workspace-source-capture-inbox/1.0',
            'capture_request_schema' => 'sc-workspace-notebook-capture-request/1.0',
            'capture_provenance_schema' => 'sc-workspace-source-capture/1.0',
            'bibliographic_context_schema' => 'sc-workspace-bibliographic-context/1.0',
            'notebook_block_schema' => 'sc-workspace-notebook-block/3.0',
            'source_surfaces' => array('manual', 'knowledge-library', 'research-librarian', 'external-web', 'document', 'workspace-object', 'other'),
            'capture_types' => array('source', 'excerpt', 'note', 'question', 'claim', 'reference', 'attachment'),
            'max_inbox_requests' => 100,
            'same_origin_session_staging' => true,
            'same_origin_post_message' => true,
            'portable_json_capture_request' => true,
            'research_content_in_handoff_url' => false,
            'incoming_capture_requires_explicit_save' => true,
            'automatic_remote_fetch' => false,
            'automatic_page_scraping' => false,
            'automatic_metadata_inference' => false,
            'automatic_ai' => false,
            'automatic_upload' => false,
        ));
    }


    public function analysis_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-analysis-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'analysis_schema' => 'sc-workspace-analysis/1.0',
            'project_schema' => 'sc-workspace-project/20.0',
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
            'project_schema' => 'sc-workspace-project/20.0',
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
            'project_schema' => 'sc-workspace-project/20.0',
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
            'project_schema' => 'sc-workspace-project/20.0',
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
            'project_schema' => 'sc-workspace-project/20.0',
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
            'project_schema' => 'sc-workspace-project/20.0',
            'storage_schema_version' => 35,
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
            'project_schema' => 'sc-workspace-project/20.0',
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


    public function integrated_knowledge_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-integrated-knowledge-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'integrated_knowledge_schema' => 'sc-workspace-integrated-knowledge/1.0',
            'integrated_ref_schema' => 'sc-workspace-integrated-knowledge-ref/1.0',
            'sources' => array('research-notebook','personal-knowledge','research-workspace'),
            'entry_kinds' => array('object','notebook','notebook-block','research-question','research-claim'),
            'derived_from_canonical_records' => true,
            'duplicates_canonical_content' => false,
            'automatic_semantic_inference' => false,
            'automatic_ai' => false,
            'automatic_mutation' => false,
            'canonical_origin_handoff' => true,
            'local_first' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'notebook_workspace_schema' => 'sc-workspace-notebook-workspace/8.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
        ));
    }



    public function knowledge_search_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-knowledge-search-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'search_schema' => 'sc-workspace-knowledge-search/1.0',
            'saved_search_schema' => 'sc-workspace-saved-search/1.0',
            'corpus' => 'derived-integrated-knowledge-index',
            'cross_project' => true,
            'fields' => array('query','kind','subtype','project','tag','origin','provenance','scope','sort'),
            'provenance_filters' => array('all','documented','linked','source-url','bibliographic'),
            'sorts' => array('relevance','updated-desc','updated-asc','title-asc','project-asc'),
            'saved_searches' => 'browser-local-preferences',
            'ranking' => 'deterministic-explainable-field-match-plus-recorded-provenance',
            'ranking_reasons_visible' => true,
            'hidden_relevance_score' => false,
            'related_material_requires_recorded_relationship_or_provenance' => true,
            'server_index' => false,
            'semantic_embeddings' => false,
            'automatic_ai' => false,
            'automatic_relationship_inference' => false,
            'automatic_semantic_similarity_edges' => false,
            'graph_persistence' => 'derived-at-runtime',
            'canonical_record_mutation' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


    public function research_collections_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-research-collections-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'collection_schema' => 'sc-workspace-research-collection/1.0',
            'view_schema' => 'sc-workspace-research-view/1.0',
            'corpus' => 'derived-integrated-knowledge-index',
            'membership' => 'dynamic-query-evaluation',
            'storage' => 'browser-local-definitions-only',
            'max_smart_collections' => 30,
            'max_saved_views' => 30,
            'builtin_views' => array('sources','evidence','decisions','analysis','notebooks','documented'),
            'groupings' => array('none','project','kind','subtype','origin'),
            'densities' => array('compact','comfortable'),
            'dashboard_derived' => true,
            'project_lens_preserved' => true,
            'canonical_records_copied' => false,
            'membership_snapshots_stored' => false,
            'server_collection_index' => false,
            'semantic_inference' => false,
            'automatic_ai' => false,
            'canonical_record_mutation' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


    public function citation_library_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-citation-library-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'reference_schema' => 'sc-workspace-reference/1.0',
            'library_schema' => 'sc-workspace-reference-library/1.0',
            'preferences_schema' => 'sc-workspace-citation-preferences/1.0',
            'export_schema' => 'sc-workspace-reference-library-export/1.0',
            'storage' => 'browser-local-workspace-library',
            'max_references' => 1500,
            'styles' => array('apa7','chicago-author-date','mla9','ieee'),
            'duplicate_detection' => array('normalized-doi','bibliographic-fingerprint'),
            'citation_keys' => 'deterministic-local-collision-safe',
            'canonical_origin_refs' => true,
            'metadata_lookup' => false,
            'metadata_inference' => false,
            'automatic_deduplication' => false,
            'automatic_project_mutation' => false,
            'automatic_ai' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


    public function composition_studio_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-composition-studio-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'section_schema' => 'sc-workspace-composition-section/1.0',
            'draft_schema' => 'sc-workspace-composition-draft/1.0',
            'library_schema' => 'sc-workspace-composition-library/1.0',
            'export_schema' => 'sc-workspace-composition-export/1.0',
            'storage' => 'browser-local-composition-library',
            'max_drafts' => 80,
            'max_sections_per_draft' => 80,
            'canonical_inputs' => array('workspace-object','notebook','notebook-block','research-question','research-claim'),
            'citation_source' => 'citation-library-explicit-reference-selection',
            'document_materialization' => 'explicit-human-action',
            'materialized_object_type' => 'document',
            'source_records_copied' => false,
            'automatic_document_creation' => false,
            'automatic_ai' => false,
            'citation_inference' => false,
            'canonical_source_mutation' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


    public function navigation_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-navigation-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'navigation_schema' => 'sc-workspace-navigation-map/1.0',
            'primary_areas' => array('start','projects','research','review','exchange'),
            'routes' => array(
                'start' => array('start'),
                'projects' => array('projects'),
                'research' => array('research','notebook','knowledge','graph'),
                'review' => array('activity','lifecycle','history','changes','reconcile','safety','audit','automation'),
                'exchange' => array('interoperability','collaboration','api-embed','institutional','share'),
            ),
            'derived_from_existing_surfaces' => true,
            'moves_canonical_data' => false,
            'duplicates_canonical_content' => false,
            'specialized_surfaces_retained' => true,
            'automatic_semantic_inference' => false,
            'automatic_ai' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


public function research_templates_contract() {
    return rest_ensure_response(array(
        'schema' => 'sc-workspace-research-templates-contract/1.0',
        'workspace_version' => SC_WORKSPACE_VERSION,
        'research_template_library_schema' => 'sc-workspace-research-template-library/1.0',
        'research_template_schema' => 'sc-workspace-research-template/1.0',
        'research_template_export_schema' => 'sc-workspace-research-template-export/1.0',
        'built_in_templates' => 8,
        'supports_project_starters' => true,
        'supports_notebook_scaffolds' => true,
        'supports_guided_workflow_scaffolds' => true,
        'supports_optional_empty_starter_objects' => true,
        'custom_templates_browser_local' => true,
        'template_instantiation_requires_user_action' => true,
        'templates_store_project_content' => false,
        'templates_store_notebook_content' => false,
        'templates_store_findings' => false,
        'templates_copy_completion_status' => false,
        'automatic_step_completion' => false,
        'automatic_ai' => false,
    ));
}

    public function experience_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-experience-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'experience_schema' => 'sc-workspace-experience/1.0',
            'preferences_schema' => 'sc-workspace-experience-preferences/1.0',
            'primary_areas' => array('start','projects','research','review','exchange'),
            'density_modes' => array('comfortable','compact'),
            'command_palette' => true,
            'command_shortcut' => 'Ctrl/Meta+K',
            'primary_area_shortcuts' => array('Alt+1','Alt+2','Alt+3','Alt+4','Alt+5'),
            'current_view_search_shortcut' => '/',
            'terminology_help' => true,
            'responsive_horizontal_primary_nav' => true,
            'minimum_control_target_px' => 44,
            'editorial_header_rule_px' => 4,
            'preferences_storage' => 'browser-local',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration' => false,
            'canonical_data_mutation' => false,
            'automatic_navigation' => false,
            'automatic_project_creation' => false,
            'automatic_ai' => false,
        ));
    }


    public function research_tasks_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-research-tasks-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'task_schema' => 'sc-workspace-research-task/1.0',
            'library_schema' => 'sc-workspace-research-task-library/1.0',
            'export_schema' => 'sc-workspace-research-task-export/1.0',
            'target_corpus' => 'derived-integrated-knowledge-index',
            'storage' => 'browser-local',
            'task_types' => array('review-needed', 'verify-claim', 'source-required', 'citation-incomplete', 'ready-for-synthesis', 'follow-up', 'custom'),
            'states' => array('open', 'in-progress', 'blocked', 'done', 'dismissed'),
            'priorities' => array('low', 'normal', 'high', 'critical'),
            'explicit_history' => true,
            'unresolved_references_visible' => true,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration' => false,
            'automatic_task_creation' => false,
            'automatic_completion' => false,
            'automatic_ai' => false,
            'automatic_canonical_mutation' => false,
        ));
    }

    public function collaboration_architecture_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-collaboration-architecture-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'architecture_schema' => 'sc-workspace-collaboration-architecture/1.0',
            'actor_schema' => 'sc-workspace-collaboration-actor/1.0',
            'policy_schema' => 'sc-workspace-collaboration-policy/1.0',
            'comment_schema' => 'sc-workspace-collaboration-comment/1.0',
            'proposal_schema' => 'sc-workspace-collaboration-proposal/1.0',
            'shareable_project_contract_schema' => 'sc-workspace-shareable-project-contract/1.0',
            'roles' => array('owner','editor','contributor','reviewer','observer'),
            'proposal_states' => array('draft','submitted','accepted','rejected','withdrawn'),
            'storage' => 'browser-local',
            'project_ownership_explicit' => true,
            'capability_grants_descriptive' => true,
            'comments_reference_canonical_targets' => true,
            'proposal_acceptance_applies_canonical_change' => false,
            'shareable_contract_includes_project_content' => false,
            'server_permissions' => false,
            'live_coediting' => false,
            'organization_membership' => false,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }

    public function shared_review_handoff_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-shared-review-handoff-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'handoff_schema' => 'sc-workspace-shared-review-handoff/1.0',
            'package_schema' => 'sc-workspace-shared-review-package/1.0',
            'response_schema' => 'sc-workspace-shared-review-response/1.0',
            'ledger_schema' => 'sc-workspace-shared-review-ledger/1.0',
            'storage' => 'browser-local',
            'scope_selection' => 'explicit-project-object-ids',
            'scope_snapshot' => 'frozen-selected-object-copy',
            'package_fingerprint_required' => true,
            'response_must_match_package' => true,
            'response_import' => 'stage-before-commit',
            'comments_merge_into_collaboration_ledger' => true,
            'proposals_merge_into_collaboration_ledger' => true,
            'proposal_acceptance_applies_change' => false,
            'automatic_canonical_mutation' => false,
            'automatic_external_send' => false,
            'live_coediting' => false,
            'server_collaboration' => false,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }

    public function api_embed_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-api-embed-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'durable_reference_schema' => 'sc-workspace-durable-reference/1.0',
            'readonly_projection_schema' => 'sc-workspace-readonly-projection/1.0',
            'readonly_api_envelope_schema' => 'sc-workspace-readonly-api-envelope/1.0',
            'embed_descriptor_schema' => 'sc-workspace-embed-descriptor/1.0',
            'renderer_script' => sc_workspace_api_embed_script_url(),
            'canonical_workspace_default' => 'private-browser-local',
            'public_disclosure' => 'explicit-static-projection-only',
            'durable_reference_format' => 'scw://project/{project_id}/{kind}/{id}',
            'durable_reference_is_authorization' => false,
            'read_only' => true,
            'live_server_project_api' => false,
            'server_project_discovery' => false,
            'automatic_publication' => false,
            'automatic_refresh' => false,
            'automatic_canonical_mutation' => false,
            'credentialed_fetch' => false,
            'post_message_bridge' => false,
            'remote_write' => false,
            'fail_closed_invalid_embed' => true,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }

    public function api_embed_hardening_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-api-embed-hardening/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'readonly_api_envelope_schema' => 'sc-workspace-readonly-api-envelope/1.0',
            'embed_descriptor_schema' => 'sc-workspace-embed-descriptor/1.0',
            'safety_report_schema' => 'sc-workspace-integration-safety-report/1.0',
            'max_embed_payload_bytes' => 98304,
            'max_api_payload_bytes' => 131072,
            'trusted_renderer_transport' => 'https-with-localhost-development-exception',
            'renderer_origin_must_match_configured_origin' => true,
            'integrity_verification_before_export' => true,
            'fail_closed_rendering' => true,
            'credentialed_fetch' => false,
            'post_message_bridge' => false,
            'remote_write' => false,
            'live_server_project_api' => false,
            'canonical_mutation' => false,
            'automatic_publication' => false,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }

    public function research_automation_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-research-automation-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'library_schema' => 'sc-workspace-research-automation/1.0',
            'routine_schema' => 'sc-workspace-research-automation-routine/1.0',
            'run_schema' => 'sc-workspace-research-automation-run/1.0',
            'export_schema' => 'sc-workspace-research-automation-export/1.0',
            'storage' => 'browser-local',
            'routine_types' => array('recurring-import','source-review','verification-check','synthesis-refresh','workflow-action'),
            'cadences' => array('on-demand','daily','weekly','monthly'),
            'schedule_is_declaration' => true,
            'manual_execution_only' => true,
            'background_execution' => false,
            'automatic_network_request' => false,
            'automatic_canonical_mutation' => false,
            'automatic_task_creation' => false,
            'automatic_ai' => false,
            'review_required' => true,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }


    public function institutional_research_packages_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-institutional-research-packages-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'package_schema' => 'sc-workspace-institutional-research-package/1.0',
            'manifest_schema' => 'sc-workspace-institutional-research-package-manifest/1.0',
            'library_schema' => 'sc-workspace-institutional-research-package-library/1.0',
            'export_schema' => 'sc-workspace-institutional-research-package-export/1.0',
            'storage' => 'browser-local',
            'scope_selection' => 'explicit-selected-integrated-knowledge-records',
            'package_state' => 'frozen-disclosure-artifact',
            'optional_context' => array('citations','provenance','research-tasks','collaboration-review'),
            'source_project_unchanged' => true,
            'automatic_publication' => false,
            'automatic_upload' => false,
            'automatic_refresh' => false,
            'automatic_canonical_mutation' => false,
            'organization_access_control' => false,
            'receiver_governance_begins_after_transfer' => true,
            'legacy_institutional_handoff_retained' => true,
            'schema_migration' => false,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
        ));
    }

    public function institutional_validation_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-institutional-transfer-validation/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Institutional Package & Handoff Validation',
            'report_schema' => 'sc-workspace-institutional-validation-report/1.0',
            'policy_schema' => 'sc-workspace-institutional-handoff-validation-policy/1.0',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'package_scope_exact_match_required' => true,
            'recipient_required' => true,
            'purpose_required' => true,
            'source_revision_staleness_detected' => true,
            'stale_transfer_requires_human_acknowledgement' => true,
            'promotion_package_sha256_required' => true,
            'receipt_handoff_project_match_required' => true,
            'duplicate_receipt_blocked' => true,
            'unsigned_receipt_requires_human_acknowledgement' => true,
            'readiness_is_explainable_not_scored' => true,
            'source_workspace_retains_independent_copy' => true,
            'automatic_upload' => false,
            'automatic_institutional_ingestion' => false,
            'automatic_source_mutation' => false,
            'organization_permissions_in_workspace' => false,
        ));
    }

    public function grounded_research_assistant_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-grounded-research-assistant-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'assistant_schema' => 'sc-workspace-grounded-research-assistant/1.0',
            'request_schema' => 'sc-workspace-grounded-research-request/1.0',
            'response_schema' => 'sc-workspace-grounded-research-response/1.0',
            'request_export_schema' => 'sc-workspace-grounded-research-request-export/1.0',
            'response_export_schema' => 'sc-workspace-grounded-research-response-export/1.0',
            'corpus' => 'derived-integrated-knowledge-index',
            'scope_selection' => 'explicit-multi-record',
            'grounding_packet' => 'frozen-bounded-snapshot-with-fingerprint',
            'citation_format' => '[n]',
            'citation_enforcement' => true,
            'substantive_segment_citation_required' => true,
            'provider_neutral' => true,
            'browser_local_library' => true,
            'human_review_required' => true,
            'materialization' => 'explicit-document-only',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration' => false,
            'automatic_ai' => false,
            'automatic_scope_expansion' => false,
            'metadata_invention' => false,
            'automatic_canonical_mutation' => false,
        ));
    }

    public function cross_project_knowledge_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-cross-project-knowledge-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'cross_project_knowledge_schema' => 'sc-workspace-cross-project-knowledge/1.0',
            'cross_project_reference_schema' => 'sc-workspace-cross-project-reference/1.0',
            'cross_project_export_schema' => 'sc-workspace-cross-project-knowledge-export/1.0',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'browser_local_reference_ledger' => true,
            'canonical_source_pointers_only' => true,
            'explicit_target_project_required' => true,
            'same_project_reference_rejected' => true,
            'unresolved_references_remain_visible' => true,
            'integrates_with_research_graph' => true,
            'copies_canonical_content' => false,
            'automatic_relationship_inference' => false,
            'automatic_content_copy' => false,
            'automatic_canonical_mutation' => false,
            'local_first' => true,
        ));
    }

    public function knowledge_graph_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-knowledge-graph-contract/2.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'knowledge_graph_schema' => 'sc-workspace-knowledge-graph/2.0',
            'relationship_explorer_schema' => 'sc-workspace-relationship-explorer/1.0',
            'activity_intelligence_schema' => 'sc-workspace-activity-intelligence/1.0',
            'collaboration_schema' => 'sc-workspace-collaboration/1.0',
            'review_package_schema' => 'sc-workspace-review-package/1.0',
            'personal_knowledge_schema' => 'sc-workspace-personal-knowledge/1.0',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'node_types' => array('project','provenance','source','evidence','dataset','analysis','decision','document','export','notebook','notebook-block','research-question','research-claim','reference','synthesis','canvas-node'),
            'relationship_types' => array('contains','sourced-from','same-source','evidence-from','uses','informs','supports','contrasts','extends','related','references','contradicts','derived-from','produced-by','supersedes','cites','cited-as','promoted-to','synthesized-into','supports-claim','captured-from'),
            'derived_from_canonical_objects' => true,
            'includes_notebook_material' => true,
            'includes_citation_library_origins' => true,
            'includes_cross_project_references' => true,
            'includes_promotion_lineage' => true,
            'includes_synthesis_usage' => true,
            'backlinks_from_explicit_notebook_links' => true,
            'duplicates_object_content' => false,
            'focus_neighborhood_depths' => array(1,2),
            'transparent_relationship_labels' => true,
            'semantic_embeddings' => false,
            'server_graph_database' => false,
            'server_search_index' => false,
            'automatic_relationship_inference' => false,
            'automatic_semantic_similarity_edges' => false,
            'graph_persistence' => 'derived-at-runtime',
            'local_first' => true,
        ));
    }

    public function ai_assistance_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-ai-assistance-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'schema' => 'sc-workspace-interoperability-contract/2.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'interoperability_schema' => 'sc-workspace-interoperability/1.0',
            'interchange_export_schema' => 'sc-workspace-interchange/2.0',
            'share_schema' => 'sc-workspace-share/1.0',
            'portable_project_schema' => 'sc-workspace-portable-project/1.0',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'accepted_formats' => array('json','csv','tsv','markdown','html','text'),
            'interchange_profiles' => array('workspace-json','obsidian-markdown','notion-csv','zotero-csl-json','portable-project'),
            'profile_schema' => 'sc-workspace-interchange-profile/1.0',
            'import_report_schema' => 'sc-workspace-interchange-import-report/1.0',
            'profile_detection' => 'deterministic-local',
            'obsidian_front_matter_supported' => true,
            'notion_column_aliases_supported' => true,
            'zotero_csl_json_supported' => true,
            'external_network_lookup' => false,
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
            'multi_profile_export_supported' => true,
            'portable_project_export_supported' => true,
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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
            'pull_creates_sync_safety_restore_point' => true,
            'idempotent_operation_retry' => true,
            'interrupted_sync_reconciliation' => true,
            'accepting_local_requires_explicit_confirmation' => true,
            'integrity_algorithm' => 'SHA-256',
            'server_store' => 'wordpress-user-meta',
            'team_sync' => false,
            'institutional_sync' => false,
            'project_change_review' => true,
            'change_review_automatic_apply' => false,
            'change_review_hidden_score' => false,
        ));
    }

    public function continuity_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-cross-device-continuity-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'continuity_schema' => 'sc-workspace-cross-device-continuity/1.0',
            'operation_schema' => 'sc-workspace-sync-operation/1.0',
            'migration_schema' => 'sc-workspace-device-migration/1.0',
            'schema_migration_required' => false,
            'revision_precondition_required' => true,
            'idempotent_sync_operation_id' => true,
            'interrupted_operation_reconciliation' => true,
            'pull_creates_sync_safety_restore_point' => true,
            'restore_mode' => 'new-local-copy',
            'device_migration_import_mode' => 'new-local-copy',
            'device_migration_transfers_sync_enrollment' => false,
            'duplicate_migration_guard' => true,
            'manual_backup_can_overwrite_sync_head' => false,
            'automatic_sync' => false,
            'background_sync' => false,
            'device_identity_in_migration_package' => false,
            'account_profile_in_migration_package' => false,
        ));
    }

    public function version_history_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-version-history-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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

    public function change_review_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-change-review-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'change_review_schema' => 'sc-workspace-change-review/1.0',
            'comparison_sources' => array('current-project', 'restore-point', 'cloud-revision'),
            'review_categories' => array('project-metadata','canonical-objects','research','evidence','analysis','decisions','traceability','canvas','briefing','guided-workflows'),
            'relationship_changes_explicit' => true,
            'automatic_apply' => false,
            'automatic_restore' => false,
            'automatic_sync' => false,
            'hidden_change_score' => false,
            'project_schema_changes' => false,
            'storage_schema_changes' => false,
            'exportable_json_review' => true,
        ));
    }

    public function safe_actions_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-safe-actions-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'safe_actions_schema' => 'sc-workspace-safe-actions/1.0',
            'action_gate_schema' => 'sc-workspace-action-gate/1.0',
            'gated_actions' => array('restore-copy','sync-resolve-local','sync-resolve-cloud','share-portable','share-review-copy','institutional-promotion'),
            'change_review_preflight' => true,
            'human_acknowledgement_required' => true,
            'automatic_proceed' => false,
            'automatic_apply' => false,
            'automatic_merge' => false,
            'hidden_risk_score' => false,
            'gate_history_scope' => 'browser-local-workspace-level',
            'project_schema_changes' => false,
            'conflict_protections_preserved' => true,
            'share_scope_review_required' => true,
            'institutional_scope_review_required' => true,
        ));
    }

    public function reconciliation_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-reconciliation-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'reconciliation_schema' => 'sc-workspace-reconciliation/1.0',
            'plan_schema' => 'sc-workspace-reconciliation-plan/1.0',
            'comparison_engine' => 'sc-workspace-change-review/1.0',
            'selection_required' => true,
            'automatic_selection' => false,
            'automatic_merge' => false,
            'automatic_overwrite' => false,
            'output_mode' => 'new-local-project-copy',
            'source_states_mutated' => false,
            'dependency_validation' => true,
            'human_acknowledgement_required' => true,
            'ledger_scope' => 'browser-local-workspace-level',
            'project_schema_changes' => false,
        ));
    }

    public function reconciliation_receipts_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-reconciliation-receipts-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'receipt_schema' => 'sc-workspace-reconciliation-receipt/1.0',
            'receipt_export_schema' => 'sc-workspace-reconciliation-receipt-export/1.0',
            'accepted_declined_changes_recorded' => true,
            'decision_rationale_required' => true,
            'reviewer_label_user_supplied' => true,
            'sha256_integrity_fingerprint' => true,
            'canonical_document_summary_created' => true,
            'authoritative_ledger_scope' => 'browser-local-workspace-level',
            'receipt_editable_in_workspace' => false,
            'source_states_mutated' => false,
            'account_identity_inferred' => false,
            'automatic_decision_authority' => false,
        ));
    }

    public function audit_trail_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-audit-trail-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'trail_schema' => 'sc-workspace-audit-trail/1.0',
            'event_schema' => 'sc-workspace-audit-event/1.0',
            'export_schema' => 'sc-workspace-audit-export/1.0',
            'derived_from_authoritative_ledgers' => true,
            'stored_shadow_database' => false,
            'event_sources' => array('project-activity','project-lifecycle','version-history','account-recovery','cross-device-sync','safe-actions','reconciliation','collaboration','institutional-handoff','share','interoperability'),
            'chronological_sort' => 'newest-first',
            'project_filter' => true,
            'source_filter' => true,
            'portable_json_export' => true,
            'project_content_in_audit_export' => false,
            'events_editable' => false,
            'hidden_governance_score' => false,
            'schema_migration_required' => true,
        ));
    }

    public function project_lifecycle_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-project-lifecycle-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'lifecycle_schema' => 'sc-workspace-project-lifecycle/1.0',
            'milestone_schema' => 'sc-workspace-governance-milestone/1.0',
            'states' => array('draft','evidence-ready','analysis-ready','decision-ready','review-ready','publication-ready','institutional-ready'),
            'human_declared_state' => true,
            'automatic_advancement' => false,
            'readiness_checklist_derived' => true,
            'hidden_readiness_score' => false,
            'readiness_is_certification' => false,
            'rationale_required' => true,
            'acknowledgement_required' => true,
            'backward_transitions_allowed' => true,
            'milestone_history_portable_with_project' => true,
            'account_identity_inferred' => false,
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
            'lastOperationId' => isset($record['lastOperationId']) ? (string) $record['lastOperationId'] : '',
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
        if (!$project || $project_id === '' || !in_array(($project['schema'] ?? ''), array('sc-workspace-project/20.0','sc-workspace-project/19.0','sc-workspace-project/18.0','sc-workspace-project/17.0','sc-workspace-project/16.0','sc-workspace-project/15.0','sc-workspace-project/14.0','sc-workspace-project/13.0','sc-workspace-project/12.0'), true)) {
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
        $operation_id = $is_sync ? sanitize_text_field((string) ($payload['operationId'] ?? '')) : '';
        if ($is_sync && $operation_id !== '' && $existing && hash_equals((string) ($existing['lastOperationId'] ?? ''), $operation_id)) {
            return rest_ensure_response(array('ok' => true, 'replayed' => true, 'item' => $this->cloud_metadata($existing)));
        }
        if ($is_manual && $existing && (($existing['storageMode'] ?? '') === 'sync-head')) {
            return new WP_Error('scw_manual_backup_sync_head_conflict', 'Manual backup cannot replace an active sync head. Use explicit Sync now so the revision precondition protects the cloud state.', array('status' => 409, 'current' => $this->cloud_metadata($existing)));
        }
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
            'lastOperationId' => $operation_id,
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


    private function cloud_notebook_store_key() { return 'sc_workspace_cloud_notebooks_v1'; }
    private function cloud_notebook_store_read() { $store = get_user_meta(get_current_user_id(), $this->cloud_notebook_store_key(), true); return is_array($store) ? $store : array(); }
    private function cloud_notebook_metadata($record) { return array('notebookId'=>(string)($record['notebookId']??''),'projectId'=>(string)($record['projectId']??''),'title'=>(string)($record['title']??'Research Notebook'),'clientUpdatedAt'=>(string)($record['clientUpdatedAt']??''),'backedUpAt'=>(string)($record['backedUpAt']??''),'fingerprint'=>(string)($record['fingerprint']??''),'notebookFingerprint'=>(string)($record['notebookFingerprint']??''),'revision'=>(int)($record['revision']??0),'storageMode'=>(string)($record['storageMode']??'manual-backup'),'bytes'=>(int)($record['bytes']??0)); }
    public function cloud_notebooks_list() { $items=array(); foreach($this->cloud_notebook_store_read() as $record){ if(is_array($record))$items[]=$this->cloud_notebook_metadata($record); } usort($items,function($a,$b){return strcmp($b['backedUpAt'],$a['backedUpAt']);}); return rest_ensure_response(array('schema'=>'sc-workspace-notebook-cloud-index/1.0','items'=>$items,'automaticSync'=>false,'explicitSync'=>true)); }
    public function cloud_notebook_store($request) {
        $payload=$request->get_json_params(); $schema=is_array($payload)?(string)($payload['schema']??''):''; $manual=$schema==='sc-workspace-notebook-cloud-backup/1.0'; $sync=$schema==='sc-workspace-notebook-sync-push/1.0';
        if(!is_array($payload)||(!$manual&&!$sync))return new WP_Error('scw_invalid_notebook_backup','Unsupported notebook account-persistence package.',array('status'=>400));
        $notebook=is_array($payload['notebook']??null)?$payload['notebook']:null; $id=sanitize_key((string)($payload['sourceNotebookId']??'')); if(!$notebook||$id===''||($notebook['schema']??'')!=='sc-workspace-notebook/3.0')return new WP_Error('scw_invalid_cloud_notebook','A valid Research Notebook is required.',array('status'=>400));
        $canonical=wp_json_encode($payload,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE); $bytes=strlen($canonical); if($bytes>1048576)return new WP_Error('scw_cloud_notebook_too_large','This notebook exceeds the 1 MB account-persistence limit.',array('status'=>413));
        $store=$this->cloud_notebook_store_read(); $existing=isset($store[$id])&&is_array($store[$id])?$store[$id]:null; $revision=$existing?max(0,(int)($existing['revision']??1)):0;
        if($sync){$expected=isset($payload['expectedRevision'])?max(0,(int)$payload['expectedRevision']):-1;if($expected!==$revision)return new WP_Error('scw_notebook_sync_conflict','Notebook sync revision conflict. Nothing was overwritten.',array('status'=>409,'currentRevision'=>$revision,'current'=>$existing?$this->cloud_notebook_metadata($existing):null));}
        if(!$existing&&count($store)>=50)return new WP_Error('scw_cloud_notebook_limit','This account has reached the 50-notebook storage limit.',array('status'=>409));
        $record=array('notebookId'=>$id,'projectId'=>sanitize_key((string)($payload['sourceProjectId']??'')),'title'=>sanitize_text_field((string)($payload['notebookTitle']??$notebook['title']??'Research Notebook')),'clientUpdatedAt'=>sanitize_text_field((string)($payload['clientUpdatedAt']??$notebook['updatedAt']??'')),'backedUpAt'=>gmdate('c'),'fingerprint'=>hash('sha256',$canonical),'notebookFingerprint'=>sanitize_text_field((string)($payload['notebookFingerprint']??hash('sha256',wp_json_encode($notebook,JSON_UNESCAPED_SLASHES|JSON_UNESCAPED_UNICODE)))),'revision'=>$revision+1,'storageMode'=>$sync?'sync-head':'manual-backup','bytes'=>$bytes,'package'=>$payload);
        $store[$id]=$record; update_user_meta(get_current_user_id(),$this->cloud_notebook_store_key(),$store); return rest_ensure_response(array('ok'=>true,'item'=>$this->cloud_notebook_metadata($record)));
    }
    public function cloud_notebook_get($request) { $id=sanitize_key((string)$request['notebook_id']);$store=$this->cloud_notebook_store_read();if(!isset($store[$id])||!is_array($store[$id]))return new WP_Error('scw_cloud_notebook_missing','Notebook account copy not found.',array('status'=>404));$record=$store[$id];return rest_ensure_response(array('schema'=>'sc-workspace-notebook-cloud-backup-response/1.0','item'=>$this->cloud_notebook_metadata($record),'package'=>$record['package'])); }
    public function cloud_notebook_delete($request) { $id=sanitize_key((string)$request['notebook_id']);$store=$this->cloud_notebook_store_read();if(!isset($store[$id]))return rest_ensure_response(array('ok'=>true,'deleted'=>false));unset($store[$id]);update_user_meta(get_current_user_id(),$this->cloud_notebook_store_key(),$store);return rest_ensure_response(array('ok'=>true,'deleted'=>true)); }

    public function readiness_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-release-readiness-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Stability, Accessibility & Release Readiness',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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

    public function public_beta_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-public-beta-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release_stage' => 'public-beta',
            'readiness_schema' => 'sc-workspace-public-beta-readiness/1.0',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'start_view' => true,
            'quick_start_templates' => array('research-investigation','analytical-assessment','decision-case','publication-preparation'),
            'first_project_support' => array(
                'blank_project' => true,
                'guided_project' => true,
                'continue_recent_project' => true,
                'knowledge_library_path' => '/knowledge-libraries/',
            ),
            'runtime_capability_checks' => array('local-storage','session-storage','web-crypto-sha256','file-api','post-message','network-state','reduced-motion'),
            'accessibility' => array(
                'target' => 'WCAG 2.2 AA',
                'keyboard_workspace_navigation' => true,
                'aria_current_view' => true,
                'visible_focus' => true,
                'reduced_motion' => true,
            ),
            'performance' => array(
                'advanced_views_render_on_selection' => true,
                'no_remote_boot_dependency' => true,
                'local_project_list_available_offline_after_page_load' => true,
            ),
            'governance' => array(
                'guest_workspace_supported' => true,
                'login_wall' => false,
                'automatic_cloud_upload' => false,
                'background_sync' => false,
                'automatic_telemetry' => false,
                'hidden_readiness_score' => false,
                'automatic_lifecycle_advance' => false,
            ),
        ));
    }

    public function scale_performance_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-scale-performance-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Scale, Performance & Large-Project Hardening',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'profile_schema' => 'sc-workspace-scale-profile/1.0',
            'budget_schema' => 'sc-workspace-performance-budget/1.0',
            'render_window' => 120,
            'derived_index_cache' => true,
            'storage_pressure_visibility' => true,
            'stress_fixtures' => true,
            'automatic_deletion' => false,
            'automatic_archival' => false,
            'automatic_compaction' => false,
            'automatic_migration' => false,
            'canonical_mutation' => false,
        ));
    }

    public function long_session_performance_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-long-session-performance-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Performance II: Long Sessions & Very Large Workspaces',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'session_schema' => 'sc-workspace-performance-session/1.0',
            'report_schema' => 'sc-workspace-performance-session-report/1.0',
            'bounded_in_memory_samples' => 120,
            'long_task_threshold_ms' => 50,
            'render_attention_ms' => 32,
            'index_attention_ms' => 250,
            'cooperative_chunk_yield' => true,
            'revision_memoization' => true,
            'bounded_render_windows' => true,
            'persistent_profiling' => false,
            'automatic_telemetry' => false,
            'automatic_deletion' => false,
            'automatic_archival' => false,
            'automatic_compaction' => false,
            'automatic_migration' => false,
            'canonical_mutation' => false,
        ));
    }

    public function recovery_disaster_simulation_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-recovery-disaster-simulation-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Product Recovery & Disaster Simulation',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'scenario_schema' => 'sc-workspace-recovery-disaster-scenario/1.0',
            'report_schema' => 'sc-workspace-recovery-disaster-report/1.0',
            'scenario_count' => 8,
            'sandboxed_failure_injection' => true,
            'production_data_injection' => false,
            'automatic_repair' => false,
            'automatic_restore' => false,
            'automatic_import_commit' => false,
            'automatic_sync' => false,
            'background_network' => false,
            'canonical_mutation' => false,
        ));
    }

    public function security_privacy_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-security-privacy-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Security, Privacy & Data-Portability Audit',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'browser_local_primary' => true,
            'application_level_localstorage_encryption' => false,
            'public_project_enumeration' => false,
            'complete_browser_local_portability' => true,
            'verified_browser_local_deletion' => true,
            'server_account_deletion_separate' => true,
            'integrity_fingerprint_is_encryption' => false,
            'durable_reference_is_authorization' => false,
            'automatic_deletion' => false,
            'automatic_upload' => false,
            'canonical_mutation' => false,
        ));
    }

    public function security_privacy_audit_ii_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-security-privacy-audit-ii-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Security & Privacy Audit II',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'audit_schema' => 'sc-workspace-security-privacy-audit-ii/1.0',
            'report_schema' => 'sc-workspace-security-privacy-audit-ii-report/1.0',
            'policy_schema' => 'sc-workspace-security-privacy-audit-ii-policy/1.0',
            'runtime_metadata_only' => true,
            'localstorage_values_exported' => false,
            'sessionstorage_values_exported' => false,
            'cookie_names_exported' => false,
            'cookie_values_exported' => false,
            'project_content_exported' => false,
            'rest_permission_split_audited' => true,
            'public_rest_routes_metadata_only_get' => true,
            'authenticated_cloud_routes_require_nonce_header' => true,
            'authenticated_cloud_routes_same_origin_credentials' => true,
            'dynamic_code_primitives_blocked' => true,
            'secret_literal_scan' => true,
            'external_network_literal_scan' => true,
            'source_audit_is_penetration_test' => false,
            'application_level_localstorage_encryption' => false,
            'automatic_remediation' => false,
            'automatic_deletion' => false,
            'automatic_upload' => false,
            'automatic_disclosure' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
        ));
    }

    public function public_product_beta_ii_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-public-product-beta-ii-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Public Product Beta II',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'beta_schema' => 'sc-workspace-public-beta-ii/1.0',
            'gate_schema' => 'sc-workspace-beta-gate/1.0',
            'field_snapshot_schema' => 'sc-workspace-beta-field-snapshot/1.0',
            'focused_application_shell_required' => true,
            'performance_gate_available' => true,
            'security_privacy_gate_available' => true,
            'recovery_gate_available' => true,
            'privacy_minimized_field_snapshot' => true,
            'hidden_readiness_score' => false,
            'automatic_telemetry' => false,
            'automatic_submission' => false,
            'automatic_repair' => false,
            'canonical_mutation' => false,
        ));
    }

    public function public_product_beta_iii_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-public-product-beta-iii-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Public Product Beta III',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'beta_schema' => 'sc-workspace-public-beta-iii/1.0',
            'checkpoint_schema' => 'sc-workspace-product-journey-checkpoint/1.0',
            'report_schema' => 'sc-workspace-product-journey-report/1.0',
            'journey' => array('discover','capture','organize','analyze','synthesize','decide','compose','review','export-handoff'),
            'journey_step_count' => 9,
            'topology_check_local_only' => true,
            'manual_walkthrough_storage' => 'sessionStorage',
            'manual_walkthrough_persistent' => false,
            'privacy_minimized_report' => true,
            'hidden_readiness_score' => false,
            'automatic_completion' => false,
            'behavioral_tracking' => false,
            'automatic_telemetry' => false,
            'automatic_submission' => false,
            'canonical_mutation' => false,
        ));
    }

    public function first_run_onboarding_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-first-run-onboarding-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'First-Run Onboarding & Project Creation',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'onboarding_schema' => 'sc-workspace-first-run-onboarding/1.0',
            'draft_schema' => 'sc-workspace-first-project-draft/1.0',
            'report_schema' => 'sc-workspace-first-run-onboarding-report/1.0',
            'first_run_detection' => 'zero-local-projects',
            'starter_count' => 5,
            'starters' => array('blank','research-investigation','analytical-assessment','decision-case','publication-preparation'),
            'project_creation' => 'explicit-submit',
            'blank_projects_supported' => true,
            'guest_use_first_class' => true,
            'account_required' => false,
            'automatic_project_creation' => false,
            'automatic_starter_selection' => false,
            'automatic_upload' => false,
            'automatic_sync' => false,
            'automatic_lifecycle_advance' => false,
        ));
    }

    public function workflow_guidance_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-workflow-guidance-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Research Workflow Guidance & Empty-State Refinement',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'guidance_schema' => 'sc-workspace-workflow-guidance/1.0',
            'empty_state_schema' => 'sc-workspace-empty-state-guidance/1.0',
            'report_schema' => 'sc-workspace-workflow-guidance-report/1.0',
            'guidance_mode' => 'derived-contextual-advisory',
            'research_stages' => array('orient','frame','gather','extract','connect','synthesize','compose','review'),
            'canonical_mutation' => false,
            'automatic_completion' => false,
            'automatic_task_creation' => false,
            'automatic_ai' => false,
            'hidden_readiness_score' => false,
            'behavioral_tracking' => false,
            'telemetry' => false,
        ));
    }

    public function collaboration_review_hardening_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-collaboration-review-hardening-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Collaboration & Shared Review Hardening',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'assessment_schema' => 'sc-workspace-shared-review-import-assessment/1.0',
            'receipt_schema' => 'sc-workspace-shared-review-reconciliation-receipt/1.0',
            'source_revision_fingerprint' => true,
            'stale_response_detection' => true,
            'duplicate_response_commit_blocked' => true,
            'stale_response_requires_owner_acknowledgement' => true,
            'legacy_package_revision_state' => 'unverifiable-requires-owner-acknowledgement',
            'reviewer_identity' => 'declarative-not-cryptographically-verified',
            'owner_identity' => 'declarative-not-cryptographically-verified',
            'response_import' => 'stage-assess-explicit-reconcile',
            'reconciliation_receipt' => true,
            'canonical_mutation' => false,
            'proposal_acceptance_applies_change' => false,
            'live_coediting' => false,
            'server_collaboration' => false,
            'automatic_send' => false,
        ));
    }

    public function field_resilience_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-field-resilience-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Product Hardening I — Browser, Recovery & Field-Use Resilience',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'route_state_schema' => 'sc-workspace-route-state/1.0',
            'resilience_schema' => 'sc-workspace-field-resilience/1.0',
            'snapshot_schema' => 'sc-workspace-resilience-snapshot/1.0',
            'safe_route_restore' => true,
            'browser_back_forward' => true,
            'stale_ui_state_sanitization' => true,
            'recovery_state_classification' => true,
            'navigation_reset_only' => true,
            'canonical_mutation' => false,
            'automatic_repair' => false,
            'automatic_upload' => false,
            'telemetry' => false,
        ));
    }

    public function persistence_integrity_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-persistence-integrity-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Product Hardening II — Persistence, Corruption & Recovery Integrity',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'integrity_schema' => 'sc-workspace-persistence-integrity/1.0',
            'transaction_schema' => 'sc-workspace-persistence-transaction/1.0',
            'report_schema' => 'sc-workspace-persistence-integrity-report/1.0',
            'recovery_candidate_schema' => 'sc-workspace-recovery-candidate/1.0',
            'read_after_write_verification' => true,
            'write_transaction_journal' => true,
            'interrupted_write_detection' => true,
            'last_known_good_checksum_binding' => true,
            'integrity_receipt_algorithm' => 'fnv1a32',
            'integrity_receipt_security_claim' => false,
            'explicit_recovery_candidate_export' => true,
            'automatic_restore' => false,
            'automatic_canonical_repair' => false,
            'canonical_mutation' => false,
            'automatic_upload' => false,
            'telemetry' => false,
        ));
    }

    public function compatibility_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-browser-compatibility-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Cross-Browser & Device Compatibility',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'compatibility_schema' => 'sc-workspace-browser-compatibility/1.0',
            'matrix_schema' => 'sc-workspace-browser-compatibility-matrix/1.0',
            'report_schema' => 'sc-workspace-browser-compatibility-report/1.0',
            'target_schema' => 'sc-workspace-browser-targets/1.0',
            'feature_detection_primary' => true,
            'user_agent_feature_gating' => false,
            'file_text_filereader_fallback' => true,
            'blob_object_url_export' => true,
            'bounded_data_uri_export_fallback' => true,
            'guarded_history_api' => true,
            'in_app_navigation_fallback' => true,
            'root_bound_viewport_adapter' => true,
            'embedded_context_detection' => true,
            'touch_pointer_detection' => true,
            'manual_device_qa_required' => true,
            'raw_user_agent_in_report' => false,
            'device_fingerprinting' => false,
            'automatic_upload' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
        ));
    }

    public function accessibility_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-accessibility-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Accessibility & Keyboard-First Product Audit',
            'target' => 'WCAG 2.2 AA',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'accessibility_schema' => 'sc-workspace-accessibility/1.0',
            'report_schema' => 'sc-workspace-accessibility-report/1.0',
            'checklist_schema' => 'sc-workspace-accessibility-checklist/1.0',
            'keyboard_group_navigation' => true,
            'modal_focus_containment' => true,
            'dialog_focus_restoration' => true,
            'escape_close_when_control_available' => true,
            'visible_focus_layer' => true,
            'reduced_motion_layer' => true,
            'forced_colors_layer' => true,
            'zoom_reflow_manual_qa' => true,
            'screen_reader_manual_qa' => true,
            'automated_certification' => false,
            'manual_audit_required' => true,
            'automatic_upload' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
            'hidden_accessibility_score' => false,
        ));
    }

    public function accessibility_performance_final_audit_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-accessibility-performance-final-audit-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Accessibility & Performance Final Audit',
            'target' => 'WCAG 2.2 AA plus bounded field-performance budgets',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'audit_schema' => 'sc-workspace-accessibility-performance-final-audit/1.0',
            'report_schema' => 'sc-workspace-accessibility-performance-final-audit-report/1.0',
            'checklist_schema' => 'sc-workspace-accessibility-performance-final-checklist/1.0',
            'critical_automated_release_gate' => true,
            'manual_field_audit_required' => true,
            'automated_accessibility_certification' => false,
            'automated_performance_certification' => false,
            'existing_accessibility_engine_reused' => true,
            'existing_long_session_monitor_reused' => true,
            'privacy_minimized_report' => true,
            'canonical_mutation' => false,
            'automatic_optimization' => false,
            'automatic_deletion' => false,
            'automatic_upload' => false,
            'telemetry' => false,
        ));
    }

    public function public_beta_iii_defect_closure_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-public-beta-iii-defect-closure-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Public Beta III Defect Closure',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'closure_schema' => 'sc-workspace-public-beta-iii-defect-closure/1.0',
            'report_schema' => 'sc-workspace-public-beta-iii-defect-closure-report/1.0',
            'automated_defect_gate' => true,
            'known_automated_blocker_count' => 0,
            'manual_field_validation_outstanding' => true,
            'manual_items_silently_closed' => false,
            'current_release_consistency_required' => true,
            'wordpress_header_window_required' => true,
            'dependency_cycle_gate_required' => true,
            'security_privacy_gate_required' => true,
            'accessibility_performance_gate_required' => true,
            'beta_iii_topology_gate_required' => true,
            'recovery_disaster_gate_required' => true,
            'no_new_product_subsystem' => true,
            'automatic_repair' => false,
            'automatic_upload' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
        ));
    }


    public function release_candidate_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-release-candidate-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Workspace Release Candidate I',
            'release_candidate' => true,
            'feature_freeze' => true,
            'feature_freeze_policy' => 'defect-fixes-certification-deployment-only',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'project_export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'known_automated_blocker_count' => 0,
            'manual_field_validation_outstanding' => true,
            'package_integrity_required' => true,
            'rollback_artifact_required' => true,
            'automatic_promotion_to_stable' => false,
            'new_product_subsystem' => false,
            'canonical_mutation' => false,
            'telemetry' => false,
        ));
    }


    public function deployment_hardening_contract() {
        return rest_ensure_response(SC_Workspace_Deployment_Hardening::contract());
    }

    public function production_certification_contract() {
        return rest_ensure_response(SC_Workspace_Production_Certification::contract());
    }

    public function production_signoff_contract() {
        return rest_ensure_response(SC_Workspace_Production_Signoff::contract());
    }

    public function ga_readiness_contract() {
        return rest_ensure_response(SC_Workspace_GA_Readiness::contract());
    }

    public function general_availability_contract() {
        return rest_ensure_response(SC_Workspace_General_Availability::contract());
    }

    public function ga_stabilization_contract() {
        return rest_ensure_response(SC_Workspace_GA_Stabilization::contract());
    }

    public function lab_integration_contract() {
        return rest_ensure_response(SC_Workspace_Lab_Integration::contract());
    }

    public function workbench_decision_roundtrip_contract() {
        return rest_ensure_response(SC_Workspace_Workbench_Decision_Roundtrip::contract());
    }

    public function cross_device_production_contract() {
        return rest_ensure_response(SC_Workspace_Cross_Device_Production::contract());
    }

    public function field_use_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-field-use-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Responsive & Field-Use Experience',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'profile_schema' => 'sc-workspace-field-use-profile/1.0',
            'feature_detection_primary' => true,
            'viewport_classes' => array('wide', 'compact', 'narrow'),
            'input_profiles' => array('fine', 'coarse', 'mixed'),
            'short_viewport_detection' => true,
            'touch_safe_targets' => true,
            'tablet_reflow' => true,
            'narrow_window_reflow' => true,
            'phone_priority' => 'capture-review-light-editing',
            'dense_surfaces_remain_available' => true,
            'contextual_lab_handoffs' => true,
            'device_fingerprinting' => false,
            'profile_persistence' => false,
            'automatic_upload' => false,
            'telemetry' => false,
            'canonical_mutation' => false,
            'manual_device_qa_required' => true,
        ));
    }


    public function import_export_compatibility_contract() {
        $project_versions = array('1.0','2.0','3.0','3.1','4.0','5.0','6.0','7.0','8.0','9.0','10.0','11.0','12.0','13.0','14.0','15.0','16.0','17.0','18.0','19.0','20.0');
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-import-export-compatibility-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Import, Export & Backward-Compatibility Hardening',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'export_schema' => 'sc-workspace-project-export/20.0',
            'schema_migration_required' => false,
            'supported_project_schemas' => array_map(function($version) { return 'sc-workspace-project/' . $version; }, $project_versions),
            'supported_export_schemas' => array_map(function($version) { return 'sc-workspace-project-export/' . $version; }, $project_versions),
            'supported_storage_versions' => range(1, 35),
            'project_import_mode' => 'stage-review-new-local-copy',
            'future_project_schema_downgrade' => false,
            'automatic_import_commit' => false,
            'automatic_overwrite' => false,
            'automatic_trust_elevation' => false,
            'server_import_pipeline' => false,
            'external_network_lookup' => false,
            'round_trip_export_check' => true,
            'round_trip_checksum_purpose' => 'drift-detection-only-not-security',
        ));
    }

    public function field_diagnostics_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-field-diagnostics-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'release' => 'Public Beta Hardening & Field Diagnostics',
            'release_stage' => 'public-beta',
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
            'schema_migration_required' => false,
            'diagnostic_schema' => 'sc-workspace-field-diagnostic/1.0',
            'issue_report_schema' => 'sc-workspace-field-report/1.0',
            'deployment_profile_schema' => 'sc-workspace-deployment-profile/1.0',
            'checks' => array(
                'browser-capabilities', 'storage-write-latency', 'workspace-size', 'serialization-latency',
                'parse-latency', 'dom-density', 'last-known-good-recovery', 'deployment-profile',
            ),
            'advisory_thresholds' => array(
                'workspace_bytes' => 4194304,
                'storage_probe_ms' => 100,
                'serialize_ms' => 150,
                'parse_ms' => 150,
                'dom_nodes' => 6000,
            ),
            'issue_reporting' => array(
                'user_generated' => true,
                'export_json' => true,
                'export_text_summary' => true,
                'automatic_submission' => false,
                'project_content_automatically_included' => false,
                'user_entered_text_included' => true,
            ),
            'privacy' => array(
                'automatic_telemetry' => false,
                'automatic_submission' => false,
                'device_identifier_included' => false,
                'project_content_included' => false,
                'source_urls_included' => false,
                'query_string_included' => false,
                'hash_included' => false,
            ),
            'governance' => array(
                'hidden_health_score' => false,
                'automatic_repair' => false,
                'automatic_issue_submission' => false,
                'human_review_before_issue_export' => true,
            ),
        ));
    }


    public function workspace_home_contract() {
        return rest_ensure_response(SC_Workspace_Home::contract());
    }

    public function universal_search_contract() {
        return rest_ensure_response(SC_Workspace_Universal_Search::contract());
    }

    public function library_continuity_contract() {
        return rest_ensure_response(SC_Workspace_Library_Continuity::contract());
    }

    public function knowledge_graph_explorer_contract() {
        return rest_ensure_response(SC_Workspace_Knowledge_Graph_Explorer::contract());
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
            'storage_schema_version' => 35,
            'project_schema' => 'sc-workspace-project/20.0',
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

    public function product_help_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-product-help-contract/1.0',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'help_schema' => 'sc-workspace-product-help/1.0',
            'report_schema' => 'sc-workspace-product-help-report/1.0',
            'recovery_guidance_schema' => 'sc-workspace-recovery-guidance/1.0',
            'surface' => 'start/help',
            'topic_count' => 10,
            'recovery_topics' => array('save-verification','restore-as-copy','import-rejection','sync-conflict','device-migration','shared-review','institutional-handoff'),
            'advisory_only' => true,
            'canonical_mutation' => false,
            'automatic_recovery' => false,
            'automatic_restore' => false,
            'automatic_upload' => false,
            'automatic_sync' => false,
            'behavioral_tracking' => false,
            'telemetry' => false,
            'project_content_in_report' => false,
            'source_urls_in_report' => false,
            'device_identifier_in_report' => false,
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
            'sc-workspace-v170',
            SC_WORKSPACE_URL . 'assets/css/workspace-v1.7.0.css',
            array(),
            SC_WORKSPACE_VERSION
        );
        wp_enqueue_script(
            'sc-workspace-project-diff-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-project-diff-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-safe-actions-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-safe-actions-v1.js',
            array('sc-workspace-home-v1', 'sc-workspace-project-diff-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-reconciliation-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-reconciliation-v1.js',
            array('sc-workspace-project-diff-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-reconciliation-receipt-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-reconciliation-receipt-v1.js',
            array('sc-workspace-reconciliation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-audit-trail-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-audit-trail-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-project-lifecycle-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-project-lifecycle-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-public-beta-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-field-diagnostics-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-field-diagnostics-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-source-capture-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-source-capture-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-notebook-portability-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-notebook-portability-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-notebook-review-provenance-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-notebook-review-provenance-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-notebook-v8',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-notebook-v8.js',
            array('sc-workspace-source-capture-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-integrated-knowledge-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-integrated-knowledge-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-knowledge-search-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-knowledge-search-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-navigation-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-navigation-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-collections-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-collections-v1.js',
            array('sc-workspace-knowledge-search-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-reference-library-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-reference-library-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-composition-studio-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-composition-studio-v1.js',
            array('sc-workspace-reference-library-v1', 'sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-interchange-v2',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-interchange-v2.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-import-export-compatibility-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-import-export-compatibility-v1.js',
            array('sc-workspace-interchange-v2'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-templates-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-templates-v1.js',
            array('sc-workspace-research-notebook-v8'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-cross-project-knowledge-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-cross-project-knowledge-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-relationship-explorer-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-relationship-explorer-v1.js',
            array('sc-workspace-integrated-knowledge-v1', 'sc-workspace-reference-library-v1', 'sc-workspace-research-notebook-v8', 'sc-workspace-cross-project-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-relationship-explorer-v2',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-relationship-explorer-v2.js',
            array('sc-workspace-relationship-explorer-v1', 'sc-workspace-library-continuity-v1', 'sc-workspace-universal-search-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-grounded-research-assistant-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-grounded-research-assistant-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-tasks-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-tasks-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-collaboration-architecture-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-collaboration-architecture-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-shared-review-handoff-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-shared-review-handoff-v1.js',
            array('sc-workspace-collaboration-architecture-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-shared-review-handoff-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-shared-review-handoff-ui-v1.js',
            array('sc-workspace-shared-review-handoff-v1', 'sc-workspace-collaboration-architecture-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-api-embed-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-api-embed-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-api-embed-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-api-embed-ui-v1.js',
            array('sc-workspace-api-embed-v1', 'sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-automation-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-automation-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-research-automation-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-research-automation-ui-v1.js',
            array('sc-workspace-research-automation-v1', 'sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-institutional-research-packages-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-institutional-research-packages-v1.js',
            array('sc-workspace-integrated-knowledge-v1', 'sc-workspace-reference-library-v1', 'sc-workspace-research-tasks-v1', 'sc-workspace-collaboration-architecture-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-institutional-validation-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-institutional-validation-v1.js',
            array('sc-workspace-institutional-research-packages-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-institutional-research-packages-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-institutional-research-packages-ui-v1.js',
            array('sc-workspace-institutional-research-packages-v1', 'sc-workspace-integrated-knowledge-v1', 'sc-workspace-institutional-validation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-scale-performance-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-scale-performance-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-scale-performance-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-scale-performance-ui-v1.js',
            array('sc-workspace-scale-performance-v1', 'sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-security-privacy-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-security-privacy-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-security-privacy-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-security-privacy-ui-v1.js',
            array('sc-workspace-security-privacy-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-public-beta-ii-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-ii-v1.js',
            array('sc-workspace-field-diagnostics-v1', 'sc-workspace-scale-performance-v1', 'sc-workspace-security-privacy-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-public-beta-ii-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-ii-ui-v1.js',
            array('sc-workspace-public-beta-ii-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-experience-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-experience-v1.js',
            array('sc-workspace-research-navigation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-field-resilience-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-field-resilience-v1.js',
            array('sc-workspace-research-navigation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-persistence-integrity-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-persistence-integrity-v1.js',
            array('sc-workspace-field-resilience-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-browser-compatibility-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-browser-compatibility-v1.js',
            array('sc-workspace-field-resilience-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-accessibility-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-accessibility-v1.js',
            array('sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-field-use-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-field-use-v1.js',
            array('sc-workspace-browser-compatibility-v1', 'sc-workspace-accessibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-recovery-disaster-simulation-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-recovery-disaster-simulation-v1.js',
            array('sc-workspace-persistence-integrity-v1', 'sc-workspace-import-export-compatibility-v1', 'sc-workspace-cross-device-continuity-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-public-beta-iii-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-iii-v1.js',
            array('sc-workspace-research-navigation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-first-run-onboarding-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-first-run-onboarding-v1.js',
            array('sc-workspace-public-beta-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-workflow-guidance-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-workflow-guidance-v1.js',
            array('sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-long-session-performance-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-long-session-performance-v1.js',
            array('sc-workspace-scale-performance-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-cross-device-continuity-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-cross-device-continuity-v1.js',
            array('sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-product-help-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-product-help-v1.js',
            array('sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-security-privacy-audit-ii-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-security-privacy-audit-ii-v1.js',
            array('sc-workspace-security-privacy-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-accessibility-performance-final-audit-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-accessibility-performance-final-audit-v1.js',
            array('sc-workspace-accessibility-v1', 'sc-workspace-long-session-performance-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-public-beta-iii-defect-closure-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-iii-defect-closure-v1.js',
            array('sc-workspace-public-beta-iii-v1', 'sc-workspace-persistence-integrity-v1', 'sc-workspace-import-export-compatibility-v1', 'sc-workspace-cross-device-continuity-v1', 'sc-workspace-recovery-disaster-simulation-v1', 'sc-workspace-security-privacy-audit-ii-v1', 'sc-workspace-accessibility-performance-final-audit-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-release-candidate-i-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-release-candidate-i-v1.js',
            array('sc-workspace-public-beta-iii-defect-closure-v1', 'sc-workspace-recovery-disaster-simulation-v1', 'sc-workspace-security-privacy-audit-ii-v1', 'sc-workspace-accessibility-performance-final-audit-v1', 'sc-workspace-browser-compatibility-v1', 'sc-workspace-persistence-integrity-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-wordpress-deployment-hardening-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-wordpress-deployment-hardening-v1.js',
            array('sc-workspace-release-candidate-i-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-production-smoke-cache-rollback-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-production-smoke-cache-rollback-v1.js',
            array('sc-workspace-wordpress-deployment-hardening-v1', 'sc-workspace-release-candidate-i-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-production-signoff-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-production-signoff-v1.js',
            array('sc-workspace-production-smoke-cache-rollback-v1', 'sc-workspace-wordpress-deployment-hardening-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-ga-readiness-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-ga-readiness-v1.js',
            array('sc-workspace-production-signoff-v1', 'sc-workspace-production-smoke-cache-rollback-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-ga-stabilization-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-ga-stabilization-v1.js',
            array('sc-workspace-general-availability-v1', 'sc-workspace-wordpress-deployment-hardening-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-home-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-home-v1.js',
            array('sc-workspace-research-navigation-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-universal-search-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-universal-search-v1.js',
            array('sc-workspace-integrated-knowledge-v1', 'sc-workspace-knowledge-search-v1', 'sc-workspace-reference-library-v1', 'sc-workspace-research-tasks-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-library-continuity-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-library-continuity-v1.js',
            array('sc-workspace-universal-search-v1', 'sc-workspace-integrated-knowledge-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-lab-integration-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-lab-integration-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-workbench-decision-roundtrip-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-workbench-decision-roundtrip-v1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-v170',
            SC_WORKSPACE_URL . 'assets/js/workspace-v1.7.0.js',
            array('sc-workspace-project-diff-v1', 'sc-workspace-safe-actions-v1', 'sc-workspace-reconciliation-v1', 'sc-workspace-reconciliation-receipt-v1', 'sc-workspace-audit-trail-v1', 'sc-workspace-project-lifecycle-v1', 'sc-workspace-public-beta-v1', 'sc-workspace-field-diagnostics-v1', 'sc-workspace-source-capture-v1', 'sc-workspace-notebook-portability-v1', 'sc-workspace-notebook-review-provenance-v1', 'sc-workspace-research-notebook-v8', 'sc-workspace-integrated-knowledge-v1', 'sc-workspace-knowledge-search-v1', 'sc-workspace-research-navigation-v1', 'sc-workspace-research-collections-v1', 'sc-workspace-reference-library-v1', 'sc-workspace-composition-studio-v1', 'sc-workspace-interchange-v2', 'sc-workspace-cross-project-knowledge-v1', 'sc-workspace-relationship-explorer-v1', 'sc-workspace-research-templates-v1', 'sc-workspace-grounded-research-assistant-v1', 'sc-workspace-research-tasks-v1', 'sc-workspace-collaboration-architecture-v1', 'sc-workspace-shared-review-handoff-v1', 'sc-workspace-shared-review-handoff-ui-v1', 'sc-workspace-api-embed-v1', 'sc-workspace-api-embed-ui-v1', 'sc-workspace-research-automation-v1', 'sc-workspace-research-automation-ui-v1', 'sc-workspace-institutional-research-packages-v1', 'sc-workspace-institutional-research-packages-ui-v1', 'sc-workspace-institutional-validation-v1', 'sc-workspace-scale-performance-v1', 'sc-workspace-scale-performance-ui-v1', 'sc-workspace-security-privacy-v1', 'sc-workspace-security-privacy-ui-v1', 'sc-workspace-public-beta-ii-v1', 'sc-workspace-experience-v1', 'sc-workspace-field-resilience-v1', 'sc-workspace-persistence-integrity-v1', 'sc-workspace-browser-compatibility-v1', 'sc-workspace-field-use-v1', 'sc-workspace-import-export-compatibility-v1', 'sc-workspace-cross-device-continuity-v1', 'sc-workspace-long-session-performance-v1', 'sc-workspace-recovery-disaster-simulation-v1', 'sc-workspace-public-beta-iii-v1', 'sc-workspace-first-run-onboarding-v1', 'sc-workspace-workflow-guidance-v1', 'sc-workspace-product-help-v1', 'sc-workspace-security-privacy-audit-ii-v1', 'sc-workspace-accessibility-performance-final-audit-v1', 'sc-workspace-public-beta-iii-defect-closure-v1', 'sc-workspace-release-candidate-i-v1', 'sc-workspace-wordpress-deployment-hardening-v1', 'sc-workspace-production-smoke-cache-rollback-v1', 'sc-workspace-production-signoff-v1', 'sc-workspace-ga-readiness-v1', 'sc-workspace-general-availability-v1', 'sc-workspace-universal-search-v1', 'sc-workspace-library-continuity-v1', 'sc-workspace-relationship-explorer-v2', 'sc-workspace-lab-integration-v1', 'sc-workspace-workbench-decision-roundtrip-v1', 'sc-workspace-cross-device-production-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-production-signoff-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-production-signoff-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-production-signoff-v1', 'sc-workspace-ga-readiness-v1', 'sc-workspace-general-availability-v1', 'sc-workspace-universal-search-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-ga-readiness-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-ga-readiness-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-ga-readiness-v1', 'sc-workspace-production-signoff-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-general-availability-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-general-availability-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-general-availability-v1', 'sc-workspace-ga-readiness-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-ga-stabilization-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-ga-stabilization-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-ga-stabilization-v1', 'sc-workspace-general-availability-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-workflow-guidance-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-workflow-guidance-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-workflow-guidance-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-product-help-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-product-help-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-product-help-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-security-privacy-audit-ii-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-security-privacy-audit-ii-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-security-privacy-audit-ii-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-institutional-validation-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-institutional-validation-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-institutional-validation-v1', 'sc-workspace-institutional-research-packages-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        $return_url = SC_Workspace_Platform::canonical_url();
        $authenticated = is_user_logged_in();
        $user = $authenticated ? wp_get_current_user() : null;
        wp_enqueue_script(
            'sc-workspace-focused-shell-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-focused-shell-v1.js',
            array('sc-workspace-v170'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-field-resilience-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-field-resilience-ui-v1.js',
            array('sc-workspace-focused-shell-v1', 'sc-workspace-field-resilience-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-persistence-integrity-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-persistence-integrity-ui-v1.js',
            array('sc-workspace-focused-shell-v1', 'sc-workspace-persistence-integrity-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-browser-compatibility-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-browser-compatibility-ui-v1.js',
            array('sc-workspace-focused-shell-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-accessibility-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-accessibility-ui-v1.js',
            array('sc-workspace-focused-shell-v1', 'sc-workspace-accessibility-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-long-session-performance-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-long-session-performance-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-long-session-performance-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-accessibility-performance-final-audit-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-accessibility-performance-final-audit-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-accessibility-performance-final-audit-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-public-beta-iii-defect-closure-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-iii-defect-closure-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-public-beta-iii-defect-closure-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-release-candidate-i-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-release-candidate-i-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-release-candidate-i-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-wordpress-deployment-hardening-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-wordpress-deployment-hardening-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-wordpress-deployment-hardening-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-production-smoke-cache-rollback-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-production-smoke-cache-rollback-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-production-smoke-cache-rollback-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );
        wp_enqueue_script(
            'sc-workspace-recovery-disaster-simulation-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-recovery-disaster-simulation-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-recovery-disaster-simulation-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_enqueue_script(
            'sc-workspace-public-beta-iii-ui-v1',
            SC_WORKSPACE_URL . 'assets/js/sc-workspace-public-beta-iii-ui-v1.js',
            array('sc-workspace-v170', 'sc-workspace-public-beta-iii-v1', 'sc-workspace-browser-compatibility-v1'),
            SC_WORKSPACE_VERSION,
            true
        );

        wp_localize_script('sc-workspace-v170', 'SCWorkspaceIdentity', array(
            'authenticated' => $authenticated,
            'workspaceVersion' => SC_WORKSPACE_VERSION,
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
        <?php $deployment_state = SC_Workspace_Deployment_Hardening::diagnostics(); ?>
        <section class="scw-shell" data-sc-workspace data-scw-focused-shell="1" data-scw-field-use="1" data-version="<?php echo esc_attr(SC_WORKSPACE_VERSION); ?>" data-storage-version="35" data-project-schema="sc-workspace-project/20.0" data-release-stage="cross-device-production" data-scw-deployment-server-state="<?php echo esc_attr($deployment_state['state']); ?>" data-scw-deployment-files-complete="<?php echo !empty($deployment_state['required_files_complete']) ? '1' : '0'; ?>" data-scw-deployment-expected-script="workspace-v1.7.0.js" data-scw-deployment-expected-style="workspace-v1.7.0.css" data-return-url="<?php echo esc_url($return_url); ?>">
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
                        <span>GENERAL AVAILABILITY</span>
                    </div>
                </div>
            </div>

            <div class="scw-boundary" role="note">
                <strong>Local-first by default</strong>
                <span>Workspace remains fully usable without signing in. Projects are stored on this device. Sign-in is optional. Account recovery and cross-device sync are optional. Backups require an explicit action, sync requires explicit per-project enrollment, and nothing synchronizes in the background. Connected tools can return structured work to the originating project through the established local-first handoff contract. Research Notebook remains inside the same project boundary and does not upload or invoke AI automatically. Workspace 1.x keeps these boundaries explicit while improving the working interface.</span>
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
                    <div class="scw-sync-production" data-scw-sync-production>
                        <div class="scw-sync-continuity-head"><strong>Production continuity plan</strong><span data-scw-sync-plan-state>Not checked</span></div>
                        <p data-scw-sync-plan-reason>Check status to derive an explainable local/cloud action plan. Workspace never applies the plan automatically.</p>
                        <div class="scw-sync-continuity-actions"><button class="scw-button" type="button" data-scw-sync-plan-export disabled>Export continuity receipt</button></div>
                    </div>
                    <div class="scw-sync-resolution" aria-label="Conflict-safe synchronization actions">
                        <button class="scw-button" type="button" data-scw-sync-remote-copy hidden>Open cloud as copy</button>
                        <button class="scw-button" type="button" data-scw-sync-resolve-local hidden>Keep local as sync head</button>
                        <button class="scw-button" type="button" data-scw-sync-resolve-cloud hidden>Use cloud here · preserve local copy</button>
                    </div>
                    <div class="scw-sync-boundary" role="note"><strong>Local-first continuity, not cloud-first storage</strong><span>Enabling sync stores local enrollment metadata only. Project content moves only after an explicit Sync now or conflict-resolution action. Continuity plans and receipts contain metadata/fingerprints, not project content or device identity. Shared team sync and institutional storage remain outside Workspace.</span></div>
                    <div class="scw-sync-continuity" data-scw-sync-continuity>
                        <div class="scw-sync-continuity-head"><strong>Device migration &amp; interrupted-sync recovery</strong><span>Migration files preserve project content and a sync baseline, never device identity or automatic enrollment.</span></div>
                        <div class="scw-sync-continuity-actions"><button class="scw-button" type="button" data-scw-sync-migration-export>Export migration package</button><button class="scw-button" type="button" data-scw-sync-migration-import>Import migration package</button><input type="file" accept="application/json,.json" data-scw-sync-migration-file hidden></div>
                        <div class="scw-sync-migration-status" data-scw-sync-migration-status role="status" aria-live="polite">Migration imports always create a new local copy. Sync must be enrolled again explicitly on the receiving device.</div>
                    </div>
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
                <section class="scw-field-diagnostics" data-scw-field-diagnostics aria-labelledby="scw-field-diagnostics-title">
                    <div class="scw-field-diagnostics-head"><div><div class="scw-kicker">PUBLIC BETA / FIELD DIAGNOSTICS</div><h3 id="scw-field-diagnostics-title">Capture the environment when something goes wrong.</h3></div><span class="scw-field-badge">LOCAL REPORT</span></div>
                    <p>Field checks measure browser capability, storage/recovery state, workspace size, serialization latency, and interface density. Reports are created locally. Nothing is submitted automatically, and project content is never added unless you type it into the issue form yourself.</p>
                    <div class="scw-field-grid" aria-live="polite">
                        <div><span>RUNTIME</span><strong data-scw-field-browser>NOT CHECKED</strong><small>Browser and core capability status.</small></div>
                        <div><span>RECOVERY</span><strong data-scw-field-recovery>NOT CHECKED</strong><small>Last-known-good snapshot availability.</small></div>
                        <div><span>WORKSPACE SIZE</span><strong data-scw-field-storage>NOT CHECKED</strong><small>Serialized local state size only.</small></div>
                        <div><span>STORAGE PROBE</span><strong data-scw-field-latency>NOT CHECKED</strong><small>Local write/read/remove latency.</small></div>
                        <div><span>DOM DENSITY</span><strong data-scw-field-dom>NOT CHECKED</strong><small>Rendered Workspace element count.</small></div>
                        <div><span>ATTENTION</span><strong data-scw-field-attention>NOT CHECKED</strong><small>Explicit threshold flags; never a hidden score.</small></div>
                    </div>
                    <div class="scw-field-actions">
                        <button class="scw-button scw-button-primary" type="button" data-scw-run-field-diagnostics>Run field check</button>
                        <button class="scw-button" type="button" data-scw-export-field-diagnostic disabled>Export field diagnostic</button>
                    </div>
                    <form class="scw-field-report-form" data-scw-field-report-form>
                        <div class="scw-field-report-grid">
                            <label><span>ISSUE TYPE</span><select name="type"><option value="functional">Functional</option><option value="performance">Performance</option><option value="accessibility">Accessibility</option><option value="recovery">Recovery / storage</option><option value="sync">Account / sync</option><option value="import-export">Import / export</option><option value="visual">Visual / layout</option><option value="other">Other</option></select></label>
                            <label><span>IMPACT</span><select name="impact"><option value="inconvenience">Inconvenience</option><option value="blocks-task">Blocks a task</option><option value="data-risk">Potential data risk</option></select></label>
                        </div>
                        <label><span>WHAT HAPPENED</span><textarea name="observed" rows="3" maxlength="5000" placeholder="Describe what you observed." required></textarea></label>
                        <label><span>WHAT DID YOU EXPECT?</span><textarea name="expected" rows="2" maxlength="5000" placeholder="Describe the expected behavior."></textarea></label>
                        <label><span>STEPS TO REPRODUCE</span><textarea name="steps" rows="3" maxlength="8000" placeholder="List the smallest sequence that reproduces the issue."></textarea></label>
                        <label class="scw-field-review"><input type="checkbox" name="reviewed" value="1"> <span>I reviewed this report. I understand that text I type above will be included, while Workspace does not automatically attach project content, source URLs, the local device identifier, query strings, or page fragments.</span></label>
                        <div class="scw-field-actions"><button class="scw-button scw-button-primary" type="submit">Export issue report</button><button class="scw-button" type="button" data-scw-export-support-summary>Export text summary</button></div>
                    </form>
                    <div class="scw-field-status" data-scw-field-status role="status" aria-live="polite">No field check has been run. Reports stay on this device until you explicitly export them.</div>
                </section>
            </details>

            <div class="scw-recovery" data-scw-recovery hidden role="status" aria-live="polite">
                <div><strong>Workspace recovery mode</strong><span data-scw-recovery-message>A damaged local state was isolated and a clean workspace was opened.</span></div>
                <button type="button" class="scw-button" data-scw-dismiss-recovery>Dismiss</button>
            </div>

            <nav id="scw-workspace-main" class="scw-workspace-primary-nav" aria-label="Workspace areas" data-scw-workspace-view-nav data-scw-keyboard-nav="1" tabindex="-1">
                <button type="button" class="is-active" data-scw-workspace-area="start" data-scw-workspace-view="start" aria-pressed="true" aria-current="page">Home</button>
                <button type="button" data-scw-workspace-area="projects" data-scw-workspace-view="projects" aria-pressed="false">Projects</button>
                <button type="button" data-scw-workspace-area="research" data-scw-workspace-view="research" aria-pressed="false">Research</button>
                <button type="button" data-scw-workspace-area="review" data-scw-workspace-view="activity" aria-pressed="false">Review</button>
                <button type="button" data-scw-workspace-area="exchange" data-scw-workspace-view="interoperability" aria-pressed="false">Exchange</button>
            </nav>
            <div class="scw-navigation-context" data-scw-navigation-context>
                <div class="scw-navigation-context-copy"><span data-scw-navigation-path>Workspace / Home</span><strong data-scw-navigation-title>Home</strong><p data-scw-navigation-description>Resume active work, orient a project, or move directly to the next task.</p></div>
                <nav class="scw-workspace-context-nav" data-scw-workspace-context-nav="start" aria-label="Home routes">
                    <button type="button" data-scw-workspace-view="start">Home</button><button type="button" data-scw-workspace-view="journey">Product Journey</button><button type="button" data-scw-workspace-view="help">Help &amp; Recovery</button>
                </nav>
                <nav class="scw-workspace-context-nav" data-scw-workspace-context-nav="research" aria-label="Research routes" hidden>
                    <button type="button" data-scw-workspace-view="research">Research home</button><button type="button" data-scw-workspace-view="notebook">Notebook</button><button type="button" data-scw-workspace-view="knowledge">Knowledge</button><button type="button" data-scw-workspace-view="graph">Graph</button>
                </nav>
                <nav class="scw-workspace-context-nav scw-workspace-review-nav" data-scw-workspace-context-nav="review" aria-label="Review routes" hidden>
                    <button type="button" data-scw-workspace-view="activity">Activity</button><button type="button" data-scw-workspace-view="lifecycle">Lifecycle</button><button type="button" data-scw-workspace-view="changes">Changes</button><button type="button" data-scw-workspace-view="audit">Audit</button><button type="button" data-scw-workspace-view="safety">Safety</button>
                    <details class="scw-review-more"><summary>More review tools</summary><div class="scw-review-more-grid"><button type="button" data-scw-workspace-view="history">History</button><button type="button" data-scw-workspace-view="reconcile">Reconcile</button><button type="button" data-scw-workspace-view="automation">Automation</button><button type="button" data-scw-workspace-view="performance">Performance</button><button type="button" data-scw-workspace-view="security">Security &amp; Privacy</button><button type="button" data-scw-workspace-view="reliability">Reliability</button><button type="button" data-scw-workspace-view="integrity">Persistence Integrity</button><button type="button" data-scw-workspace-view="compatibility">Compatibility</button><button type="button" data-scw-workspace-view="accessibility">Accessibility</button><button type="button" data-scw-workspace-view="recovery-drills">Recovery Drills</button><button type="button" data-scw-workspace-view="deployment">Deployment</button><button type="button" data-scw-workspace-view="production-certification">Production Certification</button><button type="button" data-scw-workspace-view="production-signoff">Production Sign-Off</button><button type="button" data-scw-workspace-view="ga-readiness">1.0 Readiness</button><button type="button" data-scw-workspace-view="general-availability">General Availability</button><button type="button" data-scw-workspace-view="ga-stabilization">GA Stabilization</button><button type="button" data-scw-workspace-view="beta">Beta Readiness</button><button type="button" data-scw-workspace-view="final-audit">Final Audit</button><button type="button" data-scw-workspace-view="beta-closure">Beta Closure</button><button type="button" data-scw-workspace-view="release-candidate">Release Candidate</button></div></details>
                </nav>
                <nav class="scw-workspace-context-nav" data-scw-workspace-context-nav="exchange" aria-label="Exchange routes" hidden>
                    <button type="button" data-scw-workspace-view="interoperability">Import &amp; Interoperability</button><button type="button" data-scw-workspace-view="collaboration">Collaborate</button><button type="button" data-scw-workspace-view="api-embed">API &amp; Embed</button><button type="button" data-scw-workspace-view="institutional">Institutional</button><button type="button" data-scw-workspace-view="share">Share</button>
                </nav>
            </div>
            <div class="scw-experience-controls" data-scw-experience-controls aria-label="Workspace display and navigation tools">
                <div class="scw-experience-controls-copy"><strong>Workspace controls</strong><span>Navigate quickly, adjust density, or review terminology and shortcuts.</span></div>
                <div class="scw-experience-actions">
                    <button class="scw-experience-action" type="button" data-scw-command-open aria-keyshortcuts="Control+K Meta+K">Find command <kbd>⌘K</kbd></button>
                    <button class="scw-experience-action" type="button" data-scw-density-toggle aria-pressed="false">Density: <span data-scw-density-label>Comfortable</span></button>
                    <button class="scw-experience-action" type="button" data-scw-help-open>Help</button>
                </div>
                <div class="scw-experience-status" data-scw-experience-status role="status" aria-live="polite"></div>
            </div>
            <div class="scw-experience-dialog" data-scw-command-palette hidden role="dialog" aria-modal="true" aria-labelledby="scw-command-palette-title">
                <section class="scw-experience-dialog-panel">
                    <div class="scw-experience-dialog-head"><div><span>WORKSPACE COMMANDS</span><h3 id="scw-command-palette-title">Go directly to the work.</h3></div><button class="scw-experience-dialog-close" type="button" data-scw-dialog-close aria-label="Close command palette">×</button></div>
                    <label class="scw-command-query-wrap"><span>Find a Workspace route</span><input type="search" data-scw-command-query autocomplete="off" placeholder="Search Research, Notebook, Review, Import…"></label>
                    <div class="scw-command-results" data-scw-command-results></div>
                </section>
            </div>
            <div class="scw-experience-dialog" data-scw-experience-help hidden role="dialog" aria-modal="true" aria-labelledby="scw-experience-help-title">
                <section class="scw-experience-dialog-panel">
                    <div class="scw-experience-dialog-head"><div><span>ORIENTATION</span><h3 id="scw-experience-help-title">One Workspace, five primary areas.</h3></div><button class="scw-experience-dialog-close" type="button" data-scw-dialog-close aria-label="Close Workspace help">×</button></div>
                    <div class="scw-experience-help-body">
                        <p class="scw-experience-help-intro">The primary navigation stays deliberately small. Specialized tools appear within Research, Review, and Exchange rather than competing at the top level.</p><div class="scw-experience-help-open"><button class="scw-button" type="button" data-scw-workspace-view="help" data-scw-dialog-close>Open Help &amp; Recovery</button></div>
                        <p class="scw-field-use-guidance">On compact or touch devices, Workspace prioritizes capture, review, and lightweight editing. Dense graph, comparison, and composition surfaces remain available and use bounded scrolling instead of forcing the page wider.</p>
                        <div class="scw-experience-shortcuts" aria-label="Keyboard shortcuts">
                            <div><kbd>⌘/Ctrl + K</kbd><span>Open command palette</span></div><div><kbd>Alt + 1…5</kbd><span>Open Start through Exchange</span></div><div><kbd>/</kbd><span>Focus search in the current view</span></div><div><kbd>Esc</kbd><span>Close Workspace dialogs</span></div>
                        </div>
                        <div class="scw-experience-terms">
                            <div><strong>Project</strong><span>The canonical local container for a body of work and its structured objects.</span></div><div><strong>Research</strong><span>Retrieval, Notebook, Knowledge, citations, composition, and Graph exploration.</span></div><div><strong>Notebook</strong><span>Working notes, source captures, links, synthesis, and grounded questions.</span></div><div><strong>Knowledge</strong><span>A derived view over canonical records for finding and reusing existing work.</span></div><div><strong>Review</strong><span>Activity, lifecycle, history, changes, reconciliation, safety, and audit.</span></div><div><strong>Exchange</strong><span>Deliberate import, collaboration, institutional handoff, and sharing.</span></div>
                        </div>
                    </div>
                </section>
            </div>

            <div class="scw-action-gate" data-scw-action-gate hidden role="dialog" aria-modal="true" aria-labelledby="scw-action-gate-title">
                <div class="scw-action-gate-backdrop" data-scw-action-gate-cancel></div>
                <section class="scw-action-gate-dialog">
                    <div class="scw-editorial-kicker">SAFE ACTION PREFLIGHT</div>
                    <h2 id="scw-action-gate-title" data-scw-action-gate-title>Review before proceeding</h2>
                    <p data-scw-action-gate-intro>Workspace is preparing an explicit change review for this action.</p>
                    <div class="scw-action-gate-review" data-scw-action-gate-review></div>
                    <label class="scw-action-gate-ack"><input type="checkbox" data-scw-action-gate-ack> <span data-scw-action-gate-ack-text>I reviewed this action.</span></label>
                    <div class="scw-action-gate-actions"><button class="scw-button scw-button-primary" type="button" data-scw-action-gate-proceed disabled>Proceed</button><button class="scw-button" type="button" data-scw-action-gate-cancel>Cancel</button></div>
                    <div class="scw-action-gate-status" data-scw-action-gate-status role="status" aria-live="polite"></div>
                </section>
            </div>

            <section class="scw-public-beta-start scw-workspace-home" data-scw-workspace-section="start" aria-labelledby="scw-public-beta-title">
                <div class="scw-public-beta-head">
                    <div>
                        <div class="scw-kicker">WORKSPACE HOME / PROJECT COCKPIT</div>
                        <h2 id="scw-public-beta-title">Return to the work in front of you.</h2>
                        <p>Home summarizes active projects, recent work, research context, and deterministic next actions without turning Workspace into a dashboard of hidden scores. Start new work only when you need it; otherwise continue directly from the project cockpit.</p>
                    </div>
                    <div class="scw-public-beta-badge"><span>STABLE</span><strong>v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></strong></div>
                </div>
                <section class="scw-project-cockpit" data-scw-project-cockpit aria-labelledby="scw-project-cockpit-title">
                    <div class="scw-project-cockpit-head">
                        <div><div class="scw-editorial-kicker">PROJECT COCKPIT</div><h3 id="scw-project-cockpit-title">One place to orient the active project.</h3><p data-scw-cockpit-summary>No active project yet. Create or open a project to populate the cockpit.</p></div>
                        <div class="scw-project-cockpit-active"><span>ACTIVE PROJECT</span><strong data-scw-cockpit-title>None selected</strong><small data-scw-cockpit-updated>Local workspace</small></div>
                    </div>
                    <div class="scw-project-cockpit-metrics" aria-label="Workspace project summary"><div><strong data-scw-cockpit-projects>0</strong><span>Active projects</span></div><div><strong data-scw-cockpit-objects>0</strong><span>Objects</span></div><div><strong data-scw-cockpit-research>0</strong><span>Research records</span></div><div><strong data-scw-cockpit-notebooks>0</strong><span>Notebooks</span></div></div>
                    <div class="scw-project-cockpit-grid">
                        <section><span class="scw-editorial-kicker">CONTINUE</span><h4 data-scw-cockpit-next-title>Choose a project</h4><p data-scw-cockpit-next-detail>Your next action is derived only from visible project state.</p><div class="scw-project-cockpit-actions"><button class="scw-button scw-button-primary" type="button" data-scw-cockpit-open-project disabled>Open project</button><button class="scw-button" type="button" data-scw-cockpit-view="research">Research</button><button class="scw-button" type="button" data-scw-cockpit-view="notebook">Notebook</button><button class="scw-button" type="button" data-scw-cockpit-universal-search>Search Workspace</button></div></section>
                        <section><span class="scw-editorial-kicker">WORK MODES</span><h4>Move inside the active project.</h4><div class="scw-project-cockpit-lanes"><button type="button" data-scw-cockpit-mode="objects"><strong>Evidence &amp; objects</strong><span>Sources, evidence, datasets and documents.</span></button><button type="button" data-scw-cockpit-mode="analysis"><strong>Analysis</strong><span>Questions, variables, assumptions and findings.</span></button><button type="button" data-scw-cockpit-mode="decision"><strong>Decision</strong><span>Alternatives, criteria, risk and rationale.</span></button><button type="button" data-scw-cockpit-mode="briefing"><strong>Compose</strong><span>Briefings and publication-ready outputs.</span></button></div></section>
                    </div>
                    <div class="scw-project-cockpit-boundary" role="note"><strong>Context, not scoring.</strong><span>The cockpit uses only local project state to summarize work and suggest explicit routes. It does not infer productivity, rank people, upload content, or run AI automatically.</span></div>
                </section>
                <section class="scw-first-run" data-scw-first-run aria-labelledby="scw-first-run-title">
                    <div class="scw-first-run-copy">
                        <div class="scw-editorial-kicker">FIRST RUN / YOUR FIRST PROJECT</div>
                        <h3 id="scw-first-run-title">Name the work and choose only as much structure as you need.</h3>
                        <p>Workspace creates the project locally after you submit this form. You can start blank or begin with an editable guided workflow; nothing is inferred, completed, uploaded, or enrolled in sync automatically.</p>
                    </div>
                    <form class="scw-first-run-form" data-scw-first-run-form novalidate>
                        <label><span>Project name</span><input type="text" name="title" maxlength="120" required placeholder="What are you working on?" autocomplete="off"></label>
                        <label><span>Purpose <em>optional</em></span><textarea name="description" rows="2" maxlength="600" placeholder="What are you trying to understand, analyze, decide, or prepare?"></textarea></label>
                        <fieldset class="scw-first-run-starters"><legend>Starting shape</legend>
                            <label><input type="radio" name="starter" value="blank" checked><span><strong>Blank project</strong><small>Start with an empty project and add structure later.</small></span></label>
                            <label><input type="radio" name="starter" value="research-investigation"><span><strong>Research investigation</strong><small>Question → sources → evidence → analysis → briefing</small></span></label>
                            <label><input type="radio" name="starter" value="analytical-assessment"><span><strong>Analytical assessment</strong><small>Variables → assumptions → methods → comparisons → findings</small></span></label>
                            <label><input type="radio" name="starter" value="decision-case"><span><strong>Decision case</strong><small>Alternatives → criteria → evidence → risk → rationale</small></span></label>
                            <label><input type="radio" name="starter" value="publication-preparation"><span><strong>Publication preparation</strong><small>Basis → outline → draft → review → export</small></span></label>
                        </fieldset>
                        <div class="scw-first-run-boundary" data-scw-first-run-boundary role="note">Creating a project saves it locally on this device. No account is required, and nothing is uploaded automatically.</div>
                        <div class="scw-first-run-actions"><button class="scw-button scw-button-primary" type="submit">Create first project</button><button class="scw-button" type="button" data-scw-first-run-blank>Use the standard project form</button></div>
                        <div class="scw-first-run-status" data-scw-first-run-status role="status" aria-live="polite"></div>
                    </form>
                </section>
                <div class="scw-public-beta-metrics" aria-label="Workspace local summary">
                    <div><strong data-scw-beta-projects>0</strong><span>Active projects</span></div>
                    <div><strong data-scw-beta-objects>0</strong><span>Canonical objects</span></div>
                    <div><strong data-scw-beta-milestones>0</strong><span>Lifecycle milestones</span></div>
                    <div><strong data-scw-beta-restore-points>0</strong><span>Restore points</span></div>
                </div>
                <div class="scw-public-beta-actions">
                    <button class="scw-button scw-button-primary" type="button" data-scw-beta-new>New blank project</button>
                    <button class="scw-button" type="button" data-scw-beta-continue disabled>Continue recent project</button>
                    <a class="scw-button" href="<?php echo esc_url(home_url('/knowledge-libraries/')); ?>">Explore the Library</a>
                    <button class="scw-button" type="button" data-scw-open-product-journey>Walk the product journey</button>
                </div>
                <div class="scw-public-beta-grid">
                    <section class="scw-beta-pathways" aria-labelledby="scw-beta-pathways-title">
                        <div class="scw-editorial-kicker">GUIDED FIRST PROJECT</div>
                        <h3 id="scw-beta-pathways-title">Use structure when it helps.</h3>
                        <p>Each quick start creates a new local project and opens an editable guided workflow. Nothing is inferred, completed, or uploaded automatically.</p>
                        <div class="scw-beta-pathway-list">
                            <button type="button" data-scw-beta-template="research-investigation"><strong>Research investigation</strong><span>Question → sources → evidence → analysis → briefing</span></button>
                            <button type="button" data-scw-beta-template="analytical-assessment"><strong>Analytical assessment</strong><span>Variables → assumptions → methods → comparisons → findings</span></button>
                            <button type="button" data-scw-beta-template="decision-case"><strong>Decision case</strong><span>Alternatives → criteria → evidence → risk → rationale</span></button>
                            <button type="button" data-scw-beta-template="publication-preparation"><strong>Publication preparation</strong><span>Basis → outline → draft → review → export</span></button>
                        </div>
                    </section>
                    <section class="scw-beta-runtime" aria-labelledby="scw-beta-runtime-title">
                        <div class="scw-editorial-kicker">RUNTIME STATUS</div>
                        <h3 id="scw-beta-runtime-title">Know what this browser can support.</h3>
                        <div class="scw-beta-runtime-grid" aria-live="polite">
                            <div><span>LOCAL STORAGE</span><strong data-scw-beta-cap-storage>Checking…</strong></div>
                            <div><span>INTEGRITY</span><strong data-scw-beta-cap-crypto>Checking…</strong></div>
                            <div><span>FILE IMPORT / EXPORT</span><strong data-scw-beta-cap-files>Checking…</strong></div>
                            <div><span>RETURN HANDOFFS</span><strong data-scw-beta-cap-return>Checking…</strong></div>
                        </div>
                        <p class="scw-beta-runtime-note" data-scw-beta-runtime-note role="status" aria-live="polite">Running local capability checks…</p><button class="scw-button scw-beta-diagnostics-link" type="button" data-scw-open-field-diagnostics>Open field diagnostics</button>
                    </section>
                </div>
                <section class="scw-beta-recent" aria-labelledby="scw-beta-recent-title">
                    <div class="scw-editorial-kicker">RECENT WORK</div>
                    <h3 id="scw-beta-recent-title">Continue where you left off.</h3>
                    <div class="scw-beta-recent-list" data-scw-beta-recent-list><div class="scw-beta-empty">No local projects yet. Start a blank project or choose a guided pathway above.</div></div>
                </section>
                <div class="scw-beta-boundary" role="note"><strong>Workspace operating boundary</strong><span>Guest use remains first-class. Sign-in is optional. Cloud backup and sync stay explicit. Lifecycle states remain human-declared. Workspace does not run behavioral telemetry or assign readiness/productivity scores.</span></div>
            </section>

            <section class="scw-public-beta-iii" data-scw-workspace-section="journey" data-scw-public-beta-iii hidden aria-labelledby="scw-public-beta-iii-title">
                <div class="scw-beta-iii-head">
                    <div><div class="scw-kicker">PUBLIC PRODUCT BETA III / PRODUCT JOURNEY</div><h2 id="scw-public-beta-iii-title">Test the whole path from discovery to deliberate handoff.</h2><p>Beta III treats Workspace as one product journey rather than a collection of features. Run the local topology check, then walk the nine stages yourself. Manual review marks live only in this browser session and never alter a project.</p></div>
                    <div class="scw-beta-iii-badges"><span data-scw-beta-iii-topology>CHECKING</span><span data-scw-beta-iii-walkthrough>0/9 REVIEWED</span></div>
                </div>
                <div class="scw-beta-iii-flow" aria-label="Workspace product journey"><span>Discover</span><b>→</b><span>Capture</span><b>→</b><span>Organize</span><b>→</b><span>Analyze</span><b>→</b><span>Synthesize</span><b>→</b><span>Decide</span><b>→</b><span>Compose</span><b>→</b><span>Review</span><b>→</b><span>Export / Handoff</span></div>
                <div class="scw-beta-iii-actions"><button class="scw-button scw-button-primary" type="button" data-scw-beta-iii-run>Run product-journey check</button><button class="scw-button" type="button" data-scw-beta-iii-export>Export journey report</button><button class="scw-button" type="button" data-scw-beta-iii-reset>Reset session walkthrough</button><button class="scw-button" type="button" data-scw-beta-iii-start>Return to Start</button></div>
                <div class="scw-beta-iii-grid" data-scw-beta-iii-grid><div class="scw-beta-empty">Checking the nine product-journey paths…</div></div>
                <p class="scw-beta-iii-status" data-scw-beta-iii-status role="status" aria-live="polite">Product-journey check has not run yet.</p>
                <div class="scw-beta-iii-boundary" role="note"><strong>Checklist, not a score.</strong><span>Workspace does not infer that you succeeded because a route exists or because you marked a stage reviewed. No behavioral telemetry, automatic completion, project mutation, lifecycle advancement, or automatic submission is introduced. The exported report contains route/topology state and session review marks only.</span></div>
            </section>

            <section class="scw-product-help" data-scw-workspace-section="help" data-scw-product-help hidden aria-labelledby="scw-product-help-title">
                <div class="scw-product-help-head">
                    <div><div class="scw-kicker">PRODUCT HELP / RECOVERY GUIDANCE</div><h2 id="scw-product-help-title">Understand the boundary before you repair the work.</h2><p>Workspace help explains how the product behaves, where work is stored, and which recovery path is safest. Guidance is advisory only: it does not repair, restore, upload, synchronize, or alter a project automatically.</p></div>
                    <div class="scw-product-help-boundary"><strong>Local-first remains the default.</strong><span>Guest projects live in this browser. Signing in does not silently upload project content. Backup, sync, import, restore, review reconciliation, and institutional transfer remain explicit actions.</span></div>
                </div>
                <div class="scw-product-help-truths" aria-label="Workspace operating boundaries">
                    <div><span>LOCAL</span><strong>Browser-local first</strong><small>Do not clear browser storage until important work has a verified portable or recovery copy.</small></div>
                    <div><span>BACKUP</span><strong>Explicit recovery copy</strong><small>Account backup is separate from sync enrollment and does not create background synchronization.</small></div>
                    <div><span>SYNC</span><strong>Conflict-safe, user initiated</strong><small>Workspace rejects silent last-write-wins when local and cloud revisions diverge.</small></div>
                    <div><span>RESTORE</span><strong>Prefer restore-as-copy</strong><small>Compare the recovered state before deleting or replacing any existing local project.</small></div>
                </div>
                <div class="scw-product-help-toolbar">
                    <label><span>Find help</span><input type="search" data-scw-help-search maxlength="240" placeholder="Search backup, import, sync conflict, restore…"></label>
                    <button class="scw-button" type="button" data-scw-help-export>Export help context report</button>
                </div>
                <div class="scw-product-help-list" data-scw-help-list><div class="scw-help-empty">Loading Workspace help…</div></div>
                <p class="scw-product-help-status" data-scw-help-status role="status" aria-live="polite">Product help is available locally.</p>
                <div class="scw-product-help-recovery" role="note"><strong>If Workspace appears damaged:</strong><span>Preserve evidence first. Export a project/recovery candidate when possible, inspect Persistence Integrity, use Recovery Drills only as a simulation, and avoid clearing browser storage until a separate verified copy exists. A WordPress/plugin error is a site-runtime issue and should be diagnosed separately from browser-local project recovery.</span></div>
            </section>

            <section class="scw-integrated-knowledge" data-scw-workspace-section="research" hidden aria-labelledby="scw-integrated-title">
                <div class="scw-integrated-head">
                    <div><div class="scw-kicker">INTEGRATED KNOWLEDGE WORKSPACE</div><h2 id="scw-integrated-title">Research without feature boundaries.</h2><p>Search Notebook material, canonical Workspace Objects, and Research Workspace questions and claims through one derived index. Every result remains anchored to its original record; this view does not duplicate content or invent semantic relationships.</p></div>
                    <div class="scw-integrated-actions"><button class="scw-button" type="button" data-scw-integrated-open-notebook>Open Notebook</button><button class="scw-button" type="button" data-scw-integrated-open-knowledge>Open Personal Knowledge</button><button class="scw-button" type="button" data-scw-integrated-open-project>Open active Project</button></div>
                </div>
                <div class="scw-research-route-grid" aria-label="Research pathways">
                    <button class="scw-research-route" type="button" data-scw-research-route="research"><span>FIND</span><strong>Research home</strong><small>Search every canonical research record through one derived index.</small></button>
                    <button class="scw-research-route" type="button" data-scw-research-route="notebook"><span>WORK</span><strong>Notebook</strong><small>Capture sources, write notes, synthesize material, and use grounded assistance.</small></button>
                    <button class="scw-research-route" type="button" data-scw-research-route="knowledge"><span>ORGANIZE</span><strong>Knowledge</strong><small>Work with Sources, Evidence, Datasets, Analysis, Decisions, and Documents.</small></button>
                    <button class="scw-research-route" type="button" data-scw-research-route="graph"><span>CONNECT</span><strong>Graph</strong><small>Inspect explicit relationships, provenance, and traceable connections.</small></button>
                </div>
                <aside class="scw-workflow-guidance" data-scw-workflow-guidance aria-labelledby="scw-workflow-guidance-title">
                    <div class="scw-workflow-guidance-copy"><span data-scw-workflow-guidance-stage>ORIENT / CONTEXTUAL NEXT STEP</span><strong id="scw-workflow-guidance-title" data-scw-workflow-guidance-title>Choose or create a project first.</strong><p data-scw-workflow-guidance-detail>Research guidance becomes project-specific once Workspace has an active local project.</p></div>
                    <button class="scw-button" type="button" data-scw-workflow-guidance-action>Go to Start</button>
                </aside>
                <div class="scw-integrated-metrics" aria-label="Integrated research metrics"><div><strong data-scw-integrated-total>0</strong><span>research records</span></div><div><strong data-scw-integrated-objects>0</strong><span>Workspace objects</span></div><div><strong data-scw-integrated-notebooks>0</strong><span>Notebook records</span></div><div><strong data-scw-integrated-research>0</strong><span>questions &amp; claims</span></div></div>
                <nav class="scw-research-tool-nav" data-scw-research-tool-nav aria-label="Research workspace tools">
                    <button type="button" data-scw-research-surface="overview" aria-pressed="true">Overview</button>
                    <button type="button" data-scw-research-surface="search" aria-pressed="false">Search</button>
                    <button type="button" data-scw-research-surface="library" aria-pressed="false">Library</button>
                    <button type="button" data-scw-research-surface="collections" aria-pressed="false">Collections</button>
                    <button type="button" data-scw-research-surface="cross-project" aria-pressed="false">Cross-project</button>
                    <button type="button" data-scw-research-surface="tasks" aria-pressed="false">Tasks</button>
                    <button type="button" data-scw-research-surface="assistant" aria-pressed="false">Assistant</button>
                    <button type="button" data-scw-research-surface="citations" aria-pressed="false">Citations</button>
                    <button type="button" data-scw-research-surface="composition" aria-pressed="false">Composition</button>
                </nav>
                <div class="scw-research-overview" data-scw-research-surface-panel="overview">
                    <div><span>FOCUSED RESEARCH WORKSPACE</span><h3>Choose the tool needed for the work in front of you.</h3><p>Research no longer opens every subsystem in one continuous page. Search, organize, reference, review, and compose in focused surfaces while the selected canonical research context remains available across the session.</p></div>
                    <div class="scw-research-overview-grid">
                        <button type="button" data-scw-research-surface-jump="search"><strong>Find</strong><span>Search and inspect canonical research.</span></button>
                        <button type="button" data-scw-research-surface-jump="collections"><strong>Organize</strong><span>Use dynamic views and smart collections.</span></button>
                        <button type="button" data-scw-research-surface-jump="tasks"><strong>Review next</strong><span>Track explicit research workflow state.</span></button>
                        <button type="button" data-scw-research-surface-jump="composition"><strong>Compose</strong><span>Build documents from selected research and citations.</span></button>
                    </div>
                </div>
                <section class="scw-advanced-retrieval" data-scw-research-surface-panel="search" hidden aria-labelledby="scw-advanced-retrieval-title">
                    <div class="scw-advanced-retrieval-head"><div><span>UNIVERSAL WORKSPACE SEARCH</span><h3 id="scw-advanced-retrieval-title">Find the work, not the subsystem.</h3><p>Search projects, canonical objects, notebooks, research, analysis, decisions, briefing drafts, citations, and explicit research tasks from one local index. Ranking remains deterministic and inspectable—no embeddings, hidden personalization, or query telemetry.</p></div><div class="scw-retrieval-result-count"><strong data-scw-retrieval-count>0</strong><span>matching records</span></div></div>
                    <div class="scw-integrated-toolbar scw-retrieval-toolbar">
                        <label class="scw-retrieval-query"><span>Query</span><input type="search" maxlength="320" data-scw-integrated-search placeholder='Search all local Workspace records, e.g. "grid resilience"'></label>
                        <label><span>Kind</span><select data-scw-integrated-kind><option value="all">Everything</option><option value="project">Projects</option><option value="object">Workspace objects</option><option value="notebook">Notebooks</option><option value="notebook-block">Notebook blocks</option><option value="research-question">Research questions</option><option value="research-claim">Research claims</option><option value="analysis-question">Analysis questions</option><option value="decision">Decisions</option><option value="briefing-draft">Briefing drafts</option><option value="citation-reference">Citation references</option><option value="research-task">Research tasks</option></select></label>
                        <label><span>Subtype</span><select data-scw-retrieval-subtype><option value="all">All subtypes</option></select></label>
                        <label><span>Project</span><select data-scw-integrated-project><option value="all">All projects</option></select></label>
                        <label><span>Tag</span><input type="text" maxlength="80" data-scw-retrieval-tag placeholder="Any matching tag"></label>
                        <label><span>Origin</span><select data-scw-retrieval-origin><option value="all">All origins</option></select></label>
                        <label><span>Provenance</span><select data-scw-retrieval-provenance><option value="all">Any provenance</option><option value="documented">Recorded provenance</option><option value="linked">Explicitly linked</option><option value="source-url">Source URL recorded</option><option value="bibliographic">Bibliographic context</option></select></label>
                        <label><span>Scope</span><select data-scw-retrieval-scope><option value="active">Active projects</option><option value="all">Active + archived</option></select></label>
                        <label><span>Sort</span><select data-scw-retrieval-sort><option value="relevance">Explainable relevance</option><option value="updated-desc">Recently updated</option><option value="updated-asc">Oldest updated</option><option value="title-asc">Title A–Z</option><option value="project-asc">Project A–Z</option></select></label>
                    </div>
                    <div class="scw-saved-search-bar"><label><span>Saved search</span><select data-scw-saved-search><option value="">Choose saved search</option></select></label><button type="button" class="scw-button" data-scw-save-search>Save current search</button><button type="button" class="scw-button" data-scw-delete-search disabled>Delete saved search</button><button type="button" class="scw-button" data-scw-clear-search>Clear filters</button><p data-scw-search-status role="status" aria-live="polite"></p></div>
                </section>
                <section class="scw-research-collections" data-scw-research-surface-panel="collections" data-scw-research-collections hidden aria-labelledby="scw-research-collections-title">
                    <div class="scw-research-collections-head"><div><span>DYNAMIC RESEARCH VIEWS</span><h3 id="scw-research-collections-title">Organize retrieval without copying research.</h3><p>Smart collections store explicit retrieval definitions. Saved views add grouping and density. Membership, dashboards, and project lenses are recalculated from canonical records whenever the Research workspace renders.</p></div><div class="scw-collection-metrics"><div><strong data-scw-collection-count>0</strong><span>smart collections</span></div><div><strong data-scw-view-count>0</strong><span>saved views</span></div></div></div>
                    <div class="scw-research-dashboard" aria-label="Derived research dashboard"><div><strong data-scw-dashboard-sources>0</strong><span>Sources</span></div><div><strong data-scw-dashboard-evidence>0</strong><span>Evidence</span></div><div><strong data-scw-dashboard-decisions>0</strong><span>Decisions</span></div><div><strong data-scw-dashboard-documented>0</strong><span>Documented</span></div><div><strong data-scw-dashboard-projects>0</strong><span>Projects</span></div><div><strong data-scw-dashboard-records>0</strong><span>Records</span></div></div>
                    <div class="scw-builtin-views" aria-label="Project-aware dynamic views"><button type="button" data-scw-dynamic-view="sources">Sources</button><button type="button" data-scw-dynamic-view="evidence">Evidence</button><button type="button" data-scw-dynamic-view="decisions">Decisions</button><button type="button" data-scw-dynamic-view="analysis">Analysis</button><button type="button" data-scw-dynamic-view="notebooks">Notebooks</button><button type="button" data-scw-dynamic-view="documented">Documented</button></div>
                    <div class="scw-collection-controls">
                        <label><span>Smart collection</span><select data-scw-smart-collection><option value="">Choose collection</option></select></label><button type="button" class="scw-button" data-scw-save-collection>Save current retrieval as collection</button><button type="button" class="scw-button" data-scw-delete-collection disabled>Delete collection</button>
                        <label><span>Saved view</span><select data-scw-research-view><option value="">Choose view</option></select></label><button type="button" class="scw-button" data-scw-save-view>Save current view</button><button type="button" class="scw-button" data-scw-delete-view disabled>Delete view</button>
                        <label><span>Group by</span><select data-scw-view-group><option value="project">Project</option><option value="kind">Kind</option><option value="subtype">Subtype</option><option value="origin">Origin</option><option value="none">None</option></select></label><label><span>Density</span><select data-scw-view-density><option value="comfortable">Comfortable</option><option value="compact">Compact</option></select></label>
                        <p data-scw-collection-status role="status" aria-live="polite"></p>
                    </div>
                    <div class="scw-dynamic-preview" data-scw-dynamic-preview><div class="scw-knowledge-empty-note">Dynamic view preview will appear here.</div></div>
                    <div class="scw-notebook-boundary" role="note"><strong>Definitions, not duplicate records.</strong><span>Smart collections and saved views are browser-local preferences. Their membership is recomputed from the v0.42 Advanced Retrieval corpus. No canonical research content is copied into this layer.</span></div>
                </section>
                <section class="scw-cross-project-knowledge" data-scw-research-surface-panel="cross-project" data-scw-cross-project-knowledge hidden aria-labelledby="scw-cross-project-knowledge-title">
                    <div class="scw-cross-project-head"><div><span>CROSS-PROJECT KNOWLEDGE</span><h3 id="scw-cross-project-knowledge-title">Reuse research across projects without copying the record.</h3><p>Select a canonical research result above, choose a different project as the context that needs it, and record an explicit relationship. The source stays owned by its original project; Workspace stores only the pointer, target project, relationship, and your note.</p></div><div class="scw-cross-project-metrics"><div><strong data-scw-cross-project-count>0</strong><span>references</span></div><div><strong data-scw-cross-project-projects>0</strong><span>target projects</span></div><div><strong data-scw-cross-project-unresolved>0</strong><span>unresolved</span></div></div></div>
                    <div class="scw-cross-project-toolbar"><label><span>Target project</span><select data-scw-cross-project-target><option value="">Choose target project</option></select></label><label><span>Relationship</span><select data-scw-cross-project-relation><option value="references">References</option><option value="supports">Supports</option><option value="informs">Informs</option><option value="extends">Extends</option><option value="contrasts">Contrasts</option><option value="related">Related</option></select></label><label class="scw-cross-project-note"><span>Context note</span><input type="text" maxlength="3000" data-scw-cross-project-note placeholder="Why this research matters in the target project"></label><button type="button" class="scw-button scw-button-primary" data-scw-cross-project-add disabled>Reference selected research</button><button type="button" class="scw-button" data-scw-cross-project-export>Export reference ledger</button><button type="button" class="scw-button" data-scw-cross-project-import>Import reference ledger</button><input type="file" accept="application/json,.json" data-scw-cross-project-import-file hidden><p data-scw-cross-project-status role="status" aria-live="polite"></p></div>
                    <div class="scw-cross-project-list" data-scw-cross-project-list><div class="scw-knowledge-empty-note">No cross-project references yet.</div></div>
                    <div class="scw-notebook-boundary" role="note"><strong>Reference, do not duplicate.</strong><span>Cross-project knowledge is a browser-local ledger of canonical pointers. It never copies source content into the target project, silently changes project ownership, infers relationships, or mutates either project. Missing source/target records remain visibly unresolved.</span></div>
                </section>
                <section class="scw-research-tasks" data-scw-research-surface-panel="tasks" data-scw-research-tasks hidden aria-labelledby="scw-research-tasks-title">
                    <div class="scw-research-tasks-head"><div><span>RESEARCH TASKS / WORKFLOW STATE</span><h3 id="scw-research-tasks-title">Track what research needs next without changing the research itself.</h3><p>Create explicit tasks around selected Integrated Knowledge records. Task state, priority, ownership labels, due dates, and history stay separate from the canonical record so “done” never silently changes a claim, source, citation, Notebook block, or Document.</p></div><div class="scw-research-task-metrics"><div><strong data-scw-task-open>0</strong><span>open</span></div><div><strong data-scw-task-progress>0</strong><span>in progress</span></div><div><strong data-scw-task-blocked>0</strong><span>blocked</span></div><div><strong data-scw-task-unresolved>0</strong><span>unresolved</span></div></div></div>
                    <div class="scw-research-task-layout">
                        <form class="scw-research-task-form" data-scw-task-form><div class="scw-knowledge-panel-head"><span>01 / CREATE</span><h4>Task for selected research</h4></div><p data-scw-task-selected>No research result selected.</p><label><span>Task type</span><select name="type"><option value="review-needed">Review needed</option><option value="verify-claim">Verify claim</option><option value="source-required">Source required</option><option value="citation-incomplete">Citation incomplete</option><option value="ready-for-synthesis">Ready for synthesis</option><option value="follow-up">Follow-up</option><option value="custom">Custom</option></select></label><div class="scw-research-task-form-row"><label><span>Priority</span><select name="priority"><option value="normal">Normal</option><option value="high">High</option><option value="critical">Critical</option><option value="low">Low</option></select></label><label><span>Due date</span><input type="date" name="dueDate"></label></div><label><span>Owner label</span><input name="owner" maxlength="160" placeholder="Self, editor, reviewer"></label><label><span>Task note</span><textarea name="note" rows="3" maxlength="4000" placeholder="What needs to happen next?"></textarea></label><button class="scw-button scw-button-primary" type="submit" data-scw-task-create disabled>Create task for selected research</button></form>
                        <div class="scw-research-task-board"><div class="scw-knowledge-panel-head"><span>02 / WORKFLOW</span><h4>Research task ledger</h4></div><div class="scw-research-task-filters"><label><span>Status</span><select data-scw-task-filter-status><option value="all">All states</option><option value="open">Open</option><option value="in-progress">In progress</option><option value="blocked">Blocked</option><option value="done">Done</option><option value="dismissed">Dismissed</option></select></label><label><span>Type</span><select data-scw-task-filter-type><option value="all">All types</option><option value="review-needed">Review needed</option><option value="verify-claim">Verify claim</option><option value="source-required">Source required</option><option value="citation-incomplete">Citation incomplete</option><option value="ready-for-synthesis">Ready for synthesis</option><option value="follow-up">Follow-up</option><option value="custom">Custom</option></select></label><label><span>Project</span><select data-scw-task-filter-project><option value="all">All projects</option></select></label><label><span>Resolution</span><select data-scw-task-filter-resolution><option value="all">All targets</option><option value="resolved">Resolved targets</option><option value="unresolved">Unresolved targets</option></select></label></div><div class="scw-research-task-list" data-scw-task-list><div class="scw-knowledge-empty-note">No research tasks yet. Select a research result first, then create a task only when a specific next action exists.</div></div><div class="scw-research-task-actions"><button class="scw-button" type="button" data-scw-task-export>Export task library</button><button class="scw-button" type="button" data-scw-task-import>Import task library</button><input type="file" accept="application/json,.json" data-scw-task-import-file hidden><p data-scw-task-status role="status" aria-live="polite"></p></div></div>
                    </div>
                    <div class="scw-notebook-boundary" role="note"><strong>Workflow state is not research state.</strong><span>Research Tasks are browser-local canonical pointers. Completing, blocking, dismissing, importing, exporting, or deleting a task never edits the record it references. Workspace does not generate tasks automatically or infer that research is complete.</span></div>
                </section>

                <section class="scw-grounded-research-assistant" data-scw-research-surface-panel="assistant" data-scw-grounded-research-assistant hidden aria-labelledby="scw-grounded-research-assistant-title">
                    <div class="scw-grounded-research-head"><div><span>GROUNDED RESEARCH ASSISTANT II</span><h3 id="scw-grounded-research-assistant-title">Ask across Integrated Knowledge without expanding the scope behind your back.</h3><p>Build an explicit multi-record grounding set from the research results on this page. Preparing a request freezes the selected records into an inspectable packet. Returned prose is accepted only when its citation markers resolve to that frozen set, and every substantive segment cites at least one selected record.</p></div><div class="scw-grounded-research-metrics"><div><strong data-scw-grounded-session-count>0</strong><span>draft sessions</span></div><div><strong data-scw-grounded-scope-count>0</strong><span>next-request scope</span></div></div></div>
                    <div class="scw-grounded-research-toolbar"><label><span>Saved request</span><select data-scw-grounded-session><option value="">Choose grounded request</option></select></label><button type="button" class="scw-button" data-scw-grounded-add-selected disabled>Add selected research to scope</button><button type="button" class="scw-button" data-scw-grounded-clear-scope>Clear next scope</button><button type="button" class="scw-button" data-scw-grounded-delete disabled>Delete request</button><p data-scw-grounded-status role="status" aria-live="polite"></p></div>
                    <div class="scw-grounded-research-layout">
                        <div class="scw-grounded-request"><div class="scw-knowledge-panel-head"><span>01 / SCOPE + QUESTION</span><h4>Prepare a frozen grounding request</h4></div><div class="scw-grounded-scope" data-scw-grounded-scope><div class="scw-knowledge-empty-note">Select research above and add it to the grounding scope.</div></div><form data-scw-grounded-form><label><span>Request title</span><input name="title" maxlength="240" placeholder="Research question"></label><label><span>Task</span><select name="task"><option value="grounded-summary">Grounded summary</option><option value="evidence-gaps">Evidence gaps &amp; contradictions</option><option value="compare-alternatives">Compare alternatives</option><option value="briefing-draft">Draft briefing section</option><option value="method-explanation">Explain method &amp; assumptions</option><option value="general-question">Grounded question</option></select></label><label><span>Question</span><textarea name="question" rows="5" maxlength="6000" required placeholder="Ask only what the selected research can support."></textarea></label><button type="submit" class="scw-button scw-button-primary">Prepare grounded request</button></form></div>
                        <div class="scw-grounded-packet"><div class="scw-knowledge-panel-head"><span>02 / PACKET</span><h4>Provider-neutral grounded prompt</h4></div><pre data-scw-grounded-prompt>Select a prepared request to inspect its frozen grounding packet.</pre><div class="scw-grounded-actions"><button type="button" class="scw-button" data-scw-grounded-export-request disabled>Export request</button><button type="button" class="scw-button" data-scw-grounded-copy disabled>Copy grounded prompt</button></div></div>
                        <div class="scw-grounded-review"><div class="scw-knowledge-panel-head"><span>03 / RESPONSE + REVIEW</span><h4>Citation-enforced draft</h4></div><label><span>Response source</span><select data-scw-grounded-response-source><option value="manual">Manual paste / review</option><option value="research-librarian">Research Librarian</option><option value="adapter">Connected adapter</option><option value="external">External AI tool</option></select></label><label><span>Draft response</span><textarea rows="10" maxlength="40000" data-scw-grounded-response placeholder="Return a draft with [1], [2], etc. Every substantive paragraph or list block must contain a valid citation marker."></textarea></label><div class="scw-grounded-actions"><button type="button" class="scw-button scw-button-primary" data-scw-grounded-save-response disabled>Validate &amp; save cited draft</button><button type="button" class="scw-button" data-scw-grounded-export-response disabled>Export response</button><button type="button" class="scw-button" data-scw-grounded-review disabled>Mark reviewed</button><button type="button" class="scw-button" data-scw-grounded-reject disabled>Reject draft</button></div><label><span>Materialize reviewed draft into</span><select data-scw-grounded-target-project><option value="">Choose project</option></select></label><button type="button" class="scw-button" data-scw-grounded-materialize disabled>Create Workspace Document</button><div class="scw-grounded-citations" data-scw-grounded-citations></div></div>
                    </div>
                    <div class="scw-notebook-boundary" role="note"><strong>Grounding is a boundary, not a suggestion.</strong><span>Workspace does not call an AI provider automatically, expand the selected scope, invent citations, infer missing metadata, or write a canonical Document without an explicit reviewed-materialization action. Request packets preserve exactly what was supplied for later review.</span></div>
                </section>


                <section class="scw-library-continuity" data-scw-research-surface-panel="library" data-scw-library-continuity hidden aria-labelledby="scw-library-continuity-title">
                    <div class="scw-library-continuity-head"><div><span>KNOWLEDGE LIBRARY / PROJECT CONTINUITY</span><h3 id="scw-library-continuity-title">Carry research context into Workspace without creating a second library.</h3><p>Stage saved searches, watchlists, research-queue items, source bundles, and private personal recommendations from the Knowledge Library. Every Library ID and origin remains visible. Nothing enters a Workspace project until you choose <strong>Add to project</strong>.</p></div></div>
                    <div class="scw-library-continuity-toolbar"><button type="button" class="scw-button scw-button-primary" data-scw-library-continuity-open>Open Knowledge Library</button><button type="button" class="scw-button" data-scw-library-continuity-import>Import Library package</button><input type="file" accept="application/json,.json" data-scw-library-continuity-import-file hidden><button type="button" class="scw-button" data-scw-library-continuity-clear>Clear staged context</button><p data-scw-library-continuity-status role="status" aria-live="polite"></p></div>
                    <div class="scw-library-continuity-list" data-scw-library-continuity-list><div class="scw-knowledge-empty-note">No Knowledge Library context is staged on this device.</div></div>
                    <div class="scw-notebook-boundary" role="note"><strong>One identity, two canonical systems.</strong><span>Authenticated Workspace and Library use the same WordPress account. Workspace does not copy the entire Library, read other users’ private recommendations, background-sync research, or mutate canonical Library records. Guest Workspace use remains first-class.</span></div>
                </section>
                <section class="scw-reference-library" data-scw-research-surface-panel="citations" data-scw-reference-library hidden aria-labelledby="scw-reference-library-title">
                    <div class="scw-reference-library-head"><div><span>CITATION LIBRARY / REFERENCE MANAGEMENT</span><h3 id="scw-reference-library-title">Manage reusable references without inventing metadata.</h3><p>Normalize recorded bibliographic fields, detect likely duplicates, assign citation keys, preview common citation styles, and reuse references across projects. Missing authors, dates, publishers, identifiers, and DOI metadata remain missing until you enter them.</p></div><div class="scw-reference-metrics"><div><strong data-scw-reference-count>0</strong><span>references</span></div><div><strong data-scw-reference-duplicates>0</strong><span>duplicate groups</span></div></div></div>
                    <div class="scw-reference-toolbar"><label><span>Citation style</span><select data-scw-citation-style><option value="apa7">APA 7</option><option value="chicago-author-date">Chicago author-date</option><option value="mla9">MLA 9</option><option value="ieee">IEEE</option></select></label><label class="scw-reference-search"><span>Find reference</span><input type="search" maxlength="240" data-scw-reference-search placeholder="Title, author, DOI, citation key"></label><button type="button" class="scw-button" data-scw-reference-add-selected disabled>Add selected research result</button><button type="button" class="scw-button" data-scw-reference-export>Export library</button><button type="button" class="scw-button" data-scw-reference-import>Import library</button><input type="file" accept="application/json,.json" data-scw-reference-import-file hidden><p data-scw-reference-status role="status" aria-live="polite"></p></div>
                    <div class="scw-reference-layout">
                        <form class="scw-reference-form" data-scw-reference-form><div class="scw-knowledge-panel-head"><span>ADD / EDIT</span><h4>Bibliographic reference</h4></div><input type="hidden" name="id"><label><span>Type</span><select name="type"><option value="article">Article</option><option value="book">Book</option><option value="chapter">Chapter</option><option value="report">Report</option><option value="webpage">Webpage</option><option value="dataset">Dataset</option><option value="thesis">Thesis</option><option value="conference">Conference</option><option value="other">Other</option></select></label><label><span>Title</span><input name="title" maxlength="500" required></label><label><span>Authors <em>semicolon separated</em></span><input name="authors" maxlength="2000"></label><div class="scw-reference-form-row"><label><span>Publication date</span><input name="publicationDate" maxlength="80"></label><label><span>Container / journal</span><input name="containerTitle" maxlength="300"></label></div><div class="scw-reference-form-row"><label><span>Publisher</span><input name="publisher" maxlength="300"></label><label><span>Pages / locator</span><input name="pages" maxlength="120"></label></div><div class="scw-reference-form-row"><label><span>DOI</span><input name="doi" maxlength="240"></label><label><span>Identifier</span><input name="identifier" maxlength="240"></label></div><label><span>URL</span><input name="url" maxlength="2000"></label><div class="scw-reference-form-row"><label><span>Citation key</span><input name="citationKey" maxlength="120" placeholder="Generated if blank"></label><label><span>Tags</span><input name="tags" maxlength="800" placeholder="research, climate"></label></div><label><span>Notes</span><textarea name="notes" rows="3" maxlength="4000"></textarea></label><div class="scw-reference-form-actions"><button class="scw-button scw-button-primary" type="submit">Save reference</button><button class="scw-button" type="button" data-scw-reference-form-clear>Clear</button></div></form>
                        <div class="scw-reference-list-panel"><div class="scw-knowledge-panel-head"><span>LIBRARY</span><h4>Reusable references</h4></div><div class="scw-reference-list" data-scw-reference-list><div class="scw-knowledge-empty-note">No references yet.</div></div></div>
                        <aside class="scw-reference-detail" data-scw-reference-detail><div class="scw-knowledge-empty-note">Select a reference to inspect its citation, normalized identifiers, origin links, and duplicate candidates.</div></aside>
                    </div>
                    <div class="scw-notebook-boundary" role="note"><strong>Recorded bibliography only.</strong><span>The Citation Library is browser-local Workspace data. It can normalize what you enter, but it does not query DOI services, scrape pages, infer missing metadata, automatically merge duplicates, or mutate Project records.</span></div>
                </section>

                <section class="scw-composition-studio" data-scw-research-surface-panel="composition" data-scw-composition-studio hidden aria-labelledby="scw-composition-studio-title">
                    <div class="scw-composition-head"><div><span>DOCUMENT / RESEARCH COMPOSITION</span><h3 id="scw-composition-studio-title">Compose structured research documents without copying canonical source records.</h3><p>Build ordered sections, attach selected Workspace research and Citation Library references, preview the resulting document, and materialize it into a canonical Workspace Document only when you explicitly choose to do so.</p></div><div class="scw-composition-metrics"><div><strong data-scw-composition-draft-count>0</strong><span>drafts</span></div><div><strong data-scw-composition-input-count>0</strong><span>inputs</span></div></div></div>
                    <div class="scw-composition-toolbar"><label><span>Composition</span><select data-scw-composition-draft><option value="">Choose composition</option></select></label><button class="scw-button" type="button" data-scw-composition-new>New composition</button><button class="scw-button" type="button" data-scw-composition-delete disabled>Delete draft</button><button class="scw-button" type="button" data-scw-composition-export disabled>Export draft</button><button class="scw-button" type="button" data-scw-composition-import>Import draft</button><input type="file" accept="application/json,.json" data-scw-composition-import-file hidden><p data-scw-composition-status-message role="status" aria-live="polite"></p></div>
                    <div class="scw-composition-layout">
                        <div class="scw-composition-editor"><div class="scw-knowledge-panel-head"><span>01 / DOCUMENT</span><h4>Structure and authorship</h4></div><label><span>Title</span><input type="text" maxlength="240" data-scw-composition-title disabled></label><label><span>Abstract / purpose</span><textarea rows="3" maxlength="5000" data-scw-composition-abstract disabled></textarea></label><label><span>Status</span><select data-scw-composition-status disabled><option value="draft">Draft</option><option value="review">Review</option><option value="ready">Ready</option></select></label>
                            <form class="scw-composition-section-form" data-scw-composition-section-form><div class="scw-knowledge-panel-head"><span>02 / SECTION</span><h4>Add authored section</h4></div><label><span>Section kind</span><select name="kind"><option value="introduction">Introduction</option><option value="question">Question</option><option value="sources">Sources</option><option value="evidence">Evidence</option><option value="analysis">Analysis</option><option value="decision">Decision</option><option value="discussion">Discussion</option><option value="conclusion">Conclusion</option><option value="bibliography">Bibliography</option><option value="custom">Custom</option></select></label><label><span>Section title</span><input name="title" maxlength="240" required></label><label><span>Authored text</span><textarea name="body" rows="6" maxlength="20000" placeholder="Write the section here. Workspace does not generate or infer the prose automatically."></textarea></label><button class="scw-button" type="submit">Add section</button></form>
                        </div>
                        <div class="scw-composition-structure"><div class="scw-knowledge-panel-head"><span>03 / INPUTS</span><h4>Attach research and references</h4></div><div class="scw-composition-attach"><button class="scw-button" type="button" data-scw-composition-attach-research disabled>Attach selected research result</button><button class="scw-button" type="button" data-scw-composition-attach-reference disabled>Attach selected Citation Library reference</button></div><p class="scw-composition-note">Select a section below before attaching inputs. Research attachments store canonical pointers, not copies of source content.</p><div data-scw-composition-section-list></div></div>
                        <aside class="scw-composition-preview"><div class="scw-knowledge-panel-head"><span>04 / PREVIEW</span><h4>Document preview</h4></div><pre data-scw-composition-preview>Select or create a composition to preview it.</pre><button class="scw-button scw-button-primary" type="button" data-scw-composition-materialize disabled>Create Workspace Document</button></aside>
                    </div>
                    <div class="scw-notebook-boundary" role="note"><strong>Composition remains reviewable until you materialize it.</strong><span>Drafts are browser-local. Canonical research is referenced, not copied. Citation metadata comes only from the Citation Library. Workspace never creates a Document automatically, rewrites a source record, or invents citations.</span></div>
                </section>
                <div class="scw-integrated-layout" data-scw-research-surface-panel="search" hidden><div><div class="scw-integrated-results" data-scw-integrated-results><div class="scw-knowledge-empty-note">No research records yet. Begin with a project question or capture a source; this index fills from canonical local records as the work develops.</div></div><div class="scw-integrated-more"><button class="scw-button" type="button" data-scw-integrated-load-more hidden>Load more</button></div></div><aside class="scw-integrated-detail" data-scw-integrated-detail><div class="scw-knowledge-empty-note">Select a result to inspect its canonical origin, ranking reasons, provenance, and related material.</div></aside></div>
                <div class="scw-notebook-boundary" data-scw-research-surface-panel="search" hidden role="note"><strong>Retrieval over canonical records.</strong><span>Advanced Retrieval derives results from the Integrated Knowledge index at runtime. Saved searches are local browser preferences only. No server search index, semantic embeddings, automatic AI, inferred relationships, or canonical record mutation are introduced.</span></div>
            </section>

            <section class="scw-research-notebook" data-scw-workspace-section="notebook" hidden aria-labelledby="scw-notebook-title">
                <div class="scw-notebook-head">
                    <div><div class="scw-kicker">RESEARCH NOTEBOOK</div><h2 id="scw-notebook-title">Capture, connect, synthesize, and question research without losing provenance.</h2><p>Keep working notes alongside captured sources, connect them explicitly, promote selected material into structured Workspace artifacts, and ask grounded questions against only the research you choose. Notebook originals remain in place.</p></div>
                    <label class="scw-notebook-project"><span>PROJECT</span><select data-scw-notebook-project><option value="">Choose project</option></select></label>
                </div>
                <div class="scw-notebook-metrics" aria-label="Research Notebook metrics">
                    <div><strong data-scw-notebook-metric-notebooks>0</strong><span>notebooks</span></div>
                    <div><strong data-scw-notebook-metric-sections>0</strong><span>sections</span></div>
                    <div><strong data-scw-notebook-metric-blocks>0</strong><span>blocks</span></div>
                    <div><strong data-scw-notebook-metric-promoted>0</strong><span>promoted</span></div>
                    <div><strong data-scw-notebook-metric-captures>0</strong><span>capture inbox</span></div>
                    <div><strong data-scw-notebook-metric-collections>0</strong><span>collections</span></div>
                    <div><strong data-scw-notebook-metric-links>0</strong><span>links</span></div>
                    <div><strong data-scw-notebook-metric-backlinks>0</strong><span>backlinked targets</span></div>
                    <div><strong data-scw-notebook-metric-syntheses>0</strong><span>syntheses</span></div>
                    <div><strong data-scw-notebook-metric-assistances>0</strong><span>grounded questions</span></div>
                </div>
                <section class="scw-source-capture" aria-labelledby="scw-source-capture-title">
                    <div class="scw-source-capture-head"><div><div class="scw-editorial-kicker">SOURCE CAPTURE / RESEARCH CLIPPING</div><h3 id="scw-source-capture-title">Bring research into the notebook without losing where it came from.</h3><p>Paste a source or excerpt manually, or review captures staged by compatible Sustainable Catalyst research surfaces. Workspace does not fetch the URL, scrape the page, infer citation facts, or save an incoming capture until you choose a destination.</p></div><button class="scw-button" type="button" data-scw-notebook-capture-import>Import capture request</button><input type="file" accept="application/json,.json" data-scw-notebook-capture-file hidden></div>
                    <div class="scw-source-capture-grid">
                        <form class="scw-source-capture-form" data-scw-notebook-capture-form>
                            <div class="scw-knowledge-panel-head"><span>CAPTURE MANUALLY</span><h4>Source or excerpt</h4></div>
                            <div class="scw-notebook-block-form-row"><label><span>Capture type</span><select name="blockType"><option value="source">Source</option><option value="excerpt">Excerpt / quotation</option></select></label><label><span>Source surface</span><select name="sourceSurface"><option value="manual">Manual</option><option value="knowledge-library">Knowledge Library</option><option value="research-librarian">Research Librarian</option><option value="external-web">External web</option><option value="document">Document</option><option value="other">Other</option></select></label></div>
                            <label><span>Title</span><input name="title" maxlength="240" required placeholder="Source or document title"></label>
                            <label><span>Source URL</span><input name="sourceUrl" type="url" maxlength="2000" placeholder="https://"></label>
                            <label><span>Excerpt / notes</span><textarea name="content" rows="5" maxlength="50000" placeholder="Paste the excerpt, quotation, abstract, or your capture note."></textarea></label>
                            <div class="scw-source-capture-biblio"><label><span>Authors <em>semicolon separated</em></span><input name="authors" maxlength="1200" placeholder="Author One; Author Two"></label><label><span>Publisher</span><input name="publisher" maxlength="240"></label><label><span>Journal / collection</span><input name="containerTitle" maxlength="240"></label><label><span>Publication date</span><input name="publicationDate" maxlength="80" placeholder="2026-08-09"></label><label><span>Identifier</span><input name="identifier" maxlength="240" placeholder="ISBN, report number, repository ID"></label><label><span>DOI</span><input name="doi" maxlength="240"></label><label><span>Locator / pages</span><input name="locator" maxlength="240" placeholder="pp. 42–47, §3.2"></label><label><span>License</span><input name="license" maxlength="240"></label></div>
                            <label><span>Tags</span><input name="tags" maxlength="500" placeholder="grid, reliability, policy"></label>
                            <button class="scw-button scw-button-primary" type="submit">Save capture to active section</button>
                        </form>
                        <section class="scw-source-capture-inbox-panel" aria-labelledby="scw-source-capture-inbox-title"><div class="scw-knowledge-panel-head"><span>INCOMING</span><h4 id="scw-source-capture-inbox-title">Capture inbox</h4></div><div class="scw-source-capture-inbox" data-scw-notebook-capture-inbox><div class="scw-notebook-empty">No incoming captures.</div></div></section>
                    </div>
                </section>
                <div class="scw-notebook-layout">
                    <aside class="scw-notebook-rail" aria-labelledby="scw-notebook-list-title">
                        <div class="scw-knowledge-panel-head"><span>01 / NOTEBOOKS</span><h3 id="scw-notebook-list-title">Project notebooks</h3></div>
                        <form class="scw-notebook-create" data-scw-notebook-create-form>
                            <label><span>Notebook title</span><input name="title" maxlength="160" required placeholder="Research Notebook"></label>
                            <label><span>Description</span><textarea name="description" rows="2" maxlength="1200" placeholder="What are you collecting or thinking through?"></textarea></label>
                            <button class="scw-button" type="submit">Create notebook</button>
                        </form>
                        <div class="scw-notebook-list" data-scw-notebook-list></div>
                    </aside>
                    <div class="scw-notebook-workspace">
                        <section class="scw-notebook-active" data-scw-notebook-active><div class="scw-notebook-empty">Choose or create a notebook.</div></section>
                        <div class="scw-notebook-columns">
                            <section class="scw-notebook-sections" aria-labelledby="scw-notebook-sections-title">
                                <div class="scw-knowledge-panel-head"><span>02 / SECTIONS</span><h3 id="scw-notebook-sections-title">Sections</h3></div>
                                <form class="scw-notebook-section-form" data-scw-notebook-section-form><label><span>New section</span><input name="title" maxlength="160" required placeholder="Core Sources"></label><button class="scw-button" type="submit">Add section</button></form>
                                <div data-scw-notebook-section-list></div>
                            </section>
                            <section class="scw-notebook-blocks" aria-labelledby="scw-notebook-blocks-title">
                                <div class="scw-knowledge-panel-head"><span>03 / WORKING NOTES</span><h3 id="scw-notebook-blocks-title">Blocks</h3></div>
                                <form class="scw-notebook-block-form" data-scw-notebook-block-form>
                                    <div class="scw-notebook-block-form-row"><label><span>Type</span><select name="type"><option value="note">Note</option><option value="source">Source</option><option value="excerpt">Excerpt</option><option value="question">Question</option><option value="claim">Claim</option><option value="reference">Reference</option><option value="checklist">Checklist</option><option value="divider">Divider</option><option value="attachment">Attachment reference</option></select></label><label><span>Title</span><input name="title" maxlength="240" placeholder="Working title"></label></div>
                                    <label><span>Content</span><textarea name="content" rows="5" maxlength="50000" placeholder="Capture the thought, passage, question, claim, checklist, or context."></textarea></label>
                                    <div class="scw-notebook-block-form-row"><label><span>Source URL</span><input name="sourceUrl" type="url" maxlength="2000" placeholder="https://"></label><label><span>Reference object</span><select name="referenceObjectId" data-scw-notebook-block-object><option value="">No object reference</option></select></label></div>
                                    <label><span>Tags</span><input name="tags" maxlength="500" placeholder="grid, reliability, policy"></label>
                                    <button class="scw-button scw-button-primary" type="submit">Add block</button>
                                </form>
                                <div class="scw-notebook-block-list" data-scw-notebook-block-list></div>
                            </section>
                        </div>
                        <div class="scw-notebook-footer"><div data-scw-notebook-status role="status" aria-live="polite">Notebook is local to its Workspace Project.</div><button class="scw-button" type="button" data-scw-notebook-export disabled>Export active notebook</button></div>
                        <section class="scw-notebook-portability" aria-labelledby="scw-notebook-portability-title">
                            <div class="scw-knowledge-panel-head"><span>PORTABILITY / SYNC</span><h3 id="scw-notebook-portability-title">Move notebooks without surrendering version history.</h3></div>
                            <p>Export or import a notebook as an integrity-checked portable copy, create notebook-level restore points, or opt a signed-in notebook into explicit cross-device sync. Imports and restores always create new notebook copies.</p>
                            <div class="scw-notebook-portability-controls"><button class="scw-button" type="button" data-scw-notebook-portable-import>Import notebook</button><input type="file" accept="application/json,.json" data-scw-notebook-portable-file hidden><button class="scw-button" type="button" data-scw-notebook-restore-create>Create restore point</button><button class="scw-button" type="button" data-scw-notebook-backup>Back up notebook</button><button class="scw-button" type="button" data-scw-notebook-sync-toggle>Enable sync</button><button class="scw-button" type="button" data-scw-notebook-sync-check>Check status</button><button class="scw-button scw-button-primary" type="button" data-scw-notebook-sync-now>Sync now</button><button class="scw-button" type="button" data-scw-notebook-sync-cloud-copy>Open cloud as copy</button><button class="scw-button" type="button" data-scw-notebook-sync-keep-local>Keep local as sync head</button></div>
                            <div class="scw-notebook-portability-status" data-scw-notebook-portability-status role="status" aria-live="polite">Notebook remains local unless you explicitly export, back up, or enable sync.</div>
                            <div data-scw-notebook-restore-list></div>
                            <div class="scw-notebook-sync-boundary"><strong>No silent last-write-wins</strong><span>Notebook sync uses a server revision precondition. A stale device receives a conflict instead of overwriting a newer cloud notebook. Recovery preserves both copies.</span></div>
                        </section>
                    </div>
                </div>
                <section class="scw-notebook-review-provenance" aria-labelledby="scw-notebook-review-title">
                    <div class="scw-notebook-linking-head"><div><div class="scw-editorial-kicker">REVIEW / PROVENANCE</div><h3 id="scw-notebook-review-title">Review notebook changes, reconcile selectively, and inspect lineage.</h3><p>Compare the current notebook with one of its named restore points, choose individual changes to carry forward into a new notebook copy, reconstruct a notebook audit history from authoritative records, and inspect source lineage without hidden scoring.</p></div></div>
                    <div class="scw-notebook-review-grid">
                        <section class="scw-notebook-review-panel"><div class="scw-knowledge-panel-head"><span>01 / CHANGE REVIEW</span><h4>Notebook diff</h4></div><label><span>Baseline restore point</span><select data-scw-notebook-review-baseline><option value="">Choose restore point</option></select></label><button class="scw-button" type="button" data-scw-notebook-review-create>Create Change Review</button><div data-scw-notebook-review-summary class="scw-notebook-review-summary">No notebook review generated yet.</div><div data-scw-notebook-review-list></div></section>
                        <section class="scw-notebook-review-panel"><div class="scw-knowledge-panel-head"><span>02 / RECONCILE</span><h4>Selective apply</h4></div><label><span>Reviewer label</span><input type="text" maxlength="160" value="Workspace owner" data-scw-notebook-reconcile-reviewer></label><label><span>Rationale</span><textarea maxlength="4000" rows="3" placeholder="Why should these selected changes be carried forward?" data-scw-notebook-reconcile-rationale></textarea></label><label class="scw-notebook-reconcile-ack"><input type="checkbox" data-scw-notebook-reconcile-ack> <span>I understand reconciliation creates a new notebook copy and leaves both source states unchanged.</span></label><button class="scw-button scw-button-primary" type="button" data-scw-notebook-reconcile-create>Create reconciled notebook copy</button><div data-scw-notebook-reconcile-history></div></section>
                        <section class="scw-notebook-review-panel"><div class="scw-knowledge-panel-head"><span>03 / LINEAGE</span><h4>Source lineage inspection</h4></div><label><span>Notebook material</span><select data-scw-notebook-lineage-ref><option value="">Choose notebook material</option></select></label><button class="scw-button" type="button" data-scw-notebook-lineage-inspect>Inspect lineage</button><div data-scw-notebook-lineage-result></div></section>
                    </div>
                    <section class="scw-notebook-audit"><div class="scw-knowledge-panel-head"><span>04 / AUDIT HISTORY</span><h4>Derived notebook governance history</h4></div><div data-scw-notebook-audit-list><div class="scw-notebook-empty">Notebook audit events will appear here.</div></div></section>
                    <div class="scw-notebook-sync-boundary"><strong>Review is advisory; reconciliation is explicit.</strong><span>Change Review does not decide which state is correct. Selective reconciliation creates a separate notebook copy. Audit history and lineage are derived from existing notebook records; Workspace does not maintain a shadow provenance database or calculate a hidden change/confidence score.</span></div>
                </section>

                <section class="scw-notebook-linking" aria-labelledby="scw-notebook-linking-title">
                    <div class="scw-notebook-linking-head"><div><div class="scw-editorial-kicker">COLLECTIONS / KNOWLEDGE LINKING</div><h3 id="scw-notebook-linking-title">Connect notes, sources, notebooks, and structured Workspace objects explicitly.</h3><p>Collections group research without copying it. Links create inspectable relationships between notebook material and existing Workspace objects; backlinks are derived from those explicit links.</p></div></div>
                    <div class="scw-notebook-linking-grid">
                        <section class="scw-notebook-link-panel" aria-labelledby="scw-notebook-collections-title"><div class="scw-knowledge-panel-head"><span>04 / COLLECTIONS</span><h4 id="scw-notebook-collections-title">Research collections</h4></div>
                            <form class="scw-notebook-collection-form" data-scw-notebook-collection-form><label><span>Collection title</span><input name="title" maxlength="160" required placeholder="Grid reliability evidence"></label><label><span>Description</span><textarea name="description" rows="2" maxlength="1200" placeholder="Optional organizing context"></textarea></label><button class="scw-button" type="submit">Create collection</button></form>
                            <form class="scw-notebook-collection-assign-form" data-scw-notebook-collection-assign-form><label><span>Collection</span><select name="collectionId" data-scw-notebook-collection-select><option value="">Choose collection</option></select></label><label><span>Add item</span><select name="itemRef" data-scw-notebook-collection-item><option value="">Choose notebook, note, source, or object</option></select></label><button class="scw-button" type="submit">Add to collection</button></form>
                            <div class="scw-notebook-collection-list" data-scw-notebook-collection-list></div>
                        </section>
                        <section class="scw-notebook-link-panel" aria-labelledby="scw-notebook-links-title"><div class="scw-knowledge-panel-head"><span>05 / LINKS &amp; BACKLINKS</span><h4 id="scw-notebook-links-title">Explicit knowledge links</h4></div>
                            <form class="scw-notebook-link-form" data-scw-notebook-link-form><label><span>From</span><select name="sourceRef" data-scw-notebook-link-source><option value="">Choose source item</option></select></label><label><span>Relationship</span><select name="relation"><option value="references">References</option><option value="supports">Supports</option><option value="contrasts">Contrasts</option><option value="extends">Extends</option><option value="related">Related</option></select></label><label><span>To</span><select name="targetRef" data-scw-notebook-link-target><option value="">Choose target item</option></select></label><label><span>Link note <em>optional</em></span><input name="note" maxlength="1000" placeholder="Why are these connected?"></label><button class="scw-button scw-button-primary" type="submit">Create explicit link</button></form>
                            <div class="scw-notebook-link-list" data-scw-notebook-link-list></div>
                        </section>
                    </div>
                </section>
                <section class="scw-notebook-synthesis" aria-labelledby="scw-notebook-synthesis-title">
                    <div class="scw-notebook-linking-head"><div><div class="scw-editorial-kicker">SYNTHESIS / CITATIONS</div><h3 id="scw-notebook-synthesis-title">Build reviewable research structures from selected material.</h3><p>Create outlines, citation packs, source matrices, evidence summaries, and research-synthesis drafts from notebook blocks and Workspace objects you explicitly select. Missing citation facts remain missing rather than being guessed.</p></div></div>
                    <form class="scw-notebook-synthesis-form" data-scw-notebook-synthesis-form>
                        <label><span>Output</span><select name="kind"><option value="outline">Outline</option><option value="citation-pack">Citation pack</option><option value="source-matrix">Source matrix</option><option value="evidence-summary">Evidence summary</option><option value="research-synthesis">Research synthesis draft</option></select></label>
                        <label><span>Title</span><input name="title" maxlength="240" placeholder="Working synthesis title"></label>
                        <label class="scw-notebook-synthesis-material-label"><span>Selected material</span><select name="material" multiple size="8" data-scw-notebook-synthesis-material aria-describedby="scw-notebook-synthesis-help"></select><small id="scw-notebook-synthesis-help">Select one or more notebook blocks or Workspace objects. Use Command/Control for multiple selections.</small></label>
                        <button class="scw-button scw-button-primary" type="submit">Create synthesis</button>
                    </form>
                    <div class="scw-notebook-synthesis-list" data-scw-notebook-synthesis-list><div class="scw-notebook-empty">No synthesis outputs yet.</div></div>
                </section>
                <section class="scw-notebook-assistance" aria-labelledby="scw-notebook-assistance-title">
                    <div class="scw-notebook-linking-head"><div><div class="scw-editorial-kicker">GROUNDED NOTEBOOK ASSISTANCE</div><h3 id="scw-notebook-assistance-title">Ask against explicitly selected research—and require the answer to cite it.</h3><p>Prepare a question using only selected Notebook blocks or Workspace objects. Grounding material is numbered locally. Returned or pasted answers must use those citation markers, and remain reviewable drafts until you explicitly accept or materialize them.</p></div></div>
                    <form class="scw-notebook-assistance-form" data-scw-notebook-assistance-form>
                        <label><span>Question title <em>optional</em></span><input name="title" maxlength="240" placeholder="Working question title"></label>
                        <label><span>Question</span><textarea name="question" rows="4" maxlength="5000" required placeholder="What does the selected material support, contradict, leave uncertain, or help explain?"></textarea></label>
                        <label class="scw-notebook-synthesis-material-label"><span>Grounding material</span><select name="material" multiple size="8" data-scw-notebook-assistance-material aria-describedby="scw-notebook-assistance-help"></select><small id="scw-notebook-assistance-help">Select one or more Notebook blocks or Workspace objects. They become the complete allowed grounding set for this question.</small></label>
                        <button class="scw-button scw-button-primary" type="submit">Prepare grounded question</button>
                    </form>
                    <div class="scw-notebook-assistance-list" data-scw-notebook-assistance-list><div class="scw-notebook-empty">No grounded Notebook questions yet.</div></div>
                </section>
                <section class="scw-notebook-promotions" aria-labelledby="scw-notebook-promotions-title">
                    <div class="scw-notebook-linking-head"><div><div class="scw-editorial-kicker">NOTEBOOK → WORKSPACE</div><h3 id="scw-notebook-promotions-title">Promotion lineage</h3><p>Each derivative records the notebook block it came from. A block may be promoted more than once when different structured representations are useful.</p></div></div>
                    <div class="scw-notebook-promotion-list" data-scw-notebook-promotion-list><div class="scw-notebook-empty">No notebook material has been promoted into Workspace artifacts yet.</div></div>
                </section>

                <div class="scw-notebook-boundary" role="note"><strong>Notebook links are explicit working relationships, not inferred truth.</strong><span>Collections store references rather than duplicate research. Backlinks are derived only from links you create. Promotions remain explicit; every derivative is recorded in a visible promotion ledger and the notebook original remains preserved. Synthesis uses only material you explicitly select; citation facts are carried forward only when present. Grounded Notebook Assistance also uses only explicit selection, rejects answer citations outside that set, and keeps returned AI output as a reviewable draft. No AI submission, remote fetch, page scraping, semantic linking, citation guessing, source mutation, or upload runs automatically.</span></div>
            </section>

            <section class="scw-projects" data-scw-workspace-section="projects" hidden aria-labelledby="scw-projects-title">
                <div class="scw-section-head scw-section-head-projects">
                    <div>
                        <div class="scw-kicker">PROJECTS</div>
                        <h2 id="scw-projects-title">Projects that preserve the reasoning.</h2>
                    </div>
                    <div class="scw-project-actions">
                        <button class="scw-button scw-button-primary" type="button" data-scw-new-project>New project</button>
                        <button class="scw-button" type="button" data-scw-import-project>Import project</button>
                        <input type="file" accept="application/json,.json" data-scw-import-file hidden>
                    </div>
                </div>
                <div class="scw-project-import-stage" data-scw-project-import-stage hidden aria-live="polite"></div>
                <div class="scw-project-import-actions">
                    <button class="scw-button scw-button-primary" type="button" data-scw-project-import-commit disabled>Import staged copy</button>
                    <button class="scw-button" type="button" data-scw-project-import-clear disabled>Clear staged import</button>
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
                    <div class="scw-empty-actions"><button class="scw-button scw-button-primary" type="button" data-scw-empty-new>New project</button><button class="scw-button" type="button" data-scw-empty-start>Back to Start</button></div>
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
                    <label><span>Type</span><select data-scw-knowledge-type><option value="all">All types</option><option value="source">Sources</option><option value="evidence">Evidence</option><option value="dataset">Datasets</option><option value="analysis">Analyses</option><option value="decision">Decisions</option><option value="document">Documents</option><option value="export">Exports</option><option value="notebook">Notebooks</option><option value="notebook-block">Notebook blocks</option><option value="research-question">Research questions</option><option value="research-claim">Research claims</option><option value="reference">Citation references</option><option value="synthesis">Syntheses</option><option value="canvas-node">Canvas nodes</option></select></label>
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
                    <div><div class="scw-editorial-kicker">RESEARCH GRAPH &amp; RELATIONSHIP EXPLORER</div><h2 id="scw-graph-title">Trace how research moves from sources and notebook material through evidence, analysis, decisions, documents, citations, and synthesis.</h2><p>The graph is derived at runtime from canonical Workspace records, Notebook links and backlinks, recorded provenance, promotions, synthesis selections, research evidence relationships, and Citation Library origins. Every edge remains inspectable.</p></div>
                </div>
                <div class="scw-graph-metrics" aria-label="Knowledge graph metrics">
                    <div><strong data-scw-graph-metric-nodes>0</strong><span>Nodes</span></div><div><strong data-scw-graph-metric-edges>0</strong><span>Relationships</span></div><div><strong data-scw-graph-metric-projects>0</strong><span>Projects</span></div><div><strong data-scw-graph-metric-provenance>0</strong><span>Provenance sources</span></div>
                </div>
                <div class="scw-graph-controls">
                    <label class="scw-graph-search"><span>Search graph</span><input type="search" maxlength="240" data-scw-graph-search placeholder="Search projects, objects, provenance, tags"></label>
                    <label><span>Node type</span><select data-scw-graph-node-type><option value="all">All nodes</option><option value="project">Projects</option><option value="provenance">Provenance</option><option value="library-record">Library records</option><option value="source">Sources</option><option value="evidence">Evidence</option><option value="dataset">Datasets</option><option value="analysis">Analyses</option><option value="decision">Decisions</option><option value="document">Documents</option><option value="export">Exports</option><option value="notebook">Notebooks</option><option value="notebook-block">Notebook blocks</option><option value="research-question">Research questions</option><option value="research-claim">Research claims</option><option value="reference">Citation references</option><option value="synthesis">Syntheses</option><option value="canvas-node">Canvas nodes</option></select></label>
                    <label><span>Relationship</span><select data-scw-graph-relation><option value="all">All relationships</option><option value="contains">Contains</option><option value="sourced-from">Sourced from</option><option value="same-source">Same source</option><option value="evidence-from">Evidence from</option><option value="uses">Uses</option><option value="informs">Informs</option><option value="supports">Supports</option><option value="references">References</option><option value="contrasts">Contrasts</option><option value="extends">Extends</option><option value="related">Related</option><option value="promoted-to">Promoted to</option><option value="synthesized-into">Synthesized into</option><option value="cited-as">Cited as</option><option value="supports-claim">Supports claim</option><option value="captured-from">Captured from</option><option value="contradicts">Contradicts</option><option value="derived-from">Derived from</option><option value="produced-by">Produced by</option><option value="supersedes">Supersedes</option><option value="cites">Cites</option><option value="originates-in-library">Originates in Library</option></select></label>
                    <label><span>Project</span><select data-scw-graph-project><option value="all">All projects</option></select></label>
                    <label><span>Scope</span><select data-scw-graph-scope><option value="active">Active projects</option><option value="all">Active + archived</option></select></label>
                    <label><span>Depth</span><select data-scw-graph-depth><option value="1">1 hop</option><option value="2">2 hops</option></select></label>
                </div>
                <div class="scw-graph-path-controls" data-scw-graph-path-controls>
                    <label><span>Trace from</span><select data-scw-graph-path-from><option value="">Choose starting node</option></select></label>
                    <label><span>Trace to</span><select data-scw-graph-path-to><option value="">Choose destination node</option></select></label>
                    <button type="button" class="scw-button" data-scw-graph-path-trace>Trace explicit path</button>
                    <button type="button" class="scw-button" data-scw-graph-path-clear>Clear path</button>
                    <button type="button" class="scw-button" data-scw-graph-export>Export graph snapshot</button>
                    <p data-scw-graph-path-status role="status" aria-live="polite"></p>
                </div>
                <div class="scw-graph-path" data-scw-graph-path><div class="scw-knowledge-empty-note">Choose two nodes to trace a path through recorded Workspace relationships.</div></div>
                <div class="scw-graph-layout">
                    <section class="scw-graph-results-panel" aria-labelledby="scw-graph-results-heading"><div class="scw-knowledge-panel-head"><span>01 / SEARCH</span><h3 id="scw-graph-results-heading">Graph nodes</h3></div><div class="scw-graph-results" data-scw-graph-results></div></section>
                    <section class="scw-graph-canvas-panel" aria-labelledby="scw-graph-canvas-heading"><div class="scw-knowledge-panel-head"><span>02 / FOCUS</span><h3 id="scw-graph-canvas-heading">Relationship neighborhood</h3></div><svg class="scw-graph-svg" data-scw-graph-svg role="img" aria-label="Focused Workspace knowledge graph neighborhood"></svg><div class="scw-graph-detail" data-scw-graph-detail></div></section>
                    <aside class="scw-graph-relations-panel" aria-labelledby="scw-graph-relations-heading"><div class="scw-knowledge-panel-head"><span>03 / RELATIONSHIPS</span><h3 id="scw-graph-relations-heading">Why this node is connected</h3></div><div class="scw-graph-relations" data-scw-graph-relations></div></aside>
                </div>
                <div class="scw-knowledge-boundary" role="note"><strong>Inspectable graph, not inferred truth</strong><span>Workspace builds this graph locally from explicit project containment, Notebook links/backlinks, recorded provenance, promotion records, synthesis selections, Citation Library origins, traceability, research evidence links, analysis inputs, decision inputs, and deterministic same-source matches. Path tracing and backlinks use only recorded graph edges. Library continuity appears as pointer nodes when explicit provenance exists. It does not use semantic embeddings, a server graph database, or hidden relationship inference.</span></div>
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

            <section class="scw-change-review" data-scw-workspace-section="changes" hidden aria-labelledby="scw-change-review-title">
                <div class="scw-change-review-head">
                    <div><div class="scw-editorial-kicker">PROJECT DIFF &amp; CHANGE REVIEW</div><h2 id="scw-change-review-title">See what changed before you restore, sync, share, or promote.</h2><p>Compare the current project with a named restore point—or compare two restore points from the same project. Workspace reports explicit added, removed, and modified records, including evidence, assumptions, decisions, and relationships. Nothing is applied automatically.</p></div>
                    <div class="scw-change-review-boundary"><strong>Review only</strong><span>Change Review is derived from existing project snapshots. It does not create a second project database, calculate a hidden change score, or modify either state being compared.</span></div>
                </div>
                <div class="scw-change-review-controls">
                    <label><span>Project</span><select data-scw-change-project><option value="">Choose project</option></select></label>
                    <label><span>Base state</span><select data-scw-change-base disabled><option value="">Choose a restore point</option></select></label>
                    <label><span>Compare against</span><select data-scw-change-target disabled><option value="current">Current project</option></select></label>
                    <button class="scw-button scw-button-primary" type="button" data-scw-change-run disabled>Review changes</button>
                    <button class="scw-button" type="button" data-scw-change-export disabled>Export review JSON</button>
                    <button class="scw-button" type="button" data-scw-change-reconcile disabled>Reconcile changes</button>
                </div>
                <div class="scw-change-review-status" data-scw-change-status role="status" aria-live="polite">Choose a project and restore point to begin a change review.</div>
                <div class="scw-change-review-metrics" aria-label="Change review metrics">
                    <div><strong data-scw-change-added>0</strong><span>added</span></div><div><strong data-scw-change-removed>0</strong><span>removed</span></div><div><strong data-scw-change-modified>0</strong><span>modified</span></div><div><strong data-scw-change-relationships>0</strong><span>relationship changes</span></div>
                </div>
                <div class="scw-change-review-attention" data-scw-change-attention></div>
                <div class="scw-change-review-results" data-scw-change-results><div class="scw-change-review-empty">No comparison generated yet.</div></div>
                <div class="scw-change-review-governance" role="note"><strong>No automatic reconciliation</strong><span>Use this review to inform a restore, sync, share, or institutional handoff. Workspace does not merge project states or infer which version is correct.</span></div>
            </section>

            <section class="scw-reconciliation" data-scw-workspace-section="reconcile" hidden aria-labelledby="scw-reconciliation-title">
                <div class="scw-reconciliation-head">
                    <div><div class="scw-editorial-kicker">GUIDED RECONCILIATION &amp; SELECTIVE APPLY</div><h2 id="scw-reconciliation-title">Carry forward only the changes you explicitly choose.</h2><p>Start from a named restore point, compare it with the current project or another restore point, select individual changes, validate dependencies, and create a new reconciled project copy. Neither source state is edited.</p></div>
                    <div class="scw-reconciliation-boundary"><strong>New copy only</strong><span>Workspace never mutates either comparison source, never auto-selects changes, and never performs a hidden merge. A reconciled result is always created as a separate local project.</span></div>
                </div>
                <div class="scw-reconciliation-controls">
                    <label><span>Project</span><select data-scw-reconcile-project><option value="">Choose project</option></select></label>
                    <label><span>Base state</span><select data-scw-reconcile-base disabled><option value="">Choose a restore point</option></select></label>
                    <label><span>Target state</span><select data-scw-reconcile-target disabled><option value="current">Current project</option></select></label>
                    <button class="scw-button scw-button-primary" type="button" data-scw-reconcile-load disabled>Load differences</button>
                </div>
                <div class="scw-reconciliation-status" data-scw-reconcile-status role="status" aria-live="polite">Choose a project and base restore point to begin.</div>
                <div class="scw-reconciliation-metrics" aria-label="Reconciliation metrics"><div><strong data-scw-reconcile-metric-available>0</strong><span>available changes</span></div><div><strong data-scw-reconcile-metric-selected>0</strong><span>selected</span></div><div><strong data-scw-reconcile-metric-blockers>0</strong><span>dependency blockers</span></div><div><strong data-scw-reconcile-metric-copies>0</strong><span>reconciled copies</span></div></div>
                <div class="scw-reconciliation-actions"><button class="scw-button" type="button" data-scw-reconcile-select-all disabled>Select all</button><button class="scw-button" type="button" data-scw-reconcile-clear disabled>Clear selection</button><button class="scw-button" type="button" data-scw-reconcile-export disabled>Export plan JSON</button></div>
                <div class="scw-reconciliation-grid">
                    <section class="scw-reconciliation-panel"><div class="scw-knowledge-panel-head"><span>01 / SELECT</span><h3>Explicit changes</h3></div><div data-scw-reconcile-list><div class="scw-reconciliation-empty">No comparison loaded yet.</div></div></section>
                    <section class="scw-reconciliation-panel"><div class="scw-knowledge-panel-head"><span>02 / PREVIEW &amp; DECISION</span><h3>Reconciled copy preflight</h3></div><div data-scw-reconcile-preview><div class="scw-reconciliation-empty">Select one or more changes to build a preview.</div></div><div class="scw-reconciliation-decision"><label><span>Decision maker / reviewer label</span><input type="text" maxlength="160" value="Workspace owner" data-scw-reconcile-reviewer></label><label><span>Decision rationale</span><textarea maxlength="4000" data-scw-reconcile-rationale placeholder="Why are these changes being accepted while the others are declined?"></textarea></label></div><label class="scw-reconciliation-ack"><input type="checkbox" data-scw-reconcile-ack disabled> <span>I understand this creates a new local project copy, records my accepted and declined changes in a decision receipt, and leaves both source states unchanged.</span></label><button class="scw-button scw-button-primary" type="button" data-scw-reconcile-create disabled>Create reconciled copy + receipt</button></section>
                </div>
                <section class="scw-reconciliation-history"><div class="scw-knowledge-panel-head"><span>03 / LEDGER</span><h3>Recent reconciliations</h3></div><div data-scw-reconcile-history><div class="scw-reconciliation-empty">No reconciled copies have been created yet.</div></div></section>
                <section class="scw-reconciliation-receipts"><div class="scw-knowledge-panel-head"><span>04 / DECISION RECEIPTS</span><h3>Auditable reconciliation provenance</h3></div><div data-scw-reconcile-receipts><div class="scw-reconciliation-empty">No decision receipts have been created yet.</div></div></section>
                <div class="scw-reconciliation-governance" role="note"><strong>Selective apply is not an automatic merge.</strong><span>Workspace applies only checked records to a temporary candidate, validates dependencies, requires a decision-maker label and rationale, and creates a new project copy plus an integrity-fingerprinted decision receipt. Blocked plans cannot be created.</span></div>
            </section>

            <section class="scw-safe-actions" data-scw-workspace-section="safety" hidden aria-labelledby="scw-safe-actions-title">
                <div class="scw-safe-actions-head">
                    <div><div class="scw-editorial-kicker">CHANGE GATES &amp; SAFE ACTIONS</div><h2 id="scw-safe-actions-title">Require an explicit preflight before higher-risk actions.</h2><p>Restore, conflict resolution, portable sharing, and institutional promotion now pass through a visible gate. Workspace shows the relevant change review, requires human acknowledgement, and records the local action decision before proceeding.</p></div>
                    <div class="scw-safe-actions-boundary"><strong>No hidden risk score</strong><span>Gates explain what changed and what the action will do. They do not infer which state is correct, merge versions automatically, or rank project risk.</span></div>
                </div>
                <div class="scw-safe-actions-metrics" aria-label="Safe action metrics"><div><strong data-scw-safe-metric-total>0</strong><span>gated actions</span></div><div><strong data-scw-safe-metric-proceeded>0</strong><span>proceeded</span></div><div><strong data-scw-safe-metric-cancelled>0</strong><span>cancelled</span></div><div><strong data-scw-safe-metric-changes>0</strong><span>changes reviewed</span></div></div>
                <div class="scw-safe-actions-grid">
                    <section class="scw-safe-actions-panel"><div class="scw-knowledge-panel-head"><span>01 / POLICY</span><h3>Actions protected by a gate</h3></div><div class="scw-safe-actions-policy"><div><strong>Restore as copy</strong><span>Review restore-point versus current state before creating the recovered copy.</span></div><div><strong>Sync conflict resolution</strong><span>Compare local and cloud states before choosing which becomes the working/sync head.</span></div><div><strong>Portable sharing</strong><span>Review meaningful project changes and sharing scope before export.</span></div><div><strong>Institutional promotion</strong><span>Review project changes and promotion scope before exporting to Catalyst Intelligence.</span></div></div></section>
                    <section class="scw-safe-actions-panel"><div class="scw-knowledge-panel-head"><span>02 / LEDGER</span><h3>Recent safe-action decisions</h3></div><div data-scw-safe-history><div class="scw-safe-actions-empty">No gated actions have been recorded yet.</div></div></section>
                </div>
                <div class="scw-safe-actions-governance" role="note"><strong>Human decision remains the control point.</strong><span>Change gates never apply, restore, merge, sync, share, or promote automatically. The action runs only after its preflight is shown and the required acknowledgement is explicitly checked.</span></div>
            </section>

            <section class="scw-project-lifecycle" data-scw-workspace-section="lifecycle" hidden aria-labelledby="scw-project-lifecycle-title">
                <div class="scw-project-lifecycle-head">
                    <div><div class="scw-editorial-kicker">GOVERNANCE MILESTONES &amp; PROJECT LIFECYCLE</div><h2 id="scw-project-lifecycle-title">Declare where the work is—without letting the system decide for you.</h2><p>Workspace derives a visible readiness checklist from the project’s evidence, analysis, decisions, review state, publication work, and governance records. The checklist informs a human lifecycle declaration; it never advances the project automatically.</p></div>
                    <div class="scw-project-lifecycle-boundary"><strong>Human-declared state</strong><span>Readiness is evidence for judgment, not certification. A project may move forward or backward only after an explicit acknowledgement and rationale.</span></div>
                </div>
                <div class="scw-project-lifecycle-controls"><label><span>Project</span><select data-scw-lifecycle-project><option value="">Choose project</option></select></label><div class="scw-project-lifecycle-current"><span>CURRENT STATE</span><strong data-scw-lifecycle-current>Draft</strong><small data-scw-lifecycle-current-meta>No milestone declared yet.</small></div></div>
                <div class="scw-project-lifecycle-stages" data-scw-lifecycle-stages></div>
                <div class="scw-project-lifecycle-grid">
                    <section class="scw-project-lifecycle-panel"><div class="scw-knowledge-panel-head"><span>01 / READINESS</span><h3>Supporting conditions for the selected milestone</h3></div><label><span>Target milestone</span><select data-scw-lifecycle-target><option value="draft">Draft</option><option value="evidence-ready">Evidence-ready</option><option value="analysis-ready">Analysis-ready</option><option value="decision-ready">Decision-ready</option><option value="review-ready">Review-ready</option><option value="publication-ready">Publication-ready</option><option value="institutional-ready">Institutional-ready</option></select></label><div class="scw-project-lifecycle-readiness" data-scw-lifecycle-readiness><div class="scw-project-lifecycle-empty">Choose a project to inspect lifecycle readiness.</div></div><div class="scw-project-lifecycle-status" data-scw-lifecycle-status role="status" aria-live="polite"></div></section>
                    <section class="scw-project-lifecycle-panel"><div class="scw-knowledge-panel-head"><span>02 / DECLARE</span><h3>Record a governance milestone</h3></div><form data-scw-lifecycle-form class="scw-project-lifecycle-form"><label><span>Rationale</span><textarea name="rationale" rows="5" maxlength="4000" required placeholder="Why is this lifecycle state appropriate now? What remains unresolved?"></textarea></label><label class="scw-project-lifecycle-ack"><input type="checkbox" name="acknowledged" required> <span>I reviewed the visible readiness conditions and understand this lifecycle state is a human declaration, not a quality, compliance, or truth certification.</span></label><button class="scw-button scw-button-primary" type="submit">Record milestone</button></form></section>
                </div>
                <section class="scw-project-lifecycle-history"><div class="scw-knowledge-panel-head"><span>03 / HISTORY</span><h3>Lifecycle declarations</h3></div><div data-scw-lifecycle-history><div class="scw-project-lifecycle-empty">No lifecycle milestones have been recorded yet.</div></div></section>
                <div class="scw-project-lifecycle-governance" role="note"><strong>No readiness score. No automatic advancement.</strong><span>Workspace records the conditions that were visible when a milestone was declared, including unmet conditions. The project owner can deliberately move backward when new evidence, review, or analysis warrants it.</span></div>
            </section>

            <section class="scw-audit-trail" data-scw-workspace-section="audit" hidden aria-labelledby="scw-audit-trail-title">
                <div class="scw-audit-trail-head">
                    <div><div class="scw-editorial-kicker">PROJECT AUDIT TRAIL &amp; GOVERNANCE LEDGER</div><h2 id="scw-audit-trail-title">See how consequential Workspace actions accumulated over time.</h2><p>Audit Trail derives one chronological view from the authoritative histories already maintained by Workspace. It does not copy those events into a second shadow ledger.</p></div>
                    <div class="scw-audit-trail-boundary"><strong>Derived, not duplicated</strong><span>Restore points, sync, Safe Actions, reconciliation receipts, collaboration, institutional handoffs, sharing, interoperability, and project activity remain authoritative in their original ledgers.</span></div>
                </div>
                <div class="scw-audit-trail-controls">
                    <label><span>Project</span><select data-scw-audit-project><option value="">All projects</option></select></label>
                    <label><span>Event source</span><select data-scw-audit-source><option value="">All governance sources</option><option value="project-lifecycle">Project lifecycle</option><option value="version-history">Version history</option><option value="account-recovery">Account recovery</option><option value="cross-device-sync">Cross-device sync</option><option value="safe-actions">Safe Actions</option><option value="reconciliation">Reconciliation</option><option value="collaboration">Collaboration</option><option value="institutional-handoff">Institutional handoff</option><option value="share">Share &amp; portability</option><option value="interoperability">Import &amp; interoperability</option><option value="project-activity">Project activity</option></select></label>
                    <button type="button" class="scw-button" data-scw-audit-export>Export audit JSON</button>
                </div>
                <div class="scw-audit-trail-metrics" aria-label="Audit trail metrics"><div><strong data-scw-audit-metric-events>0</strong><span>events</span></div><div><strong data-scw-audit-metric-projects>0</strong><span>projects</span></div><div><strong data-scw-audit-metric-sources>0</strong><span>sources</span></div><div><strong data-scw-audit-metric-newest>None</strong><span>newest event</span></div></div>
                <div class="scw-audit-trail-list" data-scw-audit-list><div class="scw-audit-trail-empty">No governance events are available in this view yet.</div></div>
                <div class="scw-audit-trail-status" data-scw-audit-status role="status" aria-live="polite">Audit events are reconstructed locally from existing Workspace ledgers.</div>
                <div class="scw-audit-trail-governance" role="note"><strong>No hidden governance score.</strong><span>The audit trail is chronological and source-labeled. Workspace does not score compliance, infer misconduct, rank people, or edit authoritative source events from this view.</span></div>
            </section>

            <section class="scw-interoperability" data-scw-workspace-section="interoperability" hidden aria-labelledby="scw-interoperability-title">
                <div class="scw-interoperability-head">
                    <div>
                        <div class="scw-kicker">IMPORT &amp; INTEROPERABILITY</div>
                        <h2 id="scw-interoperability-title">Move research between systems without losing where it came from.</h2>
                        <p>Stage files locally, inspect the detected interchange profile and what Workspace will create, then commit into a project. v0.46 also exports structured Workspace JSON, Obsidian-ready Markdown, Notion-style CSV, Zotero-compatible CSL JSON, or a portable Workspace Project package.</p>
                    </div>
                </div>
                <div class="scw-interoperability-boundary" role="note"><strong>Review before commit</strong><span>Supported inputs: JSON, CSV/TSV, Markdown, HTML, and plain text. Workspace recognizes common Obsidian front matter, Notion-style columns, CSL JSON, and Workspace interchange packages locally. Nothing is uploaded, enriched from the network, or treated as verified evidence merely because it was imported.</span></div>
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
                        <div class="scw-knowledge-panel-head"><span>02 / EXPORT</span><h3 id="scw-interchange-heading">Choose an interchange profile</h3></div>
                        <p>Export canonical project material through an explicit format profile. Profiles are deterministic transforms of recorded Workspace data; they do not call external services or invent missing metadata.</p>
                        <label><span>Project</span><select data-scw-interoperability-export-project><option value="">Choose project</option></select></label>
                        <label><span>Profile</span><select data-scw-interoperability-export-profile><option value="workspace-json">Workspace structured JSON</option><option value="obsidian-markdown">Obsidian-ready Markdown</option><option value="notion-csv">Notion-style CSV</option><option value="zotero-csl-json">Zotero / CSL JSON</option><option value="portable-project">Workspace portable project</option></select></label>
                        <button class="scw-button" type="button" data-scw-interoperability-export>Export selected profile</button>
                        <div class="scw-interoperability-note"><strong>Canonical remains canonical</strong><span>Every interchange export is a portable copy. Re-importing creates new draft objects or a new local Project copy rather than overwriting canonical Workspace records. Obsidian, Notion, and Zotero profiles are compatibility foundations—not live integrations.</span></div>
                    </section>
                </div>
                <section class="scw-interoperability-history" aria-labelledby="scw-interoperability-history-heading">
                    <div class="scw-knowledge-panel-head"><span>03 / ACTIVITY</span><h3 id="scw-interoperability-history-heading">Recent interoperability activity</h3></div>
                    <div data-scw-interoperability-history></div>
                    <div class="scw-interoperability-compatibility" aria-labelledby="scw-backward-compatibility-title">
                        <div class="scw-editorial-kicker">BACKWARD COMPATIBILITY</div>
                        <h3 id="scw-backward-compatibility-title">Know what Workspace will accept before you commit an import.</h3>
                        <p>Project JSON is staged and classified locally. Supported historical schemas normalize only after explicit commit; newer future schemas are blocked rather than silently downgraded.</p>
                        <div class="scw-backward-compatibility-matrix" data-scw-backward-compatibility-matrix></div>
                        <button class="scw-button" type="button" data-scw-backward-compatibility-export>Export compatibility matrix</button>
                    </div>
                </section>
            </section>

            <section class="scw-collaboration" data-scw-workspace-section="collaboration" hidden aria-labelledby="scw-collaboration-title">
                <div class="scw-collaboration-head">
                    <div><div class="scw-editorial-kicker">SHARED REVIEW &amp; RESEARCH HANDOFF</div><h2 id="scw-collaboration-title">Package a deliberate research scope for external review, then reconcile responses without losing revision context.</h2><p>v0.73.0 hardens the asynchronous review boundary with scoped source-revision fingerprints, stale-response detection, duplicate-response blocking, explicit owner acknowledgement when source research has moved, and local reconciliation receipts. Reviewer and owner identities remain declarative rather than cryptographically verified; Workspace still does not provide live co-editing, automatic sending, or automatic application of proposed changes.</p></div>
                </div>
                <section class="scw-shared-review-handoff" data-scw-shared-review-handoff aria-labelledby="scw-shared-review-title">
                    <div class="scw-shared-review-head"><div><span>V0.54 / CONTROLLED HANDOFF</span><h3 id="scw-shared-review-title">Freeze only the research material a reviewer actually needs.</h3><p>A prepared handoff stores an explicit object scope as a frozen package. Later project edits do not rewrite that package. Returned responses must match its fingerprint before Workspace will stage them.</p></div><div class="scw-shared-review-metrics"><div><strong data-scw-handoff-metric-total>0</strong><span>handoffs</span></div><div><strong data-scw-handoff-metric-active>0</strong><span>active</span></div><div><strong data-scw-handoff-metric-staged>0</strong><span>staged</span></div><div><strong data-scw-handoff-metric-unresolved>0</strong><span>unresolved</span></div></div></div>
                    <div class="scw-shared-review-grid">
                        <section class="scw-shared-review-panel"><div class="scw-knowledge-panel-head"><span>01 / DEFINE</span><h3>Create a scoped handoff</h3></div><form data-scw-handoff-form><label><span>Project</span><select name="projectId" data-scw-handoff-project required><option value="">Choose project</option></select></label><label><span>Handoff title</span><input name="title" maxlength="220" required placeholder="e.g. External review of evidence and recommendation"></label><label><span>Purpose</span><textarea name="purpose" rows="4" maxlength="4000" placeholder="What should the reviewer examine, challenge, or verify?"></textarea></label><fieldset><legend>Declared reviewers</legend><div class="scw-handoff-choice-list" data-scw-handoff-reviewers><span class="scw-handoff-empty">Choose a project first.</span></div></fieldset><fieldset><legend>Explicit review scope</legend><div class="scw-handoff-choice-list" data-scw-handoff-scope><span class="scw-handoff-empty">Choose a project first.</span></div></fieldset><button class="scw-button scw-button-primary" type="submit">Create handoff</button></form></section>
                        <section class="scw-shared-review-panel"><div class="scw-knowledge-panel-head"><span>02 / FREEZE &amp; EXCHANGE</span><h3>Prepare and reconcile the review package</h3></div><div class="scw-handoff-list" data-scw-handoff-list></div><div class="scw-handoff-active" data-scw-handoff-active><div class="scw-handoff-empty">Choose a handoff to prepare or review.</div></div><div class="scw-review-integrity" data-scw-handoff-integrity role="status" aria-live="polite"><strong>NO PACKAGE ASSESSED</strong><span>Prepare a frozen package before importing a response.</span></div><label class="scw-review-owner-ack" data-scw-handoff-owner-ack-wrap hidden><input type="checkbox" data-scw-handoff-owner-ack> <span>I am acting as the declared handoff owner and explicitly choose to reconcile this response even though the source revision is stale or cannot be verified.</span></label><div class="scw-handoff-actions"><button class="scw-button" type="button" data-scw-handoff-prepare disabled>Prepare frozen package</button><button class="scw-button" type="button" data-scw-handoff-export disabled>Export package</button><button class="scw-button" type="button" data-scw-handoff-response-import disabled>Import response</button><input type="file" accept="application/json,.json" data-scw-handoff-response-file hidden><button class="scw-button scw-button-primary" type="button" data-scw-handoff-response-commit disabled>Reconcile staged response</button><button class="scw-button" type="button" data-scw-handoff-close disabled>Close handoff</button></div><pre data-scw-handoff-package-preview>No frozen review package prepared.</pre></section>
                    </div>
                    <section class="scw-shared-review-reviewer"><div class="scw-knowledge-panel-head"><span>03 / REVIEWER RESPONSE</span><h3>Prepare a package-matched response without touching the source Workspace.</h3></div><div class="scw-handoff-actions"><button class="scw-button" type="button" data-scw-reviewer-package-import>Import review package</button><input type="file" accept="application/json,.json" data-scw-reviewer-package-file hidden></div><p data-scw-reviewer-package-meta class="scw-handoff-meta">No review package loaded.</p><form data-scw-reviewer-response-form hidden><label><span>Reviewer</span><select name="actorId" data-scw-reviewer-actor required></select></label><label><span>Decision</span><select name="decision"><option value="no-decision">No decision</option><option value="approved">Approved</option><option value="changes-requested">Changes requested</option></select></label><label><span>Response summary</span><textarea name="summary" rows="4" maxlength="5000"></textarea></label><label><span>Response entry</span><select name="entryKind"><option value="comment">Comment</option><option value="proposal">Proposal</option></select></label><label><span>Target</span><select name="targetObjectId" data-scw-reviewer-target><option value="">Project-level</option></select></label><label><span>Comment / proposed change</span><textarea name="entryBody" rows="5" maxlength="8000"></textarea></label><button class="scw-button" type="submit">Export matched response</button></form></section>
                    <p data-scw-handoff-status class="scw-handoff-status" role="status" aria-live="polite">No handoff action pending.</p>
                    <div class="scw-collaboration-boundary" role="note"><strong>Staged review, not shared editing</strong><span>Review packages are explicit frozen copies of selected research objects. Responses must match the originating package fingerprint and are staged before import. Imported comments and proposals enter the collaboration ledger; no response automatically changes canonical research.</span></div>
                </section>
                <div class="scw-editorial-kicker scw-collab-legacy-kicker">COLLABORATION ARCHITECTURE FOUNDATION · V0.53 COMPATIBILITY</div>
                <section class="scw-collaboration-architecture" data-scw-collaboration-architecture aria-labelledby="scw-collab-architecture-title">
                    <div class="scw-collab-architecture-head"><div><span>V0.53 / ARCHITECTURE</span><h3 id="scw-collab-architecture-title">Collaboration contracts around canonical project ownership.</h3><p>Actors and policies are local coordination records. Comments and proposals point to projects or objects by stable ID. Shareable-project contracts carry ownership, scope, and role declarations—not project content and not server permission grants.</p></div><div class="scw-collab-architecture-metrics"><div><strong data-scw-collab-arch-actors>0</strong><span>actors</span></div><div><strong data-scw-collab-arch-policies>0</strong><span>project policies</span></div><div><strong data-scw-collab-arch-comments>0</strong><span>open comments</span></div><div><strong data-scw-collab-arch-proposals>0</strong><span>open proposals</span></div></div></div>
                    <div class="scw-collab-architecture-grid">
                        <section class="scw-collab-architecture-panel"><div class="scw-knowledge-panel-head"><span>01 / ACTORS</span><h3>Local collaboration identities</h3></div><form data-scw-collab-actor-form><label><span>Display label</span><input name="displayName" maxlength="120" required placeholder="Name, initials, team label"></label><label><span>Default role</span><select name="role"><option value="owner">Owner</option><option value="editor">Editor</option><option value="contributor">Contributor</option><option value="reviewer">Reviewer</option><option value="observer">Observer</option></select></label><button class="scw-button" type="submit">Add actor</button></form><div data-scw-collab-actor-list class="scw-collab-actor-list"></div></section>
                        <section class="scw-collab-architecture-panel"><div class="scw-knowledge-panel-head"><span>02 / OWNERSHIP &amp; GRANTS</span><h3>Project collaboration policy</h3></div><form data-scw-collab-policy-form><label><span>Project</span><select name="projectId" data-scw-collab-arch-project required><option value="">Choose project</option></select></label><label><span>Project owner</span><select name="ownerActorId" data-scw-collab-owner required><option value="">Choose actor</option></select></label><button class="scw-button scw-button-primary" type="submit">Save ownership policy</button></form><form data-scw-collab-grant-form><label><span>Collaborator</span><select name="actorId" data-scw-collab-grant-actor required><option value="">Choose actor</option></select></label><label><span>Role grant</span><select name="role"><option value="editor">Editor</option><option value="contributor">Contributor</option><option value="reviewer">Reviewer</option><option value="observer">Observer</option></select></label><button class="scw-button" type="submit">Add / update grant</button></form><div data-scw-collab-policy-summary class="scw-collab-policy-summary"></div></section>
                    </div>
                    <div class="scw-collab-architecture-grid">
                        <section class="scw-collab-architecture-panel"><div class="scw-knowledge-panel-head"><span>03 / COMMENTS</span><h3>Canonical-target discussion</h3></div><form data-scw-collab-comment-form><label><span>Actor</span><select name="actorId" data-scw-collab-comment-actor required><option value="">Choose actor</option></select></label><label><span>Target</span><select name="objectId" data-scw-collab-comment-object><option value="">Project-level comment</option></select></label><label><span>Comment</span><textarea name="body" rows="4" maxlength="5000" required></textarea></label><button class="scw-button" type="submit">Add comment</button></form><div data-scw-collab-comment-list class="scw-collab-record-list"></div></section>
                        <section class="scw-collab-architecture-panel"><div class="scw-knowledge-panel-head"><span>04 / PROPOSALS</span><h3>Propose change without applying it</h3></div><form data-scw-collab-proposal-form><label><span>Actor</span><select name="actorId" data-scw-collab-proposal-actor required><option value="">Choose actor</option></select></label><label><span>Target object</span><select name="objectId" data-scw-collab-proposal-object required><option value="">Choose object</option></select></label><label><span>Proposal kind</span><select name="kind"><option value="replace-field">Replace field</option><option value="append-note">Append note</option><option value="status-request">Status request</option><option value="custom">Custom</option></select></label><label><span>Field <em>optional</em></span><input name="field" maxlength="120" placeholder="e.g. summary"></label><label><span>Proposed value / change</span><textarea name="proposedValue" rows="4" maxlength="8000" required></textarea></label><label><span>Rationale</span><textarea name="rationale" rows="3" maxlength="5000"></textarea></label><button class="scw-button" type="submit">Create proposal</button></form><div data-scw-collab-proposal-list class="scw-collab-record-list"></div></section>
                    </div>
                    <section class="scw-collab-contract-panel"><div class="scw-knowledge-panel-head"><span>05 / SHAREABLE PROJECT CONTRACT</span><h3>Export ownership, scope, and role declarations without project content.</h3></div><div class="scw-collab-contract-actions"><button class="scw-button" type="button" data-scw-collab-contract-preview>Preview contract</button><button class="scw-button" type="button" data-scw-collab-contract-export>Export contract</button><button class="scw-button" type="button" data-scw-collab-architecture-export>Export architecture</button><button class="scw-button" type="button" data-scw-collab-architecture-import>Import architecture</button><input type="file" accept="application/json,.json" data-scw-collab-architecture-file hidden></div><pre data-scw-collab-contract-output>No project policy selected.</pre><p data-scw-collab-arch-status role="status" aria-live="polite"></p></section>
                    <div class="scw-collaboration-boundary" role="note"><strong>Architecture, not enforcement</strong><span>Roles and capability grants describe intended responsibility in this local Workspace. They do not create server accounts, grant organization access, or protect a shared cloud tenant. Proposal acceptance records a review decision only; it never edits canonical project content.</span></div>
                </section>
                <div class="scw-editorial-kicker scw-collab-legacy-kicker">COLLABORATION FOUNDATION · PORTABLE REVIEW COMPATIBILITY</div>
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
                <div class="scw-collaboration-boundary" role="note"><strong>Collaboration foundation, not a shared tenant</strong><span>Legacy portable-review roles continue to describe responsibility inside review packages; they are not server-enforced permissions. Imported comments never edit the source project automatically. Live co-editing, organization membership, shared cloud storage, audit-grade access control, and administrative governance remain outside this personal Workspace release.</span></div>
            </section>

            <section class="scw-institutional" data-scw-workspace-section="institutional" hidden aria-labelledby="scw-institutional-title">
                <section class="scw-institutional-validation" data-scw-institutional-validation aria-labelledby="scw-iv-title">
                    <div class="scw-iv-head"><div><div class="scw-editorial-kicker">INSTITUTIONAL VALIDATION</div><h2 id="scw-iv-title">Validate the package before it leaves the personal Workspace.</h2><p>Check frozen disclosure scope, recipient and purpose, source-revision freshness, promotion integrity, and institutional receipts. Attention states require human review; they are not readiness or quality scores.</p></div><div class="scw-iv-boundary"><strong>Validation does not transfer authority.</strong><span>Passing these checks does not create organization access, accept a package into Catalyst Intelligence, or convert the source Workspace project into an institutional record.</span></div></div>
                    <div class="scw-iv-actions"><button class="scw-button scw-button-primary" type="button" data-scw-iv-run>Validate local packages &amp; handoffs</button><button class="scw-button" type="button" data-scw-iv-inspect>Inspect transfer file</button><input type="file" accept="application/json,.json" data-scw-iv-file hidden><button class="scw-button" type="button" data-scw-iv-export disabled>Export validation report</button></div>
                    <div class="scw-iv-metrics" data-scw-iv-metrics aria-label="Institutional validation summary"></div><div class="scw-iv-list" data-scw-iv-list><div class="scw-irp-empty">Run validation or inspect a package/receipt file.</div></div><div class="scw-iv-status" data-scw-iv-status role="status" aria-live="polite">Institutional validation has not run yet.</div>
                </section>
                <section class="scw-institutional-research-packages" data-scw-institutional-research-packages aria-labelledby="scw-irp-title">
                    <div class="scw-irp-head">
                        <div><div class="scw-editorial-kicker">INSTITUTIONAL RESEARCH PACKAGES</div><h2 id="scw-irp-title">Freeze a deliberate research package for institutional handoff.</h2><p>Select only the research that should travel. Workspace can include recorded provenance, related Citation Library references, Research Tasks, and Collaboration review context. The package becomes a frozen disclosure artifact; creating or exporting it does not alter the source project.</p></div>
                        <div class="scw-irp-boundary"><strong>Explicit disclosure</strong><span>Institutional packages contain selected copies for handoff. They are not public links, live mirrors, permission grants, or automatic Catalyst Intelligence imports.</span></div>
                    </div>
                    <div class="scw-irp-metrics" data-scw-irp-metrics aria-label="Institutional research package metrics"></div>
                    <div class="scw-irp-grid">
                        <section class="scw-irp-panel"><div class="scw-knowledge-panel-head"><span>01 / SCOPE</span><h3>Define exactly what leaves Workspace.</h3></div>
                            <div class="scw-irp-form">
                                <label><span>Source project</span><select data-scw-irp-project><option value="">Choose project</option></select></label>
                                <label><span>Package title</span><input type="text" maxlength="320" data-scw-irp-title placeholder="Institutional research package"></label>
                                <label><span>Receiving institution / program</span><input type="text" maxlength="320" data-scw-irp-institution required placeholder="Institution or program"></label>
                                <label><span>Purpose</span><textarea rows="4" maxlength="4000" data-scw-irp-purpose required placeholder="Why is this package being prepared?"></textarea></label>
                                <div class="scw-irp-scope" data-scw-irp-scope><div class="scw-irp-empty">Choose a project to define scope.</div></div>
                                <fieldset class="scw-irp-options"><legend>Included context</legend>
                                    <label><input type="checkbox" data-scw-irp-full checked> Include full selected research content</label>
                                    <label><input type="checkbox" data-scw-irp-provenance checked> Include recorded provenance</label>
                                    <label><input type="checkbox" data-scw-irp-citations checked> Include related Citation Library references</label>
                                    <label><input type="checkbox" data-scw-irp-tasks checked> Include related Research Tasks</label>
                                    <label><input type="checkbox" data-scw-irp-review checked> Include project/selected-object Collaboration review context</label>
                                </fieldset>
                                <div class="scw-irp-actions"><button class="scw-button scw-button-primary" type="button" data-scw-irp-freeze>Freeze institutional package</button><button class="scw-button" type="button" data-scw-irp-inspect>Inspect package file</button><input type="file" accept="application/json,.json" data-scw-irp-file hidden></div>
                                <div class="scw-irp-status" data-scw-irp-status role="status" aria-live="polite"></div>
                            </div>
                        </section>
                        <section class="scw-irp-panel"><div class="scw-knowledge-panel-head"><span>02 / PACKAGE LEDGER</span><h3>Frozen institutional disclosure artifacts.</h3></div><div class="scw-irp-list" data-scw-irp-list></div></section>
                    </div>
                    <div class="scw-irp-active" data-scw-irp-active><div class="scw-irp-empty">Open a frozen package to inspect its disclosure manifest.</div></div>
                </section>
                <div class="scw-institutional-legacy-label"><strong>Catalyst Intelligence promotion — compatibility path</strong><span>The v0.19 institutional promotion and receipt workflow remains available below. v0.57 packages are broader institutional research bundles and do not replace that explicit product-specific handoff.</span></div>

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
                <div class="scw-institutional-governance" role="note"><strong>Workspace does not become the institution.</strong><span>v0.25.0 preserves the governed handoff contract for Catalyst Intelligence while hardening the surrounding Workspace runtime. It does not create organization membership, server permissions, shared cloud storage, automatic ingestion, or an institutional tenant inside Workspace.</span></div>
            </section>

            <section class="scw-scale-performance" data-scw-workspace-section="performance" data-scw-scale-performance hidden aria-labelledby="scw-scale-performance-title">
                <div class="scw-scale-performance-head">
                    <div><div class="scw-editorial-kicker">SCALE / PERFORMANCE</div><h2 id="scw-scale-performance-title">Know when a project is getting heavy before it becomes fragile.</h2><p>Profile large-project pressure locally, inspect derived-index behavior, and keep rendering bounded. These signals are advisory only: Workspace will not delete, archive, compact, or migrate canonical research automatically.</p></div>
                    <div class="scw-scale-performance-boundary"><strong>Advisory, not destructive</strong><span>Performance hardening changes derived caches and rendering windows, not Project 20.0 or Notebook 8.0 data.</span></div>
                </div>
                <div class="scw-scale-performance-metrics" aria-label="Scale profile summary">
                    <div><strong data-scw-scale-projects>0</strong><span>projects</span></div><div><strong data-scw-scale-objects>0</strong><span>objects</span></div><div><strong data-scw-scale-blocks>0</strong><span>notebook blocks</span></div><div><strong data-scw-scale-index>0</strong><span>index entries</span></div>
                </div>
                <div class="scw-scale-performance-grid">
                    <section><span>STORAGE</span><strong data-scw-scale-bytes>0 KB</strong><p data-scw-scale-quota>Browser quota estimate unavailable</p></section>
                    <section><span>DERIVED INDEX</span><strong data-scw-scale-index-ms>0 ms</strong><p data-scw-scale-cache>0 hit / 0 miss</p></section>
                    <section><span>RENDER WINDOW</span><strong data-scw-scale-window>120</strong><p>Integrated Knowledge renders a bounded initial result window and exposes more only on request.</p></section>
                </div>
                <div class="scw-performance-session" data-scw-performance-session>
                    <div class="scw-knowledge-panel-head"><span>PERFORMANCE II / LONG SESSION</span><h3>Watch runtime pressure without profiling your research.</h3></div>
                    <p>v0.68 keeps a bounded, memory-only set of timing counters for route changes, full Workspace renders, derived-index work, cooperative yields, and supported browser long-task signals. Project content, query text, source URLs, and device identifiers are never included.</p>
                    <div class="scw-performance-session-metrics" aria-label="Long-session performance summary">
                        <div><strong data-scw-perf-session-age>0 min</strong><span>session age</span></div><div><strong data-scw-perf-routes>0</strong><span>route changes</span></div><div><strong data-scw-perf-renders>0</strong><span>full renders</span></div><div><strong data-scw-perf-render-p95>0.0 ms</strong><span>render p95</span></div><div><strong data-scw-perf-index-p95>0.0 ms</strong><span>index p95</span></div><div><strong data-scw-perf-longtasks>0</strong><span>long tasks</span></div><div><strong data-scw-perf-yields>0</strong><span>cooperative yields</span></div><div><strong data-scw-perf-heap>Heap metric unavailable</strong><span>optional heap signal</span></div>
                    </div>
                    <div class="scw-scale-performance-actions"><button class="scw-button scw-button-primary" type="button" data-scw-perf-session-run>Run session profile</button><button class="scw-button" type="button" data-scw-perf-session-reset>Reset session counters</button><button class="scw-button" type="button" data-scw-perf-session-export>Export timing report</button></div>
                    <ul class="scw-scale-performance-attention" data-scw-perf-session-findings><li>No advisory long-session signals</li></ul>
                    <div class="scw-scale-performance-status" data-scw-perf-session-status role="status" aria-live="polite"></div>
                    <div class="scw-scale-performance-boundary"><strong>Bounded and local</strong><span>At most 120 recent samples per metric stay in memory. There is no persistent profiling store, background submission, automatic cleanup of canonical research, or hidden productivity score.</span></div>
                </div>
                <div class="scw-scale-performance-actions"><button class="scw-button scw-button-primary" type="button" data-scw-scale-run>Run scale profile</button><button class="scw-button" type="button" data-scw-scale-clear-cache>Clear derived cache</button></div>
                <ul class="scw-scale-performance-attention" data-scw-scale-attention><li>No advisory scale signals</li></ul>
                <div class="scw-scale-performance-status" data-scw-scale-status role="status" aria-live="polite"></div>
            </section>

            <section class="scw-ga-stabilization" data-scw-workspace-section="ga-stabilization" data-scw-ga-stabilization hidden aria-labelledby="scw-ga-stabilization-title">
                <div class="scw-ga-stabilization-head">
                    <div><div class="scw-editorial-kicker">1.0.1 / FIELD STABILIZATION</div><h2 id="scw-ga-stabilization-title">Close the first post-GA production evidence loop.</h2><p>Record representative field evidence for the live v1.0.1 deployment without collecting behavioral telemetry or inspecting project content. A valid v1.0.0 GA certificate remains the predecessor evidence boundary.</p></div>
                    <div class="scw-ga-stabilization-boundary"><strong>Evidence, not telemetry</strong><span>This record is browser-local unless explicitly exported. Blocking defects keep the record on HOLD.</span><span class="scw-ga-stabilization-badge" data-scw-ga-stabilization-badge>HOLD</span></div>
                </div>
                <div class="scw-ga-stabilization-evidence" data-scw-ga-stabilization-evidence></div>
                <div class="scw-ga-stabilization-meta"><label><span>Field validation operator</span><input type="text" data-scw-ga-stabilization-operator placeholder="Operator"></label><label><span>Production URL</span><input type="url" data-scw-ga-stabilization-url value="https://sustainablecatalyst.com/platform/"></label></div>
                <label class="scw-ga-stabilization-notes"><span>Browser/device notes (optional, no raw user agent required)</span><textarea rows="4" data-scw-ga-stabilization-notes placeholder="Representative browser/device observations"></textarea></label>
                <div class="scw-ga-stabilization-grid" data-scw-ga-stabilization-checks></div>
                <label class="scw-ga-stabilization-attestation"><input type="checkbox" data-scw-ga-stabilization-attest> I attest that the checked field validations were actually performed against the live deployment and that any known blocking defect would keep this record on HOLD.</label>
                <div class="scw-ga-stabilization-actions"><button class="scw-button scw-button-primary" type="button" data-scw-ga-stabilization-complete>Close field stabilization</button><button class="scw-button" type="button" data-scw-ga-stabilization-export>Export stabilization report</button><button class="scw-button" type="button" data-scw-ga-stabilization-reset>Reset local record</button></div>
                <p class="scw-ga-stabilization-status" data-scw-ga-stabilization-status role="status" aria-live="polite">Post-GA field evidence is not yet closed.</p>
            </section>

            <section class="scw-recovery-drills" data-scw-workspace-section="recovery-drills" data-scw-recovery-drills hidden aria-labelledby="scw-recovery-drills-title">
                <div class="scw-recovery-drills-head"><div><div class="scw-kicker">v0.69 / PRODUCT RECOVERY &amp; DISASTER SIMULATION</div><h2 id="scw-recovery-drills-title">Prove the failure path before relying on it.</h2><p>Run isolated in-memory recovery drills for corrupt state, interrupted writes, storage exhaustion, malformed imports, stale restore behavior, sync conflicts, missing references, and future-version mismatches. The simulator does not inject faults into canonical Workspace data.</p></div><span class="scw-recovery-drills-badge" data-scw-recovery-drills-badge>CHECKING</span></div>
                <div class="scw-recovery-drills-actions"><button class="scw-button scw-button-primary" type="button" data-scw-recovery-drills-run>Run recovery drills</button><button class="scw-button" type="button" data-scw-recovery-drills-export>Export drill report</button></div>
                <div class="scw-recovery-drills-grid" data-scw-recovery-drills-grid><div class="scw-beta-empty">Recovery drills have not run yet.</div></div>
                <p class="scw-recovery-drills-status" data-scw-recovery-drills-status role="status" aria-live="polite">Recovery drill suite has not run yet.</p>
                <div class="scw-recovery-drills-boundary" role="note"><strong>Simulation is not destructive testing of your research.</strong><span>Faults run against isolated in-memory fixtures. Workspace does not corrupt live storage, force quota exhaustion, rewrite projects, auto-restore snapshots, auto-commit imports, resolve sync conflicts automatically, or contact a remote service during these drills.</span></div>
            </section>

            <section class="scw-security-privacy" data-scw-workspace-section="security" data-scw-security-privacy hidden aria-labelledby="scw-security-privacy-title">
                <div class="scw-security-privacy-head">
                    <div><div class="scw-editorial-kicker">SECURITY / PRIVACY / PORTABILITY</div><h2 id="scw-security-privacy-title">Know what Workspace stores, what it can disclose, and what deletion actually covers.</h2><p>Audit browser-local Workspace data, review the same-origin threat model, export a complete local portability bundle, and verify browser-local deletion. This surface makes boundaries explicit rather than claiming encryption, authorization, or cloud deletion that Workspace does not provide.</p></div>
                    <div class="scw-security-privacy-boundary"><strong>Private by default, not magically encrypted</strong><span>Browser localStorage is accessible within the browser/same-origin threat model. Integrity fingerprints are receipts—not encryption or authentication. Account/cloud data is a separate lifecycle boundary.</span></div>
                </div>
                <div class="scw-security-privacy-metrics" aria-label="Security and privacy audit summary"><div><strong data-scw-sec-stores>0</strong><span>local stores</span></div><div><strong data-scw-sec-bytes>0 KB</strong><span>local bytes</span></div><div><strong data-scw-sec-disclosure>0</strong><span>disclosure stores</span></div><div><strong data-scw-sec-recovery>0</strong><span>recovery stores</span></div></div>
                <div class="scw-security-privacy-actions"><button class="scw-button scw-button-primary" type="button" data-scw-sec-run>Run security/privacy audit</button><button class="scw-button" type="button" data-scw-sec-export-audit>Export metadata-only audit</button></div>
                <div class="scw-security-privacy-grid">
                    <section class="scw-security-privacy-panel"><div class="scw-knowledge-panel-head"><span>01 / THREAT MODEL</span><h3>Declared boundaries and non-claims</h3></div><div class="scw-sec-threat-model" data-scw-sec-threat-model></div></section>
                    <section class="scw-security-privacy-panel"><div class="scw-knowledge-panel-head"><span>02 / FINDINGS</span><h3>Current local audit findings</h3></div><ul class="scw-sec-findings" data-scw-sec-findings></ul></section>
                    <section class="scw-security-privacy-panel scw-security-privacy-panel-wide"><div class="scw-knowledge-panel-head"><span>03 / DATA INVENTORY</span><h3>Workspace-owned browser-local stores</h3></div><div class="scw-sec-inventory" data-scw-sec-inventory></div></section>
                    <section class="scw-security-privacy-panel"><div class="scw-knowledge-panel-head"><span>04 / PORTABILITY</span><h3>Complete browser-local export</h3></div><p>The full portability bundle includes every current <code>sc_workspace*</code> browser-local key, including unclassified future keys. It may contain private research, recovery snapshots, identifiers, drafts, and disclosure artifacts.</p><div class="scw-security-privacy-actions"><button class="scw-button scw-button-primary" type="button" data-scw-sec-export-full>Export complete local bundle</button><button class="scw-button" type="button" data-scw-sec-verify>Verify bundle</button><input type="file" accept="application/json,.json" data-scw-sec-verify-file hidden></div></section>
                    <section class="scw-security-privacy-panel scw-security-danger"><div class="scw-knowledge-panel-head"><span>05 / VERIFIED LOCAL DELETION</span><h3>Delete Workspace browser-local data</h3></div><p>This deletes Workspace-owned browser-local keys only. It does not delete account/cloud backups, WordPress records, previously exported files, or data already shared with another person/system.</p><button class="scw-button" type="button" data-scw-sec-preview-delete>Preview deletion scope</button><p class="scw-sec-delete-summary" data-scw-sec-delete-summary>Preview the deletion scope before enabling local deletion.</p><label class="scw-sec-delete-ack"><input type="checkbox" data-scw-sec-delete-ack> I understand account/cloud backups and previously exported/shared copies are outside this deletion.</label><label><span>Type <strong>DELETE WORKSPACE DATA</strong></span><input type="text" autocomplete="off" data-scw-sec-delete-phrase></label><button class="scw-button scw-button-danger" type="button" data-scw-sec-delete disabled>Delete browser-local Workspace data</button></section>
                </div>
                <div class="scw-security-audit-ii" data-scw-security-audit-ii aria-labelledby="scw-security-audit-ii-title">
                    <div class="scw-security-audit-ii-head"><div><div class="scw-editorial-kicker">AUDIT II / RELEASE SECURITY</div><h3 id="scw-security-audit-ii-title">Re-audit the browser boundary without exporting the research.</h3><p>Audit II inspects storage metadata, secure-context and embed state, script-readable cookie counts, and the release-time source gates that protect REST permissions and the current JavaScript runtime. Storage values, project content, URLs, queries, identities, referrer text, and cookie names/values stay out of the report.</p></div><div class="scw-security-audit-ii-boundary"><strong>Audit, not certification</strong><span>This is a bounded product security control. It is not a penetration test, cryptographic review, or claim that browser-local data is application-level encrypted.</span></div></div>
                    <div class="scw-security-audit-ii-metrics"><div><strong data-scw-sec2-local>0</strong><span>local stores</span></div><div><strong data-scw-sec2-session>0</strong><span>session stores</span></div><div><strong data-scw-sec2-bytes>0 KB</strong><span>Workspace bytes</span></div><div><strong data-scw-sec2-unknown>0</strong><span>unclassified stores</span></div></div>
                    <div class="scw-security-audit-ii-actions"><button class="scw-button scw-button-primary" type="button" data-scw-sec2-run>Run Audit II</button><button class="scw-button" type="button" data-scw-sec2-export>Export privacy-minimized report</button></div>
                    <div class="scw-security-audit-ii-grid"><section><div class="scw-knowledge-panel-head"><span>06 / BROWSER BOUNDARY</span><h3>Runtime exposure metadata</h3></div><div class="scw-security-audit-ii-browser" data-scw-sec2-browser></div></section><section><div class="scw-knowledge-panel-head"><span>07 / RELEASE GATES</span><h3>Source controls enforced at packaging</h3></div><div class="scw-security-audit-ii-gates" data-scw-sec2-gates></div></section><section class="scw-security-audit-ii-wide"><div class="scw-knowledge-panel-head"><span>08 / AUDIT II FINDINGS</span><h3>Conditions that need review</h3></div><ul class="scw-security-audit-ii-findings" data-scw-sec2-findings></ul></section></div>
                    <p class="scw-security-audit-ii-status" data-scw-sec2-status role="status" aria-live="polite">Audit II has not run yet.</p>
                </div>
                <div class="scw-security-privacy-status" data-scw-sec-status role="status" aria-live="polite"></div>
            </section>

            <section class="scw-public-beta-ii" data-scw-workspace-section="beta" data-scw-public-beta-ii hidden aria-labelledby="scw-public-beta-ii-title">
                <div class="scw-beta-ii-head"><div><div class="scw-kicker">PUBLIC PRODUCT BETA II / READINESS</div><h2 id="scw-public-beta-ii-title">Test the complete Workspace, not just individual features.</h2><p>Run a local product gate across persistence, integrity, recovery, focused-route isolation, performance diagnostics, security/privacy controls, and release identity. The gate produces explicit checks, never a hidden readiness score.</p></div><span class="scw-beta-ii-badge" data-scw-beta-ii-badge>CHECKING</span></div>
                <div class="scw-beta-ii-actions"><button class="scw-button scw-button-primary" type="button" data-scw-beta-ii-run>Run beta gate</button><button class="scw-button" type="button" data-scw-beta-ii-diagnostics>Open field diagnostics</button><button class="scw-button" type="button" data-scw-beta-ii-security>Open Security &amp; Privacy</button><button class="scw-button" type="button" data-scw-beta-ii-export>Export beta field snapshot</button></div>
                <div class="scw-beta-ii-checks" data-scw-beta-ii-checks><div class="scw-beta-empty">Running local beta checks…</div></div>
                <p class="scw-beta-ii-status" data-scw-beta-ii-status role="status" aria-live="polite">Beta gate has not run yet.</p>
                <div class="scw-beta-boundary" role="note"><strong>Beta II boundary</strong><span>Checks run locally and are advisory. Workspace does not send behavioral telemetry, submit diagnostics automatically, repair data automatically, mutate research, or convert checklist results into a productivity/readiness score.</span></div>
            </section>

            <section class="scw-field-resilience" data-scw-workspace-section="reliability" data-scw-field-resilience hidden aria-labelledby="scw-field-resilience-title">
                <div class="scw-resilience-head"><div><div class="scw-kicker">PRODUCT HARDENING I / RELIABILITY</div><h2 id="scw-field-resilience-title">Recover the interface before it becomes a recovery problem.</h2><p>Inspect browser capability, saved UI position, route isolation, and local recovery state. Workspace remembers only safe navigation state here; project and research data stay in their existing canonical stores.</p></div><span class="scw-resilience-badge" data-scw-resilience-badge>CHECKING</span></div>
                <div class="scw-resilience-actions"><button class="scw-button scw-button-primary" type="button" data-scw-resilience-run>Run reliability check</button><button class="scw-button" type="button" data-scw-resilience-reset>Reset navigation state</button><button class="scw-button" type="button" data-scw-resilience-export>Export resilience snapshot</button></div>
                <div class="scw-resilience-findings" data-scw-resilience-findings><div class="scw-beta-empty">Running local reliability checks…</div></div>
                <p class="scw-resilience-status" data-scw-resilience-status role="status" aria-live="polite">Reliability check has not run yet.</p>
                <div class="scw-resilience-boundary" role="note"><strong>Navigation recovery is not data recovery.</strong><span>Reset navigation state removes only Workspace UI-position keys. It does not delete projects, notebooks, citations, tasks, recovery snapshots, or other canonical research. Invalid or expired UI routes fall back to Start instead of trapping the application.</span></div>
            </section>

            <section class="scw-persistence-integrity" data-scw-workspace-section="integrity" data-scw-persistence-integrity hidden aria-labelledby="scw-persistence-integrity-title">
                <div class="scw-pi-head"><div><div class="scw-kicker">PRODUCT HARDENING II / PERSISTENCE INTEGRITY</div><h2 id="scw-persistence-integrity-title">Detect a bad save before recovery becomes guesswork.</h2><p>Audit the canonical browser-local state, verified-save receipt, last-known-good snapshot, and write transaction journal. v0.62 adds integrity receipts and interrupted-write detection without changing Storage 35 or Project 20.0.</p></div><span class="scw-pi-badge" data-scw-pi-badge>CHECKING</span></div>
                <div class="scw-pi-metrics" data-scw-pi-metrics aria-label="Persistence integrity summary"></div>
                <div class="scw-pi-actions"><button class="scw-button scw-button-primary" type="button" data-scw-pi-run>Run integrity audit</button><button class="scw-button" type="button" data-scw-pi-export-diagnostic>Export integrity report</button><button class="scw-button" type="button" data-scw-pi-export-current>Export current recovery candidate</button><button class="scw-button" type="button" data-scw-pi-export-good>Export last-known-good</button><button class="scw-button" type="button" data-scw-pi-open-history>Open History / Recovery</button></div>
                <div class="scw-pi-findings" data-scw-pi-findings><div class="scw-beta-empty">Running persistence integrity checks…</div></div>
                <p class="scw-pi-status" data-scw-pi-status role="status" aria-live="polite">Persistence integrity audit has not run yet.</p>
                <div class="scw-pi-boundary" role="note"><strong>Integrity is not encryption or automatic repair.</strong><span>The checksum receipt detects persistence integrity drift and unexpected byte changes; it is not a security signature. Recovery candidate exports contain private Workspace content and remain manual-review artifacts. Workspace never overwrites canonical research merely because an integrity check reports attention.</span></div>
            </section>

            <section class="scw-browser-compatibility" data-scw-workspace-section="compatibility" data-scw-browser-compatibility hidden aria-labelledby="scw-browser-compatibility-title">
                <div class="scw-compat-head"><div><div class="scw-kicker">v0.63 / CROSS-BROWSER &amp; DEVICE COMPATIBILITY</div><h2 id="scw-browser-compatibility-title">Adapt to the browser without guessing from the browser name.</h2><p>Inspect the runtime paths Workspace can actually use for persistence, navigation, file import/export, viewport sizing, touch input, and WordPress embedding. Feature detection controls fallbacks; browser-family labels are diagnostic only.</p></div><span class="scw-compat-badge" data-scw-compat-badge>CHECKING</span></div>
                <div class="scw-compat-summary" data-scw-compat-summary aria-label="Browser compatibility summary"></div>
                <div class="scw-compat-actions"><button class="scw-button scw-button-primary" type="button" data-scw-compat-run>Run compatibility audit</button><button class="scw-button" type="button" data-scw-compat-export>Export compatibility report</button><button class="scw-button" type="button" data-scw-compat-export-matrix>Export target matrix</button></div>
                <div class="scw-compat-findings" data-scw-compat-findings><div class="scw-beta-empty">Running local browser capability checks…</div></div>
                <p class="scw-compat-status" data-scw-compat-status role="status" aria-live="polite">Compatibility audit has not run yet.</p>
                <div class="scw-compat-boundary" role="note"><strong>Capability probes are not certification.</strong><span>v0.63 provides guarded fallbacks and automated capability fixtures, but it does not claim every physical browser/device combination has been manually certified. The exported target matrix is the field-QA checklist. Reports omit raw user-agent strings, device identifiers, project content, source URLs, query strings, and page fragments.</span></div>
            </section>

            <section class="scw-accessibility" data-scw-workspace-section="accessibility" data-scw-accessibility hidden aria-labelledby="scw-accessibility-title">
                <div class="scw-a11y-head"><div><div class="scw-kicker">v0.64 / ACCESSIBILITY &amp; KEYBOARD-FIRST PRODUCT AUDIT</div><h2 id="scw-accessibility-title">Make every Workspace path operable without relying on a pointer.</h2><p>Audit programmatic labels, section structure, status announcements, dialog behavior, keyboard navigation, motion preferences, and host-page zoom constraints. Automated checks identify structural/runtime issues; screen-reader, contrast, zoom, reflow, and complete task-flow verification remain explicit manual QA.</p></div><span class="scw-a11y-badge" data-scw-a11y-badge>CHECKING</span></div>
                <div class="scw-a11y-summary" data-scw-a11y-summary aria-label="Accessibility audit summary"></div>
                <div class="scw-a11y-actions"><button class="scw-button scw-button-primary" type="button" data-scw-a11y-run>Run accessibility audit</button><button class="scw-button" type="button" data-scw-a11y-export-report>Export accessibility report</button><button class="scw-button" type="button" data-scw-a11y-export-checklist>Export manual WCAG checklist</button></div>
                <div class="scw-a11y-findings" data-scw-a11y-findings><div class="scw-beta-empty">Running local accessibility checks…</div></div>
                <p class="scw-a11y-status" data-scw-a11y-status role="status" aria-live="polite">Accessibility audit has not run yet.</p>
                <div class="scw-a11y-boundary" role="note"><strong>Audit support is not certification.</strong><span>Workspace targets WCAG 2.2 AA, but DOM/runtime checks cannot establish conformance on their own. v0.64 exports the remaining manual keyboard, screen-reader, contrast, forced-colors, zoom, reflow, reduced-motion, touch-target, and error-state checks. Reports contain no project content, source content, raw user agent, or device identifier and are never uploaded automatically.</span></div>
            </section>



            <section class="scw-final-audit" data-scw-workspace-section="final-audit" data-scw-final-audit hidden aria-labelledby="scw-final-audit-title">
                <div class="scw-final-audit-head">
                    <div><div class="scw-editorial-kicker">FINAL AUDIT / ACCESSIBILITY + PERFORMANCE</div><h2 id="scw-final-audit-title">Block critical regressions. Keep the remaining human verification visible.</h2><p>Combine the existing keyboard/accessibility audit with bounded long-session performance evidence before Workspace enters the final beta-defect closure phase. Structural accessibility failures and critical performance regressions can block this automated gate; screen-reader, measured contrast, zoom/reflow, physical touch-device, and representative multi-hour validation remain human field work.</p></div>
                    <div class="scw-final-audit-boundary"><strong>Automated gate, not certification</strong><span>Passing this surface does not establish WCAG conformance or performance certification. It proves only that the automated release checks are below their blocking thresholds and that the remaining manual work is explicitly recorded.</span><span class="scw-final-audit-badge" data-scw-final-audit-badge>CHECKING</span></div>
                </div>
                <div class="scw-final-audit-summary" data-scw-final-audit-summary aria-label="Final accessibility and performance audit summary"></div>
                <div class="scw-final-audit-actions"><button class="scw-button scw-button-primary" type="button" data-scw-final-audit-run>Run final audit</button><button class="scw-button" type="button" data-scw-final-audit-export>Export privacy-minimized report</button><button class="scw-button" type="button" data-scw-final-audit-checklist>Export final field-QA checklist</button></div>
                <div class="scw-final-audit-grid">
                    <section><div class="scw-knowledge-panel-head"><span>01 / ACCESSIBILITY GATE</span><h3>Structural and runtime findings</h3></div><ul class="scw-final-audit-findings" data-scw-final-audit-a11y></ul></section>
                    <section><div class="scw-knowledge-panel-head"><span>02 / PERFORMANCE GATE</span><h3>Session and interface budgets</h3></div><ul class="scw-final-audit-findings" data-scw-final-audit-performance></ul></section>
                    <section class="scw-final-audit-wide"><div class="scw-knowledge-panel-head"><span>03 / HUMAN FIELD VALIDATION</span><h3>Checks automation cannot certify</h3></div><ul class="scw-final-audit-manual" data-scw-final-audit-manual></ul></section>
                </div>
                <p class="scw-final-audit-status" data-scw-final-audit-status role="status" aria-live="polite">Final audit has not run yet.</p>
            </section>

            <section class="scw-beta-closure" data-scw-workspace-section="beta-closure" data-scw-beta-closure hidden aria-labelledby="scw-beta-closure-title">
                <div class="scw-beta-closure-head">
                    <div><div class="scw-editorial-kicker">AUTOMATED DEFECT CLOSURE / PUBLIC BETA III</div><h2 id="scw-beta-closure-title">Close the automated backlog. Keep field validation visible.</h2><p>Verify that the product journey, recovery simulations, security/privacy source gates, accessibility/performance final audit, WordPress metadata boundary, and current release identity remain coherent before Workspace enters the Release Candidate phase.</p></div>
                    <div class="scw-beta-closure-boundary"><strong>Closure is not field certification</strong><span>Automated blockers can be closed here. Production WordPress, assistive technology, physical touch/zoom/contrast, representative multi-hour use, two-device continuity, and real external handoffs remain explicit human field-validation work.</span><span class="scw-beta-closure-badge" data-scw-beta-closure-badge>CHECKING</span></div>
                </div>
                <div class="scw-beta-closure-actions"><button class="scw-button scw-button-primary" type="button" data-scw-beta-closure-run>Run closure gate</button><button class="scw-button" type="button" data-scw-beta-closure-export>Export closure report</button></div>
                <div class="scw-beta-closure-grid">
                    <section><div class="scw-knowledge-panel-head"><span>01 / AUTOMATED GATE</span><h3>Release blockers</h3></div><ul class="scw-beta-closure-list" data-scw-beta-closure-checks></ul></section>
                    <section><div class="scw-knowledge-panel-head"><span>02 / CLOSED DEFECT CLASSES</span><h3>Protections that must not regress</h3></div><ul class="scw-beta-closure-list" data-scw-beta-closure-closed></ul></section>
                    <section class="scw-beta-closure-wide"><div class="scw-knowledge-panel-head"><span>03 / HUMAN FIELD VALIDATION</span><h3>Explicitly unresolved until performed</h3></div><ul class="scw-beta-closure-list" data-scw-beta-closure-manual></ul></section>
                </div>
                <p class="scw-beta-closure-status" data-scw-beta-closure-status role="status" aria-live="polite">Closure gate has not run yet.</p>
            </section>

            <section class="scw-release-candidate" data-scw-workspace-section="release-candidate" data-scw-release-candidate hidden aria-labelledby="scw-release-candidate-title">
                <div class="scw-release-candidate-head">
                    <div><div class="scw-editorial-kicker">RELEASE CANDIDATE I / FEATURE FREEZE</div><h2 id="scw-release-candidate-title">Freeze the product. Certify the release.</h2><p>Verify that the Public Beta III closure baseline, recovery drills, security/privacy boundary, accessibility/performance gate, canonical schemas, and current release identity remain intact while the product enters the pre-1.0 certification phase.</p></div>
                    <div class="scw-release-candidate-boundary"><strong>Release Candidate is not production certification</strong><span>Feature scope is frozen. Production WordPress, rollback rehearsal, assistive technology, touch/zoom/contrast, multi-hour use, two-device continuity, and real handoffs remain explicit human validation.</span><span class="scw-release-candidate-badge" data-scw-rc-badge>CHECKING</span></div>
                </div>
                <div class="scw-release-candidate-actions"><button class="scw-button scw-button-primary" type="button" data-scw-rc-run>Run RC gate</button><button class="scw-button" type="button" data-scw-rc-export>Export RC report</button><button class="scw-button" type="button" data-scw-rc-checklist>Export field checklist</button></div>
                <div class="scw-release-candidate-grid">
                    <section><div class="scw-knowledge-panel-head"><span>01 / AUTOMATED GATE</span><h3>Release Candidate blockers</h3></div><ul class="scw-release-candidate-list" data-scw-rc-checks></ul></section>
                    <section><div class="scw-knowledge-panel-head"><span>02 / FEATURE FREEZE</span><h3>Frozen product boundaries</h3></div><ul class="scw-release-candidate-list" data-scw-rc-freeze></ul></section>
                    <section class="scw-release-candidate-wide"><div class="scw-knowledge-panel-head"><span>03 / HUMAN FIELD CERTIFICATION</span><h3>Required before production sign-off</h3></div><ul class="scw-release-candidate-list" data-scw-rc-manual></ul></section>
                </div>
                <p class="scw-release-candidate-status" data-scw-rc-status role="status" aria-live="polite">Release Candidate gate has not run yet.</p>
            </section>

            <section class="scw-production-certification" data-scw-workspace-section="production-certification" data-scw-production-certification hidden aria-labelledby="scw-production-certification-title">
                <div class="scw-production-certification-head">
                    <div><div class="scw-editorial-kicker">RELEASE CANDIDATE / PRODUCTION CERTIFICATION</div><h2 id="scw-production-certification-title">Prove the package. Keep the live deployment honest.</h2><p>Separate what the release archive can certify from what only the live WordPress deployment can prove: public-page health, REST identity, cache coherence, local-project preservation, and rollback behavior.</p></div>
                    <div class="scw-production-certification-boundary"><strong>Package ready is not production certified</strong><span>Live field checks remain pending until you perform them on the deployed site. Workspace project storage is never a cache-remediation target.</span><span class="scw-production-certification-badge" data-scw-production-badge>CHECKING</span></div>
                </div>
                <div class="scw-production-certification-actions"><button class="scw-button scw-button-primary" type="button" data-scw-production-run>Run package certification</button><button class="scw-button" type="button" data-scw-production-export>Export certification report</button><button class="scw-button" type="button" data-scw-production-checklist>Export live field checklist</button></div>
                <div class="scw-production-certification-grid">
                    <section><div class="scw-knowledge-panel-head"><span>01 / PACKAGE GATE</span><h3>Automated release evidence</h3></div><ul class="scw-production-certification-list" data-scw-production-checks></ul></section>
                    <section><div class="scw-knowledge-panel-head"><span>02 / LIVE PRODUCTION</span><h3>Explicit field certification</h3></div><ul class="scw-production-certification-list" data-scw-production-manual></ul></section>
                </div>
                <p class="scw-production-certification-status" data-scw-production-status role="status" aria-live="polite">Production certification has not run yet.</p>
            </section>

            <section class="scw-production-signoff" data-scw-workspace-section="production-signoff" data-scw-production-signoff hidden aria-labelledby="scw-production-signoff-title">
                <div class="scw-production-signoff-head">
                    <div><div class="scw-editorial-kicker">LIVE PRODUCTION / RELEASE SIGN-OFF</div><h2 id="scw-production-signoff-title">Record the evidence. Sign off only what was actually tested.</h2><p>Close the remaining pre-1.0 field-validation boundary with explicit human evidence. Every item stays pending until you attest that it was performed against the live deployment.</p></div>
                    <div class="scw-production-signoff-boundary"><strong>No automatic certification</strong><span>Workspace does not inspect project contents, infer pass/fail, purge caches, perform rollback, or sign on your behalf.</span><span class="scw-production-signoff-badge" data-scw-signoff-badge>PENDING</span></div>
                </div>
                <div class="scw-production-signoff-meta"><label><span>Reviewer / operator label</span><input type="text" data-scw-signoff-reviewer placeholder="Production reviewer"></label><label><span>Production URL</span><input type="url" data-scw-signoff-url value="https://sustainablecatalyst.com/platform/"></label></div>
                <div class="scw-production-signoff-grid" data-scw-signoff-checks></div>
                <label class="scw-production-signoff-attestation"><input type="checkbox" data-scw-signoff-attest> I attest that every checked item was performed against the live deployment and that this record does not substitute for evidence I did not collect.</label>
                <div class="scw-production-signoff-actions"><button class="scw-button scw-button-primary" type="button" data-scw-signoff-complete>Complete production sign-off</button><button class="scw-button" type="button" data-scw-signoff-export>Export sign-off certificate</button><button class="scw-button" type="button" data-scw-signoff-reset>Reset local sign-off</button></div>
                <p class="scw-production-signoff-status" data-scw-signoff-status role="status" aria-live="polite">No live production evidence has been signed off.</p>
            </section>

            <section class="scw-ga-readiness" data-scw-workspace-section="ga-readiness" data-scw-ga-readiness hidden aria-labelledby="scw-ga-readiness-title">
                <div class="scw-ga-readiness-head">
                    <div><div class="scw-editorial-kicker">PRE-1.0 / RELEASE READINESS</div><h2 id="scw-ga-readiness-title">Close the evidence loop before calling Workspace ready for 1.0.</h2><p>Use the signed v0.83.0 production certificate as prior evidence, verify the v0.84.0 release boundary, and make an explicit human readiness decision. This surface never promotes the plugin to 1.0 automatically.</p></div>
                    <div class="scw-ga-readiness-boundary"><strong>Readiness is not release</strong><span>A READY dossier means the pre-1.0 evidence gate is complete. Publishing v1.0.0 remains a separate release action.</span><span class="scw-ga-readiness-badge" data-scw-ga-badge>HOLD</span></div>
                </div>
                <div class="scw-ga-readiness-evidence" data-scw-ga-signoff-evidence></div>
                <div class="scw-ga-readiness-meta"><label><span>Release decision owner</span><input type="text" data-scw-ga-owner placeholder="Release owner"></label><label><span>Target production URL</span><input type="url" data-scw-ga-url value="https://sustainablecatalyst.com/platform/"></label></div>
                <div class="scw-ga-readiness-grid" data-scw-ga-checks></div>
                <label class="scw-ga-readiness-attestation"><input type="checkbox" data-scw-ga-attest> I attest that the required v0.83.0 production sign-off evidence is valid, the v0.84.0 readiness checks were completed, and any known blocking defect would keep this dossier on HOLD.</label>
                <div class="scw-ga-readiness-actions"><button class="scw-button scw-button-primary" type="button" data-scw-ga-complete>Record 1.0 readiness decision</button><button class="scw-button" type="button" data-scw-ga-export>Export readiness dossier</button><button class="scw-button" type="button" data-scw-ga-reset>Reset readiness record</button></div>
                <p class="scw-ga-readiness-status" data-scw-ga-status role="status" aria-live="polite">1.0 readiness has not been attested.</p>
            </section>

            <section class="scw-general-availability" data-scw-workspace-section="general-availability" data-scw-general-availability hidden aria-labelledby="scw-general-availability-title">
                <div class="scw-ga-readiness-head">
                    <div><div class="scw-editorial-kicker">1.0 / GENERAL AVAILABILITY</div><h2 id="scw-general-availability-title">Record the General Availability release boundary.</h2><p>Use the valid v0.84.0 readiness dossier as predecessor evidence, verify the deployed v1.0.0 package and rollback path, and issue an explicit human GA release certificate.</p></div>
                    <div class="scw-ga-readiness-boundary"><strong>GA is an explicit release record</strong><span>Workspace never infers readiness, publishes a release, purges caches, rolls back, or changes project data automatically.</span><span class="scw-ga-readiness-badge" data-scw-ga-release-badge>HOLD</span></div>
                </div>
                <div class="scw-ga-readiness-evidence" data-scw-ga-readiness-evidence></div>
                <div class="scw-ga-readiness-meta"><label><span>GA release operator</span><input type="text" data-scw-ga-release-operator placeholder="Release operator"></label><label><span>Production URL</span><input type="url" data-scw-ga-release-url value="https://sustainablecatalyst.com/platform/"></label></div>
                <div class="scw-ga-readiness-grid" data-scw-ga-release-checks></div>
                <label class="scw-ga-readiness-attestation"><input type="checkbox" data-scw-ga-release-attest> I attest that the v0.84.0 readiness dossier is valid, every v1.0.0 GA check is complete, and any blocking defect would keep this release record on HOLD.</label>
                <div class="scw-ga-readiness-actions"><button class="scw-button scw-button-primary" type="button" data-scw-ga-release-complete>Record General Availability</button><button class="scw-button" type="button" data-scw-ga-release-export>Export GA certificate</button><button class="scw-button" type="button" data-scw-ga-release-reset>Reset GA record</button></div>
                <p class="scw-ga-readiness-status" data-scw-ga-release-status role="status" aria-live="polite">General Availability has not been attested.</p>
            </section>

            <section class="scw-wordpress-deployment" data-scw-workspace-section="deployment" data-scw-wordpress-deployment-hardening hidden aria-labelledby="scw-wordpress-deployment-title">
                <div class="scw-wordpress-deployment-head">
                    <div><div class="scw-editorial-kicker">RELEASE CANDIDATE / WORDPRESS DEPLOYMENT</div><h2 id="scw-wordpress-deployment-title">Verify the deployed release before blaming the workspace.</h2><p>Check server package completeness, WordPress/runtime version coherence, current cumulative assets, registry retry state, and the rollback boundary without reading or changing browser-local project data.</p></div>
                    <div class="scw-wordpress-deployment-boundary"><strong>Project storage is not a cache</strong><span>A mixed-version deployment is repaired through release files and cache invalidation—not by clearing Workspace projects.</span><span class="scw-wordpress-deployment-badge" data-scw-deploy-badge>CHECKING</span></div>
                </div>
                <div class="scw-wordpress-deployment-actions"><button class="scw-button scw-button-primary" type="button" data-scw-deploy-run>Run deployment check</button><button class="scw-button" type="button" data-scw-deploy-export>Export deployment report</button><button class="scw-button" type="button" data-scw-deploy-checklist>Export production checklist</button></div>
                <div class="scw-wordpress-deployment-assets" data-scw-deploy-assets></div>
                <div class="scw-wordpress-deployment-grid">
                    <section><div class="scw-knowledge-panel-head"><span>01 / AUTOMATED COHERENCE</span><h3>Current package and assets</h3></div><ul class="scw-wordpress-deployment-list" data-scw-deploy-checks></ul></section>
                    <section><div class="scw-knowledge-panel-head"><span>02 / PRODUCTION FIELD CHECKS</span><h3>Still requires a human</h3></div><ul class="scw-wordpress-deployment-list" data-scw-deploy-manual></ul></section>
                </div>
                <p class="scw-wordpress-deployment-status" data-scw-deploy-status role="status" aria-live="polite">Deployment check has not run yet.</p>
            </section>

            <section class="scw-research-automation" data-scw-workspace-section="automation" data-scw-research-automation hidden aria-labelledby="scw-research-automation-title">
                <div class="scw-auto-head">
                    <div><div class="scw-editorial-kicker">RESEARCH AUTOMATION FRAMEWORK</div><h2 id="scw-research-automation-title">Schedule the reminder. Execute the research action yourself.</h2><p>Create local routines for import review, source review, verification, synthesis refresh, and workflow follow-up. Cadence is declarative: Workspace never runs these jobs in the background or silently changes canonical research.</p></div>
                    <div class="scw-auto-boundary"><strong>Manual execution only</strong><span>A routine becomes due locally, but nothing runs until you choose Run now or Run due routines. Every result is a draft receipt for human review.</span></div>
                </div>
                <div class="scw-auto-metrics" data-scw-auto-metrics></div>
                <div class="scw-auto-grid">
                    <section class="scw-auto-panel"><div class="scw-knowledge-panel-head"><span>01 / DEFINE</span><h3>Create a reusable research routine</h3></div>
                        <label><span>Routine name</span><input type="text" data-scw-auto-name placeholder="Weekly source verification"></label>
                        <div class="scw-auto-fields"><label><span>Routine type</span><select data-scw-auto-type><option value="source-review">Source review</option><option value="verification-check">Verification check</option><option value="recurring-import">Recurring import review</option><option value="synthesis-refresh">Synthesis refresh</option><option value="workflow-action">Workflow action</option></select></label><label><span>Cadence</span><select data-scw-auto-cadence><option value="on-demand">On demand</option><option value="daily">Daily</option><option value="weekly">Weekly</option><option value="monthly">Monthly</option></select></label></div>
                        <label><span>Canonical target (optional)</span><select data-scw-auto-target><option value="">No canonical target</option></select></label>
                        <label><span>Instructions</span><textarea rows="4" data-scw-auto-instructions placeholder="What should be checked or prepared when this routine is run?"></textarea></label>
                        <label class="scw-auto-check"><input type="checkbox" data-scw-auto-enabled checked> Enabled for due-date calculation</label>
                        <button class="scw-button scw-button-primary" type="button" data-scw-auto-create>Save routine</button>
                    </section>
                    <section class="scw-auto-panel"><div class="scw-knowledge-panel-head"><span>02 / RUN</span><h3>Execute explicitly</h3></div>
                        <div class="scw-auto-toolbar"><button class="scw-button scw-button-primary" type="button" data-scw-auto-run-due>Run due routines</button><button class="scw-button" type="button" data-scw-auto-export>Export automation library</button><button class="scw-button" type="button" data-scw-auto-import>Import automation library</button><input type="file" accept="application/json,.json" data-scw-auto-file hidden></div>
                        <div class="scw-auto-routines" data-scw-auto-routines></div>
                    </section>
                </div>
                <section class="scw-auto-results"><div class="scw-knowledge-panel-head"><span>03 / REVIEW</span><h3>Automation run receipts</h3></div><div data-scw-auto-runs></div></section>
                <p class="scw-auto-status" data-scw-auto-status role="status" aria-live="polite">No automation has executed. Due schedules are local reminders only.</p>
                <div class="scw-auto-governance" role="note"><strong>Automation prepares work; it does not decide or mutate.</strong><span>No routine performs background network requests, automatic imports, automatic AI calls, automatic task creation, source verification, synthesis replacement, or canonical data mutation. Imported routines never execute automatically.</span></div>
            </section>

            <section class="scw-api-embed" data-scw-workspace-section="api-embed" data-scw-api-embed data-renderer-url="<?php echo esc_url(sc_workspace_api_embed_script_url()); ?>" data-trusted-origin="<?php echo esc_url(home_url('/')); ?>" hidden aria-labelledby="scw-api-embed-title">
                <div class="scw-api-embed-head">
                    <div><div class="scw-editorial-kicker">API, EMBED &amp; INTEGRATION HARDENING</div><h2 id="scw-api-embed-title">Expose a deliberate read-only projection through a bounded integration boundary.</h2><p>Canonical research remains private and browser-local by default. Create an explicit static projection when a particular record should travel through an API envelope or embed. Durable references identify records but never grant access.</p></div>
                    <div class="scw-api-boundary"><strong>Private by default</strong><span>No live server project API exists. Export and embed paths fail closed when integrity, payload size, or trusted-renderer checks do not pass.</span></div>
                </div>
                <div class="scw-api-grid">
                    <section class="scw-api-panel"><div class="scw-knowledge-panel-head"><span>01 / SELECT &amp; DISCLOSE</span><h3>Create a read-only projection</h3></div>
                        <label><span>Canonical research record</span><select data-scw-api-record><option value="">Choose canonical research</option></select></label>
                        <div class="scw-api-fields"><label><input type="checkbox" data-scw-api-summary checked> Summary</label><label><input type="checkbox" data-scw-api-tags> Tags</label><label><input type="checkbox" data-scw-api-provenance> Recorded provenance</label><label><input type="checkbox" data-scw-api-content> Full content <strong>explicit disclosure</strong></label></div>
                        <button class="scw-button scw-button-primary" type="button" data-scw-api-create>Create public-readonly projection</button>
                        <p class="scw-api-note">Creating a projection does not upload it. It creates a browser-local disclosure package that can then be explicitly exported or embedded.</p>
                        <div class="scw-api-list" data-scw-api-list></div>
                    </section>
                    <section class="scw-api-panel"><div class="scw-knowledge-panel-head"><span>02 / REFERENCE &amp; API</span><h3>Stable reference and static JSON envelope</h3></div>
                        <div class="scw-api-reference"><span>DURABLE REFERENCE</span><code data-scw-api-reference>No projection selected.</code></div>
                        <div class="scw-api-actions"><button class="scw-button" type="button" data-scw-api-copy-ref disabled>Copy durable reference</button><button class="scw-button" type="button" data-scw-api-export-json disabled>Export read-only API JSON</button><button class="scw-button" type="button" data-scw-api-delete disabled>Delete projection</button><button class="scw-button" type="button" data-scw-api-verify disabled>Verify integration safety</button><button class="scw-button" type="button" data-scw-api-export-safety disabled>Export safety report</button></div>
                        <pre data-scw-api-json>No API envelope selected.</pre>
                    </section>
                </div>
                <section class="scw-api-embed-panel"><div class="scw-knowledge-panel-head"><span>03 / STATIC EMBED</span><h3>Preview and copy a self-contained read-only embed.</h3></div>
                    <div class="scw-api-embed-layout"><div data-scw-api-preview><div class="scw-api-empty">Create or select a projection to preview its read-only embed.</div></div><div><label><span>Embed HTML</span><textarea rows="12" readonly data-scw-api-html></textarea></label><button class="scw-button" type="button" data-scw-api-copy-embed disabled>Copy embed HTML</button></div></div>
                    <p class="scw-api-status" data-scw-api-status role="status" aria-live="polite">No projection has been disclosed.</p>
                </section>
                <section class="scw-api-safety" aria-labelledby="scw-api-safety-title"><div class="scw-knowledge-panel-head"><span>04 / INTEGRATION SAFETY</span><h3 id="scw-api-safety-title">Verify the boundary before the projection travels.</h3></div><div data-scw-api-safety><div class="scw-api-empty">Select a projection to run integration safety checks.</div></div><p class="scw-api-note">Checks are local and diagnostic. They verify the projection fingerprint, bounded payload size, static read-only governance, and configured HTTPS renderer origin. They do not authenticate the recipient or turn a fingerprint into a signature.</p></section>
                <div class="scw-api-governance" role="note"><strong>Identifiers are not credentials.</strong><span>A <code>scw://</code> durable reference is safe to use as a stable identifier only. It does not prove identity, confer permission, expose private local records, or act as an access token. Static fingerprints detect package changes; they are not signatures or authorization. Static embeds perform no credentialed fetch, postMessage bridge, or remote canonical mutation.</span></div>
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
                    <section class="scw-research-template-library" aria-labelledby="scw-research-template-library-title">
                        <div class="scw-research-template-head"><div><span>REUSABLE RESEARCH TEMPLATES</span><h4 id="scw-research-template-library-title">Scaffold a method without copying the research.</h4><p>Use built-in protocols or explicitly saved custom structures to add a guided workflow, a Notebook section scaffold, and optional empty starter objects. Templates never contain project notes, Notebook contents, evidence, findings, citations, or completion states.</p></div></div>
                        <div class="scw-research-template-controls">
                            <label><span>Template</span><select data-scw-research-template-select></select></label>
                            <label><span>Project starter title</span><input type="text" maxlength="120" data-scw-research-template-project-title placeholder="Template project title"></label>
                            <label class="scw-template-check"><input type="checkbox" data-scw-research-template-workflow checked><span>Guided workflow</span></label>
                            <label class="scw-template-check"><input type="checkbox" data-scw-research-template-notebook checked><span>Notebook scaffold</span></label>
                            <label class="scw-template-check"><input type="checkbox" data-scw-research-template-objects><span>Empty starter objects</span></label>
                        </div>
                        <div class="scw-research-template-preview" data-scw-research-template-preview></div>
                        <div class="scw-research-template-actions"><button type="button" class="scw-button scw-button-primary" data-scw-research-template-apply>Apply structure to this project</button><button type="button" class="scw-button" data-scw-research-template-create-project>Create project starter</button><button type="button" class="scw-button" data-scw-research-template-save-workflow>Save active workflow as template</button><button type="button" class="scw-button" data-scw-research-template-export>Export custom templates</button><button type="button" class="scw-button" data-scw-research-template-import>Import custom templates</button><input type="file" accept="application/json,.json" data-scw-research-template-import-file hidden></div>
                        <p class="scw-research-template-status" data-scw-research-template-status role="status" aria-live="polite"></p>
                        <div class="scw-research-template-custom-list" data-scw-research-template-custom-list></div>
                    </section>
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

                    <aside class="scw-project-research-guidance" data-scw-project-research-guidance aria-label="Contextual research guidance"><div><span data-scw-project-guidance-stage>FRAME / CONTEXTUAL NEXT STEP</span><strong data-scw-project-guidance-title>Frame the question before collecting material.</strong><p data-scw-project-guidance-detail>Guidance follows visible project state and never marks research complete for you.</p></div><button class="scw-button" type="button" data-scw-project-guidance-action>Open Research Questions</button></aside>

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
                                <div class="scw-canvas-form-row"><label><span>From</span><select name="fromNodeId" data-scw-canvas-edge-from><option value="">Choose node</option></select></label><label><span>Relationship</span><select name="relation"><option value="supports">Supports</option><option value="references">References</option><option value="contrasts">Contrasts</option><option value="extends">Extends</option><option value="related">Related</option><option value="promoted-to">Promoted to</option><option value="synthesized-into">Synthesized into</option><option value="cited-as">Cited as</option><option value="supports-claim">Supports claim</option><option value="captured-from">Captured from</option><option value="contradicts">Contradicts</option><option value="depends-on">Depends on</option><option value="influences">Influences</option><option value="contains">Contains</option><option value="causes">Causes</option><option value="relates-to">Relates to</option><option value="sequence">Sequence</option></select></label></div>
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
                                <label><span>Relationship</span><select name="relation"><option value="derived-from">Derived from</option><option value="supports">Supports</option><option value="references">References</option><option value="contrasts">Contrasts</option><option value="extends">Extends</option><option value="related">Related</option><option value="promoted-to">Promoted to</option><option value="synthesized-into">Synthesized into</option><option value="cited-as">Cited as</option><option value="supports-claim">Supports claim</option><option value="captured-from">Captured from</option><option value="contradicts">Contradicts</option><option value="uses">Uses</option><option value="produced-by">Produced by</option><option value="informs">Informs</option><option value="supersedes">Supersedes</option><option value="cites">Cites</option><option value="originates-in-library">Originates in Library</option></select></label>
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
                                <button class="scw-op" type="button" data-scw-object-to-notebook>Add to Notebook</button>
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

                <section class="scw-lab-integration" data-scw-lab-integration aria-labelledby="scw-lab-integration-title">
                    <div class="scw-lab-integration-head">
                        <div><div class="scw-kicker">SCIENTIFIC WORKSPACE / LAB ROUND TRIP</div><h3 id="scw-lab-integration-title">Carry selected scientific context into Lab and return traceable results.</h3><p>Select the exact Workspace objects Lab should receive. Exporting a scientific context package is explicit; opening Lab carries only stable IDs in the URL. Returned results must match the originating project and handoff before Workspace materializes them.</p></div>
                    </div>
                    <div class="scw-lab-integration-grid">
                        <label><span>Lab workflow</span><select data-scw-lab-workflow><option value="model-studio">Model Studio</option><option value="graph-studio">Graph Studio</option><option value="experiment">Experiment</option><option value="bayesian-inference">Bayesian inference</option><option value="posterior-diagnostics">Posterior diagnostics</option><option value="posterior-predictive-modeling">Posterior predictive modeling</option><option value="data-transformation">Data transformation</option><option value="scientific-visualization">Scientific visualization</option></select></label>
                        <label><span>Scientific context objects</span><select multiple size="7" data-scw-lab-object-scope aria-describedby="scw-lab-scope-note"></select></label>
                        <label><span>Methodology / assumptions</span><textarea rows="4" maxlength="6000" data-scw-lab-methodology placeholder="Optional methodology, assumptions, or model context to carry with the selected objects."></textarea></label>
                        <label><span>Units / uncertainty</span><textarea rows="4" maxlength="6000" data-scw-lab-uncertainty placeholder="Optional units, uncertainty, parameter, or measurement notes."></textarea></label>
                    </div>
                    <p id="scw-lab-scope-note" class="scw-section-note">Only explicitly selected source, evidence, dataset, analysis, document, and export objects are copied into the portable context package. Nothing is uploaded automatically.</p>
                    <div class="scw-lab-integration-actions"><button class="scw-button scw-button-primary" type="button" data-scw-lab-open>Open Lab with IDs</button><button class="scw-button" type="button" data-scw-lab-export-context>Export scientific context</button><button class="scw-button" type="button" data-scw-lab-export-return-template>Export return template</button><button class="scw-button" type="button" data-scw-lab-import-return>Import Lab return</button><input type="file" accept="application/json,.json" data-scw-lab-import-return-file hidden></div>
                    <div class="scw-handoff-boundary" role="note"><strong>Execution stays in Lab</strong><span>Workspace preserves project identity, selected object IDs, provenance, scientific metadata, and deterministic derived-from traceability. It does not run models, infer scientific relationships, or commit unmatched returns.</span></div>
                    <p data-scw-lab-status role="status" aria-live="polite"></p>
                </section>

                <section class="scw-specialist-roundtrip" data-scw-specialist-roundtrip aria-labelledby="scw-specialist-roundtrip-title">
                    <div class="scw-specialist-roundtrip-head">
                        <div><div class="scw-kicker">WORKBENCH / DECISION STUDIO ROUND TRIP</div><h3 id="scw-specialist-roundtrip-title">Move bounded project context into specialized tools and bring governed outputs back.</h3><p>Choose Workbench for calculation, simulation, optimization, engineering analysis, transformation, or sensitivity work. Choose Decision Studio for decision packets, scenarios, tradeoffs, option assessment, risk review, or decision briefs. Workspace preserves the project and provenance boundary; the specialist tool performs the work.</p></div>
                    </div>
                    <div class="scw-specialist-roundtrip-grid">
                        <label><span>Destination</span><select data-scw-specialist-destination><option value="workbench">Workbench</option><option value="decision-studio">Decision Studio</option></select></label>
                        <label><span>Workflow</span><select data-scw-specialist-workflow></select></label>
                        <label><span>Context objects</span><select multiple size="7" data-scw-specialist-object-scope aria-describedby="scw-specialist-scope-note"></select></label>
                        <label><span>Purpose / method</span><textarea rows="4" maxlength="6000" data-scw-specialist-purpose placeholder="Describe the calculation, simulation, comparison, decision question, or method to carry with the selected context."></textarea></label>
                        <label><span>Parameters / constraints</span><textarea rows="4" maxlength="6000" data-scw-specialist-constraints placeholder="Optional parameters, constraints, assumptions, units, uncertainty, or decision criteria."></textarea></label>
                        <label><span>Scenario / risk notes</span><textarea rows="4" maxlength="6000" data-scw-specialist-scenario placeholder="Optional scenario framing, risks, tradeoffs, or outcome notes."></textarea></label>
                    </div>
                    <p id="scw-specialist-scope-note" class="scw-section-note">Only explicitly selected compatible Workspace objects are copied into the portable context package. Opening the specialist tool carries stable IDs only; no project content is uploaded automatically.</p>
                    <div class="scw-specialist-roundtrip-actions"><button class="scw-button scw-button-primary" type="button" data-scw-specialist-open>Open tool with IDs</button><button class="scw-button" type="button" data-scw-specialist-export-context>Export context package</button><button class="scw-button" type="button" data-scw-specialist-export-return-template>Export return template</button><button class="scw-button" type="button" data-scw-specialist-import-return>Import returned work</button><input type="file" accept="application/json,.json" data-scw-specialist-import-return-file hidden></div>
                    <div class="scw-handoff-boundary" role="note"><strong>Specialized execution stays specialized</strong><span>Workspace records the handoff, selected context IDs, destination, workflow, provenance, and deterministic derived-from traceability. It does not run Workbench calculations or Decision Studio analysis itself, and it rejects returns that do not match the originating project, handoff, and destination.</span></div>
                    <p data-scw-specialist-status role="status" aria-live="polite"></p>
                </section>

                <section class="scw-handoffs" aria-labelledby="scw-handoffs-title">
                <div class="scw-handoff-head">
                    <div>
                        <div class="scw-kicker">CROSS-PRODUCT HANDOFFS</div>
                        <h3 id="scw-handoffs-title">Connections & returns</h3>
                        <p>Review return activity or import a structured return package when you need it. The underlying handoff IDs and privacy checks remain intact.</p>
                    </div>
                    <div class="scw-handoff-actions">
                        <a class="scw-button scw-lab-handoff" href="<?php echo esc_url(home_url('/lab/')); ?>">Open the Lab</a>
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
                <div><strong>Workspace v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></strong> · Free public access · Public beta</div>
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
                    <article><b>05</b><div><strong>Connected tools and reusable artifacts</strong><p>Move stable project context into Sustainable Catalyst tools and return structured artifacts to the originating project.</p><a class="scw-pathway-link" href="<?php echo esc_url(home_url('/lab/')); ?>">Explore the Lab <span aria-hidden="true">→</span></a></div><span>Portable project context</span></article>
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
