# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr

import os
from dotenv import load_dotenv

from db import get_db
from models import User
from schemas.schemas import UserCreate, UserRead, UserLogin, Token

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "SUPER_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_db_user(db: Session, email: EmailStr, password: str):
    hashed_pw = pwd_context.hash(password)
    new_user = User(email=email, hashed_password=hashed_pw, is_active=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_user_by_email(db: Session, email: EmailStr):
    return db.query(User).filter(User.email == email).first()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/auth/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email already in use
    existing_user = get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    # Create user
    created_user = create_db_user(db, user.email, user.password)
    return UserRead(
        id=created_user.id,
        email=created_user.email,
        is_active=created_user.is_active,
        is_superuser=created_user.is_superuser
    )


@router.post("/auth/login", response_model=Token)
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user_data.email)
    if not db_user or not verify_password(user_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    return user


def get_current_active_superuser(current_user: User = Depends(get_current_user)):
    """
    Ensures the user is a superuser; raises 403 if not.
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have enough privileges",
        )
    return current_user


@router.get("/auth/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Example of a protected route: returns the currently logged-in user.
    """
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser
    )
@router.post("/auth/logout")
def logout_user(token: str = Depends(oauth2_scheme)):
    # Optionally mark token as invalid (e.g., save to a blacklist)
    return {"detail": "Logged out successfully"}


@router.get("/auth/protected")
def protected_route(current_user: User = Depends(get_current_user)):
    """
    Another example of a protected route requiring a valid JWT.
    """
    return {"message": "You are logged in!", "user_email": current_user.email}
