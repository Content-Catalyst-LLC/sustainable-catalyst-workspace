\name{inclusive_wealth}
\alias{inclusive_wealth}
\alias{capital_account}
\alias{validate_capital_account}
\alias{capital_account_summary}
\alias{inclusive_wealth_account}
\alias{inclusive_wealth_summary}
\alias{plot_inclusive_wealth}
\alias{print.catalyst_capital_account}
\alias{print.catalyst_inclusive_wealth}
\title{Capital and Inclusive-Wealth Accounts}
\usage{
capital_account(
  capital_type = c("produced", "human", "natural"),
  opening_stock,
  investment = 0,
  depreciation = 0,
  depletion = 0,
  damages = 0,
  revaluation = 0,
  closing_stock = NULL,
  shadow_price = 1,
  time = NULL,
  entity = NULL,
  unit = "stock_index",
  account_id = NULL,
  title = NULL,
  metadata = list()
)

validate_capital_account(account, tolerance = 1e-08)

capital_account_summary(account)

inclusive_wealth_account(
  produced_capital,
  human_capital,
  natural_capital,
  population = NULL,
  currency = "index",
  price_basis = "declared_shadow_prices",
  account_id = "inclusive-wealth",
  title = "Inclusive wealth account",
  metadata = list()
)

inclusive_wealth_summary(account)

plot_inclusive_wealth(account, per_capita = FALSE)

\method{print}{catalyst_capital_account}(x, ...)

\method{print}{catalyst_inclusive_wealth}(x, ...)
}
\arguments{
  \item{capital_type}{One of \code{produced}, \code{human}, or \code{natural}.}
  \item{opening_stock}{Finite non-negative opening stocks.}
  \item{investment}{Non-negative additions or investment.}
  \item{depreciation}{Non-negative depreciation.}
  \item{depletion}{Non-negative depletion.}
  \item{damages}{Non-negative damages or losses.}
  \item{revaluation}{Signed revaluation adjustments.}
  \item{closing_stock}{Optional observed closing stocks.}
  \item{shadow_price}{Positive valuation weight or shadow price.}
  \item{time}{Optional time labels.}
  \item{entity}{Optional entity labels.}
  \item{unit}{Stock unit.}
  \item{account_id}{Stable account identifier.}
  \item{title}{Human-readable title.}
  \item{metadata}{Additional metadata.}
  \item{account}{A capital or inclusive-wealth account.}
  \item{tolerance}{Maximum absolute reconciliation error.}
  \item{produced_capital}{A produced-capital account.}
  \item{human_capital}{A human-capital account.}
  \item{natural_capital}{A natural-capital account.}
  \item{population}{Optional positive population aligned with account rows.}
  \item{currency}{Currency or valuation index.}
  \item{price_basis}{Price year or valuation basis.}
  \item{per_capita}{Whether to plot per-capita wealth.}
  \item{x}{An account object.}
  \item{...}{Additional method arguments.}
}
\value{A governed capital account, inclusive-wealth account, summary, or plot.}
\description{Reconciles produced-, human-, and natural-capital stocks and flows and combines their declared values into an inclusive-wealth account.}
\details{Shadow prices are explicit analytical weights. They are not independently verified market prices and require methodological review.}
