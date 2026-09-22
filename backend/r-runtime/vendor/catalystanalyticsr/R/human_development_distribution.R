.catalyst_human_development_schema_version <- function() "1.0.0"
.catalyst_distribution_schema_version <- function() "1.0.0"

.align_analysis_vectors <- function(values, names, defaults = NULL) {
  lengths <- vapply(values, length, integer(1))
  n <- max(lengths)
  output <- vector("list", length(values))
  names(output) <- names
  for (i in seq_along(values)) {
    value <- values[[i]]
    if (is.null(value) && !is.null(defaults)) value <- defaults[[i]]
    output[[i]] <- .recycle_wealth_numeric(value, n, names[[i]])
  }
  output
}

#' Adjusted Net Savings and human-development indicators
#'
#' @param gross_savings Gross national savings.
#' @param produced_capital_depreciation Produced-capital depreciation.
#' @param education_investment Education expenditure treated as human-capital investment.
#' @param health_investment Health expenditure treated as human-capital investment.
#' @param natural_resource_depletion Natural-resource depletion.
#' @param pollution_damages Pollution damages.
#' @param climate_damages Climate-related damages.
#' @param other_adjustments Other signed adjustments.
#' @param gni Optional gross national income for percentage calculations.
#' @param time Optional time labels.
#' @param entity Optional entity labels.
#' @param unit Monetary or index unit.
#' @param life_expectancy Life expectancy in years.
#' @param expected_schooling Expected years of schooling.
#' @param mean_schooling Mean years of schooling.
#' @param income_per_capita Positive income per capita.
#' @param life_floor Minimum life-expectancy goalpost.
#' @param life_cap Maximum life-expectancy goalpost.
#' @param expected_schooling_cap Maximum expected-schooling goalpost.
#' @param mean_schooling_cap Maximum mean-schooling goalpost.
#' @param income_floor Minimum income goalpost.
#' @param income_cap Maximum income goalpost.
#' @return A governed data frame of savings or human-development indicators.
#' @name human_development
NULL

#' @rdname human_development
#' @export
adjusted_net_savings_decomposition <- function(
  gross_savings,
  produced_capital_depreciation = 0,
  education_investment = 0,
  health_investment = 0,
  natural_resource_depletion = 0,
  pollution_damages = 0,
  climate_damages = 0,
  other_adjustments = 0,
  gni = NULL,
  time = NULL,
  entity = NULL,
  unit = "currency_index"
) {
  vectors <- list(
    gross_savings, produced_capital_depreciation, education_investment, health_investment,
    natural_resource_depletion, pollution_damages, climate_damages, other_adjustments
  )
  names_vec <- c(
    "gross_savings", "produced_capital_depreciation", "education_investment", "health_investment",
    "natural_resource_depletion", "pollution_damages", "climate_damages", "other_adjustments"
  )
  aligned <- .align_analysis_vectors(vectors, names_vec)
  n <- length(aligned[[1L]])
  nonnegative <- setdiff(names_vec, "other_adjustments")
  for (name in nonnegative) {
    if (any(aligned[[name]] < 0)) stop(sprintf("`%s` cannot be negative.", name), call. = FALSE)
  }
  gni_value <- if (is.null(gni)) rep(NA_real_, n) else .recycle_wealth_numeric(gni, n, "gni", lower = .Machine$double.eps)
  time_value <- .recycle_wealth_label(time, n, "time", seq_len(n))
  entity_value <- as.character(.recycle_wealth_label(entity, n, "entity", "all"))
  .assert_single_string(unit, "unit")
  human_investment <- aligned$education_investment + aligned$health_investment
  deductions <- aligned$produced_capital_depreciation + aligned$natural_resource_depletion + aligned$pollution_damages + aligned$climate_damages
  adjusted <- aligned$gross_savings + human_investment + aligned$other_adjustments - deductions
  data.frame(
    entity = entity_value,
    time = time_value,
    gross_savings = aligned$gross_savings,
    produced_capital_depreciation = aligned$produced_capital_depreciation,
    education_investment = aligned$education_investment,
    health_investment = aligned$health_investment,
    human_capital_investment = human_investment,
    natural_resource_depletion = aligned$natural_resource_depletion,
    pollution_damages = aligned$pollution_damages,
    climate_damages = aligned$climate_damages,
    other_adjustments = aligned$other_adjustments,
    total_deductions = deductions,
    adjusted_net_savings = adjusted,
    gni = gni_value,
    adjusted_net_savings_percent_gni = ifelse(is.na(gni_value), NA_real_, 100 * adjusted / gni_value),
    sustainable_savings_signal = adjusted >= 0,
    unit = rep(unit, n),
    schema_version = rep(.catalyst_wealth_schema_version(), n),
    stringsAsFactors = FALSE
  )
}

