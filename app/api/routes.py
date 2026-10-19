from typing import Annotated

from fastapi import APIRouter, Depends
from langgraph.graph.state import CompiledStateGraph
from app.api.dependencies import get_agent, get_openai_key, rate_limit, verify_access_key
from app.agent.state import new_state
from app.api.dependencies import get_agent, rate_limit, verify_access_key
from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.config import Settings, get_settings

router = APIRouter()


@router.get("/health")
def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )


@router.post(
    "/chat",
    dependencies=[
        Depends(verify_access_key),
        Depends(get_openai_key),
        Depends(rate_limit),
    ],
)
def chat(
    body: ChatRequest,
    agent: Annotated[CompiledStateGraph, Depends(get_agent)],
) -> ChatResponse:
    result = agent.invoke(new_state(body.question))
    return ChatResponse(
        answer=result["answer"],
        sources=result["sources"],
        route=result["route"],
        critic_reason=result["critic_reason"],
        rewrites=result["rewrites"],
    )