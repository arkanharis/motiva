import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .database import engine
from .models import user, task  # Import task model
from .routers import auth, tasks  # Import tasks router

load_dotenv()

# Create tables
user.Base.metadata.create_all(bind=engine)
task.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Task & Schedule Assistant", version="1.0.0")

# Add SessionMiddleware first
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret"))

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(tasks.router)  # Add tasks router

@app.get("/")
def read_root():
    return {"message": "AI Task & Schedule Assistant Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}