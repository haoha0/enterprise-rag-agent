from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
# pydantic_settings：用于定义应用配置的Pydantic设置类

class Settings(BaseSettings):
    app_name: str = "Enterprise RAG Agent"
    app_env: str = "dev"
    app_version: str = "0.1.0"

    api_v1_prefix: str = "/api/v1"

    upload_dir: str = "storage/uploads"
    chroma_dir: str = "storage/chroma"

    max_upload_size_mb: int = 20

    chunk_size: int = 500
    chunk_overlap: int = 100

    embedding_provider: str = "mock"
    embedding_dimension: int = 384
    chroma_collection_name: str = "enterprise_knowledge_base"

    embedding_base_url: str | None = None
    embedding_api_key: str | None = None
    embedding_model: str = "text-embedding-3-small"

    llm_provider: str = "mock"
    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "deepseek-chat"
    llm_temperature: float = 0.2

    database_url: str = "postgresql+psycopg://rag_user:rag_password@localhost:5432/rag_db"

    allowed_file_extensions: set[str] = {
        ".pdf",
        ".docx",
        ".txt",
        ".md",
        ".markdown",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache  # 缓存装饰器：让get_settings函数的返回值被缓存，避免重复创建Settings实例
def get_settings() -> Settings:
    return Settings()