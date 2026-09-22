#' Export first-party Sustainable Catalyst handoffs
#'
#' @param project A reproducible project.
#' @param dir Parent export directory.
#' @param prefix Bundle directory and archive prefix.
#' @param targets Platform targets to include.
#' @param options Named target-specific option lists.
#' @param zip_bundle Create a ZIP archive.
#' @return Named generated paths.
#' @export
export_platform_handoffs <- function(project, dir = ".", prefix = "catalyst-platform-handoffs",
                                     targets = c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library", "workspace"),
                                     options = list(), zip_bundle = TRUE) {
  validate_catalyst_project(project); .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(zip_bundle, "zip_bundle")
  valid_targets <- c("site_intelligence", "research_lab", "workbench", "catalyst_canvas", "decision_studio", "knowledge_library", "workspace")
  if (!is.character(targets) || !length(targets) || anyNA(targets) || length(setdiff(targets, valid_targets))) stop("`targets` contains unsupported platform products.", call. = FALSE)
  if (!is.list(options)) stop("`options` must be a list.", call. = FALSE)
  targets <- unique(targets)
  bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(bundle_dir = bundle_dir)
  handoffs <- list()
  for (target in targets) {
    target_options <- if (is.null(options[[target]])) list() else options[[target]]
    handoff <- platform_handoff(project, target, target_options)
    path <- file.path(bundle_dir, paste0(gsub("_", "-", target), "-handoff.json"))
    handoff_to_json(handoff, path)
    paths[[target]] <- path; handoffs[[target]] <- handoff
  }
  index <- data.frame(
    target = targets,
    handoff_type = vapply(handoffs, function(x) x$handoff_type, character(1)),
    file = vapply(targets, function(x) basename(paths[[x]]), character(1)),
    project_fingerprint = vapply(handoffs, function(x) x$project_fingerprint, character(1)),
    review_status = vapply(handoffs, function(x) x$review$status, character(1)),
    stringsAsFactors = FALSE
  )
  paths$index <- file.path(bundle_dir, "handoff-index.csv"); utils::write.csv(index, paths$index, row.names = FALSE)
  paths$api_manifest <- file.path(bundle_dir, "public-api-manifest.json")
  jsonlite::write_json(.safe_json_value(catalyst_public_api_manifest()), paths$api_manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  readme <- c(
    paste0("# ", project$title, " - Sustainable Catalyst platform handoffs"), "",
    paste0("Project ID: `", project$id, "`  "), paste0("Project fingerprint: `", project_fingerprint(project), "`  "),
    paste0("Package: Catalyst Analytics R ", .catalyst_package_version()), "", "## Included targets",
    paste0("- ", targets), "", "## Use boundary",
    "These files are structured handoffs, not autonomous commands. Receiving products must validate contract versions, preserve provenance, disclose limitations, and require human review before publication or decision use."
  )
  paths$readme <- file.path(bundle_dir, "README.md"); writeLines(readme, paths$readme, useBytes = TRUE)
  files <- list.files(bundle_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE)
  base <- normalizePath(bundle_dir)
  records <- lapply(files, function(path) list(file = substring(normalizePath(path), nchar(base) + 2L), bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path))))
  manifest <- list(
    schema_version = "1.0.0", export_type = "sustainable_catalyst_platform_handoff_bundle",
    project_id = project$id, project_fingerprint = project_fingerprint(project), targets = targets,
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), created_at = .utc_now(),
    file_count = length(records), files = records,
    integrity = list(hash_algorithm = "md5", complete = TRUE, scope = "all_bundle_files_except_manifest"),
    boundary = list(human_review_required = TRUE, receiving_products_must_validate_contracts = TRUE, automated_platform_action = FALSE)
  )
  paths$manifest <- file.path(bundle_dir, "manifest.json")
  jsonlite::write_json(manifest, paths$manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (zip_bundle) {
    paths$zip <- file.path(dir, paste0(prefix, ".zip")); old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir); utils::zip(zipfile = basename(paths$zip), files = prefix)
  }
  paths
}

#' Add a platform handoff to a workspace
#'
#' @param workspace A workspace.
#' @param handoff Platform handoff.
#' @param replace Replace an existing handoff.
#' @return Updated workspace.
#' @export
workspace_add_platform_handoff <- function(workspace, handoff, replace = FALSE) {
  validate_catalyst_workspace(workspace); validate_platform_handoff(handoff); .assert_flag(replace, "replace")
  if (is.null(workspace$libraries$platform_handoffs)) workspace$libraries$platform_handoffs <- list()
  id <- paste(handoff$project_id, handoff$target, sep = "--")
  if (!is.null(workspace$libraries$platform_handoffs[[id]]) && !replace) stop("Platform handoff already exists in the workspace.", call. = FALSE)
  workspace$libraries$platform_handoffs[[id]] <- handoff
  .workspace_touch(workspace, "platform_handoff_added", list(handoff_id = id, target = handoff$target))
}

#' Retrieve a workspace platform handoff
#'
#' @param workspace A workspace.
#' @param handoff_id Handoff identifier.
#' @return Stored platform handoff.
#' @export
workspace_get_platform_handoff <- function(workspace, handoff_id) {
  validate_catalyst_workspace(workspace); .workspace_id(handoff_id, "handoff_id")
  result <- workspace$libraries$platform_handoffs[[handoff_id]]
  if (is.null(result)) stop("Platform handoff is not present in the workspace.", call. = FALSE)
  result
}
