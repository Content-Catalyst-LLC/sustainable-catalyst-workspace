.catalyst_workspace_schema_version <- function() "1.0.0"
.catalyst_workspace_export_schema_version <- function() "1.0.0"

.workspace_id <- function(x, arg = "workspace_id") {
  .project_id(x, arg)
  invisible(x)
}

.workspace_named_list <- function(x, arg) {
  if (!is.list(x)) stop(sprintf("`%s` must be a list.", arg), call. = FALSE)
  if (length(x) && (is.null(names(x)) || any(!nzchar(names(x))))) {
    stop(sprintf("Every `%s` entry must be named.", arg), call. = FALSE)
  }
  x
}

.workspace_touch <- function(workspace, action = NULL, details = list(), semantic_change = TRUE) {
  .assert_flag(semantic_change, "semantic_change")
  if (semantic_change && ".restored_workspace_fingerprint" %in% names(workspace)) {
    workspace[[".restored_workspace_fingerprint"]] <- NULL
  }
  workspace$metadata$updated_at <- .utc_now()
  workspace$metadata$package_version <- .catalyst_package_version()
  if (!is.null(action)) {
    workspace$activity[[length(workspace$activity) + 1L]] <- list(
      id = paste0("activity-", length(workspace$activity) + 1L),
      action = action,
      details = .safe_json_value(details),
      recorded_at = .utc_now()
    )
  }
  workspace
}

.workspace_restore_project_record <- function(record) {
  path <- tempfile("catalyst-workspace-project-", fileext = ".json")
  on.exit(unlink(path, force = TRUE), add = TRUE)
  jsonlite::write_json(record, path, auto_unbox = TRUE, pretty = FALSE, null = "null", na = "null", digits = NA, dataframe = "rows")
  project_from_json(path)
}

.workspace_restore_classes <- function(workspace) {
  workspace$tags <- as.character(unlist(workspace$tags, use.names = FALSE))
  if (!"active_project_id" %in% names(workspace)) workspace["active_project_id"] <- list(NULL)
  active_project_id <- workspace[["active_project_id", exact = TRUE]]
  if (is.list(active_project_id)) {
    if (length(active_project_id) == 0L ||
        (length(active_project_id) == 1L && is.null(active_project_id[[1L]]))) {
      workspace["active_project_id"] <- list(NULL)
    } else if (length(active_project_id) == 1L) {
      workspace$active_project_id <- as.character(active_project_id[[1L]])
    }
  }
  if (length(workspace$projects)) {
    workspace$projects <- lapply(workspace$projects, function(project) {
      if (inherits(project, "catalyst_project")) return(project)
      .workspace_restore_project_record(project)
    })
  }
  if (length(workspace$libraries$scenarios)) {
    for (id in names(workspace$libraries$scenarios)) {
      entry <- workspace$libraries$scenarios[[id]]
      entry$tags <- as.character(unlist(entry$tags, use.names = FALSE))
      if (!inherits(entry$scenario, "catalyst_scenario")) {
        entry$scenario <- as_catalyst_scenario(entry$scenario)
      }
      workspace$libraries$scenarios[[id]] <- entry
    }
  }
  if (length(workspace$libraries$parameter_sets)) {
    for (id in names(workspace$libraries$parameter_sets)) {
      entry <- workspace$libraries$parameter_sets[[id]]
      entry$tags <- as.character(unlist(entry$tags, use.names = FALSE))
      workspace$libraries$parameter_sets[[id]] <- entry
    }
  }
  if (is.null(workspace$libraries$regional_portfolios)) workspace$libraries$regional_portfolios <- list()
  if (length(workspace$libraries$regional_portfolios)) {
    workspace$libraries$regional_portfolios <- lapply(workspace$libraries$regional_portfolios, function(portfolio) {
      if (inherits(portfolio, "catalyst_regional_portfolio")) return(portfolio)
      portfolio$members <- lapply(portfolio$members, .as_portfolio_member)
      structure(portfolio, class = c("catalyst_regional_portfolio", "list"))
    })
  }
  if (is.null(workspace$libraries$policy_optimizations)) workspace$libraries$policy_optimizations <- list()
  if (is.null(workspace$libraries$policy_pathways)) workspace$libraries$policy_pathways <- list()
  if (is.null(workspace$libraries$policy_evaluations)) workspace$libraries$policy_evaluations <- list()
  if (is.null(workspace$libraries$institutional_governance)) workspace$libraries$institutional_governance <- list()
  if (length(workspace$libraries$policy_pathways)) {
    workspace$libraries$policy_pathways <- lapply(workspace$libraries$policy_pathways, function(pathway) {
      if (inherits(pathway, "catalyst_policy_pathway")) return(pathway)
      pathway$stages <- lapply(pathway$stages, function(stage) {
        stage$triggers <- lapply(stage$triggers, function(trigger) structure(trigger, class = c("catalyst_adaptive_trigger", "list")))
        structure(stage, class = c("catalyst_policy_stage", "list"))
      })
      structure(pathway, class = c("catalyst_policy_pathway", "list"))
    })
  }
  if (length(workspace$libraries$policy_packages)) {
    for (id in names(workspace$libraries$policy_packages)) {
      entry <- workspace$libraries$policy_packages[[id]]
      entry$scenario_ids <- as.character(unlist(entry$scenario_ids, use.names = FALSE))
      entry$parameter_set_ids <- as.character(unlist(entry$parameter_set_ids, use.names = FALSE))
      entry$tags <- as.character(unlist(entry$tags, use.names = FALSE))
      workspace$libraries$policy_packages[[id]] <- entry
    }
  }
  structure(workspace, class = "catalyst_workspace")
}

#' Create a persistent Catalyst Analytics workspace
#'
#' @param workspace_id Stable workspace identifier.
#' @param title Human-readable title.
#' @param description Workspace purpose.
#' @param owner Responsible person or institution.
#' @param tags Discovery tags.
#' @param metadata Additional metadata.
#' @return A `catalyst_workspace`.
#' @export
catalyst_workspace <- function(workspace_id, title, description = "", owner = "", tags = character(), metadata = list()) {
  .workspace_id(workspace_id)
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  .assert_single_string(owner, "owner", allow_empty = TRUE)
  if (!is.character(tags) || anyNA(tags)) stop("`tags` must be a character vector.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  now <- .utc_now()
  workspace <- structure(list(
    schema_version = .catalyst_workspace_schema_version(),
    workspace_type = "persistent_analytical_workspace",
    id = workspace_id,
    title = title,
    description = description,
    owner = owner,
    tags = unique(tags[nzchar(trimws(tags))]),
    active_project_id = NULL,
    projects = list(),
    libraries = list(scenarios = list(), parameter_sets = list(), policy_packages = list(), regional_portfolios = list(), policy_optimizations = list(), policy_pathways = list(), policy_evaluations = list(), platform_handoffs = list(), institutional_governance = list()),
    snapshots = list(),
    activity = list(),
    metadata = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = now,
      updated_at = now,
      status = "active"
    ), metadata)
  ), class = "catalyst_workspace")
  validate_catalyst_workspace(workspace)
  workspace
}

