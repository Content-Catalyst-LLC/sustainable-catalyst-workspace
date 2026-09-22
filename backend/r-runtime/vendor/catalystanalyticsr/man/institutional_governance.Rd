\name{institutional_governance}
\alias{institutional_role}
\alias{governance_actor}
\alias{institutional_template}
\alias{restricted_access_policy}
\alias{institutional_governance_workflow}
\alias{validate_institutional_governance}
\alias{assign_institutional_review}
\alias{add_review_comment}
\alias{submit_change_request}
\alias{resolve_change_request}
\alias{record_governance_approval}
\alias{sign_analytical_release}
\alias{archive_governance_workflow}
\alias{apply_governance_to_project}
\alias{governance_audit_log}
\alias{governance_summary}
\alias{governance_to_json}
\alias{governance_from_json}
\alias{print.catalyst_institutional_governance}
\title{Collaborative Review and Institutional Governance}
\usage{
institutional_role(
  role_id = c("analyst", "reviewer", "approver", "publisher", "administrator"),
  title = NULL,
  permissions = NULL,
  description = ""
)

governance_actor(actor_id, name, roles, institution = "", email = "", active = TRUE)

institutional_template(
  template_id = "standard-institutional-review",
  title = "Standard institutional review",
  review_stages = c("analysis", "methodology", "governance", "publication"),
  required_roles = c("analyst", "reviewer", "approver", "publisher"),
  required_approvals = 1L,
  retention_days = 2555L,
  metadata = list()
)

restricted_access_policy(
  policy_id = "institutional-internal",
  classification = c("public", "internal", "confidential", "restricted"),
  allowed_roles = c("analyst", "reviewer", "approver", "publisher", "administrator"),
  allowed_actor_ids = character(),
  export_allowed = TRUE,
  publication_allowed = TRUE,
  reason = ""
)

institutional_governance_workflow(
  project,
  workflow_id,
  institution_id,
  institution_name,
  actors,
  template = institutional_template(),
  access_policy = restricted_access_policy(),
  metadata = list()
)

validate_institutional_governance(workflow)

assign_institutional_review(
  workflow,
  assignment_id,
  reviewer_id,
  review_type = "methodology",
  target_type = "project",
  target_id = workflow$project$id,
  due_at = NULL,
  assigned_by = NULL
)

add_review_comment(
  workflow,
  comment_id,
  author_id,
  body,
  target_type = "project",
  target_id = workflow$project$id,
  severity = c("note", "minor", "major", "critical"),
  disposition = c("open", "acknowledged", "resolved"),
  parent_id = NULL
)

submit_change_request(
  workflow,
  request_id,
  requester_id,
  title,
  description,
  priority = c("normal", "high", "critical"),
  target_type = "project",
  target_id = workflow$project$id
)

resolve_change_request(
  workflow,
  request_id,
  actor_id,
  resolution,
  status = c("resolved", "rejected")
)

record_governance_approval(
  workflow,
  approval_id,
  actor_id,
  decision = c("approved", "rejected", "changes_requested"),
  scope = "project",
  note = ""
)

sign_analytical_release(
  workflow,
  release_id,
  actor_id,
  title,
  artifact_hashes,
  statement = "Approved for governed publication subject to the recorded scope and limitations."
)

archive_governance_workflow(workflow, actor_id, reason)

apply_governance_to_project(project, workflow)

governance_audit_log(workflow)

governance_summary(workflow)

governance_to_json(workflow, path = NULL, pretty = TRUE)

governance_from_json(x)

\method{print}{catalyst_institutional_governance}(x, ...)
}
\arguments{
  \item{role_id, reviewer_id, author_id, requester_id, actor_id}{Stable role or actor identifier.}
  \item{title, name, institution_name}{Human-readable labels.}
  \item{permissions, roles, required_roles, allowed_roles, allowed_actor_ids}{Permission and access vectors.}
  \item{description, reason, body, resolution, note, statement}{Governance narrative text.}
  \item{institution, email}{Actor affiliation and contact metadata.}
  \item{active, export_allowed, publication_allowed, pretty}{Logical controls.}
  \item{template_id, policy_id, workflow_id, institution_id, assignment_id, comment_id, request_id, approval_id, release_id}{Stable identifiers.}
  \item{review_stages, required_approvals, retention_days, metadata}{Institutional-template controls.}
  \item{classification}{Access classification.}
  \item{project, workflow, x}{Project or governance record.}
  \item{actors, template, access_policy}{Workflow participants and policies.}
  \item{review_type, target_type, target_id, due_at, assigned_by}{Review-assignment fields.}
  \item{severity, disposition, parent_id}{Structured-comment fields.}
  \item{priority, status}{Change-request state.}
  \item{decision, scope}{Approval decision and scope.}
  \item{artifact_hashes}{Named artifact hashes for a signed analytical release.}
  \item{path}{Optional JSON path.}
  \item{...}{Unused print arguments.}
}
\value{Governed role, actor, workflow, summary, audit, project, or JSON records, depending on the function.}
\description{Creates and manages collaborative institutional review workflows with role-based assignments, structured comments, change requests, approvals, signed analytical releases, restricted access, audit history, retention, and archival controls.}
