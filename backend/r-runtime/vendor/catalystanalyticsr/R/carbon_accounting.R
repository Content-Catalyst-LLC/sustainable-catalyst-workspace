.catalyst_carbon_pathway_schema_version <- function() "1.0.0"

.group_label <- function(data, fields) {
  if (!length(fields)) return(rep("all", nrow(data)))
  do.call(paste, c(unname(data[fields]), list(sep = "|")))
}

.resolve_group_budget <- function(budget, label, group_count) {
  if (!is.numeric(budget) || !length(budget) || any(!is.finite(budget)) || any(budget < 0)) {
    stop("`budget` must contain finite non-negative values.", call. = FALSE)
  }
  if (length(budget) == 1L) return(as.numeric(budget))
  if (is.null(names(budget)) || any(!nzchar(names(budget)))) {
    stop("Multiple budgets must be named by entity-group labels.", call. = FALSE)
  }
  if (!label %in% names(budget)) stop(sprintf("No carbon budget was supplied for group `%s`.", label), call. = FALSE)
  as.numeric(budget[[label]])
}

.cumulative_inventory_values <- function(time, values, accounting_basis) {
  if (accounting_basis == "period_total") return(cumsum(values))
  if (length(time) < 2L) return(rep(0, length(time)))
  if (!is.numeric(time)) {
    parsed <- suppressWarnings(as.numeric(as.Date(as.character(time))))
    if (any(!is.finite(parsed))) stop("Rate-based accounting requires numeric or date-like time values.", call. = FALSE)
    time <- parsed
  }
  increments <- c(0, (utils::head(values, -1) + utils::tail(values, -1)) / 2 * diff(as.numeric(time)))
  cumsum(increments)
}

