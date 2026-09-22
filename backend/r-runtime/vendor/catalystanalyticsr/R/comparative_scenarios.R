.normalize_scenario_collection <- function(scenarios) {
  if (inherits(scenarios, "catalyst_scenario") || is.character(scenarios)) {
    scenarios <- list(scenarios)
  }
  if (!is.list(scenarios) || !length(scenarios)) {
    stop("`scenarios` must be a non-empty list of canonical scenarios or JSON records.", call. = FALSE)
  }
  out <- lapply(scenarios, as_catalyst_scenario)
  ids <- vapply(out, function(scenario) scenario$id, character(1))
  if (anyDuplicated(ids)) stop("Scenario ids must be unique within a scenario set.", call. = FALSE)
  names(out) <- ids
  out
}

.resolve_scenario_method <- function(method, scenario, model) {
  if (is.null(method)) return(model$integration_methods[1L])
  selected <- method
  if (length(method) > 1L) {
    if (is.null(names(method)) || !scenario$id %in% names(method)) {
      stop("A multi-value `method` argument must be named by scenario id.", call. = FALSE)
    }
    selected <- method[[scenario$id]]
  }
  .assert_single_string(selected, "method")
  if (!selected %in% model$integration_methods) {
    stop(sprintf("Model `%s` does not support integration method `%s`.", model$id, selected), call. = FALSE)
  }
  selected
}

#' Run a governed set of Catalyst scenarios
#'
#' Executes canonical baseline, intervention, counterfactual, or exploratory
#' scenarios and preserves their identities, roles, model versions, and errors
#' in one comparison-ready object.
#'
#' @param scenarios Non-empty list of `catalyst_scenario` objects, JSON strings,
#'   or JSON paths.
#' @param method Optional integration method. Supply one value for every
#'   scenario or a named character vector keyed by scenario id.
#' @param include_phase_plane Include supported phase-plane outputs.
#' @param include_sensitivity Include supported local-sensitivity outputs.
#' @param continue_on_error Continue running the remaining scenarios when one
#'   scenario fails.
#' @return A `catalyst_scenario_set` containing named runs, scenario index, and
#'   any execution errors.
#' @export
run_scenarios <- function(
  scenarios,
  method = NULL,
  include_phase_plane = FALSE,
  include_sensitivity = FALSE,
  continue_on_error = FALSE
) {
  .assert_flag(include_phase_plane, "include_phase_plane")
  .assert_flag(include_sensitivity, "include_sensitivity")
  .assert_flag(continue_on_error, "continue_on_error")
  scenarios <- .normalize_scenario_collection(scenarios)

  runs <- list()
  errors <- list()
  for (scenario in scenarios) {
    model <- get_catalyst_model(scenario$model$id, scenario$model$version)
    selected_method <- .resolve_scenario_method(method, scenario, model)
    result <- tryCatch(
      run_catalyst_scenario(
        scenario,
        method = selected_method,
        include_phase_plane = include_phase_plane,
        include_sensitivity = include_sensitivity
      ),
      error = function(error) error
    )
    if (inherits(result, "error")) {
      errors[[length(errors) + 1L]] <- data.frame(
        scenario_id = scenario$id,
        scenario_title = scenario$title,
        message = conditionMessage(result),
        stringsAsFactors = FALSE
      )
      if (!continue_on_error) {
        stop(sprintf("Scenario `%s` failed: %s", scenario$id, conditionMessage(result)), call. = FALSE)
      }
    } else {
      runs[[scenario$id]] <- result
    }
  }

  error_table <- if (length(errors)) do.call(rbind, errors) else data.frame(
    scenario_id = character(), scenario_title = character(), message = character(), stringsAsFactors = FALSE
  )
  scenario_index <- do.call(rbind, lapply(scenarios, function(scenario) {
    data.frame(
      scenario_id = scenario$id,
      scenario_title = scenario$title,
      role = scenario$role,
      model_id = scenario$model$id,
      model_version = scenario$model$version,
      start = scenario$time$start,
      end = scenario$time$end,
      time_unit = scenario$time$unit,
      fingerprint = scenario_fingerprint(scenario),
      status = if (scenario$id %in% names(runs)) "completed" else "failed",
      stringsAsFactors = FALSE
    )
  }))

  structure(list(
    scenarios = scenarios,
    runs = runs,
    index = scenario_index,
    errors = error_table,
    meta = list(
      schema_version = "1.0.0",
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      requested = length(scenarios),
      completed = length(runs),
      failed = nrow(error_table)
    )
  ), class = "catalyst_scenario_set")
}

