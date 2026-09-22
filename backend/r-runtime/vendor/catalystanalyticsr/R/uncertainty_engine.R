.uncertainty_distribution_names <- function() {
  c("fixed", "uniform", "normal", "lognormal", "triangular", "beta", "discrete")
}

.uncertainty_target_roots <- function() {
  c("parameters", "policy", "initial_state", "constraints")
}

.normalize_uncertainty_spec <- function(spec) {
  if (!is.list(spec)) stop("An uncertainty specification must be a list.", call. = FALSE)
  if (is.null(spec$target) || is.null(spec$distribution)) {
    stop("An uncertainty specification requires `target` and `distribution`.", call. = FALSE)
  }
  target <- as.character(.as_scalar(spec$target, "uncertainty$target"))
  distribution <- tolower(as.character(.as_scalar(spec$distribution, "uncertainty$distribution")))
  id <- if (is.null(spec$id)) .slugify(paste(target, distribution, sep = "-")) else as.character(.as_scalar(spec$id, "uncertainty$id"))
  label <- if (is.null(spec$label)) target else as.character(.as_scalar(spec$label, "uncertainty$label"))
  parameters <- if (is.null(spec$parameters)) list() else .as_named_list(spec$parameters, "uncertainty$parameters")
  enabled <- if (is.null(spec$enabled)) TRUE else as.logical(.as_scalar(spec$enabled, "uncertainty$enabled"))
  list(id = id, target = target, distribution = distribution, parameters = parameters, label = label, enabled = enabled)
}

#' Define a governed uncertainty distribution
#'
#' @param target Scenario path such as `parameters.emissions_intensity`,
#'   `policy.a`, `initial_state.N`, or `constraints.emissions_budget`.
#' @param distribution Distribution name: fixed, uniform, normal, lognormal,
#'   triangular, beta, or discrete.
#' @param parameters Named distribution parameters.
#' @param id Stable specification identifier.
#' @param label Human-readable label.
#' @param enabled Whether the distribution participates in sampling.
#' @return A validated uncertainty specification list.
#' @export
uncertainty_spec <- function(
  target,
  distribution = c("uniform", "normal", "lognormal", "triangular", "beta", "discrete", "fixed"),
  parameters = list(),
  id = NULL,
  label = NULL,
  enabled = TRUE
) {
  .assert_single_string(target, "target")
  distribution <- match.arg(distribution)
  .assert_flag(enabled, "enabled")
  spec <- list(
    id = if (is.null(id)) .slugify(paste(target, distribution, sep = "-")) else id,
    target = target,
    distribution = distribution,
    parameters = parameters,
    label = if (is.null(label)) target else label,
    enabled = enabled
  )
  validate_uncertainty_spec(spec)
  .normalize_uncertainty_spec(spec)
}

