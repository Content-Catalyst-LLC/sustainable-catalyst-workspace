
.econometric_contract_version <- function() "1.0.0"

.econometric_identifier <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z][A-Za-z0-9._-]*$", x)) {
    stop(sprintf("`%s` must begin with a letter and contain only letters, numbers, periods, underscores, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

.econometric_columns <- function(data, columns, arg = "columns") {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  columns <- unique(columns[!is.na(columns) & nzchar(columns)])
  missing <- setdiff(columns, names(data))
  if (length(missing)) stop(sprintf("Unknown %s: %s.", arg, paste(missing, collapse = ", ")), call. = FALSE)
  invisible(columns)
}

.econometric_character <- function(x, arg, allow_empty = TRUE) {
  if (!is.character(x) || anyNA(x) || (!allow_empty && !length(x))) {
    stop(sprintf("`%s` must be a character vector.", arg), call. = FALSE)
  }
  unique(x[nzchar(trimws(x))])
}

#' Record a causal identification assumption
#'
#' @param id Stable assumption identifier.
#' @param label Human-readable label.
#' @param statement Explicit identifying assumption.
#' @param status One of required, supported, challenged, failed, or not_assessed.
#' @param evidence Evidence references or diagnostic notes.
#' @param limitations Known limitations.
#' @return A governed causal-assumption record.
#' @export
causal_assumption <- function(id, label, statement,
                              status = c("required", "supported", "challenged", "failed", "not_assessed"),
                              evidence = list(), limitations = character()) {
  status <- match.arg(status)
  .econometric_identifier(id)
  .assert_single_string(label, "label")
  .assert_single_string(statement, "statement")
  if (!is.list(evidence)) stop("`evidence` must be a list.", call. = FALSE)
  limitations <- .econometric_character(limitations, "limitations")
  structure(list(
    schema_version = .econometric_contract_version(), record_type = "causal_identification_assumption",
    id = id, label = label, statement = statement, status = status,
    evidence = .safe_json_value(evidence), limitations = limitations
  ), class = c("catalyst_causal_assumption", "list"))
}

.validate_causal_assumption <- function(x) {
  if (!is.list(x)) stop("Causal assumption must be a list.", call. = FALSE)
  required <- c("id", "label", "statement", "status", "evidence", "limitations")
  missing <- setdiff(required, names(x))
  if (length(missing)) stop("Causal assumption is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  .econometric_identifier(x$id, "assumption$id")
  .assert_single_string(x$label, "assumption$label")
  .assert_single_string(x$statement, "assumption$statement")
  if (!x$status %in% c("required", "supported", "challenged", "failed", "not_assessed")) stop("Unsupported causal-assumption status.", call. = FALSE)
  if (!is.list(x$evidence) || !is.character(x$limitations)) stop("Causal assumption evidence or limitations are invalid.", call. = FALSE)
  invisible(TRUE)
}

#' Define a governed econometric regression
#'
#' @param id Stable specification identifier.
#' @param title Human-readable title.
#' @param outcome Outcome column.
#' @param predictors Predictor columns.
#' @param unit_id Optional panel-unit column.
#' @param time_id Optional time column.
#' @param weights Optional observation-weight column.
#' @param cluster Optional cluster column for clustered uncertainty.
#' @param confidence_level Confidence level.
#' @param assumptions Causal-assumption records.
#' @param description Method description.
#' @param metadata Additional metadata.
#' @return A governed regression specification.
#' @export
regression_spec <- function(id, title, outcome, predictors, unit_id = NULL, time_id = NULL,
                            weights = NULL, cluster = NULL, confidence_level = 0.95,
                            assumptions = list(), description = "", metadata = list()) {
  .econometric_identifier(id)
  .assert_single_string(title, "title")
  .assert_single_string(outcome, "outcome")
  predictors <- .econometric_character(predictors, "predictors", allow_empty = TRUE)
  for (value in list(unit_id = unit_id, time_id = time_id, weights = weights, cluster = cluster)) {
    if (!is.null(value)) .assert_single_string(value, "optional column")
  }
  .assert_scalar_number(confidence_level, "confidence_level", lower = 0.5, upper = 0.9999)
  if (!is.list(assumptions)) stop("`assumptions` must be a list.", call. = FALSE)
  invisible(lapply(assumptions, .validate_causal_assumption))
  if (length(assumptions)) names(assumptions) <- vapply(assumptions, `[[`, character(1), "id")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .econometric_contract_version(), record_type = "econometric_regression_specification",
    id = id, title = title, outcome = outcome, predictors = predictors,
    unit_id = unit_id, time_id = time_id, weights = weights, cluster = cluster,
    confidence_level = confidence_level, assumptions = assumptions,
    description = description, metadata = metadata
  ), class = c("catalyst_regression_spec", "list"))
}

#' Validate a regression specification
#' @param spec A regression specification.
#' @param data Optional data frame used to validate columns.
#' @return Invisibly returns TRUE.
#' @export
validate_regression_spec <- function(spec, data = NULL) {
  if (!is.list(spec)) stop("`spec` must be a regression specification.", call. = FALSE)
  required <- c("id", "title", "outcome", "predictors", "unit_id", "time_id", "weights", "cluster", "confidence_level", "assumptions")
  missing <- setdiff(required, names(spec))
  if (length(missing)) stop("Regression specification is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  .econometric_identifier(spec$id, "spec$id")
  .assert_single_string(spec$title, "spec$title")
  .assert_single_string(spec$outcome, "spec$outcome")
  if (!is.character(spec$predictors) || anyNA(spec$predictors)) stop("`spec$predictors` must be a character vector.", call. = FALSE)
  .assert_scalar_number(spec$confidence_level, "spec$confidence_level", lower = 0.5, upper = 0.9999)
  invisible(lapply(spec$assumptions, .validate_causal_assumption))
  if (!is.null(data)) {
    columns <- c(spec$outcome, spec$predictors, spec$unit_id, spec$time_id, spec$weights, spec$cluster)
    .econometric_columns(data, columns, "regression columns")
  }
  invisible(TRUE)
}

.econometric_formula <- function(spec, fixed_effects) {
  terms <- spec$predictors
  if (fixed_effects %in% c("unit", "two_way")) terms <- c(terms, sprintf("factor(%s)", spec$unit_id))
  if (fixed_effects %in% c("time", "two_way")) terms <- c(terms, sprintf("factor(%s)", spec$time_id))
  stats::reformulate(terms, response = spec$outcome)
}

.econometric_covariance <- function(X, residuals, df_residual, covariance, cluster = NULL) {
  n <- nrow(X); k <- ncol(X)
  xtx_inv <- tryCatch(solve(crossprod(X)), error = function(error) NULL)
  if (is.null(xtx_inv)) stop("Regression design matrix is singular; revise predictors or fixed effects.", call. = FALSE)
  if (identical(covariance, "classical")) {
    sigma2 <- sum(residuals^2) / df_residual
    return(xtx_inv * sigma2)
  }
  if (identical(covariance, "hc1")) {
    meat <- crossprod(X, X * as.numeric(residuals^2))
    return((n / df_residual) * xtx_inv %*% meat %*% xtx_inv)
  }
  groups <- unique(cluster)
  if (length(groups) < 2L) stop("Clustered covariance requires at least two clusters.", call. = FALSE)
  meat <- matrix(0, nrow = k, ncol = k)
  for (group in groups) {
    index <- which(cluster == group)
    score <- crossprod(X[index, , drop = FALSE], residuals[index])
    meat <- meat + score %*% t(score)
  }
  adjustment <- (length(groups) / (length(groups) - 1)) * ((n - 1) / df_residual)
  adjustment * xtx_inv %*% meat %*% xtx_inv
}

.econometric_diagnostics <- function(y, fitted, residuals, X, df_residual) {
  n <- length(y); k <- ncol(X)
  centered <- y - mean(y)
  r_squared <- if (sum(centered^2) == 0) NA_real_ else 1 - sum(residuals^2) / sum(centered^2)
  adjusted <- if (is.na(r_squared) || df_residual <= 0) NA_real_ else 1 - (1 - r_squared) * (n - 1) / df_residual
  dw <- if (sum(residuals^2) == 0) NA_real_ else sum(diff(residuals)^2) / sum(residuals^2)
  non_intercept <- if (ncol(X) > 1L) X[, -1L, drop = FALSE] else matrix(numeric(), nrow = n, ncol = 0L)
  bp <- list(statistic = NA_real_, df = 0L, p_value = NA_real_)
  if (ncol(non_intercept) > 0L) {
    aux <- stats::lm.fit(cbind(1, non_intercept), residuals^2)
    aux_r2 <- if (sum((residuals^2 - mean(residuals^2))^2) == 0) 0 else 1 - sum(aux$residuals^2) / sum((residuals^2 - mean(residuals^2))^2)
    statistic <- n * max(0, aux_r2)
    bp <- list(statistic = statistic, df = ncol(non_intercept), p_value = stats::pchisq(statistic, ncol(non_intercept), lower.tail = FALSE))
  }
  normality <- list(statistic = NA_real_, p_value = NA_real_, method = "not_assessed")
  if (n >= 3L && n <= 5000L && stats::sd(residuals) > 0) {
    shapiro <- stats::shapiro.test(residuals)
    normality <- list(statistic = unname(shapiro$statistic), p_value = shapiro$p.value, method = shapiro$method)
  }
  list(
    n = n, parameters = k, df_residual = df_residual,
    rmse = sqrt(mean(residuals^2)), mae = mean(abs(residuals)),
    r_squared = r_squared, adjusted_r_squared = adjusted,
    residual_mean = mean(residuals), residual_sd = stats::sd(residuals),
    durbin_watson = dw, condition_number = kappa(X, exact = TRUE),
    breusch_pagan = bp, residual_normality = normality
  )
}

#' Fit a governed policy regression
#'
#' @param data Analysis data frame.
#' @param spec Regression specification.
#' @param fixed_effects None, unit, time, or two_way.
#' @param covariance Classical, HC1, or cluster uncertainty.
#' @return A governed policy-regression result.
#' @export
fit_policy_regression <- function(data, spec, fixed_effects = c("none", "unit", "time", "two_way"),
                                  covariance = c("classical", "hc1", "cluster")) {
  fixed_effects <- match.arg(fixed_effects)
  covariance <- match.arg(covariance)
  validate_regression_spec(spec, data)
  if (fixed_effects %in% c("unit", "two_way") && is.null(spec$unit_id)) stop("Unit fixed effects require `unit_id`.", call. = FALSE)
  if (fixed_effects %in% c("time", "two_way") && is.null(spec$time_id)) stop("Time fixed effects require `time_id`.", call. = FALSE)
  if (identical(covariance, "cluster") && is.null(spec$cluster)) stop("Clustered covariance requires `cluster` in the specification.", call. = FALSE)
  formula <- .econometric_formula(spec, fixed_effects)
  needed <- unique(c(spec$outcome, spec$predictors, spec$unit_id, spec$time_id, spec$weights, if (identical(covariance, "cluster")) spec$cluster else NULL))
  complete <- stats::complete.cases(data[, needed, drop = FALSE])
  analysis_data <- data[complete, , drop = FALSE]
  if (nrow(analysis_data) < 3L) stop("At least three complete observations are required.", call. = FALSE)
  X <- stats::model.matrix(formula, data = analysis_data)
  y <- as.numeric(analysis_data[[spec$outcome]])
  if (any(!is.finite(y))) stop("Outcome values must be finite.", call. = FALSE)
  weights <- if (is.null(spec$weights)) rep(1, length(y)) else as.numeric(analysis_data[[spec$weights]])
  if (any(!is.finite(weights)) || any(weights <= 0)) stop("Regression weights must be finite and positive.", call. = FALSE)
  Xw <- X * sqrt(weights); yw <- y * sqrt(weights)
  fit <- stats::lm.fit(Xw, yw)
  if (fit$rank < ncol(Xw) || anyNA(fit$coefficients)) stop("Regression design matrix is rank deficient; revise predictors or fixed effects.", call. = FALSE)
  beta <- unname(fit$coefficients); names(beta) <- colnames(X)
  fitted <- as.numeric(X %*% beta); residuals <- y - fitted
  df_residual <- nrow(X) - ncol(X)
  if (df_residual <= 0) stop("Regression requires positive residual degrees of freedom.", call. = FALSE)
  cluster <- if (identical(covariance, "cluster")) analysis_data[[spec$cluster]] else NULL
  vcov <- .econometric_covariance(Xw, residuals * sqrt(weights), df_residual, covariance, cluster)
  se <- sqrt(pmax(0, diag(vcov)))
  statistic <- beta / se
  p_value <- 2 * stats::pt(abs(statistic), df = df_residual, lower.tail = FALSE)
  alpha <- 1 - spec$confidence_level
  critical <- stats::qt(1 - alpha / 2, df = df_residual)
  coefficients <- data.frame(
    term = names(beta), estimate = as.numeric(beta), std_error = as.numeric(se),
    statistic = as.numeric(statistic), p_value = as.numeric(p_value),
    conf_low = as.numeric(beta - critical * se), conf_high = as.numeric(beta + critical * se),
    stringsAsFactors = FALSE
  )
  result <- structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "policy_regression",
    id = spec$id, title = spec$title, spec = spec, formula = paste(deparse(formula), collapse = " "),
    fixed_effects = fixed_effects, covariance = covariance,
    coefficients = coefficients, variance_covariance = vcov,
    fitted = fitted, residuals = residuals, row_ids = which(complete),
    diagnostics = .econometric_diagnostics(y, fitted, residuals, X, df_residual),
    metadata = list(package_version = .catalyst_package_version(), created_at = format(Sys.time(), tz = "UTC", usetz = TRUE)),
    boundary = list(association_not_causation = TRUE, causal_claim_requires_identification_review = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_policy_regression", "list"))
  result
}

#' Fit a panel regression
#' @param data Analysis data frame.
#' @param spec Regression specification with unit and time identifiers.
#' @param effects Unit, time, or two-way fixed effects.
#' @param covariance Classical, HC1, or cluster uncertainty.
#' @return A policy-regression result.
#' @export
panel_regression <- function(data, spec, effects = c("two_way", "unit", "time"), covariance = c("cluster", "hc1", "classical")) {
  effects <- match.arg(effects); covariance <- match.arg(covariance)
  fit_policy_regression(data, spec, fixed_effects = effects, covariance = covariance)
}

#' Regression diagnostic evidence
#' @param model A policy-regression result.
#' @return Diagnostic record.
#' @export
regression_diagnostics <- function(model) {
  if (!inherits(model, "catalyst_policy_regression")) stop("`model` must be a policy regression.", call. = FALSE)
  model$diagnostics
}

.econometric_effect <- function(regression, term, label) {
  row <- regression$coefficients[regression$coefficients$term == term, , drop = FALSE]
  if (nrow(row) != 1L) stop(sprintf("Effect term `%s` was not estimable.", term), call. = FALSE)
  list(label = label, term = term, estimate = row$estimate[[1L]], std_error = row$std_error[[1L]],
       p_value = row$p_value[[1L]], conf_low = row$conf_low[[1L]], conf_high = row$conf_high[[1L]])
}

#' Difference-in-differences policy evaluation
#'
#' @param data Panel data.
#' @param outcome Outcome column.
#' @param treatment Treatment-group indicator.
#' @param post Post-intervention indicator.
#' @param unit_id Unit identifier.
#' @param time_id Time identifier.
#' @param covariates Optional covariates.
#' @param cluster Cluster column; defaults to unit identifier.
#' @param confidence_level Confidence level.
#' @param assumptions Causal-assumption records.
#' @param id Stable evaluation identifier.
#' @param title Human-readable title.
#' @return A governed difference-in-differences result.
#' @export
difference_in_differences <- function(data, outcome, treatment, post, unit_id, time_id,
                                      covariates = character(), cluster = unit_id,
                                      confidence_level = 0.95, assumptions = list(),
                                      id = "difference-in-differences", title = "Difference-in-differences evaluation") {
  .econometric_columns(data, c(outcome, treatment, post, unit_id, time_id, covariates, cluster), "difference-in-differences columns")
  working <- data
  working$.catalyst_did <- as.numeric(working[[treatment]]) * as.numeric(working[[post]])
  spec <- regression_spec(id, title, outcome, c(".catalyst_did", covariates), unit_id, time_id,
                          cluster = cluster, confidence_level = confidence_level, assumptions = assumptions,
                          description = "Two-way fixed-effects difference-in-differences specification.")
  regression <- fit_policy_regression(working, spec, fixed_effects = "two_way", covariance = "cluster")
  effect <- .econometric_effect(regression, ".catalyst_did", "Average treatment effect on treated")
  structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "difference_in_differences",
    id = id, title = title, regression = regression, effect = effect,
    identification = list(design = "two_way_fixed_effects_did", treatment = treatment, post = post,
                          assumptions = assumptions, parallel_trends_requires_review = TRUE),
    boundary = list(causal_effect_requires_parallel_trends = TRUE, no_automatic_causal_authorization = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_difference_in_differences", "list"))
}

.event_term <- function(period) paste0(".catalyst_event_", if (period < 0) paste0("m", abs(period)) else paste0("p", period))

#' Event-study policy evaluation
#'
#' @param data Panel data.
#' @param outcome Outcome column.
#' @param treated Treatment-group indicator.
#' @param event_time Relative event-time column.
#' @param unit_id Unit identifier.
#' @param time_id Time identifier.
#' @param reference_period Omitted event period.
#' @param window Optional two-value lead/lag window.
#' @param covariates Optional covariates.
#' @param cluster Cluster column.
#' @param confidence_level Confidence level.
#' @param assumptions Causal-assumption records.
#' @param id Stable evaluation identifier.
#' @param title Human-readable title.
#' @return A governed event-study result.
#' @export
event_study <- function(data, outcome, treated, event_time, unit_id, time_id,
                        reference_period = -1, window = NULL, covariates = character(),
                        cluster = unit_id, confidence_level = 0.95, assumptions = list(),
                        id = "event-study", title = "Event-study evaluation") {
  .econometric_columns(data, c(outcome, treated, event_time, unit_id, time_id, covariates, cluster), "event-study columns")
  periods <- sort(unique(as.numeric(data[[event_time]])))
  periods <- periods[is.finite(periods)]
  if (!is.null(window)) {
    if (!is.numeric(window) || length(window) != 2L || any(!is.finite(window)) || window[[1L]] > window[[2L]]) stop("`window` must contain finite lower and upper periods.", call. = FALSE)
    periods <- periods[periods >= window[[1L]] & periods <= window[[2L]]]
  }
  periods <- setdiff(periods, reference_period)
  if (!length(periods)) stop("Event study requires at least one non-reference period.", call. = FALSE)
  working <- data; terms <- character(length(periods))
  for (i in seq_along(periods)) {
    terms[[i]] <- .event_term(periods[[i]])
    working[[terms[[i]]]] <- as.numeric(working[[treated]]) * as.numeric(working[[event_time]] == periods[[i]])
  }
  spec <- regression_spec(id, title, outcome, c(terms, covariates), unit_id, time_id, cluster = cluster,
                          confidence_level = confidence_level, assumptions = assumptions,
                          description = "Dynamic event-study with unit and time fixed effects.")
  regression <- fit_policy_regression(working, spec, fixed_effects = "two_way", covariance = "cluster")
  effects <- merge(data.frame(term = terms, period = periods, stringsAsFactors = FALSE), regression$coefficients, by = "term", all.x = TRUE, sort = FALSE)
  effects <- effects[order(effects$period), c("period", "term", "estimate", "std_error", "statistic", "p_value", "conf_low", "conf_high")]
  pre <- effects[effects$period < reference_period, , drop = FALSE]
  pretrend <- list(periods = nrow(pre), status = if (!nrow(pre)) "not_assessed" else if (all(pre$p_value > 0.05, na.rm = TRUE)) "not_rejected" else "challenged",
                   maximum_absolute_estimate = if (!nrow(pre)) NA_real_ else max(abs(pre$estimate), na.rm = TRUE))
  structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "event_study",
    id = id, title = title, reference_period = reference_period, regression = regression,
    effects = effects, pretrend_diagnostic = pretrend,
    identification = list(assumptions = assumptions, no_anticipation_requires_review = TRUE, parallel_trends_requires_review = TRUE),
    boundary = list(event_coefficients_not_automatic_causal_proof = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_event_study", "list"))
}

#' Interrupted time-series policy evaluation
#'
#' @param data Time-series data.
#' @param outcome Outcome column.
#' @param time Time index column.
#' @param intervention_time Intervention time.
#' @param covariates Optional covariates.
#' @param confidence_level Confidence level.
#' @param assumptions Causal-assumption records.
#' @param id Stable evaluation identifier.
#' @param title Human-readable title.
#' @return A governed interrupted-time-series result.
#' @export
interrupted_time_series <- function(data, outcome, time, intervention_time, covariates = character(),
                                    confidence_level = 0.95, assumptions = list(),
                                    id = "interrupted-time-series", title = "Interrupted time-series evaluation") {
  .econometric_columns(data, c(outcome, time, covariates), "interrupted-time-series columns")
  .assert_scalar_number(intervention_time, "intervention_time")
  working <- data
  working$.catalyst_post <- as.numeric(working[[time]] >= intervention_time)
  working$.catalyst_time_after <- pmax(0, as.numeric(working[[time]]) - intervention_time)
  spec <- regression_spec(id, title, outcome, c(time, ".catalyst_post", ".catalyst_time_after", covariates),
                          confidence_level = confidence_level, assumptions = assumptions,
                          description = "Segmented regression for level and slope changes.")
  regression <- fit_policy_regression(working, spec, fixed_effects = "none", covariance = "hc1")
  structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "interrupted_time_series",
    id = id, title = title, intervention_time = intervention_time, regression = regression,
    immediate_level_change = .econometric_effect(regression, ".catalyst_post", "Immediate level change"),
    slope_change = .econometric_effect(regression, ".catalyst_time_after", "Post-intervention slope change"),
    identification = list(assumptions = assumptions, concurrent_shocks_require_review = TRUE, functional_form_requires_review = TRUE),
    boundary = list(interruption_not_randomization = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_interrupted_time_series", "list"))
}

.synthetic_softmax <- function(theta) {
  shifted <- theta - max(theta); values <- exp(shifted); values / sum(values)
}

#' Synthetic-control policy evaluation
#'
#' @param data Long panel data.
#' @param outcome Outcome column.
#' @param unit_id Unit identifier.
#' @param time_id Time identifier.
#' @param treated_unit Treated unit value.
#' @param intervention_time First post-intervention period.
#' @param donor_units Optional donor-unit values.
#' @param confidence_level Confidence level retained in metadata.
#' @param assumptions Causal-assumption records.
#' @param id Stable evaluation identifier.
#' @param title Human-readable title.
#' @return A governed synthetic-control result.
#' @export
synthetic_control <- function(data, outcome, unit_id, time_id, treated_unit, intervention_time,
                              donor_units = NULL, confidence_level = 0.95, assumptions = list(),
                              id = "synthetic-control", title = "Synthetic-control evaluation") {
  .econometric_columns(data, c(outcome, unit_id, time_id), "synthetic-control columns")
  .assert_scalar_number(intervention_time, "intervention_time")
  .assert_scalar_number(confidence_level, "confidence_level", lower = 0.5, upper = 0.9999)
  units <- unique(as.character(data[[unit_id]])); treated_unit <- as.character(treated_unit)
  if (!treated_unit %in% units) stop("Treated unit is not present in the data.", call. = FALSE)
  if (is.null(donor_units)) donor_units <- setdiff(units, treated_unit)
  donor_units <- as.character(donor_units)
  if (!length(donor_units) || any(!donor_units %in% units) || treated_unit %in% donor_units) stop("Donor units must be present and exclude the treated unit.", call. = FALSE)
  times <- sort(unique(as.numeric(data[[time_id]])))
  pre_times <- times[times < intervention_time]; post_times <- times[times >= intervention_time]
  if (length(pre_times) < 2L || !length(post_times)) stop("Synthetic control requires at least two pre-periods and one post-period.", call. = FALSE)
  value_at <- function(unit, time) {
    values <- data[[outcome]][as.character(data[[unit_id]]) == unit & as.numeric(data[[time_id]]) == time]
    if (length(values) != 1L || !is.finite(values)) stop("Synthetic-control panel must contain one finite observation per unit and time.", call. = FALSE)
    as.numeric(values)
  }
  treated_pre <- vapply(pre_times, function(time) value_at(treated_unit, time), numeric(1))
  donor_pre <- vapply(donor_units, function(unit) vapply(pre_times, function(time) value_at(unit, time), numeric(1)), numeric(length(pre_times)))
  if (is.null(dim(donor_pre))) donor_pre <- matrix(donor_pre, ncol = 1L)
  objective <- function(theta) {
    weights <- .synthetic_softmax(theta)
    sum((treated_pre - as.numeric(donor_pre %*% weights))^2)
  }
  if (length(donor_units) == 1L) {
    fit <- list(par = 0, value = objective(0), convergence = 0L)
  } else {
    initial_weights <- tryCatch(as.numeric(qr.solve(donor_pre, treated_pre)), error = function(error) rep(1 / length(donor_units), length(donor_units)))
    initial_weights[!is.finite(initial_weights)] <- 0
    initial_weights <- pmax(initial_weights, 1e-8)
    initial_weights <- initial_weights / sum(initial_weights)
    fit <- stats::optim(log(initial_weights), objective, method = "BFGS")
  }
  weights <- .synthetic_softmax(fit$par); names(weights) <- donor_units
  effects <- do.call(rbind, lapply(times, function(time) {
    treated <- value_at(treated_unit, time)
    synthetic <- sum(weights * vapply(donor_units, function(unit) value_at(unit, time), numeric(1)))
    data.frame(time = time, treated = treated, synthetic = synthetic, gap = treated - synthetic,
               period = if (time < intervention_time) "pre" else "post", stringsAsFactors = FALSE)
  }))
  pre_gap <- effects$gap[effects$period == "pre"]; post_gap <- effects$gap[effects$period == "post"]
  summary <- list(
    pre_rmspe = sqrt(mean(pre_gap^2)), post_rmspe = sqrt(mean(post_gap^2)),
    average_post_effect = mean(post_gap), cumulative_post_effect = sum(post_gap),
    rmspe_ratio = if (sqrt(mean(pre_gap^2)) == 0) Inf else sqrt(mean(post_gap^2)) / sqrt(mean(pre_gap^2)),
    optimizer_convergence = fit$convergence
  )
  structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "synthetic_control",
    id = id, title = title, outcome = outcome, treated_unit = treated_unit,
    donor_weights = data.frame(unit = donor_units, weight = as.numeric(weights), stringsAsFactors = FALSE),
    intervention_time = intervention_time, effects = effects, summary = summary,
    identification = list(assumptions = assumptions, convex_hull_support_required = TRUE, no_interference_requires_review = TRUE),
    boundary = list(placebo_and_sensitivity_review_required = TRUE, synthetic_control_not_automatic_causal_proof = TRUE, human_review_required = TRUE)
  ), class = c("catalyst_synthetic_control", "list"))
}

#' Summarize policy effects
#' @param evaluation An econometric evaluation or policy-evaluation analysis.
#' @return A data frame of policy effects.
#' @export
policy_effect_summary <- function(evaluation) {
  if (inherits(evaluation, "catalyst_policy_evaluation_analysis")) {
    rows <- lapply(evaluation$evaluations, policy_effect_summary)
    rows <- rows[vapply(rows, nrow, integer(1)) > 0L]
    return(if (!length(rows)) data.frame() else do.call(rbind, rows))
  }
  row <- NULL
  if (inherits(evaluation, "catalyst_difference_in_differences")) {
    effect <- evaluation$effect
    row <- data.frame(evaluation_id = evaluation$id, method = "difference_in_differences", effect = effect$estimate, std_error = effect$std_error, p_value = effect$p_value, conf_low = effect$conf_low, conf_high = effect$conf_high, stringsAsFactors = FALSE)
  } else if (inherits(evaluation, "catalyst_interrupted_time_series")) {
    effect <- evaluation$immediate_level_change
    row <- data.frame(evaluation_id = evaluation$id, method = "interrupted_time_series_level", effect = effect$estimate, std_error = effect$std_error, p_value = effect$p_value, conf_low = effect$conf_low, conf_high = effect$conf_high, stringsAsFactors = FALSE)
  } else if (inherits(evaluation, "catalyst_event_study")) {
    post <- evaluation$effects[evaluation$effects$period >= 0, , drop = FALSE]
    if (nrow(post)) row <- data.frame(evaluation_id = evaluation$id, method = "event_study_average_post", effect = mean(post$estimate), std_error = sqrt(mean(post$std_error^2)), p_value = NA_real_, conf_low = mean(post$conf_low), conf_high = mean(post$conf_high), stringsAsFactors = FALSE)
  } else if (inherits(evaluation, "catalyst_synthetic_control")) {
    row <- data.frame(evaluation_id = evaluation$id, method = "synthetic_control_average_post", effect = evaluation$summary$average_post_effect, std_error = NA_real_, p_value = NA_real_, conf_low = NA_real_, conf_high = NA_real_, stringsAsFactors = FALSE)
  } else if (inherits(evaluation, "catalyst_policy_regression")) {
    rows <- evaluation$coefficients[evaluation$coefficients$term != "(Intercept)", , drop = FALSE]
    if (nrow(rows)) row <- data.frame(evaluation_id = evaluation$id, method = paste0("regression_", rows$term), effect = rows$estimate, std_error = rows$std_error, p_value = rows$p_value, conf_low = rows$conf_low, conf_high = rows$conf_high, stringsAsFactors = FALSE)
  } else stop("Unsupported econometric evaluation.", call. = FALSE)
  row
}

#' Create an integrated policy-evaluation analysis
#'
#' @param id Stable analysis identifier.
#' @param title Human-readable title.
#' @param evaluations Named econometric evaluations.
#' @param assumptions Cross-method causal assumptions.
#' @param decision_context Decision context.
#' @param review_status Draft, under_review, or approved_for_specified_use.
#' @param metadata Additional metadata.
#' @return A governed policy-evaluation analysis.
#' @export
policy_evaluation_analysis <- function(id, title, evaluations, assumptions = list(), decision_context = "",
                                       review_status = c("draft", "under_review", "approved_for_specified_use"), metadata = list()) {
  review_status <- match.arg(review_status)
  .econometric_identifier(id); .assert_single_string(title, "title")
  if (!is.list(evaluations) || !length(evaluations)) stop("`evaluations` must be a non-empty list.", call. = FALSE)
  allowed <- c("catalyst_policy_regression", "catalyst_difference_in_differences", "catalyst_event_study", "catalyst_interrupted_time_series", "catalyst_synthetic_control")
  if (any(!vapply(evaluations, function(x) any(class(x) %in% allowed), logical(1)))) stop("Every evaluation must be a supported econometric result.", call. = FALSE)
  if (is.null(names(evaluations)) || any(!nzchar(names(evaluations)))) names(evaluations) <- vapply(evaluations, `[[`, character(1), "id")
  invisible(lapply(assumptions, .validate_causal_assumption))
  .assert_single_string(decision_context, "decision_context", allow_empty = TRUE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  effects <- policy_effect_summary(structure(list(evaluations = evaluations), class = c("catalyst_policy_evaluation_analysis", "list")))
  statuses <- if (!length(assumptions)) character() else vapply(assumptions, `[[`, character(1), "status")
  identification_status <- if (any(statuses == "failed")) "failed" else if (any(statuses == "challenged")) "challenged" else if (length(statuses) && all(statuses == "supported")) "supported" else "requires_review"
  structure(list(
    schema_version = .econometric_contract_version(), analysis_type = "econometrics_and_policy_evaluation",
    id = id, title = title, decision_context = decision_context,
    evaluations = evaluations, effects = effects, assumptions = assumptions,
    identification_status = identification_status, review_status = review_status,
    metadata = utils::modifyList(list(package_version = .catalyst_package_version(), created_at = format(Sys.time(), tz = "UTC", usetz = TRUE)), metadata),
    boundary = list(causal_claim_requires_design_specific_assumptions = TRUE, automated_policy_authorization = FALSE, human_review_required = TRUE)
  ), class = c("catalyst_policy_evaluation_analysis", "list"))
}

#' Policy-evaluation summary
#' @param analysis A policy-evaluation analysis.
#' @return Compact summary record.
#' @export
policy_evaluation_summary <- function(analysis) {
  if (!inherits(analysis, "catalyst_policy_evaluation_analysis")) stop("`analysis` must be a policy-evaluation analysis.", call. = FALSE)
  list(id = analysis$id, title = analysis$title, evaluations = length(analysis$evaluations), effects = nrow(analysis$effects),
       identification_status = analysis$identification_status, review_status = analysis$review_status,
       human_review_required = analysis$boundary$human_review_required)
}

#' Plot policy-effect estimates
#' @param analysis A policy-evaluation analysis or supported evaluation.
#' @return A ggplot object.
#' @export
plot_policy_effects <- function(analysis) {
  effects <- policy_effect_summary(analysis)
  if (!nrow(effects)) stop("No policy effects are available to plot.", call. = FALSE)
  effects$label <- paste(effects$evaluation_id, effects$method, sep = " / ")
  ggplot2::ggplot(effects, ggplot2::aes(x = stats::reorder(.data$label, .data$effect), y = .data$effect)) +
    ggplot2::geom_hline(yintercept = 0, linetype = "dashed") +
    ggplot2::geom_errorbar(ggplot2::aes(ymin = .data$conf_low, ymax = .data$conf_high), width = 0.15, na.rm = TRUE) +
    ggplot2::geom_point(size = 2.5) + ggplot2::coord_flip() + theme_catalyst() +
    ggplot2::labs(x = NULL, y = "Estimated effect", title = "Policy-effect estimates", subtitle = "Intervals require design-specific causal review")
}

#' Plot an event study
#' @param evaluation An event-study result.
#' @return A ggplot object.
#' @export
plot_event_study <- function(evaluation) {
  if (!inherits(evaluation, "catalyst_event_study")) stop("`evaluation` must be an event-study result.", call. = FALSE)
  ggplot2::ggplot(evaluation$effects, ggplot2::aes(x = .data$period, y = .data$estimate)) +
    ggplot2::geom_hline(yintercept = 0, linetype = "dashed") + ggplot2::geom_vline(xintercept = evaluation$reference_period, linetype = "dotted") +
    ggplot2::geom_ribbon(ggplot2::aes(ymin = .data$conf_low, ymax = .data$conf_high), alpha = 0.15) +
    ggplot2::geom_line() + ggplot2::geom_point() + theme_catalyst() +
    ggplot2::labs(x = "Event time", y = "Estimated effect", title = evaluation$title)
}

#' Plot a synthetic-control gap
#' @param evaluation A synthetic-control result.
#' @return A ggplot object.
#' @export
plot_synthetic_control <- function(evaluation) {
  if (!inherits(evaluation, "catalyst_synthetic_control")) stop("`evaluation` must be a synthetic-control result.", call. = FALSE)
  ggplot2::ggplot(evaluation$effects, ggplot2::aes(x = .data$time, y = .data$gap)) +
    ggplot2::geom_hline(yintercept = 0, linetype = "dashed") + ggplot2::geom_vline(xintercept = evaluation$intervention_time, linetype = "dotted") +
    ggplot2::geom_line() + ggplot2::geom_point() + theme_catalyst() +
    ggplot2::labs(x = "Time", y = "Treated - synthetic", title = evaluation$title)
}

#' @export
print.catalyst_policy_regression <- function(x, ...) {
  cat(sprintf("<catalyst_policy_regression %s>\n", x$id)); cat(sprintf("  %s\n", x$title)); cat(sprintf("  n: %d | covariance: %s | fixed effects: %s\n", x$diagnostics$n, x$covariance, x$fixed_effects)); invisible(x)
}
#' @export
print.catalyst_policy_evaluation_analysis <- function(x, ...) {
  summary <- policy_evaluation_summary(x); cat(sprintf("<catalyst_policy_evaluation_analysis %s>\n", x$id)); cat(sprintf("  evaluations: %d | effects: %d | identification: %s\n", summary$evaluations, summary$effects, summary$identification_status)); invisible(x)
}