#' Validate a Catalyst Analytics workspace
#'
#' @param workspace A workspace or compatible list.
#' @return Invisibly returns `TRUE`.
#' @export
validate_catalyst_workspace <- function(workspace) {
  if (!is.list(workspace)) stop("`workspace` must be a list.", call. = FALSE)
  required <- c("schema_version", "workspace_type", "id", "title", "description", "owner", "tags", "active_project_id", "projects", "libraries", "snapshots", "activity", "metadata")
  missing <- setdiff(required, names(workspace))
  if (length(missing)) stop(sprintf("Workspace is missing fields: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  if (!identical(workspace$schema_version, .catalyst_workspace_schema_version())) stop("Unsupported workspace schema version.", call. = FALSE)
  if (!identical(workspace$workspace_type, "persistent_analytical_workspace")) stop("Unsupported workspace type.", call. = FALSE)
  .workspace_id(workspace$id, "workspace$id")
  .assert_single_string(workspace$title, "workspace$title")
  .assert_single_string(workspace$description, "workspace$description", allow_empty = TRUE)
  .assert_single_string(workspace$owner, "workspace$owner", allow_empty = TRUE)
  if (!is.character(workspace$tags) || anyNA(workspace$tags)) stop("`workspace$tags` must be a character vector.", call. = FALSE)
  .workspace_named_list(workspace$projects, "workspace$projects")
  if (!is.null(workspace$active_project_id)) {
    .assert_single_string(workspace$active_project_id, "workspace$active_project_id")
    if (is.null(workspace$projects[[workspace$active_project_id]])) stop("Active project is not present in the workspace.", call. = FALSE)
  }
  for (project in workspace$projects) validate_catalyst_project(project)
  if (!is.list(workspace$libraries)) stop("`workspace$libraries` must be a list.", call. = FALSE)
  library_fields <- c("scenarios", "parameter_sets", "policy_packages")
  if (length(setdiff(library_fields, names(workspace$libraries)))) stop("Workspace libraries are incomplete.", call. = FALSE)
  for (field in library_fields) .workspace_named_list(workspace$libraries[[field]], paste0("workspace$libraries$", field))
  for (entry in workspace$libraries$scenarios) {
    if (!is.list(entry) || is.null(entry$id) || is.null(entry$scenario) || is.null(entry$fingerprint)) stop("Scenario library entry is incomplete.", call. = FALSE)
    validate_catalyst_scenario(entry$scenario)
  }
  for (entry in workspace$libraries$parameter_sets) {
    if (!is.list(entry) || is.null(entry$id) || is.null(entry$values) || is.null(entry$hash)) stop("Parameter library entry is incomplete.", call. = FALSE)
  }
  for (entry in workspace$libraries$policy_packages) {
    if (!is.list(entry) || is.null(entry$id) || is.null(entry$scenario_ids) || is.null(entry$parameter_set_ids)) stop("Policy package entry is incomplete.", call. = FALSE)
    if (length(setdiff(entry$scenario_ids, names(workspace$libraries$scenarios)))) stop("Policy package references an unknown scenario.", call. = FALSE)
    if (length(setdiff(entry$parameter_set_ids, names(workspace$libraries$parameter_sets)))) stop("Policy package references an unknown parameter set.", call. = FALSE)
  }
  if (!is.null(workspace$libraries$regional_portfolios)) {
    .workspace_named_list(workspace$libraries$regional_portfolios, "workspace$libraries$regional_portfolios")
    invisible(lapply(workspace$libraries$regional_portfolios, validate_regional_portfolio))
  }
  if (!is.null(workspace$libraries$policy_optimizations)) {
    .workspace_named_list(workspace$libraries$policy_optimizations, "workspace$libraries$policy_optimizations")
    for (entry in workspace$libraries$policy_optimizations) {
      if (!is.list(entry) || is.null(entry$id) || is.null(entry$title) || is.null(entry$fingerprint)) stop("Policy optimization library entry is incomplete.", call. = FALSE)
    }
  }
  if (!is.null(workspace$libraries$policy_pathways)) {
    .workspace_named_list(workspace$libraries$policy_pathways, "workspace$libraries$policy_pathways")
    invisible(lapply(workspace$libraries$policy_pathways, validate_policy_pathway))
  }

  if (!is.null(workspace$libraries$policy_evaluations)) {
    .workspace_named_list(workspace$libraries$policy_evaluations, "workspace$libraries$policy_evaluations")
    for (entry in workspace$libraries$policy_evaluations) {
      if (!is.list(entry) || is.null(entry$id) || is.null(entry$title) || is.null(entry$fingerprint)) stop("Policy evaluation library entry is incomplete.", call. = FALSE)
    }
  }
  if (!is.null(workspace$libraries$platform_handoffs)) {
    .workspace_named_list(workspace$libraries$platform_handoffs, "workspace$libraries$platform_handoffs")
    invisible(lapply(workspace$libraries$platform_handoffs, validate_platform_handoff))
  }
  if (!is.null(workspace$libraries$institutional_governance)) {
    .workspace_named_list(workspace$libraries$institutional_governance, "workspace$libraries$institutional_governance")
    invisible(lapply(workspace$libraries$institutional_governance, validate_institutional_governance))
  }
  if (!is.list(workspace$snapshots) || !is.list(workspace$activity) || !is.list(workspace$metadata)) stop("Workspace snapshots, activity, and metadata must be lists.", call. = FALSE)
  restored_fingerprint <- workspace[[".restored_workspace_fingerprint", exact = TRUE]]
  if (!is.null(restored_fingerprint)) {
    if (!is.character(restored_fingerprint) || length(restored_fingerprint) != 1L ||
        is.na(restored_fingerprint) || !grepl("^[a-f0-9]{32}$", restored_fingerprint)) {
      stop("Restored workspace fingerprint override is invalid.", call. = FALSE)
    }
  }
  invisible(TRUE)
}

#' Add a project to a workspace
#'
#' @param workspace A workspace.
#' @param project A `catalyst_project`.
#' @param replace Replace an existing project.
#' @param index_contents Add project scenarios and parameter sets to the reusable libraries.
#' @return Updated workspace.
#' @export
workspace_add_project <- function(workspace, project, replace = FALSE, index_contents = TRUE) {
  validate_catalyst_workspace(workspace)
  validate_catalyst_project(project)
  .assert_flag(replace, "replace")
  .assert_flag(index_contents, "index_contents")
  if (!is.null(workspace$projects[[project$id]]) && !replace) stop("Project already exists in the workspace.", call. = FALSE)
  workspace$projects[[project$id]] <- project
  if (is.null(workspace$active_project_id)) workspace$active_project_id <- project$id
  if (index_contents) {
    for (scenario in project$scenarios) {
      workspace <- workspace_add_scenario(workspace, scenario, library_id = scenario$id, source_project_id = project$id, replace = TRUE)
    }
    for (parameter_set in project$parameter_sets) {
      workspace <- workspace_add_parameter_set(
        workspace, parameter_set$id, parameter_set$values,
        model_id = parameter_set$model$id, model_version = parameter_set$model$version,
        description = parameter_set$description, assumptions = parameter_set$assumptions,
        source_project_id = project$id, replace = TRUE
      )
    }
  }
  .workspace_touch(workspace, "project_added", list(project_id = project$id, indexed = index_contents))
}

#' Retrieve a project from a workspace
#'
#' @param workspace A workspace.
#' @param project_id Project identifier. `NULL` uses the active project.
#' @return A `catalyst_project`.
#' @export
workspace_get_project <- function(workspace, project_id = NULL) {
  validate_catalyst_workspace(workspace)
  if (is.null(project_id)) project_id <- workspace$active_project_id
  if (is.null(project_id) || is.null(workspace$projects[[project_id]])) stop("Project is not present in the workspace.", call. = FALSE)
  workspace$projects[[project_id]]
}

#' Remove a project from a workspace
#'
#' @param workspace A workspace.
#' @param project_id Project identifier.
#' @return Updated workspace.
#' @export
workspace_remove_project <- function(workspace, project_id) {
  validate_catalyst_workspace(workspace)
  .workspace_id(project_id, "project_id")
  if (is.null(workspace$projects[[project_id]])) stop("Project is not present in the workspace.", call. = FALSE)
  workspace$projects[[project_id]] <- NULL
  if (identical(workspace$active_project_id, project_id)) {
    next_project_id <- if (length(workspace$projects)) names(workspace$projects)[1L] else NULL
    workspace["active_project_id"] <- list(next_project_id)
  }
  .workspace_touch(workspace, "project_removed", list(project_id = project_id))
}

#' Set the active workspace project
#'
#' @param workspace A workspace.
#' @param project_id Project identifier.
#' @return Updated workspace.
#' @export
workspace_set_active_project <- function(workspace, project_id) {
  validate_catalyst_workspace(workspace)
  .workspace_id(project_id, "project_id")
  if (is.null(workspace$projects[[project_id]])) stop("Project is not present in the workspace.", call. = FALSE)
  workspace$active_project_id <- project_id
  .workspace_touch(workspace, "active_project_changed", list(project_id = project_id))
}

#' Add a reusable scenario to the workspace library
#'
#' @param workspace A workspace.
#' @param scenario A canonical scenario.
#' @param library_id Stable library identifier.
#' @param description Library description.
#' @param tags Discovery tags.
#' @param source_project_id Optional source project.
#' @param replace Replace an existing entry.
#' @return Updated workspace.
#' @export
workspace_add_scenario <- function(workspace, scenario, library_id = NULL, description = "", tags = character(), source_project_id = NULL, replace = FALSE) {
  validate_catalyst_workspace(workspace)
  scenario <- as_catalyst_scenario(scenario)
  if (is.null(library_id)) library_id <- scenario$id
  .workspace_id(library_id, "library_id")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.character(tags) || anyNA(tags)) stop("`tags` must be a character vector.", call. = FALSE)
  .assert_flag(replace, "replace")
  if (!is.null(source_project_id) && is.null(workspace$projects[[source_project_id]])) stop("Source project is not present in the workspace.", call. = FALSE)
  if (!is.null(workspace$libraries$scenarios[[library_id]]) && !replace) stop("Scenario library entry already exists.", call. = FALSE)
  existing_created <- workspace$libraries$scenarios[[library_id]]$created_at
  workspace$libraries$scenarios[[library_id]] <- list(
    id = library_id, title = scenario$title, description = description,
    tags = unique(tags[nzchar(trimws(tags))]), source_project_id = source_project_id,
    scenario = scenario, fingerprint = scenario_fingerprint(scenario),
    created_at = if (is.null(existing_created)) .utc_now() else existing_created,
    updated_at = .utc_now()
  )
  .workspace_touch(workspace, "scenario_library_updated", list(library_id = library_id, scenario_id = scenario$id))
}

#' Retrieve a scenario from the workspace library
#'
#' @param workspace A workspace.
#' @param library_id Scenario-library identifier.
#' @return A `catalyst_scenario`.
#' @export
workspace_get_scenario <- function(workspace, library_id) {
  validate_catalyst_workspace(workspace)
  .workspace_id(library_id, "library_id")
  entry <- workspace$libraries$scenarios[[library_id]]
  if (is.null(entry)) stop("Scenario is not present in the workspace library.", call. = FALSE)
  entry$scenario
}

#' Clone a reusable scenario
#'
#' @param workspace A workspace.
#' @param library_id Existing scenario-library identifier.
#' @param new_library_id New library identifier.
#' @param new_scenario_id New canonical scenario identifier.
#' @param title Optional new title.
#' @param role Optional new scenario role.
#' @param replace Replace an existing target entry.
#' @return Updated workspace.
#' @export
workspace_clone_scenario <- function(workspace, library_id, new_library_id, new_scenario_id = new_library_id, title = NULL, role = NULL, replace = FALSE) {
  scenario <- workspace_get_scenario(workspace, library_id)
  .workspace_id(new_library_id, "new_library_id")
  .workspace_id(new_scenario_id, "new_scenario_id")
  if (!is.null(title)) .assert_single_string(title, "title")
  if (!is.null(role) && !role %in% c("baseline", "intervention", "counterfactual", "exploratory")) stop("`role` is invalid.", call. = FALSE)
  scenario$id <- new_scenario_id
  if (!is.null(title)) scenario$title <- title
  if (!is.null(role)) scenario$role <- role
  scenario$metadata$created_at <- .utc_now()
  scenario$metadata$tags <- unique(c(scenario$metadata$tags, "workspace-clone"))
  validate_catalyst_scenario(scenario)
  workspace_add_scenario(workspace, scenario, new_library_id, description = paste0("Clone of ", library_id), tags = "clone", replace = replace)
}

#' Add a reusable parameter set
#'
#' @param workspace A workspace.
#' @param parameter_set_id Stable identifier.
#' @param values Named parameter values.
#' @param model_id Optional model identifier.
#' @param model_version Optional model version.
#' @param description Description.
#' @param assumptions Assumption records.
#' @param tags Discovery tags.
#' @param source_project_id Optional source project.
#' @param replace Replace an existing entry.
#' @return Updated workspace.
#' @export
workspace_add_parameter_set <- function(workspace, parameter_set_id, values, model_id = NULL, model_version = NULL, description = "", assumptions = list(), tags = character(), source_project_id = NULL, replace = FALSE) {
  validate_catalyst_workspace(workspace)
  .workspace_id(parameter_set_id, "parameter_set_id")
  if (!is.list(values) || (length(values) && (is.null(names(values)) || any(!nzchar(names(values)))))) stop("`values` must be a named list.", call. = FALSE)
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.list(assumptions)) stop("`assumptions` must be a list.", call. = FALSE)
  if (!is.character(tags) || anyNA(tags)) stop("`tags` must be a character vector.", call. = FALSE)
  .assert_flag(replace, "replace")
  if (!is.null(source_project_id) && is.null(workspace$projects[[source_project_id]])) stop("Source project is not present in the workspace.", call. = FALSE)
  if (!is.null(workspace$libraries$parameter_sets[[parameter_set_id]]) && !replace) stop("Parameter-library entry already exists.", call. = FALSE)
  existing_created <- workspace$libraries$parameter_sets[[parameter_set_id]]$created_at
  model <- if (is.null(model_id)) NULL else list(id = model_id, version = model_version)
  workspace$libraries$parameter_sets[[parameter_set_id]] <- list(
    id = parameter_set_id, model = model, values = values, description = description,
    assumptions = assumptions, tags = unique(tags[nzchar(trimws(tags))]),
    source_project_id = source_project_id, hash = .project_hash(list(model = model, values = values, assumptions = assumptions)),
    created_at = if (is.null(existing_created)) .utc_now() else existing_created,
    updated_at = .utc_now()
  )
  .workspace_touch(workspace, "parameter_library_updated", list(parameter_set_id = parameter_set_id))
}

