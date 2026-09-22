#' Print a Catalyst run
#'
#' @param x A `catalyst_run` object.
#' @param ... Unused.
#' @return Invisibly returns `x`.
#' @export
#' @examples
#' x <- catalyst_demo()
#' print(x)
print.catalyst_run <- function(x, ...) {
  fmt <- function(value, digits = 3) {
    if (is.null(value) || length(value) == 0L || !is.finite(value)) return(NA_character_)
    format(round(value, digits), nsmall = digits, trim = TRUE)
  }
  tw <- x$trajectory_wide
  if (!is.data.frame(tw) || nrow(tw) < 1L) {
    cat("<catalyst_run: no trajectory data>\n")
    return(invisible(x))
  }

  first <- tw[1, , drop = FALSE]
  last <- tw[nrow(tw), , drop = FALSE]
  scenario <- if ("scenario" %in% names(tw)) as.character(first$scenario) else "unknown"
  cat("Catalyst Analytics R -- Scenario Run\n")
  cat("Scenario:", scenario, "\n")
  cat("Time:", first$t, "->", last$t, " (steps:", nrow(tw), ")\n\n")

  cat("Key outcomes (model units / indices)\n")
  show <- function(label, column) {
    if (column %in% names(tw)) {
      cat(sprintf("  %-24s %8s -> %8s\n", label, fmt(first[[column]]), fmt(last[[column]])))
    }
  }
  show("GDP", "gdp")
  show("Emissions", "emissions")
  show("Adjusted Net Savings", "ans")
  show("Natural capital", "N")
  show("Atmospheric carbon", "C")

  if (is.data.frame(x$scorecard)) {
    cat("\nScorecard (percent change)\n")
    score <- x$scorecard[x$scorecard$metric %in% c("gdp", "emissions", "ans"), , drop = FALSE]
    for (i in seq_len(nrow(score))) {
      percent <- if (is.finite(score$pct_change[i])) sprintf("%+.1f%%", 100 * score$pct_change[i]) else "NA"
      cat(sprintf("  %-24s %s\n", score$metric[i], percent))
    }
  }

  if (!is.null(x$carbon_budget)) {
    cb <- x$carbon_budget
    cat("\nEmissions budget check\n")
    cat("  Status:", if (isTRUE(cb$within_budget)) "WITHIN budget" else "OVER budget", "\n")
    cat("  Cumulative emissions:", fmt(cb$cumulative_emissions), "\n")
    cat("  Budget:", fmt(cb$budget), "\n")
    cat("  Remaining:", fmt(cb$remaining), "\n")
  }

  invisible(x)
}

#' Summarize a Catalyst run
#'
#' @param object A `catalyst_run` object.
#' @param ... Unused.
#' @return Invisibly returns `object`.
#' @export
#' @examples
#' x <- catalyst_demo()
#' summary(x)
summary.catalyst_run <- function(object, ...) {
  print(object)
  cat("\nOutputs\n")
  tabular <- c("trajectory_wide", "trajectory_long", "sdg_indicators", "scorecard", "phase_plane", "sensitivities")
  for (name in tabular) {
    value <- object[[name]]
    if (is.data.frame(value)) cat("  *", name, ":", nrow(value), "rows\n")
  }
  if (is.list(object$plots)) cat("  * plots:", paste(names(object$plots), collapse = ", "), "\n")
  invisible(object)
}

#' Plot a Catalyst run
#'
#' @param x A `catalyst_run` object.
#' @param which Plot to display: `trajectory`, `sdg_dashboard`, `phase_plane`,
#'   `sensitivity_heatmap`, or `all`.
#' @param ... Unused.
#' @return Invisibly returns the selected ggplot or plot list.
#' @export
#' @examples
#' \dontrun{
#' x <- catalyst_demo()
#' plot(x, which = "trajectory")
#' }
plot.catalyst_run <- function(
  x,
  which = c("trajectory", "sdg_dashboard", "phase_plane", "sensitivity_heatmap", "all"),
  ...
) {
  which <- match.arg(which)
  if (!is.list(x$plots)) stop("This run has no `plots` list.", call. = FALSE)

  if (which == "all") {
    for (plot in x$plots) if (inherits(plot, "ggplot")) print(plot)
    return(invisible(x$plots))
  }

  plot <- x$plots[[which]]
  if (is.null(plot)) stop(sprintf("Plot '%s' not found in x$plots.", which), call. = FALSE)
  if (!inherits(plot, "ggplot")) stop(sprintf("x$plots[['%s']] is not a ggplot.", which), call. = FALSE)
  print(plot)
  invisible(plot)
}
