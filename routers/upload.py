from fastapi import APIRouter,File,UploadFile,HTTPException,Depends
import io
import PyPDF2
from database import splitter,vectorstore
import json
import os
from datetime import datetime
from routers.auth import verify_token

router = APIRouter()


# 写入文档元数据
def save_doc_meta(filename, chunk_count,username):
    meta_path = './docs_meta.json'
    
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
    
    content = await file.read() #读取二进制内容
    
    # 读取内容后判断大小
    if len(content) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400,detail='文件大小不能超过 10MB')
    
    # 将二进制包装成对象
    content_obj = io.BytesIO(content)
    # 用pyPDF2读取
    pdf_reader = PyPDF2.PdfReader(content_obj)
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()

    if not text: # 判断字符串是否为空，Python 惯用写法
        raise HTTPException(status_code=400,detail='PDF 内容为空，可能是扫描版图片')
    
    chunks = splitter.split_text(text)
    
    print(f"提取的文字前200字：{text[:200]}")
    print(f"切块数量：{len(chunks)}")
    # 把 chunks 存入 ChromaDB
    vectorstore.add_texts(
        texts=chunks,
        metadatas=[{'source': file.filename,'username':username}] * len(chunks)
    )
    save_doc_meta(file.filename, len(chunks),username)
    return {'message': '上传成功', 'chunk_count': len(chunks),}