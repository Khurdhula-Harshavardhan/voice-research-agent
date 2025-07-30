import os, time, pathlib, tempfile, asyncio
from fastapi import FastAPI, Query, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from livekit import api
from dotenv import load_dotenv
from rag.ingest_lib import ingest          # ← new import

load_dotenv()

API_KEY    = os.getenv("LIVEKIT_API_KEY")
API_SECRET = os.getenv("LIVEKIT_API_SECRET")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------- token endpoint ----------
@app.get("/api/getToken")
def get_token(
    room: str = Query("quark"),
    identity: str = Query("browser"),
):
    token = (
        api.AccessToken(api_key=API_KEY, api_secret=API_SECRET)
        .with_identity(identity)
        .with_grants(api.VideoGrants(room_join=True, room=room))
        .to_jwt()
    )
    return {"token": token, "issued_at": int(time.time())}

# ---------- upload endpoint ----------
UPLOAD_DIR = pathlib.Path(tempfile.gettempdir()) / "quark_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _run_ingest(path: pathlib.Path):
    """sync helper so BackgroundTasks can invoke it"""
    asyncio.run(ingest([path]))

@app.post("/api/upload")
async def upload_pdf(
    bg: BackgroundTasks,
    file: UploadFile = File(..., description="PDF file"),
):
    if not file.filename.lower().endswith(".pdf"):
        return {"status": "error", "detail": "Only PDF files accepted"}

    dest = UPLOAD_DIR / f"{int(time.time())}_{file.filename}"
    with dest.open("wb") as f:
        f.write(await file.read())

    # schedule ingestion in background thread
    bg.add_task(_run_ingest, dest)

    return {"status": "queued", "file": dest.name}
