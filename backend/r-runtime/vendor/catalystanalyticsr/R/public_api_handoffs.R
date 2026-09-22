.catalyst_public_api_schema_version <- function() "1.0.0"
.catalyst_platform_handoff_schema_version <- function() "1.0.0"

.api_identifier <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", x)) {
    stop(sprintf("`%s` must use letters, numbers, dots, underscores, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

#' Define a public API endpoint
#'
#' @param id Stable endpoint identifier.
#' @param method HTTP-style method label.
#' @param path Versioned route path.
#' @param title Human-readable endpoint title.
#' @param description Endpoint purpose.
#' @param request_schema Request contract identifier.
#' @param response_schema Response contract identifier.
#' @param access Access classification.
#' @param side_effects Whether the endpoint can mutate durable state.
#' @return A governed API endpoint record.
#' @export
api_endpoint <- function(id, method, path, title, description = "", request_schema = NULL,
                         response_schema = "catalyst_api_response@1.0.0",
                         access = c("public", "authenticated", "institutional"),
                         side_effects = FALSE) {
  .api_identifier(id, "id")
  method <- toupper(method)
  if (!method %in% c("GET", "POST")) stop("`method` must be GET or POST.", call. = FALSE)
  .assert_single_string(path, "path")
  if (!grepl("^/v1/", path)) stop("Public API paths must begin with `/v1/`.", call. = FALSE)
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.null(request_schema)) .assert_single_string(request_schema, "request_schema")
  .assert_single_string(response_schema, "response_schema")
  access <- match.arg(access)
  .assert_flag(side_effects, "side_effects")
  list(
    schema_version = "1.0.0", id = id, method = method, path = path, title = title,
    description = description, request_schema = request_schema,
    response_schema = response_schema, access = access, side_effects = side_effects
  )
}

.public_api_endpoints <- function() {
  list(
    health = api_endpoint("health", "GET", "/v1/health", "Package health", "Return package and contract status."),
    contracts_list = api_endpoint("contracts.list", "GET", "/v1/contracts", "Contract manifest", "List supported public contracts."),
    models_list = api_endpoint("models.list", "GET", "/v1/models", "Model registry", "List registered analytical models."),
    indicators_list = api_endpoint("indicators.list", "GET", "/v1/indicators", "Indicator registry", "List governed indicator definitions."),
    scenario_validate = api_endpoint("scenario.validate", "POST", "/v1/scenarios/validate", "Validate scenario", "Validate a canonical scenario without executing it.", "catalyst_scenario@1.0.0"),
    scenario_run = api_endpoint("scenario.run", "POST", "/v1/scenarios/run", "Run scenario", "Execute a canonical scenario with the registered R model.", "catalyst_scenario_run_request@1.0.0", access = "authenticated"),
    project_manifest = api_endpoint("project.manifest", "POST", "/v1/projects/manifest", "Project manifest", "Return a reproducibility manifest for a supplied project.", "catalyst_project@1.0.0"),
    workspace_manifest = api_endpoint("workspace.manifest", "POST", "/v1/workspaces/manifest", "Workspace manifest", "Return a manifest for a supplied workspace.", "catalyst_workspace@1.0.0"),
    handoff_build = api_endpoint("handoff.build", "POST", "/v1/handoffs", "Build platform handoff", "Build a governed first-party platform handoff.", "catalyst_platform_handoff_request@1.0.0", access = "authenticated"),
    core_provider = api_endpoint("core.provider", "GET", "/v1/core/provider", "Platform Core provider manifest", "Return the governed Catalyst Analytics R provider contract for Platform Core 3.1+."),
    core_request_validate = api_endpoint("core.request.validate", "POST", "/v1/core/requests/validate", "Validate Platform Core request", "Validate and normalize a Platform Core analytical execution request.", "catalyst_analytics_r_core_request@1.0.0", access = "authenticated")
  )
}

#' Public API manifest
#'
#' @return Versioned endpoint, contract, and boundary declaration.
#' @export
catalyst_public_api_manifest <- function() {
  endpoints <- .public_api_endpoints()
  list(
    schema_version = .catalyst_public_api_schema_version(),
    api_version = "v1", package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    base_path = "/v1", endpoints = endpoints,
    contracts = list(
      request = "catalyst_api_request@1.0.0", response = "catalyst_api_response@1.0.0",
      platform_handoff = "catalyst_platform_handoff@1.0.0",
      scenario = "catalyst_scenario@1.0.0", project = "catalyst_project@1.0.0",
      workspace = "catalyst_workspace@1.0.0",
      core_provider = "catalyst_analytics_r_core_provider@1.0.0", core_request = "catalyst_analytics_r_core_request@1.0.0", core_result = "catalyst_analytics_r_core_result@1.0.0"
    ),
    guarantees = list(
      additive_minor_releases = TRUE, explicit_contract_versions = TRUE,
      deterministic_validation = TRUE, read_only_discovery = TRUE,
      durable_mutation_endpoints = FALSE
    ),
    boundary = list(
      transport_server_not_included = TRUE,
      authentication_implemented_by_host_platform = TRUE,
      rate_limiting_implemented_by_host_platform = TRUE,
      human_review_required_for_publication_and_decisions = TRUE
    )
  )
}

#' Create a public API request envelope
#'
#' @param endpoint Endpoint identifier.
#' @param payload Request payload.
#' @param request_id Optional request identifier.
#' @param actor Actor metadata.
#' @param context Request context and provenance.
#' @return A `catalyst_api_request`.
#' @export
api_request <- function(endpoint, payload = list(), request_id = NULL, actor = list(), context = list()) {
  .api_identifier(endpoint, "endpoint")
  endpoints <- .public_api_endpoints()
  matches <- vapply(endpoints, function(entry) identical(entry$id, endpoint), logical(1))
  if (!any(matches)) stop("Unknown public API endpoint.", call. = FALSE)
  if (!is.list(payload)) stop("`payload` must be a list.", call. = FALSE)
  if (!is.list(actor) || !is.list(context)) stop("`actor` and `context` must be lists.", call. = FALSE)
  submitted_at <- .utc_now()
  if (is.null(request_id)) request_id <- paste0("req-", substr(.project_hash(list(endpoint = endpoint, payload = payload, submitted_at = submitted_at)), 1L, 20L))
  .api_identifier(request_id, "request_id")
  result <- structure(list(
    schema_version = "1.0.0", request_type = "catalyst_public_api_request",
    request_id = request_id, endpoint = endpoint, payload = payload,
    actor = actor, context = context, submitted_at = submitted_at
  ), class = c("catalyst_api_request", "list"))
  validate_api_request(result)
  result
}

#' Validate a public API request
#'
#' @param request API request record.
#' @return Invisibly returns `TRUE`.
#' @export
validate_api_request <- function(request) {
  if (!is.list(request)) stop("`request` must be a list.", call. = FALSE)
  required <- c("schema_version", "request_type", "request_id", "endpoint", "payload", "actor", "context", "submitted_at")
  missing <- setdiff(required, names(request))
  if (length(missing)) stop("API request is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(request$schema_version, "1.0.0") || !identical(request$request_type, "catalyst_public_api_request")) stop("Unsupported API request contract.", call. = FALSE)
  .api_identifier(request$request_id, "request$request_id"); .api_identifier(request$endpoint, "request$endpoint")
  endpoints <- vapply(.public_api_endpoints(), function(entry) entry$id, character(1))
  if (!request$endpoint %in% endpoints) stop("Unknown public API endpoint.", call. = FALSE)
  if (!is.list(request$payload) || !is.list(request$actor) || !is.list(request$context)) stop("API request payload, actor, and context must be lists.", call. = FALSE)
  .assert_single_string(request$submitted_at, "request$submitted_at")
  invisible(TRUE)
}

#' Create a public API response envelope
#'
#' @param request API request or request identifier.
#' @param data Response data.
#' @param status Response status.
#' @param warnings Warning messages.
#' @param errors Error messages.
#' @return A `catalyst_api_response`.
#' @export
api_response <- function(request, data = list(), status = c("ok", "accepted", "error"), warnings = character(), errors = character()) {
  status <- match.arg(status)
  if (is.list(request)) { validate_api_request(request); request_id <- request$request_id; endpoint <- request$endpoint } else {
    .api_identifier(request, "request"); request_id <- request; endpoint <- "unknown"
  }
  if (!is.character(warnings) || anyNA(warnings) || !is.character(errors) || anyNA(errors)) stop("`warnings` and `errors` must be character vectors.", call. = FALSE)
  result <- structure(list(
    schema_version = "1.0.0", response_type = "catalyst_public_api_response",
    request_id = request_id, endpoint = endpoint, status = status,
    data = .safe_json_value(data), warnings = unname(warnings), errors = unname(errors),
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    completed_at = .utc_now(),
    boundary = list(human_review_required = TRUE, automated_publication = FALSE, automated_decision_authorization = FALSE)
  ), class = c("catalyst_api_response", "list"))
  validate_api_response(result)
  result
}

#' Validate a public API response
#'
#' @param response API response record.
#' @return Invisibly returns `TRUE`.
#' @export
validate_api_response <- function(response) {
  if (!is.list(response)) stop("`response` must be a list.", call. = FALSE)
  required <- c("schema_version", "response_type", "request_id", "endpoint", "status", "data", "warnings", "errors", "package", "completed_at", "boundary")
  missing <- setdiff(required, names(response))
  if (length(missing)) stop("API response is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(response$schema_version, "1.0.0") || !identical(response$response_type, "catalyst_public_api_response")) stop("Unsupported API response contract.", call. = FALSE)
  if (!response$status %in% c("ok", "accepted", "error")) stop("Invalid API response status.", call. = FALSE)
  if (!is.character(response$warnings) || !is.character(response$errors)) stop("API response warnings and errors must be character vectors.", call. = FALSE)
  invisible(TRUE)
}

#' Dispatch an in-process public API request
#'
#' @param request API request.
#' @param stop_on_error Throw endpoint errors instead of returning an error response.
#' @return A `catalyst_api_response`.
#' @export
dispatch_api_request <- function(request, stop_on_error = FALSE) {
  validate_api_request(request); .assert_flag(stop_on_error, "stop_on_error")
  execute <- function() {
    payload <- request$payload
    switch(request$endpoint,
      health = list(status = "ok", package_version = .catalyst_package_version(), api_version = "v1", checked_at = .utc_now()),
      contracts.list = catalyst_public_api_manifest(),
      models.list = list_catalyst_models(),
      indicators.list = list_catalyst_indicators(),
      scenario.validate = { scenario <- as_catalyst_scenario(payload$scenario); list(valid = TRUE, scenario_id = scenario$id, fingerprint = scenario_fingerprint(scenario), schema_version = scenario$schema_version) },
      scenario.run = {
        scenario <- as_catalyst_scenario(payload$scenario)
        method <- if (is.null(payload$method)) NULL else payload$method
        run <- run_catalyst_scenario(scenario, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE)
        list(run_id = paste0("run-", substr(run$meta$scenario_fingerprint, 1L, 16L)), scenario_id = scenario$id, model = run$meta$model, method = run$meta$method, indicators = run$indicators, trajectory = run$trajectory_wide, provenance = run$meta)
      },
      project.manifest = project_manifest(payload$project),
      workspace.manifest = workspace_manifest(payload$workspace),
      handoff.build = platform_handoff(payload$project, payload$target, options = if (is.null(payload$options)) list() else payload$options),
      core.provider = catalyst_core_provider_manifest(),
      core.request.validate = { normalized <- as_core_analytical_request(payload$request); list(valid = TRUE, request = unclass(normalized), execution_plan = core_execution_plan(normalized)) },
      stop("Unsupported public API endpoint.", call. = FALSE)
    )
  }
  value <- tryCatch(execute(), error = function(error) error)
  if (inherits(value, "error")) {
    if (stop_on_error) stop(conditionMessage(value), call. = FALSE)
    return(api_response(request, data = list(), status = "error", errors = conditionMessage(value)))
  }
  api_response(request, data = value, status = "ok")
}

.platform_common <- function(project, target, handoff_type, title, payload, boundary, review = list(status = "requires_review", human_reviewer_required = TRUE)) {
  validate_catalyst_project(project)
  .assert_single_string(target, "target"); .assert_single_string(handoff_type, "handoff_type"); .assert_single_string(title, "title")
  result <- structure(list(
    schema_version = .catalyst_platform_handoff_schema_version(), handoff_type = handoff_type,
    target = target, project_id = project$id, project_fingerprint = project_fingerprint(project),
    title = title, payload = .safe_json_value(payload),
    provenance = list(package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), environment = project$environment, project_snapshot_count = length(project$snapshots)),
    review = review, boundary = boundary, created_at = .utc_now(), package_version = .catalyst_package_version()
  ), class = c("catalyst_platform_handoff", "list"))
  validate_platform_handoff(result)
  result
}

#' Build a Site Intelligence data handoff
#'
#' @param project A project.
#' @param dataset_ids Dataset identifiers. `NULL` includes all datasets.
#' @param indicators Requested indicator identifiers.
#' @param refresh_policy Data refresh policy.
#' @return Governed Site Intelligence handoff.
#' @export
site_intelligence_handoff <- function(project, dataset_ids = NULL, indicators = character(), refresh_policy = c("pinned_snapshot", "latest_approved")) {
  validate_catalyst_project(project); refresh_policy <- match.arg(refresh_policy)
  if (is.null(dataset_ids)) dataset_ids <- names(project$datasets)
  if (!is.character(dataset_ids) || anyNA(dataset_ids)) stop("`dataset_ids` must be a character vector.", call. = FALSE)
  unknown <- setdiff(dataset_ids, names(project$datasets)); if (length(unknown)) stop("Unknown project datasets: ", paste(unknown, collapse = ", "), call. = FALSE)
  if (!is.character(indicators) || anyNA(indicators)) stop("`indicators` must be a character vector.", call. = FALSE)
  datasets <- lapply(project$datasets[dataset_ids], dataset_manifest)
  .platform_common(project, "site_intelligence", "site_intelligence_data_request", paste0(project$title, " - Site Intelligence data request"),
    list(datasets = datasets, requested_indicators = unname(indicators), refresh_policy = refresh_policy, scope = project$scope),
    list(source_licenses_must_be_preserved = TRUE, refresh_requires_approved_snapshot = TRUE, external_data_not_treated_as_validated_model_evidence = TRUE, human_review_required = TRUE))
}

#' Build a Research Lab compute handoff
#'
#' @param project A project.
#' @param job_type Compute job type.
#' @param scenario_ids Scenario identifiers. `NULL` includes all scenarios.
#' @param resources Requested resource metadata.
#' @return Governed Research Lab handoff.
#' @export
research_lab_handoff <- function(project, job_type = c("calibration", "uncertainty", "batch_simulation", "benchmark"), scenario_ids = NULL, resources = list()) {
  validate_catalyst_project(project); job_type <- match.arg(job_type)
  if (is.null(scenario_ids)) scenario_ids <- names(project$scenarios)
  if (!is.character(scenario_ids) || anyNA(scenario_ids)) stop("`scenario_ids` must be a character vector.", call. = FALSE)
  unknown <- setdiff(scenario_ids, names(project$scenarios)); if (length(unknown)) stop("Unknown project scenarios: ", paste(unknown, collapse = ", "), call. = FALSE)
  if (!is.list(resources)) stop("`resources` must be a list.", call. = FALSE)
  .platform_common(project, "research_lab", "research_lab_compute_request", paste0(project$title, " - Research Lab compute request"),
    list(job_type = job_type, scenarios = lapply(project$scenarios[scenario_ids], unclass), models = project$models, parameter_sets = project$parameter_sets, resources = resources, return_contract = "catalyst_research_lab_result@1.0.0"),
    list(compute_result_requires_validation = TRUE, failed_jobs_must_be_reported = TRUE, returned_results_not_automatically_accepted = TRUE, human_review_required = TRUE))
}

#' Build a Workbench formula handoff
#'
#' @param project A project.
#' @param formulas Named formula records.
#' @param calculators Optional calculator definitions.
#' @return Governed Workbench handoff.
#' @export
workbench_handoff <- function(project, formulas = list(), calculators = list()) {
  validate_catalyst_project(project)
  if (!is.list(formulas) || !is.list(calculators)) stop("`formulas` and `calculators` must be lists.", call. = FALSE)
  .platform_common(project, "workbench", "workbench_formula_package", paste0(project$title, " - Workbench formula package"),
    list(formulas = formulas, calculators = calculators, parameter_sets = project$parameter_sets, indicators = project$indicators, scope = project$scope),
    list(formulas_require_unit_validation = TRUE, calculators_are_not_model_validation = TRUE, symbolic_results_require_domain_review = TRUE, human_review_required = TRUE))
}

#' Build a Catalyst Canvas assumptions handoff
#'
#' @param project A project.
#' @param objectives Optional objectives.
#' @param stakeholders Optional stakeholder records.
#' @return Governed Catalyst Canvas handoff.
#' @export
catalyst_canvas_handoff <- function(project, objectives = list(), stakeholders = list()) {
  validate_catalyst_project(project)
  if (!is.list(objectives) || !is.list(stakeholders)) stop("`objectives` and `stakeholders` must be lists.", call. = FALSE)
  assumptions <- unlist(lapply(project$scenarios, function(scenario) scenario$assumptions), recursive = FALSE)
  constraints <- unlist(lapply(project$scenarios, function(scenario) scenario$constraints), recursive = FALSE)
  .platform_common(project, "catalyst_canvas", "catalyst_canvas_assumption_package", paste0(project$title, " - Canvas assumptions package"),
    list(question = project$description, scope = project$scope, objectives = objectives, stakeholders = stakeholders, assumptions = assumptions, constraints = constraints, evidence_gaps = project$notes),
    list(canvas_does_not_validate_assumptions = TRUE, evidence_gaps_require_review = TRUE, strategic_framing_not_decision_authority = TRUE, human_review_required = TRUE))
}

#' Build a Workspace runtime handoff
#'
#' Creates a governed request for Sustainable Catalyst Workspace to host an R
#' execution using Catalyst Analytics R. The package does not execute or queue
#' the remote job itself; Workspace remains responsible for runtime isolation,
#' resource policy, authentication, persistence, and job lifecycle management.
#'
#' @param project A project.
#' @param runtime Runtime language identifier.
#' @param provider Analytical provider identifier.
#' @param resources Requested runtime resource metadata.
#' @param execution_policy Workspace execution-policy metadata.
#' @return Governed Workspace runtime handoff.
#' @export
workspace_handoff <- function(project, runtime = "r", provider = "catalystanalyticsr", resources = list(), execution_policy = list()) {
  validate_catalyst_project(project)
  .assert_single_string(runtime, "runtime"); .assert_single_string(provider, "provider")
  if (!is.list(resources) || !is.list(execution_policy)) stop("`resources` and `execution_policy` must be lists.", call. = FALSE)
  .platform_common(project, "workspace", "workspace_runtime_request", paste0(project$title, " - Workspace R runtime request"),
    list(
      project = project_manifest(project),
      runtime = list(language = runtime, provider = provider, provider_version = .catalyst_package_version()),
      resources = resources,
      execution_policy = execution_policy,
      return_contract = "catalyst_workspace_execution_result@1.0.0"
    ),
    list(
      workspace_controls_execution_environment = TRUE,
      runtime_execution_not_performed_by_package = TRUE,
      returned_results_require_validation = TRUE,
      durable_storage_and_authentication_by_host = TRUE,
      human_review_required = TRUE
    ))
}

#' Build a first-party Sustainable Catalyst handoff
#'
#' @param project A project.
#' @param target Target product.
#' @param options Target-specific options.
#' @return A governed platform handoff.
#' @export
platform_handoff <- function(project, target = c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library", "workspace"), options = list()) {
  validate_catalyst_project(project); target <- match.arg(target)
  if (!is.list(options)) stop("`options` must be a list.", call. = FALSE)
  call_with <- function(fun) do.call(fun, c(list(project = project), options))
  result <- switch(target,
    site_intelligence = call_with(site_intelligence_handoff),
    research_lab = call_with(research_lab_handoff),
    workbench = call_with(workbench_handoff),
    catalyst_canvas = call_with(catalyst_canvas_handoff),
    decision_studio = decision_studio_handoff(project),
    knowledge_library = knowledge_library_handoff(project),
    workspace = call_with(workspace_handoff)
  )
  validate_platform_handoff(result)
  result
}

#' Validate a platform handoff
#'
#' @param handoff Platform handoff record.
#' @return Invisibly returns `TRUE`.
#' @export
validate_platform_handoff <- function(handoff) {
  if (!is.list(handoff)) stop("`handoff` must be a list.", call. = FALSE)
  required <- c("schema_version", "handoff_type", "target", "project_id", "project_fingerprint", "title", "payload", "provenance", "review", "boundary", "created_at", "package_version")
  missing <- setdiff(required, names(handoff)); if (length(missing)) stop("Platform handoff is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(handoff$schema_version, "1.0.0")) stop("Unsupported platform handoff schema.", call. = FALSE)
  targets <- c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library", "workspace")
  if (!handoff$target %in% targets) stop("Unsupported platform handoff target.", call. = FALSE)
  .project_id(handoff$project_id, "handoff$project_id")
  if (!is.character(handoff$project_fingerprint) || length(handoff$project_fingerprint) != 1L || !grepl("^[a-f0-9]{32}$", handoff$project_fingerprint)) stop("Invalid project fingerprint.", call. = FALSE)
  if (!is.list(handoff$payload) || !is.list(handoff$provenance) || !is.list(handoff$review) || !is.list(handoff$boundary)) stop("Handoff payload, provenance, review, and boundary must be lists.", call. = FALSE)
  if (!isTRUE(handoff$review$human_reviewer_required) || !isTRUE(handoff$boundary$human_review_required)) stop("Platform handoffs must require human review.", call. = FALSE)
  invisible(TRUE)
}

#' Serialize a platform handoff
#'
#' @param handoff Platform handoff.
#' @param path Optional destination path.
#' @param pretty Pretty-print JSON.
#' @return JSON text or invisibly the path.
#' @export
handoff_to_json <- function(handoff, path = NULL, pretty = TRUE) {
  validate_platform_handoff(handoff); .assert_flag(pretty, "pretty")
  text <- jsonlite::toJSON(.safe_json_value(unclass(handoff)), auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (is.null(path)) return(as.character(text))
  .assert_single_string(path, "path"); dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE); writeLines(as.character(text), path, useBytes = TRUE); invisible(path)
}

#' Read a platform handoff from JSON
#'
#' @param json JSON text or file path.
#' @return A validated platform handoff.
#' @export
handoff_from_json <- function(json) {
  .assert_single_string(json, "json")
  text <- if (!grepl("^[[:space:]]*\\{", json) && file.exists(json)) paste(readLines(json, warn = FALSE, encoding = "UTF-8"), collapse = "\n") else json
  result <- jsonlite::fromJSON(text, simplifyVector = FALSE)
  class(result) <- c("catalyst_platform_handoff", "list")
  validate_platform_handoff(result)
  result
}

#' @export
print.catalyst_api_request <- function(x, ...) {
  cat(sprintf("<catalyst_api_request %s> %s\n", x$request_id, x$endpoint)); invisible(x)
}

#' @export
print.catalyst_api_response <- function(x, ...) {
  cat(sprintf("<catalyst_api_response %s> %s\n", x$request_id, x$status)); invisible(x)
}

#' @export
print.catalyst_platform_handoff <- function(x, ...) {
  cat(sprintf("<catalyst_platform_handoff %s> %s -> %s\n", x$project_id, x$handoff_type, x$target)); invisible(x)
}
