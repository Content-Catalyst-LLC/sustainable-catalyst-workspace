.catalyst_model_registry <- new.env(parent = emptyenv())

.model_registry_key <- function(id, version) paste0(id, "@", version)

.validate_model_id <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[a-z][a-z0-9._-]*$", x) || nchar(x) > 100L) {
    stop(sprintf("`%s` must be at most 100 characters and use lowercase letters, numbers, dots, underscores, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

.validate_semver <- function(x, arg = "version") {
  .assert_single_string(x, arg)
  if (!grepl("^[0-9]+\\.[0-9]+\\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?$", x, perl = TRUE)) {
    stop(sprintf("`%s` must be a semantic version such as 1.0.0.", arg), call. = FALSE)
  }
  invisible(x)
}

.validate_named_spec <- function(x, arg) {
  if (!is.list(x)) stop(sprintf("`%s` must be a list.", arg), call. = FALSE)
  if (!length(x)) return(invisible(x))
  if (is.null(names(x)) || any(!nzchar(names(x))) || anyDuplicated(names(x))) {
    stop(sprintf("`%s` must be a uniquely named list.", arg), call. = FALSE)
  }
  invisible(x)
}

#' Define a Catalyst analytical model
#'
#' Creates the governed model interface used by the model registry and scenario
#' runner. A model declares its state contract, parameter and policy defaults,
#' integration methods, units, derivative function, and flow function.
#'
#' @param id Stable lowercase model identifier.
#' @param version Semantic model version.
#' @param title Human-readable model title.
#' @param description Model description.
#' @param required_states Character vector of required state names.
#' @param default_state Named numeric vector of default initial states.
#' @param default_parameters Named list of parameter defaults.
#' @param default_policy Named list of policy defaults.
#' @param integration_methods Supported integration methods.
#' @param state_units Named character vector of state units.
#' @param flow_map Named character vector mapping canonical flow names to raw
#'   names returned by `flows`.
#' @param flow_units Named character vector of canonical flow units.
#' @param indicator_map Named list of indicator definitions. Each definition must
#'   include `source`, `unit`, and `direction`.
#' @param derivative Function with signature `(t, state, policy, params)`.
#' @param flows Function with signature `(t, state, policy, params)`.
#' @param build_params Function with signature `(params, initial_state)`.
#' @param validate_state Function that validates and returns a named state.
#' @param validate_policy Function that validates a policy list.
#' @param validate_params Function that validates parameter overrides.
#' @param metadata Optional named metadata list.
#' @return An object of class `catalyst_model`.
#' @export
new_catalyst_model <- function(
  id,
  version,
  title,
  description = "",
  required_states,
  default_state,
  default_parameters,
  default_policy,
  integration_methods = c("rk4", "euler"),
  state_units,
  flow_map,
  flow_units,
  indicator_map,
  derivative,
  flows,
  build_params,
  validate_state,
  validate_policy,
  validate_params,
  metadata = list()
) {
  .validate_model_id(id)
  .validate_semver(version)
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)

  if (!is.character(required_states) || length(required_states) < 1L ||
      any(!nzchar(required_states)) || anyDuplicated(required_states)) {
    stop("`required_states` must be a non-empty vector of unique names.", call. = FALSE)
  }
  if (!is.numeric(default_state) || is.null(names(default_state)) ||
      !identical(sort(names(default_state)), sort(required_states))) {
    stop("`default_state` must be a named numeric vector matching `required_states`.", call. = FALSE)
  }
  if (any(!is.finite(default_state))) {
    stop("`default_state` must contain finite values.", call. = FALSE)
  }
  .validate_named_spec(default_parameters, "default_parameters")
  .validate_named_spec(default_policy, "default_policy")
  invalid_policy_defaults <- names(default_policy)[!vapply(default_policy, function(value) {
    is.numeric(value) && length(value) == 1L && is.finite(value)
  }, logical(1))]
  if (length(invalid_policy_defaults)) {
    stop(sprintf("Default policy values must be finite numeric scalars: %s.", paste(invalid_policy_defaults, collapse = ", ")), call. = FALSE)
  }
  if (!is.character(integration_methods) || length(integration_methods) < 1L ||
      any(!integration_methods %in% c("rk4", "euler"))) {
    stop("`integration_methods` may contain only 'rk4' and 'euler'.", call. = FALSE)
  }
  if (!is.character(state_units) || is.null(names(state_units)) ||
      !all(required_states %in% names(state_units))) {
    stop("`state_units` must name a unit for every required state.", call. = FALSE)
  }
  if (!is.character(flow_map) || is.null(names(flow_map)) || any(!nzchar(names(flow_map))) ||
      any(!nzchar(flow_map)) || anyDuplicated(names(flow_map))) {
    stop("`flow_map` must be a uniquely named character vector.", call. = FALSE)
  }
  required_flows <- c("gdp", "consumption", "savings", "education", "abatement", "emissions", "depletion", "damages")
  if (!all(required_flows %in% names(flow_map))) {
    stop(sprintf("`flow_map` must include: %s.", paste(required_flows, collapse = ", ")), call. = FALSE)
  }
  if (!is.character(flow_units) || is.null(names(flow_units)) ||
      !all(names(flow_map) %in% names(flow_units))) {
    stop("`flow_units` must name a unit for every canonical flow.", call. = FALSE)
  }
  .validate_named_spec(indicator_map, "indicator_map")
  for (indicator_name in names(indicator_map)) {
    definition <- indicator_map[[indicator_name]]
    if (!is.list(definition) || !all(c("source", "unit", "direction") %in% names(definition))) {
      stop(sprintf("Indicator `%s` must declare source, unit, and direction.", indicator_name), call. = FALSE)
    }
    .assert_single_string(definition$source, paste0("indicator_map$", indicator_name, "$source"))
    .assert_single_string(definition$unit, paste0("indicator_map$", indicator_name, "$unit"))
    .assert_single_string(definition$direction, paste0("indicator_map$", indicator_name, "$direction"))
    if (!definition$source %in% c(required_states, names(flow_map), "ans")) {
      stop(sprintf("Indicator `%s` references unknown source `%s`.", indicator_name, definition$source), call. = FALSE)
    }
    if (!definition$direction %in% c("higher_better", "lower_better", "contextual")) {
      stop(sprintf("Indicator `%s` has an invalid direction.", indicator_name), call. = FALSE)
    }
  }
  functions <- list(
    derivative = derivative,
    flows = flows,
    build_params = build_params,
    validate_state = validate_state,
    validate_policy = validate_policy,
    validate_params = validate_params
  )
  invalid_functions <- names(functions)[!vapply(functions, is.function, logical(1))]
  if (length(invalid_functions)) {
    stop(sprintf("Model callbacks must be functions: %s.", paste(invalid_functions, collapse = ", ")), call. = FALSE)
  }
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)

  structure(list(
    id = id,
    version = version,
    title = title,
    description = description,
    required_states = required_states,
    default_state = default_state[required_states],
    default_parameters = default_parameters,
    default_policy = default_policy,
    integration_methods = unique(integration_methods),
    state_units = state_units[required_states],
    flow_map = flow_map,
    flow_units = flow_units[names(flow_map)],
    indicator_map = indicator_map,
    derivative = derivative,
    flows = flows,
    build_params = build_params,
    validate_state = validate_state,
    validate_policy = validate_policy,
    validate_params = validate_params,
    metadata = metadata
  ), class = "catalyst_model")
}

