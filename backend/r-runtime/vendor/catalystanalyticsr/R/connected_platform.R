.catalyst_connected_platform_schema_version <- function() "2.0.0"
.catalyst_connected_platform_export_schema_version <- function() "2.0.0"
.catalyst_connected_api_schema_version <- function() "2.0.0"

.platform_named_list <- function(x, arg) {
  if (is.null(x)) return(list())
  if (!is.list(x)) stop(sprintf("`%s` must be a list.", arg), call. = FALSE)
  if (length(x) && (is.null(names(x)) || any(!nzchar(names(x))))) {
    stop(sprintf("Every `%s` entry must be named.", arg), call. = FALSE)
  }
  x
}

.platform_touch <- function(platform, action = NULL, details = list()) {
  platform[[".restored_connected_platform_fingerprint"]] <- NULL
  platform[[".restored_connected_platform_state_fingerprint"]] <- NULL
  platform$metadata$updated_at <- .utc_now()
  platform$metadata$package_version <- .catalyst_package_version()
  if (!is.null(action)) {
    platform$audit[[length(platform$audit) + 1L]] <- list(
      id = paste0("platform-audit-", length(platform$audit) + 1L),
      action = action,
      details = .safe_json_value(details),
      recorded_at = .utc_now()
    )
  }
  platform
}

#' Define a connected-platform graph node
#'
#' @param node_id Stable node identifier.
#' @param node_type Node type.
#' @param title Human-readable title.
#' @param reference Contract and source reference.
#' @param provenance Provenance record.
#' @param review_status Review state.
#' @param metadata Additional metadata.
#' @return A platform node record.
#' @export
platform_node <- function(node_id, node_type = c("workspace", "project", "scenario", "dataset", "model", "indicator", "evidence", "decision", "governance", "publication", "handoff", "workflow", "external_source"), title, reference = list(), provenance = list(), review_status = c("unreviewed", "in_review", "approved", "rejected", "archived"), metadata = list()) {
  .project_id(node_id, "node_id")
  node_type <- match.arg(node_type)
  review_status <- match.arg(review_status)
  .assert_single_string(title, "title")
  if (!is.list(reference) || !is.list(provenance) || !is.list(metadata)) stop("`reference`, `provenance`, and `metadata` must be lists.", call. = FALSE)
  structure(list(
    schema_version = "1.0.0", id = node_id, node_type = node_type, title = title,
    reference = reference, provenance = provenance, review_status = review_status,
    metadata = metadata
  ), class = c("catalyst_platform_node", "list"))
}

#' Define a connected-platform lineage edge
#'
#' @param edge_id Stable edge identifier.
#' @param from_id Origin node identifier.
#' @param to_id Destination node identifier.
#' @param relation Directed relationship type.
#' @param evidence_ids Evidence records supporting the relationship.
#' @param provenance Provenance record.
#' @param review_status Review state.
#' @param metadata Additional metadata.
#' @return A platform edge record.
#' @export
platform_edge <- function(edge_id, from_id, to_id, relation, evidence_ids = character(), provenance = list(), review_status = c("unreviewed", "in_review", "approved", "rejected", "archived"), metadata = list()) {
  .project_id(edge_id, "edge_id"); .project_id(from_id, "from_id"); .project_id(to_id, "to_id")
  .assert_single_string(relation, "relation")
  review_status <- match.arg(review_status)
  if (!is.character(evidence_ids) || anyNA(evidence_ids)) stop("`evidence_ids` must be a character vector.", call. = FALSE)
  if (!is.list(provenance) || !is.list(metadata)) stop("`provenance` and `metadata` must be lists.", call. = FALSE)
  structure(list(
    schema_version = "1.0.0", id = edge_id, from_id = from_id, to_id = to_id,
    relation = relation, evidence_ids = unique(evidence_ids), provenance = provenance,
    review_status = review_status, metadata = metadata
  ), class = c("catalyst_platform_edge", "list"))
}

#' Create an evidence record
#'
#' @param evidence_id Stable evidence identifier.
#' @param title Human-readable title.
#' @param source_type Source type.
#' @param source_ref Source reference.
#' @param claims Claim identifiers or summaries.
#' @param quality_status Quality status.
#' @param metadata Additional metadata.
#' @return Evidence record.
#' @export
platform_evidence_record <- function(evidence_id, title, source_type, source_ref, claims = character(), quality_status = c("unassessed", "provisional", "reviewed", "verified", "disputed"), metadata = list()) {
  .project_id(evidence_id, "evidence_id"); .assert_single_string(title, "title"); .assert_single_string(source_type, "source_type")
  quality_status <- match.arg(quality_status)
  if (!is.list(source_ref) || !is.character(claims) || anyNA(claims) || !is.list(metadata)) stop("Invalid evidence source, claims, or metadata.", call. = FALSE)
  list(id = evidence_id, title = title, source_type = source_type, source_ref = source_ref, claims = unique(claims), quality_status = quality_status, metadata = metadata)
}

#' Create a connected decision record
#'
#' @param decision_id Stable decision identifier.
#' @param title Decision title.
#' @param alternatives Character vector of alternatives.
#' @param evidence_ids Supporting evidence identifiers.
#' @param selected_alternative Optional selected alternative.
#' @param governance_status Governance state.
#' @param metadata Additional metadata.
#' @return Decision record.
#' @export
platform_decision_record <- function(decision_id, title, alternatives, evidence_ids = character(), selected_alternative = NULL, governance_status = c("draft", "in_review", "approved", "rejected", "archived"), metadata = list()) {
  .project_id(decision_id, "decision_id"); .assert_single_string(title, "title")
  if (!is.character(alternatives) || !length(alternatives) || anyNA(alternatives)) stop("`alternatives` must be a non-empty character vector.", call. = FALSE)
  if (!is.character(evidence_ids) || anyNA(evidence_ids)) stop("`evidence_ids` must be a character vector.", call. = FALSE)
  if (!is.null(selected_alternative) && (!is.character(selected_alternative) || length(selected_alternative) != 1L || !selected_alternative %in% alternatives)) stop("`selected_alternative` must identify one declared alternative.", call. = FALSE)
  governance_status <- match.arg(governance_status)
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  list(id = decision_id, title = title, alternatives = unique(alternatives), evidence_ids = unique(evidence_ids), selected_alternative = selected_alternative, governance_status = governance_status, metadata = metadata)
}

