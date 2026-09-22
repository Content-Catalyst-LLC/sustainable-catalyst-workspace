.policy_contract_version <- function() "1.0.0"

.policy_identifier <- function(x, arg = "id") {
  .assert_single_string(x, arg)
  if (!grepl("^[A-Za-z][A-Za-z0-9._-]*$", x)) {
    stop(sprintf("`%s` must begin with a letter and contain only letters, numbers, periods, underscores, or hyphens.", arg), call. = FALSE)
  }
  invisible(x)
}

.policy_named_records <- function(x, arg, validator) {
  if (!is.list(x) || !length(x)) stop(sprintf("`%s` must be a non-empty list.", arg), call. = FALSE)
  result <- vector("list", length(x))
  ids <- character(length(x))
  for (i in seq_along(x)) {
    validator(x[[i]])
    ids[[i]] <- x[[i]]$id
    result[[i]] <- x[[i]]
  }
  if (anyDuplicated(ids)) stop(sprintf("`%s` cannot contain duplicate identifiers.", arg), call. = FALSE)
  names(result) <- ids
  result
}

#' Define a policy decision variable
#'
#' @param id Stable variable identifier.
#' @param label Human-readable label.
#' @param target Nested scenario field such as `policy$s` or `parameters$alpha`.
#' @param lower,upper Feasible bounds.
#' @param initial Initial or reference value.
#' @param step Grid-search step. When `NULL`, five evenly spaced values are used.
#' @param type Continuous or integer variable.
#' @param unit Unit label.
#' @param description Method note.
#' @return A governed decision-variable record.
#' @export
decision_variable <- function(id, label, target, lower, upper, initial = NULL, step = NULL,
                              type = c("continuous", "integer"), unit = "", description = "") {
  type <- match.arg(type)
  .policy_identifier(id)
  .assert_single_string(label, "label")
  .assert_single_string(target, "target")
  .assert_scalar_number(lower, "lower")
  .assert_scalar_number(upper, "upper")
  if (lower >= upper) stop("`lower` must be less than `upper`.", call. = FALSE)
  if (is.null(initial)) initial <- (lower + upper) / 2
  .assert_scalar_number(initial, "initial", lower = lower, upper = upper)
  if (!is.null(step)) .assert_scalar_number(step, "step", lower = .Machine$double.eps)
  .assert_single_string(unit, "unit", allow_empty = TRUE)
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (identical(type, "integer")) {
    lower <- ceiling(lower); upper <- floor(upper); initial <- round(initial)
    if (!is.null(step)) step <- max(1, round(step))
    if (lower > upper) stop("Integer bounds do not contain a feasible value.", call. = FALSE)
  }
  structure(list(
    schema_version = .policy_contract_version(), record_type = "policy_decision_variable",
    id = id, label = label, target = target, lower = lower, upper = upper,
    initial = initial, step = step, type = type, unit = unit, description = description
  ), class = c("catalyst_decision_variable", "list"))
}

.validate_decision_variable <- function(x) {
  if (!is.list(x)) stop("Decision variable must be a list.", call. = FALSE)
  required <- c("id", "label", "target", "lower", "upper", "initial", "type")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Decision variable is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  .policy_identifier(x$id, "variable$id"); .assert_single_string(x$label, "variable$label"); .assert_single_string(x$target, "variable$target")
  .assert_scalar_number(x$lower, "variable$lower"); .assert_scalar_number(x$upper, "variable$upper")
  if (x$lower >= x$upper) stop("Decision-variable lower bound must be less than upper bound.", call. = FALSE)
  .assert_scalar_number(x$initial, "variable$initial", lower = x$lower, upper = x$upper)
  if (!x$type %in% c("continuous", "integer")) stop("Unsupported decision-variable type.", call. = FALSE)
  if (!is.null(x$step)) .assert_scalar_number(x$step, "variable$step", lower = .Machine$double.eps)
  invisible(TRUE)
}

#' Define an optimization objective
#'
#' @param id Stable objective identifier.
#' @param label Human-readable label.
#' @param metric Evaluator metric name.
#' @param direction Minimize, maximize, or target.
#' @param weight Relative objective weight.
#' @param target Target value for target objectives.
#' @param tolerance Optional reporting tolerance.
#' @param unit Unit label.
#' @return A governed objective record.
#' @export
policy_objective <- function(id, label, metric, direction = c("minimize", "maximize", "target"),
                             weight = 1, target = NULL, tolerance = NULL, unit = "") {
  direction <- match.arg(direction)
  .policy_identifier(id); .assert_single_string(label, "label"); .assert_single_string(metric, "metric")
  .assert_scalar_number(weight, "weight", lower = .Machine$double.eps)
  if (identical(direction, "target")) {
    if (is.null(target)) stop("Target objectives require `target`.", call. = FALSE)
    .assert_scalar_number(target, "target")
  } else if (!is.null(target)) .assert_scalar_number(target, "target")
  if (!is.null(tolerance)) .assert_scalar_number(tolerance, "tolerance", lower = 0)
  .assert_single_string(unit, "unit", allow_empty = TRUE)
  structure(list(
    schema_version = .policy_contract_version(), record_type = "policy_objective",
    id = id, label = label, metric = metric, direction = direction, weight = weight,
    target = target, tolerance = tolerance, unit = unit
  ), class = c("catalyst_policy_objective", "list"))
}

.validate_policy_objective <- function(x) {
  if (!is.list(x)) stop("Policy objective must be a list.", call. = FALSE)
  required <- c("id", "label", "metric", "direction", "weight")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Policy objective is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  .policy_identifier(x$id, "objective$id"); .assert_single_string(x$label, "objective$label"); .assert_single_string(x$metric, "objective$metric")
  if (!x$direction %in% c("minimize", "maximize", "target")) stop("Unsupported objective direction.", call. = FALSE)
  .assert_scalar_number(x$weight, "objective$weight", lower = .Machine$double.eps)
  if (identical(x$direction, "target")) .assert_scalar_number(x$target, "objective$target")
  invisible(TRUE)
}

