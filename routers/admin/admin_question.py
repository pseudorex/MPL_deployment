from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from pydantic import BaseModel
import models
from database import SessionLocal

router = APIRouter(prefix="/admin/questions", tags=["Admin - Questions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

class QuestionRequest(BaseModel):
    id: str
    question: Optional[str] = None

@router.post("/")
def create_question(request: QuestionRequest, db: db_dependency):
    existing = db.query(models.Question).filter(models.Question.id == request.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Question ID already exists.")

    question = models.Question(**request.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@router.get("/")
def get_questions(db: db_dependency):
    return db.query(models.Question).all()