#' Create a connected publication record
#'
#' @param publication_id Stable publication identifier.
#' @param title Publication title.
#' @param artifact_refs Named artifact references.
#' @param evidence_ids Supporting evidence identifiers.
#' @param review_status Review state.
#' @param publication_status Publication state.
#' @param metadata Additional metadata.
#' @return Publication record.
#' @export
platform_publication_record <- function(publication_id, title, artifact_refs = list(), evidence_ids = character(), review_status = c("unreviewed", "in_review", "approved", "rejected"), publication_status = c("draft", "approved", "published", "withdrawn", "archived"), metadata = list()) {
  .project_id(publication_id, "publication_id"); .assert_single_string(title, "title")
  .platform_named_list(artifact_refs, "artifact_refs")
  if (!is.character(evidence_ids) || anyNA(evidence_ids) || !is.list(metadata)) stop("Invalid publication evidence or metadata.", call. = FALSE)
  review_status <- match.arg(review_status); publication_status <- match.arg(publication_status)
  list(id = publication_id, title = title, artifact_refs = artifact_refs, evidence_ids = unique(evidence_ids), review_status = review_status, publication_status = publication_status, metadata = metadata)
}

#' Create a governed connected workflow
#'
#' @param workflow_id Stable workflow identifier.
#' @param title Workflow title.
#' @param stages Ordered stage identifiers.
#' @param owner Workflow owner.
#' @param input_node_ids Input node identifiers.
#' @param output_node_ids Output node identifiers.
#' @param status Workflow status.
#' @param human_review_required Require human review at decision gates.
#' @param metadata Additional metadata.
#' @return Connected workflow record.
#' @export
connected_workflow <- function(workflow_id, title, stages, owner = "", input_node_ids = character(), output_node_ids = character(), status = c("draft", "active", "blocked", "completed", "archived"), human_review_required = TRUE, metadata = list()) {
  .project_id(workflow_id, "workflow_id"); .assert_single_string(title, "title"); .assert_single_string(owner, "owner", allow_empty = TRUE)
  if (!is.character(stages) || !length(stages) || anyNA(stages)) stop("`stages` must be a non-empty character vector.", call. = FALSE)
  if (!is.character(input_node_ids) || anyNA(input_node_ids) || !is.character(output_node_ids) || anyNA(output_node_ids)) stop("Workflow node identifiers must be character vectors.", call. = FALSE)
  status <- match.arg(status); .assert_flag(human_review_required, "human_review_required")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  list(id = workflow_id, title = title, stages = unique(stages), owner = owner, input_node_ids = unique(input_node_ids), output_node_ids = unique(output_node_ids), status = status, human_review_required = human_review_required, metadata = metadata)
}

#' Create the connected sustainability analytics platform
#'
#' @param platform_id Stable platform identifier.
#' @param title Human-readable title.
#' @param institution_id Institution identifier.
#' @param institution_name Institution name.
#' @param metadata Additional metadata.
#' @return A `catalyst_connected_platform`.
#' @export
connected_sustainability_platform <- function(platform_id, title, institution_id, institution_name, metadata = list()) {
  .project_id(platform_id, "platform_id"); .assert_single_string(title, "title")
  .project_id(institution_id, "institution_id"); .assert_single_string(institution_name, "institution_name")
  if (!is.list(metadata)) stop("`metadata` must be a list.", call. = FALSE)
  now <- .utc_now()
  platform <- structure(list(
    schema_version = .catalyst_connected_platform_schema_version(),
    platform_type = "connected_sustainability_analytics_and_decision_platform",
    id = platform_id, title = title,
    institution = list(id = institution_id, name = institution_name),
    workspaces = list(), projects = list(), nodes = list(), edges = list(),
    registries = list(models = list(), indicators = list(), evidence = list()),
    decisions = list(), publications = list(), governance = list(), handoffs = list(), workflows = list(),
    audit = list(),
    metadata = utils::modifyList(list(package_version = .catalyst_package_version(), created_at = now, updated_at = now, status = "active"), metadata),
    boundary = list(human_review_required = TRUE, automated_decision_authorization = FALSE, automated_publication = FALSE, external_identity_and_transport_provided_by_host = TRUE)
  ), class = c("catalyst_connected_platform", "list"))
  platform <- .platform_touch(platform, "platform_created", list(institution_id = institution_id))
  validate_connected_platform(platform)
  platform
}

