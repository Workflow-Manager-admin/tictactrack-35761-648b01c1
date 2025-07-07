"""
Authentication router offering registration and login endpoints.
"""
from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from . import auth, models, schemas
from .auth import ACCESS_TOKEN_EXPIRE_MINUTES, get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead, summary="Register a new user")
def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    user = models.User(
        username=user_in.username, hashed_password=auth.get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=schemas.Token,
    summary="Login and obtain JWT access token",
)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return schemas.Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=schemas.UserRead, summary="Get current user profile")
def read_users_me(current_user: Annotated[models.User, Depends(auth.get_current_user)]):
    return current_user
