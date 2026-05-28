# Enterprise RAG Agent

一个基于 FastAPI 的企业知识库 RAG + Agent 智能问答系统 MVP。当前版本已打通从文档上传、文本解析、切分、Embedding、Chroma 向量库入库，到用户提问、Top-K 检索、RAG Prompt 构造、LLM 生成答案并返回引用来源的基础链路。

当前项目默认使用 Mock Embedding 和 Mock LLM，便于本地开发、测试和理解系统流程；也预留了 OpenAI-compatible 接口，可以接入 OpenAI、DeepSeek、SiliconFlow 或其他兼容 OpenAI SDK 调用格式的模型服务。

## 功能概览

### 文档入库链路

1. 用户上传文档到 FastAPI 接口。
2. 后端校验文件名、文件扩展名和文件大小。
3. 使用 UUID 生成服务端保存文件名，并保存到 `storage/uploads/`。
4. 根据文件类型解析文本内容。
5. 将全文按固定长度和 overlap 切分为 chunks。
6. 调用 EmbeddingClient 生成文本向量。
7. 将 chunk 内容、metadata 和 embedding 写入 Chroma 持久化向量库。
8. 返回上传、解析、切分、入库状态。

### 问答链路

1. 用户提交问题。
2. 对 query 生成 embedding。
3. 到 Chroma 中执行 Top-K 相似度检索。
4. 返回相关 chunks 和来源 metadata。
5. 根据检索结果构造 RAG Prompt。
6. 调用 LLM 生成答案。
7. 返回 answer 和 sources。

## 技术栈

- Web 框架：FastAPI
- ASGI Server：Uvicorn
- 配置管理：pydantic-settings，读取 `.env`
- 文件上传：python-multipart
- PDF 解析：PyMuPDF
- Word 解析：python-docx
- 向量数据库：ChromaDB PersistentClient
- LLM / Embedding SDK：openai Python SDK 的 OpenAI-compatible 调用方式
- 测试：pytest + FastAPI TestClient

## 目录结构

```text
.
├── app
│   ├── api
│   │   └── v1
│   │       ├── documents.py        # 文档上传接口
│   │       ├── health.py           # 健康检查接口
│   │       ├── qa.py               # 检索和问答接口
│   │       └── router.py           # v1 路由聚合
│   ├── core
│   │   └── config.py               # 应用配置和环境变量
│   ├── db                         # 数据库扩展预留目录
│   ├── schemas
│   │   ├── chunk.py                # 文本块模型
│   │   ├── document.py             # 上传响应模型
│   │   ├── health.py               # 健康检查响应模型
│   │   └── qa.py                   # 检索/问答请求和响应模型
│   ├── services
│   │   ├── document_parser.py      # PDF / DOCX / TXT / Markdown 文本解析
│   │   ├── document_service.py     # 文档入库编排服务
│   │   ├── prompt_builder.py       # RAG Prompt 构造
│   │   ├── qa_service.py           # 检索和问答编排服务
│   │   ├── text_splitter.py        # 文本切分
│   │   ├── vector_store.py         # Chroma 向量库读写
│   │   ├── embeddings              # Embedding 抽象、Mock、OpenAI-compatible 实现
│   │   └── llms                    # LLM 抽象、Mock、OpenAI-compatible 实现
│   └── main.py                     # FastAPI 应用入口
├── storage
│   ├── chroma                      # Chroma 本地持久化目录
│   └── uploads                     # 上传文件保存目录
├── tests                           # 单元测试和接口测试
├── .env.example                    # 环境变量示例
├── .gitignore
└── requirements.txt
```

## 核心模块说明

### API 层

`app/main.py` 创建 FastAPI 应用，并将 v1 路由挂载到 `API_V1_PREFIX`，默认前缀为 `/api/v1`。

当前接口：

- `GET /api/v1/health`：健康检查。
- `POST /api/v1/documents/upload`：上传文档，并同步完成解析、切分、向量化和入库。
- `POST /api/v1/qa/retrieve`：只执行检索，返回 Top-K chunks。
- `POST /api/v1/qa/answer`：执行完整 RAG 问答，返回答案和引用来源。

### 文档解析

`DocumentParser` 根据文件扩展名选择解析方法：

- `.pdf`：使用 PyMuPDF 提取每页文本。
- `.docx`：使用 python-docx 提取段落文本。
- `.txt`、`.md`、`.markdown`：按 UTF-8 文本读取，忽略异常字符。

### 文本切分

`TextSplitter` 使用固定窗口切分：

- `CHUNK_SIZE`：每个 chunk 的最大字符长度，默认 `500`。
- `CHUNK_OVERLAP`：相邻 chunk 的重叠字符数，默认 `100`。

每个 chunk 会带上：

- `chunk_id`
- `document_id`
- `chunk_index`
- `content`
- `content_length`
- `metadata`

metadata 中包含原始文件名、服务端保存文件名、文件路径、扩展名、起止字符位置等信息。

### Embedding

项目通过 `BaseEmbeddingClient` 定义统一接口：

```python
embed_texts(texts: list[str]) -> list[list[float]]
```

当前实现：

- `MockEmbeddingClient`：根据文本 hash 生成稳定的伪向量，适合本地测试。
- `OpenAICompatibleEmbeddingClient`：使用 OpenAI SDK 的 embeddings API，支持兼容 OpenAI 格式的第三方服务。

### 向量库

`VectorStoreService` 使用 ChromaDB `PersistentClient`：

- 默认持久化目录：`storage/chroma`
- 默认 collection：`enterprise_knowledge_base`

