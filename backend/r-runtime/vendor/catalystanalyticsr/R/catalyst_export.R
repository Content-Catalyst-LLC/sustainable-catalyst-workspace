#' Export a Catalyst run as a portable bundle
#'
#' Convenience wrapper around [export_catalyst_bundle()] for a `catalyst_run`
#' object or compatible result list.
#'
#' @param results A `catalyst_run` object or compatible result list.
#' @param dir Output directory.
#' @param run_id Optional run identifier used in bundle names.
#' @param zip Logical. If TRUE, also create a zip archive.
#' @param overwrite Logical. If TRUE, replace existing output.
#' @param open Logical. If TRUE, open the output folder on macOS.
#' @param quiet Logical. If TRUE, suppress informational messages.
#' @return Invisibly returns bundle paths, manifest, and written-file inventory.
#' @export
#'
#' @examples
#' times <- seq(0, 5, by = 1)
#' x0 <- c(K = 1, H = 1, N = 1, C = 0, P = 1, A = 1)
#' res <- catalyst_run(times, x0, include_phase_plane = FALSE, include_sensitivity = FALSE)
#' out <- catalyst_export(res, dir = tempdir(), run_id = "demo", zip = FALSE, quiet = TRUE)
#' out
catalyst_export <- function(
  results,
  dir = tempdir(),
  run_id = "demo",
  zip = TRUE,
  overwrite = FALSE,
  open = FALSE,
  quiet = FALSE
) {
  export_catalyst_bundle(
    results = results,
    dir = dir,
    run_id = run_id,
    zip = zip,
    overwrite = overwrite,
    open = open,
    quiet = quiet
  )
}
