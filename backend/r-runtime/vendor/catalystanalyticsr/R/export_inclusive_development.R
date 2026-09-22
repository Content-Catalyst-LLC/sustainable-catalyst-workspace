.write_inclusive_json <- function(value, path) {
  jsonlite::write_json(.safe_json_value(value), path, pretty = TRUE, auto_unbox = TRUE, null = "null", na = "null", digits = NA)
  path
}

.inclusive_development_payload <- function(x) {
  list(
    schema_version = .catalyst_inclusive_development_schema_version(),
    analysis_type = x$analysis_type,
    id = x$id,
    title = x$title,
    summary = inclusive_development_summary(x),
    wealth = list(
      schema_version = x$wealth$schema_version,
      id = x$wealth$id,
      title = x$wealth$title,
      data = x$wealth$data,
      capital_accounts = lapply(x$wealth$capital_accounts, function(account) list(
        schema_version = account$schema_version,
        id = account$id,
        title = account$title,
        capital_type = account$capital_type,
        unit = account$unit,
        data = account$data,
        meta = account$meta
      )),
      meta = x$wealth$meta
    ),
    adjusted_net_savings = x$adjusted_net_savings,
    human_development = x$human_development,
    distribution = if (is.null(x$distribution)) NULL else unclass(x$distribution),
    intergenerational = if (is.null(x$intergenerational)) NULL else unclass(x$intergenerational),
    composite = if (is.null(x$composite)) NULL else list(
      schema_version = x$composite$schema_version,
      definition = unclass(x$composite$definition),
      scores = x$composite$scores,
      components = x$composite$components,
      trace = x$composite$trace,
      sensitivity = x$composite$sensitivity,
      meta = x$composite$meta
    ),
    meta = x$meta,
    review_boundary = list(
      shadow_prices_require_review = TRUE,
      human_capital_measurement_requires_review = TRUE,
      social_floor_requires_review = TRUE,
      distribution_weights_require_review = TRUE,
      composite_weights_require_review = TRUE,
      not_compliance_or_professional_advice = TRUE
    )
  )
}

.inclusive_markdown_brief <- function(x) {
  summary <- inclusive_development_summary(x)
  lines <- c(
    "# Catalyst Analytics R Inclusive Development Brief", "",
    paste0("**Analysis:** ", x$title),
    paste0("**Contract:** ", x$schema_version),
    paste0("**Closing inclusive wealth:** ", format(summary$closing_inclusive_wealth, digits = 6)),
    paste0("**Inclusive wealth change:** ", format(summary$inclusive_wealth_change, digits = 6)),
    paste0("**Closing wealth per capita:** ", format(summary$closing_per_capita_wealth, digits = 6)),
    paste0("**Adjusted Net Savings:** ", format(summary$adjusted_net_savings, digits = 6)),
    paste0("**Human Development Index:** ", format(summary$human_development_index, digits = 6)),
    paste0("**Gini:** ", format(summary$gini, digits = 6)),
    paste0("**Composite score:** ", format(summary$composite_score, digits = 6)), "",
    "## Capital composition", "",
    "| Entity | Produced share | Human share | Natural share |",
    "|---|---:|---:|---:|"
  )
  wealth_summary <- inclusive_wealth_summary(x$wealth)
  for (i in seq_len(nrow(wealth_summary))) {
    row <- wealth_summary[i, ]
    lines <- c(lines, sprintf("| %s | %.4f | %.4f | %.4f |", row$entity, row$produced_share, row$human_share, row$natural_share))
  }
  lines <- c(lines, "", "## Interpretation boundary", "",
    "Shadow prices, human-capital measures, social floors, distribution weights, intergenerational discounting, and composite-score choices require explicit human review. This analysis is not a forecast, compliance determination, autonomous decision, or professional advice.", "")
  paste(lines, collapse = "\n")
}