#' Validate a Catalyst model definition
#'
#' @param model A `catalyst_model` object.
#' @return Invisibly returns `TRUE` when valid.
#' @export
validate_catalyst_model <- function(model) {
  if (!inherits(model, "catalyst_model")) {
    stop("`model` must inherit from `catalyst_model`.", call. = FALSE)
  }
  rebuilt <- do.call(new_catalyst_model, unclass(model))
  invisible(inherits(rebuilt, "catalyst_model"))
}

.ensure_builtin_models <- function() {
  key <- .model_registry_key("khncpa", "1.0.0")
  if (!exists(key, envir = .catalyst_model_registry, inherits = FALSE)) {
    assign(key, .khncpa_model_definition(), envir = .catalyst_model_registry)
  }
  invisible(NULL)
}

#' Register a Catalyst model
#'
#' @param model A `catalyst_model` object.
#' @param overwrite Replace an existing registration with the same id/version.
#' @return Invisibly returns the registered model.
#' @export
register_catalyst_model <- function(model, overwrite = FALSE) {
  validate_catalyst_model(model)
  .assert_flag(overwrite, "overwrite")
  .ensure_builtin_models()
  key <- .model_registry_key(model$id, model$version)
  if (exists(key, envir = .catalyst_model_registry, inherits = FALSE) && !overwrite) {
    stop(sprintf("Model %s version %s is already registered.", model$id, model$version), call. = FALSE)
  }
  assign(key, model, envir = .catalyst_model_registry)
  invisible(model)
}

