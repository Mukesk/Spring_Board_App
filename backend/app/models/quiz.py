from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.db.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    questions = relationship("Question", back_populates="course_obj")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True)
    question = Column(String, index=True)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    difficulty = Column(String, index=True)  # easy, medium, hard

    course_obj = relationship("Course", back_populates="questions")


class QuizAttempt(Base):
    """
    Score Storage Service model
    """
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), index=True)
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    answers = relationship("UserAnswer", back_populates="quiz")
    course = relationship("Course")


class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_answer = Column(String)
    correct = Column(Boolean)

    quiz = relationship("QuizAttempt", back_populates="answers")
