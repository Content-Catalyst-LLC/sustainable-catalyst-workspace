#' Variable glossary for Catalyst Analytics R
#'
#' A plain-language mapping of model variables and derived indicators.
#' This is intended to make the package easier to learn and demo.
#'
#' @param include_internal Logical. If TRUE, include internal/helper entries (if any).
#'
#' @return A data.frame with columns: name, label, kind, unit, direction, notes.
#' @export
#'
#' @examples
#' catalyst_glossary()
catalyst_glossary <- function(include_internal = FALSE) {
  .assert_flag(include_internal, "include_internal")
  
  df <- data.frame(
    name = c(
      # core state variables
      "K", "H", "N", "C", "P", "A",
      # common derived series (your package uses these names elsewhere)
      "gdp", "emissions", "ans", "carbon_intensity"
    ),
    label = c(
      "Capital",
      "Human capital",
      "Natural capital",
      "Carbon stock",
      "Population",
      "Technology",
      "Gross domestic product",
      "Emissions",
      "Adjusted net savings",
      "Carbon intensity"
    ),
    kind = c(
      rep("state", 6),
      rep("derived", 4)
    ),
    unit = c(
      rep(NA_character_, 6),
      rep(NA_character_, 4)
    ),
    direction = c(
      "up",  # K
      "up",  # H
      "up",  # N
      "down",# C (typically want down)
      "up",  # P
      "up",  # A
      "up",  # gdp
      "down",# emissions
      "up",  # ans
      "down" # carbon_intensity
    ),
    notes = c(
      "Core state variable.",
      "Core state variable.",
      "Core state variable.",
      "Core state variable representing carbon burden.",
      "Core state variable.",
      "Core state variable.",
      "Derived series computed from the model state.",
      "Derived series computed from the model state.",
      "Derived series computed from the model state / indicators layer.",
      "Derived series: emissions per unit output."
    ),
    stringsAsFactors = FALSE
  )
  
  if (isTRUE(include_internal)) {
    # Reserved for future internal/helper entries; none are exposed in v0.2.0.
  }
  
  df
}

