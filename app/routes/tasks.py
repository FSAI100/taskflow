"""任务 CRUD — V2 数据库版"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.database import get_session
from app.models import Task, TaskCreate, TaskUpdate, User
from app.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["任务管理"])


@router.post("/", status_code=201)
def create_task(
    data: TaskCreate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    task = Task(
        title=data.title,
        description=data.description,
        priority=data.priority.value,
        status=data.status.value,
        user_id=user.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.get("/")
def list_tasks(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    query = select(Task).where(Task.user_id == user.id)
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    return session.exec(query).all()


@router.get("/{task_id}")
def get_task(
    task_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "任务不存在")
    return task


@router.put("/{task_id}")
def update_task(
    task_id: int,
    data: TaskUpdate,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "任务不存在")
    update_data = data.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(task, key, val.value if hasattr(val, "value") else val)
    task.updated_at = datetime.now()
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    task = session.get(Task, task_id)
    if not task or task.user_id != user.id:
        raise HTTPException(404, "任务不存在")
    session.delete(task)
    session.commit()
