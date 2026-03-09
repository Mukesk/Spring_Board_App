from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import random

from app.db.database import get_db
from app.models.quiz import Question, QuizAttempt, UserAnswer
from app.schemas.quiz import (
    QuizStartResponse, QuestionOut, QuizSubmitRequest,
    QuizSubmitResponse, ScorecardResponse, EvaluatedAnswer
)

router = APIRouter(prefix="/quiz", tags=["Quiz"])

@router.get("/start", response_model=QuizStartResponse)
def start_quiz(
    difficulty: Optional[str] = Query(None, description="Optional difficulty filter (easy, medium, hard)"),
    db: Session = Depends(get_db)
):
    query = db.query(Question)
    if difficulty:
         query = query.filter(Question.difficulty == difficulty.lower())

    questions_db = query.all()

    if not questions_db:
         raise HTTPException(status_code=404, detail="No questions found in database.")

    # Select random 10 (or less if not enough in DB)
    sample_size = min(10, len(questions_db))
    random_questions = random.sample(questions_db, sample_size)

    # Format output
    questions_out = []
    for q in random_questions:
         questions_out.append(QuestionOut(
             id=q.id,
             question=q.question,
             options=[q.option_a, q.option_b, q.option_c, q.option_d]
         ))

    # Create a new quiz attempt record
    new_attempt = QuizAttempt(
         user_id=1, # Mock user id
         total_questions=len(questions_out)
    )
    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return QuizStartResponse(quiz_id=new_attempt.id, questions=questions_out)


@router.post("/submit", response_model=QuizSubmitResponse)
def submit_quiz(submit_data: QuizSubmitRequest, db: Session = Depends(get_db)):
    # 1. Fetch Quiz Attempt
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == submit_data.quiz_id).first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Quiz not found")

    score = 0

    # 2. Evaluate answers
    for ans in submit_data.answers:
        question = db.query(Question).filter(Question.id == ans.question_id).first()
        if not question:
             continue # Skip invalid question IDs

        is_correct = ans.selected == question.correct_answer
        if is_correct:
             score += 1
        
        # Save user answer
        user_answer = UserAnswer(
             quiz_id=attempt.id,
             question_id=ans.question_id,
             selected_answer=ans.selected,
             correct=is_correct
        )
        db.add(user_answer)

    # 3. Update Attempt Score
    attempt.score = score
    db.commit()

    return QuizSubmitResponse(score=score, total=attempt.total_questions)

@router.get("/result/{quiz_id}", response_model=ScorecardResponse)
def get_scorecard(quiz_id: int, db: Session = Depends(get_db)):
    attempt = db.query(QuizAttempt).filter(QuizAttempt.id == quiz_id).first()
    if not attempt:
         raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Fetch user answers with related questions
    user_answers = db.query(UserAnswer).filter(UserAnswer.quiz_id == quiz_id).all()
    
    evaluated_answers = []
    for ua in user_answers:
         question = db.query(Question).filter(Question.id == ua.question_id).first()
         if question:
              explanation = f"The correct answer is {question.correct_answer}." # Simple explanation
              
              evaluated_answers.append(EvaluatedAnswer(
                   question=question.question,
                   correct_answer=question.correct_answer,
                   your_answer=ua.selected_answer,
                   explanation=explanation,
                   is_correct=ua.correct
              ))
              
    return ScorecardResponse(
         score=attempt.score,
         total=attempt.total_questions,
         answers=evaluated_answers
    )
