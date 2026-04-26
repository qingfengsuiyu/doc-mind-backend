from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database_sql import get_db
from models_sql import User
from pydantic import BaseModel
from jose import jwt
from datetime import datetime,timedelta
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256" # 加密算法
EXPIRE_HOURS = 24 # Token 有效期 24 小时


security = HTTPBearer()
router = APIRouter()
load_dotenv()  # 加载 .env 文件

# 创建 bcrypt 加密工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 请求体数据结构
class AuthRequest(BaseModel):
    username: str
    password: str

@router.post('/auth/register')
def register(body: AuthRequest, db: Session = Depends(get_db)):
    # 第一步：查用户名是否存在
    existing_user = db.query(User).filter(User.username == body.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='用户名已存在')
    
    # 第二步：加密密码
    hashed_password = pwd_context.hash(body.password)
    
    # 第三步：插入数据库
    user = User(username=body.username, password=hashed_password)
    db.add(user)
    db.commit()
    
    return {'message': '注册成功'}

# 登录注册逻辑
def create_token(username:str):
    expire = datetime.now() + timedelta(hours=EXPIRE_HOURS)
    payload = {
        "sub": username,      # sub 是 JWT 标准字段，存用户标识
        "exp": expire         # exp 是过期时间
    }
    return jwt.encode(payload,SECRET_KEY,algorithm=ALGORITHM)

@router.post('/auth/login')
def login(body:AuthRequest,db:Session = Depends(get_db)):
    # 第一步:查用户
    user = db.query(User).filter(User.username == body.username).first();
    if not user:
        raise HTTPException(status_code=401,detail = '用户不存在')
    # 第二部:验证密码
    if not pwd_context.verify(body.password,user.password):
        raise HTTPException(status_code=401,detail='用户不存在')
    # 第三步:生成token
    token = create_token(user.username)
    return {'token':token,'username':user.username}


def verify_token(credentials:HTTPAuthorizationCredentials=Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username = payload.get('sub')
        if not username:
            raise HTTPException(status_code=401,detail='Token 无效')
        return username
    except Exception:
        raise HTTPException(status_code=401,detail='Token 无效或已过期')
    



