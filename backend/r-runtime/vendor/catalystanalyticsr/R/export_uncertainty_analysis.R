.data_frame_records <- function(x) {
  if (is.null(x) || !is.data.frame(x) || !nrow(x)) return(list())
  lapply(seq_len(nrow(x)), function(i) as.list(x[i, , drop = FALSE]))
}

.file_hash_table <- function(paths, base_dir) {
  paths <- paths[file.exists(paths)]
  data.frame(
    file = sub(paste0("^", normalizePath(base_dir, winslash = "/"), "/?"), "", normalizePath(paths, winslash = "/")),
    md5 = unname(tools::md5sum(paths)),
    bytes = unname(file.info(paths)$size),
    stringsAsFactors = FALSE
  )
}

#' Export a reproducible uncertainty-analysis bundle
#'
#' @param x A `catalyst_uncertainty_run`.
#' @param dir Output directory.
#' @param prefix File prefix.
#' @param include_samples Include sampled inputs and per-sample results.
#' @param zip_bundle Create a ZIP archive.
#' @return Invisibly returns generated file paths.
#' @export
export_uncertainty_analysis <- function(
  x,
  dir = "catalyst_uncertainty_bundle",
  prefix = "uncertainty",
  include_samples = TRUE,
  zip_bundle = TRUE
) {
  if (!inherits(x, "catalyst_uncertainty_run")) stop("`x` must be a catalyst_uncertainty_run.", call. = FALSE)
  .assert_single_string(dir, "dir")
  .assert_single_string(prefix, "prefix")
  .assert_flag(include_samples, "include_samples")
  .assert_flag(zip_bundle, "zip_bundle")
  dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  scenario_path <- file.path(dir, paste0(prefix, "-scenario.json"))
  scenario_to_json(x$scenario, path = scenario_path, pretty = TRUE)
  summary_path <- file.path(dir, paste0(prefix, "-summary.csv"))
  sensitivity_path <- file.path(dir, paste0(prefix, "-sensitivity.csv"))
  probability_path <- file.path(dir, paste0(prefix, "-probabilities.csv"))
  failure_path <- file.path(dir, paste0(prefix, "-failures.csv"))
  utils::write.csv(x$summary, summary_path, row.names = FALSE, na = "")
  utils::write.csv(x$sensitivity, sensitivity_path, row.names = FALSE, na = "")
  utils::write.csv(x$probabilities, probability_path, row.names = FALSE, na = "")
  utils::write.csv(x$failures, failure_path, row.names = FALSE, na = "")
  paths <- c(scenario_path, summary_path, sensitivity_path, probability_path, failure_path)
  if (include_samples) {
    sample_path <- file.path(dir, paste0(prefix, "-samples.csv"))
    result_path <- file.path(dir, paste0(prefix, "-sample-results.csv"))
    utils::write.csv(x$samples, sample_path, row.names = FALSE, na = "")
    utils::write.csv(x$results, result_path, row.names = FALSE, na = "")
    paths <- c(paths, sample_path, result_path)
  }
  json_path <- file.path(dir, paste0(prefix, "-analysis.json"))
  payload <- list(
    schema_version = x$schema_version,
    analysis_type = "uncertainty_ensemble",
    scenario = unclass(x$scenario),
    scenario_fingerprint = scenario_fingerprint(x$scenario),
    specifications = x$specifications,
    summary = .data_frame_records(x$summary),
    thresholds = .data_frame_records(x$thresholds),
    probabilities = .data_frame_records(x$probabilities),
    sensitivity = .data_frame_records(x$sensitivity),
    failures = .data_frame_records(x$failures),
    meta = x$meta,
    boundary = list(forecast = FALSE, compliance = FALSE, autonomous_decision = FALSE, professional_advice = FALSE)
  )
  jsonlite::write_json(.safe_json_value(payload), json_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", dataframe = "rows", digits = 15)
  paths <- c(paths, json_path)
  manifest_path <- file.path(dir, paste0(prefix, "-manifest.json"))
  manifest <- list(
    schema_version = "1.0.0",
    bundle_type = "catalyst_uncertainty_analysis",
    package_version = .catalyst_package_version(),
    created_at = .utc_now(),
    sampling = x$meta$sampling,
    seed = x$meta$seed,
    requested = x$meta$requested,
    completed = x$meta$completed,
    failed = x$meta$failed,
    scenario_fingerprint = scenario_fingerprint(x$scenario),
    files = .data_frame_records(.file_hash_table(paths, dir))
  )
  jsonlite::write_json(.safe_json_value(manifest), manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", dataframe = "rows")
  paths <- c(paths, manifest_path)
  zip_path <- NULL
  if (zip_bundle) {
    zip_path <- paste0(normalizePath(dir, winslash = "/", mustWork = FALSE), ".zip")
    old <- setwd(dir)
    on.exit(setwd(old), add = TRUE)
    utils::zip(zipfile = zip_path, files = basename(paths))
  }
  invisible(list(directory = normalizePath(dir, winslash = "/", mustWork = FALSE), files = paths, zip = zip_path))
}

#' Export a stress-test comparison bundle
#'
#' @param x A `catalyst_stress_test`.
#' @param dir Output directory.
#' @param prefix File prefix.
#' @return Invisibly returns generated paths.
#' @export
export_stress_test <- function(x, dir = "catalyst_stress_test_bundle", prefix = "stress-test") {
  if (!inherits(x, "catalyst_stress_test")) stop("`x` must be a catalyst_stress_test.", call. = FALSE)
  .assert_single_string(dir, "dir")
  .assert_single_string(prefix, "prefix")
  comparison_bundle <- export_scenario_comparison(
    x$comparison,
    dir = dir,
    comparison_id = prefix,
    zip = FALSE,
    overwrite = TRUE,
    quiet = TRUE
  )
  case_path <- file.path(comparison_bundle$bundle_dir, "stress_cases.json")
  jsonlite::write_json(
    .safe_json_value(list(
      schema_version = x$schema_version,
      baseline_id = x$baseline$id,
      cases = x$cases,
      meta = x$meta
    )),
    case_path,
    auto_unbox = TRUE,
    pretty = TRUE,
    null = "null",
    na = "null"
  )
  invisible(c(comparison_bundle, list(stress_cases = case_path)))
}
