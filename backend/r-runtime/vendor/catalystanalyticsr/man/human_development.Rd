\name{human_development}
\alias{human_development}
\alias{adjusted_net_savings_decomposition}
\alias{human_development_indicators}
\title{Adjusted Net Savings and Human-Development Indicators}
\usage{
adjusted_net_savings_decomposition(
  gross_savings,
  produced_capital_depreciation = 0,
  education_investment = 0,
  health_investment = 0,
  natural_resource_depletion = 0,
  pollution_damages = 0,
  climate_damages = 0,
  other_adjustments = 0,
  gni = NULL,
  time = NULL,
  entity = NULL,
  unit = "currency_index"
)

human_development_indicators(
  life_expectancy,
  expected_schooling,
  mean_schooling,
  income_per_capita,
  time = NULL,
  entity = NULL,
  life_floor = 20,
  life_cap = 85,
  expected_schooling_cap = 18,
  mean_schooling_cap = 15,
  income_floor = 100,
  income_cap = 75000
)
}
\arguments{
  \item{gross_savings}{Gross national savings.}
  \item{produced_capital_depreciation}{Produced-capital depreciation.}
  \item{education_investment}{Education expenditure treated as human-capital investment.}
  \item{health_investment}{Health expenditure treated as human-capital investment.}
  \item{natural_resource_depletion}{Natural-resource depletion.}
  \item{pollution_damages}{Pollution damages.}
  \item{climate_damages}{Climate-related damages.}
  \item{other_adjustments}{Other signed adjustments.}
  \item{gni}{Optional gross national income.}
  \item{time}{Optional time labels.}
  \item{entity}{Optional entity labels.}
  \item{unit}{Monetary or index unit.}
  \item{life_expectancy}{Life expectancy in years.}
  \item{expected_schooling}{Expected years of schooling.}
  \item{mean_schooling}{Mean years of schooling.}
  \item{income_per_capita}{Positive income per capita.}
  \item{life_floor,life_cap}{Life-expectancy goalposts.}
  \item{expected_schooling_cap,mean_schooling_cap}{Schooling goalposts.}
  \item{income_floor,income_cap}{Income goalposts.}
}
\value{A data frame containing a transparent decomposition and calculated indicators.}
\description{Calculates Adjusted Net Savings and decomposed human-development indices with explicit goalposts.}
