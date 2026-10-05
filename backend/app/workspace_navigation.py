from typing import Any
from sqlalchemy.orm import Session
from .repository import list_projects,list_notebooks
SCHEMA="sc-workspace-navigation-launcher/1.0"
def targets():
    return [
      {"id":"workspace","title":"Workspace","description":"Unified research project environment.","availability":"ready","url":"https://workspace.sustainablecatalyst.com/"},
      {"id":"library","title":"Knowledge Library","description":"Structured publications, sources and research pathways.","availability":"ready","url":"https://sustainablecatalyst.com/knowledge-libraries/"},
      {"id":"research-librarian","title":"Research Librarian","description":"Research guidance and source discovery.","availability":"registered","url":""},
      {"id":"workbench","title":"Workbench","description":"Computational research and scientific calculation.","availability":"registered","url":""},
      {"id":"lab","title":"Research Lab","description":"Scientific experimentation and reproducibility.","availability":"registered","url":""},
      {"id":"decision-studio","title":"Decision Studio","description":"Decision packets, scenarios and judgment workflows.","availability":"registered","url":""},
      {"id":"site-intelligence","title":"Site Intelligence","description":"Geospatial and earth-observation intelligence.","availability":"registered","url":""},
    ]
def profile()->dict[str,Any]:
    return {"schema":SCHEMA,"version":"3.73.0","globalNavigation":True,"commandPalette":True,
      "researchLauncher":True,"projectContextAware":True,"keyboardShortcut":"Mod+K",
      "automaticNavigationToUnavailableTargets":False,"wordpressRequired":False,
      "databaseMigrationRequired":False,"targets":targets()}
def recent(db:Session,user_key:str,limit:int=8)->dict[str,Any]:
    ps=list_projects(db,user_key); ns=list_notebooks(db,user_key)
    ps=sorted(ps,key=lambda x:str(x.get("updatedAt") or x.get("clientUpdatedAt") or ""),reverse=True)[:limit]
    return {"schema":"sc-workspace-navigation-recent/1.0","version":"3.73.0","userKey":user_key,
      "projects":ps,"notebooks":ns[:limit]}
