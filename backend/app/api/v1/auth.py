from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import UserCreate, UserResponse, Token, UserLogin, LoginStep1Response, OTPVerify
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        db_user = AuthService.create_user(db=db, user_create=user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    user = AuthService.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=LoginStep1Response)
def login_json(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login step 1: Verify email/password and initiate 2FA"""
    user = AuthService.authenticate_user(db, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Initiate 2FA - generate OTP and send email
    session_token = AuthService.initiate_2fa(db, user)
    
    return {
        "session_token": session_token,
        "message": "OTP sent to your email. Please verify to complete login."
    }

@router.post("/verify-otp", response_model=Token)
def verify_otp(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """Login step 2: Verify OTP and return access token"""
    user = AuthService.verify_otp(db, otp_data.session_token, otp_data.otp_code)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired OTP",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = AuthService.create_access_token_for_user(user)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    from app.core.security import decode_access_token
    from app.models.user import User
    
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = AuthService.get_user_by_username(db, username=username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user

