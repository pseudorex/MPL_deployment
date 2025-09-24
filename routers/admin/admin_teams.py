from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
import models
from database import SessionLocal

router = APIRouter(prefix="/admin/teams", tags=["Admin - Teams"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class TeamRequest(BaseModel):
    team_name: str
    points: Optional[int] = 100

class UpdateTeamRequest(BaseModel):
    team_name: Optional[str] = None
    points: Optional[int] = None

@router.get("/")
def get_teams(db: db_dependency):
    return db.query(models.Team).all()

@router.get("/{team_name}")
def get_team_by_teamname(team_name: str, db: db_dependency):
    team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
    return team

@router.put("/{team_name}")
def update_team(team_name: str, request: UpdateTeamRequest, db: db_dependency):
    team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(team, key, value)

    db.commit()
    db.refresh(team)
    return team

@router.delete("/{team_name}")
def delete_team(db: db_dependency, team_name: str):
    team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
    team_question = db.query(models.TeamQuestion).filter(models.TeamQuestion.team_id == team.id).first()

    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(team_question)
    db.delete(team)
    db.commit()
    return {"detail": "Team deleted successfully"}
