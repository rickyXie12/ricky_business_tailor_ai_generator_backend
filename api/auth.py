from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
from models.all_models import User
from schemas.main import UserCreate, Token, UserPublic
import auth
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    try:
        if db.query(User).filter(User.username == user_in.username).first():
            logger.warning(f"Username already registered: {user_in.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        if db.query(User).filter(User.email == user_in.email).first():
            logger.warning(f"Email already registered: {user_in.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = auth.get_password_hash(user_in.password)
        new_user = User(username=user_in.username, email=user_in.email, password_hash=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User registered: {user_in.username} ({user_in.email})")
        return new_user
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise

@router.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = auth.create_access_token(data={"sub": user.username, "user_id": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}