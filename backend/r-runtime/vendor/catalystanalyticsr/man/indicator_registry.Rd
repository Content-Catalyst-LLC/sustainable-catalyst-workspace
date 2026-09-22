\name{indicator_registry}
\alias{new_catalyst_indicator}
\alias{validate_catalyst_indicator}
\alias{register_catalyst_indicator}
\alias{list_catalyst_indicators}
\alias{get_catalyst_indicator}
\alias{catalyst_indicator_manifest}
\alias{calculate_indicator}
\alias{calculate_indicators}
\alias{indicator_trace}
\alias{print.catalyst_indicator}
\alias{print.catalyst_indicator_result}
\alias{print.catalyst_indicator_set}
\title{Governed indicator definitions and calculations}
\usage{
new_catalyst_indicator(
  id,
  version,
  title,
  description,
  formula,
  required_fields,
  unit,
  direction = c("higher_better", "lower_better", "contextual"),
  aggregation = c("rowwise", "sum", "mean", "last_minus_first", "custom"),
  source = list(),
  calculation,
  targets = list(),
  metadata = list()
)

validate_catalyst_indicator(indicator)

register_catalyst_indicator(indicator, overwrite = FALSE)

list_catalyst_indicators()

get_catalyst_indicator(id, version = NULL)

catalyst_indicator_manifest(ids = NULL, versions = NULL)

calculate_indicator(
  dataset,
  indicator,
  version = NULL,
  group_by = character(),
  na_rm = FALSE
)

calculate_indicators(dataset, indicators, group_by = character(), na_rm = FALSE)

indicator_trace(result)

\method{print}{catalyst_indicator}(x, ...)

\method{print}{catalyst_indicator_result}(x, ...)

\method{print}{catalyst_indicator_set}(x, ...)
}
\arguments{
  \item{id}{Stable lowercase indicator identifier.}
  \item{version}{Semantic definition version.}
  \item{title}{Human-readable title.}
  \item{description}{Indicator interpretation.}
  \item{formula}{Human-readable formula.}
  \item{required_fields}{Required input fields.}
  \item{unit}{Output unit.}
  \item{direction}{Preferred direction or contextual status.}
  \item{aggregation}{Calculation behavior.}
  \item{source}{Methodology and source references.}
  \item{calculation}{Function accepting \code{data}, \code{dataset}, and \code{na_rm}.}
  \item{targets}{Optional target or threshold records.}
  \item{metadata}{Additional definition metadata.}
  \item{indicator}{Indicator id or definition.}
  \item{overwrite}{Replace an existing id/version registration.}
  \item{ids}{Optional indicator ids.}
  \item{versions}{Optional named versions keyed by id.}
  \item{dataset}{A \code{catalyst_dataset}.}
  \item{group_by}{Fields used for grouped aggregate calculations.}
  \item{na_rm}{Remove missing values in supported aggregates.}
  \item{indicators}{Indicator collection.}
  \item{result}{Indicator result or result set.}
  \item{x}{Object to print.}
  \item{...}{Additional print arguments.}
}
\value{
Definitions have class \code{catalyst_indicator}. Calculations return
\code{catalyst_indicator_result} or \code{catalyst_indicator_set} objects with
values and complete trace metadata.
}
\description{
Registers versioned indicator definitions and calculates them against governed
datasets while preserving formulas, fields, units, directions, sources,
versions, and calculation provenance.
}