#' Retrieve a reusable parameter set
#'
#' @param workspace A workspace.
#' @param parameter_set_id Parameter-set identifier.
#' @return Parameter-library record.
#' @export
workspace_get_parameter_set <- function(workspace, parameter_set_id) {
  validate_catalyst_workspace(workspace)
  .workspace_id(parameter_set_id, "parameter_set_id")
  entry <- workspace$libraries$parameter_sets[[parameter_set_id]]
  if (is.null(entry)) stop("Parameter set is not present in the workspace library.", call. = FALSE)
  entry
}

#' Add a reusable policy package
#'
#' @param workspace A workspace.
#' @param policy_package_id Stable identifier.
#' @param title Human-readable title.
#' @param scenario_ids Scenario-library identifiers.
#' @param parameter_set_ids Parameter-library identifiers.
#' @param assumptions Policy assumptions.
#' @param constraints Policy constraints.
#' @param description Description.
#' @param tags Discovery tags.
#' @param replace Replace an existing package.
#' @return Updated workspace.
#' @export
workspace_add_policy_package <- function(workspace, policy_package_id, title, scenario_ids = character(), parameter_set_ids = character(), assumptions = list(), constraints = list(), description = "", tags = character(), replace = FALSE) {
  validate_catalyst_workspace(workspace)
  .workspace_id(policy_package_id, "policy_package_id")
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.character(scenario_ids) || !is.character(parameter_set_ids)) stop("Policy-package references must be character vectors.", call. = FALSE)
  if (!is.list(assumptions) || !is.list(constraints)) stop("Policy-package assumptions and constraints must be lists.", call. = FALSE)
  if (!is.character(tags) || anyNA(tags)) stop("`tags` must be a character vector.", call. = FALSE)
  .assert_flag(replace, "replace")
  missing_scenarios <- setdiff(scenario_ids, names(workspace$libraries$scenarios))
  missing_parameters <- setdiff(parameter_set_ids, names(workspace$libraries$parameter_sets))
  if (length(missing_scenarios)) stop(sprintf("Unknown policy-package scenarios: %s.", paste(missing_scenarios, collapse = ", ")), call. = FALSE)
  if (length(missing_parameters)) stop(sprintf("Unknown policy-package parameter sets: %s.", paste(missing_parameters, collapse = ", ")), call. = FALSE)
  if (!is.null(workspace$libraries$policy_packages[[policy_package_id]]) && !replace) stop("Policy package already exists.", call. = FALSE)
  workspace$libraries$policy_packages[[policy_package_id]] <- list(
    id = policy_package_id, title = title, description = description,
    scenario_ids = unique(scenario_ids), parameter_set_ids = unique(parameter_set_ids),
    assumptions = assumptions, constraints = constraints, tags = unique(tags[nzchar(trimws(tags))]),
    hash = .project_hash(list(scenario_ids = scenario_ids, parameter_set_ids = parameter_set_ids, assumptions = assumptions, constraints = constraints)),
    created_at = .utc_now()
  )
  .workspace_touch(workspace, "policy_package_added", list(policy_package_id = policy_package_id))
}

