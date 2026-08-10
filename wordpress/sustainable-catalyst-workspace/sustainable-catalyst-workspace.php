<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/
 * Description: Free public research, evidence, analysis, decision, briefing, personal knowledge, inspectable knowledge graph, workflow intelligence, asynchronous review, institutional handoff, responsible AI assistance, interoperability, and portable sharing workspace with hardened local recovery, accessibility, diagnostics, release-readiness safeguards, and optional manual account recovery, conflict-safe cross-device synchronization, local project restore-point history, inspectable project change review, guided selective reconciliation into new project copies, integrity-fingerprinted reconciliation decision receipts, a derived project audit trail that unifies consequential governance events without a shadow history database, human-declared governance milestones with inspectable readiness evidence, a consolidated public-beta start experience with guided first-run pathways and compatibility status, privacy-minimized public-beta field diagnostics with explicit issue-report export and no automatic submission, a project-bound Research Notebook for low-friction working memory, explicit Source Capture & Research Clipping with bibliographic context and reviewable handoffs, Notebook Collections & Knowledge Linking with explicit cross-notebook references, backlinks, and mixed notebook/object collections, Notebook-to-Workspace Intelligence for explicit promotion into Source, Evidence, Dataset, Analysis, Decision, Document, and Canvas derivatives with visible promotion lineage, Notebook Synthesis & Citation Workspace for explicit-selection outlines, citation packs, source matrices, evidence summaries, and research-synthesis drafts without citation guessing, Grounded Notebook Assistance for citation-required questions against explicitly selected local research with provider-neutral, reviewable draft responses, and Portable & Synced Notebooks with integrity-checked import/export, notebook restore points, explicit account backup, opt-in revision-preconditioned sync, and preserve-both conflict recovery, plus Notebook Review & Provenance with notebook-level Change Review, selective reconciliation into new notebook copies, derived audit history, and inspectable source lineage, an Integrated Knowledge Workspace that unifies canonical Notebook, Personal Knowledge, and Research Workspace material through one derived research index without duplicating source content, and Unified Research Navigation that organizes the full product into five primary areas with contextual deep routes instead of a flat seventeen-item tool strip.
 * Version: 0.41.0
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '0.41.0');
define('SC_WORKSPACE_FILE', __FILE__);
define('SC_WORKSPACE_DIR', plugin_dir_path(__FILE__));
define('SC_WORKSPACE_URL', plugin_dir_url(__FILE__));

require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace-registry.php';
require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace-platform.php';
require_once SC_WORKSPACE_DIR . 'includes/class-sc-workspace.php';

register_activation_hook(__FILE__, array('SC_Workspace_Registry', 'activate'));

SC_Workspace_Platform::instance();
SC_Workspace::instance();

/** Public producer helper URL for compatible Sustainable Catalyst tools. */
function sc_workspace_return_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-return-adapter-v1.js';
}

/** Public Responsible AI adapter helper URL for compatible same-origin tools. */
function sc_workspace_ai_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-ai-adapter-v1.js';
}

/** Public Source Capture adapter helper URL for compatible same-origin research surfaces. */
function sc_workspace_source_capture_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-source-capture-v1.js';
}

/** Public Grounded Notebook Assistance adapter helper URL for compatible same-origin research surfaces. */
function sc_workspace_notebook_assistance_adapter_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-notebook-assistance-adapter-v1.js';
}
