#' Export a Catalyst results bundle
#'
#' Writes reproducible CSV, JSON, plot, and manifest outputs from a
#' `catalyst_run` object or compatible result list.
#'
#' @param results A `catalyst_run` object or compatible result list.
#' @param dir Parent output directory.
#' @param run_id Label used for folder and archive names.
#' @param zip Logical. If TRUE, create a zip archive.
#' @param overwrite Logical. If TRUE, replace existing outputs.
#' @param open Logical. If TRUE on macOS, open the output folder.
#' @param quiet Logical. If TRUE, suppress messages.
#' @return Invisibly returns bundle paths, manifest, and written-file inventory.
#' @export
#'
#' @examples
#' \dontrun{
#' x <- catalyst_demo()
#' export_catalyst_bundle(x, tempdir(), "demo", zip = FALSE, quiet = TRUE)
#' }
export_catalyst_bundle <- function(
  results,
  dir,
  run_id = NULL,
  zip = TRUE,
  overwrite = FALSE,
  open = FALSE,
  quiet = FALSE
) {
  if (!is.list(results)) stop("`results` must be a list.", call. = FALSE)
  .assert_single_string(dir, "dir")
  .assert_flag(zip, "zip")
  .assert_flag(overwrite, "overwrite")
  .assert_flag(open, "open")
  .assert_flag(quiet, "quiet")

  if (is.null(run_id)) run_id <- format(Sys.time(), "%Y%m%d_%H%M%S")
  .assert_single_string(run_id, "run_id")
  safe_run_id <- gsub("[^A-Za-z0-9._-]+", "-", trimws(run_id))
  safe_run_id <- gsub("^-+|-+$", "", safe_run_id)
  if (!nzchar(safe_run_id)) stop("`run_id` must contain a usable character.", call. = FALSE)

  if (!dir.exists(dir) && !dir.create(dir, recursive = TRUE, showWarnings = FALSE)) {
    stop("Could not create output directory.", call. = FALSE)
  }
  out_dir <- file.path(dir, paste0("bundle_", safe_run_id))
  if (dir.exists(out_dir)) {
    if (!overwrite) stop("Output bundle already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
    unlink(out_dir, recursive = TRUE, force = TRUE)
  }
  if (!dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)) {
    stop("Could not create bundle directory.", call. = FALSE)
  }

  written <- character()
  write_df <- function(name, value) {
    if (!is.data.frame(value)) return(NULL)
    path <- file.path(out_dir, paste0(name, ".csv"))
    utils::write.csv(value, path, row.names = FALSE, na = "")
    written <<- c(written, path)
    path
  }
  write_json <- function(name, value) {
    if (is.null(value)) return(NULL)
    path <- file.path(out_dir, paste0(name, ".json"))
    jsonlite::write_json(.safe_json_value(value), path, auto_unbox = TRUE, pretty = TRUE, null = "null")
    written <<- c(written, path)
    path
  }
  as_one_row_df <- function(value) {
    if (is.null(value)) return(NULL)
    if (is.data.frame(value)) return(value)
    if (is.list(value) && !is.null(names(value))) {
      return(as.data.frame(value, stringsAsFactors = FALSE))
    }
    NULL
  }

  write_df("trajectory_wide", results$trajectory_wide)
  write_df("trajectory_long", results$trajectory_long)
  write_df("sdg_indicators", results$sdg_indicators)
  indicator_definitions <- list()
  if (is.data.frame(results$sdg_indicators) && "indicator" %in% names(results$sdg_indicators)) {
    indicator_ids <- unique(as.character(results$sdg_indicators$indicator))
    for (indicator_id in indicator_ids) {
      definition <- tryCatch(get_catalyst_indicator(indicator_id), error = function(error) NULL)
      if (!is.null(definition)) indicator_definitions[[indicator_id]] <- .indicator_contract_record(definition)
    }
  }
  if (length(indicator_definitions)) write_json("indicator_definitions", indicator_definitions)
  write_df("phase_plane", results$phase_plane)
  write_df("sensitivities", results$sensitivities)
  write_df("carbon_budget", as_one_row_df(results$carbon_budget))
  write_df("scorecard", results$scorecard)

  meta <- if (is.list(results$meta)) results$meta else list()
  write_df("parameters", .named_list_table(meta$params))
  write_df("policy", .named_list_table(meta$policy))
  write_json("run_metadata", meta)

  scenario_fingerprint_value <- NULL
  if (!is.null(results$scenario)) {
    scenario <- as_catalyst_scenario(results$scenario)
    scenario_path <- file.path(out_dir, "scenario.json")
    scenario_to_json(scenario, path = scenario_path, pretty = TRUE)
    written <- c(written, scenario_path)
    scenario_fingerprint_value <- scenario_fingerprint(scenario)
  }

  if (is.list(results$plots)) {
    for (name in names(results$plots)) {
      plot <- results$plots[[name]]
      if (inherits(plot, "ggplot")) {
        image_path <- file.path(out_dir, paste0(name, ".png"))
        save_plot(plot, image_path)
        written <- c(written, image_path)
      }
    }
  }

  inventory <- function(paths) {
    if (length(paths) == 0L) return(list())
    info <- file.info(paths)
    hashes <- unname(tools::md5sum(paths))
    unname(lapply(seq_along(paths), function(i) {
      list(
        path = basename(paths[i]),
        bytes = unname(info$size[i]),
        md5 = hashes[i]
      )
    }))
  }

  manifest <- list(
    schema_version = "1.2.0",
    package = "catalystanalyticsr",
    package_version = .catalyst_package_version(),
    model = if (!is.null(meta$model)) meta$model else NULL,
    model_version = if (!is.null(meta$model_version)) meta$model_version else NULL,
    model_contract_version = if (!is.null(meta$model_contract_version)) meta$model_contract_version else NULL,
    run_id = safe_run_id,
    requested_run_id = run_id,
    scenario_schema_version = if (!is.null(results$scenario)) results$scenario$schema_version else NULL,
    scenario_fingerprint = scenario_fingerprint_value,
    indicator_registry_version = if (length(indicator_definitions)) "1.0.0" else NULL,
    indicator_definitions = names(indicator_definitions),
    created_at = format(Sys.time(), tz = "UTC", usetz = TRUE),
    files = basename(written),
    file_inventory = inventory(written)
  )
  manifest_path <- file.path(out_dir, "manifest.json")
  jsonlite::write_json(.safe_json_value(manifest), manifest_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
  written <- c(written, manifest_path)

  if (!quiet) message("Bundle written to: ", out_dir)
  if (open && identical(Sys.info()[["sysname"]], "Darwin")) {
    try(system2("open", out_dir), silent = TRUE)
  }

  zip_path <- NULL
  if (zip) {
    zip_path <- file.path(dir, paste0("bundle_", safe_run_id, ".zip"))
    if (file.exists(zip_path) && !overwrite) {
      stop("Zip file already exists. Set `overwrite = TRUE` to replace.", call. = FALSE)
    }
    if (file.exists(zip_path)) unlink(zip_path, force = TRUE)
    files_to_zip <- list.files(out_dir, all.files = TRUE, recursive = TRUE, no.. = TRUE)
    old <- getwd()
    on.exit(setwd(old), add = TRUE)
    setwd(out_dir)
    utils::zip(zipfile = zip_path, files = files_to_zip)
  }

  invisible(list(
    bundle_dir = out_dir,
    zip_path = zip_path,
    manifest = manifest,
    written = written
  ))
}
