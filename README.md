# DocMind - AI 知识库问答系统

基于 RAG（检索增强生成）技术的智能文档问答系统，支持上传 PDF 文档，并通过自然语言提问获取精准回答。

## 技术栈

**后端**
- FastAPI — 高性能 Python Web 框架
- LangChain — RAG 流程编排
- ChromaDB — 本地向量数据库
- HuggingFace Sentence Transformers — 文本 Embedding 模型
- 通义千问（Qwen-Turbo）— 大语言模型
- PyPDF2 — PDF 文档解析

**前端**
- UniApp — 跨平台前端框架（H5 + 微信小程序）

**部署**
- 阿里云香港服务器（Ubuntu + Nginx）

## 核心功能

- 📄 PDF 文档上传与解析
- 🧩 文档自动切块与向量化
- 🔍 语义相似度检索（非关键词匹配）
- 🤖 基于文档内容的 AI 精准问答
- ⚡ 流式输出（逐字显示，类 ChatGPT 体验）
- 📌 回答显示参考来源段落

## 系统架构

```
用户上传 PDF
     ↓
文字提取（PyPDF2）
     ↓
文本切块（LangChain RecursiveCharacterTextSplitter）
     ↓
向量化（paraphrase-multilingual-MiniLM-L12-v2）
     ↓
存入 ChromaDB

用户提问
     ↓
问题向量化
     ↓
ChromaDB 语义检索（Top-K 相关段落）
     ↓
构建 Prompt（上下文 + 问题）
     ↓
通义千问生成回答
     ↓
返回答案 + 参考来源
```

## 项目结构

```
doc-mind/
├── routers/
│   ├── upload.py        # 文档上传接口
│   └── chat.py          # 问答接口
├── models/
│   └── schemas.py       # Pydantic 数据模型
├── database.py          # 向量数据库 & Embedding 初始化
├── main.py              # FastAPI 入口
├── .env.example         # 环境变量示例
└── requirements.txt     # 依赖列表
```

## 本地运行

**1. 克隆项目**

```bash
git clone https://github.com/你的用户名/doc-mind.git
cd doc-mind
```

**2. 创建虚拟环境**

```bash
python3 -m venv venv
source venv/bin/activate
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

**4. 配置环境变量**

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的通义千问 API Key：

```
DASHSCOPE_API_KEY=你的sk-开头的key
```

**5. 启动服务**

```bash
uvicorn main:app --reload
```

访问 `http://127.0.0.1:8000/docs` 查看接口文档。

## API 接口

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | `/upload` | 上传 PDF 文档，建立知识库 |
| POST | `/ask` | 基于知识库进行问答 |

## 环境要求

- Python 3.8+
- 通义千问 API Key（[DashScope 控制台](https://dashscope.aliyun.com) 免费申请）

## 开发计划

- [x] FastAPI 基础框架搭建
- [x] PDF 解析与文本切块
- [x] ChromaDB 向量存储
- [x] RAG 检索问答核心链路
- [ ] 流式输出（SSE）
- [ ] 回答来源引用显示
- [ ] 文档管理（查看 / 删除 / 去重）
- [ ] JWT 用户鉴权
- [ ] UniApp 前端页面
- [ ] 部署上线

## License

MIT
