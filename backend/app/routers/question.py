from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.quiz import Question, Course
from app.schemas.quiz import QuestionCreate, QuestionOut

router = APIRouter(prefix="/questions", tags=["Question Bank"])

@router.post("", response_model=QuestionOut)
def create_question(question: QuestionCreate, db: Session = Depends(get_db)):
    # Check if course exists
    course = db.query(Course).filter(Course.id == question.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    new_question = Question(
        course_id=question.course_id,
        question=question.question,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=question.correct_answer,
        difficulty=question.difficulty.lower()
    )
    
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    # We construct options dynamically for the Output schema
    options = [new_question.option_a, new_question.option_b, new_question.option_c, new_question.option_d]
    return QuestionOut(id=new_question.id, question=new_question.question, options=options)

@router.get("/{course_id}", response_model=List[QuestionOut])
def list_questions_for_course(course_id: int, db: Session = Depends(get_db)):
    questions = db.query(Question).filter(Question.course_id == course_id).all()
    out = []
    for q in questions:
        out.append(QuestionOut(
            id=q.id,
            question=q.question,
            options=[q.option_a, q.option_b, q.option_c, q.option_d]
        ))
    return out
