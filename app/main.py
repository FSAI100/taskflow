"""
TaskFlow — 任务管理 API
V3: 数据库存储、用户认证、ai 聊天功能
"""

from fastapi import FastAPI
from app.database import create_db
from app.routes import tasks, users, chat  # ← 加了 chat

# ── 创建 FastAPI 应用实例 ──
app = FastAPI(title="TaskFlow API", version="3.0.0")


# ── 启动时自动建表 ──
@app.on_event("startup")
def on_startup():
    create_db()


# ── 注册路由 ──
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(chat.router)  # ← 新增


# ── 根路径 —— 健康检查 ──
@app.get("/")
def root():
    return {
        "app": "TaskFlow",
        "version": "3.0.0",
        "features": ["CRUD", "Auth", "AI Chat"],
    }