#' Validate a connected sustainability platform
#'
#' @param platform Platform record.
#' @return Invisibly returns `TRUE`.
#' @export
validate_connected_platform <- function(platform) {
  if (!is.list(platform)) stop("`platform` must be a list.", call. = FALSE)
  required <- c("schema_version", "platform_type", "id", "title", "institution", "workspaces", "projects", "nodes", "edges", "registries", "decisions", "publications", "governance", "handoffs", "workflows", "audit", "metadata", "boundary")
  missing <- setdiff(required, names(platform)); if (length(missing)) stop("Connected platform is missing fields: ", paste(missing, collapse = ", "), call. = FALSE)
  if (!identical(platform$schema_version, .catalyst_connected_platform_schema_version()) || !identical(platform$platform_type, "connected_sustainability_analytics_and_decision_platform")) stop("Unsupported connected-platform contract.", call. = FALSE)
  .project_id(platform$id, "platform$id"); .assert_single_string(platform$title, "platform$title")
  if (!is.list(platform$institution) || is.null(platform$institution$id) || is.null(platform$institution$name)) stop("Platform institution is incomplete.", call. = FALSE)
  for (field in c("workspaces", "projects", "nodes", "edges", "decisions", "publications", "governance", "handoffs", "workflows")) .platform_named_list(platform[[field]], paste0("platform$", field))
  if (!is.list(platform$registries) || length(setdiff(c("models", "indicators", "evidence"), names(platform$registries)))) stop("Platform registries are incomplete.", call. = FALSE)
  for (field in c("models", "indicators", "evidence")) .platform_named_list(platform$registries[[field]], paste0("platform$registries$", field))
  for (workspace in platform$workspaces) validate_catalyst_workspace(workspace)
  for (project in platform$projects) validate_catalyst_project(project)
  for (node in platform$nodes) {
    if (!is.list(node) || is.null(node$id) || is.null(node$node_type) || is.null(node$title)) stop("Platform node is incomplete.", call. = FALSE)
  }
  for (edge in platform$edges) {
    if (!is.list(edge) || is.null(edge$id) || is.null(edge$from_id) || is.null(edge$to_id) || is.null(edge$relation)) stop("Platform edge is incomplete.", call. = FALSE)
    if (is.null(platform$nodes[[edge$from_id]]) || is.null(platform$nodes[[edge$to_id]])) stop("Platform edge references an unknown node.", call. = FALSE)
    if (length(setdiff(edge$evidence_ids, names(platform$registries$evidence)))) stop("Platform edge references unknown evidence.", call. = FALSE)
  }
  for (decision in platform$decisions) if (length(setdiff(decision$evidence_ids, names(platform$registries$evidence)))) stop("Decision references unknown evidence.", call. = FALSE)
  for (publication in platform$publications) if (length(setdiff(publication$evidence_ids, names(platform$registries$evidence)))) stop("Publication references unknown evidence.", call. = FALSE)
  for (workflow in platform$workflows) {
    missing_nodes <- setdiff(c(workflow$input_node_ids, workflow$output_node_ids), names(platform$nodes))
    if (length(missing_nodes)) stop("Workflow references unknown platform nodes.", call. = FALSE)
  }
  if (!is.list(platform$audit) || !is.list(platform$metadata) || !is.list(platform$boundary)) stop("Platform audit, metadata, and boundary must be lists.", call. = FALSE)
  invisible(TRUE)
}

.platform_node_id <- function(owner_type, owner_id, record_type = NULL, record_id = NULL) {
  parts <- c(owner_type, owner_id, record_type, record_id); parts <- parts[!is.na(parts) & nzchar(parts)]
  gsub("[^A-Za-z0-9._-]", "-", paste(parts, collapse = "."))
}

.platform_edge_id <- function(from_id, relation, to_id) gsub("[^A-Za-z0-9._-]", "-", paste(from_id, relation, to_id, sep = "--"))

#' Add or replace a graph node
#'
#' @param platform Connected platform.
#' @param node Platform node.
#' @return Updated platform.
#' @export
platform_add_node <- function(platform, node) {
  validate_connected_platform(platform)
  if (!is.list(node) || is.null(node$id)) stop("`node` must be a platform node.", call. = FALSE)
  platform$nodes[[node$id]] <- node
  platform <- .platform_touch(platform, "node_upserted", list(node_id = node$id, node_type = node$node_type))
  validate_connected_platform(platform); platform
}

#' Add or replace a lineage edge
#'
#' @param platform Connected platform.
#' @param edge Platform edge.
#' @return Updated platform.
#' @export
platform_add_edge <- function(platform, edge) {
  validate_connected_platform(platform)
  if (is.null(platform$nodes[[edge$from_id]]) || is.null(platform$nodes[[edge$to_id]])) stop("Both edge endpoints must exist before the edge is added.", call. = FALSE)
  if (length(setdiff(edge$evidence_ids, names(platform$registries$evidence)))) stop("Edge references unknown evidence.", call. = FALSE)
  platform$edges[[edge$id]] <- edge
  platform <- .platform_touch(platform, "edge_upserted", list(edge_id = edge$id, relation = edge$relation))
  validate_connected_platform(platform); platform
}

.platform_put_node <- function(platform, node) { platform$nodes[[node$id]] <- node; platform }
.platform_put_edge <- function(platform, from_id, to_id, relation, evidence_ids = character(), review_status = "unreviewed") {
  edge <- platform_edge(.platform_edge_id(from_id, relation, to_id), from_id, to_id, relation, evidence_ids = evidence_ids, review_status = review_status)
  platform$edges[[edge$id]] <- edge; platform
}

