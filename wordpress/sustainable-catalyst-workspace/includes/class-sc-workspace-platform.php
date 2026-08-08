<?php
if (!defined('ABSPATH')) {
    exit;
}

final class SC_Workspace_Platform {
    const STATE_KEY = 'sc_workspace_platform_conversion_v061';
    const BACKUP_PREFIX = 'sc_workspace_platform_backup_v061_';
    const ADMIN_SLUG = 'sc-workspace-platform';

    private static $instance = null;

    public static function instance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    private function __construct() {
        add_action('admin_menu', array($this, 'register_admin_page'));
        add_action('admin_notices', array($this, 'admin_notice'));
        add_action('admin_post_sc_workspace_convert_platform', array($this, 'handle_convert'));
        add_action('admin_post_sc_workspace_restore_platform', array($this, 'handle_restore'));
        add_action('template_redirect', array($this, 'maybe_redirect_legacy_workspace_route'));
    }

    public static function state() {
        $state = get_option(self::STATE_KEY, array());
        return is_array($state) ? $state : array();
    }

    public static function is_converted() {
        $state = self::state();
        return !empty($state['converted']) && !empty($state['page_id']);
    }

    public static function canonical_url() {
        return self::is_converted() ? home_url('/platform/') : home_url('/platform/workspace/');
    }

    public static function contract_status() {
        $state = self::state();
        return array(
            'converted' => self::is_converted(),
            'page_id' => isset($state['page_id']) ? (int) $state['page_id'] : 0,
            'converted_at' => isset($state['converted_at']) ? (string) $state['converted_at'] : '',
            'canonical_url' => self::canonical_url(),
            'legacy_url' => home_url('/platform/workspace/'),
            'rollback_available' => !empty($state['backup_key']) && get_option($state['backup_key'], null) !== null,
        );
    }

    public function register_admin_page() {
        add_management_page(
            'Workspace Page Conversion',
            'Workspace Page',
            'manage_options',
            self::ADMIN_SLUG,
            array($this, 'render_admin_page')
        );
    }

    public function admin_notice() {
        if (!current_user_can('manage_options') || self::is_converted()) {
            return;
        }
        $screen = function_exists('get_current_screen') ? get_current_screen() : null;
        if ($screen && isset($screen->id) && $screen->id === 'tools_page_' . self::ADMIN_SLUG) {
            return;
        }
        $url = admin_url('tools.php?page=' . self::ADMIN_SLUG);
        echo '<div class="notice notice-info"><p><strong>Sustainable Catalyst Workspace v0.7.0:</strong> the dedicated Workspace page is ready. The Platform page is not changed automatically. <a href="' . esc_url($url) . '">Review the reversible Platform conversion</a>.</p></div>';
    }

    public function render_admin_page() {
        if (!current_user_can('manage_options')) {
            return;
        }
        $page = get_page_by_path('platform', OBJECT, 'page');
        $state = self::state();
        $converted = self::is_converted();
        $result = isset($_GET['scw_result']) ? sanitize_key(wp_unslash($_GET['scw_result'])) : '';
        ?>
        <div class="wrap">
            <h1>Workspace Page Conversion</h1>
            <p>v0.7.0 can convert the existing <code>/platform/</code> page into the dedicated Sustainable Catalyst Workspace experience while preserving the page ID, slug, parent, publication state, and page template.</p>
            <?php if ($result === 'converted') : ?><div class="notice notice-success inline"><p>Platform was converted to the dedicated Workspace page. A rollback snapshot was preserved.</p></div><?php endif; ?>
            <?php if ($result === 'restored') : ?><div class="notice notice-success inline"><p>The original Platform page title and content were restored.</p></div><?php endif; ?>
            <?php if ($result === 'missing') : ?><div class="notice notice-error inline"><p>No root page with slug <code>platform</code> was found. Nothing was changed.</p></div><?php endif; ?>
            <?php if ($result === 'failed') : ?><div class="notice notice-error inline"><p>The requested page change failed. Nothing further was changed.</p></div><?php endif; ?>
            <table class="widefat striped" style="max-width:900px;margin:20px 0">
                <tbody>
                    <tr><th style="width:220px">Conversion state</th><td><?php echo $converted ? '<strong>Converted</strong>' : 'Not converted'; ?></td></tr>
                    <tr><th>Target route</th><td><code>/platform/</code></td></tr>
                    <tr><th>Current page</th><td><?php echo $page ? esc_html($page->post_title . ' · ID ' . $page->ID) : '<em>Not found</em>'; ?></td></tr>
                    <tr><th>New page content</th><td><code>[sc_workspace_platform]</code></td></tr>
                    <tr><th>Automatic activation change</th><td>No</td></tr>
                    <tr><th>Page ID / slug / template</th><td>Preserved</td></tr>
                    <tr><th>Rollback</th><td><?php echo (!empty($state['backup_key']) && get_option($state['backup_key'], null) !== null) ? 'Available' : 'No snapshot yet'; ?></td></tr>
                    <tr><th>Legacy Workspace route</th><td><?php echo $converted ? '<code>/platform/workspace/</code> redirects to <code>/platform/</code>' : 'Unchanged until conversion'; ?></td></tr>
                </tbody>
            </table>
            <?php if (!$converted) : ?>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>">
                    <input type="hidden" name="action" value="sc_workspace_convert_platform">
                    <?php wp_nonce_field('sc_workspace_convert_platform_v061'); ?>
                    <?php submit_button('Convert Platform to Workspace', 'primary', 'submit', false); ?>
                </form>
            <?php else : ?>
                <p><a class="button button-primary" href="<?php echo esc_url(home_url('/platform/')); ?>" target="_blank" rel="noopener">Open Workspace page</a></p>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="margin-top:24px">
                    <input type="hidden" name="action" value="sc_workspace_restore_platform">
                    <?php wp_nonce_field('sc_workspace_restore_platform_v061'); ?>
                    <?php submit_button('Restore original Platform page', 'secondary', 'submit', false); ?>
                </form>
            <?php endif; ?>
            <p style="max-width:900px;margin-top:24px"><strong>Navigation note:</strong> this conversion deliberately does not rewrite custom WordPress menu labels. If your menu item has a manually entered label of “Platform,” change that label to “Workspace” after verifying the converted page.</p>
        </div>
        <?php
    }

