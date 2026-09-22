.is_browser_scenario <- function(x) {
  required <- c(
    "scenarioName", "years", "savings", "emissionsIntensity", "adaptation",
    "restoration", "humanInvestment", "initialCapital", "initialHuman",
    "initialNatural", "emissionsBudget"
  )
  is.list(x) && all(required %in% names(x))
}

#' Convert a browser demo scenario to the canonical contract
#'
#' @param x Browser scenario input list or JSON record.
#' @param created_at Timestamp retained in the resulting canonical metadata.
#' @return A `catalyst_scenario` using the registered KH-NC-PA model.
#' @export
browser_scenario_to_catalyst <- function(x, created_at = .utc_now()) {
  if (!.is_browser_scenario(x)) stop("`x` is not a supported browser scenario record.", call. = FALSE)
  value <- function(name) .as_scalar(x[[name]], name)
  years <- as.integer(value("years"))
  .assert_scalar_number(years, "years", lower = 1)
  scenario_name <- as.character(value("scenarioName"))
  .assert_single_string(scenario_name, "scenarioName")

  catalyst_scenario(
    title = scenario_name,
    id = .slugify(scenario_name),
    model = "khncpa",
    model_version = "1.0.0",
    role = "exploratory",
    times = seq(0, years, by = 1),
    initial_state = c(
      K = as.numeric(value("initialCapital")),
      H = as.numeric(value("initialHuman")),
      N = as.numeric(value("initialNatural")),
      C = 0,
      P = 1,
      A = 1
    ),
    policy = list(
      s = as.numeric(value("savings")),
      e = as.numeric(value("humanInvestment")),
      a = as.numeric(value("adaptation"))
    ),
    parameters = list(
      emissions_intensity = as.numeric(value("emissionsIntensity")),
      regen = as.numeric(value("restoration"))
    ),
    constraints = list(emissions_budget = as.numeric(value("emissionsBudget"))),
    assumptions = list(
      list(
        id = "browser-mapping",
        statement = "Browser controls were mapped to the canonical KH-NC-PA contract; equations remain conceptually related rather than numerically identical.",
        status = "declared"
      )
    ),
    metadata = list(
      description = "Migrated from the Catalyst Analytics R browser scenario input contract.",
      tags = c("browser", "compatibility"),
      created_by = "catalyst-analytics-r-demo",
      created_at = created_at,
      browser_contract_version = "1.0.0"
    )
  )
}

#' Convert a canonical scenario to browser demo inputs
#'
#' @param scenario Canonical KH-NC-PA scenario.
#' @return A browser-compatible named list.
#' @export
catalyst_scenario_to_browser <- function(scenario) {
  scenario <- as_catalyst_scenario(scenario)
  if (!identical(scenario$model$id, "khncpa")) {
    stop("Only KH-NC-PA scenarios can be mapped to the browser contract.", call. = FALSE)
  }
  if (!isTRUE(all.equal(scenario$time$start, 0, tolerance = 1e-12)) ||
      is.na(scenario$time$step) ||
      !isTRUE(all.equal(scenario$time$step, 1, tolerance = 1e-12))) {
    stop("Browser mapping requires an annual scenario beginning at time zero.", call. = FALSE)
  }
  get_value <- function(list_value, name, fallback) {
    if (is.null(list_value[[name]])) fallback else as.numeric(list_value[[name]])
  }
  list(
    scenarioName = scenario$title,
    years = as.integer(round(scenario$time$end - scenario$time$start)),
    savings = get_value(scenario$policy, "s", 0.20),
    emissionsIntensity = get_value(scenario$parameters, "emissions_intensity", 0.30),
    adaptation = get_value(scenario$policy, "a", 0),
    restoration = get_value(scenario$parameters, "regen", 0.02),
    humanInvestment = get_value(scenario$policy, "e", 0.05),
    initialCapital = get_value(scenario$initial_state, "K", 1),
    initialHuman = get_value(scenario$initial_state, "H", 1),
    initialNatural = get_value(scenario$initial_state, "N", 1),
    emissionsBudget = get_value(scenario$constraints, "emissions_budget", 120)
  )
}

.migrate_legacy_r_scenario <- function(x) {
  name <- if (!is.null(x$scenario_name)) x$scenario_name else if (!is.null(x$title)) x$title else "Migrated scenario"
  times <- if (!is.null(x$times)) unlist(x$times, use.names = FALSE) else seq(0, as.integer(x$years), by = 1)
  catalyst_scenario(
    title = as.character(.as_scalar(name, "scenario_name")),
    id = if (!is.null(x$id)) as.character(.as_scalar(x$id, "id")) else .slugify(as.character(.as_scalar(name, "scenario_name"))),
    model = if (!is.null(x$model)) as.character(.as_scalar(x$model, "model")) else "khncpa",
    model_version = "1.0.0",
    role = if (!is.null(x$role)) as.character(.as_scalar(x$role, "role")) else "exploratory",
    times = as.numeric(times),
    initial_state = unlist(x$x0, use.names = TRUE),
    policy = x$policy,
    parameters = if (is.null(x$params)) list() else x$params,
    constraints = if (is.null(x$constraints)) list() else x$constraints,
    metadata = list(
      description = "Migrated from Catalyst Analytics R scenario schema 0.1.0.",
      tags = "migration",
      created_by = "scenario-migrator",
      created_at = .utc_now(),
      migrations = "0.1.0->1.0.0"
    )
  )
}

#' Migrate a scenario to the current schema
#'
#' @param scenario Scenario list using the current schema, legacy R schema
#'   0.1.0, or legacy browser input contract.
#' @param target_version Target schema version. Currently only 1.0.0.
#' @return A current `catalyst_scenario`.
#' @export
migrate_catalyst_scenario <- function(scenario, target_version = "1.0.0") {
  .validate_semver(target_version, "target_version")
  if (!identical(target_version, .catalyst_scenario_schema_version())) {
    stop(sprintf("Unsupported target scenario schema version `%s`.", target_version), call. = FALSE)
  }
  if (inherits(scenario, "catalyst_scenario")) {
    validate_catalyst_scenario(scenario)
    return(scenario)
  }
  if (!is.list(scenario)) stop("`scenario` must be a list.", call. = FALSE)

  if (.is_browser_scenario(scenario)) return(browser_scenario_to_catalyst(scenario))
  version <- scenario$schema_version
  if (is.list(version) && length(version) == 1L) version <- version[[1L]]
  if (is.null(version)) stop("Scenario schema version is missing and no legacy contract was recognized.", call. = FALSE)
  version <- as.character(version)
  if (identical(version, "0.1.0")) return(.migrate_legacy_r_scenario(scenario))
  if (identical(version, "1.0.0")) {
    current <- .normalize_scenario(scenario)
    validate_catalyst_scenario(current)
    return(current)
  }
  stop(sprintf("No scenario migration path exists from `%s` to `%s`.", version, target_version), call. = FALSE)
}
