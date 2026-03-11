# Quiz Generation & Auto Evaluation Backend

This project serves as a comprehensive Backend API for a scalable quiz generation, question banking, and evaluation platform.

Built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, this backend handles course management, automatic question serving, submission evaluation, correct-answer validation, and includes an advanced AI integration capable of dynamically generating properly formatted multiple-choice questions on demand. It also features a background scheduler for automated question bank refreshing.

---

## 🏗️ 1. Architecture Overview

```mermaid
graph TD
    UI[Frontend / React UI] <-->|REST API + JSON| API[FastAPI Backend]
    
    subgraph Backend Configuration
    API --> Routers[Routers: /course, /question, /quiz, /ai]
    Routers --> Schemas[Pydantic Models DTOs]
    Routers --> Models[SQLAlchemy DB Models]
    API -.-> Scheduler[APScheduler Background Tasks]
    end
    
    Models <-->|ORM| Database[(Database:\n PostgreSQL)]
    
    Database -.->|Stored Tables| CTable(Courses Table)
    Database -.->|Stored Tables| QTable(Questions Table)
    Database -.->|Stored Tables| ATTable(Quiz Attempts Table)
    Database -.->|Stored Tables| UATable(User Answers Table)
    
    API -.->|OpenAI API| LLM[gpt-4o-mini]
    Scheduler -.-> API
```

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL 
- **ORM**: SQLAlchemy 
- **Background Tasks**: APScheduler
- **AI Integration**: OpenAI SDK (`gpt-4o-mini` with strict Structured Outputs)

---

## 🗄️ 2. Database Design & Modular Architecture

The system is designed with distinct modules using the following tables:

1. **`courses` Table**: Manages courses and their configurations.
2. **`questions` Table**: The centralized question bank linked to courses.
3. **`quiz_attempts` Table**: Master record tracking an individual student's total score for a quiz session.
4. **`user_answers` Table**: Granular tracking associating a student's guess with the exact question asked and its correctness.

---

## 🚀 3. Core API Endpoints

Explore and test all APIs interactively via Swagger UI by navigating to `http://localhost:8000/docs`.

### Flow 1: Course & Question Management
**`GET /course/` & `POST /course/`**
- Create and manage courses.

**`GET /question/` & `POST /question/`**
- View the question bank. Questions can be batched generated via AI.

### Flow 2: Taking a Quiz
**`GET /quiz/start?difficulty=medium`**
- Initializes a new `QuizAttempt`. Fetches randomized questions from the PostgreSQL database according to the difficulty requested.
- Omits the `correct_answer` field to prevent client-side cheating.

### Flow 3: Submitting & Auto-Evaluating
**`POST /quiz/submit`**
- Receives an array of the user's `question_id` and their `selected_answer`.
- The API queries the Database for the true `correct_answer`, calculates the integer `score`, and inserts each guess into the `user_answers` table. Finally, it updates the `QuizAttempt` total score.
- Returns ONLY the final strict score (e.g., `{ "score": 8, "total": 10}`).

### Flow 4: Detailed Scorecard
**`GET /quiz/result/{quiz_id}`**
- Retrieves the master attempt, joins the `user_answers` to the original `questions` table, and returns an exhaustive JSON array showing exactly what the user selected versus what the correct answer was.

### Flow 5: Dynamic & Background AI Question Generation
**`POST /ai/generate-question`**
- Pings OpenAI `gpt-4o-mini` using **Structured Outputs** to force the LLM to reply exactly in the shape of our SQLAlchemy schema.
- Automatically inserts the newly minted question directly into your PostgreSQL database.

**Background Refresh Agent**
- Uses **APScheduler** to automatically refresh the question bank every 15 days, balancing difficulty (5 easy, 10 medium, 5 hard per course) and replacing stale questions with new AI-generated ones.

---

## 💻 4. Local Developer Setup Guide

To run this server locally on your machine for further development:

1. **Activate Environment**:
   ```bash
   cd backend
   source .venv/bin/activate
   ```
2. **Setup Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Environment Setup**:
   Ensure you have a `.env` file in the `backend` folder containing your API Key and Database. You can reference `.env.example`:
   ```env
   OPENAI_API_KEY=sk-proj-...
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ```
4. **Database Seeding**:
   To initialize or reset the tables with sample data, run:
   ```bash
   export PYTHONPATH=. && python seed.py
   ```
5. **Start the FastAPI Server**:
   ```bash
   uvicorn main:app --reload
   ```
