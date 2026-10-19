from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic RAG Service"
    app_version: str = "0.1.0"
    environment: str = "development"

    embedding_model: str = "text-embedding-3-small"
    chroma_dir: str = ".chroma"
    collection_name: str = "documents"
    docs_dir: str = "data/docs"
    chunk_size: int = 300
    chunk_overlap: int = 50

    chat_model: str = "gpt-4o-mini"
    max_rewrites: int = 1
    top_k: int = 3

    access_key: SecretStr
    rate_limit_per_minute: int = 2
    daily_request_cap: int = 200

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()