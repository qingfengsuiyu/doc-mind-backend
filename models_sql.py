from sqlalchemy import Column,Integer,String,DateTime
from datetime import datetime
from database_sql import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer,primary_key=True,index=True)
    username = Column(String(50),unique=True,nullable=False)
    password = Column(String(200),nullable=False)
    created_at = Column(DateTime,default=datetime.now)