#' List reusable scenarios
#'
#' @param workspace A workspace.
#' @return Data frame describing scenario-library entries.
#' @export
workspace_list_scenarios <- function(workspace) {
  validate_catalyst_workspace(workspace)
  if (!length(workspace$libraries$scenarios)) return(data.frame(id = character(), scenario_id = character(), title = character(), role = character(), model = character(), fingerprint = character(), stringsAsFactors = FALSE))
  do.call(rbind, lapply(workspace$libraries$scenarios, function(entry) data.frame(
    id = entry$id, scenario_id = entry$scenario$id, title = entry$scenario$title, role = entry$scenario$role,
    model = paste0(entry$scenario$model$id, "@", entry$scenario$model$version), fingerprint = entry$fingerprint,
    stringsAsFactors = FALSE
  )))
}

#' Consolidate run history across workspace projects
#'
#' @param workspace A workspace.
#' @return Data frame of project run records.
#' @export
workspace_run_history <- function(workspace) {
  validate_catalyst_workspace(workspace)
  rows <- list()
  for (project in workspace$projects) {
    for (run in project$runs) {
      rows[[length(rows) + 1L]] <- data.frame(
        project_id = project$id, project_title = project$title, run_id = run$id,
        label = run$label, status = run$status, created_at = run$created_at,
        input_hash = run$input_hash, output_hash = run$output_hash,
        review_status = run$review_status, stringsAsFactors = FALSE
      )
    }
  }
  if (!length(rows)) return(data.frame(project_id = character(), project_title = character(), run_id = character(), label = character(), status = character(), created_at = character(), input_hash = character(), output_hash = character(), review_status = character(), stringsAsFactors = FALSE))
  do.call(rbind, rows)
}

