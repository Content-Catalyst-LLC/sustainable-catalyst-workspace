
.policy_evaluation_markdown <- function(analysis) {
  effects <- analysis$effects
  effect_lines <- if (!nrow(effects)) "- No effects were available." else vapply(seq_len(nrow(effects)), function(i) {
    paste0("- ", effects$evaluation_id[[i]], " / ", effects$method[[i]], ": ", format(effects$effect[[i]], digits = 6),
           if (is.finite(effects$conf_low[[i]])) paste0(" [", format(effects$conf_low[[i]], digits = 5), ", ", format(effects$conf_high[[i]], digits = 5), "]") else "")
  }, character(1))
  assumption_lines <- if (!length(analysis$assumptions)) "- No cross-method assumptions were recorded." else vapply(analysis$assumptions, function(x) paste0("- ", x$label, ": ", x$status, " - ", x$statement), character(1))
  c(paste0("# ", analysis$title), "", paste0("**Analysis ID:** `", analysis$id, "`  "),
    paste0("**Identification status:** ", analysis$identification_status, "  "), paste0("**Review status:** ", analysis$review_status, "  "), "",
    "## Policy effects", effect_lines, "", "## Identification assumptions", assumption_lines, "",
    "## Decision boundary", "Econometric estimates are conditional on design-specific assumptions. This bundle does not establish causal validity, authorize a policy, or replace human review.")
}

#' Export econometric and policy-evaluation evidence
#'
#' @param analysis A `catalyst_policy_evaluation_analysis`.
#' @param dir Parent output directory.
#' @param prefix Bundle directory name.
#' @param zip_bundle Create a ZIP archive.
#' @return Named generated paths.
#' @export
export_policy_evaluation <- function(analysis, dir = ".", prefix = "catalyst-policy-evaluation", zip_bundle = TRUE) {
  if (!inherits(analysis, "catalyst_policy_evaluation_analysis")) stop("`analysis` must be a policy-evaluation analysis.", call. = FALSE)
  .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(zip_bundle, "zip_bundle")
  bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(bundle_dir = bundle_dir)
  paths$analysis <- file.path(bundle_dir, "policy-evaluation-analysis.json")
  jsonlite::write_json(.safe_json_value(unclass(analysis)), paths$analysis, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  paths$effects <- file.path(bundle_dir, "policy-effects.csv"); utils::write.csv(analysis$effects, paths$effects, row.names = FALSE)
  assumption_table <- if (!length(analysis$assumptions)) data.frame(id=character(),label=character(),status=character(),statement=character(),limitations=character(),stringsAsFactors=FALSE) else do.call(rbind, lapply(analysis$assumptions, function(x) data.frame(id=x$id,label=x$label,status=x$status,statement=x$statement,limitations=paste(x$limitations,collapse="; "),stringsAsFactors=FALSE)))
  paths$assumptions <- file.path(bundle_dir, "causal-assumptions.csv"); utils::write.csv(assumption_table, paths$assumptions, row.names = FALSE)
  diagnostic_rows <- lapply(analysis$evaluations, function(evaluation) {
    regression <- if (inherits(evaluation, "catalyst_policy_regression")) evaluation else evaluation$regression
    if (is.null(regression) || is.null(regression$diagnostics)) return(NULL)
    d <- regression$diagnostics
    data.frame(evaluation_id=evaluation$id,rmse=d$rmse,mae=d$mae,r_squared=d$r_squared,adjusted_r_squared=d$adjusted_r_squared,durbin_watson=d$durbin_watson,condition_number=d$condition_number,stringsAsFactors=FALSE)
  })
  diagnostic_rows <- diagnostic_rows[!vapply(diagnostic_rows,is.null,logical(1))]
  diagnostics <- if (!length(diagnostic_rows)) data.frame(evaluation_id=character(),rmse=numeric(),mae=numeric(),r_squared=numeric(),adjusted_r_squared=numeric(),durbin_watson=numeric(),condition_number=numeric(),stringsAsFactors=FALSE) else do.call(rbind, diagnostic_rows)
  paths$diagnostics <- file.path(bundle_dir, "regression-diagnostics.csv"); utils::write.csv(diagnostics, paths$diagnostics, row.names = FALSE)
  for (name in names(analysis$evaluations)) {
    evaluation <- analysis$evaluations[[name]]
    if (inherits(evaluation, "catalyst_event_study")) { path <- file.path(bundle_dir, paste0(name, "-event-study.csv")); utils::write.csv(evaluation$effects,path,row.names=FALSE); paths[[paste0(name,"_event_study")]] <- path }
    if (inherits(evaluation, "catalyst_synthetic_control")) { path <- file.path(bundle_dir, paste0(name, "-synthetic-control.csv")); utils::write.csv(evaluation$effects,path,row.names=FALSE); paths[[paste0(name,"_synthetic_control")]] <- path }
  }
  paths$readme <- file.path(bundle_dir, "README.md"); writeLines(.policy_evaluation_markdown(analysis), paths$readme, useBytes = TRUE)
  files <- list.files(bundle_dir, recursive = TRUE, full.names = TRUE, all.files = FALSE); base <- normalizePath(bundle_dir)
  records <- lapply(files, function(path) list(file=substring(normalizePath(path),nchar(base)+2L),bytes=unname(file.info(path)$size),md5=unname(tools::md5sum(path))))
  manifest <- list(schema_version="1.0.0",export_type="econometrics_and_policy_evaluation_bundle",analysis_id=analysis$id,
                   package=list(name="catalystanalyticsr",version=.catalyst_package_version()),created_at=format(Sys.time(),tz="UTC",usetz=TRUE),
                   file_count=length(records),files=records,integrity=list(hash_algorithm="md5",complete=TRUE,scope="all_bundle_files_except_manifest"),
                   boundary=list(human_review_required=TRUE,causal_validity_not_automatic=TRUE,policy_authorization=FALSE))
  paths$manifest <- file.path(bundle_dir,"manifest.json"); jsonlite::write_json(manifest,paths$manifest,auto_unbox=TRUE,pretty=TRUE,null="null",na="null",digits=NA,dataframe="rows")
  if (zip_bundle) { paths$zip <- file.path(dir,paste0(prefix,".zip")); old <- getwd(); on.exit(setwd(old),add=TRUE); setwd(dir); utils::zip(zipfile=basename(paths$zip),files=prefix) }
  paths
}
