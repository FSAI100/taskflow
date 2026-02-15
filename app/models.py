"""
TaskFlow 数据模型
定义 API 请求和响应的数据结构
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    """任务优先级枚举"""

    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskStatus(str, Enum):
    """任务状态枚举"""

    todo = "todo"
    in_progress = "in_progress"
    done = "done"
    cancelled = "cancelled"


class TaskCreate(BaseModel):
    """创建任务时的请求体"""

    title: str = Field(..., min_length=1, max_length=200, examples=["完成项目报告"])
    description: Optional[str] = Field(None, max_length=2000)
    priority: Priority = Priority.medium
    status: TaskStatus = TaskStatus.todo


class TaskUpdate(BaseModel):
    """更新任务时的请求体（所有字段可选）"""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    priority: Optional[Priority] = None
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    """返回给用户的任务数据"""

    id: int
    title: str
    description: Optional[str] = None
    priority: Priority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
