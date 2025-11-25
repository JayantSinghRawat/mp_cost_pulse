from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing - use bcrypt with explicit backend
try:
    import bcrypt
    pwd_context = CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=12,
        bcrypt__ident="2b"  # Use bcrypt 2b identifier
    )
except Exception:
    # Fallback if bcrypt has issues
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Settings
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt directly"""
    import bcrypt
    # Ensure password is bytes
    if isinstance(plain_password, str):
        password_bytes = plain_password.encode('utf-8')
    else:
        password_bytes = plain_password
    
    # Bcrypt has a 72-byte limit - truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Verify with bcrypt directly
    if isinstance(hashed_password, str):
        hashed_bytes = hashed_password.encode('utf-8')
    else:
        hashed_bytes = hashed_password
    
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly to avoid passlib issues"""
    import bcrypt
    # Ensure password is bytes
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
    else:
        password_bytes = password
    
    # Bcrypt has a 72-byte limit - truncate if necessary
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    
    # Hash with bcrypt directly
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