#' Compare project records in a workspace
#'
#' @param workspace A workspace.
#' @param project_ids Optional project identifiers.
#' @return Data frame comparing project scope and review state.
#' @export
workspace_compare_projects <- function(workspace, project_ids = names(workspace$projects)) {
  validate_catalyst_workspace(workspace)
  if (!is.character(project_ids) || anyNA(project_ids)) stop("`project_ids` must be a character vector.", call. = FALSE)
  missing <- setdiff(project_ids, names(workspace$projects))
  if (length(missing)) stop(sprintf("Unknown workspace projects: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  rows <- lapply(project_ids, function(id) {
    project <- workspace$projects[[id]]
    summary <- project_summary(project)
    data.frame(
      project_id = id, title = project$title, fingerprint = project_fingerprint(project),
      scenarios = summary$scenarios, datasets = summary$datasets, runs = summary$runs,
      completed_runs = summary$completed_runs, failed_runs = summary$failed_runs,
      review_status = summary$review_status, publication_status = summary$publication_status,
      stringsAsFactors = FALSE
    )
  })
  if (!length(rows)) return(data.frame())
  do.call(rbind, rows)
}

.workspace_fingerprint_record <- function(workspace) {
  list(
    schema_version = workspace$schema_version, id = workspace$id, title = workspace$title,
    description = workspace$description, owner = workspace$owner, tags = sort(workspace$tags),
    active_project_id = workspace$active_project_id,
    projects = lapply(workspace$projects, function(project) list(id = project$id, fingerprint = project_fingerprint(project))),
    scenario_library = lapply(workspace$libraries$scenarios, function(entry) list(id = entry$id, fingerprint = entry$fingerprint)),
    parameter_library = lapply(workspace$libraries$parameter_sets, function(entry) list(id = entry$id, hash = entry$hash)),
    policy_packages = lapply(workspace$libraries$policy_packages, function(entry) list(id = entry$id, hash = entry$hash)),
    regional_portfolios = lapply(workspace$libraries$regional_portfolios, function(entry) list(id = entry$id, fingerprint = .project_hash(entry))),
    policy_optimizations = lapply(workspace$libraries$policy_optimizations, function(entry) list(id = entry$id, fingerprint = entry$fingerprint)),
    policy_evaluations = lapply(workspace$libraries$policy_evaluations, function(entry) list(id = entry$id, fingerprint = entry$fingerprint)),
    policy_pathways = lapply(workspace$libraries$policy_pathways, function(entry) list(id = entry$id, fingerprint = .project_hash(entry)))
  )
}

#' Compute a stable workspace fingerprint
#'
#' @param workspace A workspace.
#' @return MD5 workspace fingerprint.
#' @export
workspace_fingerprint <- function(workspace) {
  validate_catalyst_workspace(workspace)
  restored_fingerprint <- workspace[[".restored_workspace_fingerprint", exact = TRUE]]
  if (!is.null(restored_fingerprint)) return(restored_fingerprint)
  .project_hash(.workspace_fingerprint_record(workspace))
}

.workspace_snapshot_state <- function(workspace) {
  state <- unclass(workspace)
  if (!"active_project_id" %in% names(state)) state["active_project_id"] <- list(NULL)
  state[[".restored_workspace_fingerprint"]] <- NULL
  state$snapshots <- list()
  state$activity <- list()
  state$metadata$created_at <- NULL
  state$metadata$updated_at <- NULL
  state
}

#' Snapshot a complete workspace
#'
#' @param workspace A workspace.
#' @param snapshot_id Stable snapshot identifier.
#' @param note Snapshot note.
#' @return Updated workspace.
#' @export
workspace_snapshot <- function(workspace, snapshot_id, note = "") {
  validate_catalyst_workspace(workspace)
  .workspace_id(snapshot_id, "snapshot_id")
  .assert_single_string(note, "note", allow_empty = TRUE)
  if (any(vapply(workspace$snapshots, function(x) identical(x$id, snapshot_id), logical(1)))) stop("Workspace snapshot already exists.", call. = FALSE)
  workspace$snapshots[[length(workspace$snapshots) + 1L]] <- list(
    id = snapshot_id, note = note, created_at = .utc_now(),
    workspace_fingerprint = workspace_fingerprint(workspace),
    state = .workspace_snapshot_state(workspace)
  )
  .workspace_touch(workspace, "workspace_snapshotted", list(snapshot_id = snapshot_id), semantic_change = FALSE)
}

#' Restore a workspace snapshot
#'
#' @param workspace A workspace containing the snapshot.
#' @param snapshot_id Snapshot identifier.
#' @return Restored workspace, retaining snapshot and activity history.
#' @export
workspace_restore_snapshot <- function(workspace, snapshot_id) {
  validate_catalyst_workspace(workspace)
  .workspace_id(snapshot_id, "snapshot_id")
  matches <- which(vapply(workspace$snapshots, function(x) identical(x$id, snapshot_id), logical(1)))
  if (!length(matches)) stop("Workspace snapshot is not present.", call. = FALSE)
  record <- workspace$snapshots[[matches[1L]]]
  restored <- record$state
  if (!"active_project_id" %in% names(restored)) restored["active_project_id"] <- list(NULL)
  restored$snapshots <- workspace$snapshots
  restored$activity <- workspace$activity
  restored$metadata$created_at <- workspace$metadata$created_at
  restored$metadata$updated_at <- .utc_now()
  restored$metadata$package_version <- .catalyst_package_version()
  restored[[".restored_workspace_fingerprint"]] <- NULL
  restored <- .workspace_restore_classes(restored)
  restored <- .workspace_touch(restored, "workspace_snapshot_restored", list(snapshot_id = snapshot_id), semantic_change = FALSE)
  restored[[".restored_workspace_fingerprint"]] <- record$workspace_fingerprint
  validate_catalyst_workspace(restored)
  if (!identical(workspace_fingerprint(restored), record$workspace_fingerprint)) {
    stop("Restored workspace fingerprint does not match the snapshot record.", call. = FALSE)
  }
  restored
}

