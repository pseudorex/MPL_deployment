from fastapi import FastAPI
from database import engine
import models
from routers import teams, mystery, websocket
from routers.admin import admin_teams, admin_question, admin_mystery

# admin)

app = FastAPI(
    root_path="/siamMPL",
    openapi_tags=[{"name": "MPL", "description": "MPL related operations"}]
)

models.Base.metadata.create_all(bind=engine)

app.include_router(teams.router)
app.include_router(mystery.router)
app.include_router(websocket.router)

app.include_router(admin_teams.router)
app.include_router(admin_question.router)
app.include_router(admin_mystery.router)