#' Export a governed data-and-indicator analysis bundle
#'
#' Writes the source records, dataset contract, quality report, transformation
#' history, indicator definitions, calculated values, trace metadata, and file
#' inventory needed to audit a Catalyst data analysis.
#'
#' @param dataset A `catalyst_dataset`.
#' @param indicators Optional `catalyst_indicator_result`,
#'   `catalyst_indicator_set`, or indicator collection to calculate.
#' @param dir Parent output directory.
#' @param analysis_id Stable bundle identifier.
#' @param group_by Optional grouping fields used when calculating indicators.
#' @param na_rm Remove missing values in supported aggregate calculations.
#' @param zip Create a ZIP archive.
#' @param overwrite Replace an existing bundle.
#' @param quiet Suppress informational messages.
#' @return Invisibly returns paths, manifest, and file inventory.
#' @export
export_data_analysis <- function(
  dataset,
  indicators = NULL,
  dir,
  analysis_id = NULL,
  group_by = character(),
  na_rm = FALSE,
  zip = TRUE,
  overwrite = FALSE,
  quiet = FALSE
) {
  validate_catalyst_dataset(dataset)
  .assert_single_string(dir, "dir")
  .assert_flag(na_rm, "na_rm")
  .assert_flag(zip, "zip")
  .assert_flag(overwrite, "overwrite")
  .assert_flag(quiet, "quiet")
  if (is.null(analysis_id)) analysis_id <- paste0(dataset$id, "-", format(Sys.time(), "%Y%m%d-%H%M%S"))
  .assert_single_string(analysis_id, "analysis_id")
  safe_id <- gsub("[^A-Za-z0-9._-]+", "-", trimws(analysis_id))
  safe_id <- gsub("^-+|-+$", "", safe_id)
  if (!nzchar(safe_id)) stop("`analysis_id` must contain a usable character.", call. = FALSE)

  indicator_set <- NULL
  if (!is.null(indicators)) {
    if (inherits(indicators, "catalyst_indicator_result")) {
      indicator_set <- structure(list(
        dataset_id = dataset$id,
        results = stats::setNames(list(indicators), indicators$definition$id),
        values = indicators$values,
        meta = list(schema_version = "1.0.0", calculated_at = .utc_now(), package_version = .catalyst_package_version(), indicator_count = 1L)
      ), class = "catalyst_indicator_set")
    } else if (inherits(indicators, "catalyst_indicator_set")) {
      indicator_set <- indicators
    } else {
      indicator_set <- calculate_indicators(dataset, indicators, group_by = group_by, na_rm = na_rm)
    }
    if (!identical(indicator_set$dataset_id, dataset$id)) stop("Indicator results belong to a different dataset.", call. = FALSE)
  }

  if (!dir.exists(dir) && !dir.create(dir, recursive = TRUE, showWarnings = FALSE)) stop("Could not create output directory.", call. = FALSE)
  out_dir <- file.path(dir, paste0("data_analysis_", safe_id))
  if (dir.exists(out_dir)) {
    if (!overwrite) stop("Output bundle already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
    unlink(out_dir, recursive = TRUE, force = TRUE)
  }
  if (!dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)) stop("Could not create bundle directory.", call. = FALSE)

  written <- character()
  write_json <- function(name, value) {
    path <- file.path(out_dir, paste0(name, ".json"))
    jsonlite::write_json(.safe_json_value(value), path, auto_unbox = TRUE, pretty = TRUE, null = "null", digits = NA)
    written <<- c(written, path)
    path
  }
  write_csv <- function(name, value) {
    if (!is.data.frame(value)) return(NULL)
    path <- file.path(out_dir, paste0(name, ".csv"))
    utils::write.csv(value, path, row.names = FALSE, na = "")
    written <<- c(written, path)
    path
  }

  write_csv("data", dataset$data)
  write_json("dataset_manifest", dataset_manifest(dataset, include_data = FALSE))
  write_json("source", dataset$source)
  write_csv("quality_flags", dataset$quality$flags)
  write_json("transformations", dataset$transformations)

  if (!is.null(indicator_set)) {
    write_csv("indicator_values", indicator_set$values)
    write_json("indicator_definitions", lapply(indicator_set$results, function(result) .indicator_contract_record(result$definition)))
    write_json("indicator_trace", indicator_trace(indicator_set))
  }

  inventory <- function(paths) {
    if (!length(paths)) return(list())
    info <- file.info(paths)
    hashes <- unname(tools::md5sum(paths))
    unname(lapply(seq_along(paths), function(i) list(
      path = basename(paths[i]),
      bytes = unname(info$size[i]),
      md5 = hashes[i]
    )))
  }

  manifest <- list(
    schema_version = "1.0.0",
    analysis_id = safe_id,
    created_at = .utc_now(),
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    dataset = list(
      id = dataset$id,
      title = dataset$title,
      fingerprint = dataset_fingerprint(dataset),
      rows = nrow(dataset$data),
      columns = ncol(dataset$data),
      source_id = dataset$source$id,
      quality_flags = nrow(dataset$quality$flags)
    ),
    indicators = if (is.null(indicator_set)) list() else unname(lapply(indicator_set$results, function(result) list(
      id = result$definition$id,
      version = result$definition$version,
      unit = result$definition$unit,
      output_rows = nrow(result$values)
    ))),
    boundaries = list(
      source_quality_requires_review = TRUE,
      unit_compatibility_requires_review = TRUE,
      causal_claim = FALSE,
      autonomous_decision = FALSE
    ),
    files = inventory(written)
  )
  manifest_path <- write_json("manifest", manifest)

  zip_path <- NULL
  if (zip) {
    zip_path <- file.path(dir, paste0("data_analysis_", safe_id, ".zip"))
    if (file.exists(zip_path)) {
      if (!overwrite) stop("ZIP archive already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
      unlink(zip_path)
    }
    old <- setwd(out_dir)
    on.exit(setwd(old), add = TRUE)
    files <- list.files(".", recursive = TRUE, all.files = FALSE, no.. = TRUE)
    utils::zip(zipfile = zip_path, files = files, flags = "-q")
    setwd(old)
  }

  if (!quiet) message("Data analysis bundle written to ", out_dir)
  invisible(list(
    directory = out_dir,
    zip = zip_path,
    manifest = manifest,
    files = written
  ))
}
