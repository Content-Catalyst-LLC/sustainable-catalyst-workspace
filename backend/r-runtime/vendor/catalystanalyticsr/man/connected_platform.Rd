\name{connected_platform}
\alias{platform_node}
\alias{platform_edge}
\alias{platform_evidence_record}
\alias{platform_decision_record}
\alias{platform_publication_record}
\alias{connected_workflow}
\alias{connected_sustainability_platform}
\alias{validate_connected_platform}
\alias{platform_add_node}
\alias{platform_add_edge}
\alias{platform_add_project}
\alias{platform_add_workspace}
\alias{platform_register_records}
\alias{platform_add_decision}
\alias{platform_add_publication}
\alias{platform_add_governance}
\alias{platform_add_handoff}
\alias{platform_add_workflow}
\alias{platform_lineage}
\alias{connected_platform_summary}
\alias{connected_platform_manifest}
\alias{connected_platform_fingerprint}
\alias{connected_platform_to_json}
\alias{connected_platform_from_json}
\alias{catalyst_connected_api_manifest}
\alias{connected_api_request}
\alias{dispatch_connected_api_request}
\alias{print.catalyst_connected_platform}
\title{Connected sustainability analytics and decision platform}
\usage{
platform_node(node_id, node_type = c("workspace", "project", "scenario", "dataset", "model", "indicator", "evidence", "decision", "governance", "publication", "handoff", "workflow", "external_source"), title, reference = list(), provenance = list(), review_status = c("unreviewed", "in_review", "approved", "rejected", "archived"), metadata = list())

platform_edge(edge_id, from_id, to_id, relation, evidence_ids = character(), provenance = list(), review_status = c("unreviewed", "in_review", "approved", "rejected", "archived"), metadata = list())

platform_evidence_record(evidence_id, title, source_type, source_ref, claims = character(), quality_status = c("unassessed", "provisional", "reviewed", "verified", "disputed"), metadata = list())

platform_decision_record(decision_id, title, alternatives, evidence_ids = character(), selected_alternative = NULL, governance_status = c("draft", "in_review", "approved", "rejected", "archived"), metadata = list())

platform_publication_record(publication_id, title, artifact_refs = list(), evidence_ids = character(), review_status = c("unreviewed", "in_review", "approved", "rejected"), publication_status = c("draft", "approved", "published", "withdrawn", "archived"), metadata = list())

connected_workflow(workflow_id, title, stages, owner = "", input_node_ids = character(), output_node_ids = character(), status = c("draft", "active", "blocked", "completed", "archived"), human_review_required = TRUE, metadata = list())

connected_sustainability_platform(platform_id, title, institution_id, institution_name, metadata = list())

validate_connected_platform(platform)

platform_add_node(platform, node)

platform_add_edge(platform, edge)

platform_add_project(platform, project)

platform_add_workspace(platform, workspace)

platform_register_records(platform, registry = c("models", "indicators", "evidence"), records, replace = FALSE)

platform_add_decision(platform, decision)

platform_add_publication(platform, publication)

platform_add_governance(platform, governance)

platform_add_handoff(platform, handoff)

platform_add_workflow(platform, workflow)

platform_lineage(platform, node_id, direction = c("upstream", "downstream", "both"), max_depth = 20L)

connected_platform_summary(platform)

connected_platform_manifest(platform)

connected_platform_fingerprint(platform)

connected_platform_to_json(platform, path, pretty = TRUE)

connected_platform_from_json(path)

catalyst_connected_api_manifest()

connected_api_request(endpoint, payload = list(), request_id = NULL, context = list())

dispatch_connected_api_request(request, platform = NULL, stop_on_error = FALSE)

\method{print}{catalyst_connected_platform}(x, ...)
}
\arguments{
  \item{node_id}{Stable graph node identifier.}
  \item{node_type}{Graph node type.}
  \item{title}{Human-readable title.}
  \item{reference}{Contract and source reference.}
  \item{provenance}{Provenance record.}
  \item{review_status}{Review state.}
  \item{metadata}{Additional metadata.}
  \item{edge_id}{Stable graph edge identifier.}
  \item{from_id}{Origin node identifier.}
  \item{to_id}{Destination node identifier.}
  \item{relation}{Directed relationship type.}
  \item{evidence_ids}{Supporting evidence identifiers.}
  \item{evidence_id}{Stable evidence identifier.}
  \item{source_type}{Evidence source type.}
  \item{source_ref}{Evidence source reference.}
  \item{claims}{Claim identifiers or summaries.}
  \item{quality_status}{Evidence quality state.}
  \item{decision_id}{Stable decision identifier.}
  \item{alternatives}{Declared decision alternatives.}
  \item{selected_alternative}{Optional selected alternative.}
  \item{governance_status}{Decision governance state.}
  \item{publication_id}{Stable publication identifier.}
  \item{artifact_refs}{Named artifact references.}
  \item{publication_status}{Publication state.}
  \item{workflow_id}{Stable workflow identifier.}
  \item{stages}{Ordered workflow stages.}
  \item{owner}{Workflow owner.}
  \item{input_node_ids}{Input graph nodes.}
  \item{output_node_ids}{Output graph nodes.}
  \item{status}{Workflow status.}
  \item{human_review_required}{Whether human review is required.}
  \item{platform_id}{Stable connected-platform identifier.}
  \item{institution_id}{Institution identifier.}
  \item{institution_name}{Institution name.}
  \item{platform}{Connected platform record.}
  \item{node}{Platform node record.}
  \item{edge}{Platform edge record.}
  \item{project}{Reproducible analytical project.}
  \item{workspace}{Persistent analytical workspace.}
  \item{registry}{Registry name.}
  \item{records}{Named records to register.}
  \item{replace}{Whether existing identifiers may be replaced.}
  \item{decision}{Connected decision record.}
  \item{publication}{Connected publication record.}
  \item{governance}{Institutional governance record.}
  \item{handoff}{First-party platform handoff.}
  \item{workflow}{Connected workflow record.}
  \item{direction}{Lineage traversal direction.}
  \item{max_depth}{Maximum lineage traversal depth.}
  \item{path}{JSON file path.}
  \item{pretty}{Pretty-print JSON.}
  \item{endpoint}{Connected API endpoint identifier.}
  \item{payload}{Request payload.}
  \item{request_id}{Optional request identifier.}
  \item{context}{Request context.}
  \item{request}{Connected API request.}
  \item{stop_on_error}{Throw dispatch errors instead of returning an error response.}
  \item{x}{Connected platform object.}
  \item{...}{Additional print arguments.}
}
\description{Creates and manages a governed analytical graph connecting workspaces, projects, evidence, decisions, publications, governance, handoffs, workflows, and federated registries.}
\value{A connected-platform record, graph record, manifest, lineage record, API envelope, or updated platform depending on the function.}
\details{The connected platform preserves lineage and review boundaries. It does not provide an HTTP server, durable identity service, autonomous publication, or automated decision authorization.}
