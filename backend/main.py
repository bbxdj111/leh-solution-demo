import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="LEH-Solution Platform", version="1.0.0")

# Вычисляем путь к папке frontend
BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR.parent / "frontend"

# Подключаем статические файлы (CSS, JS)
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# Главная страница (Хаб)
@app.get("/")
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

# Карта для клиента
@app.get("/client_track")
async def serve_client_track():
    return FileResponse(FRONTEND_DIR / "client_track.html")

# Панель техника с ИИ
@app.get("/worker")
async def serve_worker():
    return FileResponse(FRONTEND_DIR / "worker.html")

# Админ-панель
@app.get("/admin")
async def serve_admin():
    return FileResponse(FRONTEND_DIR / "admin.html")

# Вход в систему
@app.get("/login")
async def serve_login():
    return FileResponse(FRONTEND_DIR / "login.html")

# Проверка статуса сервера
@app.get("/health")
async def health():
    return {"status": "ok", "service": "LEH-Solution"}