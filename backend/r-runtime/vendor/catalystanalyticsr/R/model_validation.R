.catalyst_model_validation_schema_version <- function() "1.0.0"

#' Create calibration and holdout partitions
#'
#' @param observations Observation data frame.
#' @param holdout_fraction Fraction assigned to holdout.
#' @param time_field Time-field name.
#' @param entity_fields Optional entity fields; splitting occurs within entity.
#' @return Observation data with a `split` column.
#' @export
validation_split <- function(observations, holdout_fraction = 0.25, time_field = "time", entity_fields = character()) {
  if (!is.data.frame(observations)) stop("`observations` must be a data frame.", call. = FALSE)
  .assert_scalar_number(holdout_fraction, "holdout_fraction", lower = 0, upper = 0.9)
  .assert_single_string(time_field, "time_field")
  if (!time_field %in% names(observations)) stop("The time field is missing.", call. = FALSE)
  if (!all(entity_fields %in% names(observations))) stop("One or more entity fields are missing.", call. = FALSE)
  out <- observations
  out$split <- "calibration"
  groups <- if (length(entity_fields)) interaction(out[entity_fields], drop = TRUE, lex.order = TRUE) else factor(rep("all", nrow(out)))
  for (group in levels(groups)) {
    indices <- which(groups == group)
    indices <- indices[order(out[[time_field]][indices])]
    holdout_n <- max(1L, floor(length(indices) * holdout_fraction))
    if (holdout_fraction == 0) holdout_n <- 0L
    if (holdout_n) out$split[tail(indices, holdout_n)] <- "holdout"
  }
  out
}

#' Compute model error metrics
#'
#' @param observed Observed values.
#' @param predicted Predicted values.
#' @param weights Optional positive weights.
#' @return One-row error-metric data frame.
#' @export
model_error_metrics <- function(observed, predicted, weights = NULL) {
  if (!is.numeric(observed) || !is.numeric(predicted) || length(observed) != length(predicted) || !length(observed)) stop("Observed and predicted values must be equal-length numeric vectors.", call. = FALSE)
  keep <- is.finite(observed) & is.finite(predicted)
  observed <- observed[keep]; predicted <- predicted[keep]
  if (is.null(weights)) weights <- rep(1, length(observed)) else weights <- weights[keep]
  if (!length(observed) || any(!is.finite(weights)) || any(weights <= 0)) stop("No valid weighted observations are available.", call. = FALSE)
  weights <- weights / sum(weights)
  residual <- observed - predicted
  denominator <- pmax(abs(observed), .Machine$double.eps)
  smape_denom <- pmax(abs(observed) + abs(predicted), .Machine$double.eps)
  sst <- sum(weights * (observed - sum(weights * observed))^2)
  data.frame(
    n = length(observed), mae = sum(weights * abs(residual)), rmse = sqrt(sum(weights * residual^2)),
    mape = 100 * sum(weights * abs(residual) / denominator), smape = 200 * sum(weights * abs(residual) / smape_denom),
    bias = sum(weights * residual), r_squared = if (sst > 0) 1 - sum(weights * residual^2) / sst else NA_real_,
    stringsAsFactors = FALSE
  )
}

#' Diagnose model residuals
#'
#' @param fitted Data frame containing observed and predicted columns.
#' @return One-row residual diagnostic data frame.
#' @export
residual_diagnostics <- function(fitted) {
  if (!is.data.frame(fitted) || !all(c("observed", "predicted") %in% names(fitted))) stop("`fitted` must contain observed and predicted columns.", call. = FALSE)
  residual <- fitted$observed - fitted$predicted
  residual <- residual[is.finite(residual)]
  n <- length(residual)
  lag1 <- if (n >= 3L && stats::sd(residual[-n]) > 0 && stats::sd(residual[-1L]) > 0) stats::cor(residual[-n], residual[-1L]) else NA_real_
  fitted_values <- fitted$predicted[is.finite(fitted$observed - fitted$predicted)]
  hetero <- if (n >= 3L && stats::sd(abs(residual)) > 0 && stats::sd(fitted_values) > 0) stats::cor(abs(residual), fitted_values) else NA_real_
  shapiro_p <- if (n >= 3L && n <= 5000L && stats::sd(residual) > 0) stats::shapiro.test(residual)$p.value else NA_real_
  data.frame(
    n = n, mean_residual = mean(residual), residual_sd = if (n > 1L) stats::sd(residual) else 0,
    lag1_autocorrelation = lag1, absolute_residual_fitted_correlation = hetero,
    shapiro_wilk_p_value = shapiro_p, max_absolute_residual = max(abs(residual)), stringsAsFactors = FALSE
  )
}

