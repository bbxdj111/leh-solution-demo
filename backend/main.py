from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI(title="LEH Solutions API")

# Путь к папке frontend (на уровень выше от backend)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Подключаем папку frontend для стилей и скриптов
if os.path.exists(FRONTEND_DIR):
    app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

# Главная страница - отдаем frontend/index.html
@app.get("/")
async def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "index.html не найден в папке frontend"}

# API для заказов и мастеров
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