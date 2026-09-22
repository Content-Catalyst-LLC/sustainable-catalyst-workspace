#' Save a ggplot to Disk
#'
#' @param plot A ggplot object.
#' @param filename File path to write (e.g., ".png", ".pdf").
#' @param width,height Plot dimensions.
#' @param dpi Resolution in dots per inch.
#' @param units Units for width/height ("in", "cm", "mm", or "px").
#' @return Invisibly returns `filename`.
#' @export
#' @examples
#' \dontrun{
#' p <- ggplot2::ggplot(mtcars, ggplot2::aes(mpg, wt)) + ggplot2::geom_point()
#' save_plot(p, tempfile(fileext = ".png"))
#' }
save_plot <- function(plot, filename, width = 10, height = 6, dpi = 300, units = "in") {
  if (!inherits(plot, "ggplot")) stop("`plot` must be a ggplot object.")
  if (!is.character(filename) || length(filename) != 1) stop("`filename` must be a single string.")
  ggplot2::ggsave(filename = filename, plot = plot, width = width, height = height, dpi = dpi, units = units)
  invisible(filename)
}