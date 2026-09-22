\name{distribution_analysis}
\alias{distribution_analysis}
\alias{distributional_analysis}
\alias{intergenerational_analysis}
\alias{print.catalyst_distribution_analysis}
\alias{print.catalyst_intergenerational_analysis}
\title{Distributional and Intergenerational Analysis}
\usage{
distributional_analysis(
  values,
  weights = NULL,
  groups = NULL,
  indicator = "distributed_value",
  unit = "index",
  higher_is_better = TRUE,
  social_floor = NULL,
  entity = "all",
  time = NULL
)

intergenerational_analysis(
  wealth,
  population,
  time,
  social_discount_rate = 0,
  generation_length = 25,
  target_per_capita = NULL,
  entity = "all"
)

\method{print}{catalyst_distribution_analysis}(x, ...)

\method{print}{catalyst_intergenerational_analysis}(x, ...)
}
\arguments{
  \item{values}{Finite non-negative observations.}
  \item{weights}{Optional positive population or survey weights.}
  \item{groups}{Optional group labels.}
  \item{indicator}{Indicator identifier.}
  \item{unit}{Unit for the distributed quantity.}
  \item{higher_is_better}{Whether larger values are preferred.}
  \item{social_floor}{Optional minimum acceptable value.}
  \item{entity}{Entity label.}
  \item{time}{Time label or ordered time vector.}
  \item{wealth}{Inclusive-wealth totals over time.}
  \item{population}{Positive population values over time.}
  \item{social_discount_rate}{Non-negative annual social discount rate.}
  \item{generation_length}{Positive number of years per generation.}
  \item{target_per_capita}{Optional target wealth per capita.}
  \item{x}{An analysis object.}
  \item{...}{Additional method arguments.}
}
\value{A governed distributional or intergenerational analysis object.}
\description{Reports weighted inequality, social-floor exposure, group shares, and changes in per-capita wealth across generations.}
