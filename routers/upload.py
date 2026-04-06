from fastapi import APIRouter,File,UploadFile,HTTPException
import io
import PyPDF2
from database import splitter,vectorstore

router = APIRouter()

@router.post('/upload')
async def upload(file:UploadFile = File(...)):
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
    metadatas=[{'source': file.filename}] * len(chunks)
)
    return {'message': '上传成功', 'chunk_count': len(chunks),}