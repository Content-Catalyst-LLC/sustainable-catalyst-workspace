#' Run a complete Catalyst Analytics scenario
#'
#' The package front door: run the model, compute indicators, produce plots,
#' and return one structured `catalyst_run` object.
#'
#' @param times Numeric vector of times.
#' @param x0 Named numeric vector of initial states (K,H,N,C,P,A).
#' @param policy List of policy controls (s,e,a).
#' @param params List of model parameters.
#' @param scenario Scenario label.
#' @param model Registered model id or `catalyst_model` object.
#' @param model_version Optional exact model version.
#' @param method Integration method.
#' @param emissions_budget Optional non-negative cumulative emissions budget.
#' @param carbon_budget_value Deprecated alias for `emissions_budget`.
#' @param include_phase_plane Logical. If TRUE, compute a phase plane.
#' @param include_sensitivity Logical. If TRUE, compute Jacobian sensitivities.
#' @return A list with class `catalyst_run`.
#' @export
#'
#' @examples
#' times <- seq(0, 10, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' x <- catalyst_run(times, x0, include_phase_plane = FALSE, include_sensitivity = FALSE)
#' plot(x, which = "trajectory")
catalyst_run <- function(
  times,
  x0,
  policy = NULL,
  params = list(),
  scenario = "baseline",
  model = "khncpa",
  model_version = NULL,
  method = c("rk4", "euler"),
  emissions_budget = NULL,
  carbon_budget_value = NULL,
  include_phase_plane = TRUE,
  include_sensitivity = TRUE
) {
  model_object <- .resolve_catalyst_model(model, model_version)
  method <- match.arg(method, model_object$integration_methods)
  if (is.null(policy)) policy <- model_object$default_policy
  model_object$validate_policy(policy)
  .assert_flag(include_phase_plane, "include_phase_plane")
  .assert_flag(include_sensitivity, "include_sensitivity")

  if (!is.null(emissions_budget) && !is.null(carbon_budget_value)) {
    stop("Provide only one of `emissions_budget` or `carbon_budget_value`.", call. = FALSE)
  }
  if (is.null(emissions_budget)) emissions_budget <- carbon_budget_value
  if (!is.null(emissions_budget)) {
    .assert_scalar_number(emissions_budget, "emissions_budget", lower = 0)
  }

  res <- simulate_dynamics(
    times = times,
    x0 = x0,
    policy = policy,
    params = params,
    model = model_object,
    method = method,
    scenario = scenario,
    return_long = TRUE
  )

  sdg_required <- c("P", "N", "C", "gdp", "emissions", "ans")
  sdg <- if (all(sdg_required %in% names(res$trajectory_wide))) {
    sdg_indicators(res$trajectory_wide)
  } else {
    .model_indicators(res$trajectory_wide, model_object)
  }
  cb <- if (is.null(emissions_budget)) NULL else {
    carbon_budget(res$trajectory_wide, budget = emissions_budget)
  }

  state0 <- vapply(model_object$required_states, function(state) {
    as.numeric(res$trajectory_wide[[state]][1L])
  }, numeric(1))

  pp <- NULL
  if (include_phase_plane && identical(model_object$id, "khncpa")) {
    safe_range <- function(values) {
      value_range <- range(values, finite = TRUE)
      if (diff(value_range) == 0) {
        pad <- max(abs(value_range[1]) * 0.05, 0.05)
        value_range <- value_range + c(-pad, pad)
      }
      value_range
    }
    pp <- phase_plane(
      x_var = "K",
      y_var = "C",
      x_range = safe_range(res$trajectory_wide$K),
      y_range = safe_range(res$trajectory_wide$C),
      n = 15,
      t = times[1],
      state_fixed = state0,
      policy = policy,
      params = params,
      normalize = TRUE
    )
  }

  sens <- if (include_sensitivity && identical(model_object$id, "khncpa")) {
    sensitivity_jacobian(state = state0, params = params, t = times[1], policy = policy)
  } else NULL

  make_score <- function(df, cols) {
    start <- df[1, , drop = FALSE]
    end <- df[nrow(df), , drop = FALSE]
    rows <- lapply(cols[cols %in% names(df)], function(metric) {
      start_value <- as.numeric(start[[metric]])
      end_value <- as.numeric(end[[metric]])
      data.frame(
        metric = metric,
        start = start_value,
        end = end_value,
        change = end_value - start_value,
        pct_change = if (is.finite(start_value) && start_value != 0) {
          (end_value - start_value) / start_value
        } else NA_real_,
        stringsAsFactors = FALSE
      )
    })
    if (length(rows) == 0L) NULL else do.call(rbind, rows)
  }
  scorecard <- make_score(res$trajectory_wide, c("gdp", "emissions", "ans", "N", "C"))

  dashboard_indicators <- intersect(
    c("gdp", "emissions", "ans", "carbon_intensity"),
    unique(sdg$indicator)
  )
  if (!length(dashboard_indicators)) {
    dashboard_indicators <- utils::head(unique(sdg$indicator), 4L)
  }
  plots <- list(
    trajectory = plot_trajectory(res$trajectory_long, metrics = c("gdp", "emissions", "ans")),
    sdg_dashboard = plot_sdg_dashboard(sdg, indicators = dashboard_indicators)
  )
  if (!is.null(pp)) plots$phase_plane <- plot_phase_plane(pp, res$trajectory_wide)
  if (!is.null(sens)) plots$sensitivity_heatmap <- plot_sensitivity_heatmap(sens)

  out <- list(
    trajectory_wide = res$trajectory_wide,
    trajectory_long = res$trajectory_long,
    sdg_indicators = sdg,
    carbon_budget = cb,
    scorecard = scorecard,
    phase_plane = pp,
    sensitivities = sens,
    meta = res$meta,
    plots = plots
  )
  class(out) <- "catalyst_run"
  out
}

