.model_indicators <- function(trajectory_wide, model) {
  if (!is.data.frame(trajectory_wide)) stop("`trajectory_wide` must be a data.frame.", call. = FALSE)
  rows <- lapply(names(model$indicator_map), function(indicator_name) {
    definition <- model$indicator_map[[indicator_name]]
    source <- definition$source
    if (!source %in% names(trajectory_wide)) {
      stop(sprintf("Indicator `%s` source `%s` is absent from the trajectory.", indicator_name, source), call. = FALSE)
    }
    data.frame(
      t = trajectory_wide$t,
      scenario = trajectory_wide$scenario,
      indicator = indicator_name,
      value = as.numeric(trajectory_wide[[source]]),
      unit = definition$unit,
      direction = definition$direction,
      indicator_version = if (!is.null(definition$version)) definition$version else "model-defined",
      formula = if (!is.null(definition$formula)) definition$formula else source,
      source_fields = source,
      registry_status = if (indicator_name %in% list_catalyst_indicators()$id) "registered" else "model-defined",
      stringsAsFactors = FALSE
    )
  })
  do.call(rbind, rows)
}
