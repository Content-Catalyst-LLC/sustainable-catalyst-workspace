import os

from app.main import app
from app.research_reporting import router as reporting_router

if os.getenv("SC_WORKSPACE_REPORTING_STUDIO_ENABLED") == "1":
    app.include_router(reporting_router)
