"""
Answer questions about any PDF the user has uploaded (RAG over Qdrant).
"""
import asyncio
from typing import Dict, Any
from livekit.agents import function_tool, RunContext
from llama_index.core import VectorStoreIndex
from llama_index.embeddings.openai import OpenAIEmbedding
from rag.vector_store import get_vector_store

def _rag_sync(question: str) -> Dict[str, Any]:
    index = VectorStoreIndex.from_vector_store(
        get_vector_store(),
        embed_model=OpenAIEmbedding(),
    )
    engine = index.as_query_engine(similarity_top_k=5)
    resp = engine.query(question)
    return {
        "answer": resp.response,
        "sources": [sn.node.text for sn in resp.source_nodes],
    }

@function_tool(
    description=(
        "Search and quote from ANY PDF the user has uploaded. "
        "Ideal for detailed, source‑grounded answers."
    )
)
async def query_papers(context: RunContext, question: str) -> Dict[str, Any]:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _rag_sync, question)