.validation_metric_rows <- function(fitted) {
  splits <- unique(fitted$split)
  metrics <- unique(fitted$metric)
  rows <- list()
  diagnostics <- list()
  for (split in splits) for (metric in metrics) {
    subset <- fitted[fitted$split == split & fitted$metric == metric, , drop = FALSE]
    if (!nrow(subset)) next
    result <- model_error_metrics(subset$observed, subset$predicted, subset$weight)
    result$split <- split; result$metric <- metric
    rows[[length(rows) + 1L]] <- result[, c("split", "metric", "n", "mae", "rmse", "mape", "smape", "bias", "r_squared")]
    diagnostic <- residual_diagnostics(subset)
    diagnostic$split <- split; diagnostic$metric <- metric
    diagnostics[[length(diagnostics) + 1L]] <- diagnostic[, c("split", "metric", setdiff(names(diagnostic), c("split", "metric")))]
  }
  list(metrics = do.call(rbind, rows), diagnostics = do.call(rbind, diagnostics))
}

#' Validate calibrated model fit
#'
#' @param calibration A `catalyst_calibration`.
#' @param observations Optional replacement observations. When supplied, the
#'   calibrated scenario is evaluated against them.
#' @param thresholds Named validation thresholds including optional `rmse`,
#'   `mae`, `absolute_bias`, and `minimum_r_squared`.
#' @return A `catalyst_model_validation` object.
#' @export
validate_model_fit <- function(calibration, observations = NULL, thresholds = list()) {
  if (!inherits(calibration, "catalyst_calibration")) stop("`calibration` must be a model calibration.", call. = FALSE)
  fitted <- calibration$fitted
  if (!is.null(observations)) fitted <- .extract_run_predictions(calibration$run, .validate_observations(observations))
  if (!is.list(thresholds)) stop("`thresholds` must be a list.", call. = FALSE)
  calculated <- .validation_metric_rows(fitted)
  checks <- list()
  for (i in seq_len(nrow(calculated$metrics))) {
    row <- calculated$metrics[i, , drop = FALSE]
    add_check <- function(name, observed, operator, reference) {
      checks[[length(checks) + 1L]] <<- data.frame(split = row$split, metric = row$metric, check = name, observed = observed, operator = operator, reference = reference, passed = .evaluate_rule(observed, operator, reference), stringsAsFactors = FALSE)
    }
    if (!is.null(thresholds$rmse)) add_check("rmse", row$rmse, "<=", thresholds$rmse)
    if (!is.null(thresholds$mae)) add_check("mae", row$mae, "<=", thresholds$mae)
    if (!is.null(thresholds$absolute_bias)) add_check("absolute_bias", abs(row$bias), "<=", thresholds$absolute_bias)
    if (!is.null(thresholds$minimum_r_squared) && is.finite(row$r_squared)) add_check("minimum_r_squared", row$r_squared, ">=", thresholds$minimum_r_squared)
  }
  check_table <- if (length(checks)) do.call(rbind, checks) else data.frame(split = character(), metric = character(), check = character(), observed = numeric(), operator = character(), reference = numeric(), passed = logical())
  status <- if (!nrow(check_table)) "not_assessed" else if (all(check_table$passed)) "passed" else "failed"
  structure(list(
    schema_version = .catalyst_model_validation_schema_version(), validation_id = paste0(calibration$calibration_id, "-validation"),
    model = calibration$model, calibration_id = calibration$calibration_id, status = status,
    fitted = fitted, metrics = calculated$metrics, residual_diagnostics = calculated$diagnostics,
    thresholds = thresholds, checks = check_table,
    meta = list(package_version = .catalyst_package_version(), created_at = .utc_now(), review_status = "unreviewed")
  ), class = "catalyst_model_validation")
}

.resample_scenario_times <- function(scenario, step) {
  scenario <- as_catalyst_scenario(scenario)
  .assert_scalar_number(step, "step", lower = .Machine$double.eps)
  values <- seq(scenario$time$start, scenario$time$end, by = step)
  if (tail(values, 1L) < scenario$time$end) values <- c(values, scenario$time$end)
  scenario$time$values <- values
  scenario$time$step <- step
  as_catalyst_scenario(scenario)
}

