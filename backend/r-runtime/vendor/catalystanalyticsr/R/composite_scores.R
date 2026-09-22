.catalyst_composite_schema_version <- function() "1.0.0"

#' Governed composite scores
#'
#' Define transparent component weights, directions, normalization ranges, and
#' missing-value treatment before calculating a composite score.
#'
#' @param id Stable score identifier.
#' @param title Human-readable title.
#' @param components Component column names.
#' @param weights Non-negative component weights.
#' @param directions `higher` or `lower` for each component.
#' @param lower_bounds Lower normalization bounds.
#' @param upper_bounds Upper normalization bounds.
#' @param missing_policy One of `error`, `renormalize`, or `zero`.
#' @param metadata Additional definition metadata.
#' @param definition A composite-score definition.
#' @param data Data frame containing component values.
#' @param entity_fields Optional identity columns retained in outputs.
#' @param time_field Optional time column retained in outputs.
#' @param weight_shift Proportional weight perturbation for sensitivity analysis.
#' @param result A calculated composite score.
#' @param x A composite-score object.
#' @param ... Additional method arguments.
#' @return A definition, score result, sensitivity table, or trace record.
#' @name composite_scores
NULL

#' @rdname composite_scores
#' @export
composite_score_definition <- function(
  id,
  title,
  components,
  weights,
  directions = "higher",
  lower_bounds = 0,
  upper_bounds = 1,
  missing_policy = c("error", "renormalize", "zero"),
  metadata = list()
) {
  .validate_dataset_id(id, "id")
  .assert_single_string(title, "title")
  if (!is.character(components) || !length(components) || any(!nzchar(components)) || anyDuplicated(components)) {
    stop("`components` must contain unique non-empty names.", call. = FALSE)
  }
  n <- length(components)
  weights <- .recycle_wealth_numeric(weights, n, "weights", lower = 0)
  if (sum(weights) <= 0) stop("At least one component weight must be positive.", call. = FALSE)
  directions <- rep(as.character(directions), length.out = n)
  if (length(directions) != n || any(!directions %in% c("higher", "lower"))) {
    stop("`directions` must contain `higher` or `lower` for each component.", call. = FALSE)
  }
  lower_bounds <- .recycle_wealth_numeric(lower_bounds, n, "lower_bounds")
  upper_bounds <- .recycle_wealth_numeric(upper_bounds, n, "upper_bounds")
  if (any(upper_bounds <= lower_bounds)) stop("Every upper bound must exceed its lower bound.", call. = FALSE)
  missing_policy <- match.arg(missing_policy)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .catalyst_composite_schema_version(),
    id = id,
    title = title,
    components = data.frame(
      component = components,
      weight = weights / sum(weights),
      direction = directions,
      lower_bound = lower_bounds,
      upper_bound = upper_bounds,
      stringsAsFactors = FALSE
    ),
    missing_policy = missing_policy,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      normalization = "bounded_min_max",
      score_range = c(0, 100)
    ), metadata)
  ), class = "catalyst_composite_definition")
}

#' @rdname composite_scores
#' @export
validate_composite_score_definition <- function(definition) {
  if (!inherits(definition, "catalyst_composite_definition")) stop("`definition` must be a composite-score definition.", call. = FALSE)
  if (!identical(definition$schema_version, .catalyst_composite_schema_version())) stop("Unsupported composite-score schema.", call. = FALSE)
  required <- c("component", "weight", "direction", "lower_bound", "upper_bound")
  if (!all(required %in% names(definition$components))) stop("Composite-score definition is incomplete.", call. = FALSE)
  if (abs(sum(definition$components$weight) - 1) > 1e-10) stop("Composite weights must sum to one.", call. = FALSE)
  if (any(definition$components$upper_bound <= definition$components$lower_bound)) stop("Composite normalization bounds are invalid.", call. = FALSE)
  invisible(TRUE)
}

.normalize_composite_values <- function(data, definition) {
  validate_composite_score_definition(definition)
  missing <- setdiff(definition$components$component, names(data))
  if (length(missing)) stop(sprintf("Missing composite component columns: %s", paste(missing, collapse = ", ")), call. = FALSE)
  values <- lapply(seq_len(nrow(definition$components)), function(i) {
    spec <- definition$components[i, , drop = FALSE]
    raw <- data[[spec$component]]
    if (!is.numeric(raw)) stop(sprintf("Composite component `%s` must be numeric.", spec$component), call. = FALSE)
    normalized <- (raw - spec$lower_bound) / (spec$upper_bound - spec$lower_bound)
    normalized <- pmin(1, pmax(0, normalized))
    if (spec$direction == "lower") normalized <- 1 - normalized
    normalized
  })
  names(values) <- definition$components$component
  as.data.frame(values, stringsAsFactors = FALSE)
}