#' Compute a carbon-budget pathway
#'
#' Calculates gross, removal, and net emissions trajectories together with
#' cumulative use of a declared carbon budget, overshoot timing, recovery, and
#' target-year diagnostics.
#'
#' @param inventory A `catalyst_emissions_inventory`.
#' @param budget Non-negative scalar budget or named vector keyed by group label.
#' @param group_by Inventory fields defining separate budget accounts.
#' @param target_year Optional target time for lock-in diagnostics.
#' @param target_net_emissions Target net emissions at or after `target_year`.
#' @return A `catalyst_carbon_pathway`.
#' @export
carbon_budget_pathway <- function(
  inventory,
  budget,
  group_by = inventory$entity_fields,
  target_year = NULL,
  target_net_emissions = 0
) {
  validate_emissions_inventory(inventory)
  if (!is.character(group_by) || any(!group_by %in% names(inventory$data)) || anyDuplicated(group_by)) {
    stop("`group_by` must contain unique inventory fields.", call. = FALSE)
  }
  if (!is.null(target_year)) {
    if (length(target_year) != 1L || is.na(target_year)) stop("`target_year` must contain one value.", call. = FALSE)
  }
  .assert_scalar_number(target_net_emissions, "target_net_emissions")

  groups <- .bind_indicator_groups(inventory$data, group_by)
  rows <- list()
  diagnostics <- list()
  for (group_name in names(groups)) {
    index <- groups[[group_name]]
    data <- inventory$data[index, , drop = FALSE]
    ordering <- order(data[[inventory$time_field]])
    data <- data[ordering, , drop = FALSE]
    rownames(data) <- NULL
    label <- if (length(group_by)) .group_label(data[1L, , drop = FALSE], group_by)[1L] else "all"
    group_budget <- .resolve_group_budget(budget, label, length(groups))

    data$cumulative_gross_emissions <- .cumulative_inventory_values(data[[inventory$time_field]], data$gross_emissions, inventory$accounting_basis)
    data$cumulative_removals <- .cumulative_inventory_values(data[[inventory$time_field]], data$removals, inventory$accounting_basis)
    data$cumulative_net_emissions <- data$cumulative_gross_emissions - data$cumulative_removals
    data$carbon_budget <- group_budget
    data$remaining_budget <- group_budget - data$cumulative_net_emissions
    data$budget_share_used <- if (group_budget == 0) {
      ifelse(data$cumulative_net_emissions <= 0, 0, Inf)
    } else data$cumulative_net_emissions / group_budget
    data$within_budget <- data$remaining_budget >= 0
    data$budget_status <- ifelse(data$within_budget, "within_budget", "overshoot")

    overshoot_index <- which(!data$within_budget)
    overshoot_time <- if (length(overshoot_index)) data[[inventory$time_field]][overshoot_index[1L]] else NA
    recovery_index <- integer()
    if (length(overshoot_index)) {
      recovery_index <- which(seq_len(nrow(data)) > overshoot_index[1L] & data$within_budget)
    }
    recovery_time <- if (length(recovery_index)) data[[inventory$time_field]][recovery_index[1L]] else NA

    target_index <- integer()
    if (!is.null(target_year)) target_index <- which(data[[inventory$time_field]] >= target_year)
    terminal_net <- utils::tail(data$net_emissions, 1L)
    post_target_positive <- if (length(target_index)) sum(pmax(data$net_emissions[target_index], 0)) else NA_real_
    target_value <- if (length(target_index)) data$net_emissions[target_index[1L]] else NA_real_
    lock_in_share <- if (length(target_index) && group_budget > 0) post_target_positive / group_budget else NA_real_
    stranded_signal <- (!is.na(overshoot_time)) || (!is.na(target_value) && target_value > target_net_emissions)

    diagnostic <- if (length(group_by)) data[1L, group_by, drop = FALSE] else data.frame(scope = "all", stringsAsFactors = FALSE)
    diagnostic$budget <- group_budget
    diagnostic$cumulative_gross_emissions <- utils::tail(data$cumulative_gross_emissions, 1L)
    diagnostic$cumulative_removals <- utils::tail(data$cumulative_removals, 1L)
    diagnostic$cumulative_net_emissions <- utils::tail(data$cumulative_net_emissions, 1L)
    diagnostic$remaining_budget <- utils::tail(data$remaining_budget, 1L)
    diagnostic$budget_share_used <- utils::tail(data$budget_share_used, 1L)
    diagnostic$overshoot_time <- overshoot_time
    diagnostic$recovery_time <- recovery_time
    diagnostic$terminal_net_emissions <- terminal_net
    diagnostic$target_year <- if (is.null(target_year)) NA else target_year
    diagnostic$target_net_emissions <- target_net_emissions
    diagnostic$net_emissions_at_target <- target_value
    diagnostic$post_target_positive_emissions <- post_target_positive
    diagnostic$carbon_lock_in_share <- lock_in_share
    diagnostic$stranded_pathway_signal <- stranded_signal
    diagnostic$within_budget <- utils::tail(data$within_budget, 1L)
    diagnostic$unit <- inventory$unit

    rows[[length(rows) + 1L]] <- data
    diagnostics[[length(diagnostics) + 1L]] <- diagnostic
  }

  pathway <- do.call(rbind, rows)
  rownames(pathway) <- NULL
  diagnostic_table <- do.call(rbind, diagnostics)
  rownames(diagnostic_table) <- NULL

  structure(list(
    schema_version = .catalyst_carbon_pathway_schema_version(),
    inventory_id = inventory$id,
    dataset_id = inventory$dataset_id,
    time_field = inventory$time_field,
    group_by = unname(group_by),
    accounting_basis = inventory$accounting_basis,
    unit = inventory$unit,
    pathway = pathway,
    diagnostics = diagnostic_table,
    meta = list(
      package_version = .catalyst_package_version(),
      created_at = .utc_now(),
      group_count = length(groups),
      target_year = target_year,
      target_net_emissions = target_net_emissions
    )
  ), class = "catalyst_carbon_pathway")
}

#' Summarize a carbon-budget pathway
#'
#' @param pathway A `catalyst_carbon_pathway`.
#' @return Group-level carbon-budget diagnostics.
#' @export
carbon_pathway_summary <- function(pathway) {
  if (!inherits(pathway, "catalyst_carbon_pathway")) stop("`pathway` must be a catalyst carbon pathway.", call. = FALSE)
  pathway$diagnostics
}

