from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
import models
from database import SessionLocal

router = APIRouter(prefix="/admin/teams_question", tags=["Admin - TeamsQuestion"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@router.delete("/{primary_id}")
def delete_team(db: db_dependency, primary_id: str):
    teamQuestion = db.query(models.TeamQuestion).filter(models.TeamQuestion.id == primary_id).first()

    if not teamQuestion:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(teamQuestion)
    db.commit()
    return {"detail": "The mapped question is deleted successfully"}
