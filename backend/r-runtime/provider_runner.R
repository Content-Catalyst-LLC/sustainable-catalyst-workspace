args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("expected input and output JSON paths")
input_path <- args[[1]]
output_path <- args[[2]]

`%||%` <- function(x, y) if (is.null(x)) y else x

fail <- function(message) {
  stop(as.character(message), call. = FALSE)
}

safe_scalar <- function(x, label, max_chars = 512L) {
  if (!is.character(x) || length(x) != 1L || is.na(x) || !nzchar(x) || nchar(x, type = "bytes") > max_chars) {
    fail(paste(label, "must be one bounded non-empty string"))
  }
  x
}

safe_jsonable <- function(x) {
  jsonlite::fromJSON(jsonlite::toJSON(x, auto_unbox = TRUE, null = "null", na = "null", digits = NA), simplifyVector = FALSE)
}

provider_manifest <- catalystanalyticsr::catalyst_core_provider_manifest()

EXECUTABLE_METHODS <- c(
  "run_catalyst_scenario",
  "run_scenarios",
  "run_uncertainty",
  "uncertainty_summary",
  "uncertainty_probabilities",
  "local_sensitivity",
  "global_sensitivity",
  "sensitivity_jacobian",
  "fit_policy_regression",
  "panel_regression",
  "difference_in_differences",
  "event_study",
  "interrupted_time_series",
  "synthetic_control",
  "policy_evaluation_analysis",
  "policy_effect_summary",
  "validate_model_fit",
  "model_validation_analysis",
  "solver_benchmark",
  "stability_assessment",
  "climate_accounting",
  "natural_capital_account",
  "inclusive_wealth_account",
  "distributional_analysis",
  "intergenerational_analysis"
)

resolve_method <- function(name) {
  name <- safe_scalar(name, "selected_method_ref", 128L)
  if (!(name %in% EXECUTABLE_METHODS)) {
    fail(paste("provider method is not executable through Workspace v3.5.0:", name))
  }
  getExportedValue("catalystanalyticsr", name)
}

build_environment <- function() {
  deps <- c("catalystanalyticsr", "ggplot2", "rlang", "jsonlite")
  versions <- lapply(deps, function(pkg) {
    if (!requireNamespace(pkg, quietly = TRUE)) return(NULL)
    as.character(utils::packageVersion(pkg))
  })
  names(versions) <- deps
  versions <- versions[!vapply(versions, is.null, logical(1))]
  list(
    r_version = paste(R.version$major, R.version$minor, sep = "."),
    platform = R.version$platform,
    package_versions = versions,
    provider_ref = provider_manifest$provider_key,
    provider_version = provider_manifest$provider_version,
    core_contract = provider_manifest$core_contract,
    workspace_adapter_version = "3.5.0",
    read_only_runtime_expected = TRUE
  )
}

doc <- jsonlite::fromJSON(input_path, simplifyVector = TRUE, simplifyDataFrame = TRUE)
if (!is.list(doc)) fail("provider envelope must be a JSON object")

action <- as.character(doc$action %||% "validate")
if (!(action %in% c("manifest", "validate", "execute"))) fail("unsupported provider adapter action")

if (identical(action, "manifest")) {
  out <- list(
    ok = TRUE,
    schema = "sc-workspace-catalyst-analytics-r-provider-adapter/1.0",
    workspace_version = "3.5.0",
    action = "manifest",
    provider = provider_manifest,
    executable_method_refs = unname(EXECUTABLE_METHODS),
    environment = build_environment(),
    boundary = list(
      workspace_controls_execution = TRUE,
      arbitrary_function_dispatch = FALSE,
      arbitrary_code_execution = FALSE,
      client_supplied_packages_allowed = FALSE,
      client_supplied_runtime_urls_allowed = FALSE,
      human_review_required = TRUE
    )
  )
  jsonlite::write_json(out, output_path, auto_unbox = TRUE, digits = 15, na = "null", null = "null", pretty = FALSE)
  quit(save = "no", status = 0)
}

