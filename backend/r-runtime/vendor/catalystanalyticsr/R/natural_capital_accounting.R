.catalyst_natural_capital_schema_version <- function() "1.0.0"

.recycle_account_vector <- function(x, length_out, argument, default = 0) {
  if (is.null(x)) x <- default
  if (!is.numeric(x) || !length(x) || any(!is.finite(x))) {
    stop(sprintf("`%s` must contain finite numeric values.", argument), call. = FALSE)
  }
  if (!length(x) %in% c(1L, length_out)) {
    stop(sprintf("`%s` must have length 1 or %d.", argument, length_out), call. = FALSE)
  }
  rep(as.numeric(x), length.out = length_out)
}

.recycle_account_label <- function(x, length_out, argument, default) {
  if (is.null(x)) x <- default
  if (!(is.atomic(x) || inherits(x, "Date")) || !length(x) || any(is.na(x))) {
    stop(sprintf("`%s` must contain non-missing values.", argument), call. = FALSE)
  }
  if (!length(x) %in% c(1L, length_out)) {
    stop(sprintf("`%s` must have length 1 or %d.", argument, length_out), call. = FALSE)
  }
  rep(x, length.out = length_out)
}

#' Create a natural-capital stock-and-flow account
#'
#' Reconciles opening stocks, regeneration, restoration, additions, extraction,
#' degradation, damages, and observed or calculated closing stocks.
#'
#' @param opening_stock Non-negative opening natural-capital stock.
#' @param regeneration Non-negative natural regeneration flow.
#' @param restoration Non-negative managed restoration flow.
#' @param additions Other non-negative additions or discoveries.
#' @param extraction Non-negative extraction or depletion flow.
#' @param degradation Non-negative degradation flow.
#' @param damages Non-negative damage or loss flow.
#' @param closing_stock Optional observed non-negative closing stock.
#' @param time Optional time labels.
#' @param entity Optional entity labels.
#' @param unit Stock and flow unit.
#' @param account_id Stable account identifier.
#' @param title Human-readable account title.
#' @param metadata Additional account metadata.
#' @return A `catalyst_natural_capital_account`.
#' @export
natural_capital_account <- function(
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
) {
  if (!is.numeric(opening_stock) || !length(opening_stock) || any(!is.finite(opening_stock)) || any(opening_stock < 0)) {
    stop("`opening_stock` must contain finite non-negative values.", call. = FALSE)
  }
  n <- max(length(opening_stock), length(regeneration), length(restoration), length(additions), length(extraction), length(degradation), length(damages), if (is.null(closing_stock)) 1L else length(closing_stock), if (is.null(time)) 1L else length(time), if (is.null(entity)) 1L else length(entity))
  opening <- .recycle_account_vector(opening_stock, n, "opening_stock")
  regeneration <- .recycle_account_vector(regeneration, n, "regeneration")
  restoration <- .recycle_account_vector(restoration, n, "restoration")
  additions <- .recycle_account_vector(additions, n, "additions")
  extraction <- .recycle_account_vector(extraction, n, "extraction")
  degradation <- .recycle_account_vector(degradation, n, "degradation")
  damages <- .recycle_account_vector(damages, n, "damages")
  flow_values <- c(regeneration, restoration, additions, extraction, degradation, damages)
  if (any(flow_values < 0)) stop("Natural-capital flows cannot be negative.", call. = FALSE)
  expected_closing <- opening + regeneration + restoration + additions - extraction - degradation - damages
  if (any(expected_closing < 0)) stop("Natural-capital flows imply a negative closing stock.", call. = FALSE)
  observed_closing <- if (is.null(closing_stock)) expected_closing else .recycle_account_vector(closing_stock, n, "closing_stock")
  if (any(observed_closing < 0)) stop("`closing_stock` cannot be negative.", call. = FALSE)
  time <- .recycle_account_label(time, n, "time", seq_len(n))
  entity <- as.character(.recycle_account_label(entity, n, "entity", "all"))
  .assert_single_string(unit, "unit")
  .validate_dataset_id(account_id, "account_id")
  .assert_single_string(title, "title")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)

  data <- data.frame(
    entity = entity,
    time = time,
    opening_stock = opening,
    regeneration = regeneration,
    restoration = restoration,
    additions = additions,
    extraction = extraction,
    degradation = degradation,
    damages = damages,
    expected_closing_stock = expected_closing,
    closing_stock = observed_closing,
    net_change = observed_closing - opening,
    accounting_net_change = regeneration + restoration + additions - extraction - degradation - damages,
    reconciliation_error = observed_closing - expected_closing,
    unit = rep(unit, n),
    stringsAsFactors = FALSE
  )

  structure(list(
    schema_version = .catalyst_natural_capital_schema_version(),
    id = account_id,
    title = title,
    data = data,
    unit = unit,
    meta = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      row_count = n,
      reconciliation_tolerance = 1e-8
    ), metadata)
  ), class = "catalyst_natural_capital_account")
}