入库字段：

- ids：chunk id
- documents：chunk 文本
- embeddings：chunk 向量
- metadatas：chunk metadata

检索时返回 `RetrievedChunk`，包含 `chunk_id`、`content`、`score` 和 `metadata`。Chroma 默认返回 distance，项目中将其转换为 `1 / (1 + distance)` 形式的相似度分数。

### RAG Prompt

`PromptBuilder` 将检索到的 chunks 组织为带来源标记的上下文，并要求模型：

- 只基于给定 context 回答。
- 如果 context 中没有答案，则回答不知道。
- 保持简洁、事实性。

### LLM

项目通过 `BaseLLMClient` 定义统一接口：

```python
generate(prompt: str) -> str
```

当前实现：

- `MockLLMClient`：返回固定 mock 答案，适合本地测试。
- `OpenAICompatibleLLMClient`：使用 OpenAI SDK 的 chat completions API，支持兼容 OpenAI 格式的第三方服务。

## 环境准备

建议使用 Python 3.11+。

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## 环境变量

`.env.example` 中包含主要配置：

```env
APP_NAME=Enterprise RAG Agent
APP_ENV=dev
APP_VERSION=0.1.0
API_V1_PREFIX=/api/v1

UPLOAD_DIR=storage/uploads
CHROMA_DIR=storage/chroma
MAX_UPLOAD_SIZE_MB=20

CHUNK_SIZE=500
CHUNK_OVERLAP=100
CHROMA_COLLECTION_NAME=enterprise_knowledge_base

EMBEDDING_PROVIDER=mock
EMBEDDING_BASE_URL=
EMBEDDING_API_KEY=
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=384

LLM_PROVIDER=mock
LLM_BASE_URL=
LLM_API_KEY=
LLM_MODEL=deepseek-chat
LLM_TEMPERATURE=0.2
```

本地开发默认使用：

```env
EMBEDDING_PROVIDER=mock
LLM_PROVIDER=mock
```

如需接入真实模型，可改为：

```env
EMBEDDING_PROVIDER=openai_compatible
EMBEDDING_BASE_URL=https://your-embedding-provider/v1
EMBEDDING_API_KEY=your_embedding_api_key
EMBEDDING_MODEL=your_embedding_model

LLM_PROVIDER=openai_compatible
LLM_BASE_URL=https://your-llm-provider/v1
LLM_API_KEY=your_llm_api_key
LLM_MODEL=your_llm_model
LLM_TEMPERATURE=0.2
```

注意：真实 Embedding 模型的向量维度需要与 Chroma collection 中已有数据保持一致。如果切换 Embedding 模型或维度，建议清空 `storage/chroma/` 后重新入库。

## 启动服务

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- API 文档：http://127.0.0.1:8000/docs
- 健康检查：http://127.0.0.1:8000/api/v1/health

## 接口示例

### 健康检查

```bash
curl http://127.0.0.1:8000/api/v1/health
```

### 上传文档

支持 `.pdf`、`.docx`、`.txt`、`.md`、`.markdown`。

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/documents/upload" \
  -F "file=@test.txt"
```

返回示例字段：

```json
{
  "document_id": "uuid",
  "original_filename": "test.txt",
  "saved_filename": "uuid.txt",
  "file_path": "storage/uploads/uuid.txt",
  "file_extension": ".txt",
  "content_type": "text/plain",
  "file_size": 123,
  "status": "uploaded",
  "parse_status": "parsed",
  "text_length": 123,
  "text_preview": "preview...",
  "chunk_status": "chunked",
  "chunk_count": 1,
  "vector_status": "stored",
  "vector_count": 1
}
```

### 检索 Top-K chunks

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qa/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这个系统支持哪些文档处理能力？",
    "top_k": 3
  }'
```

### RAG 问答

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/qa/answer" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "这个系统支持哪些文档处理能力？",
    "top_k": 3
  }'
```

返回中：

- `answer`：LLM 生成的答案。
- `sources`：用于生成答案的检索片段和来源 metadata。

## 运行测试

```bash
pytest
```

如果本地 `storage/chroma/` 已经有真实调试数据，建议使用临时 Chroma 目录运行测试，避免测试依赖历史向量库状态：

```bash
CHROMA_DIR=$(mktemp -d) EMBEDDING_PROVIDER=mock EMBEDDING_DIMENSION=384 LLM_PROVIDER=mock pytest
```

当前测试覆盖：

- 健康检查接口。
- 文档上传接口。
- 文本切分逻辑。
- Mock Embedding 稳定性和向量维度。
- Chroma 入库和相似度检索。
- Prompt 构造。
- Mock LLM 生成。
- 检索接口和问答接口。

如果本地 Chroma 中已有不同维度的 collection 或同名测试 chunk id，测试可能受到历史数据影响。需要彻底清空本地向量库时，可以执行：

```bash
rm -rf storage/chroma/*
touch storage/chroma/.gitkeep
pytest
```

## 后续可扩展方向

- 接入 PostgreSQL，保存文档元数据、用户、问答记录和权限信息。
- 增加 Dockerfile 和 docker-compose，统一启动 API、数据库和向量库依赖。
- 增加异步任务队列，将大文件解析、Embedding 和入库从接口同步流程中拆出。
- 增加文档删除、重新入库、向量库 collection 管理能力。
- 增加用户认证、企业知识库权限隔离和审计日志。
- 增加更稳定的语义切分策略，例如按标题、段落、token 数或 Markdown 结构切分。
- 增加来源引用格式优化，例如返回文件名、页码、段落编号和字符范围。
