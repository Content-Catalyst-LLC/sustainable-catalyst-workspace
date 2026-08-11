<?php
/**
 * Plugin Name: Sustainable Catalyst Workspace
 * Plugin URI: https://sustainablecatalyst.com/platform/
 * Description: Free public research, evidence, analysis, decision, briefing, personal knowledge, inspectable knowledge graph, workflow intelligence, asynchronous review, institutional handoff, responsible AI assistance, interoperability, and portable sharing workspace with read-only API/embed projections, hardened local recovery, accessibility, diagnostics, release-readiness safeguards, and optional manual account recovery, conflict-safe cross-device synchronization, local project restore-point history, inspectable project change review, guided selective reconciliation into new project copies, integrity-fingerprinted reconciliation decision receipts, a derived project audit trail that unifies consequential governance events without a shadow history database, human-declared governance milestones with inspectable readiness evidence, a consolidated public-beta start experience with guided first-run pathways and compatibility status, privacy-minimized public-beta field diagnostics with explicit issue-report export and no automatic submission, a project-bound Research Notebook for low-friction working memory, explicit Source Capture & Research Clipping with bibliographic context and reviewable handoffs, Notebook Collections & Knowledge Linking with explicit cross-notebook references, backlinks, and mixed notebook/object collections, Notebook-to-Workspace Intelligence for explicit promotion into Source, Evidence, Dataset, Analysis, Decision, Document, and Canvas derivatives with visible promotion lineage, Notebook Synthesis & Citation Workspace for explicit-selection outlines, citation packs, source matrices, evidence summaries, and research-synthesis drafts without citation guessing, Grounded Notebook Assistance for citation-required questions against explicitly selected local research with provider-neutral, reviewable draft responses, and Portable & Synced Notebooks with integrity-checked import/export, notebook restore points, explicit account backup, opt-in revision-preconditioned sync, and preserve-both conflict recovery, plus Notebook Review & Provenance with notebook-level Change Review, selective reconciliation into new notebook copies, derived audit history, and inspectable source lineage, an Integrated Knowledge Workspace that unifies canonical Notebook, Personal Knowledge, and Research Workspace material through one derived research index without duplicating source content, and Unified Research Navigation that organizes the full product into five primary areas with contextual deep routes instead of a flat seventeen-item tool strip, plus Research Collections & Dynamic Views with fielded cross-project search, local saved searches, explainable provenance-aware ranking, and explicit related-material navigation over the canonical Integrated Knowledge index, and Citation Library & Reference Management with reusable browser-local references, deterministic duplicate review, citation keys, citation style previews, and portable reference exchange without metadata invention, plus Research Graph & Relationship Explorer with Notebook, citation, promotion, synthesis, provenance, evidence, analysis, and decision relationships derived only from recorded Workspace state, and Cross-Project Knowledge for explicit browser-local references from one project context to canonical research owned by another project without copying content or changing ownership, plus Research Templates & Reusable Workflows with structure-only research protocols, Notebook scaffolds, explicit project starters, and portable custom templates that never copy findings or research content, plus Workspace Experience Consolidation with browser-local density preferences, a route command palette, keyboard navigation, terminology help, responsive horizontal mobile navigation, and consistent interaction targets without canonical data migration, and Grounded Research Assistant II for explicit Integrated Knowledge scope selection, frozen grounding packets, citation-enforced provider-neutral draft responses, and human-reviewed Document materialization without automatic AI invocation or canonical mutation, plus Research Tasks & Workflow State for explicit review, verification, sourcing, citation, synthesis, and follow-up tasks around canonical research references with separate task-state history and no automatic canonical mutation. Collaboration Architecture Foundation adds browser-local actors, project ownership policies, capability grants, canonical-target comments, review proposals, and shareable-project contracts without live co-editing or automatic proposal application. Shared Review & Research Handoff adds explicitly scoped frozen review packages, package-matched external responses, staged response import, and review-ledger handoff without silent canonical mutation. Research Automation Framework adds browser-local user-authored routines, declarative cadences, explicit manual execution, and reviewable run receipts for import review, source review, verification, synthesis refresh, and workflow follow-up without background jobs or canonical mutation. Institutional Research Packages adds explicitly scoped frozen institutional disclosure bundles containing selected research plus optional citations, provenance, task context, and collaboration review context with deterministic integrity receipts, while leaving the source project unchanged and preserving the legacy Catalyst Intelligence promotion path. Scale, Performance & Large-Project Hardening adds advisory large-workspace budgets, derived-index caching, bounded research-result rendering, storage-pressure visibility, and large-project stress fixtures without automatic deletion, archiving, compaction, or schema migration. Security, Privacy & Data-Portability Audit adds an explicit same-origin/local-storage threat model, complete Workspace-owned browser-store inventory, full browser-local portability export, disclosure/recovery boundary inspection, and typed-confirmation verified browser-local deletion while clearly separating account/cloud deletion and avoiding encryption or authorization claims the product does not provide. Focused Application Shell & Route Isolation prevents inactive Workspace surfaces from leaking into the page layout and splits the Integrated Research mega-page into one active research tool at a time. Product Hardening I adds route/session resilience, back-forward-safe navigation, stale UI-state sanitization, recovery capability classification, and actionable field-use diagnostics without changing canonical research or project schemas. Product Hardening II adds verified-save integrity receipts, write transaction journaling, interrupted-write detection, checksum-bound last-known-good snapshots, and explicit recovery candidate exports. Cross-Browser & Device Compatibility adds feature-detected file/import/export/history fallbacks, root-bound viewport adaptation, touch/embed awareness, and a privacy-minimized compatibility audit without browser-family feature gating or canonical schema migration. Accessibility & Keyboard-First Product Audit adds keyboard navigation groups, modal focus containment/restoration, stronger visible-focus and reduced-motion/forced-colors handling, privacy-minimized accessibility diagnostics, and explicit manual WCAG 2.2 AA field QA without claiming automated certification.
 * Version: 0.64.0
 * Author: Content Catalyst LLC
 * Text Domain: sustainable-catalyst-workspace
 * Requires at least: 6.4
 * Requires PHP: 8.0
 */

if (!defined('ABSPATH')) {
    exit;
}

define('SC_WORKSPACE_VERSION', '0.64.0');
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

/** Public read-only static embed renderer URL for explicitly disclosed Workspace projections. */
function sc_workspace_api_embed_script_url() {
    return SC_WORKSPACE_URL . 'assets/js/sc-workspace-api-embed-v1.js';
}
