from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from backend.models.user_models import UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

KEY=""
with open("backend/auth/secret_key.key", 'r') as file:
    KEY = file.read()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MIN = 30

class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)
    

    def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()

        expire = datetime.now(timezone.utc) + (
            expires_delta if expires_delta 
            else timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MIN)
        )

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])

        if not payload.get("id"):
            raise credentials_exception
        
        return payload
    
    except JWTError:
        raise credentials_exception


def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    return verify_token(token)


def get_current_active_user(currentUser = Depends(get_current_user)):
    return currentUser