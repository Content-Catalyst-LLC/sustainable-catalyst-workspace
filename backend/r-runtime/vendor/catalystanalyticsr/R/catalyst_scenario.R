.catalyst_scenario_schema_version <- function() "1.0.0"

.slugify <- function(x) {
  x <- tolower(trimws(x))
  x <- gsub("[^a-z0-9]+", "-", x)
  x <- gsub("^-+|-+$", "", x)
  if (!nzchar(x)) x <- "scenario"
  if (!grepl("^[a-z]", x)) x <- paste0("scenario-", x)
  substr(x, 1L, 80L)
}

.utc_now <- function() format(Sys.time(), "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")

.as_scalar <- function(x, arg) {
  if (is.list(x) && length(x) == 1L) x <- x[[1L]]
  if (length(x) != 1L) stop(sprintf("`%s` must contain one value.", arg), call. = FALSE)
  x
}

.as_nullable_scalar <- function(x, arg, default = NA) {
  if (is.null(x) || length(x) == 0L) return(default)
  .as_scalar(x, arg)
}

.as_character_vector <- function(x) {
  if (is.null(x)) return(character())
  if (is.list(x)) x <- unlist(x, recursive = TRUE, use.names = FALSE)
  as.character(x)
}

.as_numeric_vector <- function(x, arg) {
  if (is.list(x)) x <- unlist(x, recursive = TRUE, use.names = FALSE)
  if (!is.numeric(x)) x <- suppressWarnings(as.numeric(x))
  if (!length(x) || any(!is.finite(x))) {
    stop(sprintf("`%s` must contain finite numeric values.", arg), call. = FALSE)
  }
  x
}

.as_named_list <- function(x, arg) {
  if (is.null(x)) return(stats::setNames(list(), character()))
  if (!is.list(x)) {
    if (is.atomic(x) && !is.null(names(x))) x <- as.list(x)
    else stop(sprintf("`%s` must be a named list.", arg), call. = FALSE)
  }
  if (!length(x)) return(stats::setNames(list(), character()))
  if (is.null(names(x)) || any(!nzchar(names(x))) || anyDuplicated(names(x))) {
    stop(sprintf("`%s` must be a uniquely named list.", arg), call. = FALSE)
  }
  x
}

.normalize_record_list <- function(x) {
  if (is.null(x) || length(x) == 0L) return(list())
  if (is.data.frame(x)) {
    return(lapply(seq_len(nrow(x)), function(i) as.list(x[i, , drop = FALSE])))
  }
  if (!is.list(x)) stop("Record collections must be lists.", call. = FALSE)
  if (!is.null(names(x)) && all(nzchar(names(x))) && !all(vapply(x, is.list, logical(1)))) {
    return(list(x))
  }
  x
}

