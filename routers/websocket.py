from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import SessionLocal

router = APIRouter()

# --- DB Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# --- Connection Manager ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, team_name: str):
        await websocket.accept()
        self.active_connections.setdefault(team_name, []).append(websocket)

    def disconnect(self, team_name: str, websocket: WebSocket):
        if team_name in self.active_connections:
            if websocket in self.active_connections[team_name]:
                self.active_connections[team_name].remove(websocket)
            if not self.active_connections[team_name]:
                del self.active_connections[team_name]

    async def send_to_team(self, team_name: str, message: dict):
        for ws in list(self.active_connections.get(team_name, [])):
            try:
                await ws.send_json(message)
            except Exception:
                self.disconnect(team_name, ws)


manager = ConnectionManager()

# --- Listener (PC1) ---
@router.websocket("/ws/{team_name}")
async def websocket_listener(websocket: WebSocket, team_name: str):
    """PC1 connects here to listen for updates."""
    await manager.connect(websocket, team_name)
    try:
        while True:
            await websocket.receive_text()  # keep alive
    except WebSocketDisconnect:
        manager.disconnect(team_name, websocket)

# --- Time Update (PC2) ---
@router.websocket("/ws/time-update/{team_name}")
async def websocket_time_update(websocket: WebSocket, team_name: str, db: db_dependency):
    """
    PC2 sends {"event": "done", "extra_time": 60}
    → Extend team's end_time by bonus
    → Notify all listeners (PC1)
    """
    await manager.connect(websocket, team_name)
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("event") != "done":
                continue  # ignore unknown events

            # --- Get team ---
            team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
            if not team:
                await websocket.send_json({"event": "error", "detail": "Team not found"})
                continue

            if team.mystery_question is None:
                await websocket.send_json({"event": "error", "detail": "No mystery question assigned"})
                continue

            # --- Time logic ---
            now = datetime.now(timezone.utc)
            end_time = team.start_time

            # If already expired, reset from now
            # if end_time < now:
            #     raise HTTPException(status_code=400, detail="The time is already ended!")

            bonus_seconds = int(data.get("extra_time", 60))
            new_end_time = end_time + timedelta(seconds=bonus_seconds)

            # --- Save to DB ---
            team.start_time = new_end_time
            db.commit()

            # --- Notify clients ---
            remaining_seconds = max(int((new_end_time - now).total_seconds()), 0)
            await manager.send_to_team(team_name, {
                "event": "time_updated",
                "team": team_name,
                "new_end_time": new_end_time.isoformat(),
                "remaining_seconds": remaining_seconds
            })

    except WebSocketDisconnect:
        manager.disconnect(team_name, websocket)