.platform_index_project <- function(platform, project, workspace_id = NULL) {
  project_id <- .platform_node_id("project", project$id)
  project_review <- project$metadata$review_status
  if (is.null(project_review)) project_review <- "unreviewed"
  if (identical(project_review, "reviewed")) project_review <- "approved"
  if (!project_review %in% c("unreviewed", "in_review", "approved", "rejected", "archived")) project_review <- "in_review"
  platform <- .platform_put_node(platform, platform_node(project_id, "project", project$title, list(contract = "catalyst_project@1.0.0", record_id = project$id, fingerprint = project_fingerprint(project), workspace_id = workspace_id), review_status = project_review))
  if (!is.null(workspace_id)) platform <- .platform_put_edge(platform, .platform_node_id("workspace", workspace_id), project_id, "contains_project")
  collections <- list(scenario = project$scenarios, dataset = project$datasets, model = project$models, indicator = project$indicators, publication = project$publications)
  relations <- c(scenario = "uses_scenario", dataset = "uses_dataset", model = "uses_model", indicator = "produces_indicator", publication = "produces_publication")
  for (kind in names(collections)) {
    records <- collections[[kind]]
    if (!length(records)) next
    for (record_id in names(records)) {
      record <- records[[record_id]]
      title <- if (!is.null(record$title)) as.character(record$title)[1L] else record_id
      node_id <- .platform_node_id("project", project$id, kind, record_id)
      platform <- .platform_put_node(platform, platform_node(node_id, kind, title, list(contract = paste0("catalyst_", kind, "@1.0.0"), record_id = record_id, project_id = project$id, workspace_id = workspace_id)))
      platform <- .platform_put_edge(platform, project_id, node_id, unname(relations[kind]))
    }
  }
  platform
}

#' Add and index a reproducible project
#'
#' @param platform Connected platform.
#' @param project Reproducible project.
#' @return Updated platform.
#' @export
platform_add_project <- function(platform, project) {
  validate_connected_platform(platform); validate_catalyst_project(project)
  platform$projects[[project$id]] <- project
  platform <- .platform_index_project(platform, project)
  platform <- .platform_touch(platform, "project_indexed", list(project_id = project$id))
  validate_connected_platform(platform); platform
}

#' Add and index a persistent workspace
#'
#' @param platform Connected platform.
#' @param workspace Persistent workspace.
#' @return Updated platform.
#' @export
platform_add_workspace <- function(platform, workspace) {
  validate_connected_platform(platform); validate_catalyst_workspace(workspace)
  platform$workspaces[[workspace$id]] <- workspace
  workspace_node_id <- .platform_node_id("workspace", workspace$id)
  platform <- .platform_put_node(platform, platform_node(workspace_node_id, "workspace", workspace$title, list(contract = "catalyst_workspace@1.0.0", record_id = workspace$id, fingerprint = workspace_fingerprint(workspace))))
  for (project in workspace$projects) {
    platform$projects[[project$id]] <- project
    platform <- .platform_index_project(platform, project, workspace$id)
  }
  platform <- .platform_touch(platform, "workspace_indexed", list(workspace_id = workspace$id, project_count = length(workspace$projects)))
  validate_connected_platform(platform); platform
}

#' Register model, indicator, or evidence records
#'
#' @param platform Connected platform.
#' @param registry Registry name.
#' @param records Named records.
#' @param replace Allow replacement of existing identifiers.
#' @return Updated platform.
#' @export
platform_register_records <- function(platform, registry = c("models", "indicators", "evidence"), records, replace = FALSE) {
  validate_connected_platform(platform); registry <- match.arg(registry); .platform_named_list(records, "records"); .assert_flag(replace, "replace")
  duplicates <- intersect(names(records), names(platform$registries[[registry]]))
  if (length(duplicates) && !replace) stop("Registry identifiers already exist: ", paste(duplicates, collapse = ", "), call. = FALSE)
  for (id in names(records)) {
    record <- records[[id]]
    if (!is.list(record)) stop("Every registry record must be a list.", call. = FALSE)
    if (is.null(record$id)) record$id <- id
    platform$registries[[registry]][[id]] <- record
    node_type <- if (registry == "models") "model" else if (registry == "indicators") "indicator" else "evidence"
    title <- if (!is.null(record$title)) as.character(record$title)[1L] else id
    platform$nodes[[.platform_node_id("registry", registry, node_type, id)]] <- platform_node(.platform_node_id("registry", registry, node_type, id), node_type, title, list(registry = registry, record_id = id), review_status = if (registry == "evidence" && !is.null(record$quality_status) && record$quality_status %in% c("reviewed", "verified")) "approved" else "unreviewed")
  }
  platform <- .platform_touch(platform, "registry_updated", list(registry = registry, record_ids = names(records)))
  validate_connected_platform(platform); platform
}

#' Add a decision record to the connected graph
#'
#' @param platform Connected platform.
#' @param decision Decision record.
#' @return Updated platform.
#' @export
platform_add_decision <- function(platform, decision) {
  validate_connected_platform(platform)
  if (!is.list(decision) || is.null(decision$id)) stop("`decision` must be a decision record.", call. = FALSE)
  if (length(setdiff(decision$evidence_ids, names(platform$registries$evidence)))) stop("Decision references unknown evidence.", call. = FALSE)
  platform$decisions[[decision$id]] <- decision
  node_id <- .platform_node_id("decision", decision$id)
  review <- if (decision$governance_status == "approved") "approved" else if (decision$governance_status == "rejected") "rejected" else "in_review"
  platform$nodes[[node_id]] <- platform_node(node_id, "decision", decision$title, list(contract = "catalyst_connected_decision@1.0.0", record_id = decision$id), review_status = review)
  for (evidence_id in decision$evidence_ids) platform <- .platform_put_edge(platform, .platform_node_id("registry", "evidence", "evidence", evidence_id), node_id, "supports_decision", evidence_ids = evidence_id, review_status = review)
  platform <- .platform_touch(platform, "decision_added", list(decision_id = decision$id))
  validate_connected_platform(platform); platform
}

