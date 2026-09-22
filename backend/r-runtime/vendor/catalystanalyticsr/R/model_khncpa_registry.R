.khncpa_model_definition <- function() {
  default_state <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
  default_parameters <- .khncpa_build_params(list(), default_state)

  new_catalyst_model(
    id = "khncpa",
    version = "1.0.0",
    title = "KH-NC-PA Vector Dynamics Model",
    description = paste(
      "A coupled produced-capital, human-capital, natural-capital, atmospheric-carbon,",
      "population, and technology scenario model."
    ),
    required_states = .khncpa_required_states(),
    default_state = default_state,
    default_parameters = default_parameters,
    default_policy = list(s = 0.20, e = 0.05, a = 0.00),
    integration_methods = c("rk4", "euler"),
    state_units = c(K = "index", H = "index", N = "index", C = "index", P = "people_index", A = "index"),
    flow_map = c(
      gdp = "Y",
      consumption = "consumption",
      savings = "savings",
      education = "education",
      abatement = "a",
      emissions = "emissions",
      depletion = "depletion",
      damages = "damages"
    ),
    flow_units = c(
      gdp = "index",
      consumption = "index",
      savings = "index",
      education = "index",
      abatement = "share",
      emissions = "tCO2e_index",
      depletion = "index",
      damages = "index"
    ),
    indicator_map = list(
      gdp = list(source = "gdp", unit = "index", direction = "higher_better"),
      emissions = list(source = "emissions", unit = "tCO2e_index", direction = "lower_better"),
      ans = list(source = "ans", unit = "index", direction = "higher_better"),
      natural_capital = list(source = "N", unit = "index", direction = "higher_better"),
      atmospheric_carbon = list(source = "C", unit = "index", direction = "lower_better")
    ),
    derivative = .khncpa_deriv,
    flows = .khncpa_flows_from_state,
    build_params = .khncpa_build_params,
    validate_state = function(x) {
      .validate_state(x, "state")
      state <- as.numeric(x[.khncpa_required_states()])
      names(state) <- .khncpa_required_states()
      state
    },
    validate_policy = function(policy) {
      .validate_policy(policy)
      invisible(policy)
    },
    validate_params = function(params) {
      .validate_params(params)
      invisible(params)
    },
    metadata = list(
      contract_version = "1.0.0",
      status = "experimental",
      intended_use = "Exploratory sustainable-development scenario analysis",
      prohibited_uses = c("forecast", "compliance determination", "professional advice")
    )
  )
}