.normalize_scenario <- function(x) {
  if (inherits(x, "catalyst_scenario")) x <- unclass(x)
  if (!is.list(x)) stop("Scenario content must be a list.", call. = FALSE)

  x$schema_version <- as.character(.as_scalar(x$schema_version, "schema_version"))
  x$id <- as.character(.as_scalar(x$id, "id"))
  x$title <- as.character(.as_scalar(x$title, "title"))
  x$role <- as.character(.as_scalar(x$role, "role"))

  x$model <- .as_named_list(x$model, "model")
  x$model$id <- as.character(.as_scalar(x$model$id, "model$id"))
  x$model$version <- as.character(.as_scalar(x$model$version, "model$version"))

  x$time <- .as_named_list(x$time, "time")
  x$time$start <- as.numeric(.as_scalar(x$time$start, "time$start"))
  x$time$end <- as.numeric(.as_scalar(x$time$end, "time$end"))
  raw_step <- .as_nullable_scalar(x$time$step, "time$step", default = NA_real_)
  x$time$step <- if (is.null(raw_step) || is.na(raw_step)) NA_real_ else as.numeric(raw_step)
  x$time$unit <- as.character(.as_scalar(x$time$unit, "time$unit"))
  x$time$values <- .as_numeric_vector(x$time$values, "time$values")

  x$initial_state <- .as_named_list(x$initial_state, "initial_state")
  x$initial_state <- lapply(x$initial_state, function(value) as.numeric(.as_scalar(value, "initial_state value")))
  x$policy <- .as_named_list(x$policy, "policy")
  x$policy <- lapply(x$policy, function(value) as.numeric(.as_scalar(value, "policy value")))
  x$parameters <- .as_named_list(x$parameters, "parameters")
  x$parameters <- lapply(x$parameters, function(value) as.numeric(.as_scalar(value, "parameter value")))
  x$constraints <- .as_named_list(x$constraints, "constraints")
  x$constraints <- lapply(x$constraints, function(value) {
    scalar <- .as_nullable_scalar(value, "constraint value", default = NA)
    if (is.numeric(scalar)) as.numeric(scalar) else scalar
  })

  x$units <- .as_named_list(x$units, "units")
  x$units$time <- as.character(.as_scalar(x$units$time, "units$time"))
  x$units$states <- .as_named_list(x$units$states, "units$states")
  x$units$states <- lapply(x$units$states, function(value) as.character(.as_scalar(value, "state unit")))
  x$units$flows <- .as_named_list(x$units$flows, "units$flows")
  x$units$flows <- lapply(x$units$flows, function(value) as.character(.as_scalar(value, "flow unit")))

  x$scope <- .as_named_list(x$scope, "scope")
  x$scope$geography <- .as_named_list(x$scope$geography, "scope$geography")
  x$scope$geography$type <- as.character(.as_scalar(x$scope$geography$type, "scope$geography$type"))
  x$scope$geography$id <- as.character(.as_scalar(x$scope$geography$id, "scope$geography$id"))
  x$scope$geography$label <- as.character(.as_scalar(x$scope$geography$label, "scope$geography$label"))
  x$scope$sectors <- .as_character_vector(x$scope$sectors)

  x$currency <- .as_named_list(x$currency, "currency")
  x$currency$code <- as.character(.as_scalar(x$currency$code, "currency$code"))
  raw_price_year <- .as_nullable_scalar(x$currency$price_year, "currency$price_year", default = NA_integer_)
  x$currency$price_year <- if (is.null(raw_price_year) || is.na(raw_price_year)) NA_integer_ else as.integer(raw_price_year)

  x$sources <- .normalize_record_list(x$sources)
  x$assumptions <- .normalize_record_list(x$assumptions)
  x$uncertainty <- lapply(.normalize_record_list(x$uncertainty), .normalize_uncertainty_spec)

  x$review <- .as_named_list(x$review, "review")
  x$review$status <- as.character(.as_scalar(x$review$status, "review$status"))
  x$review$reviewed_by <- .as_character_vector(x$review$reviewed_by)
  x$review$notes <- .as_character_vector(x$review$notes)

  x$metadata <- .as_named_list(x$metadata, "metadata")
  x$metadata$description <- as.character(.as_scalar(x$metadata$description, "metadata$description"))
  x$metadata$tags <- .as_character_vector(x$metadata$tags)
  x$metadata$created_by <- as.character(.as_scalar(x$metadata$created_by, "metadata$created_by"))
  x$metadata$created_at <- as.character(.as_scalar(x$metadata$created_at, "metadata$created_at"))
  if (!is.null(x$metadata$migrations)) x$metadata$migrations <- .as_character_vector(x$metadata$migrations)

  structure(x, class = c("catalyst_scenario", "list"))
}