#' Build a workspace manifest
#'
#' @param workspace A workspace.
#' @return Machine-readable manifest.
#' @export
workspace_manifest <- function(workspace) {
  validate_catalyst_workspace(workspace)
  list(
    schema_version = .catalyst_workspace_schema_version(), workspace_id = workspace$id,
    title = workspace$title, owner = workspace$owner, active_project_id = workspace$active_project_id,
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    fingerprint = workspace_fingerprint(workspace),
    counts = list(
      projects = length(workspace$projects), scenarios = length(workspace$libraries$scenarios),
      parameter_sets = length(workspace$libraries$parameter_sets), policy_packages = length(workspace$libraries$policy_packages),
      regional_portfolios = length(workspace$libraries$regional_portfolios), policy_optimizations = length(workspace$libraries$policy_optimizations), policy_pathways = length(workspace$libraries$policy_pathways), policy_evaluations = length(workspace$libraries$policy_evaluations), platform_handoffs = length(workspace$libraries$platform_handoffs), institutional_governance = length(workspace$libraries$institutional_governance), runs = nrow(workspace_run_history(workspace)), snapshots = length(workspace$snapshots)
    ),
    projects = lapply(workspace$projects, function(project) list(id = project$id, title = project$title, fingerprint = project_fingerprint(project), review_status = project$metadata$review_status, publication_status = project$metadata$publication_status)),
    scenario_library = lapply(workspace$libraries$scenarios, function(entry) entry[c("id", "title", "description", "tags", "source_project_id", "fingerprint")]),
    parameter_library = lapply(workspace$libraries$parameter_sets, function(entry) entry[c("id", "model", "description", "tags", "source_project_id", "hash")]),
    policy_packages = workspace$libraries$policy_packages,
    regional_portfolios = lapply(workspace$libraries$regional_portfolios, function(portfolio) list(id=portfolio$id,title=portfolio$title,members=length(portfolio$members),fingerprint=.project_hash(portfolio))),
    policy_optimizations = workspace$libraries$policy_optimizations,
    policy_evaluations = workspace$libraries$policy_evaluations,
    platform_handoffs = lapply(workspace$libraries$platform_handoffs, function(handoff) list(target = handoff$target, handoff_type = handoff$handoff_type, project_id = handoff$project_id, project_fingerprint = handoff$project_fingerprint, review_status = handoff$review$status)),
    institutional_governance = lapply(workspace$libraries$institutional_governance, governance_summary),
    policy_pathways = lapply(workspace$libraries$policy_pathways, function(pathway) list(id=pathway$id,title=pathway$title,stages=length(pathway$stages),fingerprint=.project_hash(pathway))),
    snapshots = lapply(workspace$snapshots, function(entry) entry[c("id", "note", "created_at", "workspace_fingerprint")]),
    metadata = workspace$metadata
  )
}

