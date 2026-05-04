from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件
DATABASE_URL = os.getenv("DATABASE_URL") # 数据库连接地址

engine = create_engine(
    DATABASE_URL,
    pool_recycle=3600,    # 每小时回收连接，防止 MySQL 超时断开
    pool_pre_ping=True,   # 每次使用连接前先 ping 一下，自动重连
)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()

# 获取数据库会话的函数，后面接口里会用到
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()