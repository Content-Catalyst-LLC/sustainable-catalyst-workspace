#' Plot Model Trajectories with ggplot2
#'
#' @param trajectory_long A long data frame (e.g., res$trajectory_long).
#' @param metrics Character vector of metrics to plot (NULL = all metrics).
#' @param facet_scales Facet scaling passed to ggplot2::facet_wrap().
#' @return A ggplot object.
#' @export
#' @examples
#' times <- seq(0, 10, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = TRUE)
#' plot_trajectory(res$trajectory_long, metrics = c("gdp", "emissions"))

plot_trajectory <- function(
    trajectory_long,
    metrics = NULL,
    facet_scales = "free_y"
) {
  if (!is.data.frame(trajectory_long)) stop("`trajectory_long` must be a data.frame.")
  required <- c("t", "scenario", "metric", "value")
  if (!all(required %in% names(trajectory_long))) {
    stop("`trajectory_long` must have columns: t, scenario, metric, value.")
  }
  
  df <- trajectory_long
  if (!is.null(metrics)) {
    df <- df[df$metric %in% metrics, , drop = FALSE]
  }
  if (nrow(df) == 0) stop("No rows to plot after filtering `metrics`.")
  
  ggplot2::ggplot(df, ggplot2::aes(x = t, y = value, color = scenario)) +
    ggplot2::geom_line(linewidth = 0.8) +
    ggplot2::facet_wrap(~ metric, scales = facet_scales) +
    ggplot2::labs(x = "t", y = NULL, color = "Scenario") +
    theme_catalyst()
}
