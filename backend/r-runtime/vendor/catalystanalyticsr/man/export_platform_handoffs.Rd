\name{export_platform_handoffs}
\alias{export_platform_handoffs}
\alias{workspace_add_platform_handoff}
\alias{workspace_get_platform_handoff}
\title{Export and store Sustainable Catalyst platform handoffs}
\description{Export a complete first-party handoff bundle and retain handoffs in persistent workspaces.}
\usage{
export_platform_handoffs(project, dir = ".",
  prefix = "catalyst-platform-handoffs",
  targets = c("site_intelligence", "research_lab", "workbench",
    "catalyst_canvas", "decision_studio", "knowledge_library", "workspace"),
  options = list(), zip_bundle = TRUE)

workspace_add_platform_handoff(workspace, handoff, replace = FALSE)

workspace_get_platform_handoff(workspace, handoff_id)
}
\arguments{
  \item{project}{A reproducible project.}
  \item{dir}{Parent export directory.}
  \item{prefix}{Bundle directory and archive prefix.}
  \item{targets}{Target products to include.}
  \item{options}{Named target-specific options.}
  \item{zip_bundle}{Whether to create a ZIP archive.}
  \item{workspace}{A persistent workspace.}
  \item{handoff}{A validated platform handoff.}
  \item{replace}{Replace an existing handoff.}
  \item{handoff_id}{Workspace handoff identifier.}
}
\value{The export function returns generated paths. Workspace functions return an updated workspace or a stored handoff.}
