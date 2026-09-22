.catalyst_inclusive_development_schema_version <- function() "1.0.0"

#' Assemble inclusive wealth, human development, and distribution analysis
#'
#' @param wealth A `catalyst_inclusive_wealth` account.
#' @param adjusted_net_savings Optional Adjusted Net Savings data frame.
#' @param human_development Optional human-development indicator data frame.
#' @param distribution Optional `catalyst_distribution_analysis`.
#' @param intergenerational Optional `catalyst_intergenerational_analysis`.
#' @param composite Optional `catalyst_composite_score`.
#' @param analysis_id Stable analysis identifier.
#' @param title Human-readable title.
#' @param metadata Additional metadata.
#' @param x An inclusive-development object.
#' @param ... Additional method arguments.
#' @return A governed `catalyst_inclusive_development` analysis or summary.
#' @name inclusive_development
NULL

#' @rdname inclusive_development
#' @export
inclusive_development_analysis <- function(
  wealth,
  adjusted_net_savings = NULL,
  human_development = NULL,
  distribution = NULL,
  intergenerational = NULL,
  composite = NULL,
  analysis_id = "inclusive-development",
  title = "Inclusive wealth, human development, and distribution",
  metadata = list()
) {
  if (!inherits(wealth, "catalyst_inclusive_wealth")) stop("`wealth` must be an inclusive-wealth account.", call. = FALSE)
  if (!is.null(adjusted_net_savings) && (!is.data.frame(adjusted_net_savings) || !"adjusted_net_savings" %in% names(adjusted_net_savings))) {
    stop("`adjusted_net_savings` must be a decomposition data frame.", call. = FALSE)
  }
  if (!is.null(human_development) && (!is.data.frame(human_development) || !"human_development_index" %in% names(human_development))) {
    stop("`human_development` must be a human-development indicator data frame.", call. = FALSE)
  }
  if (!is.null(distribution) && !inherits(distribution, "catalyst_distribution_analysis")) stop("`distribution` is invalid.", call. = FALSE)
  if (!is.null(intergenerational) && !inherits(intergenerational, "catalyst_intergenerational_analysis")) stop("`intergenerational` is invalid.", call. = FALSE)
  if (!is.null(composite) && !inherits(composite, "catalyst_composite_score")) stop("`composite` is invalid.", call. = FALSE)
  .validate_dataset_id(analysis_id, "analysis_id")
  .assert_single_string(title, "title")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .catalyst_inclusive_development_schema_version(),
    analysis_type = "inclusive_wealth_human_development_distribution",
    id = analysis_id,
    title = title,
    wealth = wealth,
    adjusted_net_savings = adjusted_net_savings,
    human_development = human_development,
    distribution = distribution,
    intergenerational = intergenerational,
    composite = composite,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      review_status = "unreviewed",
      methodology_boundary = "capital valuation, social floors, distribution weights, and composite-score choices require human review"
    ), metadata)
  ), class = "catalyst_inclusive_development")
}

#' @rdname inclusive_development
#' @export
inclusive_development_summary <- function(x) {
  if (!inherits(x, "catalyst_inclusive_development")) stop("`x` must be an inclusive-development analysis.", call. = FALSE)
  wealth_summary <- inclusive_wealth_summary(x$wealth)
  final_wealth <- wealth_summary[nrow(wealth_summary), , drop = FALSE]
  final_ans <- if (is.null(x$adjusted_net_savings)) NA_real_ else tail(x$adjusted_net_savings$adjusted_net_savings, 1L)
  final_hdi <- if (is.null(x$human_development)) NA_real_ else tail(x$human_development$human_development_index, 1L)
  gini <- if (is.null(x$distribution)) NA_real_ else x$distribution$summary$gini
  floor_share <- if (is.null(x$distribution)) NA_real_ else x$distribution$summary$share_below_social_floor
  intergenerational_signal <- if (is.null(x$intergenerational)) NA else x$intergenerational$summary$non_declining_signal
  composite_score <- if (is.null(x$composite)) NA_real_ else tail(x$composite$scores$composite_score, 1L)
  data.frame(
    analysis_id = x$id,
    closing_inclusive_wealth = final_wealth$closing_inclusive_wealth,
    inclusive_wealth_change = final_wealth$absolute_change,
    closing_per_capita_wealth = final_wealth$closing_per_capita,
    adjusted_net_savings = final_ans,
    human_development_index = final_hdi,
    gini = gini,
    share_below_social_floor = floor_share,
    non_declining_per_capita_wealth = intergenerational_signal,
    composite_score = composite_score,
    stringsAsFactors = FALSE
  )
}

#' @rdname inclusive_development
#' @export
plot_inclusive_development <- function(x) {
  if (!inherits(x, "catalyst_inclusive_development")) stop("`x` must be an inclusive-development analysis.", call. = FALSE)
  data <- x$wealth$data
  long <- rbind(
    data.frame(entity = data$entity, time = data$time, capital_type = "Produced", value = data$produced_capital_value),
    data.frame(entity = data$entity, time = data$time, capital_type = "Human", value = data$human_capital_value),
    data.frame(entity = data$entity, time = data$time, capital_type = "Natural", value = data$natural_capital_value)
  )
  ggplot2::ggplot(long, ggplot2::aes(x = time, y = value, fill = capital_type)) +
    ggplot2::geom_area(position = "stack", alpha = 0.85) +
    ggplot2::facet_wrap(~entity, scales = "free_x") +
    ggplot2::labs(x = NULL, y = "Valued capital", fill = "Capital", title = x$title) +
    theme_catalyst()
}

#' @rdname inclusive_development
#' @export
print.catalyst_inclusive_development <- function(x, ...) {
  summary <- inclusive_development_summary(x)
  cat(sprintf("<catalyst_inclusive_development %s>\n", x$id))
  cat(sprintf("  closing inclusive wealth: %.4f\n", summary$closing_inclusive_wealth))
  cat(sprintf("  composite score: %s\n", ifelse(is.na(summary$composite_score), "n/a", format(summary$composite_score, digits = 4))))
  invisible(x)
}
