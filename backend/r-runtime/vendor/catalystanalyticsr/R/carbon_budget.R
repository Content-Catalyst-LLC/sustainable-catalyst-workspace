#' Compute carbon-budget consumption by time integration
#'
#' @param trajectory_wide Data frame containing time and emissions columns.
#' @param budget Single non-negative total carbon budget.
#' @param emissions_col Name of the emissions column.
#' @param time_col Name of the time column.
#' @return A list with cumulative emissions, budget, remaining amount, and status.
#' @export
#' @examples
#' trajectory <- data.frame(t = 0:2, emissions = c(1, 2, 3))
#' carbon_budget(trajectory, budget = 10)
carbon_budget <- function(trajectory_wide, budget, emissions_col = "emissions", time_col = "t") {
  if (!is.data.frame(trajectory_wide)) stop("`trajectory_wide` must be a data.frame.", call. = FALSE)
  .assert_scalar_number(budget, "budget", lower = 0)
  .assert_single_string(emissions_col, "emissions_col")
  .assert_single_string(time_col, "time_col")
  if (!emissions_col %in% names(trajectory_wide)) stop(sprintf("Column `%s` not found.", emissions_col), call. = FALSE)
  if (!time_col %in% names(trajectory_wide)) stop(sprintf("Column `%s` not found.", time_col), call. = FALSE)

  time <- trajectory_wide[[time_col]]
  emissions <- trajectory_wide[[emissions_col]]
  if (!is.numeric(time) || !is.numeric(emissions)) stop("Time and emissions columns must be numeric.", call. = FALSE)
  if (length(time) < 2L) stop("Need at least two rows to integrate emissions.", call. = FALSE)
  if (length(time) != length(emissions) || any(!is.finite(time)) || any(!is.finite(emissions))) {
    stop("Time and emissions must be finite and have equal lengths.", call. = FALSE)
  }
  if (is.unsorted(time, strictly = TRUE)) stop("Time column must be strictly increasing.", call. = FALSE)
  if (any(emissions < 0)) stop("Emissions values cannot be negative.", call. = FALSE)

  cumulative <- sum((utils::head(emissions, -1) + utils::tail(emissions, -1)) / 2 * diff(time))
  remaining <- budget - cumulative
  list(
    cumulative_emissions = cumulative,
    budget = budget,
    remaining = remaining,
    within_budget = remaining >= 0
  )
}
