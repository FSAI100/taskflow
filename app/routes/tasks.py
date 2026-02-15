"""
任务相关的 API 端点
V1：数据暂存在内存中（列表），重启就清空
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus

# ── 创建路由器 ──
router = APIRouter(prefix="/tasks", tags=["任务管理"])

# ── 内存数据库（V1 用列表暂存，V2 会换成真数据库）──
tasks_db: List[dict] = []
next_id: int = 1


# ── 1. 创建任务 ──
@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(task: TaskCreate):
    """
    创建一个新任务
    - 自动分配 ID
    - 自动记录创建时间
    """
    global next_id
    now = datetime.now()
    new_task = {
        "id": next_id,
        "title": task.title,
        "description": task.description,
        "priority": task.priority,
        "status": task.status,
        "created_at": now,
        "updated_at": now,
    }
    tasks_db.append(new_task)
    next_id += 1
    return new_task


# ── 2. 获取所有任务（支持按状态和优先级筛选）──
@router.get("/", response_model=List[TaskResponse])
def list_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[str] = None,
):
    """获取任务列表，可选筛选条件"""
    result = tasks_db

    if status:
        result = [t for t in result if t["status"] == status]
    if priority:
        result = [t for t in result if t["priority"] == priority]

    return result


# ── 3. 获取单个任务 ──
@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """通过 ID 获取单个任务"""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")


# ── 4. 更新任务 ──
@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate):
    """更新任务的某些字段"""
    for task in tasks_db:
        if task["id"] == task_id:
            update_data = task_update.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                task[key] = value
            task["updated_at"] = datetime.now()
            return task
    raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")


# ── 5. 删除任务 ──
@router.delete("/{task_id}", status_code=204)
def delete_task(task_id: int):
    """删除一个任务"""
    for i, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"任务 {task_id} 不存在")


# ── 6. 获取任务统计 ──
@router.get("/stats/summary")
def get_stats():
    """获取任务统计数据"""
    total = len(tasks_db)
    by_status = {}
    by_priority = {}
    for task in tasks_db:
        s = task["status"].value if hasattr(task["status"], "value") else task["status"]
        p = (
            task["priority"].value
            if hasattr(task["priority"], "value")
            else task["priority"]
        )
        by_status[s] = by_status.get(s, 0) + 1
        by_priority[p] = by_priority.get(p, 0) + 1
    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
    }
