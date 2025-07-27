import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.all_models import Campaign, User
from schemas.main import CampaignCreate, CampaignPublic
import auth
from jose import jwt

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

def get_current_user_id(token: str = Depends(auth.oauth2_scheme)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", response_model=CampaignPublic, status_code=201)
def create_campaign(campaign: CampaignCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    new_campaign = Campaign(**campaign.dict(), user_id=user_id)
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)
    return new_campaign

@router.get("/", response_model=List[CampaignPublic])
def get_campaigns(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    campaigns = db.query(Campaign).filter(Campaign.user_id == user_id).all()
    return campaigns