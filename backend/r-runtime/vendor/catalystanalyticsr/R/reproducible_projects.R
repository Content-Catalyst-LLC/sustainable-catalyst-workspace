.catalyst_project_schema_version <- function() "1.0.0"
.catalyst_project_run_schema_version <- function() "1.0.0"

.project_id <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$", x)) {
    stop(sprintf("`%s` must use letters, numbers, dots, underscores, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

.project_named_records <- function(x, arg) {
  if (is.null(x)) return(list())
  if (!is.list(x)) stop(sprintf("`%s` must be a list.", arg), call. = FALSE)
  if (length(x) && (is.null(names(x)) || any(!nzchar(names(x))))) {
    stop(sprintf("Every `%s` entry must be named.", arg), call. = FALSE)
  }
  x
}

.project_stable_json <- function(value) {
  jsonlite::toJSON(
    .safe_json_value(value), auto_unbox = TRUE, null = "null", na = "null",
    digits = NA, dataframe = "rows", POSIXt = "ISO8601"
  )
}

.project_hash <- function(value) {
  path <- tempfile("catalyst-project-hash-", fileext = ".json")
  on.exit(unlink(path), add = TRUE)
  writeLines(as.character(.project_stable_json(value)), path, useBytes = TRUE)
  unname(tools::md5sum(path))
}

.project_index_id <- function(record, fallback) {
  candidate <- record$id
  if (is.null(candidate) && inherits(record, "catalyst_scenario")) candidate <- record$id
  if (is.null(candidate) && inherits(record, "catalyst_dataset")) candidate <- record$id
  if (is.null(candidate) && inherits(record, "catalyst_model")) candidate <- record$id
  if (is.null(candidate)) candidate <- fallback
  candidate <- as.character(candidate)[1]
  .project_id(candidate, "record$id")
  candidate
}

#' Capture the analytical software environment
#'
#' @param packages Package names to capture. `NULL` captures the package and its declared dependencies.
#' @param include_session Include the printable `sessionInfo()` record.
#' @return A JSON-safe environment record.
#' @export
capture_project_environment <- function(packages = NULL, include_session = TRUE) {
  .assert_flag(include_session, "include_session")
  if (is.null(packages)) packages <- c("catalystanalyticsr", "ggplot2", "jsonlite", "grid", "rlang")
  if (!is.character(packages) || anyNA(packages)) stop("`packages` must be a character vector.", call. = FALSE)
  versions <- lapply(unique(packages), function(package) {
    version <- tryCatch(as.character(utils::packageVersion(package)), error = function(error) NA_character_)
    list(name = package, version = version, installed = !is.na(version))
  })
  list(
    schema_version = "1.0.0",
    captured_at = .utc_now(),
    r = list(version = R.version.string, platform = R.version$platform, arch = R.version$arch),
    operating_system = list(sysname = unname(Sys.info()["sysname"]), release = unname(Sys.info()["release"]), version = unname(Sys.info()["version"]), machine = unname(Sys.info()["machine"])),
    locale = tryCatch(Sys.getlocale(), error = function(error) NA_character_),
    timezone = tryCatch(Sys.timezone(), error = function(error) NA_character_),
    packages = versions,
    session = if (include_session) paste(utils::capture.output(utils::sessionInfo()), collapse = "\n") else NULL
  )
}

#' Create a reproducible Catalyst Analytics project
#'
#' @param project_id Stable project identifier.
#' @param title Human-readable project title.
#' @param description Project purpose and analytical question.
#' @param owner Named owner or responsible institution.
#' @param scope Geographic, sector, temporal, and decision scope.
#' @param tags Optional discovery tags.
#' @param metadata Additional metadata.
#' @return A `catalyst_project`.
#' @export
catalyst_project <- function(project_id, title, description = "", owner = "", scope = list(), tags = character(), metadata = list()) {
  .project_id(project_id, "project_id")
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  .assert_single_string(owner, "owner", allow_empty = TRUE)
  if (!is.list(scope)) stop("`scope` must be a list.", call. = FALSE)
  if (!is.character(tags) || anyNA(tags)) stop("`tags` must be a character vector.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  now <- .utc_now()
  project <- structure(list(
    schema_version = .catalyst_project_schema_version(),
    project_type = "reproducible_analytical_project",
    id = project_id,
    title = title,
    description = description,
    owner = owner,
    scope = scope,
    tags = unique(tags[nzchar(trimws(tags))]),
    scenarios = list(),
    datasets = list(),
    models = list(),
    parameter_sets = list(),
    runs = list(),
    indicators = list(),
    plots = list(),
    notes = list(),
    reviews = list(),
    snapshots = list(),
    publications = list(),
    environment = capture_project_environment(include_session = FALSE),
    metadata = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = now,
      updated_at = now,
      review_status = "unreviewed",
      publication_status = "draft"
    ), metadata)
  ), class = "catalyst_project")
  validate_catalyst_project(project)
  project
}

#' Validate a reproducible analytical project
#'
#' @param project A `catalyst_project` or compatible list.
#' @return Invisibly returns `TRUE`.
#' @export
validate_catalyst_project <- function(project) {
  if (!is.list(project)) stop("`project` must be a list.", call. = FALSE)
  required <- c("schema_version", "project_type", "id", "title", "description", "owner", "scope", "tags", "scenarios", "datasets", "models", "parameter_sets", "runs", "indicators", "plots", "notes", "reviews", "snapshots", "publications", "environment", "metadata")
  missing <- setdiff(required, names(project))
  if (length(missing)) stop(sprintf("Project is missing fields: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  if (!identical(project$schema_version, .catalyst_project_schema_version())) stop("Unsupported project schema version.", call. = FALSE)
  if (!identical(project$project_type, "reproducible_analytical_project")) stop("Unsupported project type.", call. = FALSE)
  .project_id(project$id, "project$id")
  .assert_single_string(project$title, "project$title")
  .assert_single_string(project$description, "project$description", allow_empty = TRUE)
  .assert_single_string(project$owner, "project$owner", allow_empty = TRUE)
  if (!is.list(project$scope)) stop("`project$scope` must be a list.", call. = FALSE)
  if (!is.character(project$tags) || anyNA(project$tags)) stop("`project$tags` must be a character vector.", call. = FALSE)
  for (name in c("scenarios", "datasets", "models", "parameter_sets", "runs", "indicators", "plots")) .project_named_records(project[[name]], paste0("project$", name))
  for (name in c("notes", "reviews", "snapshots", "publications")) if (!is.list(project[[name]])) stop(sprintf("`project$%s` must be a list.", name), call. = FALSE)
  if (!is.list(project$environment) || !is.list(project$metadata)) stop("Project environment and metadata must be lists.", call. = FALSE)
  if (!is.null(project$metadata$review_status) && !project$metadata$review_status %in% c("unreviewed", "in_review", "reviewed", "approved", "rejected")) stop("Project review status is invalid.", call. = FALSE)
  invisible(TRUE)
}

.project_touch <- function(project) {
  project$metadata$updated_at <- .utc_now()
  project$metadata$package_version <- .catalyst_package_version()
  project
}

#' Add a scenario to a project
#'
#' @param project A `catalyst_project`.
#' @param scenario A canonical scenario.
#' @param replace Replace an existing record with the same id.
#' @return Updated project.
#' @export
project_add_scenario <- function(project, scenario, replace = FALSE) {
  validate_catalyst_project(project); .assert_flag(replace, "replace")
  scenario <- as_catalyst_scenario(scenario)
  validate_catalyst_scenario(scenario)
  id <- scenario$id
  if (!is.null(project$scenarios[[id]]) && !replace) stop("Scenario already exists in the project.", call. = FALSE)
  project$scenarios[[id]] <- scenario
  .project_touch(project)
}

#' Add a dataset to a project
#'
#' @param project A project.
#' @param dataset A `catalyst_dataset`.
#' @param replace Replace an existing dataset.
#' @return Updated project.
#' @export
project_add_dataset <- function(project, dataset, replace = FALSE) {
  validate_catalyst_project(project); .assert_flag(replace, "replace")
  if (!inherits(dataset, "catalyst_dataset")) stop("`dataset` must be a catalyst_dataset.", call. = FALSE)
  validate_catalyst_dataset(dataset)
  id <- .project_index_id(dataset, paste0("dataset-", length(project$datasets) + 1L))
  if (!is.null(project$datasets[[id]]) && !replace) stop("Dataset already exists in the project.", call. = FALSE)
  project$datasets[[id]] <- dataset
  .project_touch(project)
}

#' Add a model manifest to a project
#'
#' @param project A project.
#' @param model A `catalyst_model` or model manifest list.
#' @param replace Replace an existing model version.
#' @return Updated project.
#' @export
project_add_model <- function(project, model, replace = FALSE) {
  validate_catalyst_project(project); .assert_flag(replace, "replace")
  if (inherits(model, "catalyst_model")) {
    validate_catalyst_model(model)
    record <- catalyst_model_manifest(model)
  } else if (is.list(model) && !is.null(model$id) && !is.null(model$version)) {
    record <- model
  } else stop("`model` must be a catalyst_model or model manifest.", call. = FALSE)
  key <- paste0(record$id, "@", record$version)
  if (!is.null(project$models[[key]]) && !replace) stop("Model version already exists in the project.", call. = FALSE)
  project$models[[key]] <- record
  .project_touch(project)
}

#' Add a named parameter set to a project
#'
#' @param project A project.
#' @param parameter_set_id Stable identifier.
#' @param values Named parameter values.
#' @param model_id Optional model identifier.
#' @param model_version Optional model version.
#' @param description Human-readable description.
#' @param assumptions Associated assumptions.
#' @param replace Replace an existing parameter set.
#' @return Updated project.
#' @export
project_add_parameter_set <- function(project, parameter_set_id, values, model_id = NULL, model_version = NULL, description = "", assumptions = list(), replace = FALSE) {
  validate_catalyst_project(project); .project_id(parameter_set_id, "parameter_set_id")
  if (!is.list(values) || !length(values) || is.null(names(values)) || any(!nzchar(names(values)))) stop("`values` must be a non-empty named list.", call. = FALSE)
  .assert_single_string(description, "description", allow_empty = TRUE); .assert_flag(replace, "replace")
  if (!is.null(model_id)) .project_id(model_id, "model_id")
  if (!is.null(model_version)) .validate_semver(model_version, "model_version")
  if (!is.list(assumptions)) stop("`assumptions` must be a list.", call. = FALSE)
  if (!is.null(project$parameter_sets[[parameter_set_id]]) && !replace) stop("Parameter set already exists in the project.", call. = FALSE)
  project$parameter_sets[[parameter_set_id]] <- list(
    schema_version = "1.0.0", id = parameter_set_id, model = list(id = model_id, version = model_version),
    description = description, values = values, assumptions = assumptions, hash = .project_hash(values), created_at = .utc_now()
  )
  .project_touch(project)
}

.project_result_summary <- function(result) {
  if (inherits(result, "catalyst_run")) {
    trajectory <- result$trajectory_wide
    terminal <- if (is.data.frame(trajectory) && nrow(trajectory)) as.list(trajectory[nrow(trajectory), , drop = FALSE]) else list()
    return(list(type = "catalyst_run", model = list(id = result$meta$model, version = result$meta$model_version), terminal = terminal, indicators = .safe_json_value(result$sdg_indicators)))
  }
  if (inherits(result, "catalyst_comparison")) return(list(type = "catalyst_comparison", summary = .safe_json_value(scenario_scorecard(result))))
  if (inherits(result, "catalyst_uncertainty_run")) return(list(type = "catalyst_uncertainty_run", summary = .safe_json_value(uncertainty_summary(result))))
  if (inherits(result, "catalyst_model_validation_analysis")) return(list(type = "catalyst_model_validation_analysis", summary = .safe_json_value(model_validation_summary(result))))
  list(type = paste(class(result), collapse = "/"), summary = .safe_json_value(result))
}

#' Add a governed analytical run to a project
#'
#' @param project A project.
#' @param result Analytical result object.
#' @param run_id Stable run identifier.
#' @param label Human-readable label.
#' @param scenario_ids Scenario ids used by the run.
#' @param parameter_set_id Optional parameter set id.
#' @param inputs Explicit input record. Defaults to linked project records.
#' @param warnings Warning messages.
#' @param errors Error messages.
#' @param review_status Run review state.
#' @param metadata Additional metadata.
#' @param replace Replace an existing run.
#' @return Updated project.
#' @export
project_add_run <- function(project, result, run_id, label = run_id, scenario_ids = character(), parameter_set_id = NULL, inputs = NULL, warnings = character(), errors = character(), review_status = "unreviewed", metadata = list(), replace = FALSE) {
  validate_catalyst_project(project); .project_id(run_id, "run_id"); .assert_single_string(label, "label"); .assert_flag(replace, "replace")
  if (!is.character(scenario_ids) || anyNA(scenario_ids)) stop("`scenario_ids` must be a character vector.", call. = FALSE)
  missing <- setdiff(scenario_ids, names(project$scenarios)); if (length(missing)) stop(sprintf("Unknown project scenarios: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  if (!is.null(parameter_set_id) && is.null(project$parameter_sets[[parameter_set_id]])) stop("Unknown project parameter set.", call. = FALSE)
  if (!is.character(warnings) || !is.character(errors)) stop("`warnings` and `errors` must be character vectors.", call. = FALSE)
  if (!review_status %in% c("unreviewed", "in_review", "reviewed", "approved", "rejected")) stop("`review_status` is invalid.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  if (!is.null(project$runs[[run_id]]) && !replace) stop("Run already exists in the project.", call. = FALSE)
  if (is.null(inputs)) inputs <- list(
    scenarios = unname(project$scenarios[scenario_ids]),
    parameter_set = if (is.null(parameter_set_id)) NULL else project$parameter_sets[[parameter_set_id]]
  )
  result_payload <- result
  if (inherits(result, "catalyst_run")) {
    result_payload <- result[c("trajectory_wide", "trajectory_long", "sdg_indicators", "carbon_budget", "scorecard", "meta", "scenario")]
    result_payload$plot_artifacts <- names(result$plots)
  }
  safe_result <- .safe_json_value(result_payload)
  created <- .utc_now()
  status <- if (length(errors)) "failed" else "completed"
  model <- NULL
  if (inherits(result, "catalyst_run")) model <- list(id = result$meta$model, version = result$meta$model_version)
  record <- structure(list(
    schema_version = .catalyst_project_run_schema_version(),
    id = run_id,
    label = label,
    status = status,
    scenario_ids = scenario_ids,
    parameter_set_id = parameter_set_id,
    model = model,
    created_at = created,
    completed_at = created,
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    environment = capture_project_environment(include_session = FALSE),
    input_hash = .project_hash(inputs),
    output_hash = .project_hash(safe_result),
    inputs = .safe_json_value(inputs),
    result_summary = .project_result_summary(result),
    result = safe_result,
    warnings = warnings,
    errors = errors,
    review_status = review_status,
    metadata = metadata
  ), class = "catalyst_project_run")
  project$runs[[run_id]] <- record
  .project_touch(project)
}

#' Add an indicator result to a project
#'
#' @param project A project.
#' @param indicator Result or indicator set.
#' @param indicator_id Stable identifier.
#' @param replace Replace an existing indicator artifact.
#' @return Updated project.
#' @export
project_add_indicator <- function(project, indicator, indicator_id, replace = FALSE) {
  validate_catalyst_project(project); .project_id(indicator_id, "indicator_id"); .assert_flag(replace, "replace")
  if (!is.null(project$indicators[[indicator_id]]) && !replace) stop("Indicator artifact already exists.", call. = FALSE)
  project$indicators[[indicator_id]] <- list(id = indicator_id, value = .safe_json_value(indicator), hash = .project_hash(indicator), created_at = .utc_now())
  .project_touch(project)
}

#' Register a plot or publication figure
#'
#' @param project A project.
#' @param plot_id Stable plot identifier.
#' @param path Existing PNG, SVG, PDF, or other figure path.
#' @param title Figure title.
#' @param caption Figure caption.
#' @param run_id Optional originating run.
#' @param replace Replace an existing plot record.
#' @return Updated project.
#' @export
project_add_plot <- function(project, plot_id, path, title = plot_id, caption = "", run_id = NULL, replace = FALSE) {
  validate_catalyst_project(project); .project_id(plot_id, "plot_id"); .assert_single_string(path, "path"); .assert_single_string(title, "title"); .assert_single_string(caption, "caption", allow_empty = TRUE); .assert_flag(replace, "replace")
  if (!file.exists(path)) stop("Plot file does not exist.", call. = FALSE)
  if (!is.null(run_id) && is.null(project$runs[[run_id]])) stop("Unknown project run.", call. = FALSE)
  if (!is.null(project$plots[[plot_id]]) && !replace) stop("Plot already exists.", call. = FALSE)
  project$plots[[plot_id]] <- list(id = plot_id, title = title, caption = caption, source_path = normalizePath(path, mustWork = TRUE), file = basename(path), media_type = tools::file_ext(path), run_id = run_id, bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path)), created_at = .utc_now())
  .project_touch(project)
}

#' Add an interpretation note
#'
#' @param project A project.
#' @param note_id Stable note identifier.
#' @param text Interpretation text.
#' @param author Author or analyst.
#' @param run_ids Related runs.
#' @param status Note status.
#' @return Updated project.
#' @export
project_add_note <- function(project, note_id, text, author = "", run_ids = character(), status = "draft") {
  validate_catalyst_project(project); .project_id(note_id, "note_id"); .assert_single_string(text, "text"); .assert_single_string(author, "author", allow_empty = TRUE)
  if (!is.character(run_ids) || anyNA(run_ids)) stop("`run_ids` must be a character vector.", call. = FALSE)
  missing <- setdiff(run_ids, names(project$runs)); if (length(missing)) stop("A note references an unknown run.", call. = FALSE)
  if (!status %in% c("draft", "reviewed", "approved", "retired")) stop("Note status is invalid.", call. = FALSE)
  if (any(vapply(project$notes, function(x) identical(x$id, note_id), logical(1)))) stop("Note id already exists.", call. = FALSE)
  project$notes[[length(project$notes) + 1L]] <- list(id = note_id, text = text, author = author, run_ids = run_ids, status = status, created_at = .utc_now())
  .project_touch(project)
}

#' Add a project review record
#'
#' @param project A project.
#' @param review_id Stable review identifier.
#' @param reviewer Reviewer name or institution.
#' @param decision Review decision.
#' @param comments Review comments.
#' @param scope Review scope.
#' @param run_ids Related runs.
#' @return Updated project.
#' @export
project_add_review <- function(project, review_id, reviewer, decision = "pending", comments = "", scope = "project", run_ids = character()) {
  validate_catalyst_project(project); .project_id(review_id, "review_id"); .assert_single_string(reviewer, "reviewer"); .assert_single_string(comments, "comments", allow_empty = TRUE); .assert_single_string(scope, "scope")
  if (!decision %in% c("pending", "changes_requested", "approved", "rejected")) stop("Review decision is invalid.", call. = FALSE)
  if (!is.character(run_ids) || anyNA(run_ids)) stop("`run_ids` must be a character vector.", call. = FALSE)
  missing <- setdiff(run_ids, names(project$runs)); if (length(missing)) stop("A review references an unknown run.", call. = FALSE)
  if (any(vapply(project$reviews, function(x) identical(x$id, review_id), logical(1)))) stop("Review id already exists.", call. = FALSE)
  project$reviews[[length(project$reviews) + 1L]] <- list(id = review_id, reviewer = reviewer, decision = decision, comments = comments, scope = scope, run_ids = run_ids, reviewed_at = .utc_now())
  decisions <- vapply(project$reviews, `[[`, character(1), "decision")
  project$metadata$review_status <- if (length(decisions) && all(decisions == "approved")) "approved" else if (any(decisions == "rejected")) "rejected" else "in_review"
  .project_touch(project)
}

#' Create an immutable project snapshot record
#'
#' @param project A project.
#' @param snapshot_id Stable snapshot identifier.
#' @param note Snapshot note.
#' @return Updated project.
#' @export
project_snapshot <- function(project, snapshot_id, note = "") {
  validate_catalyst_project(project); .project_id(snapshot_id, "snapshot_id"); .assert_single_string(note, "note", allow_empty = TRUE)
  if (any(vapply(project$snapshots, function(x) identical(x$id, snapshot_id), logical(1)))) stop("Snapshot id already exists.", call. = FALSE)
  project$snapshots[[length(project$snapshots) + 1L]] <- list(
    id = snapshot_id, note = note, created_at = .utc_now(), project_fingerprint = project_fingerprint(project),
    counts = list(scenarios = length(project$scenarios), datasets = length(project$datasets), models = length(project$models), parameter_sets = length(project$parameter_sets), runs = length(project$runs), indicators = length(project$indicators), plots = length(project$plots), notes = length(project$notes), reviews = length(project$reviews))
  )
  .project_touch(project)
}

#' Compute a portable project fingerprint
#'
#' @param project A project.
#' @return MD5 fingerprint.
#' @export
project_fingerprint <- function(project) {
  validate_catalyst_project(project)
  stable <- unclass(project)
  stable$environment$captured_at <- NULL
  stable$environment$session <- NULL
  stable$metadata$created_at <- NULL
  stable$metadata$updated_at <- NULL
  stable$publications <- lapply(stable$publications, function(x) { x$created_at <- NULL; x$path <- NULL; x })
  stable$plots <- lapply(stable$plots, function(x) { x$source_path <- NULL; x$created_at <- NULL; x })
  .project_hash(stable)
}

#' Summarize a reproducible project
#'
#' @param project A project.
#' @return One-row data frame.
#' @export
project_summary <- function(project) {
  validate_catalyst_project(project)
  data.frame(
    project_id = project$id, title = project$title, owner = project$owner,
    scenarios = length(project$scenarios), datasets = length(project$datasets), models = length(project$models),
    parameter_sets = length(project$parameter_sets), runs = length(project$runs), completed_runs = sum(vapply(project$runs, function(x) identical(x$status, "completed"), logical(1))),
    failed_runs = sum(vapply(project$runs, function(x) identical(x$status, "failed"), logical(1))),
    notes = length(project$notes), reviews = length(project$reviews), snapshots = length(project$snapshots), publications = length(project$publications),
    review_status = project$metadata$review_status, publication_status = project$metadata$publication_status,
    fingerprint = project_fingerprint(project), stringsAsFactors = FALSE
  )
}

#' Return a machine-readable project manifest
#'
#' @param project A project.
#' @return JSON-safe project manifest.
#' @export
project_manifest <- function(project) {
  validate_catalyst_project(project)
  list(
    schema_version = .catalyst_project_schema_version(), project_id = project$id, title = project$title,
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    fingerprint = project_fingerprint(project), summary = project_summary(project), scope = project$scope, tags = project$tags,
    scenarios = lapply(project$scenarios, function(x) list(id = x$id, title = x$title, role = x$role, model = x$model, fingerprint = scenario_fingerprint(x))),
    datasets = lapply(project$datasets, function(x) list(id = x$id, title = x$title, fingerprint = dataset_fingerprint(x), rows = nrow(x$data))),
    models = project$models,
    parameter_sets = lapply(project$parameter_sets, function(x) x[c("id", "model", "description", "hash", "created_at")]),
    runs = lapply(project$runs, function(x) x[c("id", "label", "status", "scenario_ids", "parameter_set_id", "model", "created_at", "input_hash", "output_hash", "review_status", "warnings", "errors")]),
    plots = lapply(project$plots, function(x) x[setdiff(names(x), "source_path")]),
    notes = project$notes, reviews = project$reviews, snapshots = project$snapshots, publications = project$publications,
    environment = project$environment, metadata = project$metadata
  )
}

#' Save a project as canonical JSON
#'
#' @param project A project.
#' @param path Destination JSON path.
#' @param pretty Pretty-print JSON.
#' @return Invisibly returns `path`.
#' @export
project_to_json <- function(project, path, pretty = TRUE) {
  validate_catalyst_project(project); .assert_single_string(path, "path"); .assert_flag(pretty, "pretty")
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  jsonlite::write_json(.safe_json_value(unclass(project)), path, auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  invisible(path)
}

#' Load a project from canonical JSON
#'
#' @param path Project JSON path.
#' @return A `catalyst_project`.
#' @export
project_from_json <- function(path) {
  .assert_single_string(path, "path")
  if (!file.exists(path)) stop("Project JSON file does not exist.", call. = FALSE)
  project <- jsonlite::fromJSON(path, simplifyVector = TRUE, simplifyDataFrame = TRUE, simplifyMatrix = FALSE)
  if (!is.list(project)) stop("Project JSON root must be an object.", call. = FALSE)
  rows_to_records <- function(value) {
    if (!is.data.frame(value)) return(value)
    lapply(seq_len(nrow(value)), function(i) {
      row <- lapply(value, function(column) {
        item <- column[[i]]
        if (is.factor(item)) as.character(item) else item
      })
      names(row) <- names(value)
      row
    })
  }
  project$tags <- as.character(project$tags)
  for (field in c("notes", "reviews", "snapshots", "publications")) project[[field]] <- rows_to_records(project[[field]])
  for (id in names(project$scenarios)) project$scenarios[[id]] <- structure(project$scenarios[[id]], class = "catalyst_scenario")
  for (id in names(project$datasets)) project$datasets[[id]] <- structure(project$datasets[[id]], class = "catalyst_dataset")
  for (id in names(project$runs)) {
    run <- project$runs[[id]]
    result <- if ("result" %in% names(run)) run[["result", exact = TRUE]] else NULL
    if (!"result" %in% names(run) || (is.list(result) && length(result) == 0L)) {
      run["result"] <- list(NULL)
    }
    project$runs[[id]] <- structure(run, class = "catalyst_project_run")
  }
  project <- structure(project, class = "catalyst_project")
  validate_catalyst_project(project)
  project
}

#' @export
print.catalyst_project <- function(x, ...) {
  summary <- project_summary(x)
  cat(sprintf("<catalyst_project %s>\n", x$id))
  cat(sprintf("  %s\n", x$title))
  cat(sprintf("  scenarios: %d | datasets: %d | runs: %d | review: %s\n", summary$scenarios, summary$datasets, summary$runs, summary$review_status))
  invisible(x)
}

#' @export
print.catalyst_project_run <- function(x, ...) {
  cat(sprintf("<catalyst_project_run %s> %s\n", x$id, x$status))
  cat(sprintf("  input: %s\n  output: %s\n", x$input_hash, x$output_hash))
  invisible(x)
}
