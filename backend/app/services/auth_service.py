from sqlalchemy.orm import Session
from typing import Optional
from datetime import timedelta, datetime
import secrets
import string
from app.models.user import User
from app.models.otp import OTP
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.core.config import settings
from app.services.email_service import EmailService

class AuthService:
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user by username and password"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        if AuthService.get_user_by_username(db, user_create.username):
            raise ValueError("Username already registered")
        if AuthService.get_user_by_email(db, user_create.email):
            raise ValueError("Email already registered")
        
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """Create an access token for a user"""
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "user_id": user.id},
            expires_delta=access_token_expires
        )
        return access_token
    
    @staticmethod
    def generate_otp() -> str:
        """Generate a random OTP code"""
        digits = string.digits
        return ''.join(secrets.choice(digits) for _ in range(settings.OTP_LENGTH))
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token for OTP verification"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def initiate_2fa(db: Session, user: User) -> str:
        """Initiate 2FA by generating OTP, sending email, and creating session"""
        # Generate OTP
        otp_code = AuthService.generate_otp()
        session_token = AuthService.generate_session_token()
        
        # Calculate expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
        
        # Invalidate any existing OTPs for this user
        db.query(OTP).filter(
            OTP.user_id == user.id,
            OTP.is_used == False
        ).update({"is_used": True})
        
        # Create new OTP record
        otp_record = OTP(
            user_id=user.id,
            otp_code=otp_code,
            session_token=session_token,
            expires_at=expires_at,
            is_used=False
        )
        db.add(otp_record)
        db.commit()
        
        # Send OTP email
        EmailService.send_otp_email(user.email, otp_code)
        
        return session_token
    
    @staticmethod
    def verify_otp(db: Session, session_token: str, otp_code: str) -> Optional[User]:
        """Verify OTP and return user if valid"""
        # Find OTP record
        otp_record = db.query(OTP).filter(
            OTP.session_token == session_token,
            OTP.is_used == False
        ).first()
        
        if not otp_record:
            return None
        
        # Check if expired
        if datetime.utcnow() > otp_record.expires_at:
            return None
        
        # Check if OTP code matches
        if otp_record.otp_code != otp_code:
            return None
        
        # Mark OTP as used
        otp_record.is_used = True
        db.commit()
        
        # Get user
        user = db.query(User).filter(User.id == otp_record.user_id).first()
        return user

