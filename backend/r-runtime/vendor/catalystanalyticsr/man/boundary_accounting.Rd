\name{boundary_accounting}
\alias{boundary_definition}
\alias{validate_boundary_definition}
\alias{evaluate_boundaries}
\alias{boundary_summary}
\alias{plot_boundary_status}
\alias{print.catalyst_boundary_definition}
\alias{print.catalyst_boundary_assessment}
\title{Sustainability boundary definitions and assessment}
\usage{
boundary_definition(
  id,
  title,
  indicator,
  unit,
  direction = c("at_or_below", "at_or_above", "inside_range"),
  lower = NULL,
  upper = NULL,
  warning_margin = 0.1,
  source = list(),
  metadata = list()
)

validate_boundary_definition(boundary)

evaluate_boundaries(
  values,
  boundaries,
  indicator_field = "indicator",
  value_field = "value",
  unit_field = "unit",
  identity_fields = character()
)

boundary_summary(assessment)

plot_boundary_status(assessment)

\method{print}{catalyst_boundary_definition}(x, ...)

\method{print}{catalyst_boundary_assessment}(x, ...)
}
\arguments{
  \item{id}{Stable boundary identifier.}
  \item{title}{Human-readable title.}
  \item{indicator}{Indicator identifier.}
  \item{unit}{Expected unit.}
  \item{direction}{Admissible-side or range definition.}
  \item{lower}{Optional lower bound.}
  \item{upper}{Optional upper bound.}
  \item{warning_margin}{Fraction of the admissible scale used for warning status.}
  \item{source}{Methodology or evidence source record.}
  \item{metadata}{Additional metadata.}
  \item{boundary}{A boundary definition.}
  \item{values}{Data frame containing indicator and value fields.}
  \item{boundaries}{One or more boundary definitions.}
  \item{indicator_field}{Indicator-id field.}
  \item{value_field}{Numeric value field.}
  \item{unit_field}{Optional unit field.}
  \item{identity_fields}{Fields retained in output records.}
  \item{assessment}{A boundary assessment.}
  \item{x}{A boundary definition or assessment.}
  \item{...}{Additional print arguments.}
}
\value{
A boundary definition, validation result, \code{catalyst_boundary_assessment},
summary table, or ggplot object.
}
\description{
Evaluates governed indicator values against at-or-below, at-or-above, or
inside-range sustainability boundaries with warning margins and unit checks.
}
