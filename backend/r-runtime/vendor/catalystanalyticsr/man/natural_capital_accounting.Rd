\name{natural_capital_accounting}
\alias{natural_capital_account}
\alias{natural_capital_from_dataset}
\alias{validate_natural_capital_account}
\alias{natural_capital_summary}
\alias{plot_natural_capital_account}
\alias{print.catalyst_natural_capital_account}
\title{Natural-capital stock-and-flow accounting}
\usage{
natural_capital_account(
  opening_stock,
  regeneration = 0,
  restoration = 0,
  additions = 0,
  extraction = 0,
  degradation = 0,
  damages = 0,
  closing_stock = NULL,
  time = NULL,
  entity = NULL,
  unit = "index",
  account_id = "natural-capital",
  title = "Natural capital account",
  metadata = list()
)

natural_capital_from_dataset(
  dataset,
  opening_field,
  regeneration_field = NULL,
  restoration_field = NULL,
  additions_field = NULL,
  extraction_field = NULL,
  degradation_field = NULL,
  damages_field = NULL,
  closing_field = NULL,
  time_field = dataset$time_field,
  entity_field = if (length(dataset$entity_fields)) dataset$entity_fields[1L] else NULL,
  unit = NULL,
  account_id = paste0(dataset$id, "-natural-capital"),
  title = paste(dataset$title, "natural capital account")
)

validate_natural_capital_account(account, tolerance = 1e-08)

natural_capital_summary(account)

plot_natural_capital_account(account)

\method{print}{catalyst_natural_capital_account}(x, ...)
}
\arguments{
  \item{opening_stock}{Non-negative opening stock.}
  \item{regeneration}{Non-negative natural regeneration.}
  \item{restoration}{Non-negative managed restoration.}
  \item{additions}{Other non-negative additions or discoveries.}
  \item{extraction}{Non-negative extraction or depletion.}
  \item{degradation}{Non-negative degradation.}
  \item{damages}{Non-negative damages or losses.}
  \item{closing_stock}{Optional observed closing stock.}
  \item{time}{Optional time labels.}
  \item{entity}{Optional entity labels.}
  \item{unit}{Stock and flow unit.}
  \item{account_id}{Stable account identifier.}
  \item{title}{Human-readable account title.}
  \item{metadata}{Additional metadata.}
  \item{dataset}{A governed Catalyst dataset.}
  \item{opening_field}{Opening-stock field.}
  \item{regeneration_field}{Optional regeneration field.}
  \item{restoration_field}{Optional restoration field.}
  \item{additions_field}{Optional additions field.}
  \item{extraction_field}{Optional extraction field.}
  \item{degradation_field}{Optional degradation field.}
  \item{damages_field}{Optional damages field.}
  \item{closing_field}{Optional observed closing-stock field.}
  \item{time_field}{Optional time field.}
  \item{entity_field}{Optional entity field.}
  \item{account}{A natural-capital account.}
  \item{tolerance}{Maximum absolute reconciliation error.}
  \item{x}{A natural-capital account.}
  \item{...}{Additional print arguments.}
}
\value{
A \code{catalyst_natural_capital_account}, validation result, summary data frame,
or ggplot object.
}
\description{
Reconciles opening stocks with regeneration, restoration, additions,
extraction, degradation, damages, and observed or calculated closing stocks.
}
