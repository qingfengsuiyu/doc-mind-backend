from fastapi import APIRouter,File,UploadFile,HTTPException,Depends
import io
import PyPDF2
from database import splitter,vectorstore
import json
import os
from datetime import datetime
from routers.auth import verify_token
from openai import OpenAI

router = APIRouter()
meta_path = './docs_meta.json'

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)
    




# 写入文档元数据
def save_doc_meta(filename, chunk_count,username):
    
    # 读取现有数据，文件不存在就用空列表
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
    else:
        docs = []
    
    # 追加新文档信息
    docs.append({
        'filename': filename,
        'chunk_count': chunk_count,
        'upload_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'username':username
        
    })
    
    # 写回文件
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
        



@router.post('/upload')
async def upload(file:UploadFile = File(...),username: str = Depends(verify_token)):
    # 文件校检
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail='只支持 PDF 文件')
    
    # 检查文件是否上传过:1.获取文件用户名
    filename = file.filename
    # 2.读取json文件
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
    else:
        docs = []
    # 3.判断json数据中是否存在该记录
    isExit = any((d['filename'] == filename and d['username'] == username) for d in docs)
    # 4.如果存在,不上传,在文件中追加一条记录,用户名为当前用户的
    if isExit:
        raise HTTPException(status_code=409,detail='File already exists')
    
    content = await file.read() #读取二进制内容
    
    # 超过10M的文件不上传
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400,detail='文件大小不能超过 10MB')
    
    
    # 读取文件-正常流程
    # 1.将二进制包装成对象
    content_obj = io.BytesIO(content)
    # 2.用pyPDF2读取
    pdf_reader = PyPDF2.PdfReader(content_obj)
    
    # 获取标题的特殊方法,使用llm读取第一页的前1000个字符,获取标题,并存入到一个特殊的分块中
    first_page_text = pdf_reader.pages[0].extract_text()
    title_response = client.chat.completions.create(
        model='qwen-turbo',
        messages=[{
            'role': 'user',
            'content': f'从下面的论文文本中提取论文标题，只返回标题本身，不要任何解释：\n{first_page_text[:1000]}'
        }]
    )
    title = title_response.choices[0].message.content.strip()
    
    # 内容分块
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()

    if not text: # 判断字符串是否为空，Python 惯用写法
        raise HTTPException(status_code=400,detail='PDF 内容为空，可能是扫描版图片')
    
    chunks = splitter.split_text(text)
    
    print(f"提取的文字前200字：{text[:200]}")
    print(f"切块数量：{len(chunks)}")
    
    # 先插入标题的分块
    vectorstore.add_texts(
        texts=[title],
        metadatas=[{'source': file.filename, 'username': username, 'type': 'title'}]
    )
    
    # 把 内容chunks 存入 ChromaDB
    vectorstore.add_texts(
        texts=chunks,
        metadatas=[{'source': file.filename,'username':username}] * len(chunks)
    )
    save_doc_meta(file.filename, len(chunks),username)
    return {'message': '上传成功', 'chunk_count': len(chunks),}