#' @rdname human_development
#' @export
human_development_indicators <- function(
  life_expectancy,
  expected_schooling,
  mean_schooling,
  income_per_capita,
  time = NULL,
  entity = NULL,
  life_floor = 20,
  life_cap = 85,
  expected_schooling_cap = 18,
  mean_schooling_cap = 15,
  income_floor = 100,
  income_cap = 75000
) {
  vectors <- .align_analysis_vectors(
    list(life_expectancy, expected_schooling, mean_schooling, income_per_capita),
    c("life_expectancy", "expected_schooling", "mean_schooling", "income_per_capita")
  )
  n <- length(vectors$life_expectancy)
  for (name in names(vectors)) {
    if (any(vectors[[name]] < 0)) stop(sprintf("`%s` cannot be negative.", name), call. = FALSE)
  }
  for (entry in list(
    list(life_floor, "life_floor"), list(life_cap, "life_cap"),
    list(expected_schooling_cap, "expected_schooling_cap"), list(mean_schooling_cap, "mean_schooling_cap"),
    list(income_floor, "income_floor"), list(income_cap, "income_cap")
  )) .assert_scalar_number(entry[[1L]], entry[[2L]], lower = 0)
  if (life_cap <= life_floor || income_cap <= income_floor || expected_schooling_cap <= 0 || mean_schooling_cap <= 0) {
    stop("Human-development goalposts must define positive ranges.", call. = FALSE)
  }
  clamp <- function(value) pmin(1, pmax(0, value))
  life_index <- clamp((vectors$life_expectancy - life_floor) / (life_cap - life_floor))
  expected_index <- clamp(vectors$expected_schooling / expected_schooling_cap)
  mean_index <- clamp(vectors$mean_schooling / mean_schooling_cap)
  education_index <- (expected_index + mean_index) / 2
  income_index <- clamp((log(pmax(vectors$income_per_capita, income_floor)) - log(income_floor)) / (log(income_cap) - log(income_floor)))
  hdi <- (life_index * education_index * income_index)^(1 / 3)
  data.frame(
    entity = as.character(.recycle_wealth_label(entity, n, "entity", "all")),
    time = .recycle_wealth_label(time, n, "time", seq_len(n)),
    life_expectancy = vectors$life_expectancy,
    expected_schooling = vectors$expected_schooling,
    mean_schooling = vectors$mean_schooling,
    income_per_capita = vectors$income_per_capita,
    life_expectancy_index = life_index,
    education_index = education_index,
    income_index = income_index,
    human_development_index = hdi,
    schema_version = rep(.catalyst_human_development_schema_version(), n),
    stringsAsFactors = FALSE
  )
}

.weighted_quantile <- function(values, weights, probability) {
  order_index <- order(values)
  values <- values[order_index]
  weights <- weights[order_index]
  cumulative <- cumsum(weights) / sum(weights)
  values[which(cumulative >= probability)[1L]]
}

.weighted_gini <- function(values, weights) {
  if (all(values == 0)) return(0)
  order_index <- order(values)
  values <- values[order_index]
  weights <- weights[order_index]
  population_share <- c(0, cumsum(weights) / sum(weights))
  value_weight <- values * weights
  resource_share <- c(0, cumsum(value_weight) / sum(value_weight))
  1 - sum((resource_share[-1L] + resource_share[-length(resource_share)]) * diff(population_share))
}

