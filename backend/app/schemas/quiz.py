from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# --- Pydantic DTOs ---

class CourseBase(BaseModel):
    course_name: str

class CourseCreate(CourseBase):
    pass

class CourseOut(CourseBase):
    id: int
    created_at: datetime
    
    model_config = {"from_attributes": True}

class QuestionBase(BaseModel):
    course_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    difficulty: str

class QuestionCreate(QuestionBase):
    pass

class QuestionOut(BaseModel):
    id: int
    question: str
    options: List[str]

    # Custom init from SQLAlchemy model to format options array
    model_config = {"from_attributes": True}

class QuizStartResponse(BaseModel):
    quiz_id: int
    questions: List[QuestionOut]


# Submit input
class SubmittedAnswer(BaseModel):
    question_id: int
    selected: str

class QuizSubmitRequest(BaseModel):
    quiz_id: int
    course_id: int
    user_id: int = 1 # Mock user for POC
    answers: List[SubmittedAnswer]

class QuizSubmitResponse(BaseModel):
    score: int
    total: int

# Scorecard output
class EvaluatedAnswer(BaseModel):
    question: str
    correct_answer: str
    your_answer: str
    explanation: str
    is_correct: bool

class ScorecardResponse(BaseModel):
    score: int
    total: int
    answers: List[EvaluatedAnswer]

# AI Gen
class GenerateQuestionRequest(BaseModel):
    course_id: int
    course_name: str
    easy: int
    medium: int
    hard: int

class GeneratedQuestionResponse(BaseModel):
    question: str
    options: List[str]
    answer: str
