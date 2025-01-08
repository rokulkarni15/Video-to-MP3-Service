from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional, List
from datetime import datetime

from ..models.domain import User, RefreshToken
from ..models.schemas import UserCreate, UserUpdate
from ..core.security import get_password_hash
from ..core.exceptions import DuplicateUserError

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def create(self, user_data: UserCreate) -> User:
        """Create a new user"""
        try:
            db_user = User(
                email=user_data.email,
                username=user_data.username,
                hashed_password=get_password_hash(user_data.password)
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise DuplicateUserError()

    def update(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(db_user, field, value)

        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            raise DuplicateUserError()

    def delete(self, user_id: int) -> bool:
        """Delete a user"""
        db_user = self.get_by_id(user_id)
        if db_user:
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False

    # Refresh Token operations
    def create_refresh_token(self, user_id: int, token: str, expires_at: datetime) -> RefreshToken:
        """Create a new refresh token"""
        db_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            is_revoked=False
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        return self.db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.is_revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()

    def revoke_refresh_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == token
        ).first()
        
        if db_token:
            db_token.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> bool:
        """Revoke all refresh tokens for a user"""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        
        self.db.commit()
        return True

    def cleanup_expired_tokens(self) -> int:
        """Clean up expired tokens"""
        result = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < datetime.utcnow()
        ).delete()
        
        self.db.commit()
        return result