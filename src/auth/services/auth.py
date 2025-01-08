from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from ..models.schemas import UserCreate, UserResponse, Token
from ..models.domain import User
from ..core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from ..core.config import settings
from ..core.exceptions import CredentialsError, DuplicateUserError

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_data: UserCreate) -> User:
        # Check if user exists
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise DuplicateUserError()
        
        # Create new user
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=get_password_hash(user_data.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def create_tokens(self, user_id: int) -> Token:
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return Token(
            access_token=access_token,
            refresh_token=refresh_token
        )

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()