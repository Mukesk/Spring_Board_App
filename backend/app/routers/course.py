from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.quiz import Course
from app.schemas.quiz import CourseCreate, CourseOut

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.post("", response_model=CourseOut)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    # Check if course already exists
    existing = db.query(Course).filter(Course.course_name == course.course_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course already exists")
    
    new_course = Course(course_name=course.course_name)
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course

@router.get("", response_model=List[CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()
