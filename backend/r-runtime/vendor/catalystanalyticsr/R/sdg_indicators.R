#' Compute a small set of SDG-adjacent indicators from a trajectory
#'
#' This function intentionally keeps the indicator set small and stable for the public package demo.
#' It returns a tidy (long) table that is easy to plot and export.
#'
#' @param trajectory_wide Data.frame from simulate_dynamics() (trajectory_wide).
#'
#' @return A data.frame with columns: t, scenario, indicator, value, unit, direction.
#' @export
#' @examples
#' times <- seq(0, 10, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = FALSE)
#' sdg <- sdg_indicators(res$trajectory_wide)
#' head(sdg)
sdg_indicators <- function(trajectory_wide) {
  if (!is.data.frame(trajectory_wide)) stop("`trajectory_wide` must be a data.frame.")
  req <- c("t", "scenario", "gdp", "emissions", "ans", "P", "N", "C")
  if (!all(req %in% names(trajectory_wide))) {
    stop("`trajectory_wide` must contain: t, scenario, gdp, emissions, ans, P, N, C.")
  }

  tw <- trajectory_wide
  # Avoid division by zero
  P <- pmax(tw$P, 1e-12)
  gdp <- tw$gdp
  emissions <- tw$emissions

  derived <- list(
    gdp = list(value = gdp, unit = "index", direction = "higher_better", formula = "gdp", fields = "gdp"),
    gdp_per_capita = list(value = gdp / P, unit = "index/person_index", direction = "higher_better", formula = "gdp / P", fields = "gdp,P"),
    emissions = list(value = emissions, unit = "tCO2e_index", direction = "lower_better", formula = "emissions", fields = "emissions"),
    emissions_per_capita = list(value = emissions / P, unit = "tCO2e_index/person_index", direction = "lower_better", formula = "emissions / P", fields = "emissions,P"),
    carbon_intensity = list(value = emissions / pmax(gdp, 1e-12), unit = "tCO2e_index/index", direction = "lower_better", formula = "emissions / gdp", fields = "emissions,gdp"),
    ans = list(value = tw$ans, unit = "index", direction = "higher_better", formula = "ans", fields = "ans"),
    natural_capital = list(value = tw$N, unit = "index", direction = "higher_better", formula = "N", fields = "N"),
    atmospheric_carbon = list(value = tw$C, unit = "index", direction = "lower_better", formula = "C", fields = "C")
  )

  out <- list()
  k <- 1
  for (nm in names(derived)) {
    out[[k]] <- data.frame(
      t = tw$t,
      scenario = tw$scenario,
      indicator = nm,
      value = as.numeric(derived[[nm]]$value),
      unit = derived[[nm]]$unit,
      direction = derived[[nm]]$direction,
      indicator_version = "1.0.0",
      formula = derived[[nm]]$formula,
      source_fields = derived[[nm]]$fields,
      registry_status = "registered",
      stringsAsFactors = FALSE
    )
    k <- k + 1
  }

  do.call(rbind, out)
}
#' Plot an SDG-style dashboard (small multiples)
#'
#' @description Creates a simple small-multiples dashboard from the output of
#' [sdg_indicators()].
#'
#' @param sdg_df Output of [sdg_indicators()].
#' @param indicators Optional subset of indicator names to show.
#' @param facet_scales Facet scaling for y.
#'
#' @return A ggplot object.
#' @export
#'
#' @examples
#' times <- seq(0, 10, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = FALSE)
#' sdg <- sdg_indicators(res$trajectory_wide)
#' plot_sdg_dashboard(sdg)
plot_sdg_dashboard <- function(
  sdg_df,
  indicators = c("gdp", "emissions", "ans", "carbon_intensity"),
  facet_scales = "free_y"
) {
  if (!is.data.frame(sdg_df)) stop("`sdg_df` must be a data.frame.")
  req <- c("t", "scenario", "indicator", "value")
  if (!all(req %in% names(sdg_df))) stop("`sdg_df` missing required columns.")

  df <- sdg_df
  if (!is.null(indicators)) {
    df <- df[df$indicator %in% indicators, , drop = FALSE]
  }
  if (nrow(df) == 0) stop("No rows to plot after filtering indicators.")

  ggplot2::ggplot(df, ggplot2::aes(x = t, y = value, color = scenario)) +
    ggplot2::geom_line(linewidth = 0.8) +
    ggplot2::facet_wrap(~ indicator, scales = facet_scales) +
    ggplot2::labs(x = "t", y = NULL, color = "Scenario", title = "SDG indicators") +
    theme_catalyst()
}
