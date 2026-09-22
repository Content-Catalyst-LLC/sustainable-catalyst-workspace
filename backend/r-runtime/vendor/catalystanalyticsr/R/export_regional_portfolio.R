#' Export regional, sector, and portfolio analytics
#'
#' @param analysis A `catalyst_regional_portfolio_analysis`.
#' @param dir Parent output directory.
#' @param prefix Bundle prefix.
#' @param zip_bundle Create a ZIP archive.
#' @param overwrite Replace an existing bundle.
#' @param quiet Suppress informational output.
#' @return Invisibly returns paths and manifest.
#' @export
export_regional_portfolio_analysis <- function(analysis, dir, prefix=analysis$id, zip_bundle=TRUE, overwrite=FALSE, quiet=FALSE) {
  if (!inherits(analysis,"catalyst_regional_portfolio_analysis")) stop("`analysis` must be a regional portfolio analysis.",call.=FALSE)
  .assert_single_string(dir,"dir"); .assert_single_string(prefix,"prefix"); .assert_flag(zip_bundle,"zip_bundle"); .assert_flag(overwrite,"overwrite"); .assert_flag(quiet,"quiet")
  safe <- gsub("[^A-Za-z0-9._-]+","-",trimws(prefix)); safe <- gsub("^-+|-+$","",safe); if(!nzchar(safe)) stop("`prefix` must contain a usable character.",call.=FALSE)
  dir.create(dir,recursive=TRUE,showWarnings=FALSE); out_dir <- file.path(dir,paste0("regional_portfolio_",safe))
  if(dir.exists(out_dir)){if(!overwrite)stop("Output bundle already exists. Set `overwrite = TRUE` to replace.",call.=FALSE);unlink(out_dir,recursive=TRUE,force=TRUE)}
  if(!dir.create(out_dir,recursive=TRUE,showWarnings=FALSE))stop("Could not create bundle directory.",call.=FALSE)
  written <- character()
  write_json <- function(name,value){path<-file.path(out_dir,paste0(name,".json"));jsonlite::write_json(.safe_json_value(value),path,auto_unbox=TRUE,pretty=TRUE,null="null",na="null",digits=NA,dataframe="rows");written<<-c(written,path);path}
  write_csv <- function(name,value){if(is.null(value)||!is.data.frame(value))return(NULL);path<-file.path(out_dir,paste0(name,".csv"));utils::write.csv(value,path,row.names=FALSE,na="");written<<-c(written,path);path}
  write_json("portfolio",unclass(analysis$portfolio)); write_json("summary",regional_portfolio_summary(analysis)); write_csv("member-indicators",analysis$indicator_values); write_csv("portfolio-aggregates",analysis$portfolio_aggregates); write_csv("regional-comparison",analysis$regional_comparison)
  if(!is.null(analysis$carbon_budgets)){write_csv("regional-carbon-pathways",analysis$carbon_budgets$pathway);write_csv("regional-carbon-diagnostics",analysis$carbon_budgets$diagnostics)}
  if(!is.null(analysis$sector_pathways)){write_csv("sector-transition-pathways",analysis$sector_pathways$pathways);write_csv("sector-transition-summary",analysis$sector_pathways$summary)}
  readme <- c(paste0("# ",analysis$title),"",paste0("**Portfolio ID:** `",analysis$id,"`  "),paste0("**Package:** catalystanalyticsr ",.catalyst_package_version(),"  "),"","## Summary",paste0("- Members: ",length(analysis$portfolio$members)),paste0("- Weighted indicators: ",nrow(analysis$portfolio_aggregates)),paste0("- Regional budget diagnostics: ",if(is.null(analysis$carbon_budgets))0 else nrow(analysis$carbon_budgets$diagnostics)),paste0("- Sector pathways: ",if(is.null(analysis$sector_pathways))0 else nrow(analysis$sector_pathways$summary)),"","## Boundary","Portfolio aggregation is analytical evidence, not autonomous resource allocation or policy authority.")
  readme_path<-file.path(out_dir,"README.md");writeLines(readme,readme_path,useBytes=TRUE);written<-c(written,readme_path)
  inventory <- function(paths){info<-file.info(paths);hashes<-unname(tools::md5sum(paths));unname(lapply(seq_along(paths),function(i)list(file=basename(paths[i]),bytes=unname(info$size[i]),md5=hashes[i])))}
  manifest <- list(schema_version=.regional_portfolio_analysis_schema_version(),export_type="regional_sector_portfolio_analytics_bundle",analysis_id=analysis$id,package=list(name="catalystanalyticsr",version=.catalyst_package_version()),created_at=.utc_now(),summary=regional_portfolio_summary(analysis),file_count=length(written),files=inventory(written),integrity=list(hash_algorithm="md5",complete=TRUE,scope="all_bundle_files_except_manifest"),boundary=list(human_review_required=TRUE,portfolio_not_allocation_authority=TRUE,regional_comparability_requires_unit_review=TRUE))
  manifest_path<-write_json("manifest",manifest)
  zip_path<-NULL
  if(zip_bundle){zip_path<-file.path(dir,paste0("regional_portfolio_",safe,".zip"));if(file.exists(zip_path)){if(!overwrite)stop("ZIP archive already exists. Set `overwrite = TRUE` to replace.",call.=FALSE);unlink(zip_path)};old<-getwd();on.exit(setwd(old),add=TRUE);setwd(out_dir);utils::zip(zipfile=zip_path,files=list.files(".",recursive=TRUE,all.files=FALSE,no..=TRUE),flags="-q");setwd(old)}
  if(!quiet)message("Regional portfolio bundle written to ",out_dir)
  invisible(list(directory=out_dir,zip=zip_path,manifest=manifest,manifest_path=manifest_path,files=written))
}
