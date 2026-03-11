from typing import List
from openai import OpenAI
import os
from sqlalchemy.orm import Session
import logging

from app.models.quiz import Question, Course
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

def generate_questions_for_course(course_name: str, difficulty: str, count: int) -> List[GeneratedQuestionResponse]:
    """Generates a batch of questions for a specific course and difficulty."""
    client = get_openai_client()
    
    logger.info(f"Generating {count} {difficulty} questions for {course_name}...")
    
    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are an expert quiz generator. Generate {count} 4-option multiple choice questions. The answer must be one of the options."},
                {"role": "user", "content": f"Generate {count} {difficulty} difficulty multiple-choice questions about {course_name}. Each question must include a question, 4 options, and correct answer."}
            ],
            response_format=BatchQuestionResponse,
        )
        
        return completion.choices[0].message.parsed.questions
    except Exception as e:
        logger.error(f"Failed to generate questions for {course_name} ({difficulty}): {e}")
        return []

def refresh_course_questions(db: Session, course_id: int):
    """
    Refreshes questions for a single course:
    - Generates 5 easy, 10 medium, 5 hard.
    - Deletes old questions for the course.
    - Inserts the new ones.
    """
    logger.info(f"Starting question refresh for course ID: {course_id}")
    
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        logger.error(f"Course ID {course_id} not found.")
        return False
    
    course_name = course.course_name

    # 1. Generate new questions
    easy_qs = generate_questions_for_course(course_name, "easy", 5)
    medium_qs = generate_questions_for_course(course_name, "medium", 10)
    hard_qs = generate_questions_for_course(course_name, "hard", 5)
    
    all_generated = easy_qs + medium_qs + hard_qs
    
    if len(all_generated) < 20:
        logger.warning(f"Expected 20 questions for {course_name}, but generated {len(all_generated)}. Skipping refresh to avoid data loss.")
        return False
        
    try:
        # 2. Delete old questions
        deleted_count = db.query(Question).filter(Question.course_id == course_id).delete()
        logger.info(f"Deleted {deleted_count} old questions for {course_name}")
        
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
                course_id=course_id,
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
        logger.info(f"Successfully inserted {len(new_db_questions)} new questions for {course_name}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Database error during refresh for {course_name}: {e}")
        return False

def refresh_all_courses(db: Session):
    """
    Finds all unique courses in the database and refreshes their questions.
    """
    logger.info("Starting global question refresh job...")
    
    courses = db.query(Course).all()
    
    if not courses:
        logger.info("No courses found to refresh.")
        return
        
    for course in courses:
        refresh_course_questions(db, course.id)
        
    logger.info("Global question refresh job completed.")
