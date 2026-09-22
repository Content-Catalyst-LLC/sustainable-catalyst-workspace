.regional_portfolio_schema_version <- function() "1.0.0"
.regional_portfolio_analysis_schema_version <- function() "1.0.0"

.scope_record_id <- function(x, arg) {
  .project_id(x, arg)
  invisible(x)
}

#' Create a governed geography scope
#'
#' @param id Stable geography identifier.
#' @param label Human-readable label.
#' @param level Geography level: global, region, country, subnational, or custom.
#' @param parent_id Optional parent geography identifier.
#' @param codes Optional named external codes such as ISO3 or UN M49.
#' @param metadata Additional metadata.
#' @return A `catalyst_geography_scope`.
#' @export
geography_scope <- function(id, label, level = c("global", "region", "country", "subnational", "custom"), parent_id = NULL, codes = list(), metadata = list()) {
  .scope_record_id(id, "id")
  .assert_single_string(label, "label")
  level <- match.arg(level)
  if (!is.null(parent_id)) .scope_record_id(parent_id, "parent_id")
  if (!is.list(codes) || (length(codes) && (is.null(names(codes)) || any(!nzchar(names(codes)))))) stop("`codes` must be a named list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(
    schema_version = "1.0.0", id = id, label = label, level = level,
    parent_id = parent_id, codes = codes, metadata = metadata
  ), class = c("catalyst_geography_scope", "list"))
}

#' Validate a geography scope
#' @param x Geography scope.
#' @return Invisibly returns `TRUE`.
#' @export
validate_geography_scope <- function(x) {
  if (!is.list(x)) stop("`x` must be a geography scope.", call. = FALSE)
  required <- c("schema_version", "id", "label", "level", "parent_id", "codes", "metadata")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Geography scope is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(x$schema_version, "1.0.0")) stop("Unsupported geography-scope schema version.", call. = FALSE)
  .scope_record_id(x$id, "x$id"); .assert_single_string(x$label, "x$label")
  if (!x$level %in% c("global", "region", "country", "subnational", "custom")) stop("Invalid geography level.", call. = FALSE)
  if (!is.null(x$parent_id)) .scope_record_id(x$parent_id, "x$parent_id")
  if (!is.list(x$codes) || !is.list(x$metadata)) stop("Geography codes and metadata must be lists.", call. = FALSE)
  invisible(TRUE)
}

.as_geography_scope <- function(x) {
  if (inherits(x, "catalyst_geography_scope")) { validate_geography_scope(x); return(x) }
  if (!is.list(x)) stop("Geography must be a geography-scope record.", call. = FALSE)
  if (!"parent_id" %in% names(x)) x["parent_id"] <- list(NULL)
  result <- structure(x, class = c("catalyst_geography_scope", "list")); validate_geography_scope(result); result
}

#' Create a governed sector scope
#'
#' @param id Stable sector identifier.
#' @param label Human-readable label.
#' @param classification Classification system such as ISIC, NAICS, NACE, or custom.
#' @param code Optional code within the classification.
#' @param parent_id Optional parent sector.
#' @param metadata Additional metadata.
#' @return A `catalyst_sector_scope`.
#' @export
sector_scope <- function(id, label, classification = "custom", code = NULL, parent_id = NULL, metadata = list()) {
  .scope_record_id(id, "id"); .assert_single_string(label, "label"); .assert_single_string(classification, "classification")
  if (!is.null(code)) .assert_single_string(code, "code")
  if (!is.null(parent_id)) .scope_record_id(parent_id, "parent_id")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(schema_version = "1.0.0", id = id, label = label, classification = classification,
                 code = code, parent_id = parent_id, metadata = metadata),
            class = c("catalyst_sector_scope", "list"))
}

#' Validate a sector scope
#' @param x Sector scope.
#' @return Invisibly returns `TRUE`.
#' @export
validate_sector_scope <- function(x) {
  if (!is.list(x)) stop("`x` must be a sector scope.", call. = FALSE)
  required <- c("schema_version", "id", "label", "classification", "code", "parent_id", "metadata")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Sector scope is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(x$schema_version, "1.0.0")) stop("Unsupported sector-scope schema version.", call. = FALSE)
  .scope_record_id(x$id, "x$id"); .assert_single_string(x$label, "x$label"); .assert_single_string(x$classification, "x$classification")
  if (!is.null(x$code)) .assert_single_string(x$code, "x$code")
  if (!is.null(x$parent_id)) .scope_record_id(x$parent_id, "x$parent_id")
  if (!is.list(x$metadata)) stop("Sector metadata must be a list.", call. = FALSE)
  invisible(TRUE)
}