    public static function perform_conversion($page) {
        if (!$page || empty($page->ID)) {
            return new WP_Error('sc_workspace_platform_missing', 'Platform page not found.');
        }
        if (self::is_converted()) {
            return self::state();
        }

        $timestamp = gmdate('Ymd_His');
        $backup_key = self::BACKUP_PREFIX . (int) $page->ID . '_' . $timestamp;
        $snapshot = array(
            'page_id' => (int) $page->ID,
            'title' => (string) $page->post_title,
            'content' => (string) $page->post_content,
            'excerpt' => isset($page->post_excerpt) ? (string) $page->post_excerpt : '',
            'slug' => isset($page->post_name) ? (string) $page->post_name : 'platform',
            'parent' => isset($page->post_parent) ? (int) $page->post_parent : 0,
            'status' => isset($page->post_status) ? (string) $page->post_status : '',
            'template' => get_page_template_slug((int) $page->ID),
            'captured_at' => gmdate('c'),
            'workspace_version' => SC_WORKSPACE_VERSION,
        );
        if (!add_option($backup_key, $snapshot, '', 'no')) {
            return new WP_Error('sc_workspace_platform_backup_failed', 'Could not preserve the Platform page snapshot.');
        }

        $result = wp_update_post(array(
            'ID' => (int) $page->ID,
            'post_title' => 'Workspace',
            'post_content' => '[sc_workspace_platform]',
        ), true);
        if (is_wp_error($result)) {
            delete_option($backup_key);
            return $result;
        }

        $state = array(
            'converted' => true,
            'page_id' => (int) $page->ID,
            'backup_key' => $backup_key,
            'converted_at' => gmdate('c'),
            'workspace_version' => SC_WORKSPACE_VERSION,
            'canonical_path' => '/platform/',
            'legacy_path' => '/platform/workspace/',
        );
        update_option(self::STATE_KEY, $state, false);
        flush_rewrite_rules(false);
        return $state;
    }

    public static function perform_restore() {
        $state = self::state();
        if (empty($state['page_id']) || empty($state['backup_key'])) {
            return new WP_Error('sc_workspace_platform_restore_missing', 'No Workspace page conversion snapshot is available.');
        }
        $snapshot = get_option($state['backup_key'], null);
        if (!is_array($snapshot)) {
            return new WP_Error('sc_workspace_platform_snapshot_missing', 'The Platform page snapshot is unavailable.');
        }
        $result = wp_update_post(array(
            'ID' => (int) $snapshot['page_id'],
            'post_title' => (string) $snapshot['title'],
            'post_content' => (string) $snapshot['content'],
            'post_excerpt' => isset($snapshot['excerpt']) ? (string) $snapshot['excerpt'] : '',
        ), true);
        if (is_wp_error($result)) {
            return $result;
        }
        update_option(self::STATE_KEY, array(
            'converted' => false,
            'page_id' => (int) $snapshot['page_id'],
            'backup_key' => $state['backup_key'],
            'restored_at' => gmdate('c'),
            'workspace_version' => SC_WORKSPACE_VERSION,
        ), false);
        flush_rewrite_rules(false);
        return true;
    }

    public function handle_convert() {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        check_admin_referer('sc_workspace_convert_platform_v061');
        $page = get_page_by_path('platform', OBJECT, 'page');
        if (!$page) {
            $this->redirect_result('missing');
        }
        $result = self::perform_conversion($page);
        $this->redirect_result(is_wp_error($result) ? 'failed' : 'converted');
    }

    public function handle_restore() {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        check_admin_referer('sc_workspace_restore_platform_v061');
        $result = self::perform_restore();
        $this->redirect_result(is_wp_error($result) ? 'failed' : 'restored');
    }

    private function redirect_result($result) {
        $url = add_query_arg(array('page' => self::ADMIN_SLUG, 'scw_result' => $result), admin_url('tools.php'));
        wp_safe_redirect($url);
        exit;
    }

    public function maybe_redirect_legacy_workspace_route() {
        if (!self::is_converted() || is_admin()) {
            return;
        }
        $request_uri = isset($_SERVER['REQUEST_URI']) ? wp_unslash($_SERVER['REQUEST_URI']) : '';
        $request_path = wp_parse_url($request_uri, PHP_URL_PATH);
        $legacy_path = wp_parse_url(home_url('/platform/workspace/'), PHP_URL_PATH);
        if ($request_path && $legacy_path && untrailingslashit($request_path) === untrailingslashit($legacy_path)) {
            wp_safe_redirect(home_url('/platform/'), 301);
            exit;
        }
    }
}