#' Add a publication record to the connected graph
#'
#' @param platform Connected platform.
#' @param publication Publication record.
#' @return Updated platform.
#' @export
platform_add_publication <- function(platform, publication) {
  validate_connected_platform(platform)
  if (!is.list(publication) || is.null(publication$id)) stop("`publication` must be a publication record.", call. = FALSE)
  if (length(setdiff(publication$evidence_ids, names(platform$registries$evidence)))) stop("Publication references unknown evidence.", call. = FALSE)
  platform$publications[[publication$id]] <- publication
  node_id <- .platform_node_id("publication", publication$id)
  platform$nodes[[node_id]] <- platform_node(node_id, "publication", publication$title, list(contract = "catalyst_connected_publication@1.0.0", record_id = publication$id), review_status = publication$review_status)
  for (evidence_id in publication$evidence_ids) platform <- .platform_put_edge(platform, .platform_node_id("registry", "evidence", "evidence", evidence_id), node_id, "supports_publication", evidence_ids = evidence_id, review_status = publication$review_status)
  platform <- .platform_touch(platform, "publication_added", list(publication_id = publication$id))
  validate_connected_platform(platform); platform
}

#' Add an institutional governance record
#'
#' @param platform Connected platform.
#' @param governance Governance workflow.
#' @return Updated platform.
#' @export
platform_add_governance <- function(platform, governance) {
  validate_connected_platform(platform); validate_institutional_governance(governance)
  platform$governance[[governance$id]] <- governance
  node_id <- .platform_node_id("governance", governance$id)
  review <- if (governance$status %in% c("approved", "signed")) "approved" else if (governance$status == "rejected") "rejected" else "in_review"
  platform$nodes[[node_id]] <- platform_node(node_id, "governance", governance$title, list(contract = "catalyst_institutional_governance@1.0.0", record_id = governance$id, project_id = governance$project$id), review_status = review)
  project_node <- .platform_node_id("project", governance$project$id)
  if (!is.null(platform$nodes[[project_node]])) platform <- .platform_put_edge(platform, project_node, node_id, "governed_by", review_status = review)
  platform <- .platform_touch(platform, "governance_added", list(governance_id = governance$id))
  validate_connected_platform(platform); platform
}

#' Add a platform handoff
#'
#' @param platform Connected platform.
#' @param handoff Platform handoff record.
#' @return Updated platform.
#' @export
platform_add_handoff <- function(platform, handoff) {
  validate_connected_platform(platform); validate_platform_handoff(handoff)
  handoff_id <- if (!is.null(handoff$id)) handoff$id else paste0(handoff$target, "-", substr(handoff$project_fingerprint, 1L, 12L))
  .project_id(handoff_id, "handoff_id")
  platform$handoffs[[handoff_id]] <- handoff
  node_id <- .platform_node_id("handoff", handoff_id)
  platform$nodes[[node_id]] <- platform_node(node_id, "handoff", handoff$title, list(contract = "catalyst_platform_handoff@1.0.0", record_id = handoff_id, target = handoff$target, project_id = handoff$project_id), review_status = "in_review")
  project_node <- .platform_node_id("project", handoff$project_id)
  if (!is.null(platform$nodes[[project_node]])) platform <- .platform_put_edge(platform, project_node, node_id, "hands_off_to", review_status = "in_review")
  platform <- .platform_touch(platform, "handoff_added", list(handoff_id = handoff_id, target = handoff$target))
  validate_connected_platform(platform); platform
}

#' Add a governed workflow
#'
#' @param platform Connected platform.
#' @param workflow Connected workflow.
#' @return Updated platform.
#' @export
platform_add_workflow <- function(platform, workflow) {
  validate_connected_platform(platform)
  if (!is.list(workflow) || is.null(workflow$id)) stop("`workflow` must be a connected workflow.", call. = FALSE)
  missing_nodes <- setdiff(c(workflow$input_node_ids, workflow$output_node_ids), names(platform$nodes)); if (length(missing_nodes)) stop("Workflow references unknown nodes: ", paste(missing_nodes, collapse = ", "), call. = FALSE)
  platform$workflows[[workflow$id]] <- workflow
  node_id <- .platform_node_id("workflow", workflow$id)
  platform$nodes[[node_id]] <- platform_node(node_id, "workflow", workflow$title, list(contract = "catalyst_connected_workflow@1.0.0", record_id = workflow$id), review_status = if (workflow$status == "completed") "approved" else "in_review")
  for (id in workflow$input_node_ids) platform <- .platform_put_edge(platform, id, node_id, "workflow_input")
  for (id in workflow$output_node_ids) platform <- .platform_put_edge(platform, node_id, id, "workflow_output")
  platform <- .platform_touch(platform, "workflow_added", list(workflow_id = workflow$id))
  validate_connected_platform(platform); platform
}

#' Trace upstream and downstream lineage
#'
#' @param platform Connected platform.
#' @param node_id Starting node identifier.
#' @param direction Trace direction.
#' @param max_depth Maximum traversal depth.
#' @return Lineage record containing matched nodes and edges.
#' @export
platform_lineage <- function(platform, node_id, direction = c("upstream", "downstream", "both"), max_depth = 20L) {
  validate_connected_platform(platform); .project_id(node_id, "node_id"); direction <- match.arg(direction)
  if (is.null(platform$nodes[[node_id]])) stop("Unknown platform node.", call. = FALSE)
  if (!is.numeric(max_depth) || length(max_depth) != 1L || is.na(max_depth) || max_depth < 0) stop("`max_depth` must be a non-negative scalar.", call. = FALSE)
  visited <- node_id; frontier <- node_id; matched_edges <- character(); depth <- 0L
  while (length(frontier) && depth < as.integer(max_depth)) {
    next_frontier <- character()
    for (edge in platform$edges) {
      take <- FALSE; candidate <- NULL
      if (direction %in% c("downstream", "both") && edge$from_id %in% frontier) { take <- TRUE; candidate <- edge$to_id }
      if (direction %in% c("upstream", "both") && edge$to_id %in% frontier) { take <- TRUE; candidate <- edge$from_id }
      if (take) { matched_edges <- unique(c(matched_edges, edge$id)); if (!candidate %in% visited) next_frontier <- c(next_frontier, candidate) }
    }
    next_frontier <- unique(next_frontier); visited <- unique(c(visited, next_frontier)); frontier <- next_frontier; depth <- depth + 1L
  }
  list(schema_version = "1.0.0", origin_node_id = node_id, direction = direction, max_depth = as.integer(max_depth), node_ids = visited, edge_ids = matched_edges, nodes = platform$nodes[visited], edges = platform$edges[matched_edges])
}

