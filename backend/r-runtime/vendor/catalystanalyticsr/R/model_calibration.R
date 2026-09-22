.catalyst_calibration_schema_version <- function() "1.0.0"

.validate_observations <- function(observations) {
  if (!is.data.frame(observations)) stop("`observations` must be a data frame.", call. = FALSE)
  required <- c("time", "metric", "observed")
  missing <- setdiff(required, names(observations))
  if (length(missing)) stop(sprintf("`observations` is missing: %s.", paste(missing, collapse = ", ")), call. = FALSE)
  if (!is.numeric(observations$time) || any(!is.finite(observations$time))) stop("Observation times must be finite numeric values.", call. = FALSE)
  if (!is.character(observations$metric) || any(!nzchar(observations$metric))) stop("Observation metrics must be non-empty strings.", call. = FALSE)
  if (!is.numeric(observations$observed) || any(!is.finite(observations$observed))) stop("Observed values must be finite numeric values.", call. = FALSE)
  if (!"weight" %in% names(observations)) observations$weight <- 1
  if (!is.numeric(observations$weight) || any(!is.finite(observations$weight)) || any(observations$weight <= 0)) stop("Observation weights must be positive finite values.", call. = FALSE)
  if (!"split" %in% names(observations)) observations$split <- "calibration"
  observations$split <- as.character(observations$split)
  rownames(observations) <- NULL
  observations
}

.normalize_parameter_definition <- function(x, name) {
  if (is.numeric(x) && length(x) == 1L) x <- list(initial = x)
  if (!is.list(x)) stop(sprintf("Calibration parameter `%s` must be a list or numeric scalar.", name), call. = FALSE)
  initial <- x$initial
  .assert_scalar_number(initial, paste0("parameters$", name, "$initial"))
  lower <- if (is.null(x$lower)) -Inf else x$lower
  upper <- if (is.null(x$upper)) Inf else x$upper
  .assert_scalar_number(lower, paste0("parameters$", name, "$lower"), finite = FALSE)
  .assert_scalar_number(upper, paste0("parameters$", name, "$upper"), finite = FALSE)
  if (lower > upper || initial < lower || initial > upper) stop(sprintf("Calibration bounds are invalid for `%s`.", name), call. = FALSE)
  target <- if (is.null(x$target)) paste0("parameters.", name) else x$target
  .assert_single_string(target, paste0("parameters$", name, "$target"))
  transform <- if (is.null(x$transform)) "identity" else x$transform
  .assert_single_string(transform, paste0("parameters$", name, "$transform"))
  if (!transform %in% c("identity", "log")) stop("Calibration transforms must be identity or log.", call. = FALSE)
  if (transform == "log" && (initial <= 0 || lower <= 0)) stop(sprintf("Log-transformed parameter `%s` must have positive initial and lower values.", name), call. = FALSE)
  list(name = name, target = target, initial = as.numeric(initial), lower = as.numeric(lower), upper = as.numeric(upper), transform = transform, unit = x$unit %||% "unspecified", description = x$description %||% "")
}

`%||%` <- function(x, y) if (is.null(x)) y else x

#' Define a governed model calibration
#'
#' @param parameters Named parameter definitions. Each definition may contain
#'   `target`, `initial`, `lower`, `upper`, `transform`, `unit`, and `description`.
#' @param objective Objective function: root-mean-square error, weighted RMSE,
#'   mean absolute error, or sum of squared errors.
#' @param method Optimization method passed to `stats::optim`.
#' @param maxit Maximum optimizer iterations.
#' @param tolerance Convergence tolerance recorded in the calibration contract.
#' @param id Stable calibration specification identifier.
#' @param title Human-readable title.
#' @param metadata Additional metadata.
#' @return A `catalyst_calibration_spec` object.
#' @export
calibration_spec <- function(
  parameters,
  objective = c("weighted_rmse", "rmse", "mae", "sse"),
  method = c("L-BFGS-B", "Nelder-Mead"),
  maxit = 250L,
  tolerance = 1e-8,
  id = "model-calibration",
  title = "Model calibration",
  metadata = list()
) {
  objective <- match.arg(objective)
  method <- match.arg(method)
  .validate_dataset_id(id, "id")
  .assert_single_string(title, "title")
  .assert_scalar_number(maxit, "maxit", lower = 1)
  .assert_scalar_number(tolerance, "tolerance", lower = 0)
  if (!is.list(parameters) || !length(parameters) || is.null(names(parameters)) || any(!nzchar(names(parameters))) || anyDuplicated(names(parameters))) {
    stop("`parameters` must be a non-empty uniquely named list.", call. = FALSE)
  }
  definitions <- lapply(names(parameters), function(name) .normalize_parameter_definition(parameters[[name]], name))
  names(definitions) <- names(parameters)
  structure(list(
    schema_version = .catalyst_calibration_schema_version(), id = id, title = title,
    parameters = definitions, objective = objective, method = method,
    control = list(maxit = as.integer(maxit), tolerance = tolerance),
    meta = utils::modifyList(list(created_at = .utc_now(), package_version = .catalyst_package_version()), metadata)
  ), class = "catalyst_calibration_spec")
}