.validate_distribution_parameters <- function(spec) {
  p <- spec$parameters
  required_number <- function(name, lower = -Inf, upper = Inf) {
    if (is.null(p[[name]])) stop(sprintf("Distribution `%s` requires parameter `%s`.", spec$distribution, name), call. = FALSE)
    value <- as.numeric(.as_scalar(p[[name]], paste0("uncertainty$parameters$", name)))
    .assert_scalar_number(value, paste0("uncertainty$parameters$", name), lower = lower, upper = upper)
    value
  }
  optional_bound <- function(name) {
    if (is.null(p[[name]]) || is.na(p[[name]])) return(NA_real_)
    value <- as.numeric(.as_scalar(p[[name]], paste0("uncertainty$parameters$", name)))
    .assert_scalar_number(value, paste0("uncertainty$parameters$", name))
    value
  }

  if (spec$distribution == "fixed") {
    required_number("value")
  } else if (spec$distribution == "uniform") {
    minimum <- required_number("min")
    maximum <- required_number("max")
    if (maximum <= minimum) stop("Uniform distribution requires `max` greater than `min`.", call. = FALSE)
  } else if (spec$distribution == "normal") {
    required_number("mean")
    required_number("sd", lower = .Machine$double.eps)
    lower <- optional_bound("min")
    upper <- optional_bound("max")
    if (is.finite(lower) && is.finite(upper) && upper <= lower) stop("Normal bounds require `max` greater than `min`.", call. = FALSE)
  } else if (spec$distribution == "lognormal") {
    required_number("meanlog")
    required_number("sdlog", lower = .Machine$double.eps)
    lower <- optional_bound("min")
    upper <- optional_bound("max")
    if (is.finite(lower) && lower < 0) stop("Lognormal `min` cannot be negative.", call. = FALSE)
    if (is.finite(lower) && is.finite(upper) && upper <= lower) stop("Lognormal bounds require `max` greater than `min`.", call. = FALSE)
  } else if (spec$distribution == "triangular") {
    minimum <- required_number("min")
    mode <- required_number("mode")
    maximum <- required_number("max")
    if (!(minimum <= mode && mode <= maximum && maximum > minimum)) {
      stop("Triangular parameters must satisfy min <= mode <= max and min < max.", call. = FALSE)
    }
  } else if (spec$distribution == "beta") {
    required_number("shape1", lower = .Machine$double.eps)
    required_number("shape2", lower = .Machine$double.eps)
    minimum <- if (is.null(p$min)) 0 else required_number("min")
    maximum <- if (is.null(p$max)) 1 else required_number("max")
    if (maximum <= minimum) stop("Beta scaling requires `max` greater than `min`.", call. = FALSE)
  } else if (spec$distribution == "discrete") {
    values <- p$values
    if (is.null(values) || !is.numeric(unlist(values, use.names = FALSE)) || !length(values)) {
      stop("Discrete distribution requires a non-empty numeric `values` vector.", call. = FALSE)
    }
    values <- as.numeric(unlist(values, use.names = FALSE))
    if (any(!is.finite(values))) stop("Discrete distribution values must be finite.", call. = FALSE)
    probabilities <- p$probabilities
    if (!is.null(probabilities)) {
      probabilities <- as.numeric(unlist(probabilities, use.names = FALSE))
      if (length(probabilities) != length(values) || any(!is.finite(probabilities)) || any(probabilities < 0) || sum(probabilities) <= 0) {
        stop("Discrete probabilities must be non-negative, finite, and match `values`.", call. = FALSE)
      }
    }
  }
  invisible(TRUE)
}

#' Validate an uncertainty specification
#'
#' @param spec Uncertainty specification list.
#' @param scenario Optional canonical scenario used to verify the target path.
#' @return Invisibly returns `TRUE` when valid.
#' @export
validate_uncertainty_spec <- function(spec, scenario = NULL) {
  spec <- .normalize_uncertainty_spec(spec)
  .validate_model_id(spec$id, "uncertainty$id")
  .assert_single_string(spec$target, "uncertainty$target")
  .assert_single_string(spec$label, "uncertainty$label")
  .assert_flag(spec$enabled, "uncertainty$enabled")
  if (!spec$distribution %in% .uncertainty_distribution_names()) {
    stop(sprintf("Unsupported uncertainty distribution `%s`.", spec$distribution), call. = FALSE)
  }
  parts <- strsplit(spec$target, ".", fixed = TRUE)[[1L]]
  if (length(parts) != 2L || !parts[1L] %in% .uncertainty_target_roots() || !nzchar(parts[2L])) {
    stop("Uncertainty target must be a two-part scenario path under parameters, policy, initial_state, or constraints.", call. = FALSE)
  }
  .validate_distribution_parameters(spec)
  if (!is.null(scenario)) .scenario_target_value(.normalize_scenario(scenario), spec$target)
  invisible(TRUE)
}

.scenario_target_value <- function(scenario, target) {
  parts <- strsplit(target, ".", fixed = TRUE)[[1L]]
  root <- parts[1L]
  name <- parts[2L]
  values <- scenario[[root]]
  if (root == "parameters" && is.null(values[[name]])) {
    model <- get_catalyst_model(scenario$model$id, scenario$model$version)
    values <- model$default_parameters
  }
  if (is.null(values[[name]])) stop(sprintf("Scenario target `%s` does not exist.", target), call. = FALSE)
  value <- as.numeric(.as_scalar(values[[name]], target))
  .assert_scalar_number(value, target)
  value
}

.set_scenario_target <- function(scenario, target, value) {
  .assert_scalar_number(value, target)
  parts <- strsplit(target, ".", fixed = TRUE)[[1L]]
  scenario[[parts[1L]]][[parts[2L]]] <- as.numeric(value)
  scenario
}

.triangular_quantile <- function(u, minimum, mode, maximum) {
  cut <- (mode - minimum) / (maximum - minimum)
  ifelse(
    u < cut,
    minimum + sqrt(u * (maximum - minimum) * (mode - minimum)),
    maximum - sqrt((1 - u) * (maximum - minimum) * (maximum - mode))
  )
}

