from __future__ import annotations

RENDERER_VERSION = "3.82.1"

def renderer_profile() -> dict:
    return {
        "schema": "sc-shared-research-graph-renderer-profile/1.0",
        "version": RENDERER_VERSION,
        "renderer": "shared-research-graph-visual-interaction-engine",
        "layouts": ["force", "cluster", "timeline", "provenance"],
        "forceDirected": True,
        "semanticClustering": True,
        "dragAndPin": True,
        "pan": True,
        "wheelZoom": True,
        "minimap": True,
        "curvedDirectedEdges": True,
        "edgeLabelsOnDemand": True,
        "degreeScaledNodes": True,
        "collisionAvoidance": True,
        "dynamicLabels": True,
        "hoverNeighborhoodHighlighting": True,
        "clickToFocus": True,
        "directRelationshipTrace": True,
        "connectedSubgraphFocus": True,
        "clusterCollapse": True,
        "fullscreen": True,
        "searchToNode": True,
        "lensTransitions": True,
        "timelineLayout": True,
        "provenanceLayout": True,
        "geographicLayoutHook": True,
        "inspectorSynchronization": True,
        "dataAuthoritySeparatedFromRenderer": True,
        "databaseMigrationRequired": False,
        "automaticTruthDetermination": False,
        "automaticEvidenceRanking": False,
    }
