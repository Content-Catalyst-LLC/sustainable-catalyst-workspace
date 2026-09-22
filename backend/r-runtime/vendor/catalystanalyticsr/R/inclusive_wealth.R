.catalyst_wealth_schema_version <- function() "1.0.0"

.recycle_wealth_numeric <- function(x, length_out, argument, default = 0, lower = -Inf) {
  if (is.null(x)) x <- default
  if (!is.numeric(x) || !length(x) || any(!is.finite(x))) {
    stop(sprintf("`%s` must contain finite numeric values.", argument), call. = FALSE)
  }
  if (!length(x) %in% c(1L, length_out)) {
    stop(sprintf("`%s` must have length 1 or %d.", argument, length_out), call. = FALSE)
  }
  value <- rep(as.numeric(x), length.out = length_out)
  if (any(value < lower)) stop(sprintf("`%s` cannot be below %s.", argument, lower), call. = FALSE)
  value
}

.recycle_wealth_label <- function(x, length_out, argument, default) {
  if (is.null(x)) x <- default
  if (!(is.atomic(x) || inherits(x, "Date")) || !length(x) || any(is.na(x))) {
    stop(sprintf("`%s` must contain non-missing values.", argument), call. = FALSE)
  }
  if (!length(x) %in% c(1L, length_out)) {
    stop(sprintf("`%s` must have length 1 or %d.", argument, length_out), call. = FALSE)
  }
  rep(x, length.out = length_out)
}

#' Capital and inclusive-wealth accounts
#'
#' Build reconciled produced-, human-, or natural-capital stock-and-flow accounts,
#' then combine them into an inclusive-wealth account with explicit shadow prices
#' and optional per-capita values.
#'
#' @param capital_type One of `produced`, `human`, or `natural`.
#' @param opening_stock Non-negative opening stock.
#' @param investment Non-negative additions or investment.
#' @param depreciation Non-negative depreciation.
#' @param depletion Non-negative depletion.
#' @param damages Non-negative damages or losses.
#' @param revaluation Finite positive or negative revaluation.
#' @param closing_stock Optional observed closing stock.
#' @param shadow_price Positive shadow price or valuation weight.
#' @param time Optional time labels.
#' @param entity Optional entity labels.
#' @param unit Stock unit.
#' @param account_id Stable account identifier.
#' @param title Human-readable title.
#' @param metadata Additional metadata.
#' @param account A capital account.
#' @param tolerance Maximum reconciliation error.
#' @param produced_capital A produced-capital account.
#' @param human_capital A human-capital account.
#' @param natural_capital A natural-capital account.
#' @param population Optional positive population values aligned to the accounts.
#' @param currency Currency or valuation index.
#' @param price_basis Price-year or valuation basis.
#' @param x An account object.
#' @param ... Additional arguments passed to methods.
#' @return A governed capital or inclusive-wealth account.
#' @name inclusive_wealth
NULL

#' @rdname inclusive_wealth
#' @export
capital_account <- function(
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
) {
  capital_type <- match.arg(capital_type)
  if (!is.numeric(opening_stock) || !length(opening_stock) || any(!is.finite(opening_stock)) || any(opening_stock < 0)) {
    stop("`opening_stock` must contain finite non-negative values.", call. = FALSE)
  }
  lengths <- c(
    length(opening_stock), length(investment), length(depreciation), length(depletion),
    length(damages), length(revaluation), if (is.null(closing_stock)) 1L else length(closing_stock),
    length(shadow_price), if (is.null(time)) 1L else length(time), if (is.null(entity)) 1L else length(entity)
  )
  n <- max(lengths)
  opening <- .recycle_wealth_numeric(opening_stock, n, "opening_stock", lower = 0)
  investment <- .recycle_wealth_numeric(investment, n, "investment", lower = 0)
  depreciation <- .recycle_wealth_numeric(depreciation, n, "depreciation", lower = 0)
  depletion <- .recycle_wealth_numeric(depletion, n, "depletion", lower = 0)
  damages <- .recycle_wealth_numeric(damages, n, "damages", lower = 0)
  revaluation <- .recycle_wealth_numeric(revaluation, n, "revaluation")
  shadow_price <- .recycle_wealth_numeric(shadow_price, n, "shadow_price", lower = .Machine$double.eps)
  expected <- opening + investment + revaluation - depreciation - depletion - damages
  if (any(expected < 0)) stop("Capital flows imply a negative closing stock.", call. = FALSE)
  observed <- if (is.null(closing_stock)) expected else .recycle_wealth_numeric(closing_stock, n, "closing_stock", lower = 0)
  time <- .recycle_wealth_label(time, n, "time", seq_len(n))
  entity <- as.character(.recycle_wealth_label(entity, n, "entity", "all"))
  .assert_single_string(unit, "unit")
  if (is.null(account_id)) account_id <- paste0(capital_type, "-capital")
  if (is.null(title)) title <- paste(tools::toTitleCase(capital_type), "capital account")
  .validate_dataset_id(account_id, "account_id")
  .assert_single_string(title, "title")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)

  data <- data.frame(
    entity = entity,
    time = time,
    capital_type = rep(capital_type, n),
    opening_stock = opening,
    investment = investment,
    revaluation = revaluation,
    depreciation = depreciation,
    depletion = depletion,
    damages = damages,
    expected_closing_stock = expected,
    closing_stock = observed,
    net_change = observed - opening,
    accounting_net_change = investment + revaluation - depreciation - depletion - damages,
    reconciliation_error = observed - expected,
    shadow_price = shadow_price,
    opening_value = opening * shadow_price,
    closing_value = observed * shadow_price,
    value_change = (observed - opening) * shadow_price,
    unit = rep(unit, n),
    stringsAsFactors = FALSE
  )

  structure(list(
    schema_version = .catalyst_wealth_schema_version(),
    account_type = "capital_stock_and_flow",
    id = account_id,
    title = title,
    capital_type = capital_type,
    unit = unit,
    data = data,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      row_count = n,
      reconciliation_tolerance = 1e-8,
      valuation_boundary = "shadow prices are declared analytical weights, not independently verified market values"
    ), metadata)
  ), class = "catalyst_capital_account")
}

