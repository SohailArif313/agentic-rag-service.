from langgraph.graph import END, START, StateGraph
from pydantic import SecretStr

from app.agent.llm import get_llm
from app.agent.nodes import AgentNodes
from app.agent.state import AgentState
from app.config import Settings
from app.rag.indexing import ensure_index
from app.rag.vector_store import get_vector_store

def build_graph(llm, vector_store, top_k: int, max_rewrites: int):
    nodes = AgentNodes(llm, vector_store, top_k)

    def after_router(state: AgentState) -> str:
        return state["route"]

    def after_critic(state: AgentState) -> str:
        if state["is_sufficient"]:
            return "generate"
        if state["rewrites"] < max_rewrites:
            return "rewrite"
        return "generate"

    builder = StateGraph(AgentState)

    builder.add_node("router", nodes.router)
    builder.add_node("retrieve", nodes.retrieve)
    builder.add_node("critic", nodes.critic)
    builder.add_node("rewrite", nodes.rewrite)
    builder.add_node("generate", nodes.generate)

    builder.add_edge(START, "router")
    builder.add_conditional_edges(
        "router", after_router, {"retrieve": "retrieve", "direct": "generate"}
    )
    builder.add_edge("retrieve", "critic")
    builder.add_conditional_edges(
        "critic", after_critic, {"generate": "generate", "rewrite": "rewrite"}
    )
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("generate", END)

    return builder.compile()


def create_agent(settings: Settings, api_key: SecretStr):
    vector_store = get_vector_store(settings, api_key)
    ensure_index(settings, vector_store)
    return build_graph(
        llm=get_llm(settings, api_key),
        vector_store=vector_store,
        top_k=settings.top_k,
        max_rewrites=settings.max_rewrites,
    )