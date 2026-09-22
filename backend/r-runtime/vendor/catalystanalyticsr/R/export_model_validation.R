.model_validation_payload <- function(x) {
  list(
    schema_version = x$schema_version, export_type = "model_validation_governance", analysis_id = x$id, title = x$title,
    summary = model_validation_summary(x),
    calibration = list(
      schema_version = x$calibration$schema_version, calibration_id = x$calibration$calibration_id,
      model = x$calibration$model, specification = unclass(x$calibration$specification), parameters = x$calibration$parameters,
      objective = x$calibration$objective, convergence = x$calibration$convergence, fitted = x$calibration$fitted
    ),
    validation = list(
      schema_version = x$validation$schema_version, validation_id = x$validation$validation_id, status = x$validation$status,
      metrics = x$validation$metrics, residual_diagnostics = x$validation$residual_diagnostics,
      thresholds = x$validation$thresholds, checks = x$validation$checks
    ),
    solver_benchmark = if (is.null(x$solver_benchmark)) NULL else unclass(x$solver_benchmark),
    stability_assessment = if (is.null(x$stability_assessment)) NULL else unclass(x$stability_assessment),
    governance = unclass(x$governance), review_boundary = list(
      calibration_requires_review = TRUE, validation_thresholds_require_review = TRUE, numerical_tolerances_require_review = TRUE,
      intended_use_requires_approval = TRUE, limitations_must_be_disclosed = TRUE, not_forecast_or_professional_advice = TRUE
    ), meta = x$meta
  )
}

.write_model_validation_json <- function(payload, path) {
  jsonlite::write_json(.safe_json_value(payload), path, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  path
}

.model_validation_markdown_brief <- function(x) {
  summary <- model_validation_summary(x)
  parameters <- paste(sprintf("- %s: %.6g (initial %.6g)", x$calibration$parameters$parameter, x$calibration$parameters$estimate, x$calibration$parameters$initial), collapse = "\n")
  limitations <- x$governance$model_card$limitations
  limitation_text <- if (length(limitations)) paste(vapply(limitations, function(item) paste0("- ", item$title, " [", item$severity, "]: ", item$description), character(1)), collapse = "\n") else "- None recorded"
  c(
    "# Catalyst Analytics R Model Validation Brief", "",
    paste0("**Analysis:** ", x$title), paste0("**Model:** ", summary$model_id, "@", summary$model_version),
    paste0("**Lifecycle:** ", summary$lifecycle_status), "", "## Calibration",
    paste0("- Objective value: ", format(summary$calibration_objective, digits = 6)),
    paste0("- Converged: ", ifelse(summary$calibration_converged, "yes", "no")), parameters, "",
    "## Validation", paste0("- Status: ", summary$validation_status),
    paste0("- Holdout RMSE: ", format(summary$holdout_rmse, digits = 6)), paste0("- Holdout MAE: ", format(summary$holdout_mae, digits = 6)), "",
    "## Numerical evidence", paste0("- Solver cases: ", summary$solver_cases), paste0("- Stability passed: ", summary$stability_passed), "",
    "## Known limitations", limitation_text, "", "## Review boundary",
    "Calibration, validation thresholds, numerical tolerances, intended use, limitations, and lifecycle approval require qualified human review."
  )
}

#' Export model calibration, validation, and governance evidence
#'
#' @param x A `catalyst_model_validation_analysis`.
#' @param dir Parent export directory.
#' @param prefix Bundle directory name.
#' @param include_history Include optimizer history.
#' @param zip_bundle Create a ZIP archive.
#' @return Named paths to exported files.
#' @export
export_model_validation <- function(x, dir = ".", prefix = "catalyst-model-validation", include_history = TRUE, zip_bundle = TRUE) {
  if (!inherits(x, "catalyst_model_validation_analysis")) stop("`x` must be a model-validation analysis.", call. = FALSE)
  .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(include_history, "include_history"); .assert_flag(zip_bundle, "zip_bundle")
  bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(bundle_dir = bundle_dir)
  paths$analysis <- .write_model_validation_json(.model_validation_payload(x), file.path(bundle_dir, "model-validation.json"))
  utils::write.csv(x$calibration$parameters, file.path(bundle_dir, "calibrated-parameters.csv"), row.names = FALSE); paths$parameters <- file.path(bundle_dir, "calibrated-parameters.csv")
  utils::write.csv(x$calibration$fitted, file.path(bundle_dir, "fitted-observations.csv"), row.names = FALSE); paths$fitted <- file.path(bundle_dir, "fitted-observations.csv")
  utils::write.csv(x$validation$metrics, file.path(bundle_dir, "validation-metrics.csv"), row.names = FALSE); paths$metrics <- file.path(bundle_dir, "validation-metrics.csv")
  utils::write.csv(x$validation$residual_diagnostics, file.path(bundle_dir, "residual-diagnostics.csv"), row.names = FALSE); paths$residuals <- file.path(bundle_dir, "residual-diagnostics.csv")
  if (include_history && nrow(x$calibration$history)) { utils::write.csv(x$calibration$history, file.path(bundle_dir, "calibration-history.csv"), row.names = FALSE); paths$history <- file.path(bundle_dir, "calibration-history.csv") }
  if (!is.null(x$solver_benchmark)) { utils::write.csv(x$solver_benchmark$summary, file.path(bundle_dir, "solver-benchmark.csv"), row.names = FALSE); paths$solver <- file.path(bundle_dir, "solver-benchmark.csv") }
  if (!is.null(x$stability_assessment)) {
    utils::write.csv(x$stability_assessment$perturbations, file.path(bundle_dir, "stability-perturbations.csv"), row.names = FALSE)
    utils::write.csv(x$stability_assessment$invariants, file.path(bundle_dir, "invariant-tests.csv"), row.names = FALSE)
    utils::write.csv(x$stability_assessment$boundary_conditions, file.path(bundle_dir, "boundary-condition-tests.csv"), row.names = FALSE)
    paths$stability <- file.path(bundle_dir, "stability-perturbations.csv")
  }
  paths$governance <- .write_model_validation_json(unclass(x$governance), file.path(bundle_dir, "model-governance.json"))
  brief <- file.path(bundle_dir, "model-validation-brief.md"); writeLines(.model_validation_markdown_brief(x), brief, useBytes = TRUE); paths$brief <- brief
  files <- setdiff(list.files(bundle_dir, full.names = TRUE), file.path(bundle_dir, "manifest.json"))
  manifest <- list(schema_version = "1.0.0", export_type = "model_validation_bundle", package_version = .catalyst_package_version(), analysis_id = x$id, created_at = .utc_now(), files = lapply(files, function(path) list(file = basename(path), bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path)))))
  paths$manifest <- .write_model_validation_json(manifest, file.path(bundle_dir, "manifest.json"))
  if (zip_bundle) { zip_path <- file.path(dir, paste0(prefix, ".zip")); old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir); utils::zip(zipfile = basename(zip_path), files = prefix); paths$zip <- zip_path }
  paths
}
