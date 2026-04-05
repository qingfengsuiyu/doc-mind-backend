# routers/chat.py
from fastapi import APIRouter,HTTPException
from models.schemas import AskRequest
import os
from openai import OpenAI
from database import vectorstore

router = APIRouter()

client = OpenAI(
        api_key = os.getenv("DASHSCOPE_API_KEY"),
        base_url = "https://dashscope.aliyuncs.com/compatible-mode/v1"
)

@router.post('/ask')
def ask(body:AskRequest):
    try:
        # 第一步：检索相关chunks
        docs = vectorstore.similarity_search(body.question, k=3)
        
        # 第二步：把chunks拼成上下文
        context = '\n'.join([doc.page_content for doc in docs])
        
        # 第三步：发给AI
        response = client.chat.completions.create(
            model = 'qwen-turbo',
            messages = [
            {
                'role': 'user',
                'content': f'基于以下内容回答问题：\n{context}\n\n问题：{body.question}'
            }
          ]
        )
        return {'answer': response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500,detail=f'AI 服务异常：{str(e)}')
    
    