#' @export
print.catalyst_scenario_set <- function(x, ...) {
  cat("<catalyst_scenario_set>\n")
  cat("  requested: ", x$meta$requested, "\n", sep = "")
  cat("  completed: ", x$meta$completed, "\n", sep = "")
  cat("  failed:    ", x$meta$failed, "\n", sep = "")
  if (nrow(x$index)) {
    cat("  scenarios: ", paste(x$index$scenario_id, collapse = ", "), "\n", sep = "")
  }
  invisible(x)
}

.as_scenario_set <- function(x) {
  if (inherits(x, "catalyst_scenario_set")) return(x)
  if (inherits(x, "catalyst_comparison")) return(x$scenario_set)
  if (inherits(x, "catalyst_run")) {
    x <- list(x)
  }
  if (is.list(x) && length(x) && all(vapply(x, inherits, logical(1), what = "catalyst_run"))) {
    ids <- vapply(x, function(run) {
      if (!is.null(run$scenario$id)) run$scenario$id else run$meta$scenario_id
    }, character(1))
    if (any(!nzchar(ids)) || anyDuplicated(ids)) stop("Runs must have unique scenario ids.", call. = FALSE)
    names(x) <- ids
    scenarios <- lapply(x, function(run) as_catalyst_scenario(run$scenario))
    index <- do.call(rbind, lapply(x, function(run) {
      scenario <- as_catalyst_scenario(run$scenario)
      data.frame(
        scenario_id = scenario$id,
        scenario_title = scenario$title,
        role = scenario$role,
        model_id = scenario$model$id,
        model_version = scenario$model$version,
        start = scenario$time$start,
        end = scenario$time$end,
        time_unit = scenario$time$unit,
        fingerprint = scenario_fingerprint(scenario),
        status = "completed",
        stringsAsFactors = FALSE
      )
    }))
    return(structure(list(
      scenarios = scenarios,
      runs = x,
      index = index,
      errors = data.frame(scenario_id = character(), scenario_title = character(), message = character(), stringsAsFactors = FALSE),
      meta = list(schema_version = "1.0.0", package_version = .catalyst_package_version(), created_at = .utc_now(), requested = length(x), completed = length(x), failed = 0L)
    ), class = "catalyst_scenario_set"))
  }
  run_scenarios(x)
}

.common_comparison_metrics <- function(runs) {
  indicator_sets <- lapply(runs, function(run) unique(as.character(run$sdg_indicators$indicator)))
  common <- Reduce(intersect, indicator_sets)
  preferred <- c("gdp", "gdp_per_capita", "emissions", "emissions_per_capita", "carbon_intensity", "ans", "natural_capital", "atmospheric_carbon")
  c(intersect(preferred, common), setdiff(common, preferred))
}