#' Create a canonical Catalyst scenario
#'
#' Creates the versioned scenario contract shared by R models, JSON exports,
#' browser compatibility mappings, and future platform handoffs.
#'
#' @param title Human-readable scenario title.
#' @param id Stable scenario identifier. Derived from `title` when omitted.
#' @param model Registered model id or `catalyst_model` object.
#' @param model_version Optional exact model version.
#' @param role Scenario role: baseline, intervention, counterfactual, or exploratory.
#' @param times Strictly increasing numeric time vector.
#' @param time_unit Unit for the time axis.
#' @param initial_state Named numeric initial state. Uses model defaults when omitted.
#' @param policy Named static policy list. Uses model defaults when omitted.
#' @param parameters Named parameter override list.
#' @param constraints Named scenario constraints such as `emissions_budget`.
#' @param units Optional unit record.
#' @param scope Optional geography and sector scope.
#' @param currency Optional currency and price-year record.
#' @param sources Source records.
#' @param assumptions Assumption records.
#' @param uncertainty Uncertainty records.
#' @param review Review status record.
#' @param metadata Scenario metadata.
#' @return A validated `catalyst_scenario` object.
#' @export
catalyst_scenario <- function(
  title,
  id = NULL,
  model = "khncpa",
  model_version = NULL,
  role = c("baseline", "intervention", "counterfactual", "exploratory"),
  times = 0:20,
  time_unit = "year",
  initial_state = NULL,
  policy = NULL,
  parameters = list(),
  constraints = list(),
  units = NULL,
  scope = NULL,
  currency = NULL,
  sources = list(),
  assumptions = list(),
  uncertainty = list(),
  review = NULL,
  metadata = NULL
) {
  .assert_single_string(title, "title")
  role <- match.arg(role)
  .validate_times(times)
  .assert_single_string(time_unit, "time_unit")
  model_object <- .resolve_catalyst_model(model, model_version)

  if (is.null(id)) id <- .slugify(title)
  .validate_model_id(id, "id")
  if (is.null(initial_state)) initial_state <- model_object$default_state
  initial_state <- model_object$validate_state(initial_state)
  if (is.null(policy)) policy <- model_object$default_policy
  model_object$validate_policy(policy)
  model_object$validate_params(parameters)
  model_object$build_params(parameters, initial_state)

  if (is.null(units)) {
    units <- list(
      time = time_unit,
      states = as.list(model_object$state_units),
      flows = as.list(model_object$flow_units)
    )
  }
  if (is.null(scope)) {
    scope <- list(
      geography = list(type = "global", id = "WORLD", label = "Global"),
      sectors = "all"
    )
  }
  if (is.null(currency)) currency <- list(code = "index", price_year = NA_integer_)
  if (is.null(review)) review <- list(status = "draft", reviewed_by = character(), notes = character())
  if (is.null(metadata)) metadata <- list()
  metadata <- utils::modifyList(list(
    description = "",
    tags = character(),
    created_by = "",
    created_at = .utc_now()
  ), metadata)

  regular_step <- unique(round(diff(times), 12))
  step <- if (length(regular_step) == 1L) regular_step else NA_real_
  object <- list(
    schema_version = .catalyst_scenario_schema_version(),
    id = id,
    title = title,
    role = role,
    model = list(id = model_object$id, version = model_object$version),
    time = list(
      start = times[1L],
      end = times[length(times)],
      step = step,
      unit = time_unit,
      values = as.numeric(times)
    ),
    initial_state = as.list(initial_state[model_object$required_states]),
    policy = policy,
    parameters = parameters,
    constraints = constraints,
    units = units,
    scope = scope,
    currency = currency,
    sources = sources,
    assumptions = assumptions,
    uncertainty = uncertainty,
    review = review,
    metadata = metadata
  )
  object <- .normalize_scenario(object)
  validate_catalyst_scenario(object)
  object
}

