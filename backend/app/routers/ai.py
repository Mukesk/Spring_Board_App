from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os
from dotenv import load_dotenv

from app.db.database import get_db
from app.models.quiz import Question
from app.schemas.quiz import GenerateQuestionRequest, GeneratedQuestionResponse
from app.services.ai_agent import refresh_course_questions, refresh_all_courses

# Load env vars
load_dotenv()

router = APIRouter(prefix="/ai", tags=["AI Generation"])

def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
         raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured. Please add it to your .env file.")
    return OpenAI(api_key=api_key)

@router.post("/generate-question", response_model=GeneratedQuestionResponse)
def generate_question(req: GenerateQuestionRequest, db: Session = Depends(get_db)):
    """
    Generates a question using OpenAI's Structured Outputs,
    saves the question to the database, and returns it.
    """
    client = get_openai_client()

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert quiz generator. Generate a 4-option multiple choice question. The answer must be one of the options."},
                {"role": "user", "content": f"Generate a {req.difficulty} difficulty multiple-choice question about {req.topic}."}
            ],
            response_format=GeneratedQuestionResponse,
        )
        
        parsed_question = completion.choices[0].message.parsed
        
        # Save to Database
        # Ensuring we at least have 4 options, pad or slice as needed just in case
        options = parsed_question.options
        while len(options) < 4:
            options.append("N/A")
            
        new_q = Question(
            question=parsed_question.question,
            option_a=options[0],
            option_b=options[1],
            option_c=options[2],
            option_d=options[3],
            correct_answer=parsed_question.answer,
            difficulty=req.difficulty.lower()
        )
        
        db.add(new_q)
        db.commit()
        db.refresh(new_q)
        
        return parsed_question

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-questions")
def trigger_refresh_questions(course: str = None, db: Session = Depends(get_db)):
    """
    Manually triggers the course question refresh.
    If 'course' is provided, it only refreshes that course.
    Otherwise, it refreshes all existing courses in the database.
    """
    try:
        if course:
            success = refresh_course_questions(db, course)
            if success:
                return {"message": f"Successfully refreshed questions for course '{course}'."}
            else:
                raise HTTPException(status_code=500, detail=f"Failed to refresh questions for course '{course}'. Check logs for details.")
        else:
            refresh_all_courses(db)
            return {"message": "Successfully triggered global refresh for all courses. Check logs to see progress."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
