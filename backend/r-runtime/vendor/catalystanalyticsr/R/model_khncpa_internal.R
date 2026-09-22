.khncpa_as_state <- function(x) {
  if (is.list(x)) x <- unlist(x)
  .validate_state(x, "state")
  as.numeric_state <- as.numeric(x[.khncpa_required_states()])
  names(as.numeric_state) <- .khncpa_required_states()
  as.numeric_state
}

.khncpa_required_states <- function() c("K", "H", "N", "C", "P", "A")

.khncpa_build_params <- function(params, x0) {
  x0 <- .khncpa_as_state(x0)
  base <- list(
    alpha = 0.30,
    beta = 0.30,
    gamma = 0.10,
    deltaK = 0.05,
    deltaH = 0.03,
    Nmax = 1.0,
    regen = 0.02,
    depletion_intensity = 0.01,
    emissions_intensity = 0.30,
    absorption = 0.10,
    C0 = as.numeric(x0[["C"]]),
    damage_scale = 0.001,
    pop_growth = 0.01,
    Pmax = NA_real_,
    tech_growth = 0.01,
    abatement_cost_scale = 0.02
  )

  .validate_params(params)
  if (is.null(params)) params <- list()
  unknown <- setdiff(names(params), names(base))
  if (length(unknown) > 0L) {
    stop(sprintf("Unknown model parameter(s): %s.", paste(unknown, collapse = ", ")), call. = FALSE)
  }
  out <- utils::modifyList(base, params)

  scalar_names <- setdiff(names(out), "Pmax")
  invalid <- scalar_names[!vapply(out[scalar_names], function(value) {
    is.numeric(value) && length(value) == 1L && is.finite(value)
  }, logical(1))]
  if (length(invalid) > 0L) {
    stop(sprintf("Model parameters must be finite numeric scalars: %s.", paste(invalid, collapse = ", ")), call. = FALSE)
  }

  nonnegative <- c(
    "alpha", "beta", "gamma", "deltaK", "deltaH", "Nmax", "regen",
    "depletion_intensity", "emissions_intensity", "absorption", "damage_scale",
    "pop_growth", "tech_growth", "abatement_cost_scale"
  )
  if (any(unlist(out[nonnegative], use.names = FALSE) < 0)) {
    stop("Model rate, scale, and elasticity parameters cannot be negative.", call. = FALSE)
  }
  if ((out$alpha + out$beta + out$gamma) > 1) {
    stop("`alpha + beta + gamma` must be <= 1.", call. = FALSE)
  }
  if (out$Nmax <= 0) stop("`Nmax` must be greater than zero.", call. = FALSE)
  if (!is.na(out$Pmax) && (!is.numeric(out$Pmax) || length(out$Pmax) != 1L || !is.finite(out$Pmax) || out$Pmax <= 0)) {
    stop("`Pmax` must be NA or a single positive finite number.", call. = FALSE)
  }
  out
}

.khncpa_get_u <- function(policy, name, t, x) {
  .validate_policy(policy)
  u <- policy[[name]]
  value <- if (is.function(u)) u(t, x) else u
  if (!is.numeric(value) || length(value) != 1L || !is.finite(value)) {
    stop(sprintf("Policy `%s` must evaluate to one finite numeric value.", name), call. = FALSE)
  }
  as.numeric(value)
}

.khncpa_flows_from_state <- function(t, x, policy, p) {
  x <- .khncpa_as_state(x)

  K <- max(as.numeric(x[["K"]]), 1e-12)
  H <- max(as.numeric(x[["H"]]), 1e-12)
  N <- max(as.numeric(x[["N"]]), 1e-12)
  C <- as.numeric(x[["C"]])
  P <- max(as.numeric(x[["P"]]), 1e-12)
  A <- max(as.numeric(x[["A"]]), 1e-12)

  s <- .khncpa_get_u(policy, "s", t, x)
  e <- .khncpa_get_u(policy, "e", t, x)
  a <- .khncpa_get_u(policy, "a", t, x)

  if (s < 0 || e < 0) stop("Policy values `s` and `e` must be >= 0.", call. = FALSE)
  if (a < 0 || a > 1) stop("Policy value `a` (abatement) must be within [0, 1].", call. = FALSE)
  if ((s + e) > 0.95) stop("Policy values `s + e` must be <= 0.95.", call. = FALSE)

  expoP <- 1 - p$alpha - p$beta - p$gamma
  Y <- A * (K ^ p$alpha) * (H ^ p$beta) * (N ^ p$gamma) * (P ^ expoP)

  abate_cost <- p$abatement_cost_scale * (a ^ 2) * Y
  emissions <- p$emissions_intensity * (1 - a) * Y
  depletion <- p$depletion_intensity * Y
  damages <- p$damage_scale * ((C - p$C0) ^ 2) * Y

  savings <- s * Y
  education <- e * Y
  consumption <- max((1 - s - e) * Y - abate_cost, 0)

  list(
    Y = Y,
    s = s,
    e = e,
    a = a,
    savings = savings,
    education = education,
    consumption = consumption,
    emissions = emissions,
    depletion = depletion,
    damages = damages
  )
}

.khncpa_deriv <- function(t, x, policy, p) {
  x <- .khncpa_as_state(x)
  fl <- .khncpa_flows_from_state(t, x, policy, p)

  K <- as.numeric(x[["K"]])
  H <- as.numeric(x[["H"]])
  N <- as.numeric(x[["N"]])
  C <- as.numeric(x[["C"]])
  P <- as.numeric(x[["P"]])
  A <- as.numeric(x[["A"]])

  dK <- fl$savings - p$deltaK * K - (p$abatement_cost_scale * (fl$a ^ 2) * fl$Y)
  dH <- fl$education - p$deltaH * H
  dN <- p$regen * (p$Nmax - N) - fl$depletion
  dC <- fl$emissions - p$absorption * (C - p$C0)
  dP <- if (is.na(p$Pmax)) {
    p$pop_growth * P
  } else {
    p$pop_growth * P * (1 - P / p$Pmax)
  }
  dA <- p$tech_growth * A

  c(K = dK, H = dH, N = dN, C = dC, P = dP, A = dA)
}
