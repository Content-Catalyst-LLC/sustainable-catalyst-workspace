.catalyst_emissions_inventory_schema_version <- function() "1.0.0"

.validate_field_reference <- function(field, data, argument, allow_null = FALSE) {
  if (is.null(field) && allow_null) return(invisible(NULL))
  .assert_single_string(field, argument)
  if (!field %in% names(data)) {
    stop(sprintf("`%s` references missing field `%s`.", argument, field), call. = FALSE)
  }
  invisible(field)
}

.numeric_inventory_field <- function(data, field, argument, allow_null = FALSE, nonnegative = FALSE, positive = FALSE) {
  if (is.null(field) && allow_null) return(NULL)
  .validate_field_reference(field, data, argument)
  values <- data[[field]]
  if (!is.numeric(values)) stop(sprintf("Field `%s` must be numeric.", field), call. = FALSE)
  if (any(!is.finite(values))) stop(sprintf("Field `%s` must contain finite values.", field), call. = FALSE)
  if (nonnegative && any(values < 0)) stop(sprintf("Field `%s` cannot contain negative values.", field), call. = FALSE)
  if (positive && any(values <= 0)) stop(sprintf("Field `%s` must contain positive values.", field), call. = FALSE)
  as.numeric(values)
}

#' Create a governed emissions inventory
#'
#' Converts a documented Catalyst dataset into a normalized inventory containing
#' gross emissions, removals, net emissions, time and entity keys, optional gas
#' and source categories, and optional Kaya identity fields.
#'
#' @param dataset A `catalyst_dataset`.
#' @param emissions_field Numeric gross-emissions field.
#' @param time_field Time field. Defaults to the dataset time field.
#' @param entity_fields Entity-key fields. Defaults to the dataset entity fields.
#' @param removals_field Optional non-negative removals or sequestration field.
#' @param gas_field Optional greenhouse-gas category field.
#' @param source_field Optional emissions-source category field.
#' @param energy_field Optional positive energy-use field for Kaya decomposition.
#' @param gdp_field Optional positive economic-output field for Kaya decomposition.
#' @param population_field Optional positive population field for Kaya decomposition.
#' @param unit Emissions unit. Defaults to the source dataset unit.
#' @param accounting_basis Either `period_total` or `rate`.
#' @param gwp_basis Global-warming-potential or CO2-equivalent basis statement.
#' @param boundaries Named organizational, geographic, sector, and temporal boundaries.
#' @param metadata Additional inventory metadata.
#' @return A `catalyst_emissions_inventory`.
#' @export
as_emissions_inventory <- function(
  dataset,
  emissions_field,
  time_field = dataset$time_field,
  entity_fields = dataset$entity_fields,
  removals_field = NULL,
  gas_field = NULL,
  source_field = NULL,
  energy_field = NULL,
  gdp_field = NULL,
  population_field = NULL,
  unit = NULL,
  accounting_basis = c("period_total", "rate"),
  gwp_basis = "CO2e as reported by source",
  boundaries = list(),
  metadata = list()
) {
  validate_catalyst_dataset(dataset)
  accounting_basis <- match.arg(accounting_basis)
  .validate_field_reference(emissions_field, dataset$data, "emissions_field")
  .validate_field_reference(time_field, dataset$data, "time_field")
  if (!is.character(entity_fields) || any(!entity_fields %in% names(dataset$data)) || anyDuplicated(entity_fields)) {
    stop("`entity_fields` must contain unique dataset fields.", call. = FALSE)
  }
  for (entry in list(
    removals_field = removals_field,
    gas_field = gas_field,
    source_field = source_field,
    energy_field = energy_field,
    gdp_field = gdp_field,
    population_field = population_field
  )) {
    if (!is.null(entry)) .validate_field_reference(entry, dataset$data, "optional field", allow_null = TRUE)
  }
  if (!is.list(boundaries)) stop("`boundaries` must be a list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  .assert_single_string(gwp_basis, "gwp_basis")

  gross <- .numeric_inventory_field(dataset$data, emissions_field, "emissions_field", nonnegative = TRUE)
  removals <- if (is.null(removals_field)) rep(0, length(gross)) else {
    .numeric_inventory_field(dataset$data, removals_field, "removals_field", nonnegative = TRUE)
  }
  energy <- .numeric_inventory_field(dataset$data, energy_field, "energy_field", allow_null = TRUE, positive = TRUE)
  gdp <- .numeric_inventory_field(dataset$data, gdp_field, "gdp_field", allow_null = TRUE, positive = TRUE)
  population <- .numeric_inventory_field(dataset$data, population_field, "population_field", allow_null = TRUE, positive = TRUE)

  if (is.null(unit)) unit <- dataset$units[[emissions_field]]
  if (is.null(unit) || !nzchar(as.character(unit))) unit <- "tCO2e"
  .assert_single_string(as.character(unit), "unit")

  identity_fields <- unique(c(entity_fields, time_field))
  normalized <- dataset$data[identity_fields]
  normalized$gross_emissions <- gross
  normalized$removals <- removals
  normalized$net_emissions <- gross - removals
  normalized$gas <- if (is.null(gas_field)) rep("CO2e", nrow(normalized)) else as.character(dataset$data[[gas_field]])
  normalized$source_category <- if (is.null(source_field)) rep("total", nrow(normalized)) else as.character(dataset$data[[source_field]])
  if (!is.null(energy)) normalized$energy <- energy
  if (!is.null(gdp)) normalized$gdp <- gdp
  if (!is.null(population)) normalized$population <- population

  group_indices <- .bind_indicator_groups(normalized, entity_fields)
  ordered <- vapply(group_indices, function(index) !is.unsorted(normalized[[time_field]][index], na.rm = TRUE), logical(1))
  if (!all(ordered)) stop("Inventory time values must be ordered within each entity group.", call. = FALSE)

  structure(list(
    schema_version = .catalyst_emissions_inventory_schema_version(),
    id = paste0(dataset$id, "-emissions-inventory"),
    title = paste(dataset$title, "emissions inventory"),
    dataset_id = dataset$id,
    dataset_fingerprint = dataset_fingerprint(dataset),
    data = normalized,
    time_field = time_field,
    entity_fields = unname(entity_fields),
    mappings = list(
      emissions = emissions_field,
      removals = removals_field,
      gas = gas_field,
      source = source_field,
      energy = energy_field,
      gdp = gdp_field,
      population = population_field
    ),
    unit = as.character(unit),
    accounting_basis = accounting_basis,
    gwp_basis = gwp_basis,
    boundaries = boundaries,
    source = dataset$source,
    metadata = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      row_count = nrow(normalized),
      gross_total = sum(gross),
      removals_total = sum(removals),
      net_total = sum(gross - removals)
    ), metadata)
  ), class = "catalyst_emissions_inventory")
}