.validate_record_ids <- function(records, kind) {
  if (!length(records)) return(invisible(TRUE))
  ids <- character(length(records))
  for (i in seq_along(records)) {
    record <- records[[i]]
    if (!is.list(record)) stop(sprintf("Every %s record must be a list.", kind), call. = FALSE)
    if (is.null(record$id)) stop(sprintf("Every %s record must include `id`.", kind), call. = FALSE)
    ids[i] <- as.character(.as_scalar(record$id, paste0(kind, "$id")))
    .validate_model_id(ids[i], paste0(kind, "$id"))
  }
  if (anyDuplicated(ids)) stop(sprintf("%s record ids must be unique.", tools::toTitleCase(kind)), call. = FALSE)
  for (record in records) {
    if (identical(kind, "source")) {
      if (is.null(record$title) || is.null(record$type)) {
        stop("Every source record must include `title` and `type`.", call. = FALSE)
      }
      .assert_single_string(as.character(.as_scalar(record$title, "source$title")), "source$title")
      .assert_single_string(as.character(.as_scalar(record$type, "source$type")), "source$type")
    } else if (identical(kind, "assumption")) {
      if (is.null(record$statement) || is.null(record$status)) {
        stop("Every assumption record must include `statement` and `status`.", call. = FALSE)
      }
      .assert_single_string(as.character(.as_scalar(record$statement, "assumption$statement")), "assumption$statement")
      status <- as.character(.as_scalar(record$status, "assumption$status"))
      if (!status %in% c("declared", "tested", "contested", "retired")) {
        stop("Assumption status is invalid.", call. = FALSE)
      }
    } else if (identical(kind, "uncertainty")) {
      validate_uncertainty_spec(record)
    }
  }
  invisible(TRUE)
}

