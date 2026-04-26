from dotenv import load_dotenv
load_dotenv()
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os


# 加载 embedding 模型（第一次会自动下载，需要等一会）
embeddings = DashScopeEmbeddings(
    model="text-embedding-v3",
    dashscope_api_key=os.getenv("sk-155ccd2b87ed4d049666f3c98cb6b60d")
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,      # 每块最多500个字符
    chunk_overlap=50     # 相邻块之间重叠50个字符
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)