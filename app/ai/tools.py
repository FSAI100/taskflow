"""
Agent 工具集：每个工具对应一个任务操作。
LLM 会根据函数名和 docstring 判断何时调用哪个工具。
"""

from langchain_core.tools import tool
from sqlmodel import Session, select
from datetime import datetime
from typing import Optional

from app.database import engine
from app.models import Task


def _get_session():
    """工具内部使用的数据库会话"""
    return Session(engine)


# ── 全局变量：记录当前用户 ID（由 chat 路由设置）──
_current_user_id: int = 0


def set_current_user_id(user_id: int):
    """在每次聊天请求时设置当前用户"""
    global _current_user_id
    _current_user_id = user_id


@tool
def create_task(
    title: str,
    description: str = "",
    priority: str = "medium",
) -> str:
    """创建一个新任务。

    Args:
        title: 任务标题（必填）
        description: 任务描述（可选）
        priority: 优先级，可选值：low / medium / high / urgent
    """
    with _get_session() as session:
        task = Task(
            title=title,
            description=description or None,
            priority=priority,
            status="todo",
            user_id=_current_user_id,
        )
        session.add(task)
        session.commit()
        session.refresh(task)
        return f"✅ 已创建任务 [ID:{task.id}] {task.title}（优先级：{task.priority}）"


@tool
def list_tasks(
    status_filter: Optional[str] = None,
) -> str:
    """查看当前用户的任务列表。

    Args:
        status_filter: 可选的状态筛选，可选值：todo / in_progress / done / cancelled。不传则返回全部。
    """
    with _get_session() as session:
        query = select(Task).where(Task.user_id == _current_user_id)
        if status_filter:
            query = query.where(Task.status == status_filter)
        tasks = session.exec(query).all()

        if not tasks:
            return "📭 没有找到符合条件的任务。"

        lines = []
        for t in tasks:
            icon = {
                "todo": "⬜",
                "in_progress": "🔵",
                "done": "✅",
                "cancelled": "❌",
            }.get(t.status, "•")
            lines.append(
                f"{icon} [ID:{t.id}] {t.title} | 优先级:{t.priority} | 状态:{t.status}"
            )
        return "\n".join(lines)


@tool
def update_task(
    task_id: int,
    new_status: Optional[str] = None,
    new_priority: Optional[str] = None,
    new_title: Optional[str] = None,
) -> str:
    """更新一个已有任务的状态、优先级或标题。

    Args:
        task_id: 要更新的任务 ID（必填）
        new_status: 新状态，可选值：todo / in_progress / done / cancelled
        new_priority: 新优先级，可选值：low / medium / high / urgent
        new_title: 新标题
    """
    with _get_session() as session:
        task = session.get(Task, task_id)
        if not task or task.user_id != _current_user_id:
            return f"❌ 找不到 ID 为 {task_id} 的任务"

        changes = []
        if new_status:
            task.status = new_status
            changes.append(f"状态→{new_status}")
        if new_priority:
            task.priority = new_priority
            changes.append(f"优先级→{new_priority}")
        if new_title:
            task.title = new_title
            changes.append(f"标题→{new_title}")

        task.updated_at = datetime.now()
        session.add(task)
        session.commit()
        return f"✅ 已更新任务 [ID:{task_id}]：{', '.join(changes)}"


@tool
def get_task_summary() -> str:
    """获取当前用户的任务统计摘要。无需参数。"""
    with _get_session() as session:
        tasks = session.exec(select(Task).where(Task.user_id == _current_user_id)).all()
        total = len(tasks)
        if total == 0:
            return "📊 你还没有任何任务。"

        status_count = {}
        priority_count = {}
        for t in tasks:
            status_count[t.status] = status_count.get(t.status, 0) + 1
            priority_count[t.priority] = priority_count.get(t.priority, 0) + 1

        lines = [f"📊 任务总计：{total} 个"]
        for s, c in status_count.items():
            lines.append(f"  - {s}: {c} 个")
        for p, c in priority_count.items():
            lines.append(f"  - {p}优先级: {c} 个")
        return "\n".join(lines)
