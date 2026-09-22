#' Adjusted Net Savings (ANS)
#'
#' Computes gross savings plus education expenditure, less resource depletion
#' and pollution damages.
#'
#' @param gross_savings Numeric gross savings.
#' @param edu_expenditure Numeric education expenditure.
#' @param resource_depletion Numeric natural resource depletion.
#' @param pollution_damage Numeric pollution damages.
#' @return Numeric adjusted net savings.
#' @export
#' @examples
#' ans(100, 10, 15, 5)
ans <- function(gross_savings, edu_expenditure, resource_depletion, pollution_damage) {
  inputs <- list(gross_savings, edu_expenditure, resource_depletion, pollution_damage)
  if (!all(vapply(inputs, is.numeric, logical(1)))) stop("All inputs must be numeric.", call. = FALSE)
  lengths <- vapply(inputs, length, integer(1))
  target <- max(lengths)
  if (target == 0L || any(lengths != 1L & lengths != target)) {
    stop("Inputs must have compatible lengths.", call. = FALSE)
  }
  if (any(!is.finite(unlist(inputs, use.names = FALSE)))) stop("All inputs must be finite.", call. = FALSE)
  if (any(edu_expenditure < 0) || any(resource_depletion < 0) || any(pollution_damage < 0)) {
    stop("Expenditure, depletion, and damage values cannot be negative.", call. = FALSE)
  }
  gross_savings + edu_expenditure - resource_depletion - pollution_damage
}
