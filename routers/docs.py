from fastapi import APIRouter
import json
import os
from database import vectorstore

router = APIRouter()

@router.get('/documents')
def get_docs():
    meta_path = './docs_meta.json'
    if not os.path.exists(meta_path):
        return {'docs': []}
    with open(meta_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)
    
    return {'docs': docs}


@router.delete('/documents/{filename}')
def delete_doc(filename: str):
    meta_path = './docs_meta.json'
    
    # 第一步：从 docs_meta.json 里删除记录
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
        
        docs = [d for d in docs if d['filename'] != filename]
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
    
    # 第二步：从 ChromaDB 里删除对应的向量
    vectorstore._collection.delete(
        where={'source': filename}
    )
    
    return {'message': f'{filename} 删除成功'}