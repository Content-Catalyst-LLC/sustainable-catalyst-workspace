#' Simulate registered model dynamics
#'
#' Runs a registered Catalyst model over `times` and returns wide and optional
#' long trajectories for analysis, plotting, and export.
#'
#' @param times Numeric vector of time points.
#' @param x0 Named numeric vector of initial state.
#' @param policy Named policy list. Uses model defaults when omitted.
#' @param params Named parameter overrides.
#' @param model Registered model id or `catalyst_model` object.
#' @param model_version Optional exact model version when `model` is an id.
#' @param method Integration method ("rk4" or "euler").
#' @param scenario Non-empty scenario label.
#' @param return_long Logical. If TRUE, also return a long trajectory.
#' @return A list with `trajectory_wide`, optional `trajectory_long`, and `meta`.
#' @export
#'
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- simulate_dynamics(times, x0, return_long = TRUE)
#' head(res$trajectory_wide)
simulate_dynamics <- function(
  times,
  x0,
  policy = NULL,
  params = list(),
  model = "khncpa",
  model_version = NULL,
  method = c("rk4", "euler"),
  scenario = "baseline",
  return_long = TRUE
) {
  model_object <- .resolve_catalyst_model(model, model_version)
  method <- match.arg(method, model_object$integration_methods)
  .validate_times(times)
  x0 <- model_object$validate_state(x0)
  if (is.null(policy)) policy <- model_object$default_policy
  model_object$validate_policy(policy)
  model_object$validate_params(params)
  .assert_single_string(scenario, "scenario")
  .assert_flag(return_long, "return_long")

  required_states <- model_object$required_states
  p <- model_object$build_params(params, x0)

  n <- length(times)
  states <- matrix(NA_real_, nrow = n, ncol = length(required_states))
  colnames(states) <- required_states
  states[1L, ] <- as.numeric(x0[required_states])

  flow_names <- names(model_object$flow_map)
  flows <- matrix(NA_real_, nrow = n, ncol = length(flow_names))
  colnames(flows) <- flow_names
  ans_series <- rep(NA_real_, n)

  record_flows <- function(i, time) {
    raw <- model_object$flows(time, states[i, ], policy, p)
    if (!is.list(raw) || !all(unname(model_object$flow_map) %in% names(raw))) {
      stop(sprintf("Model `%s` returned an invalid flow record.", model_object$id), call. = FALSE)
    }
    values <- vapply(model_object$flow_map, function(raw_name) {
      value <- raw[[raw_name]]
      if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) {
        stop(sprintf("Model flow `%s` must be one finite numeric value.", raw_name), call. = FALSE)
      }
      as.numeric(value)
    }, numeric(1))
    flows[i, ] <<- values[flow_names]
    ans_series[i] <<- ans(values[["savings"]], values[["education"]], values[["depletion"]], values[["damages"]])
  }
  record_flows(1L, times[1L])

  for (i in seq_len(n - 1L)) {
    t <- times[i]
    h <- times[i + 1L] - times[i]
    xi <- states[i, ]

    derivative <- function(time, state) {
      value <- model_object$derivative(time, state, policy, p)
      if (!is.numeric(value) || length(value) != length(required_states)) {
        stop(sprintf("Model `%s` returned an invalid derivative.", model_object$id), call. = FALSE)
      }
      if (!is.null(names(value))) value <- value[required_states]
      if (any(!is.finite(value))) {
        stop(sprintf("Model `%s` returned an invalid derivative.", model_object$id), call. = FALSE)
      }
      as.numeric(value)
    }

    xnext <- if (method == "euler") {
      k1 <- derivative(t, xi)
      xi + h * k1
    } else {
      k1 <- derivative(t, xi)
      k2 <- derivative(t + h / 2, xi + (h / 2) * k1)
      k3 <- derivative(t + h / 2, xi + (h / 2) * k2)
      k4 <- derivative(t + h, xi + h * k3)
      xi + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)
    }

    if (any(!is.finite(xnext))) {
      stop(sprintf("Non-finite state generated at time %s.", times[i + 1L]), call. = FALSE)
    }
    states[i + 1L, ] <- as.numeric(xnext)
    record_flows(i + 1L, times[i + 1L])
  }

  trajectory_wide <- data.frame(t = times, scenario = scenario, stringsAsFactors = FALSE)
  for (state_name in required_states) trajectory_wide[[state_name]] <- states[, state_name]
  for (flow_name in flow_names) trajectory_wide[[flow_name]] <- flows[, flow_name]
  trajectory_wide$ans <- ans_series

  meta <- list(
    package_version = .catalyst_package_version(),
    model = model_object$id,
    model_version = model_object$version,
    model_contract_version = catalyst_globals()$model_contract_version,
    integration_method = method,
    scenario = scenario,
    time_start = times[1L],
    time_end = times[n],
    time_steps = n,
    time_values = as.numeric(times),
    initial_state = as.list(x0[required_states]),
    params = p,
    parameter_overrides = params,
    policy = policy
  )

  if (!return_long) return(list(trajectory_wide = trajectory_wide, meta = meta))

  metric_cols <- c(required_states, flow_names, "ans")
  units <- c(
    model_object$state_units[required_states],
    model_object$flow_units[flow_names],
    ans = "index"
  )
  trajectory_long <- do.call(rbind, lapply(metric_cols, function(metric) {
    data.frame(
      t = trajectory_wide$t,
      scenario = trajectory_wide$scenario,
      metric = metric,
      value = trajectory_wide[[metric]],
      unit = unname(units[[metric]]),
      stringsAsFactors = FALSE
    )
  }))
  rownames(trajectory_long) <- NULL

  list(
    trajectory_wide = trajectory_wide,
    trajectory_long = trajectory_long,
    meta = meta
  )
}
