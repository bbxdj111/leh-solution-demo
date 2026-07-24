import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

# Определяем точный абсолютный путь к папке frontend
BASE_DIR = Path(__file__).resolve().parent  # папка backend
FRONTEND_DIR = BASE_DIR.parent / "frontend" # папка frontend на уровень выше

@app.get("/")
@app.get("/client_track")
async def read_client_track():
    file_path = FRONTEND_DIR / "client_track.html"
    if not file_path.exists():
        return {"error": f"Файл не найден по пути: {file_path}"}
    return FileResponse(file_path)

@app.get("/worker")
async def read_worker():
    file_path = FRONTEND_DIR / "worker.html"
    if not file_path.exists():
        return {"error": f"Файл не найден по пути: {file_path}"}
    return FileResponse(file_path)