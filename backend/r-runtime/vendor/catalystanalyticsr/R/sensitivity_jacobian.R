#' Finite-difference sensitivity Jacobian (d f / d theta)
#'
#' Computes a Jacobian-style sensitivity matrix for the KH-NC-PA vector field
#' with respect to model parameters. This is intended as a lightweight,
#' reproducible sensitivity diagnostic for the public package demo.
#'
#' @param state Named numeric vector of states (K,H,N,C,P,A) at which to evaluate sensitivities.
#' @param params List of parameter overrides.
#' @param params_to_test Character vector. Subset of parameters to perturb.
#' @param t Numeric. Time at which to evaluate the vector field.
#' @param policy List of policy controls (s,e,a).
#' @param eps Numeric. Relative perturbation scale.
#'
#' @return A long data.frame with columns: state, param, value, t.
#' @export
#' @examples
#' state <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' sens <- sensitivity_jacobian(state, t = 0)
#' head(sens)
sensitivity_jacobian <- function(
  state,
  params = list(),
  params_to_test = NULL,
  t = 0,
  policy = list(s = 0.20, e = 0.05, a = 0.00),
  eps = 1e-5
) {
  req <- .khncpa_required_states()
  state <- .khncpa_as_state(state)
  if (!all(req %in% names(state))) stop("`state` must include names: K, H, N, C, P, A.")
  if (!is.numeric(eps) || length(eps) != 1 || eps <= 0) stop("`eps` must be a single positive number.")

  p0 <- .khncpa_build_params(params, state)
  p_names <- names(p0)

  if (is.null(params_to_test)) {
    # A sensible small default set for the demo.
    params_to_test <- intersect(c("alpha", "beta", "gamma", "emissions_intensity", "absorption", "depletion_intensity"), p_names)
  }
  if (!is.character(params_to_test)) stop("`params_to_test` must be a character vector.")
  params_to_test <- intersect(params_to_test, p_names)
  if (length(params_to_test) == 0) stop("No valid parameters selected in `params_to_test`.")

  out <- list()
  k <- 1
  for (theta in params_to_test) {
    base_val <- p0[[theta]]
    if (!is.numeric(base_val) || length(base_val) != 1 || !is.finite(base_val)) next

    delta <- eps * (abs(base_val) + 1)
    p_plus <- p0
    p_minus <- p0
    p_plus[[theta]] <- base_val + delta
    p_minus[[theta]] <- base_val - delta

    f_plus <- .khncpa_deriv(t, state, policy, p_plus)
    f_minus <- .khncpa_deriv(t, state, policy, p_minus)

    dfdtheta <- (f_plus - f_minus) / (2 * delta)

    for (s in req) {
      out[[k]] <- data.frame(
        state = s,
        param = theta,
        value = as.numeric(dfdtheta[[s]]),
        t = t,
        stringsAsFactors = FALSE
      )
      k <- k + 1
    }
  }
  
  do.call(rbind, out)
}
#' Plot a sensitivity heatmap
#'
#' @description Create a heatmap visualization from a sensitivity/Jacobian table.
#' @param sens_df Output of [sensitivity_jacobian()].
#' @return A ggplot object.
#' @export
#'
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' run <- catalyst_run(times, x0, include_phase_plane = FALSE, include_sensitivity = TRUE)
#' plot_sensitivity_heatmap(run$sensitivities)
plot_sensitivity_heatmap <- function(sens_df) {
  if (!is.data.frame(sens_df)) stop("`sens_df` must be a data.frame.")
  needed <- c("state", "param", "value")
  if (!all(needed %in% names(sens_df))) stop("`sens_df` missing required columns.")

  ggplot2::ggplot(sens_df, ggplot2::aes(x = param, y = state, fill = value)) +
    ggplot2::geom_tile() +
    ggplot2::labs(x = "Parameter", y = "State", title = "Sensitivity heatmap") +
    theme_catalyst() +
    ggplot2::theme(axis.text.x = ggplot2::element_text(angle = 35, hjust = 1))
}