\name{composite_scores}
\alias{composite_scores}
\alias{composite_score_definition}
\alias{validate_composite_score_definition}
\alias{calculate_composite_score}
\alias{composite_weight_sensitivity}
\alias{composite_score_trace}
\alias{print.catalyst_composite_definition}
\alias{print.catalyst_composite_score}
\title{Governed Composite Scores}
\usage{
composite_score_definition(
  id,
  title,
  components,
  weights,
  directions = "higher",
  lower_bounds = 0,
  upper_bounds = 1,
  missing_policy = c("error", "renormalize", "zero"),
  metadata = list()
)

validate_composite_score_definition(definition)

calculate_composite_score(
  data,
  definition,
  entity_fields = character(),
  time_field = NULL
)

composite_weight_sensitivity(data, definition, weight_shift = 0.2)

composite_score_trace(result)

\method{print}{catalyst_composite_definition}(x, ...)

\method{print}{catalyst_composite_score}(x, ...)
}
\arguments{
  \item{id}{Stable score identifier.}
  \item{title}{Human-readable title.}
  \item{components}{Component column names.}
  \item{weights}{Non-negative component weights.}
  \item{directions}{One \code{higher} or \code{lower} direction per component.}
  \item{lower_bounds,upper_bounds}{Normalization ranges.}
  \item{missing_policy}{One of \code{error}, \code{renormalize}, or \code{zero}.}
  \item{metadata}{Additional definition metadata.}
  \item{definition}{A composite-score definition.}
  \item{data}{A data frame containing component values.}
  \item{entity_fields}{Optional identity columns retained in output.}
  \item{time_field}{Optional time column retained in output.}
  \item{weight_shift}{Proportional weight perturbation.}
  \item{result}{A calculated composite-score result.}
  \item{x}{A composite-score object.}
  \item{...}{Additional method arguments.}
}
\value{A transparent definition, calculated score, sensitivity table, or trace record.}
\description{Normalizes components against declared bounds, preserves directions and weights, calculates a 0-100 score, and tests sensitivity to weight choices.}