#' Summarize a connected platform
#'
#' @param platform Connected platform.
#' @return Summary record.
#' @export
connected_platform_summary <- function(platform) {
  validate_connected_platform(platform)
  node_types <- if (length(platform$nodes)) table(vapply(platform$nodes, `[[`, character(1), "node_type")) else integer()
  list(
    platform_id = platform$id, title = platform$title, package_version = .catalyst_package_version(),
    workspaces = length(platform$workspaces), projects = length(platform$projects), nodes = length(platform$nodes), edges = length(platform$edges),
    evidence_records = length(platform$registries$evidence), model_records = length(platform$registries$models), indicator_records = length(platform$registries$indicators),
    decisions = length(platform$decisions), publications = length(platform$publications), governance_records = length(platform$governance), handoffs = length(platform$handoffs), workflows = length(platform$workflows),
    node_types = as.list(node_types), human_review_required = isTRUE(platform$boundary$human_review_required)
  )
}

#' Connected platform manifest
#'
#' @param platform Connected platform.
#' @return Machine-readable platform manifest.
#' @export
connected_platform_manifest <- function(platform) {
  validate_connected_platform(platform)
  list(
    schema_version = "2.0.0", platform_id = platform$id, platform_fingerprint = connected_platform_fingerprint(platform),
    package = list(name = "catalystanalyticsr", version = .catalyst_package_version()),
    contracts = list(connected_platform = "2.0.0", connected_platform_export = "2.0.0", public_api_v1 = "1.0.0", connected_api_v2 = "2.0.0", project = "1.0.0", workspace = "1.0.0", platform_handoff = "1.0.0", institutional_governance = "1.0.0"),
    counts = connected_platform_summary(platform),
    registries = list(models = names(platform$registries$models), indicators = names(platform$registries$indicators), evidence = names(platform$registries$evidence)),
    boundaries = platform$boundary,
    generated_at = .utc_now()
  )
}

.connected_platform_fingerprint_record <- function(platform) {
  workspace_hashes <- if (length(platform$workspaces)) lapply(platform$workspaces, workspace_fingerprint) else list()
  project_hashes <- if (length(platform$projects)) lapply(platform$projects, project_fingerprint) else list()
  list(
    schema_version = platform$schema_version, id = platform$id, title = platform$title, institution = platform$institution,
    workspaces = workspace_hashes, projects = project_hashes, nodes = platform$nodes, edges = platform$edges,
    registries = platform$registries, decisions = platform$decisions, publications = platform$publications,
    governance = platform$governance, handoffs = platform$handoffs, workflows = platform$workflows, boundary = platform$boundary
  )
}

.connected_platform_raw_fingerprint <- function(platform) {
  .project_hash(.connected_platform_fingerprint_record(platform))
}

#' Fingerprint a connected platform
#'
#' @param platform Connected platform.
#' @return MD5 fingerprint.
#' @export
connected_platform_fingerprint <- function(platform) {
  validate_connected_platform(platform)
  current <- .connected_platform_raw_fingerprint(platform)
  restored <- platform[[".restored_connected_platform_fingerprint", exact = TRUE]]
  restored_state <- platform[[".restored_connected_platform_state_fingerprint", exact = TRUE]]
  if (!is.null(restored) && !is.null(restored_state) && identical(current, restored_state)) {
    return(restored)
  }
  current
}

.platform_restore_record <- function(record, restore_function, prefix) {
  path <- tempfile(prefix, fileext = ".json"); on.exit(unlink(path, force = TRUE), add = TRUE)
  jsonlite::write_json(record, path, auto_unbox = TRUE, pretty = FALSE, null = "null", na = "null", digits = NA, dataframe = "rows")
  restore_function(path)
}

.platform_restore_classes <- function(platform) {
  if (length(platform$workspaces)) platform$workspaces <- lapply(platform$workspaces, function(x) if (inherits(x, "catalyst_workspace")) x else .platform_restore_record(x, workspace_from_json, "connected-workspace-"))
  if (length(platform$projects)) platform$projects <- lapply(platform$projects, function(x) if (inherits(x, "catalyst_project")) x else .platform_restore_record(x, project_from_json, "connected-project-"))
  platform$nodes <- lapply(platform$nodes, function(x) structure(x, class = c("catalyst_platform_node", "list")))
  platform$edges <- lapply(platform$edges, function(x) structure(x, class = c("catalyst_platform_edge", "list")))
  structure(platform, class = c("catalyst_connected_platform", "list"))
}

#' Write a connected platform to JSON
#'
#' @param platform Connected platform.
#' @param path Output path.
#' @param pretty Pretty-print JSON.
#' @return Normalized output path invisibly.
#' @export
connected_platform_to_json <- function(platform, path, pretty = TRUE) {
  validate_connected_platform(platform); .assert_flag(pretty, "pretty")
  record <- unclass(platform)
  record[[".restored_connected_platform_fingerprint"]] <- NULL
  record[[".restored_connected_platform_state_fingerprint"]] <- NULL
  record$metadata$serialized_platform_fingerprint <- connected_platform_fingerprint(platform)
  jsonlite::write_json(.safe_json_value(record), path, auto_unbox = TRUE, pretty = pretty, null = "null", na = "null", digits = NA, dataframe = "rows")
  invisible(normalizePath(path, mustWork = FALSE))
}