#' @rdname inclusive_wealth
#' @export
validate_capital_account <- function(account, tolerance = 1e-8) {
  .assert_scalar_number(tolerance, "tolerance", lower = 0)
  if (!inherits(account, "catalyst_capital_account")) stop("`account` must be a capital account.", call. = FALSE)
  if (!identical(account$schema_version, .catalyst_wealth_schema_version())) stop("Unsupported capital-account schema.", call. = FALSE)
  required <- c(
    "entity", "time", "capital_type", "opening_stock", "investment", "revaluation",
    "depreciation", "depletion", "damages", "closing_stock", "reconciliation_error",
    "shadow_price", "opening_value", "closing_value"
  )
  if (!all(required %in% names(account$data))) stop("Capital account is incomplete.", call. = FALSE)
  if (any(account$data$opening_stock < 0) || any(account$data$closing_stock < 0)) stop("Capital stocks cannot be negative.", call. = FALSE)
  if (any(account$data$shadow_price <= 0)) stop("Shadow prices must be positive.", call. = FALSE)
  if (any(abs(account$data$reconciliation_error) > tolerance)) stop("Capital account does not reconcile within tolerance.", call. = FALSE)
  invisible(TRUE)
}

#' @rdname inclusive_wealth
#' @export
capital_account_summary <- function(account) {
  validate_capital_account(account)
  groups <- split(seq_len(nrow(account$data)), account$data$entity)
  do.call(rbind, lapply(groups, function(index) {
    data <- account$data[index, , drop = FALSE]
    data <- data[order(data$time), , drop = FALSE]
    data.frame(
      entity = data$entity[1L],
      capital_type = data$capital_type[1L],
      opening_stock = data$opening_stock[1L],
      closing_stock = data$closing_stock[nrow(data)],
      total_investment = sum(data$investment),
      total_depreciation = sum(data$depreciation),
      total_depletion = sum(data$depletion),
      total_damages = sum(data$damages),
      total_revaluation = sum(data$revaluation),
      stock_change = data$closing_stock[nrow(data)] - data$opening_stock[1L],
      opening_value = data$opening_value[1L],
      closing_value = data$closing_value[nrow(data)],
      value_change = data$closing_value[nrow(data)] - data$opening_value[1L],
      max_abs_reconciliation_error = max(abs(data$reconciliation_error)),
      unit = data$unit[1L],
      stringsAsFactors = FALSE
    )
  }))
}

