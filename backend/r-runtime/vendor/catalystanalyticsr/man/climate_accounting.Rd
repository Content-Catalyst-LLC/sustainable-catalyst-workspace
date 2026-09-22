\name{climate_accounting}
\alias{climate_accounting}
\alias{climate_accounting_summary}
\alias{print.catalyst_climate_accounting}
\title{Governed climate and natural-capital accounting analysis}
\usage{
climate_accounting(
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
)

climate_accounting_summary(analysis)

\method{print}{catalyst_climate_accounting}(x, ...)
}
\arguments{
  \item{inventory}{A governed emissions inventory.}
  \item{budget}{Carbon budget supplied to the pathway calculation.}
  \item{natural_capital}{Optional natural-capital account.}
  \item{boundaries}{Optional sustainability boundary definitions.}
  \item{group_by}{Inventory fields defining carbon-budget groups.}
  \item{target_year}{Optional policy target time.}
  \item{target_net_emissions}{Target net emissions.}
  \item{include_kaya}{Run Kaya decomposition when required fields are available.}
  \item{analysis_id}{Stable analysis identifier.}
  \item{title}{Human-readable title.}
  \item{metadata}{Additional metadata.}
  \item{analysis}{A climate-accounting analysis.}
  \item{x}{A climate-accounting analysis.}
  \item{...}{Additional print arguments.}
}
\value{
A \code{catalyst_climate_accounting} object, a list of summary tables, or the
input object invisibly for printing.
}
\description{
Assembles emissions inventory, carbon-budget pathway, Kaya decomposition,
natural-capital account, boundary assessment, terminal indicators, and review
metadata into one governed analytical record.
}
