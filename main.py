from dotenv import load_dotenv
load_dotenv()  # ← 放在最前面，第一个执行
from fastapi import FastAPI  # 导入
from routers.chat import router as chat_router
from routers.upload import router as upload_router
app = FastAPI() # 创建实例

# 这叫装饰器
@app.get('/hello')  # 配置路由
def hello_world():
    return {'message':'hi,nice to meet you.'}

# 监听这步 FastAPI 不写在代码里
# 而是通过 uvicorn 命令启动，后面会讲

@app.get('/hello/{name}')
def hello_name(name):
    return {'message':f'hi,{name}'}

# 注册路由
app.include_router(chat_router)
app.include_router(upload_router)
