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
        if (
            get_option(SC_Workspace_Registry::PENDING_KEY, '') === '1' ||
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
        echo '<div class="notice notice-warning"><p><strong>Sustainable Catalyst Workspace:</strong> the canonical Product Registry was not available during activation. Workspace is active, but its v0.4.1 Commercial Release record is pending until Product Support and Feedback is active.</p></div>';
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
    }

    public function health() {
        return rest_ensure_response(array(
            'ok' => true,
            'product' => 'Sustainable Catalyst Workspace',
            'canonical_id' => 'sustainable-catalyst-workspace',
            'version' => SC_WORKSPACE_VERSION,
            'access' => 'free-public',
            'account_required' => false,
            'persistence' => 'browser-local-projects-v5',
            'project_schema' => 'sc-workspace-project/3.1',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'identity_schema' => 'sc-workspace-identity/1.0',
            'authentication_provider' => 'wordpress',
            'anonymous_workspace_supported' => true,
            'storage_schema_version' => 5,
            'server_project_storage' => false,
            'cloud_sync' => false,
            'collaboration' => false,
            'registry_family' => 'commercial',
            'lifecycle' => 'experimental',
        ));
    }

    public function project_contract() {
        return rest_ensure_response(array(
            'schema' => 'sc-workspace-project-contract/3.1',
            'workspace_version' => SC_WORKSPACE_VERSION,
            'project_schema' => 'sc-workspace-project/3.1',
            'object_schema' => 'sc-workspace-object/1.0',
            'research_schema' => 'sc-workspace-research/1.0',
            'export_schema' => 'sc-workspace-project-export/3.1',
            'storage_schema_version' => 5,
            'persistence' => 'device-local',
            'server_storage' => false,
            'project_persistence_metadata' => true,
            'device_identity' => 'anonymous-pseudonymous-local-id',
            'account_sign_in_changes_storage' => false,
            'max_objects_per_project' => 250,
            'handoff_schema' => 'sc-workspace-handoff/1.2',
            'handoff_query_fields' => array('sc_workspace_project', 'sc_workspace_object', 'sc_workspace_origin', 'sc_workspace_return'),
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
            'project_persistence_scope' => 'device',
            'server_project_storage' => false,
            'cloud_sync' => false,
            'account_session_uploads_project_content' => false,
            'manual_portability' => 'project-json-export-import',
            'future_sync_boundary_prepared' => true,
        ));
    }

    private function enqueue_assets() {
        wp_enqueue_style(
            'sc-workspace-v041',
            SC_WORKSPACE_URL . 'assets/css/workspace-v0.4.1.css',
            array(),
            SC_WORKSPACE_VERSION
        );
        wp_enqueue_script(
            'sc-workspace-v041',
            SC_WORKSPACE_URL . 'assets/js/workspace-v0.4.1.js',
            array(),
            SC_WORKSPACE_VERSION,
            true
        );

        $return_url = home_url('/platform/workspace/');
        $authenticated = is_user_logged_in();
        $user = $authenticated ? wp_get_current_user() : null;
        wp_localize_script('sc-workspace-v041', 'SCWorkspaceIdentity', array(
            'authenticated' => $authenticated,
            'displayName' => $authenticated && $user ? $user->display_name : '',
            'loginUrl' => wp_login_url($return_url),
            'logoutUrl' => wp_logout_url($return_url),
            'registrationEnabled' => (bool) get_option('users_can_register'),
            'registrationUrl' => get_option('users_can_register') ? wp_registration_url() : '',
            'storageMode' => 'device-local',
            'cloudSync' => false,
            'serverProjectStorage' => false,
        ));
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
        $return_url = home_url('/platform/workspace/');
        ob_start();
        ?>
        <section class="scw-shell" data-sc-workspace data-version="<?php echo esc_attr(SC_WORKSPACE_VERSION); ?>" data-storage-version="5" data-return-url="<?php echo esc_url($return_url); ?>">
            <div class="scw-hero">
                <div class="scw-kicker">SUSTAINABLE CATALYST / PLATFORM</div>
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
                <span>Workspace remains fully usable without signing in. v0.4.1 can recognize an optional Sustainable Catalyst site account, but projects and project content still remain on this device. Signing in does not upload, claim, or synchronize local work.</span>
            </div>

            <section class="scw-identity" aria-labelledby="scw-identity-title">
                <div class="scw-identity-main">
                    <div>
                        <div class="scw-kicker">IDENTITY &amp; PERSISTENCE</div>
                        <h2 id="scw-identity-title">Use Workspace immediately. Add identity when it helps.</h2>
                    </div>
                    <div class="scw-identity-session">
                        <span class="scw-identity-badge" data-scw-identity-badge>GUEST</span>
                        <strong data-scw-identity-heading>Guest Workspace</strong>
                        <span data-scw-identity-detail>Your work is associated only with this browser device.</span>
                    </div>
                </div>
                <div class="scw-identity-grid">
                    <div><span>ACCESS</span><strong data-scw-identity-access>No account required</strong><small>Anonymous use remains a first-class path.</small></div>
                    <div><span>PERSISTENCE</span><strong>Saved on this device</strong><small>Cloud synchronization is not enabled in v0.4.1.</small></div>
                    <div><span>DEVICE ID</span><strong data-scw-device-id>Initializing…</strong><small>Pseudonymous local identifier; no personal data is encoded.</small></div>
                    <div class="scw-identity-actions">
                        <a class="scw-button scw-button-primary" data-scw-login href="#">Sign in</a>
                        <a class="scw-button" data-scw-register href="#" hidden>Create free account</a>
                        <a class="scw-button" data-scw-logout href="#" hidden>Sign out</a>
                    </div>
                </div>
                <p class="scw-identity-note" data-scw-identity-note>Sign-in establishes the identity boundary only. Project sync and server-side project storage remain disabled.</p>
            </section>

            <div class="scw-recovery" data-scw-recovery hidden role="status" aria-live="polite">
                <div><strong>Workspace recovery mode</strong><span data-scw-recovery-message>A damaged local state was isolated and a clean workspace was opened.</span></div>
                <button type="button" class="scw-button" data-scw-dismiss-recovery>Dismiss</button>
            </div>

            <section class="scw-projects" aria-labelledby="scw-projects-title">
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
                    <div class="scw-storage-state"><span class="scw-storage-dot" aria-hidden="true"></span><span data-scw-storage-state>Local project storage ready</span></div>
                </div>

                <div class="scw-empty" data-scw-empty>
                    <strong>No Workspace Projects yet.</strong>
                    <span>Create one to keep notes, objects, activity, and cross-product context together on this device.</span>
                </div>
                <div class="scw-project-list" data-scw-project-list aria-live="polite"></div>
            </section>

            <section class="scw-active-project" data-scw-active-project hidden aria-labelledby="scw-active-title">
                <div class="scw-active-header">
                    <div>
                        <div class="scw-kicker">ACTIVE PROJECT</div>
                        <h2 id="scw-active-title" data-scw-active-heading>Project</h2>
                    </div>
                    <div class="scw-save-state" data-scw-save-state>Saved on this device</div>
                </div>

                <div class="scw-project-editor">
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



                <section class="scw-research" aria-labelledby="scw-research-title">
                    <div class="scw-research-head">
                        <div>
                            <div class="scw-kicker">RESEARCH WORKSPACE</div>
                            <h3 id="scw-research-title">From question to evidence-backed claim.</h3>
                            <p>Frame inquiry, capture sources, manage a reading queue, extract evidence, and test claims while retaining stable links to Workspace Objects.</p>
                        </div>
                        <div class="scw-research-launchers" aria-label="Research tools">
                            <a class="scw-button" data-scw-tool="research-librarian" href="<?php echo esc_url(home_url('/research-librarian/')); ?>"><strong>Research Librarian</strong></a>
                            <a class="scw-button" data-scw-tool="knowledge-library" href="<?php echo esc_url(home_url('/library/')); ?>"><strong>Knowledge Library</strong></a>
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

                <section class="scw-objects" aria-labelledby="scw-objects-title">
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

            <section class="scw-tools" aria-labelledby="scw-tools-title">
                <div class="scw-section-head">
                    <div>
                        <div class="scw-kicker">CONNECTED TOOLS</div>
                        <h2 id="scw-tools-title">Carry the active project and object into the platform.</h2>
                        <p class="scw-section-note">Workspace sends only stable project/object IDs through the handoff contract. Titles, notes, content, tags, and provenance remain out of the URL.</p>
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
            </section>

            <footer class="scw-footer">
                <div><strong>Workspace v<?php echo esc_html(SC_WORKSPACE_VERSION); ?></strong> · Commercial Release · Free public access</div>
                <div>Guest and signed-in sessions use device-local project storage in v0.4.1. Sign-in does not upload project content.</div>
            </footer>
        </section>
        <?php
        return ob_get_clean();
    }

    public function render_entry($atts = array()) {
        $this->enqueue_assets();
        $url = home_url('/platform/workspace/');
        return '<a class="scw-entry" href="' . esc_url($url) . '"><span><small>FREE PUBLIC WORKSPACE</small><strong>Workspace</strong><em>Create local-first projects, reusable research objects, and optional account-aware sessions without a login wall.</em></span><b aria-hidden="true">→</b></a>';
    }
}