#' Export an inclusive-development analysis
#'
#' @param x A `catalyst_inclusive_development` object.
#' @param dir Output directory.
#' @param prefix File prefix.
#' @param zip_bundle Whether to create a ZIP bundle.
#' @return A named list of written paths.
#' @export
export_inclusive_development <- function(x, dir = ".", prefix = "inclusive-development", zip_bundle = TRUE) {
  if (!inherits(x, "catalyst_inclusive_development")) stop("`x` must be an inclusive-development analysis.", call. = FALSE)
  .assert_single_string(dir, "dir")
  .assert_single_string(prefix, "prefix")
  .assert_flag(zip_bundle, "zip_bundle")
  bundle_dir <- file.path(dir, prefix)
  dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  payload <- .inclusive_development_payload(x)
  paths <- list(bundle_dir = bundle_dir)
  paths$analysis <- .write_inclusive_json(payload, file.path(bundle_dir, "inclusive-development.json"))
  utils::write.csv(x$wealth$data, file.path(bundle_dir, "inclusive-wealth.csv"), row.names = FALSE)
  paths$wealth <- file.path(bundle_dir, "inclusive-wealth.csv")
  capital_summary <- do.call(rbind, lapply(x$wealth$capital_accounts, capital_account_summary))
  utils::write.csv(capital_summary, file.path(bundle_dir, "capital-account-summary.csv"), row.names = FALSE)
  paths$capital_summary <- file.path(bundle_dir, "capital-account-summary.csv")
  if (!is.null(x$adjusted_net_savings)) {
    utils::write.csv(x$adjusted_net_savings, file.path(bundle_dir, "adjusted-net-savings.csv"), row.names = FALSE)
    paths$adjusted_net_savings <- file.path(bundle_dir, "adjusted-net-savings.csv")
  }
  if (!is.null(x$human_development)) {
    utils::write.csv(x$human_development, file.path(bundle_dir, "human-development.csv"), row.names = FALSE)
    paths$human_development <- file.path(bundle_dir, "human-development.csv")
  }
  if (!is.null(x$distribution)) {
    paths$distribution <- .write_inclusive_json(unclass(x$distribution), file.path(bundle_dir, "distribution-analysis.json"))
    utils::write.csv(x$distribution$group_summary, file.path(bundle_dir, "distribution-groups.csv"), row.names = FALSE)
    paths$distribution_groups <- file.path(bundle_dir, "distribution-groups.csv")
  }
  if (!is.null(x$intergenerational)) {
    paths$intergenerational <- .write_inclusive_json(unclass(x$intergenerational), file.path(bundle_dir, "intergenerational-analysis.json"))
    utils::write.csv(x$intergenerational$trajectory, file.path(bundle_dir, "intergenerational-trajectory.csv"), row.names = FALSE)
    paths$intergenerational_trajectory <- file.path(bundle_dir, "intergenerational-trajectory.csv")
  }
  if (!is.null(x$composite)) {
    paths$composite <- .write_inclusive_json(list(
      definition = unclass(x$composite$definition), scores = x$composite$scores,
      components = x$composite$components, trace = x$composite$trace,
      sensitivity = x$composite$sensitivity
    ), file.path(bundle_dir, "composite-score.json"))
    utils::write.csv(x$composite$scores, file.path(bundle_dir, "composite-scores.csv"), row.names = FALSE)
    utils::write.csv(x$composite$components, file.path(bundle_dir, "composite-components.csv"), row.names = FALSE)
    paths$composite_scores <- file.path(bundle_dir, "composite-scores.csv")
    paths$composite_components <- file.path(bundle_dir, "composite-components.csv")
  }
  brief_path <- file.path(bundle_dir, "inclusive-development-brief.md")
  writeLines(.inclusive_markdown_brief(x), brief_path, useBytes = TRUE)
  paths$brief <- brief_path
  files <- setdiff(list.files(bundle_dir, full.names = TRUE), file.path(bundle_dir, "manifest.json"))
  file_records <- lapply(files, function(path) list(
    file = basename(path),
    bytes = unname(file.info(path)$size),
    md5 = unname(tools::md5sum(path))
  ))
  manifest <- list(
    schema_version = "1.0.0",
    export_type = "inclusive_development_bundle",
    package_version = .catalyst_package_version(),
    analysis_id = x$id,
    analysis_schema_version = x$schema_version,
    created_at = .utc_now(),
    files = file_records
  )
  paths$manifest <- .write_inclusive_json(manifest, file.path(bundle_dir, "manifest.json"))
  if (zip_bundle) {
    zip_path <- file.path(dir, paste0(prefix, ".zip"))
    old <- getwd()
    on.exit(setwd(old), add = TRUE)
    setwd(dir)
    utils::zip(zipfile = basename(zip_path), files = prefix)
    paths$zip <- zip_path
  }
  paths
}
