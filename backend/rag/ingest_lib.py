"""
Reusable ingestion helper for PDFs → Qdrant.
"""
import asyncio, pathlib
from typing import Iterable
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from .vector_store import get_vector_store

async def ingest(paths: Iterable[pathlib.Path]) -> int:
    """Embed & push the given PDF paths into Qdrant; returns #docs."""
    docs = SimpleDirectoryReader(
        input_files=[str(p) for p in paths], recursive=True
    ).load_data()

    storage = StorageContext.from_defaults(vector_store=get_vector_store())
    VectorStoreIndex(
        docs,
        storage_context=storage,
        embed_model=OpenAIEmbedding(),
        show_progress=True,
    )
    return len(docs)
