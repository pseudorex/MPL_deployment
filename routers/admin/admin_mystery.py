from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
import models
from database import SessionLocal

router = APIRouter(prefix="/admin/mystery-questions", tags=["Admin - MysteryQuestions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class MysteryQuestionRequest(BaseModel):
    difficulty: Optional[str] = None
    question: Optional[str] = None
    question_status: Optional[models.QuestionStatusEnum] = models.QuestionStatusEnum.UNALLOCATED

class UpdateMysteryQuestionRequest(BaseModel):
    difficulty: Optional[str] = None
    question: Optional[str] = None
    question_status: Optional[models.QuestionStatusEnum] = None

@router.post("/")
def create_mystery_question(request: MysteryQuestionRequest, db: db_dependency):
    q = models.MysteryQuestion(**request.model_dump())
    db.add(q)
    db.commit()
    db.refresh(q)
    return q

@router.get("/")
def get_mystery_questions(db: db_dependency):
    return db.query(models.MysteryQuestion).all()

@router.put("/{mq_id}")
def update_mystery_question(mq_id: int, request: UpdateMysteryQuestionRequest, db: db_dependency):
    q = db.query(models.MysteryQuestion).filter(models.MysteryQuestion.id == mq_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Mystery question not found")

    for key, value in request.model_dump(exclude_unset=True).items():
        setattr(q, key, value)

    db.commit()
    db.refresh(q)
    return q

@router.delete("/{mq_id}")
def delete_mystery_question(mq_id: int, db: db_dependency):
    q = db.query(models.MysteryQuestion).filter(models.MysteryQuestion.id == mq_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Mystery question not found")

    db.delete(q)
    db.commit()
    return {"detail": "Mystery question deleted successfully"}