#' Benchmark numerical solvers and time steps
#'
#' @param scenario Canonical scenario.
#' @param methods Integration methods.
#' @param step_sizes Positive time steps.
#' @param metrics Trajectory metrics used for numerical comparison.
#' @param reference_method Reference integration method.
#' @param reference_step Reference time step; defaults to the smallest supplied.
#' @return A `catalyst_solver_benchmark` object.
#' @export
solver_benchmark <- function(scenario, methods = c("rk4", "euler"), step_sizes = c(1, 0.5), metrics = c("K", "H", "N", "C", "gdp", "emissions"), reference_method = "rk4", reference_step = NULL) {
  scenario <- as_catalyst_scenario(scenario)
  if (!is.character(methods) || !length(methods)) stop("`methods` must be a character vector.", call. = FALSE)
  if (!is.numeric(step_sizes) || !length(step_sizes) || any(!is.finite(step_sizes)) || any(step_sizes <= 0)) stop("`step_sizes` must be positive finite values.", call. = FALSE)
  if (is.null(reference_step)) reference_step <- min(step_sizes)
  reference_scenario <- .resample_scenario_times(scenario, reference_step)
  reference <- run_catalyst_scenario(reference_scenario, method = reference_method, include_phase_plane = FALSE, include_sensitivity = FALSE)
  reference_final <- tail(reference$trajectory_wide, 1L)
  rows <- list(); final_values <- list()
  for (method in methods) for (step in step_sizes) {
    candidate <- .resample_scenario_times(scenario, step)
    started <- proc.time()[["elapsed"]]
    result <- tryCatch(run_catalyst_scenario(candidate, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE), error = identity)
    elapsed <- proc.time()[["elapsed"]] - started
    if (inherits(result, "error")) {
      rows[[length(rows) + 1L]] <- data.frame(method = method, step = step, success = FALSE, elapsed_seconds = elapsed, max_absolute_terminal_error = NA_real_, mean_absolute_terminal_error = NA_real_, message = conditionMessage(result), stringsAsFactors = FALSE)
      next
    }
    available <- intersect(metrics, intersect(names(result$trajectory_wide), names(reference$trajectory_wide)))
    terminal <- tail(result$trajectory_wide, 1L)
    terminal_values <- vapply(available, function(metric) as.numeric(terminal[[metric]][1L]), numeric(1))
    reference_values <- vapply(available, function(metric) as.numeric(reference_final[[metric]][1L]), numeric(1))
    errors <- abs(terminal_values - reference_values)
    rows[[length(rows) + 1L]] <- data.frame(method = method, step = step, success = TRUE, elapsed_seconds = elapsed, max_absolute_terminal_error = max(errors), mean_absolute_terminal_error = mean(errors), message = "", stringsAsFactors = FALSE)
    final_values[[length(final_values) + 1L]] <- data.frame(method = method, step = step, metric = available, final_value = unname(terminal_values), reference_value = unname(reference_values), absolute_error = unname(errors), stringsAsFactors = FALSE)
  }
  structure(list(
    schema_version = "1.0.0", scenario_id = scenario$id, reference = list(method = reference_method, step = reference_step),
    summary = do.call(rbind, rows), terminal_values = if (length(final_values)) do.call(rbind, final_values) else data.frame(),
    meta = list(created_at = .utc_now(), package_version = .catalyst_package_version())
  ), class = "catalyst_solver_benchmark")
}

