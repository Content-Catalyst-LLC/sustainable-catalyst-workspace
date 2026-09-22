\name{inclusive_development}
\alias{inclusive_development}
\alias{inclusive_development_analysis}
\alias{inclusive_development_summary}
\alias{plot_inclusive_development}
\alias{print.catalyst_inclusive_development}
\title{Inclusive Wealth, Human Development, and Distribution Analysis}
\usage{
inclusive_development_analysis(
  wealth,
  adjusted_net_savings = NULL,
  human_development = NULL,
  distribution = NULL,
  intergenerational = NULL,
  composite = NULL,
  analysis_id = "inclusive-development",
  title = "Inclusive wealth, human development, and distribution",
  metadata = list()
)

inclusive_development_summary(x)

plot_inclusive_development(x)

\method{print}{catalyst_inclusive_development}(x, ...)
}
\arguments{
  \item{wealth}{A \code{catalyst_inclusive_wealth} account.}
  \item{adjusted_net_savings}{Optional Adjusted Net Savings data frame.}
  \item{human_development}{Optional human-development data frame.}
  \item{distribution}{Optional distributional analysis.}
  \item{intergenerational}{Optional intergenerational analysis.}
  \item{composite}{Optional composite-score result.}
  \item{analysis_id}{Stable analysis identifier.}
  \item{title}{Human-readable title.}
  \item{metadata}{Additional metadata.}
  \item{x}{An inclusive-development analysis.}
  \item{...}{Additional method arguments.}
}
\value{A governed integrated analysis, summary, or plot.}
\description{Assembles capital accounts, Adjusted Net Savings, human development, distribution, intergenerational change, and composite-score evidence without hiding methodological choices.}
