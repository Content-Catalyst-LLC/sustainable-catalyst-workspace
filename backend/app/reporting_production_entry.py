"""Production route entrypoint: existing Workspace + Reporting Studio, without dev docs."""
from app.reporting_integrated_entry import app

_DEV_DOC_PATHS = frozenset(("/docs", "/docs/oauth2-redirect"))
app.router.routes[:] = [
    route for route in app.router.routes
    if getattr(route, "path", None) not in _DEV_DOC_PATHS
]
