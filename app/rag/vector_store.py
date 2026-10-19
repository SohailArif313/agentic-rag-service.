from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr

from app.config import Settings


def get_vector_store(settings: Settings, api_key: SecretStr) -> Chroma:
    embeddings = OpenAIEmbeddings(
        model=settings.embedding_model,
        api_key=api_key,
    )
    return Chroma(
        collection_name=settings.collection_name,
        embedding_function=embeddings,
        persist_directory=settings.chroma_dir,
    )


def index_documents(vector_store: Chroma, chunks: list[Document]) -> int:
    ids = [f"{chunk.metadata['source']}:{chunk.metadata['start_index']}" for chunk in chunks]
    vector_store.add_documents(documents=chunks, ids=ids)
    return len(chunks)


def search(vector_store: Chroma, query: str, k: int = 3) -> list[Document]:
    return vector_store.similarity_search(query, k=k)