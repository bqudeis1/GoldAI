from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from huggingface_hub import hf_hub_download, upload_file
import asyncio
import json
import os
from datetime import date

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- CONFIGURATION ---
REPO_ID = "bahaq/ks-data-storage" 
HF_TOKEN = os.environ.get("HF_TOKEN")

FEEDBACK_FILE = "/tmp/feedback.json"
SENTIMENT_FILE = "/tmp/sentiment.json"
STATE_FILE = "/tmp/state.json"
TRADES_FILE = "/tmp/trades.json"
FEATURES_FILE = "/tmp/features.json"

# --- HELPERS ---
def sync_from_cloud(filename, default_data):
    base_name = os.path.basename(filename)
    try:
        path = hf_hub_download(repo_id=REPO_ID, filename=base_name, repo_type="dataset", token=HF_TOKEN)
        with open(path, "r") as f:
            data = json.load(f)
        with open(filename, "w") as f:
            json.dump(data, f)
        print(f"✅ Loaded {base_name} from cloud.")
    except:
        print(f"ℹ️ {base_name} initializing with defaults.")
        with open(filename, "w") as f:
            json.dump(default_data, f)

def sync_to_cloud(filename):
    if not HF_TOKEN: return
    try:
        upload_file(path_or_fileobj=filename, path_in_repo=os.path.basename(filename),
                    repo_id=REPO_ID, repo_type="dataset", token=HF_TOKEN)
    except: pass

def check_sentiment_reset():
    today = date.today().isoformat()
    if os.path.exists(SENTIMENT_FILE):
        with open(SENTIMENT_FILE, "r") as f:
            data = json.load(f)
        if data.get("date") != today:
            data = {"bullish": 0, "bearish": 0, "date": today}
            with open(SENTIMENT_FILE, "w") as f:
                json.dump(data, f)
            sync_to_cloud(SENTIMENT_FILE)
        return data
    return {"bullish": 0, "bearish": 0, "date": today}

# --- INITIALIZATION ---
sync_from_cloud(FEEDBACK_FILE, [])
sync_from_cloud(SENTIMENT_FILE, {"bullish": 0, "bearish": 0, "date": date.today().isoformat()})
sync_from_cloud(FEATURES_FILE, [])
sync_from_cloud(TRADES_FILE, [])

class FeedbackItem(BaseModel):
    username: str
    stars: int
    comment: str

# --- ENDPOINTS ---
@app.get("/api/sentiment")
async def get_sentiment():
    return check_sentiment_reset()

@app.post("/api/sentiment/{vote_type}")
async def vote_sentiment(vote_type: str):
    data = check_sentiment_reset()
    if vote_type in ["bullish", "bearish"]:
        data[vote_type] += 1
        with open(SENTIMENT_FILE, "w") as f:
            json.dump(data, f)
        sync_to_cloud(SENTIMENT_FILE)
    return data

@app.get("/api/archive")
async def get_archive():
    if os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    return []

@app.get("/api/features")
async def get_features():
    if os.path.exists(FEATURES_FILE):
        with open(FEATURES_FILE, "r") as f:
            return json.load(f)
    return []

@app.get("/api/feedback")
async def get_feedback():
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, "r") as f:
            return json.load(f)
    return []

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if os.path.exists(STATE_FILE):
                with open(STATE_FILE, "r") as f:
                    data = json.load(f)
                await websocket.send_json(data)
            await asyncio.sleep(1)
    except: pass

# --- ROUTING ---
if os.path.exists("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    file_path = f"frontend/dist/{full_path}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return FileResponse("frontend/dist/index.html")