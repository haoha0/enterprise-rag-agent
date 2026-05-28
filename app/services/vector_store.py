import chromadb

from app.core.config import get_settings
from app.schemas.chunk import TextChunk
from app.schemas.qa import RetrievedChunk

class VectorStoreService:   # 向量库服务
    def __init__(self) -> None:
        self.settings = get_settings()

        # 持久化客户端，路径指向settings.chroma_dir
        self.client = chromadb.PersistentClient(
            path=self.settings.chroma_dir,
        )

        # 获取或创建集合（相当于关系数据库中的Table）
        self.collection = self.client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
        )

    # 数据写入，把切分好的文本块和它们对应的数学向量存入数据库
    def add_chunks(
        self,
        chunks: list[TextChunk],
        embeddings: list[list[float]],
    ) -> int:
        if not chunks:
            return 0

        # 确保 chunks 和 embeddings 对应，一个chunk（TextChunk）对应一个向量（list[float]）
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length.")

        # 存储
        self.collection.add(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.content for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )

        return len(chunks)

    # Retrieval检索核心，拿着用户提问的数学坐标（向量），去 Chroma 数据库里找出语义最相近的前 K 段文本
    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 3,
    ) -> list[RetrievedChunk]:
        result = self.collection.query( # 发起查询
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # 数据解包，query的返回值是List[List[]]，[[]]是默认返回值，防止崩溃
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        retrieved_chunks: list[RetrievedChunk] = []

        for chunk_id, document, metadata, distance in zip(
            ids,
            documents,
            metadatas,
            distances,
        ):
            score = None
            if distance is not None:
                score = 1 / (1 + distance)  # 距离转得分distance->score，Chroma默认返回距离，转换为人类直觉的得分

            retrieved_chunks.append(
                RetrievedChunk(
                    chunk_id=chunk_id,
                    content=document,
                    score=score,
                    metadata=metadata or {},
                )
            )

        return retrieved_chunks
    
# 存储的Chroma数据格式：
# chunk_id
# chunk content
# chunk embedding
# chunk metadata

# storage/chroma/
# ├── chroma.sqlite3               # 所有的文本、元数据、ID都存在这个单文件里
# └── 0e8b1... (一串UUID文件夹)      # 这是一个Collection的向量索引目录
#     ├── header.bin               # 向量图的头部配置
#     ├── data_level0.bin          # 实际的向量浮点数和底层图连接
#     └── link_lists.bin           # 图的导航跳表数据