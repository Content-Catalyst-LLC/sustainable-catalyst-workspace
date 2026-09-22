.catalyst_dataset_schema_version <- function() "1.0.0"

.validate_dataset_id <- function(id, argument = "id") {
  .assert_single_string(id, argument)
  if (!grepl("^[A-Za-z0-9][A-Za-z0-9._-]*$", id)) {
    stop(sprintf("`%s` must begin with a letter or digit and contain only letters, digits, periods, underscores, or hyphens.", argument), call. = FALSE)
  }
  invisible(id)
}

.empty_quality_flags <- function() {
  data.frame(
    code = character(),
    severity = character(),
    field = character(),
    count = integer(),
    message = character(),
    stringsAsFactors = FALSE
  )
}

.append_quality_flag <- function(flags, code, severity, field = "", count = 0L, message) {
  rbind(flags, data.frame(
    code = as.character(code),
    severity = as.character(severity),
    field = as.character(field),
    count = as.integer(count),
    message = as.character(message),
    stringsAsFactors = FALSE
  ))
}

#' Define a documented dataset source
#'
#' @param id Stable source identifier.
#' @param title Human-readable source title.
#' @param publisher Publisher or originating institution.
#' @param url Optional source URL.
#' @param license Data license or usage statement.
#' @param retrieved_at UTC retrieval timestamp.
#' @param citation Optional citation text.
#' @param metadata Additional named metadata.
#' @return A normalized source record.
#' @export
dataset_source <- function(
  id,
  title,
  publisher = "",
  url = "",
  license = "",
  retrieved_at = .utc_now(),
  citation = "",
  metadata = list()
) {
  .validate_dataset_id(id)
  .assert_single_string(title, "title")
  .assert_single_string(publisher, "publisher", allow_empty = TRUE)
  .assert_single_string(url, "url", allow_empty = TRUE)
  .assert_single_string(license, "license", allow_empty = TRUE)
  .assert_single_string(retrieved_at, "retrieved_at")
  .assert_single_string(citation, "citation", allow_empty = TRUE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  list(
    id = id,
    title = title,
    publisher = publisher,
    url = url,
    license = license,
    retrieved_at = retrieved_at,
    citation = citation,
    metadata = metadata
  )
}

.normalize_dataset_source <- function(source, fallback_id) {
  if (is.null(source)) {
    return(dataset_source(
      id = paste0(fallback_id, "-source"),
      title = "Undeclared source",
      metadata = list(status = "source_required_before_publication")
    ))
  }
  if (!is.list(source)) stop("`source` must be a source record or list.", call. = FALSE)
  defaults <- list(
    id = paste0(fallback_id, "-source"),
    title = "Undeclared source",
    publisher = "",
    url = "",
    license = "",
    retrieved_at = .utc_now(),
    citation = "",
    metadata = list()
  )
  source <- utils::modifyList(defaults, source)
  do.call(dataset_source, source[names(defaults)])
}

.normalize_units <- function(units, fields) {
  if (is.null(units)) units <- list()
  if (is.character(units) && !is.null(names(units))) units <- as.list(units)
  if (!is.list(units)) stop("`units` must be a named list or named character vector.", call. = FALSE)
  if (length(units)) {
    if (is.null(names(units)) || any(!nzchar(names(units))) || anyDuplicated(names(units))) {
      stop("`units` must be uniquely named by data field.", call. = FALSE)
    }
    unknown <- setdiff(names(units), fields)
    if (length(unknown)) stop(sprintf("Units reference unknown fields: %s.", paste(unknown, collapse = ", ")), call. = FALSE)
    invalid <- names(units)[!vapply(units, function(value) is.character(value) && length(value) == 1L && !is.na(value) && nzchar(value), logical(1))]
    if (length(invalid)) stop(sprintf("Units must be non-empty strings: %s.", paste(invalid, collapse = ", ")), call. = FALSE)
  }
  units
}

.infer_time_frequency <- function(values) {
  if (length(values) < 2L) return("single_observation")
  if (inherits(values, "Date")) {
    delta <- as.numeric(diff(values), units = "days")
  } else if (inherits(values, "POSIXt")) {
    delta <- as.numeric(diff(values), units = "secs")
  } else if (is.numeric(values)) {
    delta <- diff(as.numeric(values))
  } else {
    parsed <- suppressWarnings(as.Date(as.character(values)))
    if (all(!is.na(parsed))) delta <- as.numeric(diff(parsed), units = "days") else return("irregular_or_unknown")
  }
  delta <- delta[is.finite(delta)]
  if (!length(delta)) return("irregular_or_unknown")
  if (length(unique(round(delta, 8))) == 1L) paste0("regular:", format(delta[1L], trim = TRUE)) else "irregular"
}

.dataset_quality <- function(data, time_field = NULL, entity_fields = character()) {
  flags <- .empty_quality_flags()
  missing_counts <- colSums(is.na(data))
  for (field in names(missing_counts)[missing_counts > 0L]) {
    flags <- .append_quality_flag(
      flags, "missing_values", "warning", field, missing_counts[[field]],
      sprintf("Field `%s` contains %d missing value(s).", field, missing_counts[[field]])
    )
  }

  duplicate_rows <- sum(duplicated(data))
  if (duplicate_rows > 0L) {
    flags <- .append_quality_flag(
      flags, "duplicate_rows", "warning", "", duplicate_rows,
      sprintf("Dataset contains %d duplicate row(s).", duplicate_rows)
    )
  }

  key_fields <- unique(c(entity_fields, time_field))
  key_fields <- key_fields[nzchar(key_fields)]
  duplicate_keys <- 0L
  if (length(key_fields)) {
    keys <- data[key_fields]
    duplicate_keys <- sum(duplicated(keys))
    if (duplicate_keys > 0L) {
      flags <- .append_quality_flag(
        flags, "duplicate_keys", "error", paste(key_fields, collapse = ","), duplicate_keys,
        sprintf("Entity/time key contains %d duplicate record(s).", duplicate_keys)
      )
    }
  }

  time_ordered <- NA
  frequency <- "not_declared"
  if (!is.null(time_field)) {
    group_indices <- if (length(entity_fields)) {
      entity_key <- do.call(interaction, c(unname(data[entity_fields]), list(drop = TRUE, lex.order = TRUE)))
      split(seq_len(nrow(data)), entity_key)
    } else {
      list(dataset = seq_len(nrow(data)))
    }
    order_status <- vapply(group_indices, function(index) {
      values <- data[[time_field]][index]
      !is.unsorted(values, na.rm = TRUE)
    }, logical(1))
    frequencies <- vapply(group_indices, function(index) {
      values <- data[[time_field]][index]
      .infer_time_frequency(values[!is.na(values)])
    }, character(1))
    time_ordered <- all(order_status)
    frequency <- if (length(unique(frequencies)) == 1L) frequencies[[1L]] else "mixed"
    if (!time_ordered) {
      flags <- .append_quality_flag(
        flags, "time_not_ordered", "warning", time_field, sum(!order_status),
        sprintf("Time field `%s` is not ordered within %d entity group(s).", time_field, sum(!order_status))
      )
    }
  }

  list(
    row_count = nrow(data),
    column_count = ncol(data),
    missing_cells = sum(is.na(data)),
    duplicate_rows = duplicate_rows,
    duplicate_keys = duplicate_keys,
    time_ordered = time_ordered,
    frequency = frequency,
    flags = flags
  )
}

#' Create a governed Catalyst dataset
#'
#' @param data A data frame.
#' @param id Stable dataset identifier.
#' @param title Human-readable title.
#' @param time_field Optional time-column name.
#' @param entity_fields Optional entity-key columns such as country or sector.
#' @param units Named field-to-unit mapping.
#' @param source A record created by [dataset_source()] or compatible list.
#' @param geography Geographic-scope metadata.
#' @param sector Sector-scope metadata.
#' @param currency Currency metadata, including optional `code` and `price_year`.
#' @param required_fields Fields required for this dataset contract.
#' @param missing_policy One of `flag`, `error`, or `drop`.
#' @param transformations Existing transformation-history records.
#' @param metadata Additional named metadata.
#' @return A `catalyst_dataset` object.
#' @export
as_catalyst_dataset <- function(
  data,
  id,
  title = id,
  time_field = NULL,
  entity_fields = character(),
  units = list(),
  source = NULL,
  geography = list(),
  sector = list(),
  currency = list(code = NULL, price_year = NULL),
  required_fields = character(),
  missing_policy = c("flag", "error", "drop"),
  transformations = list(),
  metadata = list()
) {
  if (!is.data.frame(data)) stop("`data` must be a data frame.", call. = FALSE)
  if (!ncol(data)) stop("`data` must contain at least one column.", call. = FALSE)
  if (any(!nzchar(names(data))) || anyDuplicated(names(data))) {
    stop("Dataset column names must be non-empty and unique.", call. = FALSE)
  }
  .validate_dataset_id(id)
  .assert_single_string(title, "title")
  missing_policy <- match.arg(missing_policy)

  if (!is.null(time_field)) {
    .assert_single_string(time_field, "time_field")
    if (!time_field %in% names(data)) stop("`time_field` is not present in the data.", call. = FALSE)
  }
  if (!is.character(entity_fields) || any(!nzchar(entity_fields)) || anyDuplicated(entity_fields)) {
    stop("`entity_fields` must be a vector of unique field names.", call. = FALSE)
  }
  if (!all(entity_fields %in% names(data))) stop("Every `entity_fields` entry must exist in the data.", call. = FALSE)
  if (!is.character(required_fields) || any(!nzchar(required_fields)) || anyDuplicated(required_fields)) {
    stop("`required_fields` must be a vector of unique field names.", call. = FALSE)
  }
  absent <- setdiff(required_fields, names(data))
  if (length(absent)) stop(sprintf("Required fields are absent: %s.", paste(absent, collapse = ", ")), call. = FALSE)

  units <- .normalize_units(units, names(data))
  source <- .normalize_dataset_source(source, id)
  if (!is.list(geography)) stop("`geography` must be a list.", call. = FALSE)
  if (!is.list(sector)) stop("`sector` must be a list.", call. = FALSE)
  if (!is.list(currency)) stop("`currency` must be a list.", call. = FALSE)
  if (!is.list(transformations)) stop("`transformations` must be a list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)

  check_fields <- unique(c(required_fields, time_field, entity_fields))
  check_fields <- check_fields[nzchar(check_fields)]
  if (missing_policy == "drop" && length(check_fields)) {
    data <- data[stats::complete.cases(data[check_fields]), , drop = FALSE]
    rownames(data) <- NULL
  }
  quality <- .dataset_quality(data, time_field, entity_fields)
  if (missing_policy == "error" && quality$missing_cells > 0L) {
    stop("Missing values violate the selected `missing_policy`.", call. = FALSE)
  }
  if (nrow(quality$flags) && any(quality$flags$severity == "error")) {
    stop(paste(quality$flags$message[quality$flags$severity == "error"], collapse = " "), call. = FALSE)
  }

  structure(list(
    schema_version = .catalyst_dataset_schema_version(),
    id = id,
    title = title,
    data = data,
    fields = lapply(names(data), function(field) list(
      name = field,
      type = class(data[[field]])[1L],
      unit = if (field %in% names(units)) units[[field]] else NULL,
      required = field %in% required_fields
    )),
    time_field = time_field,
    entity_fields = entity_fields,
    units = units,
    source = source,
    geography = geography,
    sector = sector,
    currency = currency,
    missing_policy = missing_policy,
    transformations = transformations,
    quality = quality,
    metadata = utils::modifyList(list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now()
    ), metadata)
  ), class = "catalyst_dataset")
}

#' Read CSV or JSON data into a governed Catalyst dataset
#'
#' @param path Local CSV or JSON file path.
#' @param format `auto`, `csv`, or `json`.
#' @param ... Arguments forwarded to [as_catalyst_dataset()].
#' @return A `catalyst_dataset`.
#' @export
read_catalyst_data <- function(path, format = c("auto", "csv", "json"), ...) {
  .assert_single_string(path, "path")
  if (!file.exists(path)) stop("Data file does not exist.", call. = FALSE)
  format <- match.arg(format)
  if (format == "auto") {
    extension <- tolower(tools::file_ext(path))
    format <- if (extension %in% c("csv", "json")) extension else stop("Could not infer data format from the file extension.", call. = FALSE)
  }
  data <- if (format == "csv") {
    utils::read.csv(path, stringsAsFactors = FALSE, check.names = FALSE, na.strings = c("", "NA", "N/A", "null"))
  } else {
    value <- jsonlite::fromJSON(path, simplifyDataFrame = TRUE)
    if (is.list(value) && !is.data.frame(value) && "data" %in% names(value)) value <- value$data
    if (!is.data.frame(value)) value <- as.data.frame(value, stringsAsFactors = FALSE)
    value
  }
  dots <- list(...)
  if (is.null(dots$source)) {
    dots$source <- dataset_source(
      id = paste0(tools::file_path_sans_ext(basename(path)), "-file"),
      title = basename(path),
      metadata = list(
        local_path = normalizePath(path, winslash = "/", mustWork = TRUE),
        md5 = unname(tools::md5sum(path))
      )
    )
  }
  do.call(as_catalyst_dataset, c(list(data = data), dots))
}

#' Validate a Catalyst dataset
#'
#' @param dataset A `catalyst_dataset`.
#' @param strict When TRUE, warnings in the quality report are treated as errors.
#' @return Invisibly returns TRUE when valid.
#' @export
validate_catalyst_dataset <- function(dataset, strict = FALSE) {
  .assert_flag(strict, "strict")
  if (!inherits(dataset, "catalyst_dataset")) stop("`dataset` must inherit from `catalyst_dataset`.", call. = FALSE)
  required <- c("schema_version", "id", "title", "data", "source", "quality", "metadata")
  if (!all(required %in% names(dataset))) stop("Dataset object is incomplete.", call. = FALSE)
  if (!identical(dataset$schema_version, .catalyst_dataset_schema_version())) stop("Unsupported dataset schema version.", call. = FALSE)
  if (!is.data.frame(dataset$data)) stop("Dataset data must remain a data frame.", call. = FALSE)
  if (strict && nrow(dataset$quality$flags)) {
    stop(paste(dataset$quality$flags$message, collapse = " "), call. = FALSE)
  }
  invisible(TRUE)
}

.dataset_contract_record <- function(dataset, include_data = TRUE) {
  validate_catalyst_dataset(dataset)
  list(
    schema_version = dataset$schema_version,
    id = dataset$id,
    title = dataset$title,
    fields = dataset$fields,
    time_field = dataset$time_field,
    entity_fields = unname(dataset$entity_fields),
    units = dataset$units,
    source = dataset$source,
    geography = dataset$geography,
    sector = dataset$sector,
    currency = dataset$currency,
    missing_policy = dataset$missing_policy,
    transformations = dataset$transformations,
    quality = utils::modifyList(dataset$quality, list(flags = if (nrow(dataset$quality$flags)) {
      unname(lapply(seq_len(nrow(dataset$quality$flags)), function(i) as.list(dataset$quality$flags[i, , drop = FALSE])))
    } else list()), keep.null = TRUE),
    metadata = dataset$metadata,
    data = if (include_data) dataset$data else NULL
  )
}

#' Compute a stable dataset fingerprint
#'
#' @param dataset A `catalyst_dataset`.
#' @return MD5 fingerprint of the dataset contract and records.
#' @export
dataset_fingerprint <- function(dataset) {
  record <- .dataset_contract_record(dataset, include_data = TRUE)
  # Contract identity excludes volatile runtime metadata and machine-local paths.
  if (is.list(record$metadata)) {
    record$metadata$created_at <- NULL
    record$metadata$updated_at <- NULL
  }
  if (is.list(record$source) && is.list(record$source$metadata)) {
    record$source$metadata$local_path <- NULL
  }
  path <- tempfile(fileext = ".json")
  on.exit(unlink(path), add = TRUE)
  jsonlite::write_json(.safe_json_value(record), path, auto_unbox = TRUE, pretty = FALSE, null = "null", digits = NA)
  unname(tools::md5sum(path))
}

#' Summarize a Catalyst dataset contract
#'
#' @param dataset A `catalyst_dataset`.
#' @param include_data Include records in the returned manifest.
#' @return A machine-readable dataset manifest.
#' @export
dataset_manifest <- function(dataset, include_data = FALSE) {
  .assert_flag(include_data, "include_data")
  record <- .dataset_contract_record(dataset, include_data = include_data)
  record$fingerprint <- dataset_fingerprint(dataset)
  record
}

#' Return dataset quality diagnostics
#'
#' @param dataset A `catalyst_dataset`.
#' @return A list containing summary counts and a flag table.
#' @export
data_quality_report <- function(dataset) {
  validate_catalyst_dataset(dataset)
  dataset$quality
}

#' Record a dataset transformation
#'
#' @param dataset A `catalyst_dataset`.
#' @param operation Stable operation identifier.
#' @param description Human-readable description.
#' @param fields Affected fields.
#' @param parameters Named operation parameters.
#' @param actor Optional actor or process identifier.
#' @param occurred_at UTC timestamp.
#' @return Updated `catalyst_dataset`.
#' @export
add_dataset_transformation <- function(
  dataset,
  operation,
  description,
  fields = character(),
  parameters = list(),
  actor = "",
  occurred_at = .utc_now()
) {
  validate_catalyst_dataset(dataset)
  .assert_single_string(operation, "operation")
  .assert_single_string(description, "description")
  if (!is.character(fields) || !all(fields %in% names(dataset$data))) stop("`fields` must reference dataset columns.", call. = FALSE)
  if (!is.list(parameters)) stop("`parameters` must be a list.", call. = FALSE)
  .assert_single_string(actor, "actor", allow_empty = TRUE)
  .assert_single_string(occurred_at, "occurred_at")
  dataset$transformations[[length(dataset$transformations) + 1L]] <- list(
    operation = operation,
    description = description,
    fields = unname(fields),
    parameters = parameters,
    actor = actor,
    occurred_at = occurred_at
  )
  dataset$metadata$updated_at <- .utc_now()
  dataset
}

.catalyst_unit_registry <- new.env(parent = emptyenv())

.ensure_builtin_unit_conversions <- function() {
  builtins <- list(
    list("kg", "t", 0.001, 0, "mass"),
    list("g", "kg", 0.001, 0, "mass"),
    list("kWh", "MWh", 0.001, 0, "energy"),
    list("MWh", "GWh", 0.001, 0, "energy"),
    list("fraction", "percent", 100, 0, "ratio"),
    list("tCO2e", "kgCO2e", 1000, 0, "emissions")
  )
  for (entry in builtins) {
    key <- paste(entry[[1]], entry[[2]], sep = "->")
    if (!exists(key, envir = .catalyst_unit_registry, inherits = FALSE)) {
      assign(key, list(from = entry[[1]], to = entry[[2]], multiplier = entry[[3]], offset = entry[[4]], dimension = entry[[5]]), envir = .catalyst_unit_registry)
      reverse <- paste(entry[[2]], entry[[1]], sep = "->")
      assign(reverse, list(from = entry[[2]], to = entry[[1]], multiplier = 1 / entry[[3]], offset = -entry[[4]] / entry[[3]], dimension = entry[[5]]), envir = .catalyst_unit_registry)
    }
  }
  invisible(NULL)
}

#' Register a linear unit conversion
#'
#' @param from Source unit.
#' @param to Destination unit.
#' @param multiplier Linear multiplier.
#' @param offset Linear offset applied after multiplication.
#' @param dimension Shared measurement dimension.
#' @param reciprocal Register the mathematically reversible conversion.
#' @param overwrite Replace an existing conversion.
#' @return Invisibly returns the conversion record.
#' @export
register_unit_conversion <- function(from, to, multiplier, offset = 0, dimension, reciprocal = TRUE, overwrite = FALSE) {
  .assert_single_string(from, "from")
  .assert_single_string(to, "to")
  .assert_scalar_number(multiplier, "multiplier")
  if (multiplier == 0) stop("`multiplier` cannot be zero.", call. = FALSE)
  .assert_scalar_number(offset, "offset")
  .assert_single_string(dimension, "dimension")
  .assert_flag(reciprocal, "reciprocal")
  .assert_flag(overwrite, "overwrite")
  .ensure_builtin_unit_conversions()
  key <- paste(from, to, sep = "->")
  if (exists(key, envir = .catalyst_unit_registry, inherits = FALSE) && !overwrite) stop("Unit conversion is already registered.", call. = FALSE)
  record <- list(from = from, to = to, multiplier = multiplier, offset = offset, dimension = dimension)
  assign(key, record, envir = .catalyst_unit_registry)
  if (reciprocal) {
    assign(paste(to, from, sep = "->"), list(from = to, to = from, multiplier = 1 / multiplier, offset = -offset / multiplier, dimension = dimension), envir = .catalyst_unit_registry)
  }
  invisible(record)
}

#' List registered unit conversions
#'
#' @return A data frame of unit conversions.
#' @export
list_unit_conversions <- function() {
  .ensure_builtin_unit_conversions()
  keys <- ls(envir = .catalyst_unit_registry, all.names = TRUE)
  if (!length(keys)) return(data.frame(from = character(), to = character(), multiplier = numeric(), offset = numeric(), dimension = character(), stringsAsFactors = FALSE))
  rows <- lapply(keys, function(key) as.data.frame(get(key, envir = .catalyst_unit_registry), stringsAsFactors = FALSE))
  result <- do.call(rbind, rows)
  rownames(result) <- NULL
  result[order(result$dimension, result$from, result$to), , drop = FALSE]
}

#' Convert one numeric dataset field to another registered unit
#'
#' @param dataset A `catalyst_dataset`.
#' @param field Numeric field to convert.
#' @param to_unit Destination unit.
#' @return Updated `catalyst_dataset` with transformation history.
#' @export
convert_dataset_unit <- function(dataset, field, to_unit) {
  validate_catalyst_dataset(dataset)
  .assert_single_string(field, "field")
  .assert_single_string(to_unit, "to_unit")
  if (!field %in% names(dataset$data)) stop("`field` is not present in the dataset.", call. = FALSE)
  if (!is.numeric(dataset$data[[field]])) stop("Unit conversion requires a numeric field.", call. = FALSE)
  if (!field %in% names(dataset$units)) stop("The dataset does not declare a unit for this field.", call. = FALSE)
  from_unit <- dataset$units[[field]]
  .ensure_builtin_unit_conversions()
  key <- paste(from_unit, to_unit, sep = "->")
  if (!exists(key, envir = .catalyst_unit_registry, inherits = FALSE)) stop(sprintf("No conversion is registered from `%s` to `%s`.", from_unit, to_unit), call. = FALSE)
  conversion <- get(key, envir = .catalyst_unit_registry, inherits = FALSE)
  dataset$data[[field]] <- dataset$data[[field]] * conversion$multiplier + conversion$offset
  dataset$units[[field]] <- to_unit
  for (i in seq_along(dataset$fields)) {
    if (identical(dataset$fields[[i]]$name, field)) dataset$fields[[i]]$unit <- to_unit
  }
  dataset$quality <- .dataset_quality(dataset$data, dataset$time_field, dataset$entity_fields)
  add_dataset_transformation(
    dataset,
    operation = "unit_conversion",
    description = sprintf("Converted `%s` from %s to %s.", field, from_unit, to_unit),
    fields = field,
    parameters = conversion
  )
}

#' @export
print.catalyst_dataset <- function(x, ...) {
  cat("<catalyst_dataset>\n")
  cat("  id:          ", x$id, "\n", sep = "")
  cat("  title:       ", x$title, "\n", sep = "")
  cat("  dimensions:  ", nrow(x$data), " x ", ncol(x$data), "\n", sep = "")
  cat("  source:      ", x$source$title, "\n", sep = "")
  cat("  quality flags: ", nrow(x$quality$flags), "\n", sep = "")
  invisible(x)
}
