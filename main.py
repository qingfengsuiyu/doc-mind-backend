from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from routers.chat import router as chat_router
from routers.upload import router as upload_router
from routers.docs import router as docs_router
from routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from database_sql import engine
from models_sql import Base

# import 完之后再创建表
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/hello')
def hello_world():
    return {'message': 'hi,nice to meet you.'}

@app.get('/hello/{name}')
def hello_name(name):
    return {'message': f'hi,{name}'}

app.include_router(chat_router)
app.include_router(upload_router)
app.include_router(docs_router)
app.include_router(auth_router)