.as_sector_scope <- function(x) {
  if (inherits(x, "catalyst_sector_scope")) { validate_sector_scope(x); return(x) }
  if (!is.list(x)) stop("Sector must be a sector-scope record.", call. = FALSE)
  if (!"code" %in% names(x)) x["code"] <- list(NULL)
  if (!"parent_id" %in% names(x)) x["parent_id"] <- list(NULL)
  result <- structure(x, class = c("catalyst_sector_scope", "list")); validate_sector_scope(result); result
}

#' Apply regional and sector scope to a canonical scenario
#'
#' @param scenario Canonical scenario.
#' @param geography Geography scope.
#' @param sectors Sector scope or list of scopes.
#' @param id Optional new scenario identifier.
#' @param title Optional new title.
#' @return A scoped `catalyst_scenario`.
#' @export
scope_scenario <- function(scenario, geography, sectors, id = NULL, title = NULL) {
  scenario <- as_catalyst_scenario(scenario)
  geography <- .as_geography_scope(geography)
  if (inherits(sectors, "catalyst_sector_scope")) sectors <- list(sectors)
  if (!is.list(sectors) || !length(sectors)) stop("`sectors` must contain at least one sector scope.", call. = FALSE)
  sectors <- lapply(sectors, .as_sector_scope)
  sector_ids <- vapply(sectors, function(x) x$id, character(1)); if (anyDuplicated(sector_ids)) stop("Sector ids must be unique.", call. = FALSE)
  if (!is.null(id)) { .scope_record_id(id, "id"); scenario$id <- id }
  if (!is.null(title)) { .assert_single_string(title, "title"); scenario$title <- title }
  scenario$scope <- list(
    geography = list(type = geography$level, id = geography$id, label = geography$label),
    sectors = sector_ids
  )
  scenario$metadata$regional_scope <- .safe_json_value(geography)
  scenario$metadata$sector_scopes <- lapply(sectors, .safe_json_value)
  scenario$metadata$tags <- unique(c(scenario$metadata$tags, "regional-scope", sector_ids))
  validate_catalyst_scenario(scenario)
  scenario
}

.normalize_portfolio_indicator <- function(value, id) {
  if (is.numeric(value) && length(value) == 1L && is.finite(value)) {
    return(list(id = id, value = as.numeric(value), unit = "index", direction = "contextual", metadata = list()))
  }
  if (!is.list(value)) stop(sprintf("Indicator `%s` must be numeric or a record.", id), call. = FALSE)
  if (is.null(value$value)) stop(sprintf("Indicator `%s` is missing `value`.", id), call. = FALSE)
  .assert_scalar_number(value$value, paste0("indicators$", id, "$value"))
  unit <- if (is.null(value$unit)) "index" else value$unit; .assert_single_string(unit, paste0("indicators$", id, "$unit"))
  direction <- if (is.null(value$direction)) "contextual" else value$direction
  if (!direction %in% c("higher_better", "lower_better", "contextual")) stop(sprintf("Indicator `%s` has an invalid direction.", id), call. = FALSE)
  metadata <- if (is.null(value$metadata)) list() else value$metadata; if (!is.list(metadata)) stop("Indicator metadata must be a list.", call. = FALSE)
  list(id = id, value = as.numeric(value$value), unit = unit, direction = direction, metadata = metadata)
}

