from fastapi import APIRouter,Depends
import json
import os
from database import vectorstore
from routers.auth import verify_token

router = APIRouter()

@router.get('/documents',)
def get_docs(username: str = Depends(verify_token)):
    meta_path = './docs_meta.json'
    if not os.path.exists(meta_path):
        return {'docs': []}
    with open(meta_path, 'r', encoding='utf-8') as f:
        docs = json.load(f)
        docs = [d for d in docs if (d['username'] == username)]
    
    return {'docs': docs}


@router.delete('/documents/{filename}')
def delete_doc(filename: str,username: str = Depends(verify_token)):
    meta_path = './docs_meta.json'
    
    # 第一步：从 docs_meta.json 里删除记录
    if os.path.exists(meta_path):
        with open(meta_path, 'r', encoding='utf-8') as f:
            docs = json.load(f)
        
        docs = [d for d in docs if not ((d['filename'] == filename) and (d['username'] == username))]
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
    
    # 第二步：从 ChromaDB 里删除对应的向量
    vectorstore._collection.delete(
        where={
        '$and': [
            {'source': {'$eq': filename}},
            {'username': {'$eq': username}}
        ]
    }
    )
    
    return {'message': f'{filename} 删除成功'}