.sample_uncertainty_distribution <- function(spec, u) {
  p <- spec$parameters
  values <- switch(spec$distribution,
    fixed = rep(as.numeric(p$value), length(u)),
    uniform = stats::qunif(u, min = as.numeric(p$min), max = as.numeric(p$max)),
    normal = stats::qnorm(u, mean = as.numeric(p$mean), sd = as.numeric(p$sd)),
    lognormal = stats::qlnorm(u, meanlog = as.numeric(p$meanlog), sdlog = as.numeric(p$sdlog)),
    triangular = .triangular_quantile(u, as.numeric(p$min), as.numeric(p$mode), as.numeric(p$max)),
    beta = {
      minimum <- if (is.null(p$min)) 0 else as.numeric(p$min)
      maximum <- if (is.null(p$max)) 1 else as.numeric(p$max)
      minimum + stats::qbeta(u, shape1 = as.numeric(p$shape1), shape2 = as.numeric(p$shape2)) * (maximum - minimum)
    },
    discrete = {
      choices <- as.numeric(unlist(p$values, use.names = FALSE))
      probabilities <- if (is.null(p$probabilities)) rep(1 / length(choices), length(choices)) else as.numeric(unlist(p$probabilities, use.names = FALSE))
      probabilities <- probabilities / sum(probabilities)
      cumulative <- cumsum(probabilities)
      vapply(u, function(value) choices[which(value <= cumulative)[1L]], numeric(1))
    }
  )
  if (!is.null(p$min) && spec$distribution %in% c("normal", "lognormal")) values <- pmax(values, as.numeric(p$min))
  if (!is.null(p$max) && spec$distribution %in% c("normal", "lognormal")) values <- pmin(values, as.numeric(p$max))
  as.numeric(values)
}

.with_reproducible_seed <- function(seed, code) {
  .assert_scalar_number(seed, "seed")
  had_seed <- exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  if (had_seed) old_seed <- get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
  on.exit({
    if (had_seed) assign(".Random.seed", old_seed, envir = .GlobalEnv)
    else if (exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE)) rm(".Random.seed", envir = .GlobalEnv)
  }, add = TRUE)
  set.seed(as.integer(seed))
  force(code)
}

#' Draw reproducible uncertainty samples
#'
#' @param scenario Canonical scenario containing uncertainty records.
#' @param n Number of samples.
#' @param method Monte Carlo or Latin hypercube sampling.
#' @param seed Reproducible integer seed.
#' @param uncertainty Optional specifications overriding `scenario$uncertainty`.
#' @return A data frame containing sample ids and one column per target.
#' @export
sample_uncertainty <- function(
  scenario,
  n = 1000L,
  method = c("monte_carlo", "latin_hypercube"),
  seed = 42L,
  uncertainty = NULL
) {
  scenario <- as_catalyst_scenario(scenario)
  method <- match.arg(method)
  .assert_scalar_number(n, "n", lower = 1)
  n <- as.integer(n)
  specs <- if (is.null(uncertainty)) scenario$uncertainty else uncertainty
  specs <- lapply(specs, .normalize_uncertainty_spec)
  specs <- Filter(function(spec) isTRUE(spec$enabled), specs)
  if (!length(specs)) stop("The scenario has no enabled uncertainty specifications.", call. = FALSE)
  ids <- vapply(specs, function(spec) spec$id, character(1))
  targets <- vapply(specs, function(spec) spec$target, character(1))
  if (anyDuplicated(ids)) stop("Uncertainty specification ids must be unique.", call. = FALSE)
  if (anyDuplicated(targets)) stop("Each uncertainty target may be specified only once.", call. = FALSE)
  invisible(lapply(specs, validate_uncertainty_spec, scenario = scenario))

  draws <- .with_reproducible_seed(seed, {
    matrix_values <- matrix(NA_real_, nrow = n, ncol = length(specs), dimnames = list(NULL, targets))
    for (j in seq_along(specs)) {
      u <- if (method == "monte_carlo") {
        stats::runif(n)
      } else {
        sample(((seq_len(n) - 1) + stats::runif(n)) / n, size = n, replace = FALSE)
      }
      matrix_values[, j] <- .sample_uncertainty_distribution(specs[[j]], u)
    }
    matrix_values
  })
  out <- data.frame(sample_id = seq_len(n), draws, check.names = FALSE, stringsAsFactors = FALSE)
  attr(out, "method") <- method
  attr(out, "seed") <- as.integer(seed)
  attr(out, "specifications") <- specs
  out
}

