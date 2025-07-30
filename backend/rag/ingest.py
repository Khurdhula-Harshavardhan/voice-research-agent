"""CLI: uv run rag/ingest.py ~/papers/*.pdf"""
import sys, pathlib, asyncio
from ingest_lib import ingest

if __name__ == "__main__":
    files = [pathlib.Path(p) for p in sys.argv[1:]]
    if not files:
        print("Provide one or more PDF paths"); sys.exit(1)
    n = asyncio.run(ingest(files))
    print(f"[DONE] indexed {n} documents → Qdrant")
