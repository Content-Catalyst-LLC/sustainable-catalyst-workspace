\name{carbon_accounting}
\alias{carbon_budget_pathway}
\alias{carbon_pathway_summary}
\alias{kaya_decomposition}
\alias{plot_carbon_budget_pathway}
\alias{plot_kaya_decomposition}
\alias{print.catalyst_carbon_pathway}
\alias{print.catalyst_kaya_decomposition}
\title{Carbon-budget pathways and Kaya decomposition}
\usage{
carbon_budget_pathway(
  inventory,
  budget,
  group_by = inventory$entity_fields,
  target_year = NULL,
  target_net_emissions = 0
)

carbon_pathway_summary(pathway)

kaya_decomposition(
  inventory,
  group_by = inventory$entity_fields,
  baseline_time = NULL,
  comparison_time = NULL
)

plot_carbon_budget_pathway(pathway, facet = TRUE)

plot_kaya_decomposition(decomposition)

\method{print}{catalyst_carbon_pathway}(x, ...)

\method{print}{catalyst_kaya_decomposition}(x, ...)
}
\arguments{
  \item{inventory}{A governed emissions inventory.}
  \item{budget}{A non-negative scalar or named group budgets.}
  \item{group_by}{Inventory fields defining independent groups.}
  \item{target_year}{Optional policy or net-zero target time.}
  \item{target_net_emissions}{Target net emissions at the target time.}
  \item{pathway}{A \code{catalyst_carbon_pathway}.}
  \item{baseline_time}{Optional exact Kaya baseline time.}
  \item{comparison_time}{Optional exact Kaya comparison time.}
  \item{facet}{Facet carbon pathways by group.}
  \item{decomposition}{A \code{catalyst_kaya_decomposition}.}
  \item{x}{A carbon pathway or Kaya decomposition.}
  \item{...}{Additional print arguments.}
}
\value{
Carbon functions return a \code{catalyst_carbon_pathway}, group diagnostics,
or a ggplot object. Kaya functions return a \code{catalyst_kaya_decomposition}
or a ggplot object.
}
\description{
Calculates cumulative gross, removal, and net emissions, budget remaining,
overshoot and recovery timing, carbon lock-in signals, and additive LMDI Kaya
identity contributions.
}
