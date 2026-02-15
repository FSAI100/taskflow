"""
TaskFlow AI Agent
使用 LangGraph 的 create_react_agent 创建 ReAct Agent。
ReAct = Reason（思考）+ Act（行动）循环。
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from app.ai.prompts import SYSTEM_PROMPT
from app.ai.tools import create_task, list_tasks, update_task, get_task_summary

load_dotenv()

# ── 初始化 LLM ──

from pydantic import SecretStr

llm = ChatOpenAI(
    model="qwen-plus",  # 模型名称
    api_key=SecretStr(os.getenv("DASHSCOPE_API_KEY") or ""),  # API Key
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义千问 OpenAI 兼容端点
    temperature=0.7,  # 创造性程度 0~2，越高越发散
)

# ── 工具列表 ──
tools = [create_task, list_tasks, update_task, get_task_summary]

# ── 创建 ReAct Agent ──
agent = create_react_agent(
    model=llm,
    tools=tools,
    state_modifier=SYSTEM_PROMPT,  # 注入 System Prompt
)


def chat_with_agent(user_message: str) -> str:
    """
    主入口：传入用户消息，返回 Agent 回复文本。
    Agent 会自动决定是否调用工具、调用哪个工具。
    """
    result = agent.invoke({"messages": [{"role": "user", "content": user_message}]})
    # 取最后一条 AI 回复
    ai_messages = [
        m for m in result["messages"] if hasattr(m, "content") and m.type == "ai"
    ]
    if ai_messages:
        return ai_messages[-1].content
    return "抱歉，我没有理解你的意思。可以换个说法试试？"
