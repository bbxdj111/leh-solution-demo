import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Определяем путь к папке frontend
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# Роут для Клиента (Live-Tracking)
@app.get("/")
@app.get("/client_track")
async def read_client_track():
    return FileResponse(os.path.join(FRONTEND_DIR, "client_track.html"))

# Роут для Техника (Worker + AI Copilot)
@app.get("/worker")
async def read_worker():
    return FileResponse(os.path.join(FRONTEND_DIR, "worker.html"))