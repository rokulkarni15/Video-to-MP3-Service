from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any

from ..services.auth import AuthService
from ..models.schemas import UserCreate, UserResponse, Token, Login
from .dependencies import get_db, get_auth_service, get_current_user
from ..models.domain import User

router = APIRouter()

@router.post("/register", response_model=Token)
def register(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """Register a new user"""
    user = auth_service.create_user(user_data)
    return auth_service.create_tokens(user.id)

@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """OAuth2 compatible token login"""
    user = auth_service.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_tokens(user.id)

@router.post("/login", response_model=Token)
def login_json(
    login_data: Login,
    auth_service: AuthService = Depends(get_auth_service)
) -> Any:
    """JSON compatible login"""
    user = auth_service.authenticate(login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    return auth_service.create_tokens(user.id)

@router.get("/users/me", response_model=UserResponse)
def read_users_me(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Get current user"""
    return current_user

@router.post("/verify")
def verify_token(
    current_user: User = Depends(get_current_user)
) -> Any:
    """Verify access token"""
    return {"id": current_user.id, "email": current_user.email}