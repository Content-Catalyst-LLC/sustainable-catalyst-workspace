.validate_boundary_id <- function(id) {
  .assert_single_string(id, "id")
  if (!grepl("^[a-z][a-z0-9._-]*$", id)) stop("Boundary `id` must begin with a lowercase letter and use letters, digits, periods, underscores, or hyphens.", call. = FALSE)
  invisible(id)
}

#' Define a sustainability boundary
#'
#' @param id Stable boundary identifier.
#' @param title Human-readable title.
#' @param indicator Indicator identifier expected in the assessed data.
#' @param unit Expected unit.
#' @param direction One of `at_or_below`, `at_or_above`, or `inside_range`.
#' @param lower Optional lower bound.
#' @param upper Optional upper bound.
#' @param warning_margin Fraction of the admissible range used for warning status.
#' @param source Methodology or evidence source record.
#' @param metadata Additional metadata.
#' @return A `catalyst_boundary_definition`.
#' @export
boundary_definition <- function(
  id,
  title,
  indicator,
  unit,
  direction = c("at_or_below", "at_or_above", "inside_range"),
  lower = NULL,
  upper = NULL,
  warning_margin = 0.1,
  source = list(),
  metadata = list()
) {
  .validate_boundary_id(id)
  .assert_single_string(title, "title")
  .assert_single_string(indicator, "indicator")
  .assert_single_string(unit, "unit")
  direction <- match.arg(direction)
  .assert_scalar_number(warning_margin, "warning_margin", lower = 0, upper = 1)
  if (!is.null(lower)) .assert_scalar_number(lower, "lower")
  if (!is.null(upper)) .assert_scalar_number(upper, "upper")
  if (direction == "at_or_below" && is.null(upper)) stop("`upper` is required for an at-or-below boundary.", call. = FALSE)
  if (direction == "at_or_above" && is.null(lower)) stop("`lower` is required for an at-or-above boundary.", call. = FALSE)
  if (direction == "inside_range" && (is.null(lower) || is.null(upper) || lower >= upper)) {
    stop("Inside-range boundaries require `lower < upper`.", call. = FALSE)
  }
  if (!is.list(source)) stop("`source` must be a list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = "1.0.0",
    id = id,
    title = title,
    indicator = indicator,
    unit = unit,
    direction = direction,
    lower = lower,
    upper = upper,
    warning_margin = warning_margin,
    source = source,
    metadata = utils::modifyList(list(created_at = .utc_now(), status = "active"), metadata)
  ), class = "catalyst_boundary_definition")
}

#' Validate a boundary definition
#'
#' @param boundary A `catalyst_boundary_definition`.
#' @return Invisibly returns TRUE when valid.
#' @export
validate_boundary_definition <- function(boundary) {
  if (!inherits(boundary, "catalyst_boundary_definition")) stop("`boundary` must be a boundary definition.", call. = FALSE)
  required <- c("schema_version", "id", "title", "indicator", "unit", "direction", "warning_margin")
  if (!all(required %in% names(boundary))) stop("Boundary definition is incomplete.", call. = FALSE)
  if (!boundary$direction %in% c("at_or_below", "at_or_above", "inside_range")) stop("Boundary direction is invalid.", call. = FALSE)
  invisible(TRUE)
}

.boundary_status_value <- function(value, boundary) {
  if (!is.finite(value)) return(list(status = "unknown", distance = NA_real_, normalized_distance = NA_real_))
  warning_margin <- boundary$warning_margin
  if (boundary$direction == "at_or_below") {
    scale <- max(abs(boundary$upper), 1)
    distance <- boundary$upper - value
    status <- if (value > boundary$upper) "breached" else if (distance <= scale * warning_margin) "warning" else "within"
    return(list(status = status, distance = distance, normalized_distance = distance / scale))
  }
  if (boundary$direction == "at_or_above") {
    scale <- max(abs(boundary$lower), 1)
    distance <- value - boundary$lower
    status <- if (value < boundary$lower) "breached" else if (distance <= scale * warning_margin) "warning" else "within"
    return(list(status = status, distance = distance, normalized_distance = distance / scale))
  }
  width <- boundary$upper - boundary$lower
  distance <- min(value - boundary$lower, boundary$upper - value)
  status <- if (value < boundary$lower || value > boundary$upper) "breached" else if (distance <= width * warning_margin) "warning" else "within"
  list(status = status, distance = distance, normalized_distance = distance / width)
}

