from __future__ import annotations
import logging, asyncio, os
from dotenv import load_dotenv
from livekit.agents import Agent, AgentSession, JobContext, WorkerOptions, cli
from livekit.plugins import openai, elevenlabs, silero

from tools.search_web import search_web
from tools.query_papers import query_papers
from tools.gpu_prices import gpu_prices

load_dotenv()
logging.basicConfig(level=logging.INFO)

VAD_OPTS = dict(
    min_silence_duration=1.5,   # seconds (default 0.55)
)

SYSTEM_PROMPT = (
    "You are conversational agent serving as **Harry**, a junior research assistant with a passion for Natural Language Processing and AI. "
    "Harsha is a senior researcher who will ask you to fact check, summarize, or retrieve information from various sources."
    "Ask clarifying questions; use web/PDF/GPU tools; be concise."
    "You have access to the following tools: "
    "1. **Search Web**: For general web searches to find information.\n"
    "2. **Query Papers**: search *any* document that the user claims to have stored or uploaded previously (RAG over Qdrant)\n"
    "your agenda is to catch his mistakes, provide accurate information, and assist with research tasks.\n"
)

async def entrypoint(ctx: JobContext):
    await ctx.connect()

    agent = Agent(instructions=SYSTEM_PROMPT,
                  tools=[search_web, query_papers, gpu_prices])

    session = AgentSession(
        turn_detection="vad",          # ★ crucials
        vad=silero.VAD.load(**VAD_OPTS),
        stt=openai.STT(model="gpt-4o-transcribe"),
        llm=openai.LLM(model="gpt-4o", temperature=0.6),
        tts=elevenlabs.TTS(),
    )

    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
