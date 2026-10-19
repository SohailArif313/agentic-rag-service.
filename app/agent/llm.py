from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from app.config import Settings


def get_llm(settings: Settings, api_key: SecretStr) -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.chat_model,
        api_key=api_key,
        temperature=0,
    )