#' Distributional and intergenerational analysis
#'
#' @param values Non-negative observations.
#' @param weights Optional positive population or survey weights.
#' @param groups Optional group labels.
#' @param indicator Indicator identifier.
#' @param unit Unit for the distributed quantity.
#' @param higher_is_better Whether larger values are preferred.
#' @param social_floor Optional minimum acceptable value.
#' @param entity Entity label.
#' @param time Optional time label.
#' @param wealth Inclusive-wealth totals over time.
#' @param population Positive population over time.
#' @param social_discount_rate Non-negative annual social discount rate.
#' @param generation_length Positive number of years per generation.
#' @param target_per_capita Optional target wealth per capita.
#' @param x A distribution object.
#' @param ... Additional method arguments.
#' @return A distributional or intergenerational analysis object.
#' @name distribution_analysis
NULL

#' @rdname distribution_analysis
#' @export
distributional_analysis <- function(
  values,
  weights = NULL,
  groups = NULL,
  indicator = "distributed_value",
  unit = "index",
  higher_is_better = TRUE,
  social_floor = NULL,
  entity = "all",
  time = NULL
) {
  if (!is.numeric(values) || !length(values) || any(!is.finite(values)) || any(values < 0)) {
    stop("`values` must contain finite non-negative values.", call. = FALSE)
  }
  n <- length(values)
  weights <- if (is.null(weights)) rep(1, n) else .recycle_wealth_numeric(weights, n, "weights", lower = .Machine$double.eps)
  if (is.null(groups)) groups <- rep("all", n)
  if (length(groups) != n || any(is.na(groups))) stop("`groups` must align with `values`.", call. = FALSE)
  groups <- as.character(groups)
  .assert_single_string(indicator, "indicator")
  .assert_single_string(unit, "unit")
  .assert_flag(higher_is_better, "higher_is_better")
  .assert_single_string(entity, "entity")
  if (!is.null(social_floor)) .assert_scalar_number(social_floor, "social_floor", lower = 0)

  mean_value <- stats::weighted.mean(values, weights)
  p10 <- .weighted_quantile(values, weights, 0.10)
  p40 <- .weighted_quantile(values, weights, 0.40)
  median <- .weighted_quantile(values, weights, 0.50)
  p90 <- .weighted_quantile(values, weights, 0.90)
  total_weighted <- sum(values * weights)
  top_threshold <- .weighted_quantile(values, weights, 0.90)
  bottom_threshold <- p40
  top_share <- if (total_weighted == 0) 0 else sum(values[values >= top_threshold] * weights[values >= top_threshold]) / total_weighted
  bottom_share <- if (total_weighted == 0) 0 else sum(values[values <= bottom_threshold] * weights[values <= bottom_threshold]) / total_weighted
  floor_share <- if (is.null(social_floor)) NA_real_ else sum(weights[values < social_floor]) / sum(weights)
  group_indices <- split(seq_len(n), groups)
  group_summary <- do.call(rbind, lapply(group_indices, function(index) {
    group_total <- sum(values[index] * weights[index])
    data.frame(
      group = groups[index[1L]],
      observations = length(index),
      weight = sum(weights[index]),
      weighted_mean = stats::weighted.mean(values[index], weights[index]),
      resource_share = if (total_weighted == 0) 0 else group_total / total_weighted,
      population_share = sum(weights[index]) / sum(weights),
      stringsAsFactors = FALSE
    )
  }))
  structure(list(
    schema_version = .catalyst_distribution_schema_version(),
    analysis_type = "distributional",
    indicator = indicator,
    unit = unit,
    entity = entity,
    time = time,
    higher_is_better = higher_is_better,
    summary = list(
      observations = n,
      total_weight = sum(weights),
      weighted_mean = mean_value,
      weighted_median = median,
      p10 = p10,
      p40 = p40,
      p90 = p90,
      p90_p10_ratio = ifelse(p10 == 0, NA_real_, p90 / p10),
      gini = .weighted_gini(values, weights),
      top_10_share = top_share,
      bottom_40_share = bottom_share,
      palma_ratio = ifelse(bottom_share == 0, NA_real_, top_share / bottom_share),
      social_floor = social_floor,
      share_below_social_floor = floor_share
    ),
    group_summary = group_summary,
    records = data.frame(value = values, weight = weights, group = groups, stringsAsFactors = FALSE),
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      interpretation = if (higher_is_better) "lower-tail shortfalls require review" else "upper-tail burdens require review"
    )
  ), class = "catalyst_distribution_analysis")
}