#' Save a workspace as canonical JSON
#'
#' @param workspace A workspace.
#' @param path Destination path.
#' @param pretty Pretty-print JSON.
#' @return Invisibly returns `path`.
#' @export
workspace_to_json <- function(workspace, path, pretty = TRUE) {
  validate_catalyst_workspace(workspace)
  .assert_single_string(path, "path")
  .assert_flag(pretty, "pretty")
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  record <- unclass(workspace)
  record[[".restored_workspace_fingerprint"]] <- NULL
  jsonlite::write_json(.safe_json_value(record), path, auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  invisible(path)
}

#' Load a workspace from canonical JSON
#'
#' @param path Workspace JSON path.
#' @return A `catalyst_workspace`.
#' @export
workspace_from_json <- function(path) {
  .assert_single_string(path, "path")
  if (!file.exists(path)) stop("Workspace JSON file does not exist.", call. = FALSE)
  workspace <- jsonlite::fromJSON(path, simplifyVector = FALSE)
  if (!is.list(workspace)) stop("Workspace JSON root must be an object.", call. = FALSE)
  if (!"active_project_id" %in% names(workspace)) workspace["active_project_id"] <- list(NULL)
  if (is.null(workspace$libraries$platform_handoffs)) workspace$libraries$platform_handoffs <- list()
  workspace <- .workspace_restore_classes(workspace)
  validate_catalyst_workspace(workspace)
  workspace
}

.workspace_index_or_empty <- function(x, columns) {
  if (is.data.frame(x) && ncol(x)) return(x)
  result <- as.data.frame(stats::setNames(replicate(length(columns), character(), simplify = FALSE), columns), stringsAsFactors = FALSE)
  result
}

.workspace_markdown <- function(workspace) {
  comparison <- workspace_compare_projects(workspace)
  history <- workspace_run_history(workspace)
  project_lines <- if (!nrow(comparison)) "- No projects registered." else vapply(seq_len(nrow(comparison)), function(i) sprintf("- **%s** (`%s`): %d scenarios, %d runs, review `%s`.", comparison$title[i], comparison$project_id[i], comparison$scenarios[i], comparison$runs[i], comparison$review_status[i]), character(1))
  c(
    paste0("# ", workspace$title), "",
    paste0("**Workspace ID:** `", workspace$id, "`  "),
    paste0("**Fingerprint:** `", workspace_fingerprint(workspace), "`  "),
    paste0("**Owner:** ", if (nzchar(workspace$owner)) workspace$owner else "Not specified", "  "),
    paste0("**Active project:** ", if (is.null(workspace$active_project_id)) "None" else paste0("`", workspace$active_project_id, "`"), "  "), "",
    "## Purpose", workspace$description, "", "## Projects", project_lines, "",
    "## Reusable libraries",
    paste0("- Scenarios: ", length(workspace$libraries$scenarios)),
    paste0("- Parameter sets: ", length(workspace$libraries$parameter_sets)),
    paste0("- Policy packages: ", length(workspace$libraries$policy_packages)),
    paste0("- Regional portfolios: ", length(workspace$libraries$regional_portfolios)),
    paste0("- Policy optimizations: ", length(workspace$libraries$policy_optimizations)),
    paste0("- Policy evaluations: ", length(workspace$libraries$policy_evaluations)),
    paste0("- Platform handoffs: ", length(workspace$libraries$platform_handoffs)),
    paste0("- Adaptive policy pathways: ", length(workspace$libraries$policy_pathways)),
    paste0("- Consolidated run records: ", nrow(history)),
    paste0("- Workspace snapshots: ", length(workspace$snapshots)), "",
    "## Boundary", "A workspace preserves reusable analytical records and restoration history. It does not establish model validity, publication approval, or decision authority."
  )
}

#' Export a complete workspace bundle
#'
#' @param workspace A workspace.
#' @param dir Parent output directory.
#' @param prefix Bundle directory name.
#' @param include_project_results Include complete project run results.
#' @param zip_bundle Create a ZIP archive.
#' @return Named generated paths.
#' @export
export_workspace <- function(workspace, dir = ".", prefix = "catalyst-workspace", include_project_results = TRUE, zip_bundle = TRUE) {
  validate_catalyst_workspace(workspace)
  .assert_single_string(dir, "dir")
  .assert_single_string(prefix, "prefix")
  .assert_flag(include_project_results, "include_project_results")
  .assert_flag(zip_bundle, "zip_bundle")
  bundle_dir <- file.path(dir, prefix)
  dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  export_record <- workspace
  if (!include_project_results) {
    export_record$projects <- lapply(export_record$projects, function(project) {
      project$runs <- lapply(project$runs, function(run) {
        run["result"] <- list(NULL)
        run
      })
      project
    })
  }
  paths <- list(bundle_dir = bundle_dir)
  paths$workspace <- file.path(bundle_dir, "workspace.json")
  workspace_to_json(export_record, paths$workspace)
  paths$workspace_manifest <- file.path(bundle_dir, "workspace-manifest.json")
  jsonlite::write_json(.safe_json_value(workspace_manifest(workspace)), paths$workspace_manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  project_index <- workspace_compare_projects(workspace)
  scenario_index <- workspace_list_scenarios(workspace)
  parameter_index <- if (!length(workspace$libraries$parameter_sets)) data.frame(id = character(), model = character(), description = character(), hash = character(), stringsAsFactors = FALSE) else do.call(rbind, lapply(workspace$libraries$parameter_sets, function(entry) data.frame(id = entry$id, model = if (is.null(entry$model)) "" else paste0(entry$model$id, "@", entry$model$version), description = entry$description, hash = entry$hash, stringsAsFactors = FALSE)))
  history <- workspace_run_history(workspace)
  paths$project_index <- file.path(bundle_dir, "project-index.csv"); utils::write.csv(.workspace_index_or_empty(project_index, c("project_id", "title", "fingerprint", "scenarios", "datasets", "runs", "completed_runs", "failed_runs", "review_status", "publication_status")), paths$project_index, row.names = FALSE)
  paths$scenario_library <- file.path(bundle_dir, "scenario-library.csv"); utils::write.csv(.workspace_index_or_empty(scenario_index, c("id", "scenario_id", "title", "role", "model", "fingerprint")), paths$scenario_library, row.names = FALSE)
  paths$parameter_library <- file.path(bundle_dir, "parameter-library.csv"); utils::write.csv(parameter_index, paths$parameter_library, row.names = FALSE)
  portfolio_index <- if (!length(workspace$libraries$regional_portfolios)) data.frame(id=character(),title=character(),members=integer(),fingerprint=character(),stringsAsFactors=FALSE) else do.call(rbind,lapply(workspace$libraries$regional_portfolios,function(portfolio)data.frame(id=portfolio$id,title=portfolio$title,members=length(portfolio$members),fingerprint=.project_hash(portfolio),stringsAsFactors=FALSE)))
  paths$regional_portfolios <- file.path(bundle_dir, "regional-portfolios.csv"); utils::write.csv(portfolio_index, paths$regional_portfolios, row.names = FALSE)
  optimization_index <- if (!length(workspace$libraries$policy_optimizations)) data.frame(id=character(),title=character(),selected_candidate_id=character(),fingerprint=character(),stringsAsFactors=FALSE) else do.call(rbind,lapply(workspace$libraries$policy_optimizations,function(entry)data.frame(id=entry$id,title=entry$title,selected_candidate_id=if(is.null(entry$selected_candidate_id))"" else entry$selected_candidate_id,fingerprint=entry$fingerprint,stringsAsFactors=FALSE)))
  paths$policy_optimizations <- file.path(bundle_dir, "policy-optimizations.csv"); utils::write.csv(optimization_index, paths$policy_optimizations, row.names = FALSE)
  pathway_index <- if (!length(workspace$libraries$policy_pathways)) data.frame(id=character(),title=character(),stages=integer(),fingerprint=character(),stringsAsFactors=FALSE) else do.call(rbind,lapply(workspace$libraries$policy_pathways,function(pathway)data.frame(id=pathway$id,title=pathway$title,stages=length(pathway$stages),fingerprint=.project_hash(pathway),stringsAsFactors=FALSE)))
  paths$policy_pathways <- file.path(bundle_dir, "policy-pathways.csv"); utils::write.csv(pathway_index, paths$policy_pathways, row.names = FALSE)
  evaluation_index <- if (!length(workspace$libraries$policy_evaluations)) data.frame(id=character(),title=character(),identification_status=character(),review_status=character(),fingerprint=character(),stringsAsFactors=FALSE) else do.call(rbind,lapply(workspace$libraries$policy_evaluations,function(entry)data.frame(id=entry$id,title=entry$title,identification_status=entry$identification_status,review_status=entry$review_status,fingerprint=entry$fingerprint,stringsAsFactors=FALSE)))
  paths$policy_evaluations <- file.path(bundle_dir, "policy-evaluations.csv"); utils::write.csv(evaluation_index, paths$policy_evaluations, row.names = FALSE)
  handoff_index <- if (!length(workspace$libraries$platform_handoffs)) data.frame(id=character(),target=character(),handoff_type=character(),project_id=character(),review_status=character(),stringsAsFactors=FALSE) else do.call(rbind,lapply(names(workspace$libraries$platform_handoffs),function(id){handoff<-workspace$libraries$platform_handoffs[[id]];data.frame(id=id,target=handoff$target,handoff_type=handoff$handoff_type,project_id=handoff$project_id,review_status=handoff$review$status,stringsAsFactors=FALSE)}))
  paths$platform_handoffs <- file.path(bundle_dir, "platform-handoffs.csv"); utils::write.csv(handoff_index, paths$platform_handoffs, row.names = FALSE)
  governance_index <- if (!length(workspace$libraries$institutional_governance)) data.frame(id=character(),project_id=character(),institution=character(),status=character(),open_change_requests=integer(),signed_releases=integer(),stringsAsFactors=FALSE) else do.call(rbind,lapply(workspace$libraries$institutional_governance,function(workflow){summary<-governance_summary(workflow);data.frame(id=workflow$id,project_id=workflow$project$id,institution=workflow$institution$name,status=workflow$status,open_change_requests=summary$open_change_requests,signed_releases=summary$signed_releases,stringsAsFactors=FALSE)}))
  paths$institutional_governance <- file.path(bundle_dir, "institutional-governance.csv"); utils::write.csv(governance_index, paths$institutional_governance, row.names = FALSE)
  paths$run_history <- file.path(bundle_dir, "run-history.csv"); utils::write.csv(.workspace_index_or_empty(history, c("project_id", "project_title", "run_id", "label", "status", "created_at", "input_hash", "output_hash", "review_status")), paths$run_history, row.names = FALSE)
  paths$readme <- file.path(bundle_dir, "README.md"); writeLines(.workspace_markdown(workspace), paths$readme, useBytes = TRUE)
  files <- list.files(bundle_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE)
  base <- normalizePath(bundle_dir)
  records <- lapply(files, function(path) list(
    file = substring(normalizePath(path), nchar(base) + 2L),
    bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path))
  ))
  export_manifest <- list(
    schema_version = .catalyst_workspace_export_schema_version(),
    export_type = "persistent_analytical_workspace_bundle",
    workspace_id = workspace$id, workspace_fingerprint = workspace_fingerprint(workspace),
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    created_at = .utc_now(), include_project_results = include_project_results,
    file_count = length(records), files = records,
    integrity = list(hash_algorithm = "md5", complete = TRUE, scope = "all_bundle_files_except_manifest"),
    boundary = list(human_review_required = TRUE, workspace_not_decision_authority = TRUE)
  )
  paths$manifest <- file.path(bundle_dir, "manifest.json")
  jsonlite::write_json(export_manifest, paths$manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (zip_bundle) {
    paths$zip <- file.path(dir, paste0(prefix, ".zip"))
    old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir)
    utils::zip(zipfile = basename(paths$zip), files = prefix)
  }
  paths
}


