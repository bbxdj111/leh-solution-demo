import math
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy.orm import Session

import database
import models
from whatsapp_service import send_client_tracking_whatsapp, send_master_new_order_whatsapp

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Craftsman Order Routing System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    def disconnect(self, websocket: WebSocket, master_id: int):
        if master_id in self.active_connections:
            if websocket in self.active_connections[master_id]:
                self.active_connections[master_id].remove(websocket)

    async def broadcast_location(self, master_id: int, data: dict):
        if master_id in self.active_connections:
            for connection in list(self.active_connections[master_id]):
                try:
                    await connection.send_json(data)
                except Exception:
                    self.disconnect(connection, master_id)

ws_manager = ConnectionManager()

@app.websocket("/ws/location/{master_id}")
async def websocket_location_endpoint(websocket: WebSocket, master_id: int):
    await websocket.accept()
    if master_id not in ws_manager.active_connections:
        ws_manager.active_connections[master_id] = []
    ws_manager.active_connections[master_id].append(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await ws_manager.broadcast_location(master_id, data)
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, master_id)
    except Exception:
        ws_manager.disconnect(websocket, master_id)

class BatchAssignRequest(BaseModel):
    master_id: int
    order_ids: List[int]

class StatusUpdateRequest(BaseModel):
    status: str

class HotelBookingRequest(BaseModel):
    master_id: int
    hotel_name: str
    city_or_address: str
    check_in: str
    check_out: str
    price: float

def calculate_distance(lat1, lon1, lat2, lon2):
    if None in (lat1, lon1, lat2, lon2):
        return None
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

@app.get("/seed-data")
def seed_test_data(db: Session = Depends(database.get_db)):
    db.query(models.Order).delete()
    db.query(models.User).delete()
    db.commit()

    m1 = models.User(username="Handwerker Alex", password="123", role="master", base_address="Berlin, Alexanderplatz 1")
    m2 = models.User(username="Handwerker Thomas", password="123", role="master", base_address="Berlin, Potsdamer Platz 5")
    
    o1 = models.Order(title="Klimaanlagen-Reparatur", client_name="Anna", address="Berlin, Alexanderplatz 3", lat=52.5219, lon=13.4132, status="new")
    o2 = models.Order(title="Sanitärinstallation", client_name="Dmitri", address="Berlin, Alexanderplatz 8", lat=52.5225, lon=13.4150, status="new")
    o3 = models.Order(title="Schlosswechsel", client_name="Elena", address="Berlin, Spandau 12", lat=52.5350, lon=13.1980, status="new")

    db.add_all([m1, m2, o1, o2, o3])
    db.commit()
    return {"message": "Testdaten erfolgreich erstellt!"}

@app.get("/orders")
def get_all_orders(db: Session = Depends(database.get_db)):
    orders = db.query(models.Order).all()
    result = []
    for o in orders:
        master_name = None
        if o.master_id:
            master = db.query(models.User).filter(models.User.id == o.master_id).first()
            if master:
                master_name = master.username
        result.append({
            "id": o.id,
            "title": o.title,
            "address": o.address,
            "client_name": o.client_name,
            "status": o.status,
            "lat": o.lat,
            "lon": o.lon,
            "master_id": o.master_id,
            "master_name": master_name
        })
    return result

