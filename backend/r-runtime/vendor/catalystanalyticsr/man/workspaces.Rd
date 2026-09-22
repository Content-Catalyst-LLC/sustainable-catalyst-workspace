\name{workspaces}
\alias{catalyst_workspace}
\alias{validate_catalyst_workspace}
\alias{workspace_add_project}
\alias{workspace_get_project}
\alias{workspace_remove_project}
\alias{workspace_set_active_project}
\alias{workspace_add_scenario}
\alias{workspace_get_scenario}
\alias{workspace_clone_scenario}
\alias{workspace_add_parameter_set}
\alias{workspace_get_parameter_set}
\alias{workspace_add_policy_package}
\alias{workspace_list_scenarios}
\alias{workspace_run_history}
\alias{workspace_compare_projects}
\alias{workspace_fingerprint}
\alias{workspace_snapshot}
\alias{workspace_restore_snapshot}
\alias{workspace_manifest}
\alias{workspace_to_json}
\alias{workspace_from_json}
\alias{export_workspace}
\alias{workspace_add_regional_portfolio}
\alias{workspace_get_regional_portfolio}
\alias{workspace_add_policy_optimization}
\alias{workspace_get_policy_optimization}
\alias{workspace_add_policy_pathway}
\alias{workspace_get_policy_pathway}
\title{Persistent workspaces and reusable analytical libraries}
\usage{
catalyst_workspace(workspace_id, title, description = "", owner = "",
  tags = character(), metadata = list())

validate_catalyst_workspace(workspace)

workspace_add_project(workspace, project, replace = FALSE,
  index_contents = TRUE)

workspace_get_project(workspace, project_id = NULL)

workspace_remove_project(workspace, project_id)

workspace_set_active_project(workspace, project_id)

workspace_add_scenario(workspace, scenario, library_id = NULL,
  description = "", tags = character(), source_project_id = NULL,
  replace = FALSE)

workspace_get_scenario(workspace, library_id)

workspace_clone_scenario(workspace, library_id, new_library_id,
  new_scenario_id = new_library_id, title = NULL, role = NULL,
  replace = FALSE)

workspace_add_parameter_set(workspace, parameter_set_id, values,
  model_id = NULL, model_version = NULL, description = "",
  assumptions = list(), tags = character(), source_project_id = NULL,
  replace = FALSE)

workspace_get_parameter_set(workspace, parameter_set_id)

workspace_add_policy_package(workspace, policy_package_id, title,
  scenario_ids = character(), parameter_set_ids = character(),
  assumptions = list(), constraints = list(), description = "",
  tags = character(), replace = FALSE)

workspace_list_scenarios(workspace)

workspace_run_history(workspace)

workspace_compare_projects(workspace, project_ids = names(workspace$projects))

workspace_fingerprint(workspace)

workspace_snapshot(workspace, snapshot_id, note = "")

workspace_restore_snapshot(workspace, snapshot_id)

workspace_manifest(workspace)

workspace_to_json(workspace, path, pretty = TRUE)

workspace_from_json(path)

export_workspace(workspace, dir = ".", prefix = "catalyst-workspace",
  include_project_results = TRUE, zip_bundle = TRUE)

workspace_add_regional_portfolio(workspace, portfolio, replace = FALSE)

workspace_get_regional_portfolio(workspace, portfolio_id)
workspace_add_policy_optimization(workspace, optimization, replace = FALSE)

workspace_get_policy_optimization(workspace, optimization_id)

workspace_add_policy_pathway(workspace, pathway, replace = FALSE)

workspace_get_policy_pathway(workspace, pathway_id)

}
\arguments{
\item{workspace_id}{Stable workspace identifier.}
\item{title}{Human-readable workspace, scenario, or package title.}
\item{description}{Purpose or descriptive text.}
\item{owner}{Responsible person or institution.}
\item{tags}{Discovery tags.}
\item{metadata}{Additional metadata.}
\item{workspace}{A \code{catalyst_workspace}.}
\item{project}{A \code{catalyst_project}.}
\item{replace}{Replace an existing record with the same identifier.}
\item{index_contents}{Add project scenarios and parameter sets to the reusable libraries.}
\item{project_id}{Project identifier; when omitted in \code{workspace_get_project()}, use the active project.}
\item{scenario}{A canonical Catalyst scenario.}
\item{library_id}{Scenario-library identifier.}
\item{source_project_id}{Optional source project identifier.}
\item{new_library_id}{Identifier for the cloned library entry.}
\item{new_scenario_id}{Canonical identifier for the cloned scenario.}
\item{role}{Optional scenario role.}
\item{parameter_set_id}{Parameter-library identifier.}
\item{values}{Named parameter values.}
\item{model_id}{Optional model identifier.}
\item{model_version}{Optional model version.}
\item{assumptions}{Assumption records.}
\item{policy_package_id}{Policy-package identifier.}
\item{scenario_ids}{Scenario-library identifiers.}
\item{parameter_set_ids}{Parameter-library identifiers.}
\item{constraints}{Policy constraints.}
\item{project_ids}{Project identifiers to compare.}
\item{snapshot_id}{Workspace snapshot identifier.}
\item{note}{Snapshot note.}
\item{path}{Workspace JSON path.}
\item{pretty}{Pretty-print JSON.}
\item{dir}{Parent export directory.}
\item{prefix}{Bundle directory and ZIP prefix.}
\item{include_project_results}{Include complete project run result payloads.}
\item{zip_bundle}{Create a ZIP archive.}
\item{portfolio}{A regional portfolio.}
\item{portfolio_id}{Regional portfolio identifier.}
\item{optimization}{Policy optimization result.}
\item{optimization_id}{Optimization identifier.}
\item{pathway}{Adaptive policy pathway.}
\item{pathway_id}{Pathway identifier.}
}
\value{Constructors and mutators return a workspace. Retrieval functions return stored records. Index and comparison functions return data frames. Serialization and export functions return paths or generated artifact maps.}
\description{Creates persistent multi-project workspaces with reusable scenario, parameter, policy-package, optimization, pathway, and regional-portfolio libraries, consolidated run history, version snapshots, restoration, and portable export bundles.}