#' Validate a canonical Catalyst scenario
#'
#' @param scenario A `catalyst_scenario` object or compatible list.
#' @param require_registered_model Require the declared model version to be registered.
#' @return Invisibly returns `TRUE` when valid.
#' @export
validate_catalyst_scenario <- function(scenario, require_registered_model = TRUE) {
  .assert_flag(require_registered_model, "require_registered_model")
  scenario <- .normalize_scenario(scenario)
  required <- c(
    "schema_version", "id", "title", "role", "model", "time", "initial_state",
    "policy", "parameters", "constraints", "units", "scope", "currency",
    "sources", "assumptions", "uncertainty", "review", "metadata"
  )
  missing <- setdiff(required, names(scenario))
  if (length(missing)) stop(sprintf("Scenario is missing fields: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  if (!identical(scenario$schema_version, .catalyst_scenario_schema_version())) {
    stop(sprintf("Unsupported scenario schema version `%s`.", scenario$schema_version), call. = FALSE)
  }
  .validate_model_id(scenario$id, "id")
  .assert_single_string(scenario$title, "title")
  if (nchar(scenario$title) > 200L) stop("`title` must be at most 200 characters.", call. = FALSE)
  if (!scenario$role %in% c("baseline", "intervention", "counterfactual", "exploratory")) {
    stop("`role` is not a supported scenario role.", call. = FALSE)
  }
  .validate_model_id(scenario$model$id, "model$id")
  .validate_semver(scenario$model$version, "model$version")

  values <- scenario$time$values
  .validate_times(values)
  if (!isTRUE(all.equal(values[1L], scenario$time$start, tolerance = 1e-12)) ||
      !isTRUE(all.equal(values[length(values)], scenario$time$end, tolerance = 1e-12))) {
    stop("Scenario time start/end do not match the time values.", call. = FALSE)
  }
  .assert_single_string(scenario$time$unit, "time$unit")
  if (!is.na(scenario$time$step)) {
    .assert_scalar_number(scenario$time$step, "time$step", lower = .Machine$double.eps)
    if (length(unique(round(diff(values), 12))) != 1L ||
        !isTRUE(all.equal(diff(values)[1L], scenario$time$step, tolerance = 1e-10))) {
      stop("Scenario time step does not match the declared time values.", call. = FALSE)
    }
  }

  if (require_registered_model) {
    model <- get_catalyst_model(scenario$model$id, scenario$model$version)
    state <- unlist(scenario$initial_state, use.names = TRUE)
    model$validate_state(state)
    model$validate_policy(scenario$policy)
    model$validate_params(scenario$parameters)
    model$build_params(scenario$parameters, state)
    if (!all(model$required_states %in% names(scenario$units$states))) {
      stop("Scenario units do not cover all model states.", call. = FALSE)
    }
    if (!all(names(model$flow_map) %in% names(scenario$units$flows))) {
      stop("Scenario units do not cover all canonical model flows.", call. = FALSE)
    }
  }

  if (!length(scenario$scope$sectors) || any(!nzchar(scenario$scope$sectors))) {
    stop("Scenario scope must include at least one sector.", call. = FALSE)
  }
  if (anyDuplicated(scenario$scope$sectors)) stop("Scenario sectors must be unique.", call. = FALSE)
  if (anyDuplicated(scenario$metadata$tags)) stop("Scenario metadata tags must be unique.", call. = FALSE)
  unit_values <- c(unlist(scenario$units$states, use.names = FALSE), unlist(scenario$units$flows, use.names = FALSE))
  if (any(!nzchar(unit_values))) stop("Scenario units must be non-empty strings.", call. = FALSE)
  for (field in c("type", "id", "label")) {
    .assert_single_string(scenario$scope$geography[[field]], paste0("scope$geography$", field))
  }
  if (!identical(scenario$units$time, scenario$time$unit)) {
    stop("Scenario time unit and unit registry do not match.", call. = FALSE)
  }
  if (!is.na(scenario$currency$price_year) &&
      (scenario$currency$price_year < 1800L || scenario$currency$price_year > 3000L)) {
    stop("Currency price year must be between 1800 and 3000.", call. = FALSE)
  }
  if (!is.null(scenario$constraints$emissions_budget) &&
      !is.na(scenario$constraints$emissions_budget)) {
    .assert_scalar_number(scenario$constraints$emissions_budget, "constraints$emissions_budget", lower = 0)
  }
  if (!grepl("^[0-9]{4}-[0-9]{2}-[0-9]{2}T", scenario$metadata$created_at)) {
    stop("Scenario metadata created_at must use an ISO-8601 timestamp.", call. = FALSE)
  }
  if (!scenario$review$status %in% c("draft", "under_review", "approved", "rejected", "archived")) {
    stop("Scenario review status is invalid.", call. = FALSE)
  }
  .validate_record_ids(scenario$sources, "source")
  .validate_record_ids(scenario$assumptions, "assumption")
  .validate_record_ids(scenario$uncertainty, "uncertainty")
  if (length(scenario$uncertainty)) invisible(lapply(scenario$uncertainty, validate_uncertainty_spec, scenario = scenario))
  invisible(TRUE)
}

#' Coerce content to a canonical Catalyst scenario
#'
#' @param x Scenario list, JSON text, or JSON file path.
#' @param migrate Migrate supported legacy records to the current schema.
#' @return A validated `catalyst_scenario`.
#' @export
as_catalyst_scenario <- function(x, migrate = TRUE) {
  .assert_flag(migrate, "migrate")
  if (is.character(x) && length(x) == 1L) return(scenario_from_json(x, migrate = migrate))
  if (!is.list(x)) stop("`x` must be a scenario list, JSON string, or JSON path.", call. = FALSE)
  if (migrate) x <- migrate_catalyst_scenario(x)
  x <- .normalize_scenario(x)
  validate_catalyst_scenario(x)
  x
}

#' Serialize a Catalyst scenario to JSON
#'
#' @param scenario Scenario object or compatible list.
#' @param path Optional output path. When omitted, returns JSON text.
#' @param pretty Pretty-print JSON.
#' @return JSON text when `path` is omitted; otherwise invisibly returns `path`.
#' @export
scenario_to_json <- function(scenario, path = NULL, pretty = TRUE) {
  .assert_flag(pretty, "pretty")
  scenario <- as_catalyst_scenario(scenario)
  payload <- jsonlite::toJSON(
    .safe_json_value(unclass(scenario)),
    auto_unbox = TRUE,
    pretty = pretty,
    null = "null",
    na = "null",
    digits = NA
  )
  if (is.null(path)) return(as.character(payload))
  .assert_single_string(path, "path")
  parent <- dirname(path)
  if (!dir.exists(parent) && !dir.create(parent, recursive = TRUE, showWarnings = FALSE)) {
    stop("Could not create scenario output directory.", call. = FALSE)
  }
  writeLines(as.character(payload), path, useBytes = TRUE)
  invisible(path)
}

#' Read a Catalyst scenario from JSON
#'
#' @param json JSON text or path to a JSON file.
#' @param migrate Migrate supported legacy scenario records.
#' @return A validated `catalyst_scenario`.
#' @export
scenario_from_json <- function(json, migrate = TRUE) {
  .assert_single_string(json, "json")
  .assert_flag(migrate, "migrate")
  looks_like_json <- grepl("^[[:space:]]*(\\{|\\[)", json)
  text <- if (!looks_like_json && file.exists(json)) {
    paste(readLines(json, warn = FALSE, encoding = "UTF-8"), collapse = "\n")
  } else json
  parsed <- jsonlite::fromJSON(text, simplifyVector = FALSE)
  if (migrate) parsed <- migrate_catalyst_scenario(parsed)
  parsed <- .normalize_scenario(parsed)
  validate_catalyst_scenario(parsed)
  parsed
}

#' Compute a stable scenario fingerprint
#'
#' @param scenario Scenario object or compatible list.
#' @return An MD5 fingerprint of compact canonical JSON.
#' @export
scenario_fingerprint <- function(scenario) {
  json <- scenario_to_json(scenario, pretty = FALSE)
  path <- tempfile(fileext = ".json")
  on.exit(unlink(path, force = TRUE), add = TRUE)
  writeLines(json, path, useBytes = TRUE)
  unname(tools::md5sum(path))
}

#' Run a canonical Catalyst scenario
#'
#' @param scenario Scenario object, JSON text, or JSON path.
#' @param method Optional integration method override.
#' @param include_phase_plane Include the KH-NC-PA phase plane when supported.
#' @param include_sensitivity Include local sensitivity output when supported.
#' @return A `catalyst_run` containing the canonical scenario record.
#' @export
run_catalyst_scenario <- function(
  scenario,
  method = NULL,
  include_phase_plane = TRUE,
  include_sensitivity = TRUE
) {
  scenario <- as_catalyst_scenario(scenario)
  model <- get_catalyst_model(scenario$model$id, scenario$model$version)
  if (is.null(method)) method <- model$integration_methods[1L]
  .assert_single_string(method, "method")
  if (!method %in% model$integration_methods) {
    stop(sprintf("Model `%s` does not support integration method `%s`.", model$id, method), call. = FALSE)
  }
  budget <- scenario$constraints$emissions_budget
  if (!is.null(budget)) {
    budget <- as.numeric(budget)
    if (length(budget) == 1L && is.na(budget)) budget <- NULL
  }
  result <- catalyst_run(
    times = scenario$time$values,
    x0 = unlist(scenario$initial_state, use.names = TRUE),
    policy = scenario$policy,
    params = scenario$parameters,
    scenario = scenario$id,
    model = model,
    method = method,
    emissions_budget = budget,
    include_phase_plane = include_phase_plane,
    include_sensitivity = include_sensitivity
  )
  result$scenario <- scenario
  result$meta$scenario_id <- scenario$id
  result$meta$scenario_title <- scenario$title
  result$meta$scenario_role <- scenario$role
  result$meta$scenario_schema_version <- scenario$schema_version
  result$meta$scenario_fingerprint <- scenario_fingerprint(scenario)
  result
}

#' @export
print.catalyst_scenario <- function(x, ...) {
  cat("<catalyst_scenario>\n")
  cat("  id:      ", x$id, "\n", sep = "")
  cat("  title:   ", x$title, "\n", sep = "")
  cat("  role:    ", x$role, "\n", sep = "")
  cat("  model:   ", x$model$id, "@", x$model$version, "\n", sep = "")
  cat("  horizon: ", x$time$start, " to ", x$time$end, " ", x$time$unit, "\n", sep = "")
  cat("  review:  ", x$review$status, "\n", sep = "")
  invisible(x)
}