#' Create a regional portfolio member
#'
#' @param id Stable member identifier.
#' @param title Human-readable title.
#' @param geography Geography scope.
#' @param sectors Sector scope or list of sector scopes.
#' @param weight Portfolio weight.
#' @param indicators Named indicator values or records.
#' @param carbon_budget Optional carbon-budget allocation record.
#' @param metadata Additional metadata.
#' @return A `catalyst_portfolio_member`.
#' @export
portfolio_member <- function(id, title, geography, sectors, weight = 1, indicators = list(), carbon_budget = NULL, metadata = list()) {
  .scope_record_id(id, "id"); .assert_single_string(title, "title"); .assert_scalar_number(weight, "weight")
  if (weight < 0) stop("`weight` must be non-negative.", call. = FALSE)
  geography <- .as_geography_scope(geography)
  if (inherits(sectors, "catalyst_sector_scope")) sectors <- list(sectors)
  if (!is.list(sectors) || !length(sectors)) stop("`sectors` must contain at least one sector scope.", call. = FALSE)
  sectors <- lapply(sectors, .as_sector_scope)
  if (!is.list(indicators) || (length(indicators) && (is.null(names(indicators)) || any(!nzchar(names(indicators)))))) stop("`indicators` must be a named list.", call. = FALSE)
  indicators <- lapply(names(indicators), function(name) .normalize_portfolio_indicator(indicators[[name]], name)); names(indicators) <- vapply(indicators, function(x) x$id, character(1))
  if (!is.null(carbon_budget)) {
    if (!is.list(carbon_budget) || is.null(carbon_budget$budget)) stop("`carbon_budget` must contain `budget`.", call. = FALSE)
    .assert_scalar_number(carbon_budget$budget, "carbon_budget$budget")
    carbon_budget$unit <- if (is.null(carbon_budget$unit)) "MtCO2e" else carbon_budget$unit
    .assert_single_string(carbon_budget$unit, "carbon_budget$unit")
  }
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  structure(list(schema_version = "1.0.0", id = id, title = title, geography = geography,
                 sectors = sectors, weight = as.numeric(weight), indicators = indicators,
                 carbon_budget = carbon_budget, metadata = metadata),
            class = c("catalyst_portfolio_member", "list"))
}