#' @rdname distribution_analysis
#' @export
intergenerational_analysis <- function(
  wealth,
  population,
  time,
  social_discount_rate = 0,
  generation_length = 25,
  target_per_capita = NULL,
  entity = "all"
) {
  values <- .align_analysis_vectors(list(wealth, population), c("wealth", "population"))
  n <- length(values$wealth)
  if (any(values$wealth < 0) || any(values$population <= 0)) stop("Wealth must be non-negative and population must be positive.", call. = FALSE)
  if (length(time) != n || any(is.na(time))) stop("`time` must align with wealth and population.", call. = FALSE)
  .assert_scalar_number(social_discount_rate, "social_discount_rate", lower = 0)
  .assert_scalar_number(generation_length, "generation_length", lower = .Machine$double.eps)
  if (!is.null(target_per_capita)) .assert_scalar_number(target_per_capita, "target_per_capita", lower = 0)
  .assert_single_string(entity, "entity")
  numeric_time <- if (inherits(time, "Date")) as.numeric(time - min(time)) / 365.25 else as.numeric(time) - min(as.numeric(time))
  per_capita <- values$wealth / values$population
  discounted <- per_capita / ((1 + social_discount_rate)^numeric_time)
  start <- per_capita[1L]
  trajectory <- data.frame(
    entity = rep(entity, n),
    time = time,
    generation_index = floor(numeric_time / generation_length),
    inclusive_wealth = values$wealth,
    population = values$population,
    wealth_per_capita = per_capita,
    discounted_wealth_per_capita = discounted,
    change_from_start = per_capita - start,
    percent_change_from_start = ifelse(start == 0, NA_real_, 100 * (per_capita / start - 1)),
    target_per_capita = rep(if (is.null(target_per_capita)) NA_real_ else target_per_capita, n),
    target_gap = if (is.null(target_per_capita)) rep(NA_real_, n) else per_capita - target_per_capita,
    stringsAsFactors = FALSE
  )
  structure(list(
    schema_version = .catalyst_distribution_schema_version(),
    analysis_type = "intergenerational",
    entity = entity,
    trajectory = trajectory,
    summary = list(
      start_per_capita = per_capita[1L],
      end_per_capita = per_capita[n],
      absolute_change = per_capita[n] - per_capita[1L],
      percent_change = ifelse(per_capita[1L] == 0, NA_real_, 100 * (per_capita[n] / per_capita[1L] - 1)),
      end_discounted_per_capita = discounted[n],
      target_per_capita = target_per_capita,
      end_target_gap = if (is.null(target_per_capita)) NULL else per_capita[n] - target_per_capita,
      non_declining_signal = per_capita[n] >= per_capita[1L]
    ),
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      social_discount_rate = social_discount_rate,
      generation_length = generation_length
    )
  ), class = "catalyst_intergenerational_analysis")
}

#' @rdname distribution_analysis
#' @export
print.catalyst_distribution_analysis <- function(x, ...) {
  cat(sprintf("<catalyst_distribution_analysis %s>\n", x$indicator))
  cat(sprintf("  observations: %d\n", x$summary$observations))
  cat(sprintf("  gini: %.4f\n", x$summary$gini))
  invisible(x)
}

#' @rdname distribution_analysis
#' @export
print.catalyst_intergenerational_analysis <- function(x, ...) {
  cat(sprintf("<catalyst_intergenerational_analysis %s>\n", x$entity))
  cat(sprintf("  per-capita change: %.4f\n", x$summary$absolute_change))
  invisible(x)
}
