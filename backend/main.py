from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import engine, Base
from app.routers import quiz, ai
from app.services.scheduler import start_scheduler, stop_scheduler

# Create database tables
# This should happen before the app fully starts
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the background scheduler
    start_scheduler()
    yield
    # Shutdown: Stop the background scheduler
    stop_scheduler()

app = FastAPI(
    title="Quiz Generation API",
    description="POC API for Quiz Generation and Auto Evaluation",
    version="1.0.0",
    lifespan=lifespan
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