.metric_direction_table <- function(runs, metrics) {
  rows <- lapply(metrics, function(metric) {
    directions <- unique(unlist(lapply(runs, function(run) {
      values <- run$sdg_indicators$direction[run$sdg_indicators$indicator == metric]
      as.character(values)
    }), use.names = FALSE))
    directions <- directions[nzchar(directions)]
    if (length(directions) != 1L || !directions %in% c("higher_better", "lower_better", "contextual")) {
      stop(sprintf("Metric `%s` does not have one consistent comparison direction.", metric), call. = FALSE)
    }
    units <- unique(unlist(lapply(runs, function(run) {
      values <- run$sdg_indicators$unit[run$sdg_indicators$indicator == metric]
      as.character(values)
    }), use.names = FALSE))
    units <- units[nzchar(units)]
    data.frame(metric = metric, direction = directions, unit = if (length(units) == 1L) units else "mixed", stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

.comparison_values <- function(set, metrics, directions) {
  rows <- list()
  for (scenario_id in names(set$runs)) {
    run <- set$runs[[scenario_id]]
    scenario <- as_catalyst_scenario(run$scenario)
    for (metric in metrics) {
      values <- run$sdg_indicators[run$sdg_indicators$indicator == metric, , drop = FALSE]
      values <- values[order(values$t), , drop = FALSE]
      if (!nrow(values)) next
      start_value <- as.numeric(values$value[1L])
      final_value <- as.numeric(values$value[nrow(values)])
      direction_row <- directions[directions$metric == metric, , drop = FALSE]
      rows[[length(rows) + 1L]] <- data.frame(
        scenario_id = scenario$id,
        scenario_title = scenario$title,
        role = scenario$role,
        metric = metric,
        unit = direction_row$unit[1L],
        direction = direction_row$direction[1L],
        start_value = start_value,
        final_value = final_value,
        within_scenario_change = final_value - start_value,
        within_scenario_pct_change = if (is.finite(start_value) && start_value != 0) (final_value - start_value) / abs(start_value) else NA_real_,
        stringsAsFactors = FALSE
      )
    }
  }
  do.call(rbind, rows)
}

.resolve_baseline_id <- function(set, baseline = NULL) {
  completed <- set$index[set$index$status == "completed", , drop = FALSE]
  if (!nrow(completed)) stop("No completed scenarios are available for comparison.", call. = FALSE)
  if (!is.null(baseline)) {
    .assert_single_string(baseline, "baseline")
    if (!baseline %in% completed$scenario_id) stop("`baseline` is not a completed scenario id.", call. = FALSE)
    return(baseline)
  }
  candidates <- completed$scenario_id[completed$role == "baseline"]
  if (length(candidates) > 1L) stop("Multiple baseline scenarios are present; select one with `baseline`.", call. = FALSE)
  if (length(candidates) == 1L) return(candidates)
  completed$scenario_id[1L]
}

.normalize_rule_table <- function(rules, kind, direction_table) {
  if (is.null(rules) || !length(rules)) {
    return(data.frame(metric = character(), kind = character(), value = numeric(), operator = character(), stringsAsFactors = FALSE))
  }
  if (is.atomic(rules) && !is.null(names(rules))) rules <- as.list(rules)
  if (!is.list(rules) || is.null(names(rules)) || any(!nzchar(names(rules))) || anyDuplicated(names(rules))) {
    stop(sprintf("`%s` must be a uniquely named numeric vector or list.", kind), call. = FALSE)
  }
  rows <- lapply(names(rules), function(metric) {
    if (!metric %in% direction_table$metric) stop(sprintf("%s metric `%s` is not in the comparison.", tools::toTitleCase(kind), metric), call. = FALSE)
    item <- rules[[metric]]
    operator <- NULL
    value <- item
    if (is.list(item)) {
      value <- item$value
      operator <- item$operator
    }
    .assert_scalar_number(value, paste0(kind, "$", metric))
    direction <- direction_table$direction[match(metric, direction_table$metric)]
    if (is.null(operator)) operator <- if (identical(direction, "lower_better")) "<=" else ">="
    .assert_single_string(operator, paste0(kind, "$", metric, "$operator"))
    if (!operator %in% c(">=", "<=", ">", "<", "==")) stop("Comparison rule operators must be >=, <=, >, <, or ==.", call. = FALSE)
    data.frame(metric = metric, kind = kind, value = as.numeric(value), operator = operator, stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

.evaluate_rule <- function(value, operator, reference) {
  switch(operator,
    ">=" = value >= reference,
    "<=" = value <= reference,
    ">" = value > reference,
    "<" = value < reference,
    "==" = isTRUE(all.equal(value, reference, tolerance = 1e-10)),
    FALSE
  )
}

.build_rule_results <- function(values, rules) {
  if (!nrow(rules)) {
    return(data.frame(
      scenario_id = character(), metric = character(), kind = character(), rule_value = numeric(), operator = character(),
      observed_value = numeric(), met = logical(), distance = numeric(), stringsAsFactors = FALSE
    ))
  }
  rows <- list()
  for (i in seq_len(nrow(rules))) {
    rule <- rules[i, , drop = FALSE]
    candidates <- values[values$metric == rule$metric, , drop = FALSE]
    for (j in seq_len(nrow(candidates))) {
      observed <- candidates$final_value[j]
      rows[[length(rows) + 1L]] <- data.frame(
        scenario_id = candidates$scenario_id[j],
        metric = rule$metric,
        kind = rule$kind,
        rule_value = rule$value,
        operator = rule$operator,
        observed_value = observed,
        met = .evaluate_rule(observed, rule$operator, rule$value),
        distance = observed - rule$value,
        stringsAsFactors = FALSE
      )
    }
  }
  do.call(rbind, rows)
}

.build_deltas <- function(values, baseline_id) {
  rows <- list()
  for (metric in unique(values$metric)) {
    metric_values <- values[values$metric == metric, , drop = FALSE]
    baseline_row <- metric_values[metric_values$scenario_id == baseline_id, , drop = FALSE]
    if (nrow(baseline_row) != 1L) stop(sprintf("Baseline metric `%s` is missing or duplicated.", metric), call. = FALSE)
    for (i in seq_len(nrow(metric_values))) {
      delta <- metric_values$final_value[i] - baseline_row$final_value[1L]
      pct_delta <- if (is.finite(baseline_row$final_value[1L]) && baseline_row$final_value[1L] != 0) delta / abs(baseline_row$final_value[1L]) else NA_real_
      direction <- metric_values$direction[i]
      favorable <- if (metric_values$scenario_id[i] == baseline_id) NA else if (identical(direction, "higher_better")) delta > 0 else if (identical(direction, "lower_better")) delta < 0 else NA
      rows[[length(rows) + 1L]] <- data.frame(
        scenario_id = metric_values$scenario_id[i],
        scenario_title = metric_values$scenario_title[i],
        role = metric_values$role[i],
        baseline_id = baseline_id,
        metric = metric,
        unit = metric_values$unit[i],
        direction = direction,
        baseline_value = baseline_row$final_value[1L],
        scenario_value = metric_values$final_value[i],
        absolute_delta = delta,
        percentage_delta = pct_delta,
        favorable_vs_baseline = favorable,
        outcome = if (metric_values$scenario_id[i] == baseline_id || abs(delta) <= 1e-12) "tied" else if (isTRUE(favorable)) "improved" else if (isFALSE(favorable)) "worsened" else "contextual",
        stringsAsFactors = FALSE
      )
    }
  }
  do.call(rbind, rows)
}

.build_rankings <- function(values) {
  rows <- list()
  for (metric in unique(values$metric)) {
    candidates <- values[values$metric == metric, , drop = FALSE]
    direction <- candidates$direction[1L]
    rank_values <- if (identical(direction, "lower_better")) candidates$final_value else -candidates$final_value
    candidates$rank <- rank(rank_values, ties.method = "min", na.last = "keep")
    candidates$rank_count <- nrow(candidates)
    rows[[length(rows) + 1L]] <- candidates[, c("scenario_id", "scenario_title", "role", "metric", "unit", "direction", "final_value", "rank", "rank_count"), drop = FALSE]
  }
  do.call(rbind, rows)
}

.build_tradeoffs <- function(deltas, baseline_id) {
  scenario_ids <- setdiff(unique(deltas$scenario_id), baseline_id)
  if (!length(scenario_ids)) return(data.frame(
    scenario_id = character(), baseline_id = character(), improved_metrics = character(), worsened_metrics = character(),
    tied_metrics = character(), improved_count = integer(), worsened_count = integer(), tied_count = integer(), classification = character(), stringsAsFactors = FALSE
  ))
  rows <- lapply(scenario_ids, function(id) {
    subset <- deltas[deltas$scenario_id == id, , drop = FALSE]
    improved <- subset$metric[subset$outcome == "improved"]
    worsened <- subset$metric[subset$outcome == "worsened"]
    tied <- subset$metric[subset$outcome %in% c("tied", "contextual")]
    classification <- if (length(improved) && !length(worsened)) {
      "dominates_baseline"
    } else if (!length(improved) && length(worsened)) {
      "dominated_by_baseline"
    } else if (length(improved) && length(worsened)) {
      "tradeoff"
    } else {
      "equivalent_or_contextual"
    }
    data.frame(
      scenario_id = id,
      baseline_id = baseline_id,
      improved_metrics = paste(improved, collapse = ","),
      worsened_metrics = paste(worsened, collapse = ","),
      tied_metrics = paste(tied, collapse = ","),
      improved_count = length(improved),
      worsened_count = length(worsened),
      tied_count = length(tied),
      classification = classification,
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}

.pareto_dominates <- function(a, b, tolerance = 1e-12) {
  all(a >= b - tolerance) && any(a > b + tolerance)
}

.build_pareto <- function(values) {
  scenario_ids <- unique(values$scenario_id)
  metrics <- unique(values$metric)
  matrix_values <- matrix(NA_real_, nrow = length(scenario_ids), ncol = length(metrics), dimnames = list(scenario_ids, metrics))
  for (i in seq_len(nrow(values))) matrix_values[values$scenario_id[i], values$metric[i]] <- values$final_value[i]
  direction_lookup <- stats::setNames(values$direction[match(metrics, values$metric)], metrics)
  oriented <- matrix_values
  for (metric in metrics) if (identical(direction_lookup[[metric]], "lower_better")) oriented[, metric] <- -oriented[, metric]

  dominance_rows <- list()
  dominates_count <- stats::setNames(integer(length(scenario_ids)), scenario_ids)
  dominated_by_count <- stats::setNames(integer(length(scenario_ids)), scenario_ids)
  for (i in seq_along(scenario_ids)) {
    for (j in seq_along(scenario_ids)) {
      if (i == j) next
      if (.pareto_dominates(oriented[i, ], oriented[j, ])) {
        dominance_rows[[length(dominance_rows) + 1L]] <- data.frame(
          dominator = scenario_ids[i], dominated = scenario_ids[j], stringsAsFactors = FALSE
        )
        dominates_count[i] <- dominates_count[i] + 1L
        dominated_by_count[j] <- dominated_by_count[j] + 1L
      }
    }
  }
  dominance <- if (length(dominance_rows)) do.call(rbind, dominance_rows) else data.frame(dominator = character(), dominated = character(), stringsAsFactors = FALSE)

  remaining <- scenario_ids
  layer <- stats::setNames(integer(length(scenario_ids)), scenario_ids)
  rank_number <- 1L
  while (length(remaining)) {
    front <- remaining[vapply(remaining, function(id) {
      !any(vapply(setdiff(remaining, id), function(other) .pareto_dominates(oriented[other, ], oriented[id, ]), logical(1)))
    }, logical(1))]
    layer[front] <- rank_number
    remaining <- setdiff(remaining, front)
    rank_number <- rank_number + 1L
  }
  front <- data.frame(
    scenario_id = scenario_ids,
    pareto_rank = unname(layer[scenario_ids]),
    non_dominated = unname(layer[scenario_ids]) == 1L,
    dominates_count = unname(dominates_count[scenario_ids]),
    dominated_by_count = unname(dominated_by_count[scenario_ids]),
    stringsAsFactors = FALSE
  )
  list(front = front, dominance = dominance, metrics = metrics)
}

.build_comparison_scorecard <- function(values, deltas, rankings, rule_results, pareto) {
  out <- merge(values, deltas[, c("scenario_id", "metric", "baseline_id", "baseline_value", "absolute_delta", "percentage_delta", "favorable_vs_baseline", "outcome")], by = c("scenario_id", "metric"), all.x = TRUE, sort = FALSE)
  out <- merge(out, rankings[, c("scenario_id", "metric", "rank", "rank_count")], by = c("scenario_id", "metric"), all.x = TRUE, sort = FALSE)
  if (nrow(rule_results)) {
    for (kind in unique(rule_results$kind)) {
      subset <- rule_results[rule_results$kind == kind, c("scenario_id", "metric", "rule_value", "operator", "met", "distance"), drop = FALSE]
      names(subset)[3:6] <- paste0(kind, c("_value", "_operator", "_met", "_distance"))
      out <- merge(out, subset, by = c("scenario_id", "metric"), all.x = TRUE, sort = FALSE)
    }
  }
  out <- merge(out, pareto$front, by = "scenario_id", all.x = TRUE, sort = FALSE)
  out[order(out$metric, out$rank, out$scenario_id), , drop = FALSE]
}

#' Compare a set of completed Catalyst scenarios
#'
#' @param x A `catalyst_scenario_set`, list of `catalyst_run` objects, or list
#'   of canonical scenarios.
#' @param baseline Optional baseline scenario id. When omitted, the single
#'   scenario with role `baseline` is used, otherwise the first scenario.
#' @param metrics Optional indicator names. Defaults to all common indicators.
#' @param targets Optional named target rules. Values may be numeric scalars or
#'   lists containing `value` and `operator`.
#' @param thresholds Optional named threshold rules with the same structure as
#'   `targets`.
#' @return A `catalyst_comparison` containing values, deltas, rankings,
#'   scorecards, trade-offs, rule results, and Pareto diagnostics.
#' @export
compare_scenarios <- function(x, baseline = NULL, metrics = NULL, targets = list(), thresholds = list()) {
  set <- .as_scenario_set(x)
  if (length(set$runs) < 2L) stop("At least two completed scenarios are required for comparison.", call. = FALSE)
  model_pairs <- unique(vapply(set$runs, function(run) paste0(run$meta$model, "@", run$meta$model_version), character(1)))
  if (length(model_pairs) != 1L) stop("Comparative scenarios must use the same model id and version.", call. = FALSE)

  common <- .common_comparison_metrics(set$runs)
  if (is.null(metrics)) metrics <- common
  if (!is.character(metrics) || !length(metrics) || any(!nzchar(metrics)) || anyDuplicated(metrics)) {
    stop("`metrics` must be a non-empty vector of unique indicator names.", call. = FALSE)
  }
  unavailable <- setdiff(metrics, common)
  if (length(unavailable)) stop(sprintf("Metrics are not available across every run: %s.", paste(unavailable, collapse = ", ")), call. = FALSE)

  baseline_id <- .resolve_baseline_id(set, baseline)
  directions <- .metric_direction_table(set$runs, metrics)
  values <- .comparison_values(set, metrics, directions)
  target_rules <- .normalize_rule_table(targets, "target", directions)
  threshold_rules <- .normalize_rule_table(thresholds, "threshold", directions)
  rules <- rbind(target_rules, threshold_rules)
  rule_results <- .build_rule_results(values, rules)
  deltas <- .build_deltas(values, baseline_id)
  rankings <- .build_rankings(values)
  pareto <- .build_pareto(values)
  tradeoffs <- .build_tradeoffs(deltas, baseline_id)
  scorecard <- .build_comparison_scorecard(values, deltas, rankings, rule_results, pareto)

  structure(list(
    schema_version = "1.0.0",
    scenario_set = set,
    baseline_id = baseline_id,
    model = model_pairs[1L],
    metrics = metrics,
    directions = directions,
    values = values,
    deltas = deltas,
    rankings = rankings,
    scorecard = scorecard,
    rules = rules,
    rule_results = rule_results,
    tradeoffs = tradeoffs,
    pareto = pareto,
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      scenario_count = length(set$runs),
      metric_count = length(metrics)
    )
  ), class = "catalyst_comparison")
}

#' Extract scenario deltas
#'
#' @param x A `catalyst_comparison` or comparison-compatible input.
#' @param ... Arguments passed to [compare_scenarios()] when needed.
#' @return A data frame of absolute and percentage differences from baseline.
#' @export
scenario_deltas <- function(x, ...) {
  if (!inherits(x, "catalyst_comparison")) x <- compare_scenarios(x, ...)
  x$deltas
}

#' Extract per-metric scenario rankings
#'
#' @param x A `catalyst_comparison` or comparison-compatible input.
#' @param ... Arguments passed to [compare_scenarios()] when needed.
#' @return A ranking data frame.
#' @export
scenario_rankings <- function(x, ...) {
  if (!inherits(x, "catalyst_comparison")) x <- compare_scenarios(x, ...)
  x$rankings
}

#' Extract the comparative scenario scorecard
#'
#' @param x A `catalyst_comparison` or comparison-compatible input.
#' @param ... Arguments passed to [compare_scenarios()] when needed.
#' @return A metric-by-scenario scorecard.
#' @export
scenario_scorecard <- function(x, ...) {
  if (!inherits(x, "catalyst_comparison")) x <- compare_scenarios(x, ...)
  x$scorecard
}

#' Extract Pareto-frontier diagnostics
#'
#' @param x A `catalyst_comparison` or comparison-compatible input.
#' @param ... Arguments passed to [compare_scenarios()] when needed.
#' @return A list containing the Pareto front, dominance relationships, and
#'   evaluated metrics.
#' @export
pareto_diagnostics <- function(x, ...) {
  if (!inherits(x, "catalyst_comparison")) x <- compare_scenarios(x, ...)
  x$pareto
}

#' Plot comparative scenario results
#'
#' @param comparison A `catalyst_comparison`.
#' @param metric Indicator to plot.
#' @param type Plot type: overlaid trajectory, terminal values, or deltas.
#' @return A ggplot object.
#' @export
plot_scenario_comparison <- function(comparison, metric = NULL, type = c("trajectory", "terminal", "delta")) {
  if (!inherits(comparison, "catalyst_comparison")) comparison <- compare_scenarios(comparison)
  type <- match.arg(type)
  if (is.null(metric)) metric <- comparison$metrics[1L]
  .assert_single_string(metric, "metric")
  if (!metric %in% comparison$metrics) stop("`metric` is not in the comparison.", call. = FALSE)

  if (type == "trajectory") {
    rows <- do.call(rbind, lapply(comparison$scenario_set$runs, function(run) {
      run$sdg_indicators[run$sdg_indicators$indicator == metric, c("t", "scenario", "value", "unit", "direction"), drop = FALSE]
    }))
    title <- paste("Scenario trajectories:", metric)
    return(ggplot2::ggplot(rows, ggplot2::aes(x = t, y = value, color = scenario)) +
      ggplot2::geom_line(linewidth = 0.9) +
      ggplot2::labs(x = "Time", y = unique(rows$unit)[1L], color = "Scenario", title = title) +
      theme_catalyst())
  }
  if (type == "terminal") {
    rows <- comparison$values[comparison$values$metric == metric, , drop = FALSE]
    return(ggplot2::ggplot(rows, ggplot2::aes(x = stats::reorder(scenario_id, final_value), y = final_value)) +
      ggplot2::geom_col() +
      ggplot2::coord_flip() +
      ggplot2::labs(x = NULL, y = rows$unit[1L], title = paste("Terminal scenario values:", metric)) +
      theme_catalyst())
  }
  rows <- comparison$deltas[comparison$deltas$metric == metric & comparison$deltas$scenario_id != comparison$baseline_id, , drop = FALSE]
  ggplot2::ggplot(rows, ggplot2::aes(x = stats::reorder(scenario_id, absolute_delta), y = absolute_delta)) +
    ggplot2::geom_col() +
    ggplot2::coord_flip() +
    ggplot2::geom_hline(yintercept = 0, linewidth = 0.4) +
    ggplot2::labs(x = NULL, y = paste("Delta from", comparison$baseline_id), title = paste("Scenario deltas:", metric)) +
    theme_catalyst()
}

#' Plot a two-metric scenario trade-off plane
#'
#' @param comparison A `catalyst_comparison`.
#' @param x_metric Indicator for the horizontal axis.
#' @param y_metric Indicator for the vertical axis.
#' @return A ggplot object marking the non-dominated scenarios.
#' @export
plot_scenario_tradeoffs <- function(comparison, x_metric, y_metric) {
  if (!inherits(comparison, "catalyst_comparison")) comparison <- compare_scenarios(comparison)
  .assert_single_string(x_metric, "x_metric")
  .assert_single_string(y_metric, "y_metric")
  if (!all(c(x_metric, y_metric) %in% comparison$metrics)) stop("Both trade-off metrics must be in the comparison.", call. = FALSE)
  x_values <- comparison$values[comparison$values$metric == x_metric, c("scenario_id", "scenario_title", "final_value"), drop = FALSE]
  names(x_values)[3L] <- "x_value"
  y_values <- comparison$values[comparison$values$metric == y_metric, c("scenario_id", "final_value"), drop = FALSE]
  names(y_values)[2L] <- "y_value"
  rows <- merge(x_values, y_values, by = "scenario_id")
  rows <- merge(rows, comparison$pareto$front[, c("scenario_id", "non_dominated")], by = "scenario_id")
  ggplot2::ggplot(rows, ggplot2::aes(x = x_value, y = y_value, shape = non_dominated, label = scenario_id)) +
    ggplot2::geom_point(size = 3) +
    ggplot2::geom_text(nudge_y = 0.02, check_overlap = TRUE) +
    ggplot2::labs(x = x_metric, y = y_metric, shape = "Pareto front", title = "Scenario trade-off plane") +
    theme_catalyst()
}

#' @export
plot.catalyst_comparison <- function(x, ...) plot_scenario_comparison(x, ...)

#' @export
print.catalyst_comparison <- function(x, ...) {
  cat("<catalyst_comparison>\n")
  cat("  baseline:  ", x$baseline_id, "\n", sep = "")
  cat("  scenarios: ", x$meta$scenario_count, "\n", sep = "")
  cat("  metrics:   ", paste(x$metrics, collapse = ", "), "\n", sep = "")
  non_dominated <- x$pareto$front$scenario_id[x$pareto$front$non_dominated]
  cat("  Pareto:    ", paste(non_dominated, collapse = ", "), "\n", sep = "")
  invisible(x)
}
