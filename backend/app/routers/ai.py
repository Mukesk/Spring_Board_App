from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from openai import OpenAI
import os
from dotenv import load_dotenv

from app.db.database import get_db
from app.models.quiz import Question
from app.schemas.quiz import GenerateQuestionRequest, GeneratedQuestionResponse

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

