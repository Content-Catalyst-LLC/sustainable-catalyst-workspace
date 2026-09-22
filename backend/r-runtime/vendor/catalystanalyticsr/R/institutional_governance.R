.catalyst_institutional_governance_schema_version <- function() "1.0.0"
.catalyst_governance_export_schema_version <- function() "1.0.0"

.governance_id <- function(x, arg = "id") {
  .project_id(x, arg)
  invisible(x)
}

.governance_default_permissions <- function(role) {
  switch(role,
    analyst = c("comment", "submit_change", "respond_change"),
    reviewer = c("comment", "review", "request_change"),
    approver = c("comment", "approve", "reject", "request_change"),
    publisher = c("comment", "publish", "archive"),
    administrator = c("comment", "submit_change", "respond_change", "review", "request_change", "approve", "reject", "publish", "archive", "manage"),
    character()
  )
}

#' Define an institutional governance role
#'
#' @param role_id Stable role identifier.
#' @param title Human-readable title.
#' @param permissions Character vector of permissions.
#' @param description Role description.
#' @return A governance role record.
#' @export
institutional_role <- function(role_id = c("analyst", "reviewer", "approver", "publisher", "administrator"), title = NULL, permissions = NULL, description = "") {
  role_id <- match.arg(role_id)
  if (is.null(title)) title <- tools::toTitleCase(gsub("_", " ", role_id))
  if (is.null(permissions)) permissions <- .governance_default_permissions(role_id)
  .assert_single_string(title, "title")
  .assert_single_string(description, "description", allow_empty = TRUE)
  if (!is.character(permissions) || anyNA(permissions)) stop("`permissions` must be a character vector.", call. = FALSE)
  list(id = role_id, title = title, permissions = unique(permissions), description = description)
}

#' Define an institutional governance actor
#'
#' @param actor_id Stable actor identifier.
#' @param name Human-readable name.
#' @param roles Role identifiers.
#' @param institution Institution identifier.
#' @param email Optional contact email.
#' @param active Whether the actor may participate.
#' @return A governance actor record.
#' @export
governance_actor <- function(actor_id, name, roles, institution = "", email = "", active = TRUE) {
  .governance_id(actor_id, "actor_id")
  .assert_single_string(name, "name")
  .assert_single_string(institution, "institution", allow_empty = TRUE)
  .assert_single_string(email, "email", allow_empty = TRUE)
  .assert_flag(active, "active")
  allowed <- c("analyst", "reviewer", "approver", "publisher", "administrator")
  if (!is.character(roles) || !length(roles) || anyNA(roles) || length(setdiff(roles, allowed))) stop("`roles` contains unsupported governance roles.", call. = FALSE)
  list(id = actor_id, name = name, roles = unique(roles), institution = institution, email = email, active = active)
}