.scenario_from_uncertainty_sample <- function(scenario, samples, row) {
  out <- scenario
  targets <- setdiff(names(samples), "sample_id")
  for (target in targets) out <- .set_scenario_target(out, target, as.numeric(samples[[target]][row]))
  out$metadata$tags <- unique(c(out$metadata$tags, "uncertainty-realization"))
  out$metadata$uncertainty_sample_id <- as.integer(samples$sample_id[row])
  out
}

.uncertainty_metric_rows <- function(run, sample_id, metrics) {
  rows <- lapply(metrics, function(metric) {
    values <- run$sdg_indicators[run$sdg_indicators$indicator == metric, , drop = FALSE]
    values <- values[order(values$t), , drop = FALSE]
    if (!nrow(values)) return(NULL)
    data.frame(
      sample_id = sample_id,
      metric = metric,
      value = as.numeric(values$value[nrow(values)]),
      unit = as.character(values$unit[nrow(values)]),
      direction = as.character(values$direction[nrow(values)]),
      stringsAsFactors = FALSE
    )
  })
  rows <- Filter(Negate(is.null), rows)
  if (!length(rows)) NULL else do.call(rbind, rows)
}

.default_uncertainty_metrics <- function(run) {
  available <- unique(as.character(run$sdg_indicators$indicator))
  preferred <- c("gdp", "gdp_per_capita", "emissions", "emissions_per_capita", "carbon_intensity", "ans", "natural_capital", "atmospheric_carbon")
  selected <- intersect(preferred, available)
  if (length(selected)) selected else utils::head(available, 6L)
}

.build_uncertainty_summary <- function(results) {
  if (!nrow(results)) return(data.frame())
  rows <- lapply(unique(results$metric), function(metric) {
    subset <- results[results$metric == metric & is.finite(results$value), , drop = FALSE]
    if (!nrow(subset)) return(NULL)
    q <- stats::quantile(subset$value, probs = c(0.025, 0.10, 0.50, 0.90, 0.975), names = FALSE, na.rm = TRUE, type = 8)
    data.frame(
      metric = metric,
      unit = subset$unit[1L],
      direction = subset$direction[1L],
      n = nrow(subset),
      mean = mean(subset$value),
      sd = stats::sd(subset$value),
      min = min(subset$value),
      p025 = q[1L],
      p10 = q[2L],
      median = q[3L],
      p90 = q[4L],
      p975 = q[5L],
      max = max(subset$value),
      stringsAsFactors = FALSE
    )
  })
  rows <- Filter(Negate(is.null), rows)
  if (!length(rows)) data.frame() else do.call(rbind, rows)
}

