from fastapi import FastAPI
from database import engine
import models
from routers import teams, mystery, websocket
from routers.admin import admin_teams, admin_question, admin_mystery
import os
import uvicorn   # ✅ Added to start the server

# Create FastAPI app
app = FastAPI(
    root_path="/siamMPL",
    openapi_tags=[{"name": "MPL", "description": "MPL related operations"}]
)

# Create database tables (if they don't exist)
models.Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(teams.router)
app.include_router(mystery.router)
app.include_router(websocket.router)

app.include_router(admin_teams.router)
app.include_router(admin_question.router)
app.include_router(admin_mystery.router)

# ✅ Added entry point for Render/Local development
if __name__ == "__main__":
    # Render provides a PORT environment variable. Default to 8000 for local use.
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