.logarithmic_mean <- function(x, y) {
  if (!is.finite(x) || !is.finite(y) || x <= 0 || y <= 0) return(NA_real_)
  if (isTRUE(all.equal(x, y, tolerance = 1e-12))) return(x)
  (x - y) / (log(x) - log(y))
}

#' Decompose emissions with the Kaya identity
#'
#' Uses population, GDP, energy, and gross emissions fields retained by a
#' governed inventory. Additive log-mean Divisia contributions reconcile the
#' change between the first and final observation in each group.
#'
#' @param inventory A governed emissions inventory containing population, GDP, and energy.
#' @param group_by Inventory fields defining independent decompositions.
#' @param baseline_time Optional exact baseline time.
#' @param comparison_time Optional exact comparison time.
#' @return A `catalyst_kaya_decomposition` containing levels and contributions.
#' @export
kaya_decomposition <- function(
  inventory,
  group_by = inventory$entity_fields,
  baseline_time = NULL,
  comparison_time = NULL
) {
  validate_emissions_inventory(inventory)
  required <- c("population", "gdp", "energy")
  absent <- setdiff(required, names(inventory$data))
  if (length(absent)) stop(sprintf("Kaya decomposition requires inventory fields: %s.", paste(absent, collapse = ", ")), call. = FALSE)
  if (!is.character(group_by) || any(!group_by %in% names(inventory$data)) || anyDuplicated(group_by)) {
    stop("`group_by` must contain unique inventory fields.", call. = FALSE)
  }
  data <- inventory$data
  if (any(data$gross_emissions <= 0)) stop("Kaya decomposition requires positive gross emissions.", call. = FALSE)

  data$affluence <- data$gdp / data$population
  data$energy_intensity <- data$energy / data$gdp
  data$carbon_intensity <- data$gross_emissions / data$energy
  data$reconstructed_emissions <- data$population * data$affluence * data$energy_intensity * data$carbon_intensity
  data$identity_error <- data$gross_emissions - data$reconstructed_emissions

  groups <- .bind_indicator_groups(data, group_by)
  contributions <- lapply(groups, function(index) {
    subset <- data[index, , drop = FALSE]
    subset <- subset[order(subset[[inventory$time_field]]), , drop = FALSE]
    if (!is.null(baseline_time)) {
      base_index <- which(subset[[inventory$time_field]] == baseline_time)
      if (!length(base_index)) stop("`baseline_time` was not found in every Kaya group.", call. = FALSE)
      base <- subset[base_index[1L], , drop = FALSE]
    } else base <- subset[1L, , drop = FALSE]
    if (!is.null(comparison_time)) {
      comp_index <- which(subset[[inventory$time_field]] == comparison_time)
      if (!length(comp_index)) stop("`comparison_time` was not found in every Kaya group.", call. = FALSE)
      comp <- subset[comp_index[1L], , drop = FALSE]
    } else comp <- subset[nrow(subset), , drop = FALSE]

    e0 <- base$gross_emissions[1L]
    e1 <- comp$gross_emissions[1L]
    weight <- .logarithmic_mean(e1, e0)
    factors <- c("population", "affluence", "energy_intensity", "carbon_intensity")
    effect <- vapply(factors, function(field) weight * log(comp[[field]][1L] / base[[field]][1L]), numeric(1))
    row <- if (length(group_by)) base[1L, group_by, drop = FALSE] else data.frame(scope = "all", stringsAsFactors = FALSE)
    row$baseline_time <- base[[inventory$time_field]][1L]
    row$comparison_time <- comp[[inventory$time_field]][1L]
    row$baseline_emissions <- e0
    row$comparison_emissions <- e1
    row$emissions_change <- e1 - e0
    for (field in factors) row[[paste0(field, "_effect")]] <- unname(effect[[field]])
    row$explained_change <- sum(effect)
    row$residual <- row$emissions_change - row$explained_change
    row$unit <- inventory$unit
    row
  })
  contribution_table <- do.call(rbind, contributions)
  rownames(contribution_table) <- NULL

  structure(list(
    schema_version = "1.0.0",
    inventory_id = inventory$id,
    time_field = inventory$time_field,
    group_by = unname(group_by),
    levels = data,
    contributions = contribution_table,
    meta = list(
      method = "additive_lmdi_kaya_identity",
      package_version = .catalyst_package_version(),
      created_at = .utc_now()
    )
  ), class = "catalyst_kaya_decomposition")
}

