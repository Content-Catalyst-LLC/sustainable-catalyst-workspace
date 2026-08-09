<?php
if (!defined('ABSPATH')) {
    exit;
}

final class SC_Workspace_Platform {
    const STATE_KEY = 'sc_workspace_platform_conversion_v061';
    const BACKUP_PREFIX = 'sc_workspace_platform_backup_v061_';
    const ADMIN_SLUG = 'sc-workspace-platform';
    const NAV_BACKUP_KEY = 'sc_workspace_navigation_backup_v082';

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
        add_action('admin_post_sc_workspace_relabel_navigation', array($this, 'handle_relabel_navigation'));
        add_action('admin_post_sc_workspace_restore_navigation', array($this, 'handle_restore_navigation'));
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
            'navigation_label' => 'Workspace',
            'navigation_label_backup_available' => get_option(self::NAV_BACKUP_KEY, null) !== null,
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
        echo '<div class="notice notice-info"><p><strong>Sustainable Catalyst Workspace v0.13.0:</strong> the dedicated Workspace page is ready. The Platform page is not changed automatically. <a href="' . esc_url($url) . '">Review the reversible Platform conversion</a>.</p></div>';
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
            <p>v0.13.0 keeps <code>/platform/</code> as the stable route while presenting the product publicly as <strong>Workspace</strong>. Page conversion and navigation relabeling remain explicit administrator actions with rollback.</p>
            <?php if ($result === 'converted') : ?><div class="notice notice-success inline"><p>Platform was converted to the dedicated Workspace page. A rollback snapshot was preserved.</p></div><?php endif; ?>
            <?php if ($result === 'restored') : ?><div class="notice notice-success inline"><p>The original Platform page title and content were restored.</p></div><?php endif; ?>
            <?php if ($result === 'missing') : ?><div class="notice notice-error inline"><p>No root page with slug <code>platform</code> was found. Nothing was changed.</p></div><?php endif; ?>
            <?php if ($result === 'failed') : ?><div class="notice notice-error inline"><p>The requested page change failed. Nothing further was changed.</p></div><?php endif; ?>
            <?php if ($result === 'nav-updated') : ?><div class="notice notice-success inline"><p>Matching Platform navigation labels now display as Workspace. A navigation-label snapshot was preserved.</p></div><?php endif; ?>
            <?php if ($result === 'nav-restored') : ?><div class="notice notice-success inline"><p>The previous navigation labels were restored.</p></div><?php endif; ?>
            <?php if ($result === 'nav-none') : ?><div class="notice notice-info inline"><p>No matching Platform navigation labels required changing.</p></div><?php endif; ?>
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
                    <tr><th>Recommended navigation label</th><td><strong>Workspace</strong> (route remains <code>/platform/</code>)</td></tr>
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
            <hr style="max-width:900px;margin:32px 0 24px">
            <h2>Public navigation label</h2>
            <p style="max-width:900px">The public product name is <strong>Workspace</strong>. This action changes only matching WordPress navigation-item labels that point to the root Platform page or <code>/platform/</code>. It does not change the route or unrelated menu items.</p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:inline-block;margin-right:8px">
                <input type="hidden" name="action" value="sc_workspace_relabel_navigation">
                <?php wp_nonce_field('sc_workspace_relabel_navigation_v082'); ?>
                <?php submit_button('Relabel Platform navigation to Workspace', 'primary', 'submit', false); ?>
            </form>
            <?php if (get_option(self::NAV_BACKUP_KEY, null) !== null) : ?>
                <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" style="display:inline-block">
                    <input type="hidden" name="action" value="sc_workspace_restore_navigation">
                    <?php wp_nonce_field('sc_workspace_restore_navigation_v082'); ?>
                    <?php submit_button('Restore previous navigation labels', 'secondary', 'submit', false); ?>
                </form>
            <?php endif; ?>
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

    public static function relabel_navigation_items() {
        $page = get_page_by_path('platform', OBJECT, 'page');
        $page_id = $page && !empty($page->ID) ? (int) $page->ID : 0;
        $items = get_posts(array(
            'post_type' => 'nav_menu_item',
            'post_status' => 'any',
            'numberposts' => -1,
            'orderby' => 'ID',
            'order' => 'ASC',
        ));
        $changes = array();
        foreach ($items as $item) {
            $title = trim((string) $item->post_title);
            $url = (string) get_post_meta($item->ID, '_menu_item_url', true);
            $object_id = (int) get_post_meta($item->ID, '_menu_item_object_id', true);
            $object = (string) get_post_meta($item->ID, '_menu_item_object', true);
            $matches_page = $page_id && $object === 'page' && $object_id === $page_id;
            $path = $url ? wp_parse_url($url, PHP_URL_PATH) : '';
            $matches_url = $path && untrailingslashit($path) === untrailingslashit(wp_parse_url(home_url('/platform/'), PHP_URL_PATH));
            if (strcasecmp($title, 'Platform') !== 0 || (!$matches_page && !$matches_url)) {
                continue;
            }
            $changes[] = array('id' => (int) $item->ID, 'title' => $title);
        }
        if (!$changes) {
            return array('changed' => 0, 'items' => array());
        }
        if (get_option(self::NAV_BACKUP_KEY, null) === null) {
            add_option(self::NAV_BACKUP_KEY, array('captured_at' => gmdate('c'), 'items' => $changes), '', 'no');
        }
        $changed = 0;
        foreach ($changes as $change) {
            $result = wp_update_post(array('ID' => $change['id'], 'post_title' => 'Workspace'), true);
            if (!is_wp_error($result)) {
                $changed++;
            }
        }
        return array('changed' => $changed, 'items' => $changes);
    }

    public static function restore_navigation_items() {
        $backup = get_option(self::NAV_BACKUP_KEY, null);
        if (!is_array($backup) || empty($backup['items']) || !is_array($backup['items'])) {
            return new WP_Error('sc_workspace_nav_backup_missing', 'No navigation-label snapshot is available.');
        }
        foreach ($backup['items'] as $item) {
            if (empty($item['id'])) {
                continue;
            }
            wp_update_post(array('ID' => (int) $item['id'], 'post_title' => isset($item['title']) ? (string) $item['title'] : 'Platform'), true);
        }
        return true;
    }

    public function handle_relabel_navigation() {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        check_admin_referer('sc_workspace_relabel_navigation_v082');
        $result = self::relabel_navigation_items();
        $this->redirect_result(!empty($result['changed']) ? 'nav-updated' : 'nav-none');
    }

    public function handle_restore_navigation() {
        if (!current_user_can('manage_options')) {
            wp_die('Insufficient permissions.');
        }
        check_admin_referer('sc_workspace_restore_navigation_v082');
        $result = self::restore_navigation_items();
        $this->redirect_result(is_wp_error($result) ? 'failed' : 'nav-restored');
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
