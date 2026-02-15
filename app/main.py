"""
TaskFlow — 任务管理 API
V1: 内存存储版本
"""

from fastapi import FastAPI
from app.routes import tasks

# ── 创建 FastAPI 应用实例 ──
app = FastAPI(
    title="TaskFlow API",
    description="一个不断进化的任务管理系统",
    version="1.0.0",
)

# ── 注册路由 ──
app.include_router(tasks.router)


# ── 根路径 —— 健康检查 ──
@app.get("/")
def root():
    return {
        "app": "TaskFlow",
        "version": "1.0.0",
        "docs": "/docs",
        "message": "访问 /docs 查看完整 API 文档",
    }
