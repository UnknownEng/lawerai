"""
Authentication Router for User Accounts and Case History Persistence
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..database import get_db, User
from ..auth import get_password_hash, verify_password, create_access_token, get_current_user
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str = ""
    beta_code: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyBetaCodeRequest(BaseModel):
    code: str



class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    stmt = select(User).where(User.email == req.email.lower().strip())
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    user = User(
        email=req.email.lower().strip(),
        hashed_password=get_password_hash(req.password),
        full_name=req.full_name.strip()
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name}
    }


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == req.email.lower().strip())
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )

    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {"id": user.id, "email": user.email, "full_name": user.full_name}
    }


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "full_name": user.full_name}


@router.post("/verify-beta-code")
async def verify_beta_code(req: VerifyBetaCodeRequest):
    expected = (settings.BETA_ACCESS_CODE or "QANOON-BETA-2026").strip()
    provided = (req.code or "").strip()
    if provided.lower() == expected.lower():
        return {"valid": True, "message": "Beta invite code accepted."}

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid beta invitation code. Please check with your administrator."
    )

