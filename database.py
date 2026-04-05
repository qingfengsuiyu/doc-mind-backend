from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

# 加载 embedding 模型（第一次会自动下载，需要等一会）
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # 每块最多500个字符
    chunk_overlap=50     # 相邻块之间重叠50个字符
)

vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embeddings
)