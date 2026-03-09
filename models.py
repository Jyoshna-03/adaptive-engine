from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class QuestionOut(BaseModel):
    question_id: str
    text: str
    options: List[str]
    topic: str
    difficulty: float

class QuestionInDB(BaseModel):
    text: str
    difficulty: float = Field(..., ge=0.1, le=1.0)
    discrimination: float = Field(default=1.0)
    topic: str
    tags: List[str]
    options: List[str]
    correct_answer: str

class SessionStart(BaseModel):
    student_name: Optional[str] = "Anonymous"

class SessionOut(BaseModel):
    session_id: str
    student_name: str
    ability_score: float
    questions_answered: int
    message: str

class AnswerSubmit(BaseModel):
    question_id: str
    selected_answer: str

class AnswerResult(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str
    new_ability_score: float
    questions_answered: int
    session_complete: bool

class WeakTopic(BaseModel):
    topic: str
    correct: int
    total: int
    accuracy: float

class StudyPlan(BaseModel):
    student_name: str
    final_ability_score: float
    total_questions: int
    accuracy_percent: float
    weak_topics: List[WeakTopic]
    study_plan: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)