.validate_calibration_targets <- function(scenario, spec) {
  for (name in names(spec$parameters)) {
    target <- spec$parameters[[name]]$target
    parts <- strsplit(target, ".", fixed = TRUE)[[1L]]
    if (length(parts) != 2L || !parts[1L] %in% c("parameters", "policy", "initial_state") || !nzchar(parts[2L])) {
      stop(sprintf("Unsupported calibration target `%s`.", target), call. = FALSE)
    }
    section <- scenario[[parts[1L]]]
    if (is.null(section) || !is.list(section) || !parts[2L] %in% names(section)) {
      stop(sprintf("Unsupported calibration target `%s`.", target), call. = FALSE)
    }
  }
  invisible(TRUE)
}

.set_scenario_target <- function(scenario, target, value) {
  parts <- strsplit(target, ".", fixed = TRUE)[[1L]]
  if (length(parts) != 2L || !parts[1L] %in% c("parameters", "policy", "initial_state")) {
    stop(sprintf("Unsupported calibration target `%s`.", target), call. = FALSE)
  }
  scenario[[parts[1L]]][[parts[2L]]] <- value
  scenario
}

.calibration_parameter_vectors <- function(spec) {
  defs <- spec$parameters
  initial <- vapply(defs, `[[`, numeric(1), "initial")
  lower <- vapply(defs, `[[`, numeric(1), "lower")
  upper <- vapply(defs, `[[`, numeric(1), "upper")
  transform <- vapply(defs, `[[`, character(1), "transform")
  to_work <- function(values) ifelse(transform == "log", log(values), values)
  finite_lower <- ifelse(transform == "log", log(lower), lower)
  finite_upper <- ifelse(transform == "log", log(upper), upper)
  list(initial = to_work(initial), lower = finite_lower, upper = finite_upper, transform = transform)
}

.from_calibration_scale <- function(values, spec) {
  transforms <- vapply(spec$parameters, `[[`, character(1), "transform")
  result <- ifelse(transforms == "log", exp(values), values)
  names(result) <- names(spec$parameters)
  result
}

.extract_run_predictions <- function(run, observations) {
  trajectory <- run$trajectory_wide
  rows <- vector("list", nrow(observations))
  for (i in seq_len(nrow(observations))) {
    metric <- observations$metric[i]
    if (!metric %in% names(trajectory)) stop(sprintf("Metric `%s` is not available in the model trajectory.", metric), call. = FALSE)
    index <- which.min(abs(trajectory$t - observations$time[i]))
    rows[[i]] <- data.frame(
      time = observations$time[i], model_time = trajectory$t[index], metric = metric,
      observed = observations$observed[i], predicted = as.numeric(trajectory[[metric]][index]),
      weight = observations$weight[i], split = observations$split[i], stringsAsFactors = FALSE
    )
  }
  out <- do.call(rbind, rows)
  out$residual <- out$observed - out$predicted
  out
}

.calibration_objective_value <- function(fitted, objective) {
  residual <- fitted$residual
  weights <- fitted$weight / sum(fitted$weight)
  switch(objective,
    weighted_rmse = sqrt(sum(weights * residual^2)),
    rmse = sqrt(mean(residual^2)),
    mae = mean(abs(residual)),
    sse = sum(residual^2)
  )
}

