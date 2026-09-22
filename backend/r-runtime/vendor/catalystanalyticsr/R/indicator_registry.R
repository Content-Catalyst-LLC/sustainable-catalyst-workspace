.catalyst_indicator_registry <- new.env(parent = emptyenv())

.validate_indicator_id <- function(id) {
  .assert_single_string(id, "id")
  if (!grepl("^[a-z][a-z0-9_]*$", id)) stop("Indicator `id` must use lowercase letters, digits, and underscores.", call. = FALSE)
  invisible(id)
}

.indicator_registry_key <- function(id, version) paste(id, version, sep = "@")

#' Define a governed indicator
#'
#' @param id Stable lowercase indicator identifier.
#' @param version Semantic definition version.
#' @param title Human-readable title.
#' @param description Indicator interpretation.
#' @param formula Human-readable formula.
#' @param required_fields Input fields required by the calculation.
#' @param unit Output unit.
#' @param direction `higher_better`, `lower_better`, or `contextual`.
#' @param aggregation Calculation behavior such as `rowwise`, `sum`, or `custom`.
#' @param source Source and methodology references.
#' @param calculation Function with signature `(data, dataset, na_rm)`.
#' @param targets Optional target or threshold records.
#' @param metadata Additional definition metadata.
#' @return A `catalyst_indicator` definition.
#' @export
new_catalyst_indicator <- function(
  id,
  version,
  title,
  description,
  formula,
  required_fields,
  unit,
  direction = c("higher_better", "lower_better", "contextual"),
  aggregation = c("rowwise", "sum", "mean", "last_minus_first", "custom"),
  source = list(),
  calculation,
  targets = list(),
  metadata = list()
) {
  .validate_indicator_id(id)
  .validate_semver(version)
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  .assert_single_string(formula, "formula")
  if (!is.character(required_fields) || !length(required_fields) || any(!nzchar(required_fields)) || anyDuplicated(required_fields)) {
    stop("`required_fields` must be a non-empty vector of unique field names.", call. = FALSE)
  }
  .assert_single_string(unit, "unit")
  direction <- match.arg(direction)
  aggregation <- match.arg(aggregation)
  if (!is.list(source)) stop("`source` must be a list.", call. = FALSE)
  if (!is.function(calculation)) stop("`calculation` must be a function.", call. = FALSE)
  if (!is.list(targets)) stop("`targets` must be a list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)

  structure(list(
    id = id,
    version = version,
    title = title,
    description = description,
    formula = formula,
    required_fields = required_fields,
    unit = unit,
    direction = direction,
    aggregation = aggregation,
    source = source,
    calculation = calculation,
    targets = targets,
    metadata = utils::modifyList(list(status = "active", created_at = .utc_now()), metadata)
  ), class = "catalyst_indicator")
}

#' Validate a governed indicator definition
#'
#' @param indicator A `catalyst_indicator`.
#' @return Invisibly returns TRUE when valid.
#' @export
validate_catalyst_indicator <- function(indicator) {
  if (!inherits(indicator, "catalyst_indicator")) stop("`indicator` must inherit from `catalyst_indicator`.", call. = FALSE)
  rebuilt <- do.call(new_catalyst_indicator, unclass(indicator))
  invisible(inherits(rebuilt, "catalyst_indicator"))
}

.direct_indicator <- function(id, title, field, unit, direction, description = "") {
  new_catalyst_indicator(
    id = id,
    version = "1.0.0",
    title = title,
    description = description,
    formula = field,
    required_fields = field,
    unit = unit,
    direction = direction,
    aggregation = "rowwise",
    source = list(type = "field", methodology = "Direct reported or modeled value."),
    calculation = local({
      selected_field <- field
      function(data, dataset, na_rm) as.numeric(data[[selected_field]])
    }),
    metadata = list(builtin = TRUE)
  )
}

.ensure_builtin_indicators <- function() {
  definitions <- list(
    .direct_indicator("gdp", "Gross domestic product", "gdp", "currency", "higher_better", "Reported or modeled economic output."),
    .direct_indicator("emissions", "Greenhouse-gas emissions", "emissions", "tCO2e", "lower_better", "Reported or modeled greenhouse-gas emissions."),
    .direct_indicator("ans", "Adjusted net savings", "ans", "index", "higher_better", "Adjusted-net-savings value supplied by a model or dataset."),
    .direct_indicator("natural_capital", "Natural capital", "natural_capital", "index", "higher_better", "Natural-capital stock or index."),
    .direct_indicator("atmospheric_carbon", "Atmospheric carbon", "atmospheric_carbon", "index", "lower_better", "Atmospheric-carbon stock or index."),
    new_catalyst_indicator(
      "gdp_per_capita", "1.0.0", "GDP per capita", "Economic output divided by population.",
      "gdp / population", c("gdp", "population"), "currency/person", "higher_better", "rowwise",
      source = list(type = "derived", methodology = "GDP divided by population."),
      calculation = function(data, dataset, na_rm) as.numeric(data$gdp) / pmax(as.numeric(data$population), .Machine$double.eps),
      metadata = list(builtin = TRUE)
    ),
    new_catalyst_indicator(
      "emissions_per_capita", "1.0.0", "Emissions per capita", "Greenhouse-gas emissions divided by population.",
      "emissions / population", c("emissions", "population"), "tCO2e/person", "lower_better", "rowwise",
      source = list(type = "derived", methodology = "Emissions divided by population."),
      calculation = function(data, dataset, na_rm) as.numeric(data$emissions) / pmax(as.numeric(data$population), .Machine$double.eps),
      metadata = list(builtin = TRUE)
    ),
    new_catalyst_indicator(
      "carbon_intensity", "1.0.0", "Carbon intensity", "Greenhouse-gas emissions per unit of economic output.",
      "emissions / gdp", c("emissions", "gdp"), "tCO2e/currency", "lower_better", "rowwise",
      source = list(type = "derived", methodology = "Emissions divided by GDP."),
      calculation = function(data, dataset, na_rm) as.numeric(data$emissions) / pmax(as.numeric(data$gdp), .Machine$double.eps),
      metadata = list(builtin = TRUE)
    ),
    new_catalyst_indicator(
      "cumulative_emissions", "1.0.0", "Cumulative emissions", "Sum of emissions over the selected observations.",
      "sum(emissions)", "emissions", "tCO2e", "lower_better", "sum",
      source = list(type = "derived", methodology = "Unweighted sum across observations; users must align the observation frequency and emissions unit."),
      calculation = function(data, dataset, na_rm) sum(as.numeric(data$emissions), na.rm = na_rm),
      metadata = list(builtin = TRUE, frequency_sensitive = TRUE)
    ),
    new_catalyst_indicator(
      "adjusted_net_savings", "1.0.0", "Adjusted net savings", "Gross savings adjusted for depreciation, resource depletion, damages, and education investment.",
      "gross_savings - depreciation - depletion - damages + education_investment",
      c("gross_savings", "depreciation", "depletion", "damages", "education_investment"),
      "currency", "higher_better", "rowwise",
      source = list(type = "derived", methodology = "Transparent simplified adjusted-net-savings identity."),
      calculation = function(data, dataset, na_rm) {
        as.numeric(data$gross_savings) - as.numeric(data$depreciation) - as.numeric(data$depletion) - as.numeric(data$damages) + as.numeric(data$education_investment)
      },
      metadata = list(builtin = TRUE)
    ),
    new_catalyst_indicator(
      "natural_capital_change", "1.0.0", "Natural-capital change", "Difference between the final and initial natural-capital observations.",
      "last(natural_capital) - first(natural_capital)", "natural_capital", "index", "higher_better", "last_minus_first",
      source = list(type = "derived", methodology = "Final value minus initial value in the supplied record order."),
      calculation = function(data, dataset, na_rm) {
        values <- as.numeric(data$natural_capital)
        values <- values[!is.na(values)]
        if (!length(values)) return(NA_real_)
        values[length(values)] - values[1L]
      },
      metadata = list(builtin = TRUE)
    ),
    new_catalyst_indicator(
      "net_emissions", "1.0.0", "Net greenhouse-gas emissions", "Gross emissions less removals and sequestration.",
      "emissions - removals", c("emissions", "removals"), "tCO2e", "lower_better", "rowwise",
      source = list(type = "derived", methodology = "Gross emissions minus non-negative removals."),
      calculation = function(data, dataset, na_rm) as.numeric(data$emissions) - as.numeric(data$removals),
      metadata = list(builtin = TRUE, climate_accounting = TRUE)
    ),
    new_catalyst_indicator(
      "removal_share", "1.0.0", "Emissions removal share", "Removals as a share of gross emissions.",
      "removals / emissions", c("emissions", "removals"), "fraction", "higher_better", "rowwise",
      source = list(type = "derived", methodology = "Removals divided by gross emissions."),
      calculation = function(data, dataset, na_rm) as.numeric(data$removals) / pmax(as.numeric(data$emissions), .Machine$double.eps),
      metadata = list(builtin = TRUE, climate_accounting = TRUE)
    ),
    new_catalyst_indicator(
      "energy_intensity", "1.0.0", "Energy intensity", "Energy use per unit of economic output.",
      "energy / gdp", c("energy", "gdp"), "energy/currency", "lower_better", "rowwise",
      source = list(type = "derived", methodology = "Energy use divided by GDP."),
      calculation = function(data, dataset, na_rm) as.numeric(data$energy) / pmax(as.numeric(data$gdp), .Machine$double.eps),
      metadata = list(builtin = TRUE, climate_accounting = TRUE)
    ),
    new_catalyst_indicator(
      "natural_capital_balance", "1.0.0", "Natural-capital accounting balance", "Additions less extraction, degradation, and damages.",
      "regeneration + restoration + additions - extraction - degradation - damages",
      c("regeneration", "restoration", "additions", "extraction", "degradation", "damages"),
      "index", "higher_better", "rowwise",
      source = list(type = "derived", methodology = "Transparent natural-capital stock-and-flow accounting identity."),
      calculation = function(data, dataset, na_rm) {
        as.numeric(data$regeneration) + as.numeric(data$restoration) + as.numeric(data$additions) -
          as.numeric(data$extraction) - as.numeric(data$degradation) - as.numeric(data$damages)
      },
      metadata = list(builtin = TRUE, climate_accounting = TRUE)
    )
  )
  for (definition in definitions) {
    key <- .indicator_registry_key(definition$id, definition$version)
    if (!exists(key, envir = .catalyst_indicator_registry, inherits = FALSE)) {
      assign(key, definition, envir = .catalyst_indicator_registry)
    }
  }
  invisible(NULL)
}

#' Register a Catalyst indicator
#'
#' @param indicator A `catalyst_indicator` definition.
#' @param overwrite Replace an existing definition with the same id and version.
#' @return Invisibly returns the registered definition.
#' @export
register_catalyst_indicator <- function(indicator, overwrite = FALSE) {
  validate_catalyst_indicator(indicator)
  .assert_flag(overwrite, "overwrite")
  .ensure_builtin_indicators()
  key <- .indicator_registry_key(indicator$id, indicator$version)
  if (exists(key, envir = .catalyst_indicator_registry, inherits = FALSE) && !overwrite) {
    stop(sprintf("Indicator %s version %s is already registered.", indicator$id, indicator$version), call. = FALSE)
  }
  assign(key, indicator, envir = .catalyst_indicator_registry)
  invisible(indicator)
}

#' List registered Catalyst indicators
#'
#' @return A data frame of indicator definitions.
#' @export
list_catalyst_indicators <- function() {
  .ensure_builtin_indicators()
  keys <- ls(envir = .catalyst_indicator_registry, all.names = TRUE)
  rows <- lapply(keys, function(key) {
    definition <- get(key, envir = .catalyst_indicator_registry, inherits = FALSE)
    data.frame(
      id = definition$id,
      version = definition$version,
      title = definition$title,
      unit = definition$unit,
      direction = definition$direction,
      aggregation = definition$aggregation,
      required_fields = paste(definition$required_fields, collapse = ","),
      status = if (!is.null(definition$metadata$status)) definition$metadata$status else "active",
      stringsAsFactors = FALSE
    )
  })
  result <- do.call(rbind, rows)
  rownames(result) <- NULL
  result[order(result$id, result$version), , drop = FALSE]
}

#' Retrieve a registered Catalyst indicator
#'
#' @param id Indicator identifier.
#' @param version Optional exact version. The highest registered version is used when omitted.
#' @return A `catalyst_indicator`.
#' @export
get_catalyst_indicator <- function(id, version = NULL) {
  .validate_indicator_id(id)
  .ensure_builtin_indicators()
  available <- list_catalyst_indicators()
  available <- available[available$id == id, , drop = FALSE]
  if (!nrow(available)) stop(sprintf("Indicator `%s` is not registered.", id), call. = FALSE)
  if (is.null(version)) {
    version <- available$version[.version_order(available$version)][nrow(available)]
  } else {
    .validate_semver(version)
  }
  key <- .indicator_registry_key(id, version)
  if (!exists(key, envir = .catalyst_indicator_registry, inherits = FALSE)) stop(sprintf("Indicator `%s` version `%s` is not registered.", id, version), call. = FALSE)
  get(key, envir = .catalyst_indicator_registry, inherits = FALSE)
}

.indicator_contract_record <- function(indicator) {
  validate_catalyst_indicator(indicator)
  list(
    id = indicator$id,
    version = indicator$version,
    title = indicator$title,
    description = indicator$description,
    formula = indicator$formula,
    required_fields = unname(indicator$required_fields),
    unit = indicator$unit,
    direction = indicator$direction,
    aggregation = indicator$aggregation,
    source = indicator$source,
    targets = indicator$targets,
    metadata = indicator$metadata
  )
}

#' Export indicator registry definitions
#'
#' @param ids Optional indicator identifiers.
#' @param versions Optional named versions keyed by indicator id.
#' @return A list of machine-readable indicator definitions.
#' @export
catalyst_indicator_manifest <- function(ids = NULL, versions = NULL) {
  .ensure_builtin_indicators()
  if (is.null(ids)) ids <- unique(list_catalyst_indicators()$id)
  if (!is.character(ids) || any(!nzchar(ids))) stop("`ids` must be indicator identifiers.", call. = FALSE)
  lapply(ids, function(id) {
    version <- if (!is.null(versions) && id %in% names(versions)) versions[[id]] else NULL
    .indicator_contract_record(get_catalyst_indicator(id, version))
  })
}

.resolve_indicator <- function(indicator, version = NULL) {
  if (inherits(indicator, "catalyst_indicator")) return(indicator)
  if (is.character(indicator) && length(indicator) == 1L) return(get_catalyst_indicator(indicator, version))
  stop("`indicator` must be a registered id or `catalyst_indicator`.", call. = FALSE)
}

.bind_indicator_groups <- function(data, group_by) {
  if (!length(group_by)) return(list(all = seq_len(nrow(data))))
  interaction_value <- do.call(interaction, c(unname(data[group_by]), list(drop = TRUE, lex.order = TRUE)))
  split(seq_len(nrow(data)), interaction_value)
}

#' Calculate one governed indicator
#'
#' @param dataset A `catalyst_dataset`.
#' @param indicator Registered indicator id or definition.
#' @param version Optional exact indicator version.
#' @param group_by Optional dataset fields for grouped aggregation.
#' @param na_rm Remove missing values in supported aggregate calculations.
#' @return A `catalyst_indicator_result` with values and trace metadata.
#' @export
calculate_indicator <- function(dataset, indicator, version = NULL, group_by = character(), na_rm = FALSE) {
  validate_catalyst_dataset(dataset)
  definition <- .resolve_indicator(indicator, version)
  validate_catalyst_indicator(definition)
  .assert_flag(na_rm, "na_rm")
  if (!is.character(group_by) || any(!group_by %in% names(dataset$data)) || anyDuplicated(group_by)) {
    stop("`group_by` must contain unique dataset fields.", call. = FALSE)
  }
  absent <- setdiff(definition$required_fields, names(dataset$data))
  if (length(absent)) stop(sprintf("Indicator `%s` requires absent fields: %s.", definition$id, paste(absent, collapse = ", ")), call. = FALSE)
  non_numeric <- definition$required_fields[!vapply(dataset$data[definition$required_fields], is.numeric, logical(1))]
  if (length(non_numeric)) stop(sprintf("Indicator `%s` requires numeric fields: %s.", definition$id, paste(non_numeric, collapse = ", ")), call. = FALSE)

  groups <- .bind_indicator_groups(dataset$data, group_by)
  rows <- list()
  for (group_name in names(groups)) {
    index <- groups[[group_name]]
    subset <- dataset$data[index, , drop = FALSE]
    calculated <- definition$calculation(subset, dataset, na_rm)
    calculated <- as.numeric(calculated)
    if (definition$aggregation == "rowwise") {
      if (length(calculated) != nrow(subset)) stop("Rowwise indicator calculations must return one value per input row.", call. = FALSE)
      identity_fields <- unique(c(group_by, dataset$entity_fields, dataset$time_field))
      identity_fields <- identity_fields[nzchar(identity_fields)]
      row <- if (length(identity_fields)) subset[identity_fields] else data.frame(row = index)
      row$value <- calculated
    } else {
      if (length(calculated) != 1L) stop("Aggregate indicator calculations must return one value per group.", call. = FALSE)
      row <- if (length(group_by)) subset[1L, group_by, drop = FALSE] else data.frame(scope = "dataset", stringsAsFactors = FALSE)
      row$value <- calculated
    }
    rows[[length(rows) + 1L]] <- row
  }
  values <- do.call(rbind, rows)
  rownames(values) <- NULL
  values$indicator <- definition$id
  values$indicator_version <- definition$version
  values$unit <- definition$unit
  values$direction <- definition$direction

  trace <- list(
    schema_version = "1.0.0",
    indicator = .indicator_contract_record(definition),
    dataset = list(
      id = dataset$id,
      title = dataset$title,
      fingerprint = dataset_fingerprint(dataset),
      source = dataset$source,
      units = dataset$units
    ),
    calculation = list(
      calculated_at = .utc_now(),
      package_version = .catalyst_package_version(),
      group_by = unname(group_by),
      na_rm = na_rm,
      input_rows = nrow(dataset$data),
      output_rows = nrow(values),
      missing_required_cells = sum(is.na(dataset$data[definition$required_fields]))
    )
  )

  structure(list(
    definition = definition,
    dataset_id = dataset$id,
    values = values,
    trace = trace
  ), class = "catalyst_indicator_result")
}


.rbind_fill_indicator_values <- function(values) {
  fields <- unique(unlist(lapply(values, names), use.names = FALSE))
  normalized <- lapply(values, function(value) {
    absent <- setdiff(fields, names(value))
    for (field in absent) value[[field]] <- NA
    value[fields]
  })
  do.call(rbind, normalized)
}

#' Calculate multiple governed indicators
#'
#' @param dataset A `catalyst_dataset`.
#' @param indicators Character vector, list of ids, or list of definitions.
#' @param group_by Optional fields used for aggregate calculations.
#' @param na_rm Remove missing values in supported aggregates.
#' @return A `catalyst_indicator_set`.
#' @export
calculate_indicators <- function(dataset, indicators, group_by = character(), na_rm = FALSE) {
  if (is.character(indicators)) indicators <- as.list(indicators)
  if (!is.list(indicators) || !length(indicators)) stop("`indicators` must be a non-empty collection.", call. = FALSE)
  results <- lapply(indicators, function(indicator) calculate_indicator(dataset, indicator, group_by = group_by, na_rm = na_rm))
  ids <- vapply(results, function(result) result$definition$id, character(1))
  if (anyDuplicated(ids)) stop("Indicator ids must be unique within a calculation set.", call. = FALSE)
  names(results) <- ids
  combined <- .rbind_fill_indicator_values(lapply(results, function(result) result$values))
  rownames(combined) <- NULL
  structure(list(
    dataset_id = dataset$id,
    results = results,
    values = combined,
    meta = list(
      schema_version = "1.0.0",
      calculated_at = .utc_now(),
      package_version = .catalyst_package_version(),
      indicator_count = length(results)
    )
  ), class = "catalyst_indicator_set")
}

#' Return indicator calculation trace metadata
#'
#' @param result A `catalyst_indicator_result` or `catalyst_indicator_set`.
#' @return Trace record or named collection of trace records.
#' @export
indicator_trace <- function(result) {
  if (inherits(result, "catalyst_indicator_result")) return(result$trace)
  if (inherits(result, "catalyst_indicator_set")) return(lapply(result$results, function(value) value$trace))
  stop("`result` must be a Catalyst indicator result or set.", call. = FALSE)
}

#' @export
print.catalyst_indicator <- function(x, ...) {
  cat("<catalyst_indicator>\n")
  cat("  id:          ", x$id, "@", x$version, "\n", sep = "")
  cat("  title:       ", x$title, "\n", sep = "")
  cat("  formula:     ", x$formula, "\n", sep = "")
  cat("  unit:        ", x$unit, "\n", sep = "")
  invisible(x)
}

#' @export
print.catalyst_indicator_result <- function(x, ...) {
  cat("<catalyst_indicator_result>\n")
  cat("  indicator: ", x$definition$id, "@", x$definition$version, "\n", sep = "")
  cat("  dataset:   ", x$dataset_id, "\n", sep = "")
  cat("  rows:      ", nrow(x$values), "\n", sep = "")
  invisible(x)
}

#' @export
print.catalyst_indicator_set <- function(x, ...) {
  cat("<catalyst_indicator_set>\n")
  cat("  dataset:    ", x$dataset_id, "\n", sep = "")
  cat("  indicators: ", length(x$results), "\n", sep = "")
  invisible(x)
}