#' Plot a carbon-budget pathway
#'
#' @param pathway A catalyst carbon pathway.
#' @param facet Facet separate entity groups.
#' @return A ggplot object.
#' @export
plot_carbon_budget_pathway <- function(pathway, facet = TRUE) {
  if (!inherits(pathway, "catalyst_carbon_pathway")) stop("`pathway` must be a catalyst carbon pathway.", call. = FALSE)
  .assert_flag(facet, "facet")
  data <- pathway$pathway
  data$group_label <- .group_label(data, pathway$group_by)
  data$time_value <- data[[pathway$time_field]]
  plot <- ggplot2::ggplot(data, ggplot2::aes(
    x = time_value,
    y = cumulative_net_emissions,
    color = group_label
  )) +
    ggplot2::geom_line(linewidth = 0.9) +
    ggplot2::geom_line(ggplot2::aes(y = carbon_budget), linetype = "dashed", linewidth = 0.7) +
    ggplot2::labs(
      x = pathway$time_field,
      y = paste("Cumulative net emissions (", pathway$unit, ")", sep = ""),
      color = "Group",
      title = "Carbon-budget pathway",
      subtitle = "Solid lines show cumulative net emissions; dashed lines show declared budgets."
    ) +
    theme_catalyst()
  if (facet && length(pathway$group_by)) plot <- plot + ggplot2::facet_wrap(~ group_label, scales = "free_y")
  plot
}

#' Plot Kaya decomposition contributions
#'
#' @param decomposition A `catalyst_kaya_decomposition`.
#' @return A ggplot object.
#' @export
plot_kaya_decomposition <- function(decomposition) {
  if (!inherits(decomposition, "catalyst_kaya_decomposition")) stop("`decomposition` must be a Kaya decomposition.", call. = FALSE)
  fields <- c("population_effect", "affluence_effect", "energy_intensity_effect", "carbon_intensity_effect", "residual")
  rows <- lapply(seq_len(nrow(decomposition$contributions)), function(i) {
    record <- decomposition$contributions[i, , drop = FALSE]
    group_label <- .group_label(record, decomposition$group_by)[1L]
    data.frame(
      group_label = group_label,
      factor = fields,
      contribution = as.numeric(unlist(record[1L, fields], use.names = FALSE)),
      stringsAsFactors = FALSE
    )
  })
  data <- do.call(rbind, rows)
  ggplot2::ggplot(data, ggplot2::aes(x = factor, y = contribution, fill = group_label)) +
    ggplot2::geom_col(position = "dodge") +
    ggplot2::geom_hline(yintercept = 0, linewidth = 0.4) +
    ggplot2::labs(x = NULL, y = "Contribution to emissions change", fill = "Group", title = "Kaya decomposition") +
    theme_catalyst() +
    ggplot2::theme(axis.text.x = ggplot2::element_text(angle = 28, hjust = 1))
}

#' @export
print.catalyst_carbon_pathway <- function(x, ...) {
  cat("<catalyst_carbon_pathway>\n")
  cat("  inventory: ", x$inventory_id, "\n", sep = "")
  cat("  groups:    ", nrow(x$diagnostics), "\n", sep = "")
  cat("  overshoot: ", sum(!x$diagnostics$within_budget), " group(s)\n", sep = "")
  invisible(x)
}

#' @export
print.catalyst_kaya_decomposition <- function(x, ...) {
  cat("<catalyst_kaya_decomposition>\n")
  cat("  inventory: ", x$inventory_id, "\n", sep = "")
  cat("  groups:    ", nrow(x$contributions), "\n", sep = "")
  cat("  method:    ", x$meta$method, "\n", sep = "")
  invisible(x)
}
