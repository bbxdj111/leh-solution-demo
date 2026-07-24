from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="LEH Solutions API")

# Пути к папкам
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Монтируем статику, если папка существует
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# Поиск index.html по всем возможным путям
def get_index_path():
    possible_paths = [
        os.path.join(FRONTEND_DIR, "index.html"),
        os.path.join(BASE_DIR, "index.html"),
        os.path.join(CURRENT_DIR, "index.html"),
        "frontend/index.html",
        "static/index.html"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# Главная страница (/)
@app.get("/")
async def serve_index():
    index_path = get_index_path()
    if index_path:
        return FileResponse(index_path)
    return {"status": "error", "message": "Файл index.html не найден на сервере"}

# API маршруты
@app.get("/orders")
async def get_orders():
    return [
        {"id": 101, "title": "Montage & Installation", "client_name": "Müller GmbH", "city": "Berlin", "status": "NEU"},
        {"id": 102, "title": "Wartung & Reparatur", "client_name": "Schmidt AG", "city": "Potsdam", "status": "NEU"},
        {"id": 103, "title": "Elektroinstallation", "client_name": "Schneider", "city": "Leipzig", "status": "NEU"}
    ]

@app.get("/admin/masters")
async def get_masters():
    return [
        {"name": "Hans (LEH Team 1)"},
        {"name": "Stefan (LEH Team 2)"},
        {"name": "Marek (LEH Team 3)"}
    ]

@app.get("/seed-data")
async def seed_data():
    return {"status": "success", "message": "Testdaten geladen!"}