validate_portfolio_member <- function(x) {
  if (!is.list(x)) stop("Portfolio member must be a list.", call. = FALSE)
  required <- c("schema_version", "id", "title", "geography", "sectors", "weight", "indicators", "carbon_budget", "metadata")
  missing <- setdiff(required, names(x)); if (length(missing)) stop("Portfolio member is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(x$schema_version, "1.0.0")) stop("Unsupported portfolio-member schema version.", call. = FALSE)
  .scope_record_id(x$id, "x$id"); .assert_single_string(x$title, "x$title"); validate_geography_scope(x$geography)
  if (!is.list(x$sectors) || !length(x$sectors)) stop("Portfolio member requires sector scopes.", call. = FALSE)
  invisible(lapply(x$sectors, validate_sector_scope))
  .assert_scalar_number(x$weight, "x$weight"); if (x$weight < 0) stop("Portfolio member weight must be non-negative.", call. = FALSE)
  if (!is.list(x$indicators) || !is.list(x$metadata)) stop("Portfolio indicators and metadata must be lists.", call. = FALSE)
  invisible(TRUE)
}

.as_portfolio_member <- function(x) {
  if (inherits(x, "catalyst_portfolio_member")) { validate_portfolio_member(x); return(x) }
  if (!is.list(x)) stop("Portfolio member must be a list.", call. = FALSE)
  x$geography <- .as_geography_scope(x$geography); x$sectors <- lapply(x$sectors, .as_sector_scope)
  result <- structure(x, class = c("catalyst_portfolio_member", "list")); validate_portfolio_member(result); result
}

.normalize_portfolio_price_year <- function(x, label = "price_year") {
  if (is.null(x) || length(x) == 0L) return(NA_integer_)
  if (length(x) != 1L) stop(sprintf("`%s` must be a single number or NULL.", label), call. = FALSE)
  if (is.na(x)) return(NA_integer_)
  .assert_scalar_number(x, label)
  value <- as.integer(x)
  if (value < 1800L || value > 3000L) {
    stop(sprintf("`%s` must be between 1800 and 3000 when supplied.", label), call. = FALSE)
  }
  value
}

#' Create a governed regional and sector portfolio
#'
#' @param portfolio_id Stable portfolio identifier.
#' @param title Human-readable title.
#' @param members Non-empty member list.
#' @param description Portfolio purpose.
#' @param base_currency Base currency or index.
#' @param price_year Optional price year.
#' @param metadata Additional metadata.
#' @return A `catalyst_regional_portfolio`.
#' @export
regional_portfolio <- function(portfolio_id, title, members, description = "", base_currency = "index", price_year = NA_integer_, metadata = list()) {
  .scope_record_id(portfolio_id, "portfolio_id"); .assert_single_string(title, "title"); .assert_single_string(description, "description", allow_empty = TRUE)
  .assert_single_string(base_currency, "base_currency")
  price_year <- .normalize_portfolio_price_year(price_year, "price_year")
  if (inherits(members, "catalyst_portfolio_member")) members <- list(members)
  if (!is.list(members) || !length(members)) stop("`members` must be a non-empty list.", call. = FALSE)
  members <- lapply(members, .as_portfolio_member); ids <- vapply(members, function(x) x$id, character(1)); if (anyDuplicated(ids)) stop("Portfolio member ids must be unique.", call. = FALSE); names(members) <- ids
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  result <- structure(list(
    schema_version = .regional_portfolio_schema_version(), portfolio_type = "regional_sector_portfolio",
    id = portfolio_id, title = title, description = description, members = members,
    base_currency = base_currency, price_year = price_year,
    metadata = utils::modifyList(list(package_version = .catalyst_package_version(), created_at = .utc_now(), updated_at = .utc_now(), review_status = "unreviewed"), metadata)
  ), class = c("catalyst_regional_portfolio", "list"))
  validate_regional_portfolio(result); result
}

#' Validate a regional portfolio
#' @param portfolio Regional portfolio.
#' @return Invisibly returns `TRUE`.
#' @export
validate_regional_portfolio <- function(portfolio) {
  if (!is.list(portfolio)) stop("`portfolio` must be a list.", call. = FALSE)
  required <- c("schema_version", "portfolio_type", "id", "title", "description", "members", "base_currency", "price_year", "metadata")
  missing <- setdiff(required, names(portfolio)); if (length(missing)) stop("Portfolio is missing: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(portfolio$schema_version, .regional_portfolio_schema_version())) stop("Unsupported portfolio schema version.", call. = FALSE)
  if (!identical(portfolio$portfolio_type, "regional_sector_portfolio")) stop("Unsupported portfolio type.", call. = FALSE)
  .scope_record_id(portfolio$id, "portfolio$id"); .assert_single_string(portfolio$title, "portfolio$title"); .assert_single_string(portfolio$description, "portfolio$description", allow_empty = TRUE)
  if (!is.list(portfolio$members) || !length(portfolio$members)) stop("Portfolio requires members.", call. = FALSE)
  invisible(lapply(portfolio$members, validate_portfolio_member))
  .assert_single_string(portfolio$base_currency, "portfolio$base_currency")
  .normalize_portfolio_price_year(portfolio$price_year, "portfolio$price_year")
  if (!is.list(portfolio$metadata)) stop("Portfolio metadata must be a list.", call. = FALSE)
  invisible(TRUE)
}

portfolio_indicator_table <- function(portfolio) {
  validate_regional_portfolio(portfolio)
  rows <- list()
  for (member in portfolio$members) for (indicator in member$indicators) {
    rows[[length(rows) + 1L]] <- data.frame(
      member_id = member$id, member_title = member$title,
      geography_id = member$geography$id, geography_label = member$geography$label,
      sector_ids = paste(vapply(member$sectors, function(x) x$id, character(1)), collapse = ";"),
      weight = member$weight, indicator = indicator$id, value = indicator$value,
      unit = indicator$unit, direction = indicator$direction, stringsAsFactors = FALSE
    )
  }
  if (!length(rows)) return(data.frame(member_id=character(),member_title=character(),geography_id=character(),geography_label=character(),sector_ids=character(),weight=numeric(),indicator=character(),value=numeric(),unit=character(),direction=character(),stringsAsFactors=FALSE))
  do.call(rbind, rows)
}

#' Aggregate weighted portfolio indicators
#' @param portfolio Regional portfolio.
#' @return Weighted indicator summary table.
#' @export
portfolio_aggregate <- function(portfolio) {
  values <- portfolio_indicator_table(portfolio)
  if (!nrow(values)) return(data.frame())
  groups <- split(seq_len(nrow(values)), interaction(values$indicator, values$unit, drop = TRUE, lex.order = TRUE))
  rows <- lapply(groups, function(idx) {
    block <- values[idx, , drop = FALSE]; total_weight <- sum(block$weight)
    weighted <- if (total_weight > 0) sum(block$value * block$weight) / total_weight else NA_real_
    directions <- unique(block$direction)
    data.frame(indicator = block$indicator[1L], unit = block$unit[1L], direction = if (length(directions)==1L) directions else "contextual",
      weighted_value = weighted, total_weight = total_weight, members = nrow(block), minimum = min(block$value), maximum = max(block$value), stringsAsFactors = FALSE)
  })
  result <- do.call(rbind, rows); rownames(result) <- NULL; result[order(result$indicator, result$unit), , drop = FALSE]
}

#' Compare portfolio regions by indicator
#' @param portfolio Regional portfolio.
#' @param indicator Optional indicator id.
#' @return Region-by-indicator ranking table.
#' @export
portfolio_compare_regions <- function(portfolio, indicator = NULL) {
  values <- portfolio_indicator_table(portfolio)
  if (!is.null(indicator)) { .assert_single_string(indicator, "indicator"); values <- values[values$indicator == indicator, , drop = FALSE] }
  if (!nrow(values)) return(values)
  values$rank <- NA_integer_
  for (metric in unique(values$indicator)) {
    idx <- which(values$indicator == metric); direction <- unique(values$direction[idx]); direction <- if (length(direction)==1L) direction else "contextual"
    order_value <- if (identical(direction, "lower_better")) values$value[idx] else -values$value[idx]
    values$rank[idx] <- rank(order_value, ties.method = "min")
  }
  values[order(values$indicator, values$rank, values$member_id), , drop = FALSE]
}

#' Calculate weighted indicator summaries from a data frame
#' @param data Input data frame.
#' @param value_col Value column name.
#' @param weight_col Weight column name.
#' @param group_cols Optional grouping columns.
#' @param na_rm Remove incomplete rows.
#' @return Weighted summary table.
#' @export
weighted_indicator_summary <- function(data, value_col, weight_col, group_cols = character(), na_rm = FALSE) {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  .assert_single_string(value_col, "value_col"); .assert_single_string(weight_col, "weight_col"); .assert_flag(na_rm, "na_rm")
  if (!is.character(group_cols) || anyNA(group_cols)) stop("`group_cols` must be a character vector.", call. = FALSE)
  missing <- setdiff(c(value_col, weight_col, group_cols), names(data)); if (length(missing)) stop("Missing columns: ", paste(missing, collapse = ", "), call. = FALSE)
  values <- data[[value_col]]; weights <- data[[weight_col]]
  if (!is.numeric(values) || !is.numeric(weights)) stop("Value and weight columns must be numeric.", call. = FALSE)
  if (any(weights < 0, na.rm = TRUE)) stop("Weights must be non-negative.", call. = FALSE)
  idx_groups <- if (!length(group_cols)) list(all = seq_len(nrow(data))) else split(seq_len(nrow(data)), do.call(interaction, c(unname(data[group_cols]), list(drop = TRUE, lex.order = TRUE))))
  rows <- lapply(idx_groups, function(idx) {
    keep <- is.finite(values[idx]) & is.finite(weights[idx])
    if (!na_rm && !all(keep)) return(NULL)
    idx <- idx[keep]; if (!length(idx)) return(NULL)
    weighted_value <- if (sum(weights[idx]) > 0) sum(values[idx] * weights[idx]) / sum(weights[idx]) else NA_real_
    if (!length(group_cols)) {
      return(data.frame(weighted_value = weighted_value, total_weight = sum(weights[idx]), observations = length(idx), stringsAsFactors = FALSE))
    }
    row <- data[idx[1L], group_cols, drop = FALSE]
    row$weighted_value <- weighted_value
    row$total_weight <- sum(weights[idx]); row$observations <- length(idx); row
  })
  rows <- Filter(Negate(is.null), rows); if (!length(rows)) return(data.frame())
  result <- do.call(rbind, rows); rownames(result) <- NULL; result
}

#' Build regional carbon-budget pathways
#'
#' @param data Data frame containing geography, time, and emissions.
#' @param budgets Data frame containing one budget per geography.
#' @param geography_col Geography column in `data`.
#' @param time_col Time column in `data`.
#' @param emissions_col Net-emissions column in `data`.
#' @param budget_geography_col Geography column in `budgets`.
#' @param budget_col Budget value column.
#' @param unit Emissions unit.
#' @return A `catalyst_regional_carbon_budgets`.
#' @export
regional_carbon_budgets <- function(data, budgets, geography_col = "geography_id", time_col = "year", emissions_col = "net_emissions", budget_geography_col = "geography_id", budget_col = "carbon_budget", unit = "MtCO2e") {
  if (!is.data.frame(data) || !is.data.frame(budgets)) stop("`data` and `budgets` must be data frames.", call. = FALSE)
  if (!nrow(data) || !nrow(budgets)) stop("`data` and `budgets` must be non-empty.", call. = FALSE)
  for (x in c(geography_col,time_col,emissions_col,budget_geography_col,budget_col,unit)) .assert_single_string(x, "column or unit")
  missing_data <- setdiff(c(geography_col,time_col,emissions_col), names(data)); if (length(missing_data)) stop("Emissions data is missing: ", paste(missing_data, collapse = ", "), call. = FALSE)
  missing_budget <- setdiff(c(budget_geography_col,budget_col), names(budgets)); if (length(missing_budget)) stop("Budget data is missing: ", paste(missing_budget, collapse = ", "), call. = FALSE)
  if (!is.numeric(data[[time_col]]) || !is.numeric(data[[emissions_col]]) || !is.numeric(budgets[[budget_col]])) stop("Time, emissions, and budget columns must be numeric.", call. = FALSE)
  if (anyDuplicated(budgets[[budget_geography_col]])) stop("Budgets must contain one row per geography.", call. = FALSE)
  rows <- list(); diagnostics <- list()
  for (geo in unique(as.character(data[[geography_col]]))) {
    block <- data[as.character(data[[geography_col]]) == geo, , drop = FALSE]; block <- block[order(block[[time_col]]), , drop = FALSE]
    budget_row <- budgets[as.character(budgets[[budget_geography_col]]) == geo, , drop = FALSE]
    if (nrow(budget_row) != 1L) stop(sprintf("Geography `%s` does not have exactly one budget.", geo), call. = FALSE)
    emissions <- block[[emissions_col]]; if (any(!is.finite(emissions))) stop("Emissions must be finite.", call. = FALSE)
    cumulative <- cumsum(emissions); budget <- budget_row[[budget_col]][1L]; remaining <- budget - cumulative; overshoot <- remaining < 0
    rows[[length(rows)+1L]] <- data.frame(geography_id=geo,time=block[[time_col]],net_emissions=emissions,cumulative_emissions=cumulative,carbon_budget=budget,remaining_budget=remaining,budget_share_used=if (budget==0) NA_real_ else cumulative/budget,overshoot=overshoot,unit=unit,stringsAsFactors=FALSE)
    first_over <- which(overshoot)[1L]; diagnostics[[length(diagnostics)+1L]] <- data.frame(geography_id=geo,carbon_budget=budget,cumulative_emissions=tail(cumulative,1L),remaining_budget=tail(remaining,1L),overshoot=any(overshoot),overshoot_time=if (length(first_over) && !is.na(first_over)) block[[time_col]][first_over] else NA_real_,unit=unit,stringsAsFactors=FALSE)
  }
  structure(list(schema_version="1.0.0",pathway=do.call(rbind,rows),diagnostics=do.call(rbind,diagnostics),meta=list(package_version=.catalyst_package_version(),created_at=.utc_now())), class=c("catalyst_regional_carbon_budgets","list"))
}

#' Summarize sector transition pathways
#'
#' @param data Sector time-series data.
#' @param sector_col Sector column.
#' @param time_col Time column.
#' @param output_col Output or activity column.
#' @param emissions_col Emissions column.
#' @param geography_col Optional geography column.
#' @return A `catalyst_sector_transition_pathways`.
#' @export
sector_transition_pathways <- function(data, sector_col="sector_id", time_col="year", output_col="output", emissions_col="emissions", geography_col=NULL) {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  if (!nrow(data)) stop("`data` must be non-empty.", call. = FALSE)
  cols <- c(sector_col,time_col,output_col,emissions_col); if (!is.null(geography_col)) cols <- c(cols,geography_col)
  missing <- setdiff(cols,names(data)); if (length(missing)) stop("Sector pathway data is missing: ", paste(missing,collapse=", "), call. = FALSE)
  if (!is.numeric(data[[time_col]]) || !is.numeric(data[[output_col]]) || !is.numeric(data[[emissions_col]])) stop("Time, output, and emissions columns must be numeric.", call. = FALSE)
  keys <- if (is.null(geography_col)) as.character(data[[sector_col]]) else paste(data[[geography_col]],data[[sector_col]],sep="::")
  groups <- split(seq_len(nrow(data)),keys); paths <- list(); summaries <- list()
  for (key in names(groups)) {
    block <- data[groups[[key]],,drop=FALSE]; block <- block[order(block[[time_col]]),,drop=FALSE]
    intensity <- ifelse(block[[output_col]]==0,NA_real_,block[[emissions_col]]/block[[output_col]])
    geo <- if (is.null(geography_col)) "ALL" else as.character(block[[geography_col]][1L]); sector <- as.character(block[[sector_col]][1L])
    paths[[length(paths)+1L]] <- data.frame(geography_id=geo,sector_id=sector,time=block[[time_col]],output=block[[output_col]],emissions=block[[emissions_col]],emissions_intensity=intensity,stringsAsFactors=FALSE)
    start_output <- block[[output_col]][1L]; end_output <- tail(block[[output_col]],1L); start_emissions <- block[[emissions_col]][1L]; end_emissions <- tail(block[[emissions_col]],1L); start_intensity <- intensity[1L]; end_intensity <- tail(intensity,1L)
    output_change <- if (start_output==0) NA_real_ else end_output/start_output-1; emissions_change <- if (start_emissions==0) NA_real_ else end_emissions/start_emissions-1; intensity_change <- if (!is.finite(start_intensity) || start_intensity==0) NA_real_ else end_intensity/start_intensity-1
    status <- if (is.finite(output_change) && is.finite(emissions_change) && output_change >= 0 && emissions_change <= 0) "absolute_decoupling" else if (is.finite(intensity_change) && intensity_change < 0) "intensity_improving" else "transition_gap"
    summaries[[length(summaries)+1L]] <- data.frame(geography_id=geo,sector_id=sector,start_time=block[[time_col]][1L],end_time=tail(block[[time_col]],1L),output_change=output_change,emissions_change=emissions_change,intensity_change=intensity_change,status=status,stringsAsFactors=FALSE)
  }
  structure(list(schema_version="1.0.0",pathways=do.call(rbind,paths),summary=do.call(rbind,summaries),meta=list(package_version=.catalyst_package_version(),created_at=.utc_now())),class=c("catalyst_sector_transition_pathways","list"))
}

#' Create integrated regional, sector, and portfolio analysis
#' @param portfolio Regional portfolio.
#' @param carbon_budgets Optional regional carbon-budget result.
#' @param sector_pathways Optional sector-transition result.
#' @return A `catalyst_regional_portfolio_analysis`.
#' @export
regional_portfolio_analysis <- function(portfolio, carbon_budgets=NULL, sector_pathways=NULL) {
  validate_regional_portfolio(portfolio)
  if (!is.null(carbon_budgets) && !inherits(carbon_budgets,"catalyst_regional_carbon_budgets")) stop("`carbon_budgets` must be a regional carbon-budget result.", call. = FALSE)
  if (!is.null(sector_pathways) && !inherits(sector_pathways,"catalyst_sector_transition_pathways")) stop("`sector_pathways` must be a sector-transition result.", call. = FALSE)
  structure(list(schema_version=.regional_portfolio_analysis_schema_version(),analysis_type="regional_sector_portfolio_analysis",id=portfolio$id,title=portfolio$title,portfolio=portfolio,indicator_values=portfolio_indicator_table(portfolio),portfolio_aggregates=portfolio_aggregate(portfolio),regional_comparison=portfolio_compare_regions(portfolio),carbon_budgets=carbon_budgets,sector_pathways=sector_pathways,meta=list(package_version=.catalyst_package_version(),created_at=.utc_now(),human_review_required=TRUE)),class=c("catalyst_regional_portfolio_analysis","list"))
}

#' Summarize regional portfolio analysis
#' @param analysis Regional portfolio analysis.
#' @return Named summary list.
#' @export
regional_portfolio_summary <- function(analysis) {
  if (!inherits(analysis,"catalyst_regional_portfolio_analysis")) stop("`analysis` must be a regional portfolio analysis.", call. = FALSE)
  list(id=analysis$id,title=analysis$title,members=length(analysis$portfolio$members),geographies=length(unique(vapply(analysis$portfolio$members,function(x)x$geography$id,character(1)))),sectors=length(unique(unlist(lapply(analysis$portfolio$members,function(x)vapply(x$sectors,function(y)y$id,character(1)))))),indicators=length(unique(analysis$indicator_values$indicator)),carbon_budget_geographies=if(is.null(analysis$carbon_budgets))0L else nrow(analysis$carbon_budgets$diagnostics),sector_pathways=if(is.null(analysis$sector_pathways))0L else nrow(analysis$sector_pathways$summary),review_boundary="Analytical aggregation requires human review and does not allocate policy authority.")
}

#' Save a regional portfolio as JSON
#' @param portfolio Regional portfolio.
#' @param path Destination path.
#' @param pretty Pretty-print JSON.
#' @return Invisibly returns `path`.
#' @export
regional_portfolio_to_json <- function(portfolio,path,pretty=TRUE) {
  validate_regional_portfolio(portfolio); .assert_single_string(path,"path"); .assert_flag(pretty,"pretty"); dir.create(dirname(path),recursive=TRUE,showWarnings=FALSE)
  jsonlite::write_json(.safe_json_value(unclass(portfolio)),path,auto_unbox=TRUE,pretty=pretty,null="null",na="null",digits=NA,dataframe="rows"); invisible(path)
}

#' Load a regional portfolio from JSON
#' @param path JSON path.
#' @return A regional portfolio.
#' @export
regional_portfolio_from_json <- function(path) {
  .assert_single_string(path,"path"); if(!file.exists(path)) stop("Portfolio JSON file does not exist.",call.=FALSE)
  x <- jsonlite::fromJSON(path,simplifyVector=FALSE)
  x["price_year"] <- list(.normalize_portfolio_price_year(x$price_year, "portfolio$price_year"))
  x$members <- lapply(x$members,.as_portfolio_member)
  result <- structure(x,class=c("catalyst_regional_portfolio","list")); validate_regional_portfolio(result); result
}

#' Plot portfolio indicator values
#' @param analysis Regional portfolio analysis.
#' @param indicator Indicator id.
#' @return A ggplot object.
#' @export
plot_portfolio_indicators <- function(analysis, indicator) {
  if (!inherits(analysis,"catalyst_regional_portfolio_analysis")) stop("`analysis` must be a regional portfolio analysis.",call.=FALSE); .assert_single_string(indicator,"indicator")
  rows <- analysis$regional_comparison[analysis$regional_comparison$indicator==indicator,,drop=FALSE]; if(!nrow(rows)) stop("Indicator is not present in the portfolio.",call.=FALSE)
  ggplot2::ggplot(rows,ggplot2::aes(x=stats::reorder(member_id,value),y=value,fill=geography_id))+ggplot2::geom_col()+ggplot2::coord_flip()+ggplot2::labs(x=NULL,y=rows$unit[1L],fill="Geography",title=paste("Regional portfolio:",indicator))+theme_catalyst()
}

#' Plot regional carbon-budget pathways
#' @param x Regional carbon-budget result.
#' @return A ggplot object.
#' @export
plot_regional_carbon_budgets <- function(x) {
  if (!inherits(x,"catalyst_regional_carbon_budgets")) stop("`x` must be a regional carbon-budget result.",call.=FALSE)
  ggplot2::ggplot(x$pathway,ggplot2::aes(x=time,y=remaining_budget,color=geography_id))+ggplot2::geom_line(linewidth=.9)+ggplot2::geom_hline(yintercept=0,linewidth=.4)+ggplot2::labs(x="Time",y=paste("Remaining budget (",unique(x$pathway$unit)[1L],")",sep=""),color="Geography",title="Regional carbon budgets")+theme_catalyst()
}

#' @export
print.catalyst_regional_portfolio <- function(x, ...) {
  cat(sprintf("<catalyst_regional_portfolio %s>\n",x$id)); cat(sprintf("  %s\n",x$title)); cat(sprintf("  members: %d | indicators: %d\n",length(x$members),nrow(portfolio_aggregate(x)))); invisible(x)
}

#' @export
print.catalyst_regional_portfolio_analysis <- function(x, ...) {
  summary <- regional_portfolio_summary(x); cat(sprintf("<catalyst_regional_portfolio_analysis %s>\n",x$id)); cat(sprintf("  members: %d | geographies: %d | sectors: %d\n",summary$members,summary$geographies,summary$sectors)); invisible(x)
}
