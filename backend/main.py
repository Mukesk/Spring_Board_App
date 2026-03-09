from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.routers import quiz, ai

# Create database tables
# This should happen before the app fully starts
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Quiz Generation API",
    description="POC API for Quiz Generation and Auto Evaluation",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For POC, all origins are OK
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(quiz.router)
app.include_router(ai.router)

@app.get("/")
def read_root():
    return {"message": "Quiz POC Backend is running. Go to /docs for Swagger UI."}
