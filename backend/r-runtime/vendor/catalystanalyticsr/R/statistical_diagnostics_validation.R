# Statistical diagnostics and validation evidence contract.

.statistical_diagnostics_contract_version <- function() "1.0.0"
.statistical_diagnostics_contract_ref <- function() "sc.analytics-r.statistical-diagnostics-validation.v1"

.statistical_character <- function(x, arg, allow_empty = TRUE) {
  if (!is.character(x) || anyNA(x) || (!allow_empty && !length(x))) {
    stop(sprintf("`%s` must be a character vector.", arg), call. = FALSE)
  }
  unique(x[nzchar(trimws(x))])
}

.statistical_identifier <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z][A-Za-z0-9._:-]*$", x)) {
    stop(sprintf("`%s` must begin with a letter and contain only letters, numbers, periods, underscores, colons, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

#' Statistical diagnostics and validation contract manifest
#' @return Machine-readable diagnostics contract metadata.
#' @export
statistical_diagnostics_manifest <- function() {
  list(
    schema_version = .statistical_diagnostics_contract_version(),
    contract = .statistical_diagnostics_contract_ref(),
    provider_key = "catalystanalyticsr",
    provider_version = .catalyst_package_version(),
    core_provider_contract = "sc.core.analytical-runtime-provider.v1",
    core_result_contract = "sc.core.analytical-result-provenance.v1",
    core_minimum_release = "3.2.0",
    workspace_minimum_release = "3.5.0",
    object_types = c("statistical_diagnostic", "statistical_assumption", "robustness_evidence", "model_comparison_evidence", "statistical_validation_bundle"),
    supported_sources = c("catalyst_model_validation", "catalyst_policy_regression", "provider_native"),
    boundaries = list(
      diagnostics_are_evidence = TRUE,
      p_values_do_not_certify_validity = TRUE,
      thresholds_are_user_or_method_supplied = TRUE,
      assumptions_require_interpretation = TRUE,
      model_comparison_does_not_select_a_winner = TRUE,
      no_automatic_scientific_validity_certification = TRUE,
      no_automatic_policy_authorization = TRUE,
      human_review_required = TRUE
    )
  )
}

#' Create a machine-readable statistical diagnostic
#' @param id Stable diagnostic identifier.
#' @param diagnostic_type Diagnostic category.
#' @param name Human-readable diagnostic name.
#' @param observed Observed statistic or metric value.
#' @param reference Optional comparison/reference value.
#' @param operator Optional comparison operator.
#' @param p_value Optional p-value reported as evidence only.
#' @param method_ref Optional method/test reference.
#' @param units Optional units.
#' @param evidence_refs Related evidence references.
#' @param notes Review notes.
#' @return A statistical diagnostic record.
#' @export
statistical_diagnostic <- function(id, diagnostic_type = c("fit_metric", "residual", "assumption_test", "robustness", "numerical", "calibration", "comparison"), name, observed = NULL, reference = NULL, operator = NULL, p_value = NULL, method_ref = NULL, units = NULL, evidence_refs = character(), notes = character()) {
  diagnostic_type <- match.arg(diagnostic_type)
  .statistical_identifier(id)
  .assert_single_string(name, "name")
  scalar_ok <- function(x) is.null(x) || (length(x) == 1L && (is.numeric(x) || is.character(x)) && !is.na(x))
  if (!scalar_ok(observed)) stop("`observed` must be a scalar number, scalar string, or NULL.", call. = FALSE)
  if (!scalar_ok(reference)) stop("`reference` must be a scalar number, scalar string, or NULL.", call. = FALSE)
  if (!is.null(operator)) {
    .assert_single_string(operator, "operator")
    if (!operator %in% c("<", "<=", "=", ">=", ">", "between", "descriptive")) stop("Unsupported diagnostic operator.", call. = FALSE)
  }
  if (!is.null(p_value)) .assert_scalar_number(p_value, "p_value", lower = 0, upper = 1)
  if (!is.null(method_ref)) .assert_single_string(method_ref, "method_ref")
  if (!is.null(units)) .assert_single_string(units, "units")
  structure(list(
    schema_version = .statistical_diagnostics_contract_version(),
    record_type = "statistical_diagnostic",
    id = id,
    diagnostic_type = diagnostic_type,
    name = name,
    observed = observed,
    reference = reference,
    operator = operator,
    p_value = p_value,
    method_ref = method_ref,
    units = units,
    evidence_refs = .statistical_character(evidence_refs, "evidence_refs"),
    notes = .statistical_character(notes, "notes"),
    boundary = list(
      p_value_is_evidence_not_validity = TRUE,
      threshold_does_not_certify_model = TRUE,
      human_interpretation_required = TRUE
    )
  ), class = c("catalyst_statistical_diagnostic", "list"))
}

#' Create a statistical assumption record
#' @param id Stable identifier.
#' @param label Human-readable label.
#' @param statement Assumption statement.
#' @param status Declared evidence status.
#' @param evidence_refs Evidence references.
#' @param limitations Known limitations.
#' @return A statistical assumption record.
#' @export
statistical_assumption <- function(id, label, statement, status = c("declared", "supported", "challenged", "failed", "not_assessed"), evidence_refs = character(), limitations = character()) {
  status <- match.arg(status)
  .statistical_identifier(id)
  .assert_single_string(label, "label")
  .assert_single_string(statement, "statement")
  structure(list(
    schema_version = .statistical_diagnostics_contract_version(), record_type = "statistical_assumption",
    id = id, label = label, statement = statement, status = status,
    evidence_refs = .statistical_character(evidence_refs, "evidence_refs"),
    limitations = .statistical_character(limitations, "limitations"),
    boundary = list(status_is_evidence_state_not_certification = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_statistical_assumption", "list"))
}

#' Create robustness evidence
#' @param id Stable identifier.
#' @param method_ref Robustness method.
#' @param target_ref Target estimate/model reference.
#' @param result Structured result.
#' @param evidence_refs Evidence references.
#' @param limitations Limitations.
#' @return Robustness evidence record.
#' @export
statistical_robustness_evidence <- function(id, method_ref, target_ref, result = list(), evidence_refs = character(), limitations = character()) {
  .statistical_identifier(id)
  .assert_single_string(method_ref, "method_ref")
  .assert_single_string(target_ref, "target_ref")
  if (!is.list(result)) stop("`result` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .statistical_diagnostics_contract_version(), record_type = "robustness_evidence",
    id = id, method_ref = method_ref, target_ref = target_ref, result = .safe_json_value(result),
    evidence_refs = .statistical_character(evidence_refs, "evidence_refs"),
    limitations = .statistical_character(limitations, "limitations"),
    boundary = list(robustness_does_not_establish_truth = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_statistical_robustness", "list"))
}

#' Create model-comparison evidence without selecting a winner
#' @param id Stable identifier.
#' @param model_refs Model references.
#' @param criteria Named comparison criteria.
#' @param evidence_refs Evidence references.
#' @param notes Notes.
#' @return Model-comparison evidence.
#' @export
statistical_model_comparison <- function(id, model_refs, criteria = list(), evidence_refs = character(), notes = character()) {
  .statistical_identifier(id)
  model_refs <- .statistical_character(model_refs, "model_refs", FALSE)
  if (length(model_refs) < 2L) stop("At least two model references are required.", call. = FALSE)
  if (!is.list(criteria)) stop("`criteria` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .statistical_diagnostics_contract_version(), record_type = "model_comparison_evidence",
    id = id, model_refs = model_refs, criteria = .safe_json_value(criteria),
    evidence_refs = .statistical_character(evidence_refs, "evidence_refs"), notes = .statistical_character(notes, "notes"),
    boundary = list(no_automatic_winner = TRUE, criteria_require_context = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_statistical_model_comparison", "list"))
}

#' Build a statistical validation evidence bundle
#' @param id Stable bundle identifier.
#' @param analysis_ref Analysis reference.
#' @param model_ref Optional model reference.
#' @param diagnostics Diagnostic records.
#' @param assumptions Assumption records.
#' @param robustness Robustness records.
#' @param comparisons Model-comparison records.
#' @param source_status Optional source-system status retained as provenance only.
#' @param limitations Limitations.
#' @param review_status Review state.
#' @param provenance Provenance metadata.
#' @return A statistical validation evidence bundle.
#' @export
statistical_validation_bundle <- function(id, analysis_ref, model_ref = NULL, diagnostics = list(), assumptions = list(), robustness = list(), comparisons = list(), source_status = NULL, limitations = character(), review_status = c("unreviewed", "in_review", "reviewed"), provenance = list()) {
  review_status <- match.arg(review_status)
  .statistical_identifier(id)
  .assert_single_string(analysis_ref, "analysis_ref")
  if (!is.null(model_ref)) .assert_single_string(model_ref, "model_ref")
  if (!is.list(diagnostics) || !is.list(assumptions) || !is.list(robustness) || !is.list(comparisons) || !is.list(provenance)) stop("Diagnostic bundle collections and provenance must be lists.", call. = FALSE)
  if (!is.null(source_status)) .assert_single_string(source_status, "source_status")
  x <- structure(list(
    schema_version = .statistical_diagnostics_contract_version(), bundle_type = "statistical_validation_evidence",
    contract = .statistical_diagnostics_contract_ref(), id = id, analysis_ref = analysis_ref, model_ref = model_ref,
    diagnostics = diagnostics, assumptions = assumptions, robustness = robustness, comparisons = comparisons,
    source_status = source_status, limitations = .statistical_character(limitations, "limitations"), review_status = review_status,
    summary = list(diagnostic_count = length(diagnostics), assumption_count = length(assumptions), robustness_count = length(robustness), comparison_count = length(comparisons)),
    provenance = utils::modifyList(list(package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), created_at = .utc_now()), provenance),
    boundary = list(evidence_only = TRUE, no_automatic_scientific_validity_certification = TRUE, no_automatic_significance_conclusion = TRUE, no_automatic_model_selection = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_statistical_validation_bundle", "list"))
  validate_statistical_validation_bundle(x)
  x
}

#' Validate a statistical validation bundle
#' @param x Statistical validation bundle.
#' @return Invisibly TRUE.
#' @export
validate_statistical_validation_bundle <- function(x) {
  if (!is.list(x)) stop("`x` must be a statistical validation bundle.", call. = FALSE)
  required <- c("schema_version", "bundle_type", "contract", "id", "analysis_ref", "diagnostics", "assumptions", "robustness", "comparisons", "review_status", "summary", "provenance", "boundary")
  missing <- setdiff(required, names(x))
  if (length(missing)) stop("Statistical validation bundle is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(x$schema_version, "1.0.0") || !identical(x$bundle_type, "statistical_validation_evidence") || !identical(x$contract, .statistical_diagnostics_contract_ref())) stop("Unsupported statistical validation contract.", call. = FALSE)
  .statistical_identifier(x$id)
  .assert_single_string(x$analysis_ref, "analysis_ref")
  if (!x$review_status %in% c("unreviewed", "in_review", "reviewed")) stop("Unsupported review status.", call. = FALSE)
  for (d in x$diagnostics) if (!is.list(d) || !identical(d$record_type, "statistical_diagnostic")) stop("Invalid diagnostic record.", call. = FALSE)
  for (a in x$assumptions) if (!is.list(a) || !identical(a$record_type, "statistical_assumption")) stop("Invalid assumption record.", call. = FALSE)
  for (r in x$robustness) if (!is.list(r) || !identical(r$record_type, "robustness_evidence")) stop("Invalid robustness record.", call. = FALSE)
  for (c in x$comparisons) if (!is.list(c) || !identical(c$record_type, "model_comparison_evidence")) stop("Invalid comparison record.", call. = FALSE)
  if (!isTRUE(x$boundary$evidence_only) || !isTRUE(x$boundary$no_automatic_scientific_validity_certification) || !isTRUE(x$boundary$human_review_required)) stop("Statistical validation boundary is invalid.", call. = FALSE)
  invisible(TRUE)
}

#' Convert model-validation output into the v2.2 diagnostics contract
#' @param validation A catalyst_model_validation object.
#' @param analysis_ref Optional analysis reference.
#' @return Statistical validation evidence bundle.
#' @export
statistical_validation_from_model <- function(validation, analysis_ref = NULL) {
  if (!inherits(validation, "catalyst_model_validation")) stop("`validation` must be a catalyst_model_validation.", call. = FALSE)
  if (is.null(analysis_ref)) analysis_ref <- validation$validation_id
  diagnostics <- list()
  idx <- 0L
  if (is.data.frame(validation$metrics)) for (i in seq_len(nrow(validation$metrics))) {
    row <- validation$metrics[i, , drop = FALSE]
    for (nm in intersect(c("mae", "rmse", "mape", "smape", "bias", "r_squared"), names(row))) {
      value <- as.numeric(row[[nm]][[1L]])
      if (!is.finite(value)) next
      idx <- idx + 1L
      diagnostics[[idx]] <- statistical_diagnostic(paste0("metric:", idx), "fit_metric", paste(row$split, row$metric, nm, sep = "/"), value, method_ref = "model_error_metrics")
    }
  }
  if (is.data.frame(validation$residual_diagnostics)) for (i in seq_len(nrow(validation$residual_diagnostics))) {
    row <- validation$residual_diagnostics[i, , drop = FALSE]
    for (nm in intersect(c("mean_residual", "residual_sd", "lag1_autocorrelation", "absolute_residual_fitted_correlation", "shapiro_wilk_p_value", "max_absolute_residual"), names(row))) {
      value <- as.numeric(row[[nm]][[1L]])
      if (!is.finite(value)) next
      idx <- idx + 1L
      diagnostics[[idx]] <- statistical_diagnostic(paste0("residual:", idx), "residual", paste(row$split, row$metric, nm, sep = "/"), value, p_value = if (nm == "shapiro_wilk_p_value") value else NULL, method_ref = "residual_diagnostics")
    }
  }
  model_ref <- if (is.character(validation$model) && length(validation$model)) validation$model[[1L]] else "model:validation-source"
  statistical_validation_bundle(
    paste0(validation$validation_id, "-diagnostics"), analysis_ref, model_ref = model_ref,
    diagnostics = diagnostics, source_status = validation$status,
    limitations = c("Source pass/fail threshold status is preserved as provenance and is not a scientific-validity certification."),
    provenance = list(source_type = "catalyst_model_validation", source_validation_id = validation$validation_id)
  )
}

#' Convert a policy regression into the v2.2 diagnostics contract
#' @param model A catalyst_policy_regression.
#' @param analysis_ref Optional analysis reference.
#' @return Statistical validation evidence bundle.
#' @export
statistical_validation_from_regression <- function(model, analysis_ref = NULL) {
  if (!inherits(model, "catalyst_policy_regression")) stop("`model` must be a catalyst_policy_regression.", call. = FALSE)
  if (is.null(analysis_ref)) analysis_ref <- model$id
  d <- model$diagnostics
  diagnostics <- list()
  idx <- 0L
  scalar_names <- intersect(c("n", "parameters", "df_residual", "rmse", "mae", "r_squared", "adjusted_r_squared", "residual_mean", "residual_sd", "durbin_watson", "condition_number"), names(d))
  for (nm in scalar_names) {
    value <- d[[nm]]
    if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) next
    idx <- idx + 1L
    diagnostics[[idx]] <- statistical_diagnostic(paste0("regression:", idx), if (grepl("residual|durbin", nm)) "residual" else "fit_metric", nm, value, method_ref = "fit_policy_regression")
  }
  if (is.list(d$breusch_pagan) && is.finite(d$breusch_pagan$statistic)) {
    idx <- idx + 1L
    diagnostics[[idx]] <- statistical_diagnostic(paste0("regression:", idx), "assumption_test", "Breusch-Pagan statistic", d$breusch_pagan$statistic, p_value = d$breusch_pagan$p_value, method_ref = "breusch_pagan")
  }
  if (is.list(d$residual_normality) && is.finite(d$residual_normality$statistic)) {
    idx <- idx + 1L
    diagnostics[[idx]] <- statistical_diagnostic(paste0("regression:", idx), "assumption_test", "Residual normality statistic", d$residual_normality$statistic, p_value = d$residual_normality$p_value, method_ref = d$residual_normality$method)
  }
  assumptions <- lapply(model$spec$assumptions, function(a) statistical_assumption(paste0("assumption:", a$id), a$label, a$statement, status = if (a$status == "required") "declared" else a$status, limitations = a$limitations))
  statistical_validation_bundle(
    paste0(model$id, "-diagnostics"), analysis_ref, model_ref = model$id,
    diagnostics = diagnostics, assumptions = assumptions,
    limitations = c("Regression diagnostics describe model behavior and assumptions; they do not establish causal identification or scientific validity."),
    provenance = list(source_type = "catalyst_policy_regression", covariance = model$covariance, fixed_effects = model$fixed_effects)
  )
}

#' Serialize a statistical validation bundle
#' @param x Statistical validation bundle.
#' @param path Optional output path.
#' @param pretty Pretty-print JSON.
#' @return JSON text or invisibly the path.
#' @export
statistical_validation_to_json <- function(x, path = NULL, pretty = TRUE) {
  validate_statistical_validation_bundle(x)
  .assert_flag(pretty, "pretty")
  text <- jsonlite::toJSON(unclass(x), auto_unbox = TRUE, null = "null", na = "null", pretty = pretty, digits = NA)
  if (is.null(path)) return(text)
  writeLines(text, path, useBytes = TRUE)
  invisible(path)
}

#' Deserialize a statistical validation bundle
#' @param json JSON text or path.
#' @return Statistical validation evidence bundle.
#' @export
statistical_validation_from_json <- function(json) {
  .assert_single_string(json, "json")
  text <- if (file.exists(json)) paste(readLines(json, warn = FALSE, encoding = "UTF-8"), collapse = "\n") else json
  x <- jsonlite::fromJSON(text, simplifyVector = FALSE)
  class(x) <- c("catalyst_statistical_validation_bundle", "list")
  validate_statistical_validation_bundle(x)
  x
}

#' @export
print.catalyst_statistical_validation_bundle <- function(x, ...) {
  cat(sprintf("<catalyst_statistical_validation_bundle %s>\n", x$id))
  cat(sprintf("  analysis: %s | diagnostics: %d | review: %s\n", x$analysis_ref, length(x$diagnostics), x$review_status))
  cat("  evidence only; human review required\n")
  invisible(x)
}
