from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os
from dotenv import load_dotenv

from app.db.database import get_db
from app.models.quiz import Question, Course
from app.schemas.quiz import GenerateQuestionRequest, GeneratedQuestionResponse
from app.services.ai_agent import refresh_course_questions, refresh_all_courses, generate_questions_for_course

# Load env vars
load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Generation"])

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
         raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured. Please add it to your .env file.")
    return OpenAI(api_key=api_key)

@router.post("/fill-question-bank")
def fill_question_bank(req: GenerateQuestionRequest, db: Session = Depends(get_db)):
    """
    The admin can manually request AI to generate questions by specifying:
    - Course ID
    - Course name
    - Number of questions per difficulty level
    """
    # 1. Verify existence of course
    course = db.query(Course).filter(Course.id == req.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    try:
        easy_qs = generate_questions_for_course(req.course_name, "easy", req.easy) if req.easy > 0 else []
        medium_qs = generate_questions_for_course(req.course_name, "medium", req.medium) if req.medium > 0 else []
        hard_qs = generate_questions_for_course(req.course_name, "hard", req.hard) if req.hard > 0 else []
        
        all_generated = easy_qs + medium_qs + hard_qs
        
        if not all_generated:
            raise HTTPException(status_code=500, detail="No questions were generated.")
            
        new_db_questions = []
        for i, q in enumerate(all_generated):
            options = q.options
            while len(options) < 4:
                options.append("N/A")
                
            if i < req.easy:
                diff = "easy"
            elif i < req.easy + req.medium:
                diff = "medium"
            else:
                diff = "hard"
                
            new_q = Question(
                question=q.question,
                course_id=req.course_id,
                option_a=options[0],
                option_b=options[1],
                option_c=options[2],
                option_d=options[3],
                correct_answer=q.answer,
                difficulty=diff
            )
            new_db_questions.append(new_q)
            
        db.bulk_save_objects(new_db_questions)
        db.commit()
        
        return {"message": f"Successfully generated and inserted {len(new_db_questions)} questions into the bank.", "count": len(new_db_questions)}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-questions")
def trigger_refresh_questions(course_id: int = None, db: Session = Depends(get_db)):
    """
    Manually triggers the course question refresh.
    If 'course_id' is provided, it only refreshes that course.
    Otherwise, it refreshes all existing courses in the database.
    """
    try:
        if course_id:
            success = refresh_course_questions(db, course_id)
            if success:
                return {"message": f"Successfully refreshed questions for course ID '{course_id}'."}
            else:
                raise HTTPException(status_code=500, detail=f"Failed to refresh questions for course ID '{course_id}'. Check logs for details.")
        else:
            refresh_all_courses(db)
            return {"message": "Successfully triggered global refresh for all courses. Check logs to see progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

