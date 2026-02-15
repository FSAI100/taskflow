"""数据库连接和会话管理"""

from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./taskflow.db")
engine = create_engine(DATABASE_URL, echo=True)


def create_db():
    """创建所有表"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """获取数据库会话（每个请求一个）"""
    with Session(engine) as session:
        yield session
