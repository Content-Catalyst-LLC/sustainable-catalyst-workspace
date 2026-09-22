if (getRversion() >= "2.15.1") utils::globalVariables(c(
  "x", "dx", "y", "dy", "xend", "yend",
  "value", "scenario", "param", "state", "t", "final_value", "scenario_id",
  "x_value", "y_value", "non_dominated", "absolute_delta",
  "cumulative_net_emissions", "carbon_budget", "group_label", "time_value",
  "factor", "contribution", "measure", "stock", "entity", "boundary_label",
  "normalized_distance", "status", "metric", "time", "capital_type",
  "opening_value", "closing_value", "inclusive_wealth", "inclusive_wealth_per_capita",
  "generation_index", "normalized_score", "weighted_contribution",
  "series", "predicted", "residual", "split", "method", "step",
  "max_absolute_terminal_error", "member_id", "geography_id", "remaining_budget"
))

#' Internal constants for catalystanalyticsr
#'
#' Returns stable package constants used by examples, validation, and release
#' checks. Most users will not need to call this function directly.
#'
#' @param dummy Unused; retained for backwards compatibility.
#' @return A named list of internal constants.
#' @keywords internal
#' @export
#'
#' @examples
#' catalyst_globals()
catalyst_globals <- function(dummy = NULL) {
  list(
    required_state_names = c("K", "H", "N", "C", "P", "A"),
    required_traj_long_cols = c("t", "scenario", "metric", "value"),
    model_id = "khncpa",
    model_contract_version = "1.0.0",
    scenario_schema_version = "1.0.0",
    comparison_schema_version = "1.0.0",
    uncertainty_schema_version = "1.0.0",
    dataset_schema_version = "1.0.0",
    indicator_schema_version = "1.0.0",
    emissions_inventory_schema_version = "1.0.0",
    climate_accounting_schema_version = "1.0.0",
    natural_capital_schema_version = "1.0.0",
    boundary_schema_version = "1.0.0",
    wealth_schema_version = "1.0.0",
    human_development_schema_version = "1.0.0",
    distribution_schema_version = "1.0.0",
    composite_score_schema_version = "1.0.0",
    inclusive_development_schema_version = "1.0.0",
    calibration_schema_version = "1.0.0",
    model_validation_schema_version = "1.0.0",
    model_governance_schema_version = "1.0.0",
    regional_portfolio_schema_version = "1.0.0",
    regional_portfolio_analysis_schema_version = "1.0.0",
    econometric_evaluation_schema_version = "1.0.0",
    policy_evaluation_schema_version = "1.0.0",
    demo_export_schema_version = "2.4.0"
  )
}

utils::globalVariables(c("sample_id", "median", "p10", "p90", "estimate", "target", "absolute_effect"))

utils::globalVariables(c("evaluation_id", "effect", "conf_low", "conf_high", "label", "period", "time", "gap"))