#' Evaluate values against declared boundaries
#'
#' @param values Data frame containing indicator and value fields.
#' @param boundaries Boundary definition or list of definitions.
#' @param indicator_field Indicator-id field.
#' @param value_field Numeric value field.
#' @param unit_field Optional unit field.
#' @param identity_fields Fields retained in the assessment output.
#' @return A `catalyst_boundary_assessment`.
#' @export
evaluate_boundaries <- function(
  values,
  boundaries,
  indicator_field = "indicator",
  value_field = "value",
  unit_field = "unit",
  identity_fields = character()
) {
  if (!is.data.frame(values)) stop("`values` must be a data frame.", call. = FALSE)
  for (field in c(indicator_field, value_field)) .validate_field_reference(field, values, field)
  if (!is.numeric(values[[value_field]])) stop("Boundary values must be numeric.", call. = FALSE)
  if (!is.null(unit_field)) .validate_field_reference(unit_field, values, "unit_field", allow_null = TRUE)
  if (!is.character(identity_fields) || any(!identity_fields %in% names(values)) || anyDuplicated(identity_fields)) {
    stop("`identity_fields` must contain unique value-table fields.", call. = FALSE)
  }
  if (inherits(boundaries, "catalyst_boundary_definition")) boundaries <- list(boundaries)
  if (!is.list(boundaries) || !length(boundaries)) stop("`boundaries` must contain at least one definition.", call. = FALSE)
  lapply(boundaries, validate_boundary_definition)
  ids <- vapply(boundaries, function(boundary) boundary$id, character(1))
  if (anyDuplicated(ids)) stop("Boundary identifiers must be unique.", call. = FALSE)

  rows <- list()
  for (boundary in boundaries) {
    matching <- which(as.character(values[[indicator_field]]) == boundary$indicator)
    if (!length(matching)) {
      row <- data.frame(indicator = boundary$indicator, value = NA_real_, unit = boundary$unit, stringsAsFactors = FALSE)
      result <- .boundary_status_value(NA_real_, boundary)
      row$boundary_id <- boundary$id
      row$boundary_title <- boundary$title
      row$direction <- boundary$direction
      row$lower <- if (is.null(boundary$lower)) NA_real_ else boundary$lower
      row$upper <- if (is.null(boundary$upper)) NA_real_ else boundary$upper
      row$status <- result$status
      row$distance <- result$distance
      row$normalized_distance <- result$normalized_distance
      row$message <- "No matching indicator value was supplied."
      rows[[length(rows) + 1L]] <- row
      next
    }
    for (index in matching) {
      row <- if (length(identity_fields)) values[index, identity_fields, drop = FALSE] else data.frame(scope = "assessment", stringsAsFactors = FALSE)
      observed_unit <- if (is.null(unit_field)) boundary$unit else as.character(values[[unit_field]][index])
      if (!identical(observed_unit, boundary$unit)) {
        result <- list(status = "unit_mismatch", distance = NA_real_, normalized_distance = NA_real_)
        message <- sprintf("Observed unit `%s` does not match boundary unit `%s`.", observed_unit, boundary$unit)
      } else {
        result <- .boundary_status_value(values[[value_field]][index], boundary)
        message <- switch(result$status,
          within = "Value is within the declared boundary.",
          warning = "Value is within the warning margin of the boundary.",
          breached = "Value breaches the declared boundary.",
          "Boundary status could not be determined."
        )
      }
      row$indicator <- boundary$indicator
      row$value <- values[[value_field]][index]
      row$unit <- observed_unit
      row$boundary_id <- boundary$id
      row$boundary_title <- boundary$title
      row$direction <- boundary$direction
      row$lower <- if (is.null(boundary$lower)) NA_real_ else boundary$lower
      row$upper <- if (is.null(boundary$upper)) NA_real_ else boundary$upper
      row$status <- result$status
      row$distance <- result$distance
      row$normalized_distance <- result$normalized_distance
      row$message <- message
      rows[[length(rows) + 1L]] <- row
    }
  }
  assessment <- .rbind_fill_indicator_values(rows)
  rownames(assessment) <- NULL
  structure(list(
    schema_version = "1.0.0",
    definitions = lapply(boundaries, unclass),
    assessment = assessment,
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      assessed_values = nrow(assessment),
      breached = sum(assessment$status == "breached"),
      warnings = sum(assessment$status == "warning")
    )
  ), class = "catalyst_boundary_assessment")
}

#' Summarize a boundary assessment
#'
#' @param assessment A `catalyst_boundary_assessment`.
#' @return Counts by boundary status.
#' @export
boundary_summary <- function(assessment) {
  if (!inherits(assessment, "catalyst_boundary_assessment")) stop("`assessment` must be a boundary assessment.", call. = FALSE)
  counts <- as.data.frame(table(assessment$assessment$status), stringsAsFactors = FALSE)
  names(counts) <- c("status", "count")
  counts
}

#' Plot sustainability boundary status
#'
#' @param assessment A boundary assessment.
#' @return A ggplot object.
#' @export
plot_boundary_status <- function(assessment) {
  if (!inherits(assessment, "catalyst_boundary_assessment")) stop("`assessment` must be a boundary assessment.", call. = FALSE)
  data <- assessment$assessment
  data$boundary_label <- paste(data$boundary_title, data$indicator, sep = ": ")
  ggplot2::ggplot(data, ggplot2::aes(x = stats::reorder(boundary_label, normalized_distance), y = normalized_distance, fill = status)) +
    ggplot2::geom_col() +
    ggplot2::coord_flip() +
    ggplot2::geom_hline(yintercept = 0, linewidth = 0.4) +
    ggplot2::labs(x = NULL, y = "Normalized distance from boundary", fill = "Status", title = "Boundary assessment") +
    theme_catalyst()
}

#' @export
print.catalyst_boundary_definition <- function(x, ...) {
  cat("<catalyst_boundary_definition>\n")
  cat("  id:        ", x$id, "\n", sep = "")
  cat("  indicator: ", x$indicator, "\n", sep = "")
  cat("  direction: ", x$direction, "\n", sep = "")
  invisible(x)
}

#' @export
print.catalyst_boundary_assessment <- function(x, ...) {
  cat("<catalyst_boundary_assessment>\n")
  cat("  assessed: ", nrow(x$assessment), "\n", sep = "")
  cat("  breached: ", sum(x$assessment$status == "breached"), "\n", sep = "")
  cat("  warnings: ", sum(x$assessment$status == "warning"), "\n", sep = "")
  invisible(x)
}
