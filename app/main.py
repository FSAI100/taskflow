"""
TaskFlow — 任务管理 API
V4: 数据库存储、用户认证、ai 聊天功能、前端页面。
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles  # 新增
from app.database import create_db
from app.routes import tasks, users, chat, pages  # 加了 pages


# ── 创建 FastAPI 应用实例 ──
app = FastAPI(title="TaskFlow", version="4.0.0")

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ── 启动时自动建表 ──
@app.on_event("startup")
def on_startup():
    create_db()


# ── 注册路由 ──
app.include_router(users.router)
app.include_router(tasks.router)
app.include_router(chat.router)

# 页面路由
app.include_router(pages.router)


# ── 根路径 —— 健康检查 ──
@app.get("/")
def root():
    return {
        "app": "TaskFlow",
        "version": "4.0.0",
        "features": ["CRUD", "Auth", "AI Chat", "Pages"],
        "static": "/static/",
    }
