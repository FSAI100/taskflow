"""聊天端点：接收用户消息，返回 AI 回复"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.auth import get_current_user
from app.models import User
from app.ai.agent import chat_with_agent
from app.ai.tools import set_current_user_id

router = APIRouter(prefix="/chat", tags=["AI 聊天"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/", response_model=ChatResponse)
def chat(
    req: ChatRequest,
    user: User = Depends(get_current_user),
):
    """
    发送消息给 AI 助手。

    需要登录（带 Token）。AI 会自动识别你的意图：
    - "帮我加个任务" → 创建任务
    - "我有哪些待办" → 查看任务
    - "把XX标记为完成" → 更新任务
    - "总结一下" → 任务统计
    """
    # 告诉工具函数"当前是谁在操作"
    set_current_user_id(user.id)

    try:
        reply = chat_with_agent(req.message)
        return ChatResponse(reply=reply)
    except Exception as e:
        err_msg = str(e) if str(e) else repr(e)
        return ChatResponse(reply="AI 服务暂时不可用，请稍后重试。错误：" + err_msg)


@router.post("/weekly-report")
def weekly_report(user: User = Depends(get_current_user)):
    """让 AI 生成本周工作周报"""
    set_current_user_id(user.id)
    try:
        reply = chat_with_agent(
            "请帮我生成本周工作周报。先查看本周完成的任务，然后按以下格式总结："
            "1. 本周完成概览（总数）2. 按优先级分类 3. 下周建议。语气专业简洁。"
        )
        return {"report": reply}
    except Exception as e:
        err_msg = str(e) if str(e) else repr(e)
        return {"report": "周报生成失败：" + err_msg}
