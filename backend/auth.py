"""
SentinelAI - Authentication Module
JWT-based authentication with role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import sqlalchemy as sa
from database import get_session, User
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


# === Pydantic Schemas ===

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: str
    role: str = "analyst"
    department: str = "Engineering"

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str
    role: str
    department: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str


# === Utility Functions ===

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=payload.get("role"))
    except JWTError:
        raise credentials_exception
    
    session = get_session()
    user = session.query(User).filter(User.username == token_data.username).first()
    session.close()
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_role(roles: List[str]):
    """Role-based access control decorator"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(roles)}"
            )
        return current_user
    return role_checker


# === Seed Users ===

def seed_users():
    """Create default users for demo"""
    session = get_session()
    
    default_users = [
        {
            "email": "admin@sentinelai.com",
            "username": "admin",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin",
            "department": "IT"
        },
        {
            "email": "analyst@sentinelai.com",
            "username": "analyst",
            "password": "analyst123",
            "full_name": "Sarah Chen",
            "role": "analyst",
            "department": "Security"
        },
        {
            "email": "compliance@sentinelai.com",
            "username": "compliance",
            "password": "compliance123",
            "full_name": "Michael Torres",
            "role": "compliance",
            "department": "Compliance"
        },
        {
            "email": "viewer@sentinelai.com",
            "username": "viewer",
            "password": "viewer123",
            "full_name": "Jessica Williams",
            "role": "viewer",
            "department": "Management"
        }
    ]
    
    for user_data in default_users:
        existing = session.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                department=user_data["department"],
                is_active=True
            )
            session.add(user)
    
    session.commit()
    session.close()
    print("✅ Default users seeded!")


if __name__ == '__main__':
    seed_users()

