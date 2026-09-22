.catalyst_model_validation_analysis_schema_version <- function() "1.0.0"

#' Assemble calibration, validation, numerical, and governance evidence
#'
#' @param calibration A `catalyst_calibration`.
#' @param validation A `catalyst_model_validation`.
#' @param solver Optional `catalyst_solver_benchmark`.
#' @param stability Optional `catalyst_stability_assessment`.
#' @param governance A `catalyst_model_governance` record.
#' @param analysis_id Stable analysis identifier.
#' @param title Human-readable title.
#' @param metadata Additional metadata.
#' @return A `catalyst_model_validation_analysis`.
#' @export
model_validation_analysis <- function(calibration, validation, solver = NULL, stability = NULL, governance, analysis_id = "model-validation", title = "Calibration, validation, and model governance", metadata = list()) {
  if (!inherits(calibration, "catalyst_calibration")) stop("`calibration` is invalid.", call. = FALSE)
  if (!inherits(validation, "catalyst_model_validation")) stop("`validation` is invalid.", call. = FALSE)
  if (!is.null(solver) && !inherits(solver, "catalyst_solver_benchmark")) stop("`solver` is invalid.", call. = FALSE)
  if (!is.null(stability) && !inherits(stability, "catalyst_stability_assessment")) stop("`stability` is invalid.", call. = FALSE)
  if (!inherits(governance, "catalyst_model_governance")) stop("`governance` is invalid.", call. = FALSE)
  .validate_dataset_id(analysis_id, "analysis_id"); .assert_single_string(title, "title")
  structure(list(
    schema_version = .catalyst_model_validation_analysis_schema_version(), analysis_type = "calibration_validation_model_governance",
    id = analysis_id, title = title, calibration = calibration, validation = validation, solver_benchmark = solver,
    stability_assessment = stability, governance = governance,
    meta = utils::modifyList(list(package_version = .catalyst_package_version(), created_at = .utc_now(), review_status = "unreviewed", methodology_boundary = "calibration quality, validation thresholds, solver tolerances, intended use, and lifecycle approval require human review"), metadata)
  ), class = "catalyst_model_validation_analysis")
}

#' Summarize integrated model validation evidence
#'
#' @param x A model-validation analysis.
#' @return One-row summary.
#' @export
model_validation_summary <- function(x) {
  if (!inherits(x, "catalyst_model_validation_analysis")) stop("`x` must be a model-validation analysis.", call. = FALSE)
  holdout <- x$validation$metrics[x$validation$metrics$split == "holdout", , drop = FALSE]
  if (!nrow(holdout)) holdout <- x$validation$metrics
  data.frame(
    analysis_id = x$id, model_id = x$calibration$model$id, model_version = x$calibration$model$version,
    calibration_objective = x$calibration$objective, calibration_converged = x$calibration$convergence$code == 0,
    validation_status = x$validation$status, holdout_rmse = if (nrow(holdout)) mean(holdout$rmse) else NA_real_,
    holdout_mae = if (nrow(holdout)) mean(holdout$mae) else NA_real_,
    solver_cases = if (is.null(x$solver_benchmark)) 0L else nrow(x$solver_benchmark$summary),
    stability_passed = if (is.null(x$stability_assessment)) NA else x$stability_assessment$stable,
    lifecycle_status = x$governance$lifecycle_status,
    open_limitations = model_governance_summary(x$governance)$open_limitations,
    stringsAsFactors = FALSE
  )
}

#' @export
print.catalyst_model_validation_analysis <- function(x, ...) {
  summary <- model_validation_summary(x)
  cat(sprintf("<catalyst_model_validation_analysis %s>\n", x$id))
  cat(sprintf("  validation: %s\n", summary$validation_status))
  cat(sprintf("  lifecycle: %s\n", summary$lifecycle_status))
  invisible(x)
}
