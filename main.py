from fastapi import FastAPI
from database import engine
import models
from routers import teams, mystery, websocket
from routers.admin import admin_teams, admin_question, admin_mystery
import os
import uvicorn
from dotenv import load_dotenv

# Load local .env for testing
load_dotenv()

app = FastAPI(
    root_path="/siamMPL",
    openapi_tags=[{"name": "MPL", "description": "MPL related operations"}]
)

# Create tables
models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(teams.router)
app.include_router(mystery.router)
app.include_router(websocket.router)
app.include_router(admin_teams.router)
app.include_router(admin_question.router)
app.include_router(admin_mystery.router)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Render uses $PORT
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