#' Calibrate a registered Catalyst model
#'
#' @param scenario Canonical scenario used as the calibration template.
#' @param observations Data frame with `time`, `metric`, and `observed`; optional
#'   `weight` and `split` columns are supported.
#' @param spec A `catalyst_calibration_spec`.
#' @param include_phase_plane Include phase-plane output during final execution.
#' @param include_sensitivity Include local sensitivity output during final execution.
#' @return A `catalyst_calibration` object.
#' @export
calibrate_model <- function(scenario, observations, spec, include_phase_plane = FALSE, include_sensitivity = FALSE) {
  scenario <- as_catalyst_scenario(scenario)
  observations <- .validate_observations(observations)
  if (!inherits(spec, "catalyst_calibration_spec")) stop("`spec` must be a calibration specification.", call. = FALSE)
  .validate_calibration_targets(scenario, spec)
  .assert_flag(include_phase_plane, "include_phase_plane")
  .assert_flag(include_sensitivity, "include_sensitivity")
  vectors <- .calibration_parameter_vectors(spec)
  history <- list()
  evaluate <- function(work_values) {
    values <- .from_calibration_scale(work_values, spec)
    candidate <- scenario
    for (name in names(values)) candidate <- .set_scenario_target(candidate, spec$parameters[[name]]$target, values[[name]])
    candidate <- as_catalyst_scenario(candidate)
    result <- tryCatch(run_catalyst_scenario(candidate, include_phase_plane = FALSE, include_sensitivity = FALSE), error = identity)
    if (inherits(result, "error")) return(.Machine$double.xmax / 1000)
    fitted <- .extract_run_predictions(result, observations)
    value <- .calibration_objective_value(fitted, spec$objective)
    history[[length(history) + 1L]] <<- data.frame(iteration = length(history) + 1L, objective = value, t(values), check.names = FALSE)
    value
  }
  objective_function <- function(work_values) {
    if (any(work_values < vectors$lower) || any(work_values > vectors$upper)) return(.Machine$double.xmax / 1000)
    evaluate(work_values)
  }
  optim_args <- list(par = vectors$initial, fn = objective_function, method = spec$method)
  if (identical(spec$method, "L-BFGS-B")) {
    optim_args$lower <- vectors$lower
    optim_args$upper <- vectors$upper
    optim_args$control <- list(maxit = spec$control$maxit, factr = max(spec$control$tolerance / .Machine$double.eps, 1))
  } else {
    optim_args$control <- list(maxit = spec$control$maxit, reltol = spec$control$tolerance)
  }
  optimization <- do.call(stats::optim, optim_args)
  estimates <- .from_calibration_scale(optimization$par, spec)
  calibrated_scenario <- scenario
  for (name in names(estimates)) calibrated_scenario <- .set_scenario_target(calibrated_scenario, spec$parameters[[name]]$target, estimates[[name]])
  calibrated_scenario <- as_catalyst_scenario(calibrated_scenario)
  run <- run_catalyst_scenario(calibrated_scenario, include_phase_plane = include_phase_plane, include_sensitivity = include_sensitivity)
  fitted <- .extract_run_predictions(run, observations)
  parameter_table <- do.call(rbind, lapply(names(estimates), function(name) data.frame(
    parameter = name, target = spec$parameters[[name]]$target,
    initial = spec$parameters[[name]]$initial, estimate = estimates[[name]],
    lower = spec$parameters[[name]]$lower, upper = spec$parameters[[name]]$upper,
    unit = spec$parameters[[name]]$unit, at_lower_bound = isTRUE(all.equal(estimates[[name]], spec$parameters[[name]]$lower)),
    at_upper_bound = isTRUE(all.equal(estimates[[name]], spec$parameters[[name]]$upper)), stringsAsFactors = FALSE
  )))
  history_table <- if (length(history)) do.call(rbind, history) else data.frame()
  structure(list(
    schema_version = .catalyst_calibration_schema_version(), calibration_id = spec$id,
    model = calibrated_scenario$model, scenario = calibrated_scenario, specification = spec,
    parameters = parameter_table, fitted = fitted, objective = .calibration_objective_value(fitted, spec$objective),
    convergence = list(code = optimization$convergence, message = optimization$message %||% "", evaluations = optimization$counts),
    history = history_table, run = run,
    meta = list(package_version = .catalyst_package_version(), created_at = .utc_now(), review_status = "unreviewed")
  ), class = "catalyst_calibration")
}

#' Summarize a model calibration
#'
#' @param x A `catalyst_calibration`.
#' @return One-row calibration summary.
#' @export
calibration_summary <- function(x) {
  if (!inherits(x, "catalyst_calibration")) stop("`x` must be a model calibration.", call. = FALSE)
  data.frame(
    calibration_id = x$calibration_id, model_id = x$model$id, model_version = x$model$version,
    objective = x$specification$objective, objective_value = x$objective,
    converged = x$convergence$code == 0, parameter_count = nrow(x$parameters), observation_count = nrow(x$fitted),
    stringsAsFactors = FALSE
  )
}

#' Plot observed and calibrated model values
#'
#' @param x A `catalyst_calibration`.
#' @return A ggplot object.
#' @export
plot_calibration_fit <- function(x) {
  if (!inherits(x, "catalyst_calibration")) stop("`x` must be a model calibration.", call. = FALSE)
  long <- rbind(
    data.frame(time = x$fitted$time, metric = x$fitted$metric, series = "Observed", value = x$fitted$observed),
    data.frame(time = x$fitted$time, metric = x$fitted$metric, series = "Calibrated model", value = x$fitted$predicted)
  )
  ggplot2::ggplot(long, ggplot2::aes(x = time, y = value, colour = series, linetype = series)) +
    ggplot2::geom_line() + ggplot2::geom_point() + ggplot2::facet_wrap(~metric, scales = "free_y") +
    ggplot2::labs(x = NULL, y = NULL, colour = NULL, linetype = NULL, title = x$specification$title) + theme_catalyst()
}

#' @export
print.catalyst_calibration <- function(x, ...) {
  summary <- calibration_summary(x)
  cat(sprintf("<catalyst_calibration %s>\n", x$calibration_id))
  cat(sprintf("  model: %s@%s\n", x$model$id, x$model$version))
  cat(sprintf("  objective: %s = %.6g\n", summary$objective, summary$objective_value))
  cat(sprintf("  converged: %s\n", ifelse(summary$converged, "yes", "no")))
  invisible(x)
}