if (!identical(doc$envelope_type, "catalyst_workspace_core_analytical_execution")) {
  fail("unsupported Catalyst Analytics R Workspace envelope")
}
if (!is.list(doc$request)) fail("provider envelope request must be an object")
if (!is.list(doc$plan)) fail("provider envelope plan must be an object")
if (!is.list(doc$boundary) || !isTRUE(doc$boundary$workspace_controls_execution)) {
  fail("Workspace execution boundary is required")
}

request <- catalystanalyticsr::as_core_analytical_request(doc$request)
catalystanalyticsr::validate_core_analytical_request(request)
plan <- catalystanalyticsr::core_execution_plan(request)

if (!identical(plan$provider_ref, "catalystanalyticsr") ||
    !identical(plan$core_contract, "sc.core.analytical-runtime-provider.v1") ||
    !identical(plan$runtime, "r") ||
    !identical(plan$execution_host, "workspace")) {
  fail("provider execution plan boundary mismatch")
}
if (!is.null(doc$plan$selected_method_ref) && !identical(as.character(doc$plan$selected_method_ref), as.character(plan$selected_method_ref))) {
  fail("submitted plan does not match provider-governed method selection")
}

base <- list(
  ok = TRUE,
  schema = "sc-workspace-catalyst-analytics-r-provider-adapter/1.0",
  workspace_version = "3.5.0",
  action = action,
  request_key = request$request_key,
  provider = provider_manifest,
  plan = plan,
  environment = build_environment(),
  boundary = list(
    workspace_controls_execution = TRUE,
    workspace_controls_authentication = TRUE,
    workspace_controls_persistence = TRUE,
    arbitrary_function_dispatch = FALSE,
    arbitrary_code_execution = FALSE,
    client_supplied_packages_allowed = FALSE,
    client_supplied_runtime_urls_allowed = FALSE,
    provider_does_not_queue_remote_jobs = TRUE,
    human_review_required = TRUE
  )
)

if (identical(action, "validate")) {
  base$validated <- TRUE
  jsonlite::write_json(base, output_path, auto_unbox = TRUE, digits = 15, na = "null", null = "null", pretty = FALSE)
  quit(save = "no", status = 0)
}

if (!identical(plan$execution_status, "available")) {
  fail(paste("provider capability is not executable in Catalyst Analytics R v2.1.0:", request$analysis_type))
}
method_ref <- as.character(plan$selected_method_ref)
request$method_ref <- method_ref
fun <- resolve_method(method_ref)
method_args <- doc$resolved_method_args %||% list()
if (!is.list(method_args)) fail("resolved_method_args must be an object")
if (length(method_args) > 64L) fail("resolved_method_args exceeds the Workspace bound")
if (is.null(names(method_args)) || any(!nzchar(names(method_args)))) fail("resolved_method_args must use named arguments")

started <- format(Sys.time(), tz = "UTC", usetz = TRUE)
native_result <- tryCatch(
  do.call(fun, method_args),
  error = function(e) fail(paste("Catalyst Analytics R method failed:", conditionMessage(e)))
)
completed <- format(Sys.time(), tz = "UTC", usetz = TRUE)

execution_ref <- as.character(doc$external_execution_ref %||% request$external_execution_ref %||% paste0("workspace-analytics-r:", request$request_key))
result_ref <- as.character(doc$result_ref %||% paste0("analytics-r-result:", request$request_key))

core_result <- catalystanalyticsr::core_analytical_result(
  request = request,
  result_ref = result_ref,
  external_execution_ref = execution_ref,
  environment_ref = as.character(doc$environment_ref %||% paste0("workspace-r-env:", request$request_key)),
  status = "completed",
  native_result = native_result,
  provenance = list(
    workspace = list(
      adapter_version = "3.5.0",
      execution_started_at = started,
      execution_completed_at = completed,
      selected_method_ref = method_ref
    )
  )
)

base$executed <- TRUE
base$selected_method_ref <- method_ref
base$core_result <- unclass(core_result)
base$native_result <- safe_jsonable(native_result)
base$external_execution_ref <- execution_ref
base$completed_at <- completed

jsonlite::write_json(base, output_path, auto_unbox = TRUE, digits = 15, na = "null", null = "null", pretty = FALSE)
