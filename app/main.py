import os
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .database import engine
from .models import user
from .routers import auth

load_dotenv()

user.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FastAPI Auth with Google OAuth", version="1.0.0")

# pasang SessionMiddleware dulu
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SESSION_SECRET_KEY", "default_secret"))

# pasang middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# router autentikasi
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "FastAPI Auth Backend is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
