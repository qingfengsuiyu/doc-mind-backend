# 这部分只写接口逻辑
from pydantic import BaseModel
from typing import List


class Message(BaseModel):
    role: str
    content: str
    
# 定义一个数据结构,描述请求体长什么样
class AskRequest(BaseModel):
    question:str
    history: List[Message] = []  # 默认空列表
    source: str = ''  # 当前选中的文档名，空字符串表示全部

