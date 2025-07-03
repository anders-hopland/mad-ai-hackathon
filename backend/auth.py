"""
Authentication module with Google OAuth and JWT tokens
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import jwt
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session, select

from .database import User, get_db

import logging

logger = logging.getLogger("autoqa-auth")
# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv(
    "GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback"
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token", auto_error=False)


# Pydantic Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    picture: Optional[str] = None


class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str
    picture: str


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID from database"""
    return db.get(User, user_id)


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email from database"""
    statement = select(User).where(User.email == email)
    return db.exec(statement).first()


def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    """Get user by Google ID from database"""
    statement = select(User).where(User.google_id == google_id)
    return db.exec(statement).first()


def create_user(
    db: Session, email: str, name: str, google_id: str, picture: Optional[str] = None
) -> User:
    """Create new user in database"""
    user = User(email=email, name=name, google_id=google_id, picture=picture)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> Optional[User]:
    """Get current authenticated user from JWT token"""
    if not token:
        return None

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        logger.info(f"Attempting to decode token: {token[:20]}...")
        logger.info(f"Using SECRET_KEY: {SECRET_KEY[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"JWT payload: {payload}")
        user_id_str = payload.get("sub")
        if user_id_str is None:
            logger.warning("No 'sub' field in JWT payload")
            raise credentials_exception
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            logger.warning(f"Invalid user_id format: {user_id_str}")
            raise credentials_exception
        logger.info(f"Extracted user_id: {user_id}")
        token_data = TokenData(user_id=user_id)
    except InvalidTokenError as e:
        logger.error(f"JWT decode error: {e}")
        raise credentials_exception

    user = get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        logger.warning(f"User not found for ID: {token_data.user_id}")
        raise credentials_exception
    logger.info(f"Successfully authenticated user: {user.email}")
    return user


async def get_current_active_user(
    current_user: Annotated[Optional[User], Depends(get_current_user)],
) -> User:
    """Get current active user, raise exception if not authenticated"""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return current_user


async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """Get user info from Google using access token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google",
            )
        user_data = response.json()
        return GoogleUserInfo(**user_data)


async def exchange_code_for_token(code: str) -> str:
    """Exchange authorization code for access token"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": GOOGLE_REDIRECT_URI,
            },
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange code for token",
            )
        token_data = response.json()
        return token_data["access_token"]