#' Read a connected platform from JSON
#'
#' @param path Input path.
#' @return A `catalyst_connected_platform`.
#' @export
connected_platform_from_json <- function(path) {
  record <- jsonlite::read_json(path, simplifyVector = FALSE)
  serialized_fingerprint <- record$metadata$serialized_platform_fingerprint
  record$metadata$serialized_platform_fingerprint <- NULL
  result <- .platform_restore_classes(record)
  validate_connected_platform(result)
  if (is.character(serialized_fingerprint) && length(serialized_fingerprint) == 1L && grepl("^[0-9a-f]{32}$", serialized_fingerprint)) {
    result[[".restored_connected_platform_fingerprint"]] <- serialized_fingerprint
    result[[".restored_connected_platform_state_fingerprint"]] <- .connected_platform_raw_fingerprint(result)
  }
  result
}

.platform_index_rows <- function(records, type) {
  if (!length(records)) return(data.frame(id = character(), type = character(), title = character(), status = character(), stringsAsFactors = FALSE))
  rows <- lapply(records, function(record) data.frame(id = as.character(record$id), type = type, title = if (is.null(record$title)) "" else as.character(record$title), status = if (!is.null(record$review_status)) as.character(record$review_status) else if (!is.null(record$status)) as.character(record$status) else "", stringsAsFactors = FALSE))
  do.call(rbind, rows)
}