#' Run a stable demonstration scenario
#'
#' @param seed Integer seed retained for reproducibility.
#' @param budget_mode Budget behavior: "auto", "pass", "fail", or "custom".
#' @param headroom Fractional budget slack for automatic modes.
#' @param emissions_budget Numeric budget required for custom mode.
#' @return A `catalyst_run` object.
#' @export
#'
#' @examples
#' x <- catalyst_demo()
#' print(x)
#' plot(x, which = "trajectory")
catalyst_demo <- function(
  seed = 42L,
  budget_mode = c("auto", "pass", "fail", "custom"),
  headroom = 0.05,
  emissions_budget = NULL
) {
  .assert_scalar_number(seed, "seed")
  .assert_scalar_number(headroom, "headroom", lower = 0, upper = 0.99)
  set.seed(as.integer(seed))
  budget_mode <- match.arg(budget_mode)

  times <- seq(0, 20, by = 1)
  x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
  base <- simulate_dynamics(times, x0, return_long = FALSE)
  cumulative <- carbon_budget(base$trajectory_wide, budget = 1e12)$cumulative_emissions

  if (budget_mode == "custom") {
    if (is.null(emissions_budget)) {
      stop("For `budget_mode = 'custom'`, supply `emissions_budget`.", call. = FALSE)
    }
    .assert_scalar_number(emissions_budget, "emissions_budget", lower = 0)
    budget <- emissions_budget
  } else if (!is.null(emissions_budget)) {
    stop("`emissions_budget` is only used when `budget_mode = 'custom'`.", call. = FALSE)
  } else if (budget_mode %in% c("auto", "pass")) {
    budget <- cumulative * (1 + headroom)
  } else {
    budget <- cumulative * (1 - headroom)
  }

  catalyst_run(
    times = times,
    x0 = x0,
    scenario = paste0("demo_", budget_mode),
    emissions_budget = budget,
    include_phase_plane = TRUE,
    include_sensitivity = TRUE
  )
}
