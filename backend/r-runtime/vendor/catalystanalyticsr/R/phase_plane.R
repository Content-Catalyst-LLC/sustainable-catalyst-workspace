#' Compute a 2D phase plane (vector field) for the KH-NC-PA model
#'
#' This is a utility for visualization: pick two state dimensions (e.g., K vs C)
#' and hold the other state variables fixed.
#'
#' @param x_var Character. State name for x-axis (default "K").
#' @param y_var Character. State name for y-axis (default "C").
#' @param x_range Numeric length-2. Range for x grid.
#' @param y_range Numeric length-2. Range for y grid.
#' @param n Integer. Grid resolution per axis.
#' @param t Numeric. Time at which to evaluate the vector field.
#' @param state_fixed Named numeric vector. Baseline values for all states.
#' @param policy List of policy controls (s, e, a) as in simulate_dynamics().
#' @param params List of parameters (overrides defaults).
#' @param normalize Logical. If TRUE, scales arrows to unit length for plotting.
#'
#' @return A data.frame with columns x, y, dx, dy, dx_raw, dy_raw.
#' @export
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' base <- simulate_dynamics(times, x0, return_long = FALSE)
#'
#' state0 <- as.numeric(base$trajectory_wide[1, c("K","H","N","C","P","A")])
#' names(state0) <- c("K","H","N","C","P","A")
#'
#' pp <- phase_plane(
#'   x_var = "K",
#'   y_var = "C",
#'   x_range = range(base$trajectory_wide$K, na.rm = TRUE),
#'   y_range = range(base$trajectory_wide$C, na.rm = TRUE),
#'   n = 10,
#'   t = times[1],
#'   state_fixed = state0,
#'   policy = list(s = 0.20, e = 0.05, a = 0.00),
#'   params = list(),
#'   normalize = TRUE
#' )
#' head(pp)
phase_plane <- function(
  x_var = "K",
  y_var = "C",
  x_range = c(0.5, 3),
  y_range = c(-1, 3),
  n = 15,
  t = 0,
  state_fixed = c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1),
  policy = list(s = 0.20, e = 0.05, a = 0.00),
  params = list(),
  normalize = TRUE
) {
  req <- .khncpa_required_states()
  state_fixed <- .khncpa_as_state(state_fixed)
  if (!all(req %in% names(state_fixed))) {
    stop("`state_fixed` must include names: K, H, N, C, P, A.")
  }
  if (!x_var %in% req || !y_var %in% req) stop("`x_var` and `y_var` must be valid state names.")
  if (!is.numeric(x_range) || length(x_range) != 2) stop("`x_range` must be length-2 numeric.")
  if (!is.numeric(y_range) || length(y_range) != 2) stop("`y_range` must be length-2 numeric.")
  if (!is.numeric(n) || length(n) != 1 || n < 3) stop("`n` must be an integer >= 3.")

  p <- .khncpa_build_params(params, state_fixed)

  xs <- seq(x_range[1], x_range[2], length.out = n)
  ys <- seq(y_range[1], y_range[2], length.out = n)
  grid <- expand.grid(x = xs, y = ys, KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE)

  dx_raw <- numeric(nrow(grid))
  dy_raw <- numeric(nrow(grid))

  for (i in seq_len(nrow(grid))) {
    st <- state_fixed
    st[[x_var]] <- grid$x[i]
    st[[y_var]] <- grid$y[i]
    d <- .khncpa_deriv(t, st, policy, p)
    dx_raw[i] <- as.numeric(d[[x_var]])
    dy_raw[i] <- as.numeric(d[[y_var]])
  }

  dx <- dx_raw
  dy <- dy_raw
  if (isTRUE(normalize)) {
    mag <- sqrt(dx_raw^2 + dy_raw^2)
    mag[mag == 0] <- 1
    dx <- dx_raw / mag
    dy <- dy_raw / mag
  }

  data.frame(
    x = grid$x,
    y = grid$y,
    dx = dx,
    dy = dy,
    dx_raw = dx_raw,
    dy_raw = dy_raw,
    x_var = x_var,
    y_var = y_var,
    stringsAsFactors = FALSE
  )
}

#' Plot a phase plane
#'
#' @param phase_df Output of phase_plane().
#' @param trajectory_wide Optional trajectory_wide to overlay.
#' @param arrow_scale Numeric. Length multiplier for arrows.
#'
#' @return A ggplot object.
#' @export
#' @examples
#' x <- catalyst_demo()
#' pp <- x$phase_plane
#' if (!is.null(pp)) {
#'   plot_phase_plane(pp, trajectory_wide = x$trajectory_wide)
#' }

plot_phase_plane <- function(
  phase_df,
  trajectory_wide = NULL,
  arrow_scale = 0.12
) {
  if (!is.data.frame(phase_df)) stop("`phase_df` must be a data.frame (from phase_plane()).")
  needed <- c("x", "y", "dx", "dy", "x_var", "y_var")
  if (!all(needed %in% names(phase_df))) stop("`phase_df` is missing required columns.")

  x_var <- unique(phase_df$x_var)[1]
  y_var <- unique(phase_df$y_var)[1]

  arrows <- transform(
    phase_df,
    xend = x + arrow_scale * dx,
    yend = y + arrow_scale * dy
  )

  p <- ggplot2::ggplot(arrows, ggplot2::aes(x = x, y = y, xend = xend, yend = yend)) +
    ggplot2::geom_segment(
      linewidth = 0.35,
      alpha = 0.75,
      arrow = grid::arrow(length = grid::unit(0.08, "inches"))
    ) +
    ggplot2::labs(x = x_var, y = y_var, title = "Phase plane") +
    theme_catalyst()

  if (!is.null(trajectory_wide)) {
    if (!is.data.frame(trajectory_wide)) stop("`trajectory_wide` must be a data.frame.")
    if (!all(c(x_var, y_var) %in% names(trajectory_wide))) {
      stop("`trajectory_wide` must contain the selected x/y state columns.")
    }
    p <- p + ggplot2::geom_path(
      data = trajectory_wide,
      ggplot2::aes(x = !!rlang::sym(x_var), y = !!rlang::sym(y_var)),
      inherit.aes = FALSE,
      linewidth = 0.9
    )
  }

  p
}