@app.get("/orders/{order_id}")
def get_single_order(order_id: int, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    return order

@app.get("/admin/masters")
def get_masters(db: Session = Depends(database.get_db)):
    return db.query(models.User).filter(models.User.role == "master").all()

@app.get("/admin/orders/nearby-cluster")
def get_nearby_cluster(anchor_order_id: int, radius_km: float = 5.0, db: Session = Depends(database.get_db)):
    anchor = db.query(models.Order).filter(models.Order.id == anchor_order_id).first()
    if not anchor:
        raise HTTPException(status_code=404, detail="Hauptauftrag nicht gefunden")

    free_orders = db.query(models.Order).filter(
        models.Order.id != anchor_order_id,
        models.Order.status == "new"
    ).all()

    suggested = []
    for o in free_orders:
        dist = calculate_distance(anchor.lat, anchor.lon, o.lat, o.lon)
        if dist is not None and dist <= radius_km:
            suggested.append({
                "id": o.id,
                "title": o.title,
                "address": o.address,
                "client_name": o.client_name,
                "distance_km": dist,
                "auto_selected": True
            })

    return {
        "anchor_order": {
            "id": anchor.id,
            "title": anchor.title,
            "address": anchor.address
        },
        "radius_km": radius_km,
        "suggested_orders": suggested
    }

@app.post("/admin/orders/batch-assign")
def batch_assign_orders(req: BatchAssignRequest, db: Session = Depends(database.get_db)):
    orders = db.query(models.Order).filter(models.Order.id.in_(req.order_ids)).all()
    master = db.query(models.User).filter(models.User.id == req.master_id).first()

    for o in orders:
        o.master_id = req.master_id
        o.status = "in_progress"
        
        tracking_url = f"http://127.0.0.1:8000/frontend/client_track.html?order_id={o.id}"
        send_client_tracking_whatsapp(
            client_phone="+491701234567",
            client_name=o.client_name,
            order_title=o.title,
            tracking_link=tracking_url
        )

    if master and orders:
        order_names = ", ".join([o.title for o in orders])
        send_master_new_order_whatsapp(
            master_phone="+491709876543",
            master_name=master.username,
            order_title=order_names,
            address=orders[0].address
        )

    db.commit()
    return {"message": "Aufträge erfolgreich zugewiesen und WhatsApp benachrichtigt", "assigned_count": len(orders)}

@app.get("/master/{master_id}/orders")
def get_master_orders(master_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Order).filter(models.Order.master_id == master_id).all()

@app.post("/master/orders/{order_id}/status")
def update_order_status(order_id: int, req: StatusUpdateRequest, db: Session = Depends(database.get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Auftrag nicht gefunden")
    order.status = req.status
    db.commit()
    return {"message": "Status aktualisiert", "new_status": order.status}

@app.get("/admin/hotels/search")
def search_hotels(city: str = "Berlin"):
    return [
        {"name": f"Hotel Central {city}", "address": f"Hauptstraße 10, {city}", "price_per_night": 75.0, "rating": "4.5 ★"},
        {"name": f"Handwerker-Inn {city}", "address": f"Bahnhofstraße 4, {city}", "price_per_night": 52.0, "rating": "4.1 ★"},
        {"name": f"City Budget Hotel {city}", "address": f"Parkweg 12, {city}", "price_per_night": 45.0, "rating": "3.9 ★"}
    ]

@app.post("/admin/hotels/book")
def book_hotel(req: HotelBookingRequest, db: Session = Depends(database.get_db)):
    booking = models.HotelBooking(
        master_id=req.master_id,
        hotel_name=req.hotel_name,
        city_or_address=req.city_or_address,
        check_in=req.check_in,
        check_out=req.check_out,
        price=req.price
    )
    db.add(booking)
    db.commit()
    return {"message": f"Hotel '{req.hotel_name}' gebucht!"}

@app.get("/admin/hotels/bookings")
def get_hotel_bookings(db: Session = Depends(database.get_db)):
    bookings = db.query(models.HotelBooking).all()
    result = []
    for b in bookings:
        master = db.query(models.User).filter(models.User.id == b.master_id).first()
        result.append({
            "id": b.id,
            "master_name": master.username if master else f"ID {b.master_id}",
            "hotel_name": b.hotel_name,
            "city_or_address": b.city_or_address,
            "check_in": b.check_in,
            "check_out": b.check_out,
            "price": b.price
        })
    return result

BASE_DIR = Path(__file__).resolve().parent.parent
frontend_path = BASE_DIR / "frontend"

if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path), html=True), name="frontend")