#' Define an institutional governance template
#'
#' @param template_id Stable identifier.
#' @param title Human-readable title.
#' @param review_stages Ordered review stages.
#' @param required_roles Roles required in the workflow.
#' @param required_approvals Minimum approved decisions before signing.
#' @param retention_days Minimum retention period.
#' @param metadata Additional template metadata.
#' @return Institutional template record.
#' @export
institutional_template <- function(template_id = "standard-institutional-review", title = "Standard institutional review", review_stages = c("analysis", "methodology", "governance", "publication"), required_roles = c("analyst", "reviewer", "approver", "publisher"), required_approvals = 1L, retention_days = 2555L, metadata = list()) {
  .governance_id(template_id, "template_id")
  .assert_single_string(title, "title")
  if (!is.character(review_stages) || !length(review_stages) || anyNA(review_stages)) stop("`review_stages` must be a non-empty character vector.", call. = FALSE)
  allowed_roles <- c("analyst", "reviewer", "approver", "publisher", "administrator")
  if (!is.character(required_roles) || anyNA(required_roles) || length(setdiff(required_roles, allowed_roles))) stop("`required_roles` contains unsupported roles.", call. = FALSE)
  .assert_scalar_number(required_approvals, "required_approvals")
  .assert_scalar_number(retention_days, "retention_days")
  if (required_approvals < 1 || required_approvals != as.integer(required_approvals)) stop("`required_approvals` must be a positive integer.", call. = FALSE)
  if (retention_days < 0 || retention_days != as.integer(retention_days)) stop("`retention_days` must be a non-negative integer.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  list(id = template_id, title = title, review_stages = unique(review_stages), required_roles = unique(required_roles), required_approvals = as.integer(required_approvals), retention_days = as.integer(retention_days), metadata = metadata)
}

#' Define a restricted-access policy
#'
#' @param policy_id Stable identifier.
#' @param classification Access classification.
#' @param allowed_roles Roles allowed to access the record.
#' @param allowed_actor_ids Explicit actor allow-list.
#' @param export_allowed Whether governed exports are permitted.
#' @param publication_allowed Whether publication may be approved.
#' @param reason Policy rationale.
#' @return Restricted-access policy record.
#' @export
restricted_access_policy <- function(policy_id = "institutional-internal", classification = c("public", "internal", "confidential", "restricted"), allowed_roles = c("analyst", "reviewer", "approver", "publisher", "administrator"), allowed_actor_ids = character(), export_allowed = TRUE, publication_allowed = TRUE, reason = "") {
  .governance_id(policy_id, "policy_id")
  classification <- match.arg(classification)
  if (!is.character(allowed_roles) || anyNA(allowed_roles)) stop("`allowed_roles` must be a character vector.", call. = FALSE)
  if (!is.character(allowed_actor_ids) || anyNA(allowed_actor_ids)) stop("`allowed_actor_ids` must be a character vector.", call. = FALSE)
  .assert_flag(export_allowed, "export_allowed")
  .assert_flag(publication_allowed, "publication_allowed")
  .assert_single_string(reason, "reason", allow_empty = TRUE)
  list(id = policy_id, classification = classification, allowed_roles = unique(allowed_roles), allowed_actor_ids = unique(allowed_actor_ids), export_allowed = export_allowed, publication_allowed = publication_allowed, reason = reason)
}

.governance_actor_record <- function(workflow, actor_id) {
  .governance_id(actor_id, "actor_id")
  actor <- workflow$actors[[actor_id]]
  if (is.null(actor) || !isTRUE(actor$active)) stop("Governance actor is missing or inactive.", call. = FALSE)
  actor
}

.governance_actor_permissions <- function(workflow, actor_id) {
  actor <- .governance_actor_record(workflow, actor_id)
  unique(unlist(lapply(actor$roles, function(role) workflow$roles[[role]]$permissions), use.names = FALSE))
}

.governance_require_permission <- function(workflow, actor_id, permission) {
  if (!permission %in% .governance_actor_permissions(workflow, actor_id)) stop(sprintf("Actor `%s` lacks `%s` permission.", actor_id, permission), call. = FALSE)
  invisible(TRUE)
}

.governance_audit <- function(workflow, action, actor_id = "system", object_type = "workflow", object_id = workflow$id, details = list()) {
  workflow$audit[[length(workflow$audit) + 1L]] <- list(
    id = paste0("audit-", length(workflow$audit) + 1L),
    action = action, actor_id = actor_id, object_type = object_type, object_id = object_id,
    details = .safe_json_value(details), recorded_at = .utc_now()
  )
  workflow$metadata$updated_at <- .utc_now()
  workflow$metadata$package_version <- .catalyst_package_version()
  workflow
}

#' Create an institutional governance workflow
#'
#' @param project A reproducible analytical project.
#' @param workflow_id Stable workflow identifier.
#' @param institution_id Institution identifier.
#' @param institution_name Human-readable institution name.
#' @param actors Governance actor records.
#' @param template Institutional template.
#' @param access_policy Restricted-access policy.
#' @param metadata Additional workflow metadata.
#' @return A `catalyst_institutional_governance` record.
#' @export
institutional_governance_workflow <- function(project, workflow_id, institution_id, institution_name, actors, template = institutional_template(), access_policy = restricted_access_policy(), metadata = list()) {
  validate_catalyst_project(project)
  .governance_id(workflow_id, "workflow_id")
  .governance_id(institution_id, "institution_id")
  .assert_single_string(institution_name, "institution_name")
  if (!is.list(actors) || !length(actors)) stop("`actors` must be a non-empty list.", call. = FALSE)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  actor_index <- list()
  for (actor in actors) {
    if (!is.list(actor) || is.null(actor$id)) stop("Every actor must be a governance_actor record.", call. = FALSE)
    if (!is.null(actor_index[[actor$id]])) stop("Governance actor identifiers must be unique.", call. = FALSE)
    actor_index[[actor$id]] <- actor
  }
  roles <- lapply(c("analyst", "reviewer", "approver", "publisher", "administrator"), institutional_role)
  names(roles) <- vapply(roles, `[[`, character(1), "id")
  now <- .utc_now()
  workflow <- structure(list(
    schema_version = .catalyst_institutional_governance_schema_version(),
    governance_type = "collaborative_institutional_review",
    id = workflow_id,
    title = paste0(project$title, " - Institutional review"),
    institution = list(id = institution_id, name = institution_name),
    project = list(id = project$id, title = project$title, fingerprint = project_fingerprint(project)),
    roles = roles,
    actors = actor_index,
    template = template,
    access_policy = access_policy,
    review_assignments = list(),
    comments = list(),
    change_requests = list(),
    approvals = list(),
    signed_releases = list(),
    audit = list(),
    retention = list(retention_days = template$retention_days, archive_status = "active", archive_reason = NULL, archived_at = NULL, disposal_eligible_at = NULL),
    status = "draft",
    metadata = utils::modifyList(list(package_version = .catalyst_package_version(), created_at = now, updated_at = now), metadata)
  ), class = c("catalyst_institutional_governance", "list"))
  workflow <- .governance_audit(workflow, "workflow_created", details = list(project_id = project$id, institution_id = institution_id))
  validate_institutional_governance(workflow)
  workflow
}

#' Validate an institutional governance workflow
#'
#' @param workflow Governance workflow or compatible list.
#' @return Invisibly returns `TRUE`.
#' @export
validate_institutional_governance <- function(workflow) {
  if (!is.list(workflow)) stop("`workflow` must be a list.", call. = FALSE)
  required <- c("schema_version", "governance_type", "id", "title", "institution", "project", "roles", "actors", "template", "access_policy", "review_assignments", "comments", "change_requests", "approvals", "signed_releases", "audit", "retention", "status", "metadata")
  missing <- setdiff(required, names(workflow))
  if (length(missing)) stop("Governance workflow is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(workflow$schema_version, .catalyst_institutional_governance_schema_version()) || !identical(workflow$governance_type, "collaborative_institutional_review")) stop("Unsupported institutional governance contract.", call. = FALSE)
  .governance_id(workflow$id, "workflow$id")
  .assert_single_string(workflow$title, "workflow$title")
  if (!is.list(workflow$institution) || is.null(workflow$institution$id) || is.null(workflow$institution$name)) stop("Workflow institution is incomplete.", call. = FALSE)
  if (!is.list(workflow$project) || is.null(workflow$project$id) || is.null(workflow$project$fingerprint)) stop("Workflow project reference is incomplete.", call. = FALSE)
  if (!is.list(workflow$roles) || !is.list(workflow$actors) || !length(workflow$actors)) stop("Workflow roles and actors are incomplete.", call. = FALSE)
  for (actor in workflow$actors) {
    if (!is.list(actor) || is.null(actor$id) || is.null(actor$roles) || length(setdiff(actor$roles, names(workflow$roles)))) stop("Workflow actor has invalid roles.", call. = FALSE)
  }
  for (field in c("review_assignments", "comments", "change_requests", "approvals", "signed_releases")) .workspace_named_list(workflow[[field]], paste0("workflow$", field))
  if (!is.list(workflow$audit) || !is.list(workflow$retention) || !is.list(workflow$metadata)) stop("Workflow audit, retention, and metadata must be lists.", call. = FALSE)
  if (!workflow$status %in% c("draft", "in_review", "changes_requested", "approved", "signed", "archived", "rejected")) stop("Workflow status is invalid.", call. = FALSE)
  if (!workflow$retention$archive_status %in% c("active", "archived", "disposal_eligible")) stop("Workflow archive status is invalid.", call. = FALSE)
  for (assignment in workflow$review_assignments) {
    if (is.null(workflow$actors[[assignment$reviewer_id]])) stop("Review assignment references an unknown actor.", call. = FALSE)
  }
  invisible(TRUE)
}

#' Assign a review
#'
#' @param workflow Governance workflow.
#' @param assignment_id Stable assignment identifier.
#' @param reviewer_id Reviewer actor identifier.
#' @param review_type Review stage or type.
#' @param target_type Target record type.
#' @param target_id Target record identifier.
#' @param due_at Optional due date or timestamp.
#' @param assigned_by Optional assigning actor. `NULL` records a system assignment.
#' @return Updated workflow.
#' @export
assign_institutional_review <- function(workflow, assignment_id, reviewer_id, review_type = "methodology", target_type = "project", target_id = workflow$project$id, due_at = NULL, assigned_by = NULL) {
  validate_institutional_governance(workflow)
  .governance_id(assignment_id, "assignment_id"); .governance_id(reviewer_id, "reviewer_id")
  .assert_single_string(review_type, "review_type"); .assert_single_string(target_type, "target_type"); .assert_single_string(target_id, "target_id")
  actor <- .governance_actor_record(workflow, reviewer_id)
  if (!any(actor$roles %in% c("reviewer", "approver", "administrator"))) stop("Assigned actor does not hold a review-capable role.", call. = FALSE)
  if (!is.null(assigned_by)) .governance_require_permission(workflow, assigned_by, "manage")
  if (!is.null(workflow$review_assignments[[assignment_id]])) stop("Review assignment already exists.", call. = FALSE)
  workflow$review_assignments[[assignment_id]] <- list(id = assignment_id, reviewer_id = reviewer_id, review_type = review_type, target_type = target_type, target_id = target_id, due_at = due_at, status = "assigned", assigned_by = if (is.null(assigned_by)) "system" else assigned_by, assigned_at = .utc_now(), completed_at = NULL)
  workflow$status <- "in_review"
  workflow <- .governance_audit(workflow, "review_assigned", if (is.null(assigned_by)) "system" else assigned_by, "review_assignment", assignment_id, list(reviewer_id = reviewer_id, review_type = review_type))
  validate_institutional_governance(workflow); workflow
}

#' Add a structured review comment
#'
#' @param workflow Governance workflow.
#' @param comment_id Stable comment identifier.
#' @param author_id Author actor identifier.
#' @param body Comment text.
#' @param target_type Target record type.
#' @param target_id Target record identifier.
#' @param severity Comment severity.
#' @param disposition Initial disposition.
#' @param parent_id Optional parent comment identifier.
#' @return Updated workflow.
#' @export
add_review_comment <- function(workflow, comment_id, author_id, body, target_type = "project", target_id = workflow$project$id, severity = c("note", "minor", "major", "critical"), disposition = c("open", "acknowledged", "resolved"), parent_id = NULL) {
  validate_institutional_governance(workflow)
  .governance_id(comment_id, "comment_id"); .governance_require_permission(workflow, author_id, "comment")
  .assert_single_string(body, "body"); .assert_single_string(target_type, "target_type"); .assert_single_string(target_id, "target_id")
  severity <- match.arg(severity); disposition <- match.arg(disposition)
  if (!is.null(parent_id) && is.null(workflow$comments[[parent_id]])) stop("Parent comment does not exist.", call. = FALSE)
  if (!is.null(workflow$comments[[comment_id]])) stop("Comment already exists.", call. = FALSE)
  workflow$comments[[comment_id]] <- list(id = comment_id, author_id = author_id, body = body, target_type = target_type, target_id = target_id, severity = severity, disposition = disposition, parent_id = parent_id, created_at = .utc_now(), resolved_at = if (identical(disposition, "resolved")) .utc_now() else NULL)
  workflow <- .governance_audit(workflow, "comment_added", author_id, "comment", comment_id, list(severity = severity, target_id = target_id))
  validate_institutional_governance(workflow); workflow
}

#' Submit an institutional change request
#'
#' @param workflow Governance workflow.
#' @param request_id Stable request identifier.
#' @param requester_id Requesting actor identifier.
#' @param title Request title.
#' @param description Requested change.
#' @param priority Priority level.
#' @param target_type Target record type.
#' @param target_id Target record identifier.
#' @return Updated workflow.
#' @export
submit_change_request <- function(workflow, request_id, requester_id, title, description, priority = c("normal", "high", "critical"), target_type = "project", target_id = workflow$project$id) {
  validate_institutional_governance(workflow)
  .governance_id(request_id, "request_id")
  permissions <- .governance_actor_permissions(workflow, requester_id)
  if (!any(c("submit_change", "request_change") %in% permissions)) stop("Actor cannot submit a change request.", call. = FALSE)
  .assert_single_string(title, "title"); .assert_single_string(description, "description"); .assert_single_string(target_type, "target_type"); .assert_single_string(target_id, "target_id")
  priority <- match.arg(priority)
  if (!is.null(workflow$change_requests[[request_id]])) stop("Change request already exists.", call. = FALSE)
  workflow$change_requests[[request_id]] <- list(id = request_id, requester_id = requester_id, title = title, description = description, priority = priority, target_type = target_type, target_id = target_id, status = "open", resolution = NULL, created_at = .utc_now(), resolved_at = NULL, resolved_by = NULL)
  workflow$status <- "changes_requested"
  workflow <- .governance_audit(workflow, "change_requested", requester_id, "change_request", request_id, list(priority = priority, target_id = target_id))
  validate_institutional_governance(workflow); workflow
}

#' Resolve an institutional change request
#'
#' @param workflow Governance workflow.
#' @param request_id Change-request identifier.
#' @param actor_id Resolving actor identifier.
#' @param resolution Resolution note.
#' @param status Final status.
#' @return Updated workflow.
#' @export
resolve_change_request <- function(workflow, request_id, actor_id, resolution, status = c("resolved", "rejected")) {
  validate_institutional_governance(workflow)
  .governance_require_permission(workflow, actor_id, "respond_change")
  request <- workflow$change_requests[[request_id]]
  if (is.null(request)) stop("Change request does not exist.", call. = FALSE)
  if (!identical(request$status, "open")) stop("Change request is already closed.", call. = FALSE)
  .assert_single_string(resolution, "resolution"); status <- match.arg(status)
  request$status <- status; request$resolution <- resolution; request$resolved_by <- actor_id; request$resolved_at <- .utc_now()
  workflow$change_requests[[request_id]] <- request
  if (!any(vapply(workflow$change_requests, function(x) identical(x$status, "open"), logical(1)))) workflow$status <- "in_review"
  workflow <- .governance_audit(workflow, "change_request_closed", actor_id, "change_request", request_id, list(status = status))
  validate_institutional_governance(workflow); workflow
}

#' Record an approval decision
#'
#' @param workflow Governance workflow.
#' @param approval_id Stable approval identifier.
#' @param actor_id Approver actor identifier.
#' @param decision Approval decision.
#' @param scope Approval scope.
#' @param note Decision note.
#' @return Updated workflow.
#' @export
record_governance_approval <- function(workflow, approval_id, actor_id, decision = c("approved", "rejected", "changes_requested"), scope = "project", note = "") {
  validate_institutional_governance(workflow)
  .governance_id(approval_id, "approval_id"); decision <- match.arg(decision)
  .governance_require_permission(workflow, actor_id, if (identical(decision, "approved")) "approve" else if (identical(decision, "rejected")) "reject" else "request_change")
  .assert_single_string(scope, "scope"); .assert_single_string(note, "note", allow_empty = TRUE)
  if (!is.null(workflow$approvals[[approval_id]])) stop("Approval identifier already exists.", call. = FALSE)
  workflow$approvals[[approval_id]] <- list(id = approval_id, actor_id = actor_id, decision = decision, scope = scope, note = note, project_fingerprint = workflow$project$fingerprint, decided_at = .utc_now())
  workflow$status <- switch(decision, approved = "approved", rejected = "rejected", changes_requested = "changes_requested")
  workflow <- .governance_audit(workflow, "approval_recorded", actor_id, "approval", approval_id, list(decision = decision, scope = scope))
  validate_institutional_governance(workflow); workflow
}

#' Sign an analytical release
#'
#' @param workflow Governance workflow.
#' @param release_id Stable release identifier.
#' @param actor_id Publisher actor identifier.
#' @param title Release title.
#' @param artifact_hashes Named artifact hashes.
#' @param statement Signature statement.
#' @return Updated workflow with signed release record.
#' @export
sign_analytical_release <- function(workflow, release_id, actor_id, title, artifact_hashes, statement = "Approved for governed publication subject to the recorded scope and limitations.") {
  validate_institutional_governance(workflow)
  .governance_id(release_id, "release_id"); .governance_require_permission(workflow, actor_id, "publish")
  .assert_single_string(title, "title"); .assert_single_string(statement, "statement")
  if (!is.list(artifact_hashes) && !is.character(artifact_hashes)) stop("`artifact_hashes` must be a named list or character vector.", call. = FALSE)
  if (is.null(names(artifact_hashes)) || any(!nzchar(names(artifact_hashes)))) stop("`artifact_hashes` must be named.", call. = FALSE)
  if (!isTRUE(workflow$access_policy$publication_allowed)) stop("Access policy prohibits publication.", call. = FALSE)
  open_changes <- vapply(workflow$change_requests, function(x) identical(x$status, "open"), logical(1))
  if (any(open_changes)) stop("Open change requests must be resolved before signing.", call. = FALSE)
  approved <- Filter(function(x) identical(x$decision, "approved"), workflow$approvals)
  if (length(unique(vapply(approved, `[[`, character(1), "actor_id"))) < workflow$template$required_approvals) stop("Required institutional approvals are incomplete.", call. = FALSE)
  if (!is.null(workflow$signed_releases[[release_id]])) stop("Release identifier already exists.", call. = FALSE)
  signed_at <- .utc_now()
  signature <- .project_hash(list(workflow_id = workflow$id, project_fingerprint = workflow$project$fingerprint, actor_id = actor_id, artifact_hashes = artifact_hashes, statement = statement, signed_at = signed_at))
  workflow$signed_releases[[release_id]] <- list(id = release_id, title = title, actor_id = actor_id, project_id = workflow$project$id, project_fingerprint = workflow$project$fingerprint, artifact_hashes = as.list(artifact_hashes), statement = statement, signature = signature, signed_at = signed_at, revocation_status = "active")
  workflow$status <- "signed"
  workflow <- .governance_audit(workflow, "analytical_release_signed", actor_id, "signed_release", release_id, list(signature = signature))
  validate_institutional_governance(workflow); workflow
}

#' Archive an institutional governance workflow
#'
#' @param workflow Governance workflow.
#' @param actor_id Archiving actor identifier.
#' @param reason Archive rationale.
#' @return Archived workflow.
#' @export
archive_governance_workflow <- function(workflow, actor_id, reason) {
  validate_institutional_governance(workflow)
  .governance_require_permission(workflow, actor_id, "archive")
  .assert_single_string(reason, "reason")
  archived_at <- .utc_now()
  workflow$status <- "archived"
  workflow$retention$archive_status <- "archived"
  workflow$retention$archive_reason <- reason
  workflow$retention$archived_at <- archived_at
  archive_time <- as.POSIXct(strptime(archived_at, format = "%Y-%m-%dT%H:%M:%SZ", tz = "UTC"))
  workflow$retention$disposal_eligible_at <- format(archive_time + workflow$retention$retention_days * 86400, "%Y-%m-%dT%H:%M:%SZ", tz = "UTC")
  workflow <- .governance_audit(workflow, "workflow_archived", actor_id, "workflow", workflow$id, list(reason = reason, disposal_eligible_at = workflow$retention$disposal_eligible_at))
  validate_institutional_governance(workflow); workflow
}

#' Apply governance status to a project
#'
#' @param project Reproducible project.
#' @param workflow Institutional governance workflow for the project.
#' @return Updated project metadata.
#' @export
apply_governance_to_project <- function(project, workflow) {
  validate_catalyst_project(project); validate_institutional_governance(workflow)
  if (!identical(project$id, workflow$project$id)) stop("Workflow does not govern this project.", call. = FALSE)
  project$metadata$review_status <- if (workflow$status %in% c("approved", "signed", "archived")) "approved" else if (identical(workflow$status, "rejected")) "rejected" else "in_review"
  project$metadata$publication_status <- if (identical(workflow$status, "signed")) "approved" else if (identical(workflow$status, "archived") && length(workflow$signed_releases)) "published" else "draft"
  project$metadata$governance_workflow_id <- workflow$id
  project$metadata$governance_fingerprint <- .project_hash(workflow)
  .project_touch(project)
}

#' Institutional governance audit log
#'
#' @param workflow Governance workflow.
#' @return Audit history data frame.
#' @export
governance_audit_log <- function(workflow) {
  validate_institutional_governance(workflow)
  if (!length(workflow$audit)) return(data.frame(id = character(), action = character(), actor_id = character(), object_type = character(), object_id = character(), recorded_at = character(), stringsAsFactors = FALSE))
  do.call(rbind, lapply(workflow$audit, function(x) data.frame(id = x$id, action = x$action, actor_id = x$actor_id, object_type = x$object_type, object_id = x$object_id, recorded_at = x$recorded_at, stringsAsFactors = FALSE)))
}

#' Summarize institutional governance status
#'
#' @param workflow Governance workflow.
#' @return Governance summary list.
#' @export
governance_summary <- function(workflow) {
  validate_institutional_governance(workflow)
  open_changes <- sum(vapply(workflow$change_requests, function(x) identical(x$status, "open"), logical(1)))
  approved <- sum(vapply(workflow$approvals, function(x) identical(x$decision, "approved"), logical(1)))
  list(schema_version = workflow$schema_version, workflow_id = workflow$id, project_id = workflow$project$id, institution = workflow$institution, status = workflow$status, classification = workflow$access_policy$classification, actors = length(workflow$actors), assignments = length(workflow$review_assignments), comments = length(workflow$comments), change_requests = length(workflow$change_requests), open_change_requests = open_changes, approvals = length(workflow$approvals), approved_decisions = approved, required_approvals = workflow$template$required_approvals, signed_releases = length(workflow$signed_releases), archived = identical(workflow$retention$archive_status, "archived"), human_approval_required = TRUE, automated_publication = FALSE)
}

#' Serialize an institutional governance workflow
#'
#' @param workflow Governance workflow.
#' @param path Optional destination path. When `NULL`, returns JSON text.
#' @param pretty Pretty-print JSON.
#' @return JSON text or invisibly returns `path`.
#' @export
governance_to_json <- function(workflow, path = NULL, pretty = TRUE) {
  validate_institutional_governance(workflow)
  value <- .safe_json_value(unclass(workflow))
  if (is.null(path)) return(as.character(jsonlite::toJSON(value, auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")))
  jsonlite::write_json(value, path, auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  invisible(path)
}

#' Restore an institutional governance workflow from JSON
#'
#' @param x JSON text or file path.
#' @return A `catalyst_institutional_governance` record.
#' @export
governance_from_json <- function(x) {
  .assert_single_string(x, "x")
  record <- jsonlite::fromJSON(x, simplifyVector = FALSE)
  for (field in c("roles", "actors", "review_assignments", "comments", "change_requests", "approvals", "signed_releases")) if (is.null(record[[field]])) record[[field]] <- list()
  result <- structure(record, class = c("catalyst_institutional_governance", "list"))
  validate_institutional_governance(result); result
}

.governance_rows <- function(records, fields) {
  if (!length(records)) return(as.data.frame(stats::setNames(lapply(fields, function(x) character()), fields), stringsAsFactors = FALSE))
  do.call(rbind, lapply(records, function(record) {
    values <- lapply(fields, function(field) {
      value <- record[[field]]
      if (is.null(value)) "" else if (length(value) > 1L) paste(value, collapse = "; ") else as.character(value)
    })
    names(values) <- fields
    as.data.frame(values, stringsAsFactors = FALSE)
  }))
}

#' Export an institutional governance bundle
#'
#' @param workflow Governance workflow.
#' @param dir Destination directory.
#' @param prefix Bundle prefix.
#' @param zip_bundle Create a ZIP archive.
#' @return Named generated paths.
#' @export
export_institutional_governance <- function(workflow, dir = ".", prefix = "catalyst-institutional-governance", zip_bundle = TRUE) {
  validate_institutional_governance(workflow)
  .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(zip_bundle, "zip_bundle")
  if (!isTRUE(workflow$access_policy$export_allowed)) stop("Access policy prohibits export.", call. = FALSE)
  bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(bundle_dir = bundle_dir)
  paths$workflow <- file.path(bundle_dir, "institutional-governance.json"); governance_to_json(workflow, paths$workflow)
  paths$summary <- file.path(bundle_dir, "governance-summary.json"); jsonlite::write_json(governance_summary(workflow), paths$summary, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null")
  tables <- list(
    review_assignments = list(file = "review-assignments.csv", records = workflow$review_assignments, fields = c("id", "reviewer_id", "review_type", "target_type", "target_id", "status", "assigned_at", "due_at", "completed_at")),
    comments = list(file = "structured-comments.csv", records = workflow$comments, fields = c("id", "author_id", "target_type", "target_id", "severity", "disposition", "body", "created_at", "resolved_at")),
    change_requests = list(file = "change-requests.csv", records = workflow$change_requests, fields = c("id", "requester_id", "title", "priority", "target_type", "target_id", "status", "resolution", "created_at", "resolved_at")),
    approvals = list(file = "approvals.csv", records = workflow$approvals, fields = c("id", "actor_id", "decision", "scope", "note", "decided_at")),
    signed_releases = list(file = "signed-releases.csv", records = workflow$signed_releases, fields = c("id", "title", "actor_id", "project_id", "project_fingerprint", "signature", "signed_at", "revocation_status"))
  )
  for (name in names(tables)) {
    spec <- tables[[name]]; paths[[name]] <- file.path(bundle_dir, spec$file)
    utils::write.csv(.governance_rows(spec$records, spec$fields), paths[[name]], row.names = FALSE)
  }
  paths$audit <- file.path(bundle_dir, "audit-log.csv"); utils::write.csv(governance_audit_log(workflow), paths$audit, row.names = FALSE)
  paths$readme <- file.path(bundle_dir, "README.md")
  summary <- governance_summary(workflow)
  writeLines(c(paste0("# ", workflow$title), "", paste0("Institution: ", workflow$institution$name), paste0("Project: ", workflow$project$title), paste0("Status: ", workflow$status), paste0("Classification: ", workflow$access_policy$classification), paste0("Open change requests: ", summary$open_change_requests), paste0("Approved decisions: ", summary$approved_decisions, " / ", summary$required_approvals), paste0("Signed releases: ", summary$signed_releases), "", "This bundle preserves review assignments, comments, change requests, approvals, signatures, audit history, access controls, retention metadata, and human-approval boundaries."), paths$readme, useBytes = TRUE)
  files <- list.files(bundle_dir, full.names = TRUE, recursive = TRUE)
  base <- normalizePath(bundle_dir)
  records <- lapply(files, function(path) list(file = substring(normalizePath(path), nchar(base) + 2L), bytes = unname(file.info(path)$size), md5 = unname(tools::md5sum(path))))
  manifest <- list(schema_version = .catalyst_governance_export_schema_version(), export_type = "institutional_governance_bundle", workflow_id = workflow$id, project_id = workflow$project$id, package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), created_at = .utc_now(), file_count = length(records), files = records, integrity = list(hash_algorithm = "md5", complete = TRUE, scope = "all_bundle_files_except_manifest"), boundary = list(human_approval_required = TRUE, automated_publication = FALSE, access_policy_enforced = TRUE))
  paths$manifest <- file.path(bundle_dir, "manifest.json"); jsonlite::write_json(manifest, paths$manifest, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", digits = NA, dataframe = "rows")
  if (zip_bundle) { paths$zip <- file.path(dir, paste0(prefix, ".zip")); old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir); utils::zip(zipfile = basename(paths$zip), files = prefix) }
  paths
}

#' Add an institutional governance workflow to a workspace
#'
#' @param workspace Workspace.
#' @param workflow Institutional governance workflow.
#' @param replace Replace an existing workflow.
#' @return Updated workspace.
#' @export
workspace_add_institutional_governance <- function(workspace, workflow, replace = FALSE) {
  validate_catalyst_workspace(workspace); validate_institutional_governance(workflow); .assert_flag(replace, "replace")
  if (is.null(workspace$libraries$institutional_governance)) workspace$libraries$institutional_governance <- list()
  if (!is.null(workspace$libraries$institutional_governance[[workflow$id]]) && !replace) stop("Institutional governance workflow already exists.", call. = FALSE)
  workspace$libraries$institutional_governance[[workflow$id]] <- workflow
  .workspace_touch(workspace, "institutional_governance_added", list(workflow_id = workflow$id, project_id = workflow$project$id))
}

#' Retrieve institutional governance from a workspace
#'
#' @param workspace Workspace.
#' @param workflow_id Workflow identifier.
#' @return Institutional governance workflow.
#' @export
workspace_get_institutional_governance <- function(workspace, workflow_id) {
  validate_catalyst_workspace(workspace); .governance_id(workflow_id, "workflow_id")
  workflow <- workspace$libraries$institutional_governance[[workflow_id]]
  if (is.null(workflow)) stop("Institutional governance workflow is not present in the workspace.", call. = FALSE)
  workflow
}

#' @export
print.catalyst_institutional_governance <- function(x, ...) {
  summary <- governance_summary(x)
  cat(sprintf("<catalyst_institutional_governance %s>\n", x$id))
  cat(sprintf("  institution: %s | project: %s\n", x$institution$name, x$project$id))
  cat(sprintf("  status: %s | assignments: %d | open changes: %d | signed releases: %d\n", x$status, summary$assignments, summary$open_change_requests, summary$signed_releases))
  invisible(x)
}
