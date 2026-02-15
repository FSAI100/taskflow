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

    # 调用 Agent
    reply = chat_with_agent(req.message)
    return ChatResponse(reply=reply)
