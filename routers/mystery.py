# routers/mystery.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal
import models
from routers.websocket import manager  # for sending points updates
from datetime import datetime

router = APIRouter(prefix="/mystery", tags=["Mystery"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class MysteryRequest(BaseModel):
    team_name: str
    difficulty: str
    cost: int   # how many points needed to take this mystery


# class QuitRequest(BaseModel):
#     team_name: str
#     question_id: int


@router.put("/", status_code=status.HTTP_200_OK)
async def assign_mystery_question(request: MysteryRequest, db: Session = Depends(get_db)):
    # Find team
    team = db.query(models.Team).filter(models.Team.team_name == request.team_name).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")


    # Check if team already has a mystery
    if team.mystery_question is not None:
        raise HTTPException(
            status_code=409,
            detail="This team already has an allocated mystery question."
        )

    # Ensure team has enough points
    if team.points < request.cost:
        raise HTTPException(
            status_code=400,
            detail="Not enough points to purchase this question."
        )

    #  Get an available mystery question of given difficulty
    mystery = (
        db.query(models.MysteryQuestion)
        .filter(models.MysteryQuestion.difficulty == request.difficulty)
        .filter(models.MysteryQuestion.question_status == models.QuestionStatusEnum.UNALLOCATED)
        .first()
    )

    if not mystery:
        raise HTTPException(status_code=404, detail="No available question for this difficulty")

    #  Allocate it
    mystery.question_status = models.QuestionStatusEnum.ALLOCATED
    team.mystery_question = mystery.id

    team.points -= request.cost

    db.commit()
    db.refresh(team)
    db.refresh(mystery)

    # Send points update to team via WebSocket
    await manager.send_to_team(team.team_name, {
        "event": "points_updated",
        "team": team.team_name,
        "new_points": team.points
    })

    return {
        "team_name": team.team_name,
        "remaining_points": team.points,
        "mystery_id": mystery.id,
        "difficulty": mystery.difficulty,
        "question": mystery.question
    }



# @router.delete("/quit", status_code=status.HTTP_200_OK)
# def quit_mystery(request: QuitRequest, db: Session = Depends(get_db)):
#     # 1. Find team
#     team = db.query(models.Team).filter(models.Team.team_name == request.team_name).first()
#     if not team:
#         raise HTTPException(status_code=404, detail="Team not found")
#
#     #  Check if the team actually has this mystery assigned
#     if team.mystery_question != request.question_id:
#         raise HTTPException(
#             status_code=400,
#             detail="This team is not assigned to this question."
#         )
#
#     #  Free the question
#     mystery = db.query(models.MysteryQuestion).filter(models.MysteryQuestion.id == request.question_id).first()
#     if not mystery:
#         raise HTTPException(status_code=404, detail="Mystery question not found")
#
#     mystery.question_status = models.QuestionStatusEnum.UNALLOCATED
#     team.mystery_question = None  # free it
#
#     db.commit()
#
#     return {"detail": f"Team {team.team_name} has quit mystery question {request.question_id}"}

@router.delete("/quit", status_code=status.HTTP_200_OK)
def quit_mystery(team_name: str, db: Session = Depends(get_db)):
    # 1. Find team
    team = db.query(models.Team).filter(models.Team.team_name == team_name).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    question_id = team.mystery_question

    #  Free the question
    mystery = db.query(models.MysteryQuestion).filter(models.MysteryQuestion.id == question_id).first()
    if not mystery:
        raise HTTPException(status_code=404, detail="Mystery question not found")

    mystery.question_status = models.QuestionStatusEnum.UNALLOCATED
    team.mystery_question = None  # free it

    db.commit()

    return {"detail": f"Team {team.team_name} has quit mystery question with question id {question_id}"}

