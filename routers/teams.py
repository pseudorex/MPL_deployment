from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models
from pydantic import BaseModel

router = APIRouter(prefix="/teamquestions", tags=["TeamQuestion"])

# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Depends(get_db)


class TeamQuestionRequest(BaseModel):
    teamname: str
    question_code: str   # should match Question.question_code


@router.post("/")
def create_team_and_assign_question(request: TeamQuestionRequest, db: Session = db_dependency):
    # Check if team already exists
    team = db.query(models.Team).filter(models.Team.team_name == request.teamname).first()
    if team:
        raise HTTPException(status_code=400, detail="The team is already allocated with a question!")

    # 2. If not exists → create new team with default points = 100
    if not team:
        team = models.Team(team_name=request.teamname, points=100)
        db.add(team)
        db.commit()
        db.refresh(team)

    # Find the question in NORMAL question table by question_code
    question = db.query(models.Question).filter(
        models.Question.id == request.question_code
    ).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")


    existing_mapping = db.query(models.TeamQuestion).filter(
        models.TeamQuestion.team_id == team.id,
        models.TeamQuestion.question_id == question.id
    ).first()

    existing_mapping_question = db.query(models.TeamQuestion).filter(
        models.TeamQuestion.question_id == question.id
    ).first()

    if existing_mapping_question:
        raise HTTPException(status_code=400, detail="This question is alloted already")

    if existing_mapping:
        raise HTTPException(status_code=400, detail="This team already has this question")

    # 5. Create the mapping (no points stored here)
    mapping = models.TeamQuestion(
        team_id=team.id,
        question_id=question.id,
    )


    db.add(mapping)
    db.commit()
    db.refresh(mapping)

    return {
        "message": "Team created & question assigned successfully",
        "question": question.question,
        "teamname": team.team_name,
        "points": team.points,   # ✅ points from Team table
    }
