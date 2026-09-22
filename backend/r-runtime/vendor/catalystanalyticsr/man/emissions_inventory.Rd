\name{emissions_inventory}
\alias{as_emissions_inventory}
\alias{validate_emissions_inventory}
\alias{emissions_inventory_manifest}
\alias{emissions_inventory_summary}
\alias{print.catalyst_emissions_inventory}
\title{Governed greenhouse-gas emissions inventories}
\usage{
as_emissions_inventory(
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
)

validate_emissions_inventory(inventory)

emissions_inventory_manifest(inventory, include_data = FALSE)

emissions_inventory_summary(inventory, group_by = inventory$entity_fields)

\method{print}{catalyst_emissions_inventory}(x, ...)
}
\arguments{
  \item{dataset}{A \code{catalyst_dataset}.}
  \item{emissions_field}{Numeric gross-emissions field.}
  \item{time_field}{Time field.}
  \item{entity_fields}{Entity-key fields.}
  \item{removals_field}{Optional non-negative removals or sequestration field.}
  \item{gas_field}{Optional greenhouse-gas category field.}
  \item{source_field}{Optional emissions-source category field.}
  \item{energy_field}{Optional positive energy-use field.}
  \item{gdp_field}{Optional positive economic-output field.}
  \item{population_field}{Optional positive population field.}
  \item{unit}{Emissions unit.}
  \item{accounting_basis}{Whether observations are period totals or rates.}
  \item{gwp_basis}{Global-warming-potential or CO2-equivalent basis statement.}
  \item{boundaries}{Named inventory boundary metadata.}
  \item{metadata}{Additional metadata.}
  \item{inventory}{A governed emissions inventory.}
  \item{include_data}{Include normalized records in the manifest.}
  \item{group_by}{Fields used to group inventory summaries.}
  \item{x}{An emissions inventory.}
  \item{...}{Additional print arguments.}
}
\value{
\code{as_emissions_inventory()} returns a \code{catalyst_emissions_inventory}.
Validation returns invisibly. Manifest and summary functions return machine-readable records.
}
\description{
Creates and validates normalized emissions inventories that preserve source,
unit, scope, gross emissions, removals, net emissions, and optional Kaya fields.
}
