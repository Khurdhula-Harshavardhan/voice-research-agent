import os, tavily
from typing import List, Dict
from livekit.agents import function_tool, RunContext
from jigsawstack import AsyncJigsawStack

@function_tool(name="search_web", description="Search the web for information")
async def search_web(context: RunContext, query: str, k: int = 5) -> List[Dict[str, str]]:
    """Search the open web via Tavily and return a list of {'title', 'url'} dicts.
    """
    jigsaw = AsyncJigsawStack(api_key=os.environ.get("JIGSAWSTACK_API_KEY"))
    results = await jigsaw.web.search({
        "query": query,
        "ai_overview": True,
    })
    return results["ai_overview"]
