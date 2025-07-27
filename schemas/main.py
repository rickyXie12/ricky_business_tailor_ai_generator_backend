from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# --- User Schemas ---
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# --- Campaign Schemas ---
class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    brand_name: str
    target_audience: Optional[str] = None
    tone_id: str

class CampaignPublic(CampaignCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# --- Batch Generation Schemas ---
class PostGenerationInput(BaseModel):
    title: str
    topic: Optional[str] = None
    brief: str
    brand_name: str
    tone: str
    target_audience: Optional[str] = None
    generate_caption: bool = True
    generate_image: bool = True

class BatchGenerationRequest(BaseModel):
    name: str
    posts: List[PostGenerationInput]