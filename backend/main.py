import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="LEH-Solution Platform", version="1.0.0")

# Автоматический поиск папок
BASE_DIR = Path(__file__).resolve().parent  # папка backend
ROOT_DIR = BASE_DIR.parent                  # корень проекта
FRONTEND_DIR = ROOT_DIR / "frontend"

def get_html_file(filename: str):
    path = FRONTEND_DIR / filename
    # Если файлы случайно попали во вложенную папку frontend/frontend/
    if not path.exists():
        path = FRONTEND_DIR / "frontend" / filename
    
    if not path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Файл {filename} не найден в папке {FRONTEND_DIR}"
        )
    return FileResponse(path)

# Главная страница (Хаб)
@app.get("/")
async def serve_index():
    return get_html_file("index.html")

# Карта для клиента
@app.get("/client_track")
async def serve_client_track():
    return get_html_file("client_track.html")

# Панель техника с ИИ
@app.get("/worker")
async def serve_worker():
    return get_html_file("worker.html")

# Проверка работоспособности
@app.get("/health")
async def health():
    return {"status": "ok", "service": "LEH-Solution Platform"}