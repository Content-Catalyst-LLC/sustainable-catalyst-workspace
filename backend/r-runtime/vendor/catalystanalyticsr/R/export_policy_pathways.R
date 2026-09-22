.policy_pathway_markdown <- function(analysis) {
  optimization <- analysis$optimization
  recommendation <- optimization$recommendation
  decisions <- if (is.null(recommendation)) "- No feasible recommendation was identified." else vapply(names(recommendation$decisions), function(id) paste0("- `", id, "`: ", format(recommendation$decisions[[id]], digits = 6)), character(1))
  c(
    paste0("# ", analysis$title), "",
    paste0("**Analysis ID:** `", analysis$id, "`  "),
    paste0("**Candidates:** ", nrow(optimization$candidates), "  "),
    paste0("**Feasible:** ", sum(optimization$candidates$feasible), "  "),
    paste0("**Pareto candidates:** ", sum(optimization$candidates$pareto), "  "), "",
    "## Review recommendation", decisions, "",
    "## Decision boundary",
    "Optimization results are analytical recommendations. They do not establish causal validity, allocate public resources, authorize a policy, or execute an adaptive trigger. Human review is required."
  )
}

#' Export optimization and policy-pathway evidence
#'
#' @param analysis A `catalyst_policy_pathway_analysis`.
#' @param dir Parent output directory.
#' @param prefix Bundle directory name.
#' @param zip_bundle Create a ZIP archive.
#' @return Named generated paths.
#' @export
export_policy_pathway_analysis <- function(analysis, dir = ".", prefix = "catalyst-policy-pathway", zip_bundle = TRUE) {
  if (!inherits(analysis, "catalyst_policy_pathway_analysis")) stop("`analysis` must be a policy pathway analysis.", call. = FALSE)
  .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(zip_bundle, "zip_bundle")
  bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(bundle_dir = bundle_dir)
  paths$analysis <- file.path(bundle_dir, "policy-pathway-analysis.json")
  jsonlite::write_json(.safe_json_value(unclass(analysis)), paths$analysis, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  paths$candidates <- file.path(bundle_dir, "optimization-candidates.csv"); utils::write.csv(analysis$optimization$candidates, paths$candidates, row.names = FALSE)
  paths$pareto <- file.path(bundle_dir, "pareto-frontier.csv"); utils::write.csv(analysis$optimization$pareto_frontier, paths$pareto, row.names = FALSE)
  paths$feasible_region <- file.path(bundle_dir, "feasible-region.json")
  jsonlite::write_json(.safe_json_value(analysis$optimization$feasible_region), paths$feasible_region, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA)
  if (!is.null(analysis$pathway)) {
    paths$pathway <- file.path(bundle_dir, "adaptive-policy-pathway.json")
    jsonlite::write_json(.safe_json_value(unclass(analysis$pathway)), paths$pathway, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
    paths$sequence <- file.path(bundle_dir, "policy-sequence.csv"); utils::write.csv(policy_sequence(analysis$pathway), paths$sequence, row.names = FALSE)
  }
  if (!is.null(analysis$pathway_evaluation)) {
    paths$triggers <- file.path(bundle_dir, "adaptive-trigger-status.csv"); utils::write.csv(analysis$pathway_evaluation$trigger_status, paths$triggers, row.names = FALSE)
  }
  if (!is.null(analysis$robust_analysis)) {
    paths$robustness <- file.path(bundle_dir, "robust-pathway-summary.csv"); utils::write.csv(analysis$robust_analysis$summary, paths$robustness, row.names = FALSE)
    paths$regret <- file.path(bundle_dir, "scenario-regret.csv"); utils::write.csv(analysis$robust_analysis$performance, paths$regret, row.names = FALSE)
  }
  if (!is.null(analysis$cost_effectiveness)) {
    paths$cost_effectiveness <- file.path(bundle_dir, "cost-effectiveness.csv"); utils::write.csv(analysis$cost_effectiveness, paths$cost_effectiveness, row.names = FALSE)
  }
  if (!is.null(analysis$marginal_abatement)) {
    paths$marginal_abatement <- file.path(bundle_dir, "marginal-abatement.csv"); utils::write.csv(analysis$marginal_abatement, paths$marginal_abatement, row.names = FALSE)
  }
  paths$readme <- file.path(bundle_dir, "README.md"); writeLines(.policy_pathway_markdown(analysis), paths$readme, useBytes = TRUE)
  files <- list.files(bundle_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE)
  base <- normalizePath(bundle_dir)
  records <- lapply(files, function(path) list(file = substring(normalizePath(path), nchar(base) + 2L), bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path))))
  manifest <- list(
    schema_version = "1.0.0", export_type = "optimization_and_policy_pathway_bundle",
    analysis_id = analysis$id, package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    created_at = format(Sys.time(), tz = "UTC", usetz = TRUE), file_count = length(records), files = records,
    integrity = list(hash_algorithm = "md5", complete = TRUE, scope = "all_bundle_files_except_manifest"),
    boundary = list(human_review_required = TRUE, recommendation_not_authorization = TRUE, triggers_not_execution = TRUE)
  )
  paths$manifest <- file.path(bundle_dir, "manifest.json")
  jsonlite::write_json(manifest, paths$manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (zip_bundle) {
    paths$zip <- file.path(dir, paste0(prefix, ".zip")); old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir); utils::zip(zipfile = basename(paths$zip), files = prefix)
  }
  paths
}