.calculate_composite_with_weights <- function(normalized, weights, missing_policy) {
  matrix_values <- as.matrix(normalized)
  scores <- numeric(nrow(matrix_values))
  for (i in seq_len(nrow(matrix_values))) {
    row <- matrix_values[i, ]
    missing <- is.na(row)
    if (any(missing) && missing_policy == "error") stop("Composite components contain missing values.", call. = FALSE)
    if (missing_policy == "zero") row[missing] <- 0
    active_weights <- weights
    if (missing_policy == "renormalize") {
      active_weights[missing] <- 0
      if (sum(active_weights) <= 0) {
        scores[i] <- NA_real_
        next
      }
      active_weights <- active_weights / sum(active_weights)
      row[missing] <- 0
    }
    scores[i] <- 100 * sum(row * active_weights)
  }
  scores
}

#' @rdname composite_scores
#' @export
calculate_composite_score <- function(data, definition, entity_fields = character(), time_field = NULL) {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  validate_composite_score_definition(definition)
  identity_fields <- unique(c(entity_fields, time_field))
  if (length(identity_fields) && !all(identity_fields %in% names(data))) stop("Identity fields are missing from `data`.", call. = FALSE)
  normalized <- .normalize_composite_values(data, definition)
  weights <- definition$components$weight
  score <- .calculate_composite_with_weights(normalized, weights, definition$missing_policy)
  scores <- if (length(identity_fields)) data[identity_fields] else data.frame(row_id = seq_len(nrow(data)))
  scores$composite_score <- score
  contribution_rows <- do.call(rbind, lapply(seq_len(nrow(data)), function(i) {
    data.frame(
      row_id = i,
      component = definition$components$component,
      raw_value = vapply(definition$components$component, function(name) data[[name]][i], numeric(1)),
      normalized_score = as.numeric(unlist(normalized[i, , drop = FALSE], use.names = FALSE)),
      weight = weights,
      weighted_contribution = 100 * as.numeric(unlist(normalized[i, , drop = FALSE], use.names = FALSE)) * weights,
      direction = definition$components$direction,
      lower_bound = definition$components$lower_bound,
      upper_bound = definition$components$upper_bound,
      stringsAsFactors = FALSE
    )
  }))
  structure(list(
    schema_version = .catalyst_composite_schema_version(),
    definition = definition,
    scores = scores,
    components = contribution_rows,
    trace = list(
      formula = "100 * sum(normalized_component * normalized_weight)",
      normalization = "bounded_min_max",
      missing_policy = definition$missing_policy,
      component_count = nrow(definition$components)
    ),
    meta = list(package_version = .catalyst_package_version(), created_at = .utc_now())
  ), class = "catalyst_composite_score")
}

#' @rdname composite_scores
#' @export
composite_weight_sensitivity <- function(data, definition, weight_shift = 0.20) {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  validate_composite_score_definition(definition)
  .assert_scalar_number(weight_shift, "weight_shift", lower = 0, upper = 0.95)
  normalized <- .normalize_composite_values(data, definition)
  base_weights <- definition$components$weight
  base_score <- .calculate_composite_with_weights(normalized, base_weights, definition$missing_policy)
  rows <- list()
  counter <- 0L
  for (component_index in seq_along(base_weights)) {
    for (direction in c(-1, 1)) {
      changed <- base_weights
      target <- max(0, min(1, base_weights[component_index] * (1 + direction * weight_shift)))
      remaining_old <- sum(base_weights[-component_index])
      changed[component_index] <- target
      if (length(changed) == 1L) {
        changed[component_index] <- 1
      } else if (remaining_old > 0) {
        changed[-component_index] <- base_weights[-component_index] * (1 - target) / remaining_old
      }
      score <- .calculate_composite_with_weights(normalized, changed, definition$missing_policy)
      counter <- counter + 1L
      rows[[counter]] <- data.frame(
        component = definition$components$component[component_index],
        perturbation = if (direction < 0) "decrease" else "increase",
        original_weight = base_weights[component_index],
        perturbed_weight = changed[component_index],
        mean_absolute_score_change = mean(abs(score - base_score), na.rm = TRUE),
        max_absolute_score_change = max(abs(score - base_score), na.rm = TRUE),
        min_score = min(score, na.rm = TRUE),
        max_score = max(score, na.rm = TRUE),
        stringsAsFactors = FALSE
      )
    }
  }
  do.call(rbind, rows)
}

#' @rdname composite_scores
#' @export
composite_score_trace <- function(result) {
  if (!inherits(result, "catalyst_composite_score")) stop("`result` must be a composite score.", call. = FALSE)
  list(
    definition_id = result$definition$id,
    definition_title = result$definition$title,
    schema_version = result$schema_version,
    components = result$definition$components,
    missing_policy = result$definition$missing_policy,
    formula = result$trace$formula,
    normalization = result$trace$normalization
  )
}

#' @rdname composite_scores
#' @export
print.catalyst_composite_definition <- function(x, ...) {
  cat(sprintf("<catalyst_composite_definition %s>\n", x$id))
  cat(sprintf("  components: %d\n", nrow(x$components)))
  invisible(x)
}

#' @rdname composite_scores
#' @export
print.catalyst_composite_score <- function(x, ...) {
  cat(sprintf("<catalyst_composite_score %s>\n", x$definition$id))
  cat(sprintf("  rows: %d\n", nrow(x$scores)))
  invisible(x)
}
