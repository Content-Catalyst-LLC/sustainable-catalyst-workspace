\name{regional_portfolio}
\alias{geography_scope}
\alias{validate_geography_scope}
\alias{sector_scope}
\alias{validate_sector_scope}
\alias{scope_scenario}
\alias{portfolio_member}
\alias{regional_portfolio}
\alias{validate_regional_portfolio}
\alias{portfolio_aggregate}
\alias{portfolio_compare_regions}
\alias{weighted_indicator_summary}
\alias{regional_carbon_budgets}
\alias{sector_transition_pathways}
\alias{regional_portfolio_analysis}
\alias{regional_portfolio_summary}
\alias{regional_portfolio_to_json}
\alias{regional_portfolio_from_json}
\alias{plot_portfolio_indicators}
\alias{plot_regional_carbon_budgets}
\alias{export_regional_portfolio_analysis}
\title{Regional, sector, and portfolio analytics}
\usage{
geography_scope(id, label, level = c("global", "region", "country", "subnational", "custom"), parent_id = NULL, codes = list(), metadata = list())
validate_geography_scope(x)
sector_scope(id, label, classification = "custom", code = NULL, parent_id = NULL, metadata = list())
validate_sector_scope(x)
scope_scenario(scenario, geography, sectors, id = NULL, title = NULL)
portfolio_member(id, title, geography, sectors, weight = 1, indicators = list(), carbon_budget = NULL, metadata = list())
regional_portfolio(portfolio_id, title, members, description = "", base_currency = "index", price_year = NA_integer_, metadata = list())
validate_regional_portfolio(portfolio)
portfolio_aggregate(portfolio)
portfolio_compare_regions(portfolio, indicator = NULL)
weighted_indicator_summary(data, value_col, weight_col, group_cols = character(), na_rm = FALSE)
regional_carbon_budgets(data, budgets, geography_col = "geography_id", time_col = "year", emissions_col = "net_emissions", budget_geography_col = "geography_id", budget_col = "carbon_budget", unit = "MtCO2e")
sector_transition_pathways(data, sector_col = "sector_id", time_col = "year", output_col = "output", emissions_col = "emissions", geography_col = NULL)
regional_portfolio_analysis(portfolio, carbon_budgets = NULL, sector_pathways = NULL)
regional_portfolio_summary(analysis)
regional_portfolio_to_json(portfolio, path, pretty = TRUE)
regional_portfolio_from_json(path)
plot_portfolio_indicators(analysis, indicator)
plot_regional_carbon_budgets(x)
export_regional_portfolio_analysis(analysis, dir, prefix = analysis$id, zip_bundle = TRUE, overwrite = FALSE, quiet = FALSE)
}
\arguments{
\item{id, portfolio_id}{Stable identifier.}
\item{label, title}{Human-readable label or title.}
\item{level}{Geography level.}
\item{parent_id}{Optional parent identifier.}
\item{codes}{External geography codes.}
\item{metadata}{Additional metadata.}
\item{x}{Scope or carbon-budget object.}
\item{classification, code}{Sector classification and code.}
\item{scenario}{Canonical scenario.}
\item{geography}{Geography scope.}
\item{sectors}{Sector scope or list of scopes.}
\item{weight}{Portfolio weight.}
\item{indicators}{Named indicator values or records.}
\item{carbon_budget}{Optional member carbon-budget allocation.}
\item{members}{Portfolio members.}
\item{description}{Portfolio description.}
\item{base_currency, price_year}{Valuation basis.}
\item{portfolio}{Regional portfolio.}
\item{indicator}{Optional indicator id.}
\item{data, budgets}{Input data frames.}
\item{value_col, weight_col, group_cols}{Weighted-summary columns.}
\item{na_rm}{Remove incomplete rows.}
\item{geography_col, time_col, emissions_col, budget_geography_col, budget_col, unit}{Regional budget fields and unit.}
\item{sector_col, output_col}{Sector pathway fields.}
\item{carbon_budgets}{Regional carbon-budget result.}
\item{sector_pathways}{Sector-transition result.}
\item{analysis}{Regional portfolio analysis.}
\item{path, pretty}{JSON destination and formatting.}
\item{dir, prefix, zip_bundle, overwrite, quiet}{Export controls.}
}
\value{Constructors return governed scope, member, portfolio, or analysis records. Summary functions return data frames or lists. Export functions return generated paths invisibly.}
\description{Provides governed geography and sector scopes, weighted regional portfolios, multi-region comparisons, carbon-budget pathways, sector transition diagnostics, visualization, JSON interchange, and portable publication bundles.}
