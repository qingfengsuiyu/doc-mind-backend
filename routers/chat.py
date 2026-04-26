# routers/chat.py
from fastapi import APIRouter, HTTPException,Depends
from models.schemas import AskRequest
import os
from openai import OpenAI
from database import vectorstore
from fastapi.responses import StreamingResponse
import json
from routers.auth import verify_token

router = APIRouter()

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

@router.post('/ask')
def ask(body: AskRequest, username: str = Depends(verify_token)):
    try:
        # 第一步：检索相关chunks
        if body.source:
            docs = vectorstore.similarity_search(
                body.question, 
                k=9,
                filter={'source': body.source}
            )
        else:
            docs = vectorstore.similarity_search(body.question, k=9)
        
        # 第二步：把chunks拼成上下文
        context = '\n'.join([doc.page_content for doc in docs])
        
        # 第三步：构建完整messages
        messages = [
            {
                'role': 'system',
                'content': '你是一个知识库问答助手。回答问题时请注意：1. 只使用纯文本回答，不要使用任何Markdown语法，不要使用**加粗**、#标题、-列表等格式。2. 语言简洁清晰。3. 只根据提供的文档内容回答，如果文档中没有相关信息，请直接说明。'
            }
        ]
        
        # 第四步：加入历史对话
        for msg in body.history:
            messages.append({
                'role': 'user' if msg.role == 'user' else 'assistant',
                'content': msg.content
            })
        
        # 第五步：加入当前问题+检索到的上下文
        messages.append({
            'role': 'user',
            'content': f'基于以下内容回答问题：\n{context}\n\n问题：{body.question}'
        })
        
        response = client.chat.completions.create(
            model='qwen-turbo',
            messages=messages
        )
        return {'answer': response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'AI 服务异常：{str(e)}')
    
    
@router.post('/ask/stream')
def ask_stream(body:AskRequest,username: str = Depends(verify_token)):
    def generate():
        if body.source:
            docs = vectorstore.similarity_search(
                body.question, 
                k=9,
                filter={'source': body.source}
            )
        else:
            docs = vectorstore.similarity_search(body.question, k=9)
        
        context = '\n'.join([doc.page_content for doc in docs])
        messages = [
            {
                'role': 'system',
                'content': '你是一个知识库问答助手。回答问题时请注意：1. 只使用纯文本回答，不要使用任何Markdown语法，不要使用**加粗**、#标题、-列表等格式。2. 语言简洁清晰。3. 只根据提供的文档内容回答，如果文档中没有相关信息，请直接说明。'
            }
        ]
        for msg in body.history:
            messages.append({
                'role': 'user' if msg.role == 'user' else 'assistant',
                'content': msg.content
            })
        
        messages.append({
            'role': 'user',
            'content': f'基于以下内容回答问题：\n{context}\n\n问题：{body.question}'
        })
        # stream=True 开启流式
        response = client.chat.completions.create(
            model='qwen-turbo',
            messages=messages,
            stream=True
        )
        # stream=True 时，response 不再是完整回答
        # 而是一个"流"，可以用 for 循环逐块读取
        # 每次循环，chunk 就是 AI 新生成的一小块内容
        for chunk in response:
            text = chunk.choices[0].delta.content
            if text:
                # SSE 格式：data: 内容\n\n
                yield f"data: {json.dumps({'type': 'text', 'content': text}, ensure_ascii=False)}\n\n"
        
        sources = [doc.page_content[:200] for doc in docs]
        yield f"data: {json.dumps({'type': 'sources', 'content': sources}, ensure_ascii=False)}\n\n"
        
        # 发送结束标志
        yield "data: [DONE]\n\n"
    return StreamingResponse(generate(), media_type="text/event-stream")