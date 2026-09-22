#' Export climate, carbon, and natural-capital accounting
#'
#' Writes normalized inventory records, carbon-budget pathways, Kaya
#' decomposition, natural-capital accounts, boundary assessments, diagnostic
#' tables, methodology metadata, and a file-integrity manifest.
#'
#' @param analysis A `catalyst_climate_accounting`.
#' @param dir Parent output directory.
#' @param prefix Optional stable bundle prefix.
#' @param zip_bundle Create a ZIP archive.
#' @param overwrite Replace an existing bundle.
#' @param quiet Suppress informational messages.
#' @return Invisibly returns bundle paths, manifest, and files.
#' @export
export_climate_accounting <- function(
  analysis,
  dir,
  prefix = analysis$id,
  zip_bundle = TRUE,
  overwrite = FALSE,
  quiet = FALSE
) {
  if (!inherits(analysis, "catalyst_climate_accounting")) stop("`analysis` must be a climate-accounting object.", call. = FALSE)
  .assert_single_string(dir, "dir")
  .assert_single_string(prefix, "prefix")
  .assert_flag(zip_bundle, "zip_bundle")
  .assert_flag(overwrite, "overwrite")
  .assert_flag(quiet, "quiet")
  safe_prefix <- gsub("[^A-Za-z0-9._-]+", "-", trimws(prefix))
  safe_prefix <- gsub("^-+|-+$", "", safe_prefix)
  if (!nzchar(safe_prefix)) stop("`prefix` must contain a usable character.", call. = FALSE)
  if (!dir.exists(dir) && !dir.create(dir, recursive = TRUE, showWarnings = FALSE)) stop("Could not create output directory.", call. = FALSE)
  out_dir <- file.path(dir, paste0("climate_accounting_", safe_prefix))
  if (dir.exists(out_dir)) {
    if (!overwrite) stop("Output bundle already exists. Set `overwrite = TRUE` to replace it.", call. = FALSE)
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
    if (is.null(value) || !is.data.frame(value)) return(NULL)
    path <- file.path(out_dir, paste0(name, ".csv"))
    utils::write.csv(value, path, row.names = FALSE, na = "")
    written <<- c(written, path)
    path
  }

  write_json("inventory_manifest", emissions_inventory_manifest(analysis$inventory, include_data = FALSE))
  write_csv("emissions_inventory", analysis$inventory$data)
  write_csv("emissions_summary", emissions_inventory_summary(analysis$inventory))
  write_csv("carbon_pathway", analysis$carbon_pathway$pathway)
  write_csv("carbon_diagnostics", analysis$carbon_pathway$diagnostics)
  write_csv("terminal_values", analysis$terminal_values)
  if (!is.null(analysis$kaya)) {
    write_csv("kaya_levels", analysis$kaya$levels)
    write_csv("kaya_contributions", analysis$kaya$contributions)
    write_json("kaya_methodology", analysis$kaya$meta)
  }
  if (!is.null(analysis$natural_capital)) {
    write_csv("natural_capital_account", analysis$natural_capital$data)
    write_csv("natural_capital_summary", natural_capital_summary(analysis$natural_capital))
    write_json("natural_capital_metadata", list(
      schema_version = analysis$natural_capital$schema_version,
      id = analysis$natural_capital$id,
      title = analysis$natural_capital$title,
      unit = analysis$natural_capital$unit,
      meta = analysis$natural_capital$meta
    ))
  }
  if (!is.null(analysis$boundary_assessment)) {
    write_json("boundary_definitions", analysis$boundary_assessment$definitions)
    write_csv("boundary_assessment", analysis$boundary_assessment$assessment)
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

  brief <- c(
    paste0("# ", analysis$title),
    "",
    paste0("- Analysis id: `", analysis$id, "`"),
    paste0("- Package version: `", .catalyst_package_version(), "`"),
    paste0("- Inventory: `", analysis$inventory$id, "`"),
    paste0("- Carbon groups: ", nrow(analysis$carbon_pathway$diagnostics)),
    paste0("- Groups beyond budget: ", sum(!analysis$carbon_pathway$diagnostics$within_budget)),
    paste0("- Stranded-pathway signals: ", sum(analysis$carbon_pathway$diagnostics$stranded_pathway_signal)),
    paste0("- Kaya decomposition included: ", if (!is.null(analysis$kaya)) "yes" else "no"),
    paste0("- Natural-capital account included: ", if (!is.null(analysis$natural_capital)) "yes" else "no"),
    paste0("- Boundary assessment included: ", if (!is.null(analysis$boundary_assessment)) "yes" else "no"),
    "",
    "## Review boundary",
    "",
    "These accounts are analytical records. Source boundaries, carbon-budget allocation, GWP basis, natural-capital valuation, and interpretation require human review."
  )
  brief_path <- file.path(out_dir, "brief.md")
  writeLines(brief, brief_path, useBytes = TRUE)
  written <- c(written, brief_path)

  manifest <- list(
    schema_version = .catalyst_climate_accounting_schema_version(),
    analysis_id = analysis$id,
    title = analysis$title,
    created_at = .utc_now(),
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    contracts = list(
      emissions_inventory = analysis$inventory$schema_version,
      carbon_pathway = analysis$carbon_pathway$schema_version,
      climate_accounting = analysis$schema_version,
      natural_capital = if (is.null(analysis$natural_capital)) NULL else analysis$natural_capital$schema_version,
      boundary_assessment = if (is.null(analysis$boundary_assessment)) NULL else analysis$boundary_assessment$schema_version
    ),
    inventory = list(
      id = analysis$inventory$id,
      dataset_id = analysis$inventory$dataset_id,
      dataset_fingerprint = analysis$inventory$dataset_fingerprint,
      unit = analysis$inventory$unit,
      accounting_basis = analysis$inventory$accounting_basis,
      row_count = nrow(analysis$inventory$data)
    ),
    carbon = list(
      groups = nrow(analysis$carbon_pathway$diagnostics),
      overshoot_groups = sum(!analysis$carbon_pathway$diagnostics$within_budget),
      stranded_pathway_signals = sum(analysis$carbon_pathway$diagnostics$stranded_pathway_signal)
    ),
    included = list(
      kaya = !is.null(analysis$kaya),
      natural_capital = !is.null(analysis$natural_capital),
      boundary_assessment = !is.null(analysis$boundary_assessment)
    ),
    review_boundaries = list(
      source_and_scope_review_required = TRUE,
      carbon_budget_allocation_review_required = TRUE,
      global_warming_potential_basis_review_required = TRUE,
      natural_capital_valuation_review_required = TRUE,
      causal_claim = FALSE,
      autonomous_decision = FALSE
    ),
    files = inventory(written)
  )
  write_json("manifest", manifest)


  zip_path <- NULL
  if (zip_bundle) {
    zip_path <- file.path(dir, paste0("climate_accounting_", safe_prefix, ".zip"))
    if (file.exists(zip_path)) {
      if (!overwrite) stop("ZIP archive already exists. Set `overwrite = TRUE` to replace it.", call. = FALSE)
      unlink(zip_path)
    }
    old <- setwd(out_dir)
    on.exit(setwd(old), add = TRUE)
    files <- list.files(".", recursive = TRUE, all.files = FALSE, no.. = TRUE)
    utils::zip(zipfile = zip_path, files = files, flags = "-q")
    setwd(old)
  }

  if (!quiet) message("Climate accounting bundle written to ", out_dir)
  invisible(list(directory = out_dir, zip = zip_path, manifest = manifest, files = written))
}
