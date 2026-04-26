from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库连接地址
DATABASE_URL = "mysql+pymysql://root:213465@localhost:3306/docmind"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()

# 获取数据库会话的函数，后面接口里会用到
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()