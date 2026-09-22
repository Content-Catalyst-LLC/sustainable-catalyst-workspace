.catalyst_climate_accounting_schema_version <- function() "1.0.0"

.climate_terminal_values <- function(pathway, natural_capital = NULL) {
  carbon <- pathway$diagnostics
  rows <- list()
  for (i in seq_len(nrow(carbon))) {
    identity <- if (length(pathway$group_by)) carbon[i, pathway$group_by, drop = FALSE] else data.frame(scope = "all", stringsAsFactors = FALSE)
    records <- list(
      list(indicator = "cumulative_net_emissions", value = carbon$cumulative_net_emissions[i], unit = carbon$unit[i]),
      list(indicator = "remaining_carbon_budget", value = carbon$remaining_budget[i], unit = carbon$unit[i]),
      list(indicator = "terminal_net_emissions", value = carbon$terminal_net_emissions[i], unit = carbon$unit[i]),
      list(indicator = "carbon_lock_in_share", value = carbon$carbon_lock_in_share[i], unit = "fraction")
    )
    for (record in records) {
      row <- identity
      row$indicator <- record$indicator
      row$value <- record$value
      row$unit <- record$unit
      rows[[length(rows) + 1L]] <- row
    }
  }
  if (!is.null(natural_capital)) {
    summary <- natural_capital_summary(natural_capital)
    for (i in seq_len(nrow(summary))) {
      for (record in list(
        list(indicator = "natural_capital_closing_stock", value = summary$closing_stock[i]),
        list(indicator = "natural_capital_net_change", value = summary$net_change[i])
      )) {
        rows[[length(rows) + 1L]] <- data.frame(
          entity = summary$entity[i],
          indicator = record$indicator,
          value = record$value,
          unit = summary$unit[i],
          stringsAsFactors = FALSE
        )
      }
    }
  }
  result <- .rbind_fill_indicator_values(rows)
  rownames(result) <- NULL
  result
}

#' Assemble a governed climate and natural-capital accounting analysis
#'
#' @param inventory A governed emissions inventory.
#' @param budget Carbon budget supplied to [carbon_budget_pathway()].
#' @param natural_capital Optional `catalyst_natural_capital_account`.
#' @param boundaries Optional sustainability boundary definitions.
#' @param group_by Inventory fields defining carbon-budget groups.
#' @param target_year Optional net-zero or policy target year.
#' @param target_net_emissions Target net emissions at the target year.
#' @param include_kaya Run Kaya decomposition when required fields are available.
#' @param analysis_id Stable analysis identifier.
#' @param title Human-readable title.
#' @param metadata Additional metadata.
#' @return A `catalyst_climate_accounting` object.
#' @export
climate_accounting <- function(
  inventory,
  budget,
  natural_capital = NULL,
  boundaries = list(),
  group_by = inventory$entity_fields,
  target_year = NULL,
  target_net_emissions = 0,
  include_kaya = TRUE,
  analysis_id = paste0(inventory$dataset_id, "-climate-accounting"),
  title = "Climate, carbon, and natural-capital accounting",
  metadata = list()
) {
  validate_emissions_inventory(inventory)
  .assert_flag(include_kaya, "include_kaya")
  .validate_dataset_id(analysis_id, "analysis_id")
  .assert_single_string(title, "title")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  if (!is.null(natural_capital)) validate_natural_capital_account(natural_capital)
  pathway <- carbon_budget_pathway(
    inventory = inventory,
    budget = budget,
    group_by = group_by,
    target_year = target_year,
    target_net_emissions = target_net_emissions
  )
  kaya <- NULL
  if (include_kaya && all(c("population", "gdp", "energy") %in% names(inventory$data)) && all(inventory$data$gross_emissions > 0)) {
    kaya <- kaya_decomposition(inventory, group_by = group_by)
  }
  terminal_values <- .climate_terminal_values(pathway, natural_capital)
  assessment <- NULL
  if (inherits(boundaries, "catalyst_boundary_definition")) boundaries <- list(boundaries)
  if (length(boundaries)) {
    identity_fields <- setdiff(names(terminal_values), c("indicator", "value", "unit"))
    assessment <- evaluate_boundaries(terminal_values, boundaries, identity_fields = identity_fields)
  }

  structure(list(
    schema_version = .catalyst_climate_accounting_schema_version(),
    id = analysis_id,
    title = title,
    inventory = inventory,
    carbon_pathway = pathway,
    kaya = kaya,
    natural_capital = natural_capital,
    boundary_assessment = assessment,
    terminal_values = terminal_values,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      accounting_status = "analytical_review_required",
      causal_claim = FALSE,
      autonomous_decision = FALSE
    ), metadata)
  ), class = "catalyst_climate_accounting")
}

#' Summarize climate and natural-capital accounting
#'
#' @param analysis A `catalyst_climate_accounting`.
#' @return A list of emissions, carbon-budget, Kaya, natural-capital, and boundary summaries.
#' @export
climate_accounting_summary <- function(analysis) {
  if (!inherits(analysis, "catalyst_climate_accounting")) stop("`analysis` must be a climate-accounting object.", call. = FALSE)
  list(
    emissions = emissions_inventory_summary(analysis$inventory),
    carbon = carbon_pathway_summary(analysis$carbon_pathway),
    kaya = if (is.null(analysis$kaya)) NULL else analysis$kaya$contributions,
    natural_capital = if (is.null(analysis$natural_capital)) NULL else natural_capital_summary(analysis$natural_capital),
    boundaries = if (is.null(analysis$boundary_assessment)) NULL else analysis$boundary_assessment$assessment,
    terminal_values = analysis$terminal_values
  )
}

#' @export
print.catalyst_climate_accounting <- function(x, ...) {
  cat("<catalyst_climate_accounting>\n")
  cat("  id:               ", x$id, "\n", sep = "")
  cat("  carbon groups:    ", nrow(x$carbon_pathway$diagnostics), "\n", sep = "")
  cat("  Kaya decomposition:", if (is.null(x$kaya)) " no" else " yes", "\n", sep = "")
  cat("  natural capital:  ", if (is.null(x$natural_capital)) " no" else " yes", "\n", sep = "")
  invisible(x)
}