#' Validate a governed emissions inventory
#'
#' @param inventory A `catalyst_emissions_inventory`.
#' @return Invisibly returns TRUE when valid.
#' @export
validate_emissions_inventory <- function(inventory) {
  if (!inherits(inventory, "catalyst_emissions_inventory")) {
    stop("`inventory` must inherit from `catalyst_emissions_inventory`.", call. = FALSE)
  }
  required <- c("schema_version", "id", "dataset_id", "data", "time_field", "entity_fields", "unit", "accounting_basis", "source")
  if (!all(required %in% names(inventory))) stop("Emissions inventory is incomplete.", call. = FALSE)
  if (!identical(inventory$schema_version, .catalyst_emissions_inventory_schema_version())) stop("Unsupported emissions-inventory schema version.", call. = FALSE)
  if (!is.data.frame(inventory$data)) stop("Inventory data must remain a data frame.", call. = FALSE)
  expected <- c(inventory$entity_fields, inventory$time_field, "gross_emissions", "removals", "net_emissions", "gas", "source_category")
  if (!all(expected %in% names(inventory$data))) stop("Inventory data is missing normalized accounting fields.", call. = FALSE)
  if (any(inventory$data$gross_emissions < 0) || any(inventory$data$removals < 0)) stop("Gross emissions and removals cannot be negative.", call. = FALSE)
  if (!isTRUE(all.equal(inventory$data$net_emissions, inventory$data$gross_emissions - inventory$data$removals, tolerance = 1e-10))) {
    stop("Net emissions do not reconcile to gross emissions less removals.", call. = FALSE)
  }
  invisible(TRUE)
}

.emissions_inventory_record <- function(inventory, include_data = TRUE) {
  validate_emissions_inventory(inventory)
  list(
    schema_version = inventory$schema_version,
    id = inventory$id,
    title = inventory$title,
    dataset_id = inventory$dataset_id,
    dataset_fingerprint = inventory$dataset_fingerprint,
    time_field = inventory$time_field,
    entity_fields = unname(inventory$entity_fields),
    mappings = inventory$mappings,
    unit = inventory$unit,
    accounting_basis = inventory$accounting_basis,
    gwp_basis = inventory$gwp_basis,
    boundaries = inventory$boundaries,
    source = inventory$source,
    metadata = inventory$metadata,
    data = if (include_data) inventory$data else NULL
  )
}

#' Return an emissions-inventory manifest
#'
#' @param inventory A governed emissions inventory.
#' @param include_data Include normalized records.
#' @return A machine-readable inventory record.
#' @export
emissions_inventory_manifest <- function(inventory, include_data = FALSE) {
  .assert_flag(include_data, "include_data")
  .emissions_inventory_record(inventory, include_data = include_data)
}

#' Summarize gross, removal, and net emissions
#'
#' @param inventory A governed emissions inventory.
#' @param group_by Optional grouping fields from the normalized inventory.
#' @return A data frame of emissions totals and removal shares.
#' @export
emissions_inventory_summary <- function(inventory, group_by = inventory$entity_fields) {
  validate_emissions_inventory(inventory)
  if (!is.character(group_by) || any(!group_by %in% names(inventory$data)) || anyDuplicated(group_by)) {
    stop("`group_by` must contain unique inventory fields.", call. = FALSE)
  }
  groups <- .bind_indicator_groups(inventory$data, group_by)
  rows <- lapply(groups, function(index) {
    data <- inventory$data[index, , drop = FALSE]
    row <- if (length(group_by)) data[1L, group_by, drop = FALSE] else data.frame(scope = "inventory", stringsAsFactors = FALSE)
    row$gross_emissions <- sum(data$gross_emissions)
    row$removals <- sum(data$removals)
    row$net_emissions <- sum(data$net_emissions)
    row$removal_share <- if (row$gross_emissions == 0) 0 else row$removals / row$gross_emissions
    row$unit <- inventory$unit
    row
  })
  result <- do.call(rbind, rows)
  rownames(result) <- NULL
  result
}

#' @export
print.catalyst_emissions_inventory <- function(x, ...) {
  cat("<catalyst_emissions_inventory>\n")
  cat("  id:       ", x$id, "\n", sep = "")
  cat("  rows:     ", nrow(x$data), "\n", sep = "")
  cat("  unit:     ", x$unit, "\n", sep = "")
  cat("  net total:", format(sum(x$data$net_emissions), trim = TRUE), "\n")
  invisible(x)
}