#' Add a reusable regional portfolio to a workspace
#' @param workspace A workspace.
#' @param portfolio Regional portfolio.
#' @param replace Replace an existing portfolio.
#' @return Updated workspace.
#' @export
workspace_add_regional_portfolio <- function(workspace, portfolio, replace=FALSE) {
  validate_catalyst_workspace(workspace); validate_regional_portfolio(portfolio); .assert_flag(replace,"replace")
  if (is.null(workspace$libraries$regional_portfolios)) workspace$libraries$regional_portfolios <- list()
  if (!is.null(workspace$libraries$regional_portfolios[[portfolio$id]]) && !replace) stop("Regional portfolio already exists in the workspace.",call.=FALSE)
  workspace$libraries$regional_portfolios[[portfolio$id]] <- portfolio
  .workspace_touch(workspace,"regional_portfolio_added",list(portfolio_id=portfolio$id))
}

#' Retrieve a reusable regional portfolio
#' @param workspace A workspace.
#' @param portfolio_id Portfolio identifier.
#' @return A regional portfolio.
#' @export
workspace_get_regional_portfolio <- function(workspace, portfolio_id) {
  validate_catalyst_workspace(workspace); .workspace_id(portfolio_id,"portfolio_id")
  portfolio <- workspace$libraries$regional_portfolios[[portfolio_id]]; if(is.null(portfolio))stop("Regional portfolio is not present in the workspace.",call.=FALSE); portfolio
}


#' Add a policy optimization to a workspace
#' @param workspace A workspace.
#' @param optimization Policy optimization result.
#' @param replace Replace an existing record.
#' @return Updated workspace.
#' @export
workspace_add_policy_optimization <- function(workspace, optimization, replace = FALSE) {
  validate_catalyst_workspace(workspace)
  if (!inherits(optimization, "catalyst_policy_optimization")) stop("`optimization` must be a policy optimization result.", call. = FALSE)
  .assert_flag(replace, "replace")
  if (is.null(workspace$libraries$policy_optimizations)) workspace$libraries$policy_optimizations <- list()
  if (!is.null(workspace$libraries$policy_optimizations[[optimization$id]]) && !replace) stop("Policy optimization already exists in the workspace.", call. = FALSE)
  workspace$libraries$policy_optimizations[[optimization$id]] <- list(
    id = optimization$id, title = optimization$title,
    selected_candidate_id = if (is.null(optimization$recommendation)) NULL else optimization$recommendation$candidate_id,
    summary = policy_optimization_summary(optimization), fingerprint = .project_hash(optimization)
  )
  .workspace_touch(workspace, "policy_optimization_added", list(optimization_id = optimization$id))
}

#' Retrieve a workspace policy optimization record
#' @param workspace A workspace.
#' @param optimization_id Optimization identifier.
#' @return Stored optimization summary record.
#' @export
workspace_get_policy_optimization <- function(workspace, optimization_id) {
  validate_catalyst_workspace(workspace); .workspace_id(optimization_id, "optimization_id")
  result <- workspace$libraries$policy_optimizations[[optimization_id]]
  if (is.null(result)) stop("Policy optimization is not present in the workspace.", call. = FALSE)
  result
}

#' Add an adaptive policy pathway to a workspace
#' @param workspace A workspace.
#' @param pathway Policy pathway.
#' @param replace Replace an existing pathway.
#' @return Updated workspace.
#' @export
workspace_add_policy_pathway <- function(workspace, pathway, replace = FALSE) {
  validate_catalyst_workspace(workspace); validate_policy_pathway(pathway); .assert_flag(replace, "replace")
  if (is.null(workspace$libraries$policy_pathways)) workspace$libraries$policy_pathways <- list()
  if (!is.null(workspace$libraries$policy_pathways[[pathway$id]]) && !replace) stop("Policy pathway already exists in the workspace.", call. = FALSE)
  workspace$libraries$policy_pathways[[pathway$id]] <- pathway
  .workspace_touch(workspace, "policy_pathway_added", list(pathway_id = pathway$id))
}

#' Retrieve an adaptive policy pathway
#' @param workspace A workspace.
#' @param pathway_id Pathway identifier.
#' @return Policy pathway.
#' @export
workspace_get_policy_pathway <- function(workspace, pathway_id) {
  validate_catalyst_workspace(workspace); .workspace_id(pathway_id, "pathway_id")
  result <- workspace$libraries$policy_pathways[[pathway_id]]
  if (is.null(result)) stop("Policy pathway is not present in the workspace.", call. = FALSE)
  result
}


#' Add a policy evaluation to a workspace
#' @param workspace A workspace.
#' @param analysis Policy-evaluation analysis.
#' @param replace Replace an existing record.
#' @return Updated workspace.
#' @export
workspace_add_policy_evaluation <- function(workspace, analysis, replace = FALSE) {
  validate_catalyst_workspace(workspace)
  if (!inherits(analysis, "catalyst_policy_evaluation_analysis")) stop("`analysis` must be a policy-evaluation analysis.", call. = FALSE)
  .assert_flag(replace, "replace")
  if (is.null(workspace$libraries$policy_evaluations)) workspace$libraries$policy_evaluations <- list()
  if (is.null(workspace$libraries$institutional_governance)) workspace$libraries$institutional_governance <- list()
  if (!is.null(workspace$libraries$policy_evaluations[[analysis$id]]) && !replace) stop("Policy evaluation already exists in the workspace.", call. = FALSE)
  workspace$libraries$policy_evaluations[[analysis$id]] <- list(
    id = analysis$id, title = analysis$title, effects = analysis$effects,
    identification_status = analysis$identification_status, review_status = analysis$review_status,
    fingerprint = .project_hash(analysis)
  )
  .workspace_touch(workspace, "policy_evaluation_added", list(evaluation_id = analysis$id))
}

#' Retrieve a workspace policy evaluation
#' @param workspace A workspace.
#' @param evaluation_id Evaluation identifier.
#' @return Stored policy-evaluation record.
#' @export
workspace_get_policy_evaluation <- function(workspace, evaluation_id) {
  validate_catalyst_workspace(workspace); .workspace_id(evaluation_id, "evaluation_id")
  result <- workspace$libraries$policy_evaluations[[evaluation_id]]
  if (is.null(result)) stop("Policy evaluation is not present in the workspace.", call. = FALSE)
  result
}

#' @export
print.catalyst_workspace <- function(x, ...) {
  manifest <- workspace_manifest(x)
  cat(sprintf("<catalyst_workspace %s>\n", x$id))
  cat(sprintf("  %s\n", x$title))
  cat(sprintf("  projects: %d | scenarios: %d | parameter sets: %d | runs: %d\n", manifest$counts$projects, manifest$counts$scenarios, manifest$counts$parameter_sets, manifest$counts$runs))
  invisible(x)
}