#' Build a natural-capital account from a Catalyst dataset
#'
#' @param dataset A governed Catalyst dataset.
#' @param opening_field Opening-stock field.
#' @param regeneration_field Optional regeneration field.
#' @param restoration_field Optional restoration field.
#' @param additions_field Optional additions field.
#' @param extraction_field Optional extraction field.
#' @param degradation_field Optional degradation field.
#' @param damages_field Optional damages field.
#' @param closing_field Optional observed closing-stock field.
#' @param time_field Optional time field.
#' @param entity_field Optional entity field.
#' @param unit Optional account unit.
#' @param account_id Stable account identifier.
#' @param title Account title.
#' @return A `catalyst_natural_capital_account`.
#' @export
natural_capital_from_dataset <- function(
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
) {
  validate_catalyst_dataset(dataset)
  .validate_field_reference(opening_field, dataset$data, "opening_field")
  optional <- list(
    regeneration_field = regeneration_field,
    restoration_field = restoration_field,
    additions_field = additions_field,
    extraction_field = extraction_field,
    degradation_field = degradation_field,
    damages_field = damages_field,
    closing_field = closing_field,
    time_field = time_field,
    entity_field = entity_field
  )
  for (name in names(optional)) {
    if (!is.null(optional[[name]])) .validate_field_reference(optional[[name]], dataset$data, name, allow_null = TRUE)
  }
  value <- function(field, default = 0) if (is.null(field)) default else dataset$data[[field]]
  if (is.null(unit)) unit <- dataset$units[[opening_field]]
  if (is.null(unit) || !nzchar(as.character(unit))) unit <- "index"
  natural_capital_account(
    opening_stock = dataset$data[[opening_field]],
    regeneration = value(regeneration_field),
    restoration = value(restoration_field),
    additions = value(additions_field),
    extraction = value(extraction_field),
    degradation = value(degradation_field),
    damages = value(damages_field),
    closing_stock = if (is.null(closing_field)) NULL else dataset$data[[closing_field]],
    time = if (is.null(time_field)) seq_len(nrow(dataset$data)) else dataset$data[[time_field]],
    entity = if (is.null(entity_field)) "all" else dataset$data[[entity_field]],
    unit = as.character(unit),
    account_id = account_id,
    title = title,
    metadata = list(dataset_id = dataset$id, dataset_fingerprint = dataset_fingerprint(dataset), source = dataset$source)
  )
}

#' Validate a natural-capital account
#'
#' @param account A `catalyst_natural_capital_account`.
#' @param tolerance Maximum absolute reconciliation error.
#' @return Invisibly returns TRUE when valid.
#' @export
validate_natural_capital_account <- function(account, tolerance = 1e-8) {
  .assert_scalar_number(tolerance, "tolerance", lower = 0)
  if (!inherits(account, "catalyst_natural_capital_account")) stop("`account` must be a natural-capital account.", call. = FALSE)
  if (!identical(account$schema_version, .catalyst_natural_capital_schema_version())) stop("Unsupported natural-capital account schema.", call. = FALSE)
  required <- c("entity", "time", "opening_stock", "regeneration", "restoration", "additions", "extraction", "degradation", "damages", "closing_stock", "reconciliation_error")
  if (!all(required %in% names(account$data))) stop("Natural-capital account is incomplete.", call. = FALSE)
  if (any(abs(account$data$reconciliation_error) > tolerance)) stop("Natural-capital account does not reconcile within tolerance.", call. = FALSE)
  invisible(TRUE)
}

#' Summarize a natural-capital account
#'
#' @param account A natural-capital account.
#' @return Entity-level stock-and-flow summary.
#' @export
natural_capital_summary <- function(account) {
  if (!inherits(account, "catalyst_natural_capital_account")) stop("`account` must be a natural-capital account.", call. = FALSE)
  groups <- split(seq_len(nrow(account$data)), account$data$entity)
  rows <- lapply(groups, function(index) {
    data <- account$data[index, , drop = FALSE]
    data <- data[order(data$time), , drop = FALSE]
    data.frame(
      entity = data$entity[1L],
      opening_stock = data$opening_stock[1L],
      closing_stock = utils::tail(data$closing_stock, 1L),
      net_change = utils::tail(data$closing_stock, 1L) - data$opening_stock[1L],
      regeneration = sum(data$regeneration),
      restoration = sum(data$restoration),
      additions = sum(data$additions),
      extraction = sum(data$extraction),
      degradation = sum(data$degradation),
      damages = sum(data$damages),
      maximum_reconciliation_error = max(abs(data$reconciliation_error)),
      unit = account$unit,
      stringsAsFactors = FALSE
    )
  })
  result <- do.call(rbind, rows)
  rownames(result) <- NULL
  result
}

#' Plot a natural-capital account
#'
#' @param account A natural-capital account.
#' @return A ggplot object showing opening and closing stocks over time.
#' @export
plot_natural_capital_account <- function(account) {
  if (!inherits(account, "catalyst_natural_capital_account")) stop("`account` must be a natural-capital account.", call. = FALSE)
  data <- rbind(
    data.frame(entity = account$data$entity, time = account$data$time, stock = account$data$opening_stock, measure = "opening_stock", stringsAsFactors = FALSE),
    data.frame(entity = account$data$entity, time = account$data$time, stock = account$data$closing_stock, measure = "closing_stock", stringsAsFactors = FALSE)
  )
  ggplot2::ggplot(data, ggplot2::aes(x = time, y = stock, color = measure, group = interaction(entity, measure))) +
    ggplot2::geom_line(linewidth = 0.8) +
    ggplot2::facet_wrap(~ entity, scales = "free_y") +
    ggplot2::labs(x = "Time", y = paste("Natural capital (", account$unit, ")", sep = ""), color = NULL, title = account$title) +
    theme_catalyst()
}

#' @export
print.catalyst_natural_capital_account <- function(x, ...) {
  cat("<catalyst_natural_capital_account>\n")
  cat("  id:       ", x$id, "\n", sep = "")
  cat("  entities: ", length(unique(x$data$entity)), "\n", sep = "")
  cat("  rows:     ", nrow(x$data), "\n", sep = "")
  cat("  unit:     ", x$unit, "\n", sep = "")
  invisible(x)
}
