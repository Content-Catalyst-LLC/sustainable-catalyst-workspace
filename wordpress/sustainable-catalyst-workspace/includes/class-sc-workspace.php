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
    }

    public function retry_registry_registration() {
        if (get_option(SC_Workspace_Registry::PENDING_KEY, '') === '1') {
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
        echo '<div class="notice notice-warning"><p><strong>Sustainable Catalyst Workspace:</strong> the canonical Product Registry was not available during activation. Workspace is active, but its Commercial Release record is pending until Product Support and Feedback is active.</p></div>';
    }

    public function register_rest_routes() {
        register_rest_route('sc-workspace/v1', '/health', array(
            'methods' => 'GET',
            'callback' => array($this, 'health'),
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
            'persistence' => 'browser-local-session-foundation',
            'server_project_storage' => false,
            'registry_family' => 'commercial',
            'lifecycle' => 'experimental',
        ));
    }

    private function enqueue_assets() {
        wp_enqueue_style(
            'sc-workspace-v010',
            SC_WORKSPACE_URL . 'assets/css/workspace-v0.1.0.css',
            array(),
            SC_WORKSPACE_VERSION
        );
        wp_enqueue_script(
            'sc-workspace-v010',
            SC_WORKSPACE_URL . 'assets/js/workspace-v0.1.0.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );
    }

    private function tools() {
        return array(
            array('key' => 'research-librarian', 'eyebrow' => 'DISCOVER', 'name' => 'Research Librarian', 'description' => 'Frame questions, route inquiry, and move into evidence-backed research.', 'url' => home_url('/research-librarian/')),
            array('key' => 'knowledge-library', 'eyebrow' => 'LEARN', 'name' => 'Knowledge Library', 'description' => 'Explore structured articles, fields, pathways, and open knowledge resources.', 'url' => home_url('/library/')),
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
        ob_start();
        ?>
        <section class="scw-shell" data-sc-workspace data-version="<?php echo esc_attr(SC_WORKSPACE_VERSION); ?>">
            <div class="scw-hero">
                <div class="scw-kicker">SUSTAINABLE CATALYST / PLATFORM</div>
                <div class="scw-hero-grid">
                    <div>
                        <h1>Workspace</h1>
                        <p class="scw-deck">A free working environment for moving from questions to research, analysis, structured judgment, and reusable outputs across Sustainable Catalyst.</p>
                    </div>
                    <div class="scw-state" aria-label="Workspace release state">
                        <span>FREE ACCESS</span>
                        <span>v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></span>
                        <span>EXPERIMENTAL</span>
                    </div>
                </div>
            </div>

            <div class="scw-boundary" role="note">
                <strong>Persistence boundary</strong>
                <span>v0.1.0 stores only lightweight session state in this browser. It does not create a cloud account, server project, or shared workspace.</span>
            </div>

            <div class="scw-session" aria-labelledby="scw-session-title">
                <div class="scw-session-copy">
                    <div class="scw-kicker">CURRENT WORK</div>
                    <h2 id="scw-session-title">Start where the problem is.</h2>
                    <p>Open a lightweight session, then move directly into the tool that fits the work. Workspace will remember the current session and recently opened tools on this device.</p>
                </div>
                <div class="scw-session-panel">
                    <div class="scw-session-meta">
                        <span class="scw-session-label">SESSION</span>
                        <strong data-scw-session-name>No active session</strong>
                        <span data-scw-session-time>Browser-local state is ready.</span>
                    </div>
                    <div class="scw-actions">
                        <button class="scw-button scw-button-primary" type="button" data-scw-start>Start workspace</button>
                        <button class="scw-button" type="button" data-scw-clear hidden>Clear session</button>
                    </div>
                </div>
            </div>

            <div class="scw-section-head">
                <div>
                    <div class="scw-kicker">CONNECTED TOOLS</div>
                    <h2>Move across the platform without losing your place.</h2>
                </div>
                <a class="scw-text-link" href="<?php echo esc_url(home_url('/platform/')); ?>">Platform overview <span aria-hidden="true">→</span></a>
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

            <div class="scw-recent" data-scw-recent-wrap hidden>
                <div class="scw-kicker">RECENT IN THIS BROWSER</div>
                <div class="scw-recent-list" data-scw-recent aria-live="polite"></div>
            </div>

            <footer class="scw-footer">
                <div><strong>Workspace v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></strong> · Commercial Release · Free public access</div>
                <div>AI is a tool within Sustainable Catalyst, not an autonomous decision-maker.</div>
            </footer>
        </section>
        <?php
        return ob_get_clean();
    }

    public function render_entry($atts = array()) {
        $this->enqueue_assets();
        $url = home_url('/platform/workspace/');
        return '<a class="scw-entry" href="' . esc_url($url) . '"><span><small>FREE PUBLIC WORKSPACE</small><strong>Workspace</strong><em>Move from research to analysis and structured decisions across Sustainable Catalyst.</em></span><b aria-hidden="true">→</b></a>';
    }
}
