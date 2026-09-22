#' Export a comparative scenario bundle
#'
#' Writes comparison tables, canonical scenarios, trajectories, plots, a JSON
#' summary, and a checksummed manifest.
#'
#' @param comparison A `catalyst_comparison` or comparison-compatible input.
#' @param dir Parent output directory.
#' @param comparison_id Identifier used for the bundle folder and archive.
#' @param zip Create a zip archive.
#' @param overwrite Replace existing outputs.
#' @param quiet Suppress informational messages.
#' @return Invisibly returns bundle paths, manifest, and written-file inventory.
#' @export
export_scenario_comparison <- function(
  comparison,
  dir,
  comparison_id = NULL,
  zip = TRUE,
  overwrite = FALSE,
  quiet = FALSE
) {
  if (!inherits(comparison, "catalyst_comparison")) comparison <- compare_scenarios(comparison)
  .assert_single_string(dir, "dir")
  .assert_flag(zip, "zip")
  .assert_flag(overwrite, "overwrite")
  .assert_flag(quiet, "quiet")
  if (is.null(comparison_id)) comparison_id <- paste0("comparison_", format(Sys.time(), "%Y%m%d_%H%M%S"))
  .assert_single_string(comparison_id, "comparison_id")
  safe_id <- gsub("[^A-Za-z0-9._-]+", "-", trimws(comparison_id))
  safe_id <- gsub("^-+|-+$", "", safe_id)
  if (!nzchar(safe_id)) stop("`comparison_id` must contain a usable character.", call. = FALSE)

  if (!dir.exists(dir) && !dir.create(dir, recursive = TRUE, showWarnings = FALSE)) stop("Could not create output directory.", call. = FALSE)
  out_dir <- file.path(dir, paste0("comparison_", safe_id))
  if (dir.exists(out_dir)) {
    if (!overwrite) stop("Comparison bundle already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
    unlink(out_dir, recursive = TRUE, force = TRUE)
  }
  if (!dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)) stop("Could not create comparison bundle directory.", call. = FALSE)
  scenario_dir <- file.path(out_dir, "scenarios")
  trajectory_dir <- file.path(out_dir, "trajectories")
  plot_dir <- file.path(out_dir, "plots")
  dir.create(scenario_dir)
  dir.create(trajectory_dir)
  dir.create(plot_dir)

  written <- character()
  write_df <- function(name, value, parent = out_dir) {
    path <- file.path(parent, paste0(name, ".csv"))
    utils::write.csv(value, path, row.names = FALSE, na = "")
    written <<- c(written, path)
    path
  }
  write_df("scenario_index", comparison$scenario_set$index)
  write_df("terminal_values", comparison$values)
  write_df("deltas", comparison$deltas)
  write_df("rankings", comparison$rankings)
  write_df("scorecard", comparison$scorecard)
  write_df("tradeoffs", comparison$tradeoffs)
  write_df("pareto_front", comparison$pareto$front)
  write_df("dominance", comparison$pareto$dominance)
  write_df("rules", comparison$rules)
  write_df("rule_results", comparison$rule_results)

  for (scenario_id in names(comparison$scenario_set$runs)) {
    run <- comparison$scenario_set$runs[[scenario_id]]
    scenario_path <- file.path(scenario_dir, paste0(scenario_id, ".json"))
    scenario_to_json(run$scenario, scenario_path, pretty = TRUE)
    written <- c(written, scenario_path)
    write_df(scenario_id, run$trajectory_wide, trajectory_dir)
  }

  for (metric in comparison$metrics) {
    trajectory_plot <- plot_scenario_comparison(comparison, metric, "trajectory")
    terminal_plot <- plot_scenario_comparison(comparison, metric, "terminal")
    trajectory_path <- file.path(plot_dir, paste0(metric, "_trajectory.png"))
    terminal_path <- file.path(plot_dir, paste0(metric, "_terminal.png"))
    save_plot(trajectory_plot, trajectory_path)
    save_plot(terminal_plot, terminal_path)
    written <- c(written, trajectory_path, terminal_path)
  }

  summary_payload <- list(
    schema_version = "1.0.0",
    comparison_id = safe_id,
    package = "catalystanalyticsr",
    package_version = .catalyst_package_version(),
    created_at = .utc_now(),
    model = comparison$model,
    baseline_id = comparison$baseline_id,
    metrics = unname(comparison$metrics),
    scenarios = unname(lapply(comparison$scenario_set$scenarios, .safe_json_value)),
    terminal_values = .safe_json_value(comparison$values),
    deltas = .safe_json_value(comparison$deltas),
    rankings = .safe_json_value(comparison$rankings),
    tradeoffs = .safe_json_value(comparison$tradeoffs),
    pareto = list(
      front = .safe_json_value(comparison$pareto$front),
      dominance = .safe_json_value(comparison$pareto$dominance),
      metrics = unname(comparison$pareto$metrics)
    ),
    rules = .safe_json_value(comparison$rules),
    rule_results = .safe_json_value(comparison$rule_results),
    boundary = list(forecast = FALSE, compliance = FALSE, professional_advice = FALSE)
  )
  summary_path <- file.path(out_dir, "comparison.json")
  jsonlite::write_json(.safe_json_value(summary_payload), summary_path, auto_unbox = TRUE, pretty = TRUE, null = "null", dataframe = "rows")
  written <- c(written, summary_path)

  relative_paths <- function(paths) substring(paths, nchar(out_dir) + 2L)
  inventory <- function(paths) {
    info <- file.info(paths)
    hashes <- unname(tools::md5sum(paths))
    unname(lapply(seq_along(paths), function(i) list(
      path = relative_paths(paths[i]),
      bytes = unname(info$size[i]),
      md5 = hashes[i]
    )))
  }
  manifest <- list(
    schema_version = "1.0.0",
    package = "catalystanalyticsr",
    package_version = .catalyst_package_version(),
    comparison_id = safe_id,
    requested_comparison_id = comparison_id,
    baseline_id = comparison$baseline_id,
    model = comparison$model,
    scenario_count = comparison$meta$scenario_count,
    metric_count = comparison$meta$metric_count,
    created_at = .utc_now(),
    files = relative_paths(written),
    file_inventory = inventory(written)
  )
  manifest_path <- file.path(out_dir, "manifest.json")
  jsonlite::write_json(.safe_json_value(manifest), manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  written <- c(written, manifest_path)

  zip_path <- NULL
  if (zip) {
    zip_path <- file.path(dir, paste0("comparison_", safe_id, ".zip"))
    if (file.exists(zip_path) && !overwrite) stop("Comparison zip already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
    if (file.exists(zip_path)) unlink(zip_path, force = TRUE)
    files_to_zip <- list.files(out_dir, all.files = TRUE, recursive = TRUE, no.. = TRUE)
    old <- getwd()
    on.exit(setwd(old), add = TRUE)
    setwd(out_dir)
    utils::zip(zipfile = zip_path, files = files_to_zip)
  }
  if (!quiet) message("Comparison bundle written to: ", out_dir)
  invisible(list(bundle_dir = out_dir, zip_path = zip_path, manifest = manifest, written = written))
}