#' @rdname inclusive_wealth
#' @export
inclusive_wealth_account <- function(
  produced_capital,
  human_capital,
  natural_capital,
  population = NULL,
  currency = "index",
  price_basis = "declared_shadow_prices",
  account_id = "inclusive-wealth",
  title = "Inclusive wealth account",
  metadata = list()
) {
  accounts <- list(produced = produced_capital, human = human_capital, natural = natural_capital)
  for (name in names(accounts)) {
    validate_capital_account(accounts[[name]])
    if (!identical(accounts[[name]]$capital_type, name)) {
      stop(sprintf("`%s_capital` must have capital type `%s`.", name, name), call. = FALSE)
    }
  }
  reference <- produced_capital$data
  for (name in c("human", "natural")) {
    candidate <- accounts[[name]]$data
    if (nrow(candidate) != nrow(reference) || !identical(as.character(candidate$entity), as.character(reference$entity)) || !identical(as.character(candidate$time), as.character(reference$time))) {
      stop("Capital accounts must have aligned entity and time rows.", call. = FALSE)
    }
  }
  n <- nrow(reference)
  population_values <- if (is.null(population)) rep(NA_real_, n) else .recycle_wealth_numeric(population, n, "population", lower = .Machine$double.eps)
  produced_value <- produced_capital$data$closing_value
  human_value <- human_capital$data$closing_value
  natural_value <- natural_capital$data$closing_value
  total <- produced_value + human_value + natural_value
  opening_total <- produced_capital$data$opening_value + human_capital$data$opening_value + natural_capital$data$opening_value
  data <- data.frame(
    entity = reference$entity,
    time = reference$time,
    produced_capital_value = produced_value,
    human_capital_value = human_value,
    natural_capital_value = natural_value,
    inclusive_wealth = total,
    opening_inclusive_wealth = opening_total,
    inclusive_wealth_change = total - opening_total,
    produced_share = ifelse(total == 0, NA_real_, produced_value / total),
    human_share = ifelse(total == 0, NA_real_, human_value / total),
    natural_share = ifelse(total == 0, NA_real_, natural_value / total),
    population = population_values,
    inclusive_wealth_per_capita = ifelse(is.na(population_values), NA_real_, total / population_values),
    currency = rep(currency, n),
    price_basis = rep(price_basis, n),
    stringsAsFactors = FALSE
  )
  .validate_dataset_id(account_id, "account_id")
  .assert_single_string(title, "title")
  .assert_single_string(currency, "currency")
  .assert_single_string(price_basis, "price_basis")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = .catalyst_wealth_schema_version(),
    account_type = "inclusive_wealth",
    id = account_id,
    title = title,
    capital_accounts = accounts,
    data = data,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      currency = currency,
      price_basis = price_basis,
      population_available = !all(is.na(population_values)),
      methodology = "inclusive wealth is the sum of produced, human, and natural capital valued with declared shadow prices"
    ), metadata)
  ), class = "catalyst_inclusive_wealth")
}

#' @rdname inclusive_wealth
#' @export
inclusive_wealth_summary <- function(account) {
  if (!inherits(account, "catalyst_inclusive_wealth")) stop("`account` must be an inclusive-wealth account.", call. = FALSE)
  groups <- split(seq_len(nrow(account$data)), account$data$entity)
  do.call(rbind, lapply(groups, function(index) {
    data <- account$data[index, , drop = FALSE]
    data <- data[order(data$time), , drop = FALSE]
    start <- data[1L, , drop = FALSE]
    end <- data[nrow(data), , drop = FALSE]
    data.frame(
      entity = start$entity,
      start_time = start$time,
      end_time = end$time,
      opening_inclusive_wealth = start$opening_inclusive_wealth,
      closing_inclusive_wealth = end$inclusive_wealth,
      absolute_change = end$inclusive_wealth - start$opening_inclusive_wealth,
      percent_change = ifelse(start$opening_inclusive_wealth == 0, NA_real_, 100 * (end$inclusive_wealth / start$opening_inclusive_wealth - 1)),
      closing_per_capita = end$inclusive_wealth_per_capita,
      produced_share = end$produced_share,
      human_share = end$human_share,
      natural_share = end$natural_share,
      stringsAsFactors = FALSE
    )
  }))
}

#' @rdname inclusive_wealth
#' @export
plot_inclusive_wealth <- function(account, per_capita = FALSE) {
  if (!inherits(account, "catalyst_inclusive_wealth")) stop("`account` must be an inclusive-wealth account.", call. = FALSE)
  .assert_flag(per_capita, "per_capita")
  measure <- if (per_capita) "inclusive_wealth_per_capita" else "inclusive_wealth"
  label <- if (per_capita) "Inclusive wealth per capita" else "Inclusive wealth"
  data <- account$data
  if (per_capita && all(is.na(data[[measure]]))) stop("Population is required for per-capita plotting.", call. = FALSE)
  ggplot2::ggplot(data, ggplot2::aes(x = time, y = .data[[measure]], group = entity)) +
    ggplot2::geom_line(linewidth = 0.9) +
    ggplot2::geom_point(size = 2) +
    ggplot2::facet_wrap(~entity, scales = "free_x") +
    ggplot2::labs(x = NULL, y = label, title = account$title) +
    theme_catalyst()
}

#' @rdname inclusive_wealth
#' @export
print.catalyst_capital_account <- function(x, ...) {
  cat(sprintf("<catalyst_capital_account %s>\n", x$id))
  cat(sprintf("  type: %s\n", x$capital_type))
  cat(sprintf("  rows: %d\n", nrow(x$data)))
  invisible(x)
}

#' @rdname inclusive_wealth
#' @export
print.catalyst_inclusive_wealth <- function(x, ...) {
  cat(sprintf("<catalyst_inclusive_wealth %s>\n", x$id))
  cat(sprintf("  rows: %d\n", nrow(x$data)))
  cat(sprintf("  price basis: %s\n", x$meta$price_basis))
  invisible(x)
}
