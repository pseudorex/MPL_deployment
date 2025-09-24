from database import Base
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
import enum
from datetime import datetime, timedelta
import pytz

IST = pytz.timezone("Asia/Kolkata")

def default_start_time():
    return datetime.now(IST) + timedelta(minutes=30)

# Define ENUM for question_status
class QuestionStatusEnum(str, enum.Enum):
    ALLOCATED = "ALLOCATED"
    UNALLOCATED = "UNALLOCATED"

class Question(Base):
    __tablename__ = "question"

    id = Column(String(255), primary_key=True)
    question = Column(String(255), nullable=True)


class MysteryQuestion(Base):
    __tablename__ = "mystery_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    difficulty = Column(String(255), nullable=True)
    question = Column(String(255), nullable=True)
    question_status = Column(Enum(QuestionStatusEnum), nullable=True)


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_name = Column(String(255), nullable=False)
    points = Column(Integer, nullable=True, default=100)
    mystery_question = Column(Integer, unique=True, nullable=True)
    start_time = Column(DateTime, nullable=True, default=default_start_time)



class TeamQuestion(Base):
    __tablename__ = "team_question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(String(255), unique=True, nullable=True)
    team_id = Column(Integer, unique=True, nullable=True)