#' Define a policy constraint
#'
#' @param id Stable constraint identifier.
#' @param label Human-readable label.
#' @param metric Evaluator metric name.
#' @param operator One of `<=`, `>=`, `==`, or `between`.
#' @param value Comparison value for scalar operators.
#' @param lower,upper Bounds for a between constraint.
#' @param tolerance Numerical equality tolerance.
#' @param hard Whether violation removes a candidate from the feasible region.
#' @return A governed constraint record.
#' @export
policy_constraint <- function(id, label, metric, operator = c("<=", ">=", "==", "between"),
                              value = NULL, lower = NULL, upper = NULL, tolerance = 1e-8, hard = TRUE) {
  operator <- match.arg(operator)
  .policy_identifier(id); .assert_single_string(label, "label"); .assert_single_string(metric, "metric")
  .assert_scalar_number(tolerance, "tolerance", lower = 0); .assert_flag(hard, "hard")
  if (identical(operator, "between")) {
    if (is.null(lower) || is.null(upper)) stop("Between constraints require `lower` and `upper`.", call. = FALSE)
    .assert_scalar_number(lower, "lower"); .assert_scalar_number(upper, "upper")
    if (lower > upper) stop("Constraint lower bound cannot exceed upper bound.", call. = FALSE)
  } else {
    if (is.null(value)) stop("Scalar constraints require `value`.", call. = FALSE)
    .assert_scalar_number(value, "value")
  }
  structure(list(
    schema_version = .policy_contract_version(), record_type = "policy_constraint",
    id = id, label = label, metric = metric, operator = operator, value = value,
    lower = lower, upper = upper, tolerance = tolerance, hard = hard
  ), class = c("catalyst_policy_constraint", "list"))
}

.validate_policy_constraint <- function(x) {
  if (!is.list(x)) stop("Policy constraint must be a list.", call. = FALSE)
  required <- c("id", "label", "metric", "operator", "tolerance", "hard")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Policy constraint is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  .policy_identifier(x$id, "constraint$id"); .assert_single_string(x$label, "constraint$label"); .assert_single_string(x$metric, "constraint$metric")
  if (!x$operator %in% c("<=", ">=", "==", "between")) stop("Unsupported constraint operator.", call. = FALSE)
  .assert_scalar_number(x$tolerance, "constraint$tolerance", lower = 0); .assert_flag(x$hard, "constraint$hard")
  if (identical(x$operator, "between")) {
    .assert_scalar_number(x$lower, "constraint$lower"); .assert_scalar_number(x$upper, "constraint$upper")
  } else .assert_scalar_number(x$value, "constraint$value")
  invisible(TRUE)
}

#' Create a policy optimization specification
#'
#' @param id Stable analysis identifier.
#' @param title Human-readable title.
#' @param variables Decision-variable records.
#' @param objectives Objective records.
#' @param constraints Optional constraint records.
#' @param method Grid or random-search candidate generation.
#' @param max_evaluations Maximum candidate evaluations.
#' @param seed Reproducible random seed.
#' @param description Analysis purpose.
#' @param metadata Additional metadata.
#' @return A `catalyst_policy_optimization_spec`.
#' @export
policy_optimization_spec <- function(id, title, variables, objectives, constraints = list(),
                                     method = c("grid", "random_search"), max_evaluations = 1000L,
                                     seed = 1L, description = "", metadata = list()) {
  method <- match.arg(method)
  .policy_identifier(id); .assert_single_string(title, "title"); .assert_single_string(description, "description", allow_empty = TRUE)
  .assert_scalar_number(max_evaluations, "max_evaluations", lower = 1); .assert_scalar_number(seed, "seed")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  variables <- .policy_named_records(variables, "variables", .validate_decision_variable)
  objectives <- .policy_named_records(objectives, "objectives", .validate_policy_objective)
  if (!is.list(constraints)) stop("`constraints` must be a list.", call. = FALSE)
  if (length(constraints)) constraints <- .policy_named_records(constraints, "constraints", .validate_policy_constraint)
  metric_names <- c(vapply(objectives, `[[`, character(1), "metric"), if (length(constraints)) vapply(constraints, `[[`, character(1), "metric") else character())
  if (length(intersect(names(variables), metric_names))) stop("Variable identifiers cannot duplicate evaluator metric names.", call. = FALSE)
  result <- structure(list(
    schema_version = .policy_contract_version(), analysis_type = "policy_optimization_specification",
    id = id, title = title, description = description, variables = variables,
    objectives = objectives, constraints = constraints, method = method,
    max_evaluations = as.integer(max_evaluations), seed = as.integer(seed), metadata = metadata
  ), class = c("catalyst_policy_optimization_spec", "list"))
  validate_policy_optimization_spec(result)
  result
}