.normalize_probability_rules <- function(rules, results) {
  if (is.null(rules) || !length(rules)) return(data.frame(metric = character(), value = numeric(), operator = character(), stringsAsFactors = FALSE))
  if (!is.list(rules) || is.null(names(rules)) || any(!nzchar(names(rules)))) stop("`thresholds` must be a named list.", call. = FALSE)
  available <- unique(results$metric)
  rows <- lapply(names(rules), function(metric) {
    if (!metric %in% available) stop(sprintf("Threshold metric `%s` is unavailable.", metric), call. = FALSE)
    item <- rules[[metric]]
    value <- item
    operator <- NULL
    if (is.list(item)) {
      value <- item$value
      operator <- item$operator
    }
    .assert_scalar_number(value, paste0("thresholds$", metric))
    direction <- unique(results$direction[results$metric == metric])[1L]
    if (is.null(operator)) operator <- if (identical(direction, "lower_better")) "<=" else ">="
    .assert_single_string(operator, paste0("thresholds$", metric, "$operator"))
    if (!operator %in% c(">=", "<=", ">", "<", "==")) stop("Threshold operators must be >=, <=, >, <, or ==.", call. = FALSE)
    data.frame(metric = metric, value = as.numeric(value), operator = operator, stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

.build_probability_results <- function(results, rules) {
  if (!nrow(rules)) return(data.frame(metric = character(), threshold = numeric(), operator = character(), successes = integer(), n = integer(), probability = numeric(), stringsAsFactors = FALSE))
  rows <- lapply(seq_len(nrow(rules)), function(i) {
    rule <- rules[i, , drop = FALSE]
    values <- results$value[results$metric == rule$metric & is.finite(results$value)]
    met <- vapply(values, .evaluate_rule, logical(1), operator = rule$operator, reference = rule$value)
    data.frame(metric = rule$metric, threshold = rule$value, operator = rule$operator, successes = sum(met), n = length(met), probability = if (length(met)) mean(met) else NA_real_, stringsAsFactors = FALSE)
  })
  do.call(rbind, rows)
}

.build_global_sensitivity <- function(samples, results, method = "spearman") {
  targets <- setdiff(names(samples), "sample_id")
  metrics <- unique(results$metric)
  rows <- list()
  for (metric in metrics) {
    values <- results[results$metric == metric, c("sample_id", "value"), drop = FALSE]
    joined <- merge(samples, values, by = "sample_id", all = FALSE, sort = FALSE)
    for (target in targets) {
      input_sd <- stats::sd(joined[[target]], na.rm = TRUE)
      output_sd <- stats::sd(joined$value, na.rm = TRUE)
      estimate <- if (!is.finite(input_sd) || !is.finite(output_sd) || input_sd == 0 || output_sd == 0) NA_real_ else suppressWarnings(stats::cor(joined[[target]], joined$value, use = "complete.obs", method = method))
      rows[[length(rows) + 1L]] <- data.frame(
        target = target,
        metric = metric,
        method = method,
        estimate = estimate,
        absolute_effect = abs(estimate),
        n = sum(stats::complete.cases(joined[[target]], joined$value)),
        stringsAsFactors = FALSE
      )
    }
  }
  if (!length(rows)) data.frame() else do.call(rbind, rows)
}

#' Run a sampled uncertainty ensemble
#'
#' @param scenario Canonical scenario containing uncertainty specifications.
#' @param n Number of sampled realizations.
#' @param sampling Sampling design: Monte Carlo or Latin hypercube.
#' @param seed Reproducible seed.
#' @param metrics Terminal indicators to retain.
#' @param thresholds Optional named probability thresholds.
#' @param method Optional model integration method.
#' @param continue_on_error Continue after failed realizations.
#' @return A `catalyst_uncertainty_run`.
#' @export
run_uncertainty <- function(
  scenario,
  n = 1000L,
  sampling = c("monte_carlo", "latin_hypercube"),
  seed = 42L,
  metrics = NULL,
  thresholds = list(),
  method = NULL,
  continue_on_error = TRUE
) {
  scenario <- as_catalyst_scenario(scenario)
  sampling <- match.arg(sampling)
  .assert_flag(continue_on_error, "continue_on_error")
  samples <- sample_uncertainty(scenario, n = n, method = sampling, seed = seed)
  result_rows <- list()
  failures <- list()
  resolved_metrics <- metrics
  for (i in seq_len(nrow(samples))) {
    realization <- .scenario_from_uncertainty_sample(scenario, samples, i)
    result <- tryCatch(
      run_catalyst_scenario(realization, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE),
      error = function(error) error
    )
    if (inherits(result, "error")) {
      failures[[length(failures) + 1L]] <- data.frame(sample_id = samples$sample_id[i], message = conditionMessage(result), stringsAsFactors = FALSE)
      if (!continue_on_error) stop(sprintf("Uncertainty sample %s failed: %s", samples$sample_id[i], conditionMessage(result)), call. = FALSE)
      next
    }
    if (is.null(resolved_metrics)) resolved_metrics <- .default_uncertainty_metrics(result)
    if (!is.character(resolved_metrics) || !length(resolved_metrics) || any(!nzchar(resolved_metrics)) || anyDuplicated(resolved_metrics)) {
      stop("`metrics` must contain unique indicator names.", call. = FALSE)
    }
    unavailable <- setdiff(resolved_metrics, unique(as.character(result$sdg_indicators$indicator)))
    if (length(unavailable)) stop(sprintf("Uncertainty metrics are unavailable: %s.", paste(unavailable, collapse = ", ")), call. = FALSE)
    rows <- .uncertainty_metric_rows(result, samples$sample_id[i], resolved_metrics)
    if (!is.null(rows)) result_rows[[length(result_rows) + 1L]] <- rows
  }
  results <- if (length(result_rows)) do.call(rbind, result_rows) else data.frame(sample_id = integer(), metric = character(), value = numeric(), unit = character(), direction = character(), stringsAsFactors = FALSE)
  failure_table <- if (length(failures)) do.call(rbind, failures) else data.frame(sample_id = integer(), message = character(), stringsAsFactors = FALSE)
  summary <- .build_uncertainty_summary(results)
  rules <- .normalize_probability_rules(thresholds, results)
  probabilities <- .build_probability_results(results, rules)
  sensitivity <- .build_global_sensitivity(samples[samples$sample_id %in% unique(results$sample_id), , drop = FALSE], results, method = "spearman")
  structure(list(
    schema_version = "1.0.0",
    scenario = scenario,
    specifications = attr(samples, "specifications"),
    samples = samples,
    results = results,
    summary = summary,
    thresholds = rules,
    probabilities = probabilities,
    sensitivity = sensitivity,
    failures = failure_table,
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      sampling = sampling,
      seed = as.integer(seed),
      requested = nrow(samples),
      completed = length(unique(results$sample_id)),
      failed = nrow(failure_table),
      failure_rate = if (nrow(samples)) nrow(failure_table) / nrow(samples) else NA_real_
    )
  ), class = "catalyst_uncertainty_run")
}

#' @export
print.catalyst_uncertainty_run <- function(x, ...) {
  cat("<catalyst_uncertainty_run>\n")
  cat("  scenario:  ", x$scenario$id, "\n", sep = "")
  cat("  sampling:  ", x$meta$sampling, "\n", sep = "")
  cat("  requested: ", x$meta$requested, "\n", sep = "")
  cat("  completed: ", x$meta$completed, "\n", sep = "")
  cat("  failed:    ", x$meta$failed, "\n", sep = "")
  invisible(x)
}

#' Extract uncertainty interval summaries
#'
#' @param x A `catalyst_uncertainty_run`.
#' @return Metric interval summary data frame.
#' @export
uncertainty_summary <- function(x) {
  if (!inherits(x, "catalyst_uncertainty_run")) stop("`x` must be a catalyst_uncertainty_run.", call. = FALSE)
  x$summary
}

#' Extract threshold-crossing probabilities
#'
#' @param x A `catalyst_uncertainty_run`.
#' @return Probability data frame.
#' @export
uncertainty_probabilities <- function(x) {
  if (!inherits(x, "catalyst_uncertainty_run")) stop("`x` must be a catalyst_uncertainty_run.", call. = FALSE)
  x$probabilities
}

#' Compute global input-output sensitivity
#'
#' @param x A `catalyst_uncertainty_run`.
#' @param method Correlation method: spearman or pearson.
#' @return Sensitivity data frame.
#' @export
global_sensitivity <- function(x, method = c("spearman", "pearson")) {
  if (!inherits(x, "catalyst_uncertainty_run")) stop("`x` must be a catalyst_uncertainty_run.", call. = FALSE)
  method <- match.arg(method)
  .build_global_sensitivity(x$samples[x$samples$sample_id %in% unique(x$results$sample_id), , drop = FALSE], x$results, method = method)
}

#' Plot uncertainty distributions or intervals
#'
#' @param x A `catalyst_uncertainty_run`.
#' @param metric Indicator name.
#' @param type Distribution histogram or interval plot.
#' @return A ggplot object.
#' @export
plot_uncertainty <- function(x, metric = NULL, type = c("distribution", "interval")) {
  if (!inherits(x, "catalyst_uncertainty_run")) stop("`x` must be a catalyst_uncertainty_run.", call. = FALSE)
  type <- match.arg(type)
  if (type == "interval") {
    rows <- x$summary
    return(ggplot2::ggplot(rows, ggplot2::aes(x = stats::reorder(metric, median), y = median, ymin = p10, ymax = p90)) +
      ggplot2::geom_pointrange() + ggplot2::coord_flip() +
      ggplot2::labs(x = NULL, y = "P10 to P90 interval", title = "Uncertainty intervals") + theme_catalyst())
  }
  if (is.null(metric)) metric <- x$summary$metric[1L]
  .assert_single_string(metric, "metric")
  rows <- x$results[x$results$metric == metric, , drop = FALSE]
  if (!nrow(rows)) stop("`metric` is not present in the uncertainty results.", call. = FALSE)
  ggplot2::ggplot(rows, ggplot2::aes(x = value)) +
    ggplot2::geom_histogram(bins = 30) +
    ggplot2::geom_vline(xintercept = stats::median(rows$value), linetype = 2) +
    ggplot2::labs(x = paste(metric, paste0("(", rows$unit[1L], ")")), y = "Sample count", title = paste("Uncertainty distribution:", metric)) +
    theme_catalyst()
}

#' Plot a sensitivity tornado chart
#'
#' @param x A `catalyst_uncertainty_run`.
#' @param metric Indicator name.
#' @param method Correlation method.
#' @return A ggplot object.
#' @export
plot_tornado <- function(x, metric = NULL, method = c("spearman", "pearson")) {
  method <- match.arg(method)
  sensitivity <- global_sensitivity(x, method = method)
  if (is.null(metric)) metric <- unique(sensitivity$metric)[1L]
  .assert_single_string(metric, "metric")
  rows <- sensitivity[sensitivity$metric == metric, , drop = FALSE]
  if (!nrow(rows)) stop("`metric` is not present in the sensitivity results.", call. = FALSE)
  ggplot2::ggplot(rows, ggplot2::aes(x = stats::reorder(target, estimate), y = estimate)) +
    ggplot2::geom_col() + ggplot2::coord_flip() + ggplot2::geom_hline(yintercept = 0, linewidth = 0.4) +
    ggplot2::labs(x = NULL, y = paste(tools::toTitleCase(method), "correlation"), title = paste("Sensitivity tornado:", metric)) + theme_catalyst()
}

#' Compute one-at-a-time local sensitivity
#'
#' @param scenario Canonical scenario.
#' @param targets Scenario target paths. Defaults to enabled uncertainty targets.
#' @param change Relative perturbation size.
#' @param metrics Terminal indicators.
#' @param method Optional integration method.
#' @return Data frame of central finite-difference effects and elasticities.
#' @export
local_sensitivity <- function(scenario, targets = NULL, change = 0.01, metrics = NULL, method = NULL) {
  scenario <- as_catalyst_scenario(scenario)
  .assert_scalar_number(change, "change", lower = .Machine$double.eps, upper = 0.5)
  if (is.null(targets)) targets <- vapply(Filter(function(x) isTRUE(.normalize_uncertainty_spec(x)$enabled), scenario$uncertainty), function(x) .normalize_uncertainty_spec(x)$target, character(1))
  if (!is.character(targets) || !length(targets) || any(!nzchar(targets)) || anyDuplicated(targets)) stop("`targets` must be unique scenario paths.", call. = FALSE)
  baseline <- run_catalyst_scenario(scenario, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE)
  if (is.null(metrics)) metrics <- .default_uncertainty_metrics(baseline)
  baseline_rows <- .uncertainty_metric_rows(baseline, 0L, metrics)
  rows <- list()
  for (target in targets) {
    original <- .scenario_target_value(scenario, target)
    delta <- max(abs(original) * change, sqrt(.Machine$double.eps))
    lower_input <- max(0, original - delta)
    upper_input <- original + delta
    lower_scenario <- .set_scenario_target(scenario, target, lower_input)
    upper_scenario <- .set_scenario_target(scenario, target, upper_input)
    lower_run <- run_catalyst_scenario(lower_scenario, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE)
    upper_run <- run_catalyst_scenario(upper_scenario, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE)
    lower_rows <- .uncertainty_metric_rows(lower_run, -1L, metrics)
    upper_rows <- .uncertainty_metric_rows(upper_run, 1L, metrics)
    for (metric in metrics) {
      base_value <- baseline_rows$value[baseline_rows$metric == metric][1L]
      lower_value <- lower_rows$value[lower_rows$metric == metric][1L]
      upper_value <- upper_rows$value[upper_rows$metric == metric][1L]
      derivative <- (upper_value - lower_value) / (upper_input - lower_input)
      elasticity <- if (is.finite(base_value) && base_value != 0 && original != 0) derivative * original / base_value else NA_real_
      rows[[length(rows) + 1L]] <- data.frame(target = target, metric = metric, baseline_input = original, perturbation = delta, lower_value = lower_value, baseline_value = base_value, upper_value = upper_value, derivative = derivative, elasticity = elasticity, absolute_elasticity = abs(elasticity), stringsAsFactors = FALSE)
    }
  }
  do.call(rbind, rows)
}

#' Define a scenario shock
#'
#' @param target Scenario target path.
#' @param value Shock value.
#' @param mode Apply by setting, adding, or multiplying.
#' @return A validated shock record.
#' @export
stress_shock <- function(target, value, mode = c("set", "add", "multiply")) {
  .assert_single_string(target, "target")
  .assert_scalar_number(value, "value")
  mode <- match.arg(mode)
  parts <- strsplit(target, ".", fixed = TRUE)[[1L]]
  if (length(parts) != 2L || !parts[1L] %in% .uncertainty_target_roots()) stop("Stress target must be a supported two-part scenario path.", call. = FALSE)
  list(target = target, mode = mode, value = as.numeric(value))
}

#' Define a named stress-test case
#'
#' @param id Stable case identifier.
#' @param title Human-readable case title.
#' @param shocks Non-empty list of `stress_shock()` records.
#' @param description Optional explanation.
#' @return A stress case list.
#' @export
stress_case <- function(id, title, shocks, description = "") {
  .validate_model_id(id, "id")
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.list(shocks) || !length(shocks)) stop("`shocks` must be a non-empty list.", call. = FALSE)
  for (shock in shocks) {
    if (!is.list(shock) || is.null(shock$target) || is.null(shock$mode) || is.null(shock$value)) stop("Every stress case entry must be a stress shock.", call. = FALSE)
    stress_shock(shock$target, shock$value, shock$mode)
  }
  list(id = id, title = title, description = description, shocks = shocks)
}

.apply_stress_case <- function(scenario, case) {
  out <- scenario
  for (shock in case$shocks) {
    current <- .scenario_target_value(out, shock$target)
    value <- switch(shock$mode, set = shock$value, add = current + shock$value, multiply = current * shock$value)
    out <- .set_scenario_target(out, shock$target, value)
  }
  out$id <- paste0(scenario$id, "-stress-", case$id)
  out$title <- paste(scenario$title, "-", case$title)
  out$role <- "counterfactual"
  out$metadata$description <- case$description
  out$metadata$tags <- unique(c(out$metadata$tags, "stress-test", case$id))
  out
}

#' Run named structural stress tests
#'
#' @param scenario Baseline canonical scenario.
#' @param cases Non-empty list of `stress_case()` records.
#' @param metrics Comparison indicators.
#' @param method Optional integration method.
#' @return A `catalyst_stress_test` with scenario comparison results.
#' @export
run_stress_tests <- function(scenario, cases, metrics = NULL, method = NULL) {
  scenario <- as_catalyst_scenario(scenario)
  scenario$role <- "baseline"
  if (!is.list(cases) || !length(cases)) stop("`cases` must be a non-empty list.", call. = FALSE)
  normalized <- lapply(cases, function(case) stress_case(case$id, case$title, case$shocks, if (is.null(case$description)) "" else case$description))
  ids <- vapply(normalized, function(case) case$id, character(1))
  if (anyDuplicated(ids)) stop("Stress case ids must be unique.", call. = FALSE)
  scenarios <- c(list(scenario), lapply(normalized, function(case) .apply_stress_case(scenario, case)))
  set <- run_scenarios(scenarios, method = method, include_phase_plane = FALSE, include_sensitivity = FALSE)
  comparison <- compare_scenarios(set, baseline = scenario$id, metrics = metrics)
  structure(list(
    schema_version = "1.0.0",
    baseline = scenario,
    cases = normalized,
    scenario_set = set,
    comparison = comparison,
    meta = list(package_version = .catalyst_package_version(), created_at = .utc_now(), case_count = length(normalized))
  ), class = "catalyst_stress_test")
}

#' @export
print.catalyst_stress_test <- function(x, ...) {
  cat("<catalyst_stress_test>\n")
  cat("  baseline: ", x$baseline$id, "\n", sep = "")
  cat("  cases:    ", x$meta$case_count, "\n", sep = "")
  cat("  metrics:  ", length(x$comparison$metrics), "\n", sep = "")
  invisible(x)
}

#' Extract stress-test scorecards
#'
#' @param x A `catalyst_stress_test`.
#' @return List containing deltas, trade-offs, and Pareto diagnostics.
#' @export
stress_test_summary <- function(x) {
  if (!inherits(x, "catalyst_stress_test")) stop("`x` must be a catalyst_stress_test.", call. = FALSE)
  list(deltas = x$comparison$deltas, tradeoffs = x$comparison$tradeoffs, pareto = x$comparison$pareto)
}

#' Plot stress-test outcomes
#'
#' @param x A `catalyst_stress_test`.
#' @param metric Indicator name.
#' @param type Terminal values or baseline deltas.
#' @return A ggplot object.
#' @export
plot_stress_test <- function(x, metric = NULL, type = c("delta", "terminal")) {
  if (!inherits(x, "catalyst_stress_test")) stop("`x` must be a catalyst_stress_test.", call. = FALSE)
  type <- match.arg(type)
  plot_scenario_comparison(x$comparison, metric = metric, type = type)
}
