import os
from qdrant_client import QdrantClient
from llama_index.vector_stores.qdrant import QdrantVectorStore

from dotenv import load_dotenv

load_dotenv()

_qdrant_vs = None

def get_vector_store() -> QdrantVectorStore:
    """Singleton accessor for the Qdrant vector store."""
    global _qdrant_vs
    if _qdrant_vs is None:
        _qdrant_vs = QdrantVectorStore(
            client=QdrantClient(
                url=os.getenv("QDRANT_URL"),
                api_key=os.getenv("QDRANT_API_KEY"),
            ),
            collection_name="quark-papers",
            embeddings_dim=1536,
        )
    return _qdrant_vs
