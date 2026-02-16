# TaskFlow

基于 FastAPI 的任务管理 API，支持用户认证、任务 CRUD、AI 对话与周报生成，从零迭代到可测试、可进化的全栈应用。

## 功能概览

- **用户系统**：注册、登录、JWT 认证、重置密码
- **任务管理**：创建 / 列表 / 详情 / 更新 / 删除，支持优先级与状态筛选
- **AI 聊天**：自然语言操控任务（如「帮我加个任务：写周报」「我有哪些待办」「总结一下」）
- **周报 Agent**：`POST /chat/weekly-report` 自动汇总本周已完成任务并生成结构化周报
- **前端页面**：登录页、仪表盘（静态 + API 调用）
- **测试与质量**：pytest 测试框架、用户/任务 API 测试、AI 回复关键词评测（可选）

## 技术栈

- **后端**：FastAPI、SQLModel、SQLite、JWT（python-jose）、passlib
- **AI**：LangChain、LangGraph（ReAct Agent）、通义千问（DashScope 兼容接口）
- **测试**：pytest、httpx、TestClient、内存 SQLite

## 项目结构

```
taskflow/
├── app/
│   ├── main.py          # FastAPI 应用入口
│   ├── database.py      # 数据库连接与建表
│   ├── auth.py          # 密码哈希、JWT、当前用户
│   ├── models.py        # User、Task 等模型
│   ├── routes/
│   │   ├── users.py     # 注册、登录、/me、重置密码
│   │   ├── tasks.py     # 任务 CRUD
│   │   ├── chat.py      # AI 聊天、周报
│   │   └── pages.py     # 登录页、仪表盘
│   ├── ai/
│   │   ├── agent.py     # ReAct Agent 与 chat_with_agent
│   │   ├── tools.py     # 创建/列表/更新任务、统计、本周完成
│   │   └── prompts.py   # 系统提示词
│   ├── static/         # 前端静态资源
│   └── templates/      # HTML 模板
├── tests/
│   ├── conftest.py      # 内存 DB、client 等 fixture
│   ├── test_users.py    # 用户 API 测试
│   ├── test_tasks.py    # 任务 API 测试
│   └── test_chat.py     # AI 回复评测（需 API Key）
├── requirements.txt
├── .env                 # 环境变量（勿提交密钥）
└── README.md
```

## 环境配置

1. **克隆并进入项目**

```bash
git clone <repo-url>
cd taskflow
```

2. **创建虚拟环境并安装依赖**

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **配置环境变量**

在项目根目录创建 `.env`，例如：

```env
DATABASE_URL=sqlite:///./taskflow.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
DASHSCOPE_API_KEY=sk-xxx   # 通义千问 API Key，AI 聊天与周报必填
```

## 运行方式

```bash
# 确保已激活虚拟环境
uvicorn app.main:app --reload
```

默认地址：<http://127.0.0.1:8000>  
API 文档：<http://127.0.0.1:8000/docs>

## 主要 API

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/users/register` | 注册 |
| POST | `/users/login` | 登录，返回 `access_token` |
| GET  | `/users/me` | 当前用户（需 Bearer Token） |
| POST | `/tasks/` | 创建任务（需认证） |
| GET  | `/tasks/` | 任务列表，可选 `status`、`priority` |
| GET  | `/tasks/{id}` | 任务详情 |
| PUT  | `/tasks/{id}` | 更新任务 |
| DELETE | `/tasks/{id}` | 删除任务 |
| POST | `/chat/` | AI 聊天（需认证） |
| POST | `/chat/weekly-report` | 生成本周工作周报（需认证） |
| GET  | `/login` | 登录页 |
| GET  | `/dashboard` | 仪表盘 |

## 测试

```bash
# 全部测试（无 API Key 时 AI 评测会跳过）
pytest tests/ -v

# 仅用户与任务 API
pytest tests/test_users.py tests/test_tasks.py -v

# 仅 AI 评测（需配置 DASHSCOPE_API_KEY）
pytest tests/test_chat.py -v
```

## 许可证

按项目仓库约定使用。
