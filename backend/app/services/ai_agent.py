from typing import List
from openai import OpenAI
import os
from sqlalchemy.orm import Session
import logging

from app.models.quiz import Question
from app.schemas.quiz import GeneratedQuestionResponse
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class BatchQuestionResponse(BaseModel):
    questions: List[GeneratedQuestionResponse]

def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY is not configured.")
    return OpenAI(api_key=api_key)

def generate_questions_for_course(course: str, difficulty: str, count: int) -> List[GeneratedQuestionResponse]:
    """Generates a batch of questions for a specific course and difficulty."""
    client = get_openai_client()
    
    logger.info(f"Generating {count} {difficulty} questions for {course}...")
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are an expert quiz generator. Generate {count} 4-option multiple choice questions. The answer must be one of the options."},
                {"role": "user", "content": f"Generate {count} {difficulty} difficulty multiple-choice questions about {course}."}
            ],
            response_format=BatchQuestionResponse,
        )
        
        return completion.choices[0].message.parsed.questions
    except Exception as e:
        logger.error(f"Failed to generate questions for {course} ({difficulty}): {e}")
        return []

def refresh_course_questions(db: Session, course: str):
    """
    Refreshes questions for a single course:
    - Generates 5 easy, 10 medium, 5 hard.
    - Deletes old questions for the course.
    - Inserts the new ones.
    """
    logger.info(f"Starting question refresh for course: {course}")
    
    # 1. Generate new questions
    easy_qs = generate_questions_for_course(course, "easy", 5)
    medium_qs = generate_questions_for_course(course, "medium", 10)
    hard_qs = generate_questions_for_course(course, "hard", 5)
    
    all_generated = easy_qs + medium_qs + hard_qs
    
    if len(all_generated) < 20:
        logger.warning(f"Expected 20 questions for {course}, but generated {len(all_generated)}. Skipping refresh to avoid data loss.")
        return False
        
    try:
        # 2. Delete old questions
        deleted_count = db.query(Question).filter(Question.course == course).delete()
        logger.info(f"Deleted {deleted_count} old questions for {course}")
        
        # 3. Insert new questions
        new_db_questions = []
        # Assign difficulty based on batch
        for i, q in enumerate(all_generated):
            options = q.options
            while len(options) < 4:
                options.append("N/A")
                
            if i < 5:
                diff = "easy"
            elif i < 15:
                diff = "medium"
            else:
                diff = "hard"
                
            new_q = Question(
                question=q.question,
                course=course,
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
        logger.info(f"Successfully inserted {len(new_db_questions)} new questions for {course}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during refresh for {course}: {e}")
        return False

def refresh_all_courses(db: Session):
    """
    Finds all unique courses in the database and refreshes their questions.
    """
    logger.info("Starting global question refresh job...")
    
    # Find active courses. We assume any course currently in the DB is active.
    # Note: If questions are deleted, the course is "lost". In a real system you'd have a Course table.
    courses = db.query(Question.course).filter(Question.course.isnot(None)).distinct().all()
    
    if not courses:
        logger.info("No courses found to refresh.")
        return
        
    for (course_name,) in courses:
        refresh_course_questions(db, course_name)
        
    logger.info("Global question refresh job completed.")
