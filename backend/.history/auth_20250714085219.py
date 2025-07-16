# auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy import text
from database import engine
from schemas import UserInDB, TokenData
from typing import Optional

SECRET_KEY = "0fd58da17a8195ddf5c5e1d91f8391752550b47e29e56575b7d1fe15080a308c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_user_from_db(username: str) -> Optional[UserInDB]:
    query = text("SELECT username, hashed_password, role FROM users WHERE username = :username")
    with engine.connect() as conn:
        row = conn.execute(query, {"username": username}).fetchone()
    return UserInDB(**row._mapping) if row else None

async def authenticate_user(username: str, password: str) -> UserInDB:
    user = await get_user_from_db(username)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str     = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username, role=role)
    except JWTError:
        raise credentials_exception

    user = await get_user_from_db(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def require_role(required: str):
    async def checker(current_user: UserInDB = Depends(get_current_user)):
        if current_user.role != required:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return current_user
    return checker

require_admin = require_role("admin")
require_user  = require_role("user")
