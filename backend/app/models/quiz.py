from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime

from app.db.database import Base

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)
    difficulty = Column(String, index=True) # easy, medium, hard

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True) # Assuming a simple user_id for POC
    score = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    answers = relationship("UserAnswer", back_populates="quiz")

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz_attempts.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    selected_answer = Column(String)
    correct = Column(Boolean)

    quiz = relationship("QuizAttempt", back_populates="answers")
    # You could also add a back-populates relationship to Question if needed
