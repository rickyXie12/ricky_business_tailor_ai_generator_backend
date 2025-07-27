from dotenv import load_dotenv
# Load environment variables from .env file BEFORE any other imports
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from api import auth, campaigns, batch

# This will create tables if they don't exist.
# Note: For production, it's better to use a migration tool like Alembic.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Social Media Generator API",
    description="API for generating batch social media content using AI.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(batch.router, prefix="/api")

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

#
# database.py (Corrected)
#
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
# No longer need dotenv here, main.py handles it.

DATABASE_URL = os.getenv("DATABASE_URL")

# Add a check to ensure the URL was loaded
if DATABASE_URL is None:
    raise Exception("DATABASE_URL environment variable not set. Make sure you have a .env file.")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()