.core_provider_contract_version <- function() "1.0.0"
.core_contract_ref <- function() "sc.core.analytical-runtime-provider.v1"

.core_provider_capabilities <- function() {
  list(
    scenario_simulation = list(category = "simulation", method_refs = c("run_catalyst_scenario", "run_scenarios"), input_types = c("scenario", "parameter_set"), output_types = c("analytical_result", "trajectory"), execution_status = "available"),
    uncertainty_analysis = list(category = "uncertainty", method_refs = c("run_uncertainty", "uncertainty_summary", "uncertainty_probabilities"), input_types = c("scenario", "uncertainty_spec"), output_types = c("analytical_result", "uncertainty"), execution_status = "available"),
    sensitivity_analysis = list(category = "uncertainty", method_refs = c("local_sensitivity", "global_sensitivity", "sensitivity_jacobian"), input_types = c("scenario", "uncertainty_run"), output_types = c("analytical_result", "sensitivity"), execution_status = "available"),
    econometrics = list(category = "statistics", method_refs = c("fit_policy_regression", "panel_regression"), input_types = c("dataset", "regression_spec"), output_types = c("analytical_result", "estimate", "diagnostic"), execution_status = "available"),
    causal_inference = list(category = "causal", method_refs = c("difference_in_differences", "event_study", "interrupted_time_series", "synthetic_control"), input_types = c("dataset", "causal_assumption"), output_types = c("analytical_result", "estimate", "diagnostic"), execution_status = "available"),
    policy_evaluation = list(category = "policy", method_refs = c("policy_evaluation_analysis", "policy_effect_summary"), input_types = c("econometric_evaluation", "causal_assumption"), output_types = c("analytical_result", "estimate", "evidence"), execution_status = "available"),
    forecasting = list(category = "prediction", method_refs = c("scenario_projection"), input_types = c("scenario", "model"), output_types = c("analytical_result", "projection"), execution_status = "projection_only", limitation = "v2.2.0 exposes governed scenario projection; generic statistical forecasting and calibration arrive in the predictive-runtime sequence."),
    model_validation = list(category = "validation", method_refs = c("validate_model_fit", "model_validation_analysis", "solver_benchmark", "stability_assessment"), input_types = c("model", "dataset", "scenario"), output_types = c("analytical_result", "diagnostic"), execution_status = "available"),
    climate_accounting = list(category = "sustainability", method_refs = c("climate_accounting"), input_types = c("dataset", "scenario"), output_types = c("analytical_result", "indicator"), execution_status = "available"),
    natural_capital = list(category = "sustainability", method_refs = c("natural_capital_account"), input_types = c("dataset", "capital_account"), output_types = c("analytical_result", "indicator"), execution_status = "available"),
    inclusive_wealth = list(category = "sustainability", method_refs = c("inclusive_wealth_account"), input_types = c("dataset", "capital_account"), output_types = c("analytical_result", "indicator"), execution_status = "available"),
    distribution_analysis = list(category = "distribution", method_refs = c("distributional_analysis", "intergenerational_analysis"), input_types = c("dataset"), output_types = c("analytical_result", "indicator", "diagnostic"), execution_status = "available")
  )
}

#' Platform Core analytical-provider manifest
#'
#' Returns the provider-side declaration consumed by Platform Core 3.1+ and
#' Workspace. Core owns analytical semantics and provenance binding; Workspace
#' owns execution. Catalyst Analytics R supplies the governed R methods.
#'
#' @return A provider manifest compatible with `sc.core.analytical-runtime-provider.v1`.
#' @export
catalyst_core_provider_manifest <- function() {
  caps <- .core_provider_capabilities()
  list(
    schema_version = .core_provider_contract_version(),
    provider_type = "core_analytical_runtime_provider",
    provider_key = "catalystanalyticsr",
    provider_version = .catalyst_package_version(),
    core_contract = .core_contract_ref(),
    diagnostics_contract = "sc.analytics-r.statistical-diagnostics-validation.v1",
    core_minimum_release = "3.2.0",
    core_registry_baseline_provider_version = "2.0.1",
    runtime = "r",
    execution_host = "workspace",
    transport_mode = "hosted",
    invocation_mode = "workspace-managed",
    capabilities = lapply(names(caps), function(key) c(list(capability_key = key), caps[[key]])),
    boundary = list(
      core_executes_provider = FALSE,
      workspace_controls_execution_environment = TRUE,
      arbitrary_function_dispatch = FALSE,
      runtime_execution_not_performed_by_transport_contract = TRUE,
      statistical_significance_not_inferred_by_core = TRUE,
      scientific_validity_not_certified_by_core = TRUE,
      human_review_required = TRUE
    )
  )
}