#' Validate a policy optimization specification
#' @param spec Optimization specification.
#' @return Invisibly returns `TRUE`.
#' @export
validate_policy_optimization_spec <- function(spec) {
  if (!is.list(spec)) stop("`spec` must be a list.", call. = FALSE)
  required <- c("schema_version", "analysis_type", "id", "title", "variables", "objectives", "constraints", "method", "max_evaluations", "seed")
  missing <- setdiff(required, names(spec)); if (length(missing)) stop("Optimization specification is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(spec$schema_version, .policy_contract_version())) stop("Unsupported policy optimization schema version.", call. = FALSE)
  .policy_identifier(spec$id, "spec$id"); .assert_single_string(spec$title, "spec$title")
  .policy_named_records(spec$variables, "spec$variables", .validate_decision_variable)
  .policy_named_records(spec$objectives, "spec$objectives", .validate_policy_objective)
  if (length(spec$constraints)) .policy_named_records(spec$constraints, "spec$constraints", .validate_policy_constraint)
  if (!spec$method %in% c("grid", "random_search")) stop("Unsupported optimization method.", call. = FALSE)
  .assert_scalar_number(spec$max_evaluations, "spec$max_evaluations", lower = 1); .assert_scalar_number(spec$seed, "spec$seed")
  invisible(TRUE)
}

.policy_variable_values <- function(variable) {
  if (!is.null(variable$step)) {
    values <- seq(variable$lower, variable$upper, by = variable$step)
    if (!length(values) || tail(values, 1L) < variable$upper) values <- c(values, variable$upper)
  } else values <- seq(variable$lower, variable$upper, length.out = 5L)
  if (identical(variable$type, "integer")) values <- unique(round(values))
  pmin(variable$upper, pmax(variable$lower, values))
}

.policy_generate_candidates <- function(spec) {
  if (identical(spec$method, "grid")) {
    values <- lapply(spec$variables, .policy_variable_values)
    candidates <- do.call(expand.grid, c(values, KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE))
    names(candidates) <- names(spec$variables)
    if (nrow(candidates) > spec$max_evaluations) {
      keep <- unique(round(seq(1, nrow(candidates), length.out = spec$max_evaluations)))
      candidates <- candidates[keep, , drop = FALSE]
    }
  } else {
    set.seed(spec$seed)
    candidates <- as.data.frame(lapply(spec$variables, function(variable) {
      values <- stats::runif(spec$max_evaluations, variable$lower, variable$upper)
      if (identical(variable$type, "integer")) round(values) else values
    }), stringsAsFactors = FALSE)
  }
  rownames(candidates) <- NULL
  candidates
}

.policy_constraint_evaluation <- function(constraint, metrics) {
  value <- metrics[[constraint$metric]]
  if (is.null(value) || !is.numeric(value) || length(value) != 1L || !is.finite(value)) {
    return(list(satisfied = FALSE, violation = Inf))
  }
  tol <- constraint$tolerance
  if (identical(constraint$operator, "<=")) {
    violation <- max(0, value - constraint$value - tol)
  } else if (identical(constraint$operator, ">=")) {
    violation <- max(0, constraint$value - value - tol)
  } else if (identical(constraint$operator, "==")) {
    violation <- max(0, abs(value - constraint$value) - tol)
  } else {
    violation <- max(0, constraint$lower - value - tol, value - constraint$upper - tol)
  }
  list(satisfied = isTRUE(violation <= 0), violation = violation)
}

.policy_objective_loss <- function(values, objective) {
  if (identical(objective$direction, "minimize")) values
  else if (identical(objective$direction, "maximize")) -values
  else abs(values - objective$target)
}

.policy_pareto_flags <- function(losses, eligible) {
  n <- nrow(losses); result <- rep(FALSE, n)
  idx <- which(eligible)
  for (i in idx) {
    dominated <- FALSE
    for (j in idx[idx != i]) {
      if (all(losses[j, ] <= losses[i, ], na.rm = FALSE) && any(losses[j, ] < losses[i, ], na.rm = FALSE)) {
        dominated <- TRUE; break
      }
    }
    result[[i]] <- !dominated
  }
  result
}

#' Evaluate policy candidates
#'
#' @param spec Optimization specification.
#' @param evaluator Function receiving a named decision list and returning named numeric metrics or `list(metrics=...)`.
#' @param candidates Optional candidate data frame.
#' @return Candidate table with feasibility, objective score, and Pareto status.
#' @export
evaluate_policy_candidates <- function(spec, evaluator, candidates = NULL) {
  validate_policy_optimization_spec(spec)
  if (!is.function(evaluator)) stop("`evaluator` must be a function.", call. = FALSE)
  if (is.null(candidates)) candidates <- .policy_generate_candidates(spec)
  if (!is.data.frame(candidates) || !nrow(candidates)) stop("`candidates` must be a non-empty data frame.", call. = FALSE)
  missing <- setdiff(names(spec$variables), names(candidates)); if (length(missing)) stop("Candidate table is missing variables: ", paste(missing, collapse = ", "), call. = FALSE)
  candidates <- candidates[, names(spec$variables), drop = FALSE]
  for (id in names(spec$variables)) {
    variable <- spec$variables[[id]]; values <- candidates[[id]]
    if (!is.numeric(values) || any(!is.finite(values)) || any(values < variable$lower | values > variable$upper)) stop("Candidate values violate variable bounds: ", id, call. = FALSE)
    if (identical(variable$type, "integer") && any(values != round(values))) stop("Integer candidate values must be whole numbers: ", id, call. = FALSE)
  }
  metric_names <- unique(c(vapply(spec$objectives, `[[`, character(1), "metric"), if (length(spec$constraints)) vapply(spec$constraints, `[[`, character(1), "metric") else character()))
  evaluated <- vector("list", nrow(candidates))
  errors <- character(nrow(candidates)); status <- rep("success", nrow(candidates))
  for (i in seq_len(nrow(candidates))) {
    decision <- as.list(candidates[i, , drop = FALSE])
    value <- tryCatch(evaluator(decision), error = function(error) error)
    if (inherits(value, "error")) {
      evaluated[[i]] <- list(); errors[[i]] <- conditionMessage(value); status[[i]] <- "failed"
    } else {
      if (is.list(value) && !is.null(value$metrics)) value <- value$metrics
      if (is.atomic(value)) value <- as.list(value)
      if (!is.list(value) || is.null(names(value))) stop("Evaluator results must be named numeric metrics.", call. = FALSE)
      evaluated[[i]] <- value
    }
  }
  metrics <- as.data.frame(stats::setNames(lapply(metric_names, function(metric) vapply(evaluated, function(row) {
    value <- row[[metric]]; if (is.null(value) || !is.numeric(value) || length(value) != 1L || !is.finite(value)) NA_real_ else as.numeric(value)
  }, numeric(1))), metric_names), stringsAsFactors = FALSE)
  hard_feasible <- rep(TRUE, nrow(candidates)); violation_count <- integer(nrow(candidates)); violation_total <- numeric(nrow(candidates))
  for (constraint in spec$constraints) {
    checks <- lapply(evaluated, function(row) .policy_constraint_evaluation(constraint, row))
    satisfied <- vapply(checks, `[[`, logical(1), "satisfied"); violation <- vapply(checks, `[[`, numeric(1), "violation")
    violation_count <- violation_count + as.integer(!satisfied); violation_total <- violation_total + violation
    if (isTRUE(constraint$hard)) hard_feasible <- hard_feasible & satisfied
  }
  objective_losses <- matrix(NA_real_, nrow = nrow(candidates), ncol = length(spec$objectives), dimnames = list(NULL, names(spec$objectives)))
  normalized <- objective_losses
  for (j in seq_along(spec$objectives)) {
    objective <- spec$objectives[[j]]; loss <- .policy_objective_loss(metrics[[objective$metric]], objective); objective_losses[, j] <- loss
    finite <- is.finite(loss)
    if (any(finite)) {
      span <- diff(range(loss[finite])); normalized[finite, j] <- if (span <= .Machine$double.eps) 0 else (loss[finite] - min(loss[finite])) / span
    }
  }
  weights <- vapply(spec$objectives, `[[`, numeric(1), "weight")
  objective_score <- rowSums(sweep(normalized, 2L, weights, `*`), na.rm = FALSE) / sum(weights)
  eligible <- status == "success" & hard_feasible & apply(is.finite(objective_losses), 1L, all)
  objective_score[!eligible] <- Inf
  pareto <- .policy_pareto_flags(objective_losses, eligible)
  result <- cbind(data.frame(candidate_id = paste0("candidate-", seq_len(nrow(candidates))), candidates, stringsAsFactors = FALSE), metrics)
  result$feasible <- eligible; result$constraint_violations <- violation_count; result$total_violation <- violation_total
  result$objective_score <- objective_score; result$pareto <- pareto; result$evaluation_status <- status; result$error <- errors
  result
}

#' Optimize policy choices
#'
#' @param spec Optimization specification.
#' @param evaluator Policy evaluator.
#' @param candidates Optional candidate table.
#' @return A `catalyst_policy_optimization` result.
#' @export
optimize_policy <- function(spec, evaluator, candidates = NULL) {
  table <- evaluate_policy_candidates(spec, evaluator, candidates)
  feasible <- which(table$feasible & is.finite(table$objective_score))
  selected <- if (length(feasible)) feasible[[which.min(table$objective_score[feasible])]] else NA_integer_
  variable_ids <- names(spec$variables)
  objective_metric_ids <- vapply(spec$objectives, `[[`, character(1), "metric")
  constraint_metric_ids <- if (length(spec$constraints)) {
    vapply(spec$constraints, `[[`, character(1), "metric")
  } else {
    character()
  }
  metric_ids <- unique(c(objective_metric_ids, constraint_metric_ids))
  recommendation <- if (is.na(selected)) NULL else list(
    candidate_id = table$candidate_id[[selected]], decisions = as.list(table[selected, variable_ids, drop = FALSE]),
    metrics = as.list(table[selected, metric_ids, drop = FALSE]), objective_score = table$objective_score[[selected]],
    constraint_violations = table$constraint_violations[[selected]], review_status = "unreviewed"
  )
  result <- structure(list(
    schema_version = .policy_contract_version(), analysis_type = "policy_optimization",
    id = spec$id, title = spec$title, spec = spec, candidates = table,
    recommendation = recommendation, pareto_frontier = table[table$pareto, , drop = FALSE],
    feasible_region = NULL, metadata = list(package_version = .catalyst_package_version(), created_at = format(Sys.time(), tz = "UTC", usetz = TRUE)),
    boundary = list(human_review_required = TRUE, recommendation_not_authorization = TRUE, evaluator_validity_not_established = TRUE)
  ), class = c("catalyst_policy_optimization", "list"))
  result$feasible_region <- policy_feasible_region(result)
  result
}

#' Return the Pareto frontier
#' @param x Policy optimization result.
#' @return Candidate data frame.
#' @export
policy_pareto_frontier <- function(x) {
  if (!inherits(x, "catalyst_policy_optimization")) stop("`x` must be a policy optimization result.", call. = FALSE)
  x$candidates[x$candidates$pareto, , drop = FALSE]
}

#' Summarize the feasible policy region
#' @param x Policy optimization result.
#' @return Feasibility summary and variable bounds.
#' @export
policy_feasible_region <- function(x) {
  if (!inherits(x, "catalyst_policy_optimization")) stop("`x` must be a policy optimization result.", call. = FALSE)
  feasible <- x$candidates[x$candidates$feasible, , drop = FALSE]
  variable_ids <- names(x$spec$variables)
  bounds <- lapply(variable_ids, function(id) list(
    variable = id,
    minimum = if (nrow(feasible)) min(feasible[[id]]) else NA_real_,
    maximum = if (nrow(feasible)) max(feasible[[id]]) else NA_real_
  ))
  names(bounds) <- variable_ids
  list(total_candidates = nrow(x$candidates), feasible_candidates = nrow(feasible),
       feasible_share = nrow(feasible) / nrow(x$candidates), variable_bounds = bounds)
}

.policy_set_nested <- function(record, path, value) {
  keys <- strsplit(path, "[$.]", perl = TRUE)[[1L]]
  keys <- keys[nzchar(keys)]
  if (!length(keys)) stop("Decision-variable target is empty.", call. = FALSE)
  set_value <- function(node, remaining) {
    key <- remaining[[1L]]
    if (length(remaining) == 1L) { node[[key]] <- value; return(node) }
    if (is.null(node[[key]]) || !is.list(node[[key]])) stop("Decision-variable target does not exist: ", path, call. = FALSE)
    node[[key]] <- set_value(node[[key]], remaining[-1L]); node
  }
  set_value(record, keys)
}

#' Create a target-seeking scenario
#'
#' @param scenario Canonical scenario template.
#' @param spec Optimization specification whose variable targets map into the scenario.
#' @param evaluator Policy evaluator.
#' @param candidates Optional candidate table.
#' @param id New scenario identifier.
#' @param title New scenario title.
#' @return Optimization result plus an optimized canonical scenario.
#' @export
target_seeking_scenario <- function(scenario, spec, evaluator, candidates = NULL, id = NULL, title = NULL) {
  validate_catalyst_scenario(scenario); validate_policy_optimization_spec(spec)
  optimization <- optimize_policy(spec, evaluator, candidates)
  if (is.null(optimization$recommendation)) stop("No feasible target-seeking scenario was found.", call. = FALSE)
  optimized <- unclass(scenario)
  if (is.null(optimized$provenance) || !is.list(optimized$provenance)) optimized$provenance <- list()
  decisions <- optimization$recommendation$decisions
  for (variable_id in names(spec$variables)) optimized <- .policy_set_nested(optimized, spec$variables[[variable_id]]$target, decisions[[variable_id]])
  if (!is.null(id)) { .policy_identifier(id); optimized$id <- id }
  if (!is.null(title)) { .assert_single_string(title, "title"); optimized$title <- title }
  optimized$role <- "intervention"
  optimized$provenance$optimization <- list(analysis_id = spec$id, candidate_id = optimization$recommendation$candidate_id, objective_score = optimization$recommendation$objective_score)
  optimized <- as_catalyst_scenario(optimized); validate_catalyst_scenario(optimized)
  structure(list(
    schema_version = .policy_contract_version(), analysis_type = "target_seeking_scenario",
    optimization = optimization, scenario = optimized,
    boundary = list(human_review_required = TRUE, optimized_scenario_not_policy_authorization = TRUE)
  ), class = c("catalyst_target_seeking_scenario", "list"))
}

#' Cost-effectiveness analysis
#'
#' @param data Option-level data frame.
#' @param option_col,cost_col,effect_col Column names.
#' @param baseline_effect Baseline effect for the first increment.
#' @return Incremental cost-effectiveness table.
#' @export
cost_effectiveness_analysis <- function(data, option_col = "option", cost_col = "cost", effect_col = "effect", baseline_effect = 0) {
  if (!is.data.frame(data) || !nrow(data)) stop("`data` must be a non-empty data frame.", call. = FALSE)
  required <- c(option_col, cost_col, effect_col); missing <- setdiff(required, names(data)); if (length(missing)) stop("Cost-effectiveness data is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!is.numeric(data[[cost_col]]) || !is.numeric(data[[effect_col]]) || any(!is.finite(data[[cost_col]])) || any(!is.finite(data[[effect_col]]))) stop("Cost and effect columns must be finite numeric values.", call. = FALSE)
  .assert_scalar_number(baseline_effect, "baseline_effect")
  result <- data[order(data[[effect_col]], data[[cost_col]]), , drop = FALSE]
  dominated <- logical(nrow(result))
  for (i in seq_len(nrow(result))) for (j in seq_len(nrow(result))) if (i != j && result[[cost_col]][j] <= result[[cost_col]][i] && result[[effect_col]][j] >= result[[effect_col]][i] && (result[[cost_col]][j] < result[[cost_col]][i] || result[[effect_col]][j] > result[[effect_col]][i])) dominated[[i]] <- TRUE
  result$dominated <- dominated
  result$incremental_cost <- c(result[[cost_col]][1L], diff(result[[cost_col]]))
  result$incremental_effect <- c(result[[effect_col]][1L] - baseline_effect, diff(result[[effect_col]]))
  result$incremental_cost_effectiveness <- ifelse(result$incremental_effect > 0, result$incremental_cost / result$incremental_effect, NA_real_)
  rownames(result) <- NULL
  structure(result, class = c("catalyst_cost_effectiveness", "data.frame"))
}

#' Marginal abatement curve
#'
#' @param data Option-level data frame.
#' @param option_col,cost_col,abatement_col Column names.
#' @return Marginal-abatement table ordered by cost per unit.
#' @export
marginal_abatement_curve <- function(data, option_col = "option", cost_col = "cost", abatement_col = "abatement") {
  if (!is.data.frame(data) || !nrow(data)) stop("`data` must be a non-empty data frame.", call. = FALSE)
  required <- c(option_col, cost_col, abatement_col); missing <- setdiff(required, names(data)); if (length(missing)) stop("Abatement data is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!is.numeric(data[[cost_col]]) || !is.numeric(data[[abatement_col]]) || any(!is.finite(data[[cost_col]])) || any(!is.finite(data[[abatement_col]])) || any(data[[abatement_col]] <= 0)) stop("Costs must be finite and abatement must be positive.", call. = FALSE)
  result <- data
  result$cost_per_unit <- result[[cost_col]] / result[[abatement_col]]
  result <- result[order(result$cost_per_unit, -result[[abatement_col]]), , drop = FALSE]
  result$cumulative_abatement <- cumsum(result[[abatement_col]])
  rownames(result) <- NULL
  structure(result, class = c("catalyst_marginal_abatement", "data.frame"))
}

#' Define an adaptive trigger
#'
#' @param id,label Stable identifier and label.
#' @param metric Evidence metric.
#' @param operator Trigger operator.
#' @param threshold Trigger threshold.
#' @param action Action recommendation.
#' @param review_period Review interval.
#' @param description Method note.
#' @return Adaptive trigger record.
#' @export
adaptive_trigger <- function(id, label, metric, operator = c(">", ">=", "<", "<=", "=="), threshold, action, review_period = 1, description = "") {
  operator <- match.arg(operator); .policy_identifier(id); .assert_single_string(label, "label"); .assert_single_string(metric, "metric")
  .assert_scalar_number(threshold, "threshold"); .assert_scalar_number(review_period, "review_period", lower = .Machine$double.eps)
  if (!is.list(action) && !(is.character(action) && length(action) == 1L)) stop("`action` must be a list or single string.", call. = FALSE)
  .assert_single_string(description, "description", allow_empty = TRUE)
  structure(list(id = id, label = label, metric = metric, operator = operator, threshold = threshold,
                 action = .safe_json_value(action), review_period = review_period, description = description),
            class = c("catalyst_adaptive_trigger", "list"))
}

.policy_triggered <- function(value, operator, threshold, tolerance = 1e-8) {
  if (operator == ">") value > threshold + tolerance else if (operator == ">=") value >= threshold - tolerance else if (operator == "<") value < threshold - tolerance else if (operator == "<=") value <= threshold + tolerance else abs(value - threshold) <= tolerance
}

#' Define a policy stage
#'
#' @param id,label Stable identifier and label.
#' @param start,end Stage boundaries.
#' @param actions Planned actions.
#' @param triggers Adaptive triggers.
#' @param decision_gate Whether human review is required at the stage boundary.
#' @return A policy-stage record.
#' @export
policy_stage <- function(id, label, start, end, actions = list(), triggers = list(), decision_gate = TRUE) {
  .policy_identifier(id); .assert_single_string(label, "label"); .assert_scalar_number(start, "start"); .assert_scalar_number(end, "end")
  if (start > end) stop("Policy-stage start cannot exceed end.", call. = FALSE)
  if (!is.list(actions) || !is.list(triggers)) stop("Stage actions and triggers must be lists.", call. = FALSE)
  .assert_flag(decision_gate, "decision_gate")
  if (length(triggers)) {
    ids <- vapply(triggers, function(trigger) { if (!inherits(trigger, "catalyst_adaptive_trigger") && !is.list(trigger)) stop("Invalid adaptive trigger.", call. = FALSE); trigger$id }, character(1))
    if (anyDuplicated(ids)) stop("Policy stage cannot contain duplicate trigger identifiers.", call. = FALSE)
    names(triggers) <- ids
  }
  structure(list(id = id, label = label, start = start, end = end, actions = .safe_json_value(actions), triggers = triggers, decision_gate = decision_gate), class = c("catalyst_policy_stage", "list"))
}

#' Create an adaptive policy pathway
#'
#' @param id,title Stable identifier and title.
#' @param stages Ordered policy stages.
#' @param description Pathway purpose.
#' @param objectives Optional objective records.
#' @param metadata Additional metadata.
#' @return A `catalyst_policy_pathway`.
#' @export
policy_pathway <- function(id, title, stages, description = "", objectives = list(), metadata = list()) {
  .policy_identifier(id); .assert_single_string(title, "title"); .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.list(stages) || !length(stages)) stop("`stages` must be a non-empty list.", call. = FALSE)
  ids <- vapply(stages, function(stage) { if (!inherits(stage, "catalyst_policy_stage") && !is.list(stage)) stop("Invalid policy stage.", call. = FALSE); stage$id }, character(1))
  if (anyDuplicated(ids)) stop("Policy pathway cannot contain duplicate stage identifiers.", call. = FALSE); names(stages) <- ids
  if (length(objectives)) objectives <- .policy_named_records(objectives, "objectives", .validate_policy_objective)
  result <- structure(list(
    schema_version = .policy_contract_version(), pathway_type = "adaptive_policy_pathway",
    id = id, title = title, description = description, stages = stages, objectives = objectives,
    metadata = utils::modifyList(list(created_at = format(Sys.time(), tz = "UTC", usetz = TRUE), status = "draft"), metadata),
    boundary = list(human_decision_gates_required = TRUE, triggers_are_review_prompts = TRUE)
  ), class = c("catalyst_policy_pathway", "list"))
  validate_policy_pathway(result); result
}

#' Validate a policy pathway
#' @param pathway Policy pathway.
#' @return Invisibly returns `TRUE`.
#' @export
validate_policy_pathway <- function(pathway) {
  if (!is.list(pathway)) stop("`pathway` must be a list.", call. = FALSE)
  required <- c("schema_version", "pathway_type", "id", "title", "stages", "objectives", "metadata", "boundary")
  missing <- setdiff(required, names(pathway)); if (length(missing)) stop("Policy pathway is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(pathway$schema_version, .policy_contract_version()) || !identical(pathway$pathway_type, "adaptive_policy_pathway")) stop("Unsupported policy pathway contract.", call. = FALSE)
  .policy_identifier(pathway$id, "pathway$id"); .assert_single_string(pathway$title, "pathway$title")
  starts <- vapply(pathway$stages, `[[`, numeric(1), "start"); ends <- vapply(pathway$stages, `[[`, numeric(1), "end")
  if (is.unsorted(starts, strictly = FALSE)) stop("Policy stages must be ordered by start.", call. = FALSE)
  if (length(starts) > 1L && any(starts[-1L] < ends[-length(ends)])) stop("Policy stages cannot overlap.", call. = FALSE)
  invisible(TRUE)
}

#' Return policy sequence records
#' @param pathway Policy pathway.
#' @return Stage-level data frame.
#' @export
policy_sequence <- function(pathway) {
  validate_policy_pathway(pathway)
  do.call(rbind, lapply(pathway$stages, function(stage) data.frame(
    stage_id = stage$id, label = stage$label, start = stage$start, end = stage$end,
    actions = length(stage$actions), triggers = length(stage$triggers), decision_gate = stage$decision_gate,
    stringsAsFactors = FALSE
  )))
}

#' Evaluate adaptive pathway triggers
#'
#' @param pathway Policy pathway.
#' @param evidence Time-indexed evidence data frame.
#' @param time_col Time column name.
#' @return Trigger status and action recommendations.
#' @export
evaluate_policy_pathway <- function(pathway, evidence, time_col = "time") {
  validate_policy_pathway(pathway)
  if (!is.data.frame(evidence) || !nrow(evidence) || !time_col %in% names(evidence) || !is.numeric(evidence[[time_col]])) stop("`evidence` must contain a numeric time column.", call. = FALSE)
  records <- list(); actions <- list(); k <- 0L
  for (stage in pathway$stages) {
    rows <- which(evidence[[time_col]] >= stage$start & evidence[[time_col]] <= stage$end)
    latest <- if (length(rows)) rows[[which.max(evidence[[time_col]][rows])]] else NA_integer_
    for (trigger in stage$triggers) {
      k <- k + 1L
      value <- if (!is.na(latest) && trigger$metric %in% names(evidence)) evidence[[trigger$metric]][[latest]] else NA_real_
      finite_value <- is.numeric(value) && length(value) == 1L && is.finite(value)
      triggered <- finite_value && .policy_triggered(value, trigger$operator, trigger$threshold)
      status <- if (!finite_value) "no_evidence" else if (triggered) "triggered_for_review" else "not_triggered"
      records[[k]] <- data.frame(stage_id = stage$id, trigger_id = trigger$id, metric = trigger$metric,
                                  observed_value = if (is.finite(value)) value else NA_real_, operator = trigger$operator,
                                  threshold = trigger$threshold, status = status, decision_gate = stage$decision_gate,
                                  stringsAsFactors = FALSE)
      if (triggered) actions[[length(actions) + 1L]] <- list(stage_id = stage$id, trigger_id = trigger$id, action = trigger$action, review_required = TRUE)
    }
  }
  trigger_table <- if (length(records)) do.call(rbind, records) else data.frame(stage_id=character(),trigger_id=character(),metric=character(),observed_value=numeric(),operator=character(),threshold=numeric(),status=character(),decision_gate=logical(),stringsAsFactors=FALSE)
  structure(list(
    schema_version = .policy_contract_version(), analysis_type = "adaptive_policy_pathway_evaluation",
    pathway_id = pathway$id, evaluated_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
    trigger_status = trigger_table, recommended_actions = actions,
    boundary = list(human_review_required = TRUE, triggers_do_not_execute_actions = TRUE)
  ), class = c("catalyst_policy_pathway_evaluation", "list"))
}

#' Robust pathway analysis
#'
#' @param pathways Policy pathways.
#' @param performance Data frame with `pathway_id`, `scenario_id`, and objective metrics.
#' @param objectives Objective records.
#' @param regret_tolerance Maximum acceptable worst-case normalized regret.
#' @return Scenario scores and pathway robustness summary.
#' @export
robust_pathway_analysis <- function(pathways, performance, objectives, regret_tolerance = 0.25) {
  if (!is.list(pathways) || !length(pathways)) stop("`pathways` must be a non-empty list.", call. = FALSE)
  pathway_ids <- vapply(pathways, function(pathway) { validate_policy_pathway(pathway); pathway$id }, character(1))
  if (anyDuplicated(pathway_ids)) stop("Pathway identifiers must be unique.", call. = FALSE)
  objectives <- .policy_named_records(objectives, "objectives", .validate_policy_objective)
  if (!is.data.frame(performance) || !all(c("pathway_id", "scenario_id") %in% names(performance))) stop("Performance data requires pathway_id and scenario_id.", call. = FALSE)
  if (length(setdiff(unique(performance$pathway_id), pathway_ids))) stop("Performance data references an unknown pathway.", call. = FALSE)
  metrics <- vapply(objectives, `[[`, character(1), "metric"); missing <- setdiff(metrics, names(performance)); if (length(missing)) stop("Performance data is missing objective metrics: ", paste(missing, collapse = ", "), call. = FALSE)
  for (metric in metrics) if (!is.numeric(performance[[metric]]) || any(!is.finite(performance[[metric]]))) stop("Performance objective metrics must be finite numeric values: ", metric, call. = FALSE)
  .assert_scalar_number(regret_tolerance, "regret_tolerance", lower = 0)
  scores <- rep(0, nrow(performance)); weights <- vapply(objectives, `[[`, numeric(1), "weight")
  for (scenario in unique(performance$scenario_id)) {
    idx <- which(performance$scenario_id == scenario)
    for (objective in objectives) {
      loss <- .policy_objective_loss(performance[[objective$metric]][idx], objective)
      span <- diff(range(loss)); normalized <- if (span <= .Machine$double.eps) rep(0, length(loss)) else (loss - min(loss)) / span
      scores[idx] <- scores[idx] + objective$weight * normalized / sum(weights)
    }
  }
  scored <- performance; scored$normalized_loss <- scores
  scored$regret <- stats::ave(scored$normalized_loss, scored$scenario_id, FUN = function(x) x - min(x))
  summary <- do.call(rbind, lapply(split(scored, scored$pathway_id), function(rows) data.frame(
    pathway_id = rows$pathway_id[[1L]], mean_normalized_loss = mean(rows$normalized_loss),
    maximum_regret = max(rows$regret), robust = max(rows$regret) <= regret_tolerance,
    scenarios = length(unique(rows$scenario_id)), stringsAsFactors = FALSE
  )))
  summary$rank <- rank(summary$maximum_regret, ties.method = "min")
  summary <- summary[order(summary$rank, summary$mean_normalized_loss), , drop = FALSE]; rownames(summary) <- NULL
  structure(list(
    schema_version = .policy_contract_version(), analysis_type = "robust_policy_pathway_analysis",
    performance = scored, summary = summary, regret_tolerance = regret_tolerance,
    boundary = list(human_review_required = TRUE, robustness_not_prediction = TRUE)
  ), class = c("catalyst_robust_pathway_analysis", "list"))
}

#' Assemble optimization and pathway evidence
#'
#' @param optimization Policy optimization result.
#' @param pathway Optional policy pathway.
#' @param pathway_evaluation Optional pathway evaluation.
#' @param robust_analysis Optional robust pathway analysis.
#' @param cost_effectiveness Optional cost-effectiveness table.
#' @param marginal_abatement Optional marginal-abatement table.
#' @return A `catalyst_policy_pathway_analysis`.
#' @export
policy_pathway_analysis <- function(optimization, pathway = NULL, pathway_evaluation = NULL,
                                    robust_analysis = NULL, cost_effectiveness = NULL, marginal_abatement = NULL) {
  if (!inherits(optimization, "catalyst_policy_optimization")) stop("`optimization` must be a policy optimization result.", call. = FALSE)
  if (!is.null(pathway)) validate_policy_pathway(pathway)
  structure(list(
    schema_version = .policy_contract_version(), analysis_type = "optimization_and_policy_pathway_analysis",
    id = optimization$id, title = optimization$title, optimization = optimization,
    pathway = pathway, pathway_evaluation = pathway_evaluation, robust_analysis = robust_analysis,
    cost_effectiveness = cost_effectiveness, marginal_abatement = marginal_abatement,
    summary = policy_optimization_summary(optimization),
    boundary = list(human_review_required = TRUE, no_autonomous_decision = TRUE, no_autonomous_execution = TRUE)
  ), class = c("catalyst_policy_pathway_analysis", "list"))
}

#' Summarize policy optimization
#' @param x Optimization result.
#' @return Summary list.
#' @export
policy_optimization_summary <- function(x) {
  if (!inherits(x, "catalyst_policy_optimization")) stop("`x` must be a policy optimization result.", call. = FALSE)
  list(id = x$id, title = x$title, candidates = nrow(x$candidates), feasible = sum(x$candidates$feasible),
       pareto = sum(x$candidates$pareto), recommendation_available = !is.null(x$recommendation),
       selected_candidate_id = if (is.null(x$recommendation)) NULL else x$recommendation$candidate_id,
       human_review_required = TRUE)
}

#' Plot a policy Pareto frontier
#' @param x Optimization result.
#' @param x_metric,y_metric Objective metric names.
#' @return A ggplot object.
#' @export
plot_policy_pareto <- function(x, x_metric, y_metric) {
  if (!inherits(x, "catalyst_policy_optimization")) stop("`x` must be a policy optimization result.", call. = FALSE)
  .assert_single_string(x_metric, "x_metric"); .assert_single_string(y_metric, "y_metric")
  if (!all(c(x_metric, y_metric) %in% names(x$candidates))) stop("Requested Pareto metrics are unavailable.", call. = FALSE)
  ggplot2::ggplot(x$candidates, ggplot2::aes_string(x = x_metric, y = y_metric, shape = "feasible", alpha = "pareto")) +
    ggplot2::geom_point(size = 3) + ggplot2::labs(title = x$title, subtitle = "Feasible candidates and non-dominated frontier") + theme_catalyst()
}

#' Plot a marginal-abatement curve
#' @param x Marginal-abatement table.
#' @param option_col Option column.
#' @return A ggplot object.
#' @export
plot_marginal_abatement <- function(x, option_col = "option") {
  if (!inherits(x, "catalyst_marginal_abatement") && !is.data.frame(x)) stop("`x` must be a marginal-abatement table.", call. = FALSE)
  if (!option_col %in% names(x)) stop("Option column is unavailable.", call. = FALSE)
  ggplot2::ggplot(x, ggplot2::aes_string(x = option_col, y = "cost_per_unit")) +
    ggplot2::geom_col() + ggplot2::labs(x = NULL, y = "Cost per unit", title = "Marginal abatement curve") + theme_catalyst()
}

#' Plot an adaptive policy pathway
#' @param pathway Policy pathway.
#' @return A ggplot object.
#' @export
plot_policy_pathway <- function(pathway) {
  sequence <- policy_sequence(pathway)
  sequence$y <- rev(seq_len(nrow(sequence)))
  ggplot2::ggplot(sequence) + ggplot2::geom_segment(ggplot2::aes_string(x = "start", xend = "end", y = "y", yend = "y"), linewidth = 5) +
    ggplot2::geom_point(ggplot2::aes_string(x = "end", y = "y", shape = "decision_gate"), size = 3) +
    ggplot2::scale_y_continuous(breaks = sequence$y, labels = sequence$label) +
    ggplot2::labs(x = "Time", y = NULL, title = pathway$title, subtitle = "Stages and human decision gates") + theme_catalyst()
}

#' @export
print.catalyst_policy_optimization <- function(x, ...) {
  summary <- policy_optimization_summary(x)
  cat(sprintf("<catalyst_policy_optimization %s>\n", x$id))
  cat(sprintf("  candidates: %d | feasible: %d | Pareto: %d\n", summary$candidates, summary$feasible, summary$pareto))
  cat(sprintf("  recommendation: %s | human review required\n", if (summary$recommendation_available) summary$selected_candidate_id else "none"))
  invisible(x)
}

#' @export
print.catalyst_policy_pathway <- function(x, ...) {
  cat(sprintf("<catalyst_policy_pathway %s>\n", x$id)); cat(sprintf("  %s\n", x$title)); cat(sprintf("  stages: %d | human decision gates required\n", length(x$stages))); invisible(x)
}
