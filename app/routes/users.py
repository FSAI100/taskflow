"""用户注册、登录、个人信息"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.database import get_session
from app.models import User, UserCreate, UserResponse
from app.models import LoginRequest, ResetPasswordRequest
from app.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(data: UserCreate, session: Session = Depends(get_session)):
    # 检查用户名是否已存在
    existing = session.exec(select(User).where(User.username == data.username)).first()
    if existing:
        raise HTTPException(400, "用户名已存在")
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.post("/login")
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(401, "用户名或密码错误")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, session: Session = Depends(get_session)):
    """重置密码（用于 hash 异常或忘记密码时恢复登录）"""
    user = session.exec(select(User).where(User.username == data.username)).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    user.hashed_password = hash_password(data.new_password)
    session.add(user)
    session.commit()
    return {"message": "密码已更新，请使用新密码登录"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
