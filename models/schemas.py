# 这部分只写接口逻辑
from pydantic import BaseModel

# 定义一个数据结构,描述请求体长什么样
class AskRequest(BaseModel):
    question:str

