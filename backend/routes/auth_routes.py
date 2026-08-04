"""
SentinelAI - Authentication Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import (
    verify_password, get_password_hash, create_access_token, create_refresh_token,
    get_current_user, get_current_active_user, require_role, Token, UserCreate, UserResponse, seed_users
)
from database import get_session, User
from config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    session = get_session()
    user = session.query(User).filter(User.username == form_data.username).first()
    session.close()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username, "role": user.role}
    )
    
    # Update last login
    from datetime import datetime
    session = get_session()
    db_user = session.query(User).filter(User.id == user.id).first()
    db_user.last_login = datetime.utcnow()
    session.commit()
    session.close()
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, current_user: User = Depends(require_role(["admin"]))):
    """Register new user (admin only)"""
    session = get_session()
    
    # Check if username exists
    existing = session.query(User).filter(User.username == user_data.username).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email exists
    existing = session.query(User).filter(User.email == user_data.email).first()
    if existing:
        session.close()
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        department=user_data.department,
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user info"""
    return current_user


@router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(require_role(["admin", "analyst"]))):
    """Get all users"""
    session = get_session()
    users = session.query(User).all()
    session.close()
    return users


@router.get("/seed")
async def seed_database():
    """Seed database with default users"""
    try:
        seed_users()
        return {"message": "Database seeded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

