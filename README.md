# Harry

Born to be Dua Lipa but forced to be Harry.

Harry is a research assistant who can help you with actual papers or quick fact-checks. 

## Setup

### Prerequisites
- Python 3.11+
- Node.js
- Qdrant vector database

### Environment Variables
Create `.env` files in both `backend/` and `frontend/` with:

**Backend (.env):**
```
LIVEKIT_API_KEY=your_key
LIVEKIT_API_SECRET=your_secret
OPENAI_API_KEY=your_key
ELEVENLABS_API_KEY=your_key
TAVILY_API_KEY=your_key
```

**Frontend (.env):**
```
REACT_APP_SHA_KEY=your_key
```

### Installation & Run

**Backend:**
```bash
cd backend
pip install -e .
python agent.py dev
python token_server.py  # separate terminal
```

**Frontend:**
```bash
cd frontend
npm install
npm start
```

Access at `http://localhost:3000`


## Persona

Harry friendly and knowledgeable research assistant who helps users find information through natural conversation. He speaks clearly and concisely, his task is to help Harsha catch obvious mistakes in writings, fact check claims he might make from various sources, or even help harsha quickly answer a quesion during a call.

## Thought Process behind Tech Stack:

- Why LiveKit: it was a must!
- Why Qdrant: easy to use familiarity from earlier projects.
- Why JigsawStack search: is AI-powered, easy to work with. I understand the INs and OUTs of this model.
- Why elevenlabs: wanted to clone Dua's voice and make it a British female research assistant, but they've added 2FA for creating a voice clone. Prompting the user to read from the screen. still a decent choice.
- OpenAI for embeddings & as brains: easy choice. GPT-4o provides the balance between speed to quality of output. 

## Features:
1. You can upload any PDF and infer it.
2. Download transcriptions.
3. Has AI-powered internet access. (You would always get close to accurate answers or would be prompted to provide more information.)

## Cons:
1. Lack of quality guardrails, if you provide it an image and ask the agent to caption it, it will hallucinate as it falls outside the prompt and the narrative (story) behind the agent. This is because there is no corresponding tool call. 
2. Poor performance on non-Latin languages. gpt-4o transcribe assumes my Hindi to be Urdu at times, causing my voice agent to respond in a language I don't really understand.
3. Awkward pauses can lead to a change of turn (the agent will take over, without you completing your thoughts)

## BTS for a Call

- User opens browser → enters SHA key → clicks Start Call.
- Frontend fetches JWT, auto‑publishes mic, joins a fresh LiveKit room.
- agent.py worker joins the same room and waits for VAD turn.
- Speech ↔ STT ↔ LLM (GPT‑4o) ↔ TTS round‑trips with ~1‑second latency.
- User can upload PDFs; a green toast confirms ingestion.
- At any point, the transcript (last line per speaker) is visible and can be downloaded as a text file.

## What would I improve if I had more time?
- Clone Dua's voice.
- Make the conversation a smoother exp, provide the user with settings on UI where they can set speech rate (rate at which the turns happen), speed (rate at which the agent responds).
- Better RAG, at times the model clearly Hallucinates. No excuses here. Could have done a better job here.