#' Export a connected platform publication bundle
#'
#' @param platform Connected platform.
#' @param dir Output directory.
#' @param prefix Bundle directory prefix.
#' @param zip_bundle Create a ZIP bundle.
#' @return Paths to generated artifacts.
#' @export
export_connected_platform <- function(platform, dir, prefix = "connected-sustainability-platform", zip_bundle = TRUE) {
  validate_connected_platform(platform); .assert_single_string(dir, "dir"); .assert_single_string(prefix, "prefix"); .assert_flag(zip_bundle, "zip_bundle")
  dir.create(dir, recursive = TRUE, showWarnings = FALSE); bundle_dir <- file.path(dir, prefix); dir.create(bundle_dir, recursive = TRUE, showWarnings = FALSE)
  paths <- list(
    platform = file.path(bundle_dir, "connected-platform.json"), manifest_record = file.path(bundle_dir, "platform-manifest.json"),
    nodes = file.path(bundle_dir, "node-index.csv"), edges = file.path(bundle_dir, "edge-index.csv"), evidence = file.path(bundle_dir, "evidence-index.csv"),
    decisions = file.path(bundle_dir, "decision-index.csv"), publications = file.path(bundle_dir, "publication-index.csv"), workflows = file.path(bundle_dir, "workflow-index.csv"),
    readme = file.path(bundle_dir, "README.md"), integrity = file.path(bundle_dir, "manifest.json")
  )
  connected_platform_to_json(platform, paths$platform)
  jsonlite::write_json(connected_platform_manifest(platform), paths$manifest_record, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", dataframe = "rows")
  node_rows <- if (length(platform$nodes)) do.call(rbind, lapply(platform$nodes, function(x) data.frame(id=x$id,node_type=x$node_type,title=x$title,review_status=x$review_status,stringsAsFactors=FALSE))) else data.frame(id=character(),node_type=character(),title=character(),review_status=character())
  edge_rows <- if (length(platform$edges)) do.call(rbind, lapply(platform$edges, function(x) data.frame(id=x$id,from_id=x$from_id,to_id=x$to_id,relation=x$relation,review_status=x$review_status,stringsAsFactors=FALSE))) else data.frame(id=character(),from_id=character(),to_id=character(),relation=character(),review_status=character())
  utils::write.csv(node_rows, paths$nodes, row.names = FALSE); utils::write.csv(edge_rows, paths$edges, row.names = FALSE)
  utils::write.csv(.platform_index_rows(platform$registries$evidence, "evidence"), paths$evidence, row.names = FALSE)
  utils::write.csv(.platform_index_rows(platform$decisions, "decision"), paths$decisions, row.names = FALSE)
  utils::write.csv(.platform_index_rows(platform$publications, "publication"), paths$publications, row.names = FALSE)
  utils::write.csv(.platform_index_rows(platform$workflows, "workflow"), paths$workflows, row.names = FALSE)
  summary <- connected_platform_summary(platform)
  writeLines(c(
    paste0("# ", platform$title), "", "Connected Sustainability Analytics and Decision Platform export.", "",
    paste0("- Platform ID: `", platform$id, "`"), paste0("- Workspaces: ", summary$workspaces), paste0("- Projects: ", summary$projects),
    paste0("- Graph nodes: ", summary$nodes), paste0("- Graph edges: ", summary$edges), paste0("- Evidence records: ", summary$evidence_records),
    paste0("- Decisions: ", summary$decisions), paste0("- Publications: ", summary$publications), "",
    "## Boundaries", "", "This bundle preserves analytical lineage and governance records. It does not authorize decisions, publish artifacts, verify identity, or execute cross-product actions without host-platform controls and human review."
  ), paths$readme)
  included <- unlist(paths[names(paths) != "integrity"], use.names = FALSE)
  info <- file.info(included); hashes <- unname(tools::md5sum(included))
  files <- lapply(seq_along(included), function(i) list(file = basename(included[i]), bytes = unname(info$size[i]), md5 = hashes[i]))
  manifest <- list(schema_version = .catalyst_connected_platform_export_schema_version(), export_type = "connected_sustainability_platform_bundle", platform_id = platform$id, platform_fingerprint = connected_platform_fingerprint(platform), package = list(name = "catalystanalyticsr", version = .catalyst_package_version()), created_at = .utc_now(), file_count = length(files), files = files, integrity = list(hash_algorithm = "md5", complete = TRUE, scope = "all_bundle_files_except_manifest"), boundary = platform$boundary)
  jsonlite::write_json(manifest, paths$integrity, auto_unbox = TRUE, pretty = TRUE, null = "null", na = "null", dataframe = "rows")
  if (zip_bundle) { paths$zip <- file.path(dir, paste0(prefix, ".zip")); old <- getwd(); on.exit(setwd(old), add = TRUE); setwd(dir); utils::zip(zipfile = basename(paths$zip), files = prefix) }
  class(paths) <- c("catalyst_connected_platform_export", "list"); paths
}

.connected_api_endpoints <- function() {
  list(
    manifest = list(id="platform.manifest",method="POST",path="/v2/platform/manifest",title="Connected platform manifest"),
    validate = list(id="platform.validate",method="POST",path="/v2/platform/validate",title="Validate connected platform"),
    lineage = list(id="platform.lineage",method="POST",path="/v2/platform/lineage",title="Trace analytical lineage"),
    summary = list(id="platform.summary",method="POST",path="/v2/platform/summary",title="Summarize connected platform"),
    registry = list(id="platform.registries",method="POST",path="/v2/platform/registries",title="Inspect federated registries")
  )
}

#' Connected public API manifest
#'
#' @return A versioned API v2 manifest retaining the v1 API contract.
#' @export
catalyst_connected_api_manifest <- function() {
  list(schema_version = .catalyst_connected_api_schema_version(), api_version = "v2", base_path = "/v2", package = list(name="catalystanalyticsr",version=.catalyst_package_version()), endpoints=.connected_api_endpoints(), compatibility=list(public_api_v1=catalyst_public_api_manifest()), boundary=list(transport_server_not_included=TRUE,authentication_by_host=TRUE,durable_mutation_by_host=TRUE,human_review_required=TRUE,automated_decision_authorization=FALSE))
}

#' Create a connected API request
#'
#' @param endpoint Connected endpoint identifier.
#' @param payload Request payload.
#' @param request_id Optional request identifier.
#' @param context Request context.
#' @return Connected API request.
#' @export
connected_api_request <- function(endpoint, payload = list(), request_id = NULL, context = list()) {
  .assert_single_string(endpoint, "endpoint")
  ids <- vapply(.connected_api_endpoints(), `[[`, character(1), "id"); if (!endpoint %in% ids) stop("Unknown connected API endpoint.", call. = FALSE)
  if (!is.list(payload) || !is.list(context)) stop("`payload` and `context` must be lists.", call. = FALSE)
  if (is.null(request_id)) request_id <- paste0("v2-req-", substr(.project_hash(list(endpoint=endpoint,payload=payload,at=.utc_now())),1L,16L))
  .project_id(request_id, "request_id")
  list(schema_version="2.0.0",request_type="catalyst_connected_api_request",request_id=request_id,endpoint=endpoint,payload=payload,context=context,submitted_at=.utc_now())
}

#' Dispatch a connected API request
#'
#' @param request Connected API request.
#' @param platform Optional platform when not included in the payload.
#' @param stop_on_error Throw errors instead of returning an error response.
#' @return Connected API response envelope.
#' @export
dispatch_connected_api_request <- function(request, platform = NULL, stop_on_error = FALSE) {
  if (!is.list(request) || !identical(request$schema_version, "2.0.0") || !identical(request$request_type, "catalyst_connected_api_request")) stop("Unsupported connected API request.", call. = FALSE)
  .assert_flag(stop_on_error, "stop_on_error")
  target <- if (!is.null(request$payload$platform)) .platform_restore_classes(request$payload$platform) else platform
  execute <- function() {
    validate_connected_platform(target)
    switch(request$endpoint,
      platform.manifest = connected_platform_manifest(target),
      platform.validate = list(valid=TRUE,platform_id=target$id,fingerprint=connected_platform_fingerprint(target)),
      platform.lineage = platform_lineage(target, request$payload$node_id, direction = if (is.null(request$payload$direction)) "both" else request$payload$direction, max_depth = if (is.null(request$payload$max_depth)) 20L else request$payload$max_depth),
      platform.summary = connected_platform_summary(target),
      platform.registries = target$registries,
      stop("Unsupported connected API endpoint.", call. = FALSE)
    )
  }
  value <- tryCatch(execute(), error=function(error) error)
  if (inherits(value,"error")) {
    if (stop_on_error) stop(conditionMessage(value), call. = FALSE)
    return(list(schema_version="2.0.0",response_type="catalyst_connected_api_response",request_id=request$request_id,endpoint=request$endpoint,status="error",data=list(),errors=conditionMessage(value),completed_at=.utc_now(),boundary=list(human_review_required=TRUE,automated_decision_authorization=FALSE)))
  }
  list(schema_version="2.0.0",response_type="catalyst_connected_api_response",request_id=request$request_id,endpoint=request$endpoint,status="ok",data=.safe_json_value(value),errors=character(),completed_at=.utc_now(),boundary=list(human_review_required=TRUE,automated_decision_authorization=FALSE))
}

#' @export
print.catalyst_connected_platform <- function(x, ...) {
  summary <- connected_platform_summary(x)
  cat("Connected Sustainability Analytics and Decision Platform", x$id, "\n")
  cat(" Workspaces:", summary$workspaces, " Projects:", summary$projects, " Nodes:", summary$nodes, " Edges:", summary$edges, "\n")
  cat(" Evidence:", summary$evidence_records, " Decisions:", summary$decisions, " Publications:", summary$publications, "\n")
  invisible(x)
}