.core_visibility <- function(x) {
  match.arg(x, c("internal", "public"))
}

.core_request_identifier <- function(x, arg) {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$", x)) stop(sprintf("`%s` contains unsupported characters.", arg), call. = FALSE)
  x
}

#' Create a Platform Core analytical execution request
#'
#' @param request_key Stable Core request key.
#' @param analysis_type Declared provider capability.
#' @param input_refs Core/Workspace object references.
#' @param parameters Analytical parameters resolved by Workspace/provider code.
#' @param reproducibility Seed, snapshots, code references, or other reproducibility metadata.
#' @param method_ref Optional governed method reference.
#' @param session_ref Optional Core session reference.
#' @param external_execution_ref Optional Workspace execution reference.
#' @param provenance Provenance metadata.
#' @param visibility `internal` or `public`.
#' @return A `catalyst_core_analytical_request`.
#' @export
core_analytical_request <- function(request_key, analysis_type, input_refs = character(), parameters = list(), reproducibility = list(), method_ref = NULL, session_ref = NULL, external_execution_ref = NULL, provenance = list(), visibility = c("internal", "public")) {
  request_key <- .core_request_identifier(request_key, "request_key")
  .assert_single_string(analysis_type, "analysis_type")
  if (!is.character(input_refs) || anyNA(input_refs)) stop("`input_refs` must be a character vector.", call. = FALSE)
  if (!is.list(parameters) || !is.list(reproducibility) || !is.list(provenance)) stop("`parameters`, `reproducibility`, and `provenance` must be lists.", call. = FALSE)
  if (!is.null(method_ref)) .assert_single_string(method_ref, "method_ref")
  if (!is.null(session_ref)) .assert_single_string(session_ref, "session_ref")
  if (!is.null(external_execution_ref)) .assert_single_string(external_execution_ref, "external_execution_ref")
  visibility <- .core_visibility(visibility)
  x <- structure(list(
    schema_version = .core_provider_contract_version(),
    request_type = "sc.core.analytical-execution-request.v1",
    request_key = request_key,
    provider_ref = "catalystanalyticsr",
    provider_version = .catalyst_package_version(),
    analysis_type = analysis_type,
    method_ref = method_ref,
    runtime = "r",
    execution_host = "workspace",
    input_refs = unname(input_refs),
    parameters = parameters,
    reproducibility = reproducibility,
    session_ref = session_ref,
    external_execution_ref = external_execution_ref,
    status = "declared",
    visibility = visibility,
    provenance = provenance,
    submitted_at = .utc_now(),
    boundary = list(core_executes_provider = FALSE, workspace_executes_provider = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_core_analytical_request", "list"))
  validate_core_analytical_request(x)
  x
}

#' Normalize an existing Core request record
#'
#' Accepts the JSON-shaped request returned by Platform Core 3.1 and normalizes
#' it to the Catalyst Analytics R provider-side request contract.
#'
#' @param x Request list from Core.
#' @return A `catalyst_core_analytical_request`.
#' @export
as_core_analytical_request <- function(x) {
  if (!is.list(x)) stop("`x` must be a request list.", call. = FALSE)
  if (identical(x$request_type, "sc.core.analytical-execution-request.v1")) {
    class(x) <- c("catalyst_core_analytical_request", "list")
    validate_core_analytical_request(x)
    return(x)
  }
  out <- core_analytical_request(
    request_key = x$request_key,
    analysis_type = x$analysis_type,
    input_refs = if (is.null(x$input_refs)) character() else unlist(x$input_refs, use.names = FALSE),
    parameters = if (is.null(x$parameters)) list() else x$parameters,
    reproducibility = if (is.null(x$reproducibility)) list() else x$reproducibility,
    method_ref = x$method_ref,
    session_ref = x$session_ref,
    external_execution_ref = x$external_execution_ref,
    provenance = if (is.null(x$provenance)) list() else x$provenance,
    visibility = if (is.null(x$visibility)) "internal" else x$visibility
  )
  out
}

#' Validate a Core analytical request
#'
#' @param request Core analytical request.
#' @param require_executable Fail when the requested capability is declared but not fully executable in this release.
#' @return Invisibly `TRUE`.
#' @export
validate_core_analytical_request <- function(request, require_executable = FALSE) {
  if (!is.list(request)) stop("`request` must be a list.", call. = FALSE)
  .assert_flag(require_executable, "require_executable")
  required <- c("schema_version", "request_type", "request_key", "provider_ref", "analysis_type", "runtime", "execution_host", "input_refs", "parameters", "reproducibility", "visibility", "boundary")
  missing <- setdiff(required, names(request)); if (length(missing)) stop("Core request is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(request$schema_version, "1.0.0") || !identical(request$request_type, "sc.core.analytical-execution-request.v1")) stop("Unsupported Core analytical request contract.", call. = FALSE)
  if (!identical(request$provider_ref, "catalystanalyticsr")) stop("Core request targets a different analytical provider.", call. = FALSE)
  if (!identical(request$runtime, "r") || !identical(request$execution_host, "workspace")) stop("Catalyst Analytics R requires runtime=r and execution_host=workspace.", call. = FALSE)
  caps <- .core_provider_capabilities(); if (!request$analysis_type %in% names(caps)) stop("Unsupported analytical capability: ", request$analysis_type, call. = FALSE)
  if (!is.character(request$input_refs) || anyNA(request$input_refs)) stop("Core request input_refs must be character references.", call. = FALSE)
  if (!is.list(request$parameters) || !is.list(request$reproducibility)) stop("Core request parameters and reproducibility must be lists.", call. = FALSE)
  if (!request$visibility %in% c("internal", "public")) stop("Unsupported request visibility.", call. = FALSE)
  if (!isFALSE(request$boundary$core_executes_provider) || !isTRUE(request$boundary$workspace_executes_provider)) stop("Core/Workspace execution boundary is invalid.", call. = FALSE)
  if (isTRUE(require_executable) && identical(caps[[request$analysis_type]]$execution_status, "projection_only") && identical(request$analysis_type, "forecasting")) stop("Generic forecasting is not executable in v2.2.0; use scenario projection or the later predictive-runtime provider.", call. = FALSE)
  invisible(TRUE)
}

#' Resolve a governed execution plan for Workspace
#'
#' This does not run R code. It selects only from the package-maintained method
#' registry and returns the entrypoint candidates Workspace may invoke.
#'
#' @param request Core analytical request.
#' @return A governed execution plan.
#' @export
core_execution_plan <- function(request) {
  request <- as_core_analytical_request(request); validate_core_analytical_request(request)
  cap <- .core_provider_capabilities()[[request$analysis_type]]
  requested <- request$method_ref
  if (!is.null(requested) && !requested %in% cap$method_refs) stop("`method_ref` is not registered for the requested capability.", call. = FALSE)
  selected <- if (is.null(requested)) cap$method_refs[[1L]] else requested
  list(
    schema_version = "1.0.0", plan_type = "catalyst_analytics_r_core_execution_plan",
    request_key = request$request_key, provider_ref = "catalystanalyticsr", provider_version = .catalyst_package_version(),
    core_contract = .core_contract_ref(), runtime = "r", execution_host = "workspace",
    analysis_type = request$analysis_type, selected_method_ref = selected, allowed_method_refs = unname(cap$method_refs),
    execution_status = cap$execution_status, input_refs = request$input_refs,
    package_entrypoint = selected,
    boundary = list(arbitrary_function_dispatch = FALSE, plan_does_not_execute = TRUE, workspace_must_resolve_input_refs = TRUE, workspace_must_capture_environment = TRUE, human_review_required = TRUE)
  )
}

#' Build a Workspace execution envelope for a Core request
#'
#' @param request Core analytical request.
#' @param resource_policy Workspace resource-policy metadata.
#' @param environment Requested environment metadata.
#' @return A Workspace-hosted R execution envelope.
#' @export
workspace_core_execution_envelope <- function(request, resource_policy = list(), environment = list()) {
  request <- as_core_analytical_request(request); validate_core_analytical_request(request)
  if (!is.list(resource_policy) || !is.list(environment)) stop("`resource_policy` and `environment` must be lists.", call. = FALSE)
  plan <- core_execution_plan(request)
  list(
    schema_version = "1.0.0", envelope_type = "catalyst_workspace_core_analytical_execution",
    request_key = request$request_key, provider = catalyst_core_provider_manifest(), plan = plan,
    request = unclass(request), resource_policy = resource_policy,
    environment_request = utils::modifyList(list(capture_r_version = TRUE, capture_package_versions = TRUE, capture_lockfile_ref = TRUE, capture_container_ref = TRUE, capture_code_ref = TRUE), environment),
    return_contract = "catalyst_analytics_r_core_result@1.0.0",
    boundary = list(workspace_controls_execution = TRUE, workspace_controls_authentication = TRUE, workspace_controls_persistence = TRUE, package_does_not_queue_remote_jobs = TRUE, human_review_required = TRUE)
  )
}

#' Build a Core-compatible analytical result envelope
#'
#' @param request Core analytical request.
#' @param result_ref Stable result reference.
#' @param output_refs Result object references.
#' @param estimate_refs Estimate references.
#' @param uncertainty_refs Uncertainty references.
#' @param diagnostic_refs Diagnostic references.
#' @param artifact_refs Artifact references.
#' @param environment_ref Workspace runtime-environment reference.
#' @param external_execution_ref Workspace execution reference.
#' @param status Result status.
#' @param provenance Result provenance.
#' @param native_result Optional provider-native summary safe for JSON serialization.
#' @param warnings Warning strings.
#' @param errors Error strings.
#' @return A `catalyst_core_analytical_result`.
#' @export
core_analytical_result <- function(request, result_ref, output_refs = character(), estimate_refs = character(), uncertainty_refs = character(), diagnostic_refs = character(), artifact_refs = character(), environment_ref = NULL, external_execution_ref = NULL, status = c("recorded", "completed", "failed"), provenance = list(), native_result = NULL, warnings = character(), errors = character()) {
  request <- as_core_analytical_request(request); validate_core_analytical_request(request)
  result_ref <- .core_request_identifier(result_ref, "result_ref"); status <- match.arg(status)
  refs <- list(output_refs = output_refs, estimate_refs = estimate_refs, uncertainty_refs = uncertainty_refs, diagnostic_refs = diagnostic_refs, artifact_refs = artifact_refs)
  for (nm in names(refs)) if (!is.character(refs[[nm]]) || anyNA(refs[[nm]])) stop(sprintf("`%s` must be a character vector.", nm), call. = FALSE)
  if (!is.null(environment_ref)) .assert_single_string(environment_ref, "environment_ref")
  if (!is.null(external_execution_ref)) .assert_single_string(external_execution_ref, "external_execution_ref")
  if (!is.list(provenance)) stop("`provenance` must be a list.", call. = FALSE)
  if (!is.character(warnings) || anyNA(warnings) || !is.character(errors) || anyNA(errors)) stop("`warnings` and `errors` must be character vectors.", call. = FALSE)
  x <- structure(list(
    schema_version = "1.0.0", result_type = "catalyst_analytics_r_core_result",
    core_contract = .core_contract_ref(), request_ref = request$request_key, request_key = request$request_key,
    result_ref = result_ref, provider_ref = "catalystanalyticsr", provider_version = .catalyst_package_version(),
    runtime = "r", execution_host = "workspace", analysis_type = request$analysis_type, method_ref = request$method_ref,
    external_execution_ref = if (is.null(external_execution_ref)) request$external_execution_ref else external_execution_ref,
    environment_ref = environment_ref, status = status,
    output_refs = unname(output_refs), estimate_refs = unname(estimate_refs), uncertainty_refs = unname(uncertainty_refs), diagnostic_refs = unname(diagnostic_refs), artifact_refs = unname(artifact_refs),
    native_result = if (is.null(native_result)) list() else .safe_json_value(native_result), warnings = unname(warnings), errors = unname(errors),
    provenance = utils::modifyList(list(package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), core_contract = .core_contract_ref()), provenance),
    completed_at = .utc_now(),
    boundary = list(core_records_result_but_does_not_execute = TRUE, workspace_execution_required = TRUE, result_does_not_certify_scientific_validity = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_core_analytical_result", "list"))
  validate_core_analytical_result(x); x
}

#' Validate a Core-compatible analytical result
#'
#' @param result Analytical result envelope.
#' @return Invisibly `TRUE`.
#' @export
validate_core_analytical_result <- function(result) {
  if (!is.list(result)) stop("`result` must be a list.", call. = FALSE)
  required <- c("schema_version", "result_type", "core_contract", "request_ref", "result_ref", "provider_ref", "provider_version", "runtime", "execution_host", "analysis_type", "status", "output_refs", "estimate_refs", "uncertainty_refs", "diagnostic_refs", "artifact_refs", "provenance", "boundary")
  missing <- setdiff(required, names(result)); if (length(missing)) stop("Core result is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(result$schema_version, "1.0.0") || !identical(result$result_type, "catalyst_analytics_r_core_result")) stop("Unsupported Core analytical result contract.", call. = FALSE)
  if (!identical(result$core_contract, .core_contract_ref()) || !identical(result$provider_ref, "catalystanalyticsr") || !identical(result$runtime, "r") || !identical(result$execution_host, "workspace")) stop("Core analytical result provider/runtime boundary mismatch.", call. = FALSE)
  if (!result$status %in% c("recorded", "completed", "failed")) stop("Unsupported result status.", call. = FALSE)
  for (nm in c("output_refs", "estimate_refs", "uncertainty_refs", "diagnostic_refs", "artifact_refs")) if (!is.character(result[[nm]]) || anyNA(result[[nm]])) stop(sprintf("Result `%s` must be character references.", nm), call. = FALSE)
  if (!isTRUE(result$boundary$core_records_result_but_does_not_execute) || !isTRUE(result$boundary$workspace_execution_required)) stop("Core result boundary is invalid.", call. = FALSE)
  invisible(TRUE)
}

#' Serialize a Core request to JSON
#' @param request Core analytical request.
#' @param path Optional path.
#' @param pretty Pretty-print JSON.
#' @return JSON text or invisibly the path.
#' @export
core_request_to_json <- function(request, path = NULL, pretty = TRUE) {
  request <- as_core_analytical_request(request); validate_core_analytical_request(request); .assert_flag(pretty, "pretty")
  text <- jsonlite::toJSON(.safe_json_value(unclass(request)), auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (is.null(path)) return(as.character(text)); .assert_single_string(path, "path"); dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE); writeLines(as.character(text), path, useBytes = TRUE); invisible(path)
}

#' Restore a Core request from JSON
#' @param json JSON text or path.
#' @return A validated request.
#' @export
core_request_from_json <- function(json) {
  .assert_single_string(json, "json"); text <- if (!grepl("^[[:space:]]*\\{", json) && file.exists(json)) paste(readLines(json, warn = FALSE, encoding = "UTF-8"), collapse = "\n") else json
  x <- jsonlite::fromJSON(text, simplifyVector = FALSE); x$input_refs <- unlist(x$input_refs, use.names = FALSE); class(x) <- c("catalyst_core_analytical_request", "list"); validate_core_analytical_request(x); x
}

#' Serialize a Core analytical result to JSON
#' @param result Core analytical result.
#' @param path Optional path.
#' @param pretty Pretty-print JSON.
#' @return JSON text or invisibly the path.
#' @export
core_result_to_json <- function(result, path = NULL, pretty = TRUE) {
  validate_core_analytical_result(result); .assert_flag(pretty, "pretty")
  text <- jsonlite::toJSON(.safe_json_value(unclass(result)), auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (is.null(path)) return(as.character(text)); .assert_single_string(path, "path"); dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE); writeLines(as.character(text), path, useBytes = TRUE); invisible(path)
}

#' Restore a Core analytical result from JSON
#' @param json JSON text or path.
#' @return A validated analytical result.
#' @export
core_result_from_json <- function(json) {
  .assert_single_string(json, "json"); text <- if (!grepl("^[[:space:]]*\\{", json) && file.exists(json)) paste(readLines(json, warn = FALSE, encoding = "UTF-8"), collapse = "\n") else json
  x <- jsonlite::fromJSON(text, simplifyVector = FALSE)
  as_character_refs <- function(value) { if (is.null(value) || !length(value)) character() else as.character(unlist(value, use.names = FALSE)) }
  for (nm in c("output_refs", "estimate_refs", "uncertainty_refs", "diagnostic_refs", "artifact_refs", "warnings", "errors")) x[[nm]] <- as_character_refs(x[[nm]])
  class(x) <- c("catalyst_core_analytical_result", "list"); validate_core_analytical_result(x); x
}

#' @export
print.catalyst_core_analytical_request <- function(x, ...) { cat(sprintf("<catalyst_core_analytical_request %s> %s via Workspace/R\n", x$request_key, x$analysis_type)); invisible(x) }
#' @export
print.catalyst_core_analytical_result <- function(x, ...) { cat(sprintf("<catalyst_core_analytical_result %s> %s [%s]\n", x$result_ref, x$analysis_type, x$status)); invisible(x) }