.version_order <- function(versions) {
  parsed <- lapply(versions, function(value) {
    core <- sub("[-+].*$", "", value)
    as.integer(strsplit(core, "\\.", fixed = FALSE)[[1]])
  })
  matrix_values <- do.call(rbind, parsed)
  order(matrix_values[, 1], matrix_values[, 2], matrix_values[, 3], versions)
}

#' List registered Catalyst models
#'
#' @return A data frame describing registered model versions.
#' @export
list_catalyst_models <- function() {
  .ensure_builtin_models()
  keys <- ls(envir = .catalyst_model_registry, all.names = TRUE)
  if (!length(keys)) {
    return(data.frame(id = character(), version = character(), title = character(), states = character(), methods = character(), stringsAsFactors = FALSE))
  }
  rows <- lapply(keys, function(key) {
    model <- get(key, envir = .catalyst_model_registry, inherits = FALSE)
    data.frame(
      id = model$id,
      version = model$version,
      title = model$title,
      states = paste(model$required_states, collapse = ","),
      methods = paste(model$integration_methods, collapse = ","),
      stringsAsFactors = FALSE
    )
  })
  result <- do.call(rbind, rows)
  version_rank <- integer(nrow(result))
  for (model_id in unique(result$id)) {
    idx <- which(result$id == model_id)
    version_rank[idx[.version_order(result$version[idx])]] <- seq_along(idx)
  }
  result[order(result$id, version_rank), , drop = FALSE]
}

#' Retrieve a registered Catalyst model
#'
#' @param id Model identifier.
#' @param version Optional exact model version. The latest registered version is
#'   returned when omitted.
#' @return A `catalyst_model` object.
#' @export
get_catalyst_model <- function(id, version = NULL) {
  .validate_model_id(id)
  .ensure_builtin_models()
  models <- list_catalyst_models()
  available <- models[models$id == id, , drop = FALSE]
  if (!nrow(available)) stop(sprintf("Model `%s` is not registered.", id), call. = FALSE)
  if (is.null(version)) {
    version <- available$version[tail(.version_order(available$version), 1L)]
  } else {
    .validate_semver(version)
    if (!version %in% available$version) {
      stop(sprintf("Model `%s` version `%s` is not registered.", id, version), call. = FALSE)
    }
  }
  get(.model_registry_key(id, version), envir = .catalyst_model_registry, inherits = FALSE)
}

.resolve_catalyst_model <- function(model, version = NULL) {
  if (inherits(model, "catalyst_model")) {
    validate_catalyst_model(model)
    return(model)
  }
  .assert_single_string(model, "model")
  get_catalyst_model(model, version = version)
}

#' @export
print.catalyst_model <- function(x, ...) {
  cat("<catalyst_model>\n")
  cat("  id:      ", x$id, "\n", sep = "")
  cat("  version: ", x$version, "\n", sep = "")
  cat("  title:   ", x$title, "\n", sep = "")
  cat("  states:  ", paste(x$required_states, collapse = ", "), "\n", sep = "")
  cat("  methods: ", paste(x$integration_methods, collapse = ", "), "\n", sep = "")
  invisible(x)
}

#' Export a serializable model manifest
#'
#' @param model Model id or `catalyst_model` object.
#' @param version Optional exact version when `model` is an id.
#' @return A serializable named list describing the model contract.
#' @export
catalyst_model_manifest <- function(model = "khncpa", version = NULL) {
  model <- .resolve_catalyst_model(model, version)
  list(
    schema_version = "1.0.0",
    id = model$id,
    version = model$version,
    title = model$title,
    description = model$description,
    required_states = unname(model$required_states),
    default_state = as.list(model$default_state),
    default_parameters = .safe_json_value(model$default_parameters),
    default_policy = .safe_json_value(model$default_policy),
    integration_methods = unname(model$integration_methods),
    state_units = as.list(model$state_units),
    flow_map = as.list(model$flow_map),
    flow_units = as.list(model$flow_units),
    indicator_map = .safe_json_value(model$indicator_map),
    metadata = .safe_json_value(model$metadata)
  )
}