#' Assess numerical stability, invariants, and boundary behavior
#'
#' @param scenario Canonical scenario.
#' @param perturbation_fraction Fractional perturbation applied to initial states.
#' @param tolerance Maximum relative terminal divergence considered stable.
#' @param invariant_states States that must remain finite and non-negative.
#' @return A `catalyst_stability_assessment` object.
#' @export
stability_assessment <- function(scenario, perturbation_fraction = 0.01, tolerance = 0.1, invariant_states = c("K", "H", "N", "P", "A")) {
  scenario <- as_catalyst_scenario(scenario)
  .assert_scalar_number(perturbation_fraction, "perturbation_fraction", lower = 0)
  .assert_scalar_number(tolerance, "tolerance", lower = 0)
  baseline <- run_catalyst_scenario(scenario, include_phase_plane = FALSE, include_sensitivity = FALSE)
  baseline_terminal <- tail(baseline$trajectory_wide, 1L)
  perturbations <- list(); rows <- list()
  for (state in intersect(names(scenario$initial_state), invariant_states)) {
    candidate <- scenario
    candidate$initial_state[[state]] <- candidate$initial_state[[state]] * (1 + perturbation_fraction)
    candidate <- as_catalyst_scenario(candidate)
    result <- run_catalyst_scenario(candidate, include_phase_plane = FALSE, include_sensitivity = FALSE)
    terminal <- tail(result$trajectory_wide, 1L)
    available <- intersect(invariant_states, names(terminal))
    terminal_values <- vapply(available, function(metric) as.numeric(terminal[[metric]][1L]), numeric(1))
    baseline_values <- vapply(available, function(metric) as.numeric(baseline_terminal[[metric]][1L]), numeric(1))
    scale <- pmax(abs(baseline_values), .Machine$double.eps)
    relative <- abs(terminal_values - baseline_values) / scale
    rows[[length(rows) + 1L]] <- data.frame(perturbation = paste0("initial_state.", state), max_relative_terminal_divergence = max(relative), stable = max(relative) <= tolerance, stringsAsFactors = FALSE)
    perturbations[[state]] <- result
  }
  invariant_rows <- lapply(intersect(invariant_states, names(baseline$trajectory_wide)), function(state) data.frame(
    invariant = paste0(state, "_finite_nonnegative"), passed = all(is.finite(baseline$trajectory_wide[[state]])) && all(baseline$trajectory_wide[[state]] >= 0), stringsAsFactors = FALSE
  ))
  invariant_rows[[length(invariant_rows) + 1L]] <- data.frame(invariant = "strictly_increasing_time", passed = !is.unsorted(baseline$trajectory_wide$t, strictly = TRUE), stringsAsFactors = FALSE)
  boundary_cases <- data.frame(
    case = c("zero_natural_capital", "zero_population", "negative_capital_rejected"),
    expected = c("runs_or_controlled_failure", "runs_or_controlled_failure", "validation_failure"),
    observed = character(3), passed = logical(3), stringsAsFactors = FALSE
  )
  case1 <- scenario; case1$initial_state$N <- 0
  outcome1 <- tryCatch({ run_catalyst_scenario(as_catalyst_scenario(case1), include_phase_plane = FALSE, include_sensitivity = FALSE); "run" }, error = function(e) "controlled_failure")
  boundary_cases$observed[1] <- outcome1; boundary_cases$passed[1] <- outcome1 %in% c("run", "controlled_failure")
  case2 <- scenario; case2$initial_state$P <- 0
  outcome2 <- tryCatch({ run_catalyst_scenario(as_catalyst_scenario(case2), include_phase_plane = FALSE, include_sensitivity = FALSE); "run" }, error = function(e) "controlled_failure")
  boundary_cases$observed[2] <- outcome2; boundary_cases$passed[2] <- outcome2 %in% c("run", "controlled_failure")
  case3 <- scenario; case3$initial_state$K <- -1
  outcome3 <- tryCatch({ as_catalyst_scenario(case3); "accepted" }, error = function(e) "validation_failure")
  boundary_cases$observed[3] <- outcome3; boundary_cases$passed[3] <- outcome3 == "validation_failure"
  perturbation_table <- if (length(rows)) do.call(rbind, rows) else data.frame()
  invariants <- do.call(rbind, invariant_rows)
  structure(list(
    schema_version = "1.0.0", scenario_id = scenario$id, perturbation_fraction = perturbation_fraction, tolerance = tolerance,
    perturbations = perturbation_table, invariants = invariants, boundary_conditions = boundary_cases,
    stable = (if (nrow(perturbation_table)) all(perturbation_table$stable) else TRUE) && all(invariants$passed) && all(boundary_cases$passed),
    meta = list(created_at = .utc_now(), package_version = .catalyst_package_version())
  ), class = "catalyst_stability_assessment")
}

#' Plot validation residuals
#'
#' @param x A `catalyst_model_validation`.
#' @return A ggplot object.
#' @export
plot_residual_diagnostics <- function(x) {
  if (!inherits(x, "catalyst_model_validation")) stop("`x` must be a model validation.", call. = FALSE)
  ggplot2::ggplot(x$fitted, ggplot2::aes(x = predicted, y = residual, colour = split)) +
    ggplot2::geom_hline(yintercept = 0, linetype = 2) + ggplot2::geom_point() +
    ggplot2::facet_wrap(~metric, scales = "free") + ggplot2::labs(x = "Predicted", y = "Observed - predicted", colour = "Split", title = "Residual diagnostics") + theme_catalyst()
}

#' Plot solver benchmark accuracy
#'
#' @param x A `catalyst_solver_benchmark`.
#' @return A ggplot object.
#' @export
plot_solver_benchmark <- function(x) {
  if (!inherits(x, "catalyst_solver_benchmark")) stop("`x` must be a solver benchmark.", call. = FALSE)
  data <- x$summary[x$summary$success, , drop = FALSE]
  ggplot2::ggplot(data, ggplot2::aes(x = step, y = max_absolute_terminal_error, colour = method)) +
    ggplot2::geom_line() + ggplot2::geom_point() + ggplot2::scale_x_reverse() +
    ggplot2::labs(x = "Time step", y = "Maximum terminal error", colour = "Method", title = "Solver benchmark") + theme_catalyst()
}

#' @export
print.catalyst_model_validation <- function(x, ...) {
  cat(sprintf("<catalyst_model_validation %s>\n", x$validation_id))
  cat(sprintf("  status: %s\n", x$status))
  cat(sprintf("  observations: %d\n", nrow(x$fitted)))
  